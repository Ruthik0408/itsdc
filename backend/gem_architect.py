import json
import os
import re

from feature_dsl import get_feature_contract, validate_feature_plan
from tpp_architect import (
    ALWAYS_INCLUDE_COLUMN_NAMES,
    BACKEND_DIR,
    FORENSIC_FEATURE_PRIORITIES,
    LAST_BAD_RESPONSE_FILE,
    MAX_CONTEXT_FK_COLUMNS,
    MAX_LLM_COLUMNS_PER_TABLE,
    MAX_LLM_SCHEMA_TABLES,
    MAX_PROFILE_TABLES,
    MAX_TABLE_SPARSE_COLUMN_FRACTION,
    MAX_VALIDATION_RULES_PER_PROMPT,
    SCHEMA_FILE,
    append_unique_columns,
    apply_column_profiles,
    column_priority,
    compact_column_for_llama,
    create_tpp_architecture_completion,
    echo,
    ensure_ollama_is_running,
    filter_non_empty_columns,
    group_schema,
    is_amount_candidate_column,
    is_context_candidate_column,
    is_date_column,
    is_excluded_table,
    is_numeric_column,
    limited_compact_columns,
    name_contains_any,
    parse_llama_json_object,
    parse_validation_markdown,
    profile_columns_from_database,
    removed_sparse_columns,
    save_bad_llama_response,
    score_table_for_llama,
    set_architect_log_prefix,
    sparse_column_fraction,
)

set_architect_log_prefix("gem_architect")

GEM_SOURCE_CONFIG_FILE = str(BACKEND_DIR / "gem_anomaly_sources.json")
GEM_OUTPUT_FILE = str(BACKEND_DIR / "gem_anomaly_guide.md")
GEM_SCHEMA_CANDIDATE_AUDIT_FILE = BACKEND_DIR / "gem_schema_candidates.json"
GEM_VALIDATION_CONTEXT_FILE = BACKEND_DIR.parent / "validation_files" / "GEM_BILLS_VALIDATION.md"
GEM_FEATURE_RULES_FILE = BACKEND_DIR / "gem_feature_rules.md"
GEM_DAK_SECTION_IDS = (113, 127, 128, 129, 219, 348)
GEM_ARCHITECT_TABLES = (
    "dak",
    "gem_bill",
    "gem_product",
    "cheque_slip",
    "punching_medium",
    "schedule3",
    "ecs",
)
GEM_PAYMENT_FLOW = (
    "dak -> gem_bill -> gem_product(product names/items) -> cheque_slip -> "
    "punching_medium -> schedule3 -> ecs"
)
GEM_DAK_LINK_RULE = "Join payment stages with dak.id = <stage>.fk_dak."
GEM_PRODUCT_LINK_RULE = "Join product rows with gem_bill.id = gem_product.fk_gem_bill."


def get_gem_architect_source_tables() -> tuple[str, ...]:
    configured = os.getenv("GEM_ARCHITECT_SOURCE_TABLES")
    raw_tables = configured if configured is not None else ",".join(GEM_ARCHITECT_TABLES)
    tables = []
    seen = set()
    for table in raw_tables.split(","):
        table = table.strip()
        if not table or table in seen or is_excluded_table(table):
            continue
        tables.append(table)
        seen.add(table)
    return tuple(tables)


BUSINESS_PRIORITY_TABLES = get_gem_architect_source_tables()


def is_gem_architect_source_table(table_name: str) -> bool:
    return table_name in set(BUSINESS_PRIORITY_TABLES)


def parse_gem_validation_context_rules() -> tuple[dict, ...]:
    if not GEM_VALIDATION_CONTEXT_FILE.exists():
        return ()
    return tuple(parse_validation_markdown(GEM_VALIDATION_CONTEXT_FILE))


def load_gem_feature_rules() -> str:
    if not GEM_FEATURE_RULES_FILE.exists():
        return ""
    return GEM_FEATURE_RULES_FILE.read_text(encoding="utf-8")[:16000]


def gem_validation_rules_for_table(table_name: str) -> list[dict]:
    return [
        dict(rule)
        for rule in parse_gem_validation_context_rules()
        if rule["table"] == table_name
    ][:MAX_VALIDATION_RULES_PER_PROMPT]


def gem_validation_column_names_by_table() -> dict[str, set[str]]:
    by_table: dict[str, set[str]] = {}
    for rule in parse_gem_validation_context_rules():
        by_table.setdefault(rule["table"], set()).add(rule["column"])
    return by_table


def gem_validation_context_for_table_detail(table_detail: dict) -> list[dict]:
    selected_rules = gem_validation_rules_for_table(table_detail["table"])
    seen = {(rule["table"], rule["column"], rule["validation"]) for rule in selected_rules}
    for relationship in table_detail.get("relationship_context", []):
        referenced_table = relationship.get("referenced_table")
        if not referenced_table:
            continue
        for rule in gem_validation_rules_for_table(referenced_table):
            key = (rule["table"], rule["column"], rule["validation"])
            if key in seen:
                continue
            selected_rules.append(rule)
            seen.add(key)
            if len(selected_rules) >= MAX_VALIDATION_RULES_PER_PROMPT:
                return selected_rules
    return selected_rules[:MAX_VALIDATION_RULES_PER_PROMPT]


def parse_schema_file(path):
    echo(f"Reading GEM schema from {path}")
    rows = []
    current_table = None
    table_pattern = re.compile(r"^## Table: (?P<table>.+)$")
    column_pattern = re.compile(
        r"^\| (?P<column>[^|]+) \| (?P<data_type>[^|]+) \| (?P<key>[^|]*) \| (?P<references>[^|]+) \|$"
    )

    with open(path, "r", encoding="utf-8") as schema_file:
        for raw_line in schema_file:
            line = raw_line.strip()
            table_match = table_pattern.match(line)
            if table_match:
                current_table = table_match.group("table").strip()
                if is_excluded_table(current_table):
                    current_table = None
                continue

            if (
                not current_table
                or is_excluded_table(current_table)
                or line.startswith("|---")
                or line.startswith("| Column Name")
            ):
                continue

            column_match = column_pattern.match(line)
            if not column_match:
                continue
            column = column_match.group("column").strip()
            if column == "Column Name":
                continue

            rows.append(
                {
                    "table": current_table,
                    "column": column,
                    "data_type": column_match.group("data_type").strip().lower(),
                    "key": column_match.group("key").strip(),
                    "references": column_match.group("references").strip(),
                }
            )

    rows = prune_schema_rows_to_gem_relationships(rows)
    tables = {row["table"] for row in rows}
    echo(f"Parsed {len(tables)} GEM architect table(s) and {len(rows)} columns from schema.")
    return rows


def prune_schema_rows_to_gem_relationships(schema_rows):
    root_tables = set(BUSINESS_PRIORITY_TABLES)
    return [
        row
        for row in schema_rows
        if row["table"] in root_tables and not is_excluded_table(row["table"])
    ]


def select_structural_profile_tables(schema_rows):
    tables = group_schema(schema_rows)
    scored_tables = []

    for table_name, columns in tables.items():
        if is_excluded_table(table_name) or not is_gem_architect_source_table(table_name):
            continue
        has_pk = any(column["key"] == "PK" for column in columns)
        if not has_pk:
            continue
        scored_tables.append((score_table_for_llama(table_name, columns), table_name, columns))

    scored_tables.sort(key=lambda item: BUSINESS_PRIORITY_TABLES.index(item[1]))
    return scored_tables[:MAX_PROFILE_TABLES]


def direct_relationship_context(
    table_name,
    columns,
    all_tables,
    max_relationships=10,
    validation_columns_by_table=None,
):
    relationships = []
    for column in columns:
        referenced_table = column.get("references")
        if column.get("key") != "FK" or not referenced_table or referenced_table == "None":
            continue
        if referenced_table not in all_tables or is_excluded_table(referenced_table):
            continue
        relationships.append(
            {
                "source_fk": column["column"],
                "referenced_table": referenced_table,
                "join_rule": f"{table_name}.{column['column']} = {referenced_table}.id",
                "referenced_columns": limited_compact_columns(
                    all_tables[referenced_table],
                    8,
                    validation_columns_by_table=validation_columns_by_table,
                ),
            }
        )

    if table_name == "gem_bill" and "gem_product" in all_tables:
        relationships.append(
            {
                "source_fk": "id",
                "referenced_table": "gem_product",
                "join_rule": GEM_PRODUCT_LINK_RULE,
                "referenced_columns": limited_compact_columns(
                    all_tables["gem_product"],
                    12,
                    validation_columns_by_table=validation_columns_by_table,
                ),
            }
        )

    if table_name in {"gem_bill", "cheque_slip", "punching_medium", "schedule3", "ecs"}:
        relationships.append(
            {
                "source_fk": "fk_dak",
                "referenced_table": "dak_payment_siblings",
                "join_rule": GEM_DAK_LINK_RULE,
                "referenced_columns": [
                    "dak.id",
                    "gem_bill.fk_dak",
                    "cheque_slip.fk_dak",
                    "punching_medium.fk_dak",
                    "schedule3.fk_dak",
                    "ecs.fk_dak",
                ],
            }
        )

    return relationships[:max_relationships]


def build_table_summary_for_llama(
    table_name,
    profiled_columns,
    table_profile,
    score,
    validation_columns_by_table=None,
):
    usable_columns = filter_non_empty_columns(profiled_columns)
    pk_columns = [column for column in usable_columns if column["key"] == "PK"]
    amount_columns = [column for column in usable_columns if is_amount_candidate_column(column)]
    if not amount_columns:
        amount_columns = [
            column
            for column in usable_columns
            if column["key"] not in {"PK", "FK"} and is_numeric_column(column)
        ]
    date_columns = [column for column in usable_columns if is_date_column(column)]
    context_columns = [column for column in usable_columns if is_context_candidate_column(column)]
    if not context_columns:
        context_columns = [
            column
            for column in usable_columns
            if column["key"] == "FK"
            or column["column"] in ALWAYS_INCLUDE_COLUMN_NAMES
            or name_contains_any(column, ("vendor", "product", "unit", "section", "status", "mode", "bank"))
        ]
    status_columns = [
        column
        for column in usable_columns
        if column["column"] in ALWAYS_INCLUDE_COLUMN_NAMES
        or name_contains_any(column, ("status", "approved", "released", "rollback", "rejection"))
    ]

    return {
        "table": table_name,
        "row_count": table_profile.get("row_count", 0),
        "column_count": len(profiled_columns),
        "usable_column_count": len(usable_columns),
        "sparse_column_fraction": round(sparse_column_fraction(profiled_columns), 4),
        "score": round(score, 4),
        "primary_keys": limited_compact_columns(pk_columns, 3, validation_columns_by_table),
        "amount_candidates": limited_compact_columns(amount_columns, 8, validation_columns_by_table),
        "date_candidates": limited_compact_columns(date_columns, 8, validation_columns_by_table),
        "context_candidates": limited_compact_columns(context_columns, 14, validation_columns_by_table),
        "status_candidates": limited_compact_columns(status_columns, 8, validation_columns_by_table),
    }


def build_llama_table_inventory(schema_rows):
    all_tables = group_schema(schema_rows)
    validation_columns = gem_validation_column_names_by_table()
    profile_candidates = select_structural_profile_tables(schema_rows)
    table_columns = {table_name: columns for _, table_name, columns in profile_candidates}
    profiles = profile_columns_from_database(table_columns)

    scored_tables = []
    audit_candidates = []
    for _, table_name, columns in profile_candidates:
        table_profile = profiles.get(table_name, {"row_count": 0, "columns": {}})
        profiled_columns = apply_column_profiles(columns, table_profile)
        usable_columns = filter_non_empty_columns(profiled_columns)
        amount_columns = [column for column in usable_columns if is_amount_candidate_column(column)]
        if not amount_columns:
            amount_columns = [
                column
                for column in usable_columns
                if column["key"] not in {"PK", "FK"} and is_numeric_column(column)
            ]
        table_sparse_fraction = sparse_column_fraction(profiled_columns)

        if not usable_columns:
            continue
        has_pk = any(column["key"] == "PK" for column in usable_columns)
        if not has_pk or not amount_columns:
            continue
        if table_name not in BUSINESS_PRIORITY_TABLES and table_sparse_fraction > MAX_TABLE_SPARSE_COLUMN_FRACTION:
            continue

        table_score = score_table_for_llama(table_name, usable_columns)
        table_score += min(len(amount_columns), 3) * 10
        table_score -= table_sparse_fraction * 40
        scored_tables.append((table_score, table_name, profiled_columns, table_profile))

    scored_tables.sort(key=lambda item: BUSINESS_PRIORITY_TABLES.index(item[1]))
    selected_tables = scored_tables[:MAX_LLM_SCHEMA_TABLES]
    summaries = []
    table_details = {}

    for score, table_name, profiled_columns, table_profile in selected_tables:
        usable_columns = filter_non_empty_columns(profiled_columns)
        relationships = direct_relationship_context(
            table_name,
            usable_columns,
            all_tables,
            validation_columns_by_table=validation_columns,
        )
        summary = build_table_summary_for_llama(
            table_name,
            profiled_columns,
            table_profile,
            score,
            validation_columns_by_table=validation_columns,
        )
        summaries.append(summary)
        table_details[table_name] = {
            "table": table_name,
            "row_count": table_profile.get("row_count", 0),
            "columns": sorted(
                usable_columns,
                key=lambda column: column_priority(column, validation_columns),
                reverse=True,
            ),
            "relationship_context": relationships,
            "validation_context": gem_validation_rules_for_table(table_name),
            "column_count": len(profiled_columns),
            "usable_column_count": len(usable_columns),
            "sparse_column_fraction": round(sparse_column_fraction(profiled_columns), 4),
        }
        audit_candidates.append(
            {
                **summary,
                "business_priority": table_name in BUSINESS_PRIORITY_TABLES,
                "relationship_context": relationships,
                "validation_context": gem_validation_rules_for_table(table_name),
                "full_usable_columns_for_stage_2": [
                    {
                        "column": column["column"],
                        "data_type": column["data_type"],
                        "key": column["key"],
                        "references": column["references"],
                        "non_null_count": column.get("non_null_count", 0),
                        "null_fraction": column.get("null_fraction", 1),
                    }
                    for column in sorted(
                        usable_columns,
                        key=lambda column: column_priority(column, validation_columns),
                        reverse=True,
                    )
                ],
                "removed_sparse_columns": removed_sparse_columns(profiled_columns),
            }
        )

    with open(GEM_SCHEMA_CANDIDATE_AUDIT_FILE, "w", encoding="utf-8") as output_file:
        json.dump(audit_candidates, output_file, indent=2)
    echo(f"Wrote GEM schema candidates to {GEM_SCHEMA_CANDIDATE_AUDIT_FILE}")
    return summaries, table_details


def trim_columns_for_llama(columns, validation_columns_by_table=None):
    validation_columns_by_table = validation_columns_by_table or {}
    usable_columns = filter_non_empty_columns(columns)
    validation_columns = [
        column
        for column in usable_columns
        if column["column"] in validation_columns_by_table.get(column.get("table"), set())
    ]
    always_columns = [column for column in usable_columns if column["column"] in ALWAYS_INCLUDE_COLUMN_NAMES]
    pk_columns = [column for column in usable_columns if column["key"] == "PK"]
    numeric_columns = [column for column in usable_columns if column["key"] != "FK" and is_numeric_column(column)]
    date_columns = [column for column in usable_columns if is_date_column(column)]
    fk_columns = [column for column in usable_columns if column["key"] == "FK"]
    product_columns = [
        column
        for column in usable_columns
        if name_contains_any(column, ("product", "item", "brand", "category", "hsn"))
    ]
    other_columns = [
        column
        for column in usable_columns
        if column not in pk_columns
        and column not in numeric_columns
        and column not in date_columns
        and column not in fk_columns
        and column not in product_columns
    ]

    ordered_columns = []
    for bucket in (
        validation_columns,
        always_columns,
        pk_columns,
        numeric_columns,
        date_columns,
        product_columns,
        fk_columns[:MAX_CONTEXT_FK_COLUMNS],
        other_columns,
    ):
        append_unique_columns(
            ordered_columns,
            sorted(bucket, key=lambda column: column_priority(column, validation_columns_by_table), reverse=True),
        )
    return ordered_columns[:MAX_LLM_COLUMNS_PER_TABLE]


def build_table_feature_prompt(table_detail):
    table_name = table_detail["table"]
    full_usable_columns = [compact_column_for_llama(column) for column in table_detail["columns"]]
    validation_context = gem_validation_context_for_table_detail(table_detail)
    section_ids = ", ".join(str(section_id) for section_id in GEM_DAK_SECTION_IDS)

    return {
        "task": (
            "Act as a senior Government Accounts, Defence Audit, GEM Bill Payment Flow, "
            "and Forensic Analytics architect. Create one anomaly detection source plan for GEM_BILLS only. "
            "The final model is Isolation Forest; design deterministic, machine-computable forensic features. "
            "Use gem_feature_rules as the controlling feature requirements when visible columns support them. "
            f"GEM payment flow is {GEM_PAYMENT_FLOW}. "
            f"{GEM_DAK_LINK_RULE} {GEM_PRODUCT_LINK_RULE} "
            "Product names, product brands, categories, HSN, quantities, unit prices, and total values from "
            "gem_product are important context for repeat purchase, rate variation, fake item identity, "
            "and product/payment mismatch detection."
        ),
        "strict_rules": [
            "Use only column names from full_usable_columns.",
            f"Use only these tables in reasoning: {', '.join(GEM_ARCHITECT_TABLES)}.",
            f"Use only GEM_BILLS section ids: {section_ids}.",
            "Do not remove, rewrite, or rely on THIRD_PARTY_PAYMENTS rules.",
            "Do not invent columns, formulas, or feature operations.",
            "Every feature must be deterministic, numeric, safe for null values, and explainable to an auditor.",
            "For GEM flow, relation from dak to each payment table is dak.id = table.fk_dak.",
            "For product enrichment, relation is gem_bill.id = gem_product.fk_gem_bill.",
            "Use id as id_column when present.",
            "Prefer amount_column in this order when present: amount_to_be_paid, amount_passed, bill_amount, total_value, amount, schedule3_amount.",
            "context_columns should include fk_dak, product_name/product_brand/product_category, vendor identity, invoice/order/supply order, payment reference, UTR, bank/account, payment mode, status, approval, and record_status when visible.",
            "date_column must be a real date/timestamp column from full_usable_columns, or null if none is suitable.",
            "Each feature_plan item must obey feature_contract exactly.",
            "Highest priority order: missing GEM bill for dak, missing product rows/product names, downstream payment without GEM bill, skipped payment stages, amount mismatch between GEM bill and payment stages, repeated product/vendor/order/invoice, same product different unit_price, date sequence contradiction, payment routing mismatch, weak ECS trail.",
            "Use duplicate_normalized_key for product_name, product_brand, invoice_no, gem_invoice_no, order_id, transaction_id, vendor_name, vendor_code, payment_reference_no, and utr_no when visible.",
            "Use duplicate_distinct to detect same product/vendor/order/invoice paid across different daks, amounts, beneficiaries, or dates.",
            "Use ratio_to_group_median, group_rank_pct, and group_frequency for product/vendor/category amount or unit_price inconsistency.",
            "Use rolling_window_count and rolling_window_amount_sum for repeated vendor/product/invoice/order patterns across nearby dates.",
            "Use numeric_gt and numeric_lt for bill_amount, amount_passed, amount_to_be_paid, total_value, unit_price, GST, deduction, and payment amount contradictions when comparable columns exist.",
            "Use date_after and date_in_future for order, supply order, invoice, expected delivery, actual delivery, CRAC, PRC, bill, cheque, PM, schedule, CMP, UTR, and ECS chronology.",
            "Do not output referenced-table columns directly; use this table's visible columns only. Runtime/category config handles fk_dak scoping.",
            "Do not skip this table. If the table is weak, return the best valid source plan from visible columns.",
        ],
        "forensic_feature_priorities": FORENSIC_FEATURE_PRIORITIES,
        "business_workflow_context": {
            "normal_flow": GEM_PAYMENT_FLOW,
            "dak_link_rule": GEM_DAK_LINK_RULE,
            "product_link_rule": GEM_PRODUCT_LINK_RULE,
            "gem_section_ids": GEM_DAK_SECTION_IDS,
        },
        "gem_feature_rules": load_gem_feature_rules(),
        "validation_context": validation_context,
        "feature_contract": get_feature_contract(),
        "output_contract": {
            "format": "json_object",
            "shape": {
                "source": {
                    "table": table_name,
                    "id_column": "exact id/primary key column from full_usable_columns",
                    "amount_column": "exact numeric money/value column from full_usable_columns",
                    "context_columns": ["exact columns useful for grouping/comparison"],
                    "date_column": "exact date/timestamp column or null",
                    "why_this_source": "short reason grounded in visible columns and GEM flow",
                    "feature_plan": [
                        {
                            "name": "stable feature name",
                            "op": "operation from feature_contract.supported_operations",
                            "source": "amount or event_date, required for amount/date operations",
                            "group_by": "selected context column, required for group operations",
                            "column": "selected column, required for single-column rule operations",
                            "columns": "selected columns, required for duplicate/rolling-window operations",
                            "left": "selected left column, required for date_after",
                            "right": "selected right column, required for date_after or numeric comparison",
                            "condition_column": "selected condition column for conditional missing rules",
                            "value": "literal value for equals, starts_with, missing_when_equals, or numeric threshold",
                            "params": "optional operation parameters",
                            "reason": "why this feature matters for GEM bill payment risk",
                        }
                    ],
                },
                "guide_markdown": "short markdown note for this GEM table",
            },
        },
        "table": table_name,
        "row_count": table_detail["row_count"],
        "column_count": table_detail["column_count"],
        "usable_column_count": table_detail["usable_column_count"],
        "full_usable_columns": full_usable_columns,
        "relationship_context": table_detail.get("relationship_context", []),
    }


def ask_llama_to_plan_table(table_detail):
    table_name = table_detail["table"]
    echo(f"Asking the LLM to plan GEM features for {table_name}.")
    prompt = build_table_feature_prompt(table_detail)
    response = create_tpp_architecture_completion(prompt)
    raw_text = response.choices[0].message.content.strip()
    echo(f"Raw LLM GEM feature-plan response length for {table_name}: {len(raw_text)} characters.")

    try:
        payload = parse_llama_json_object(raw_text)
    except (json.JSONDecodeError, ValueError, RuntimeError) as exc:
        save_bad_llama_response(raw_text)
        raise RuntimeError(
            f"LLM returned invalid GEM feature-plan JSON for {table_name}. "
            f"Raw response saved to {LAST_BAD_RESPONSE_FILE}. Detail: {exc}"
        ) from exc

    source = payload.get("source")
    if not isinstance(source, dict):
        raise RuntimeError(f"LLM did not return a `source` object for {table_name}.")

    source["table"] = table_name
    return source, str(payload.get("guide_markdown", "")).strip()


def filter_source_to_visible_columns(source, table_detail):
    visible_columns = {column["column"] for column in table_detail["columns"]}
    if source.get("id_column") not in visible_columns or source.get("amount_column") not in visible_columns:
        return None
    if source.get("date_column") and source["date_column"] not in visible_columns:
        source["date_column"] = None
    source["context_columns"] = [
        column
        for column in source.get("context_columns", [])
        if isinstance(column, str) and column in visible_columns
    ]
    source["feature_plan"] = validate_feature_plan(
        source.get("feature_plan", []),
        {
            "context_columns": source["context_columns"],
            "date_column": source.get("date_column"),
        },
    )
    return source if source["feature_plan"] else None


def ask_llama_for_architecture(schema_rows):
    ensure_ollama_is_running()
    _, table_details = build_llama_table_inventory(schema_rows)
    selected_tables = [table for table in BUSINESS_PRIORITY_TABLES if table in table_details]
    missing_required_tables = [table for table in BUSINESS_PRIORITY_TABLES if table not in table_details]
    echo(
        "Planning GEM_BILLS source tables. "
        f"Available={len(selected_tables)}, missing_or_unscorable={len(missing_required_tables)}."
    )
    if missing_required_tables:
        echo(f"Missing/unscorable GEM table(s): {', '.join(missing_required_tables)}")

    sources = []
    guide_notes = []
    for table in selected_tables:
        table_detail = table_details.get(table)
        if not table_detail:
            continue
        try:
            source, guide_note = ask_llama_to_plan_table(table_detail)
        except RuntimeError as exc:
            echo(str(exc))
            continue
        source = filter_source_to_visible_columns(source, table_detail)
        if not source:
            echo(f"Rejected LLM GEM source for {table}: required columns were not usable.")
            continue
        sources.append(source)
        if guide_note:
            guide_notes.append(f"### {table}\n\n{guide_note}")

    if not sources:
        raise RuntimeError("LLM did not produce any usable GEM source plan.")
    return {"sources": sources, "guide_markdown": "\n\n".join(guide_notes)}


def write_outputs(payload):
    with open(GEM_SOURCE_CONFIG_FILE, "w", encoding="utf-8") as output_file:
        json.dump(payload["sources"], output_file, indent=2)
    with open(GEM_OUTPUT_FILE, "w", encoding="utf-8") as guide_file:
        guide_file.write(payload.get("guide_markdown", "").strip() + "\n")
    echo(f"Wrote GEM anomaly source config to {GEM_SOURCE_CONFIG_FILE}")
    echo(f"Wrote GEM anomaly guide to {GEM_OUTPUT_FILE}")


def main():
    schema_rows = parse_schema_file(SCHEMA_FILE)
    payload = ask_llama_for_architecture(schema_rows)
    write_outputs(payload)


if __name__ == "__main__":
    main()
