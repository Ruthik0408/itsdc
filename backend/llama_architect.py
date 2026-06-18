import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

import psycopg2
from psycopg2 import sql
from openai import OpenAI

from db_config import get_database_settings, get_llama_settings
from feature_dsl import get_feature_contract, validate_feature_plan
from table_exclusions import EXCLUDED_TABLES, get_allowed_source_tables, is_allowed_source_table, is_excluded_table


BACKEND_DIR = Path(__file__).resolve().parent

SCHEMA_FILE = str(BACKEND_DIR / "tulip2.0_schema.md")
OUTPUT_FILE = str(BACKEND_DIR / "anomaly_guide.md")
SOURCE_CONFIG_FILE = str(BACKEND_DIR / "anomaly_sources.json")
LAST_BAD_RESPONSE_FILE = BACKEND_DIR / "last_llama_architect_response.txt"
SCHEMA_CANDIDATE_AUDIT_FILE = BACKEND_DIR / "llama_schema_candidates.json"
ARCHITECT_VERSION = "2026-06-17-business-priority-tables-v8"
BUSINESS_WORKFLOW_CONTEXT = {
    "normal_flow": (
        "dak -> exactly one first-stage bill table "
        "(bill, gem_bill, cash_requisition, civ_medical_bill, civ_paybill, "
        "civ_tada_ltc_bill, echs_medical_bill) -> cheque_slip -> "
        "punching_medium -> schedule3 -> ecs"
    ),
    "business_rules": [
        "A dak normally falls into one bill-type table first, not many.",
        "Rejected records can stop in the middle and should not be forced into later stages.",
        "Verified or accepted records should continue to the next stage in the common flow.",
        "Later-stage rows without the expected earlier-stage row are suspicious.",
        "Use id, fk_dak, fk_bill, fk_cheque_slip, fk_schedule3, fk_punching_medium, and related FK columns to understand movement between tables.",
    ],
}
MAX_LLM_SCHEMA_TABLES = int(os.getenv("LLAMA_MAX_SCHEMA_TABLES", "40"))
MAX_LLM_COLUMNS_PER_TABLE = int(os.getenv("LLAMA_MAX_COLUMNS_PER_TABLE", "15"))
MAX_PROFILE_TABLES = int(os.getenv("LLAMA_MAX_PROFILE_TABLES", "381"))
MAX_NULL_FRACTION = float(os.getenv("LLAMA_MAX_NULL_FRACTION", "0.80"))
MIN_AMOUNT_NON_NULL_RATIO = float(os.getenv("LLAMA_MIN_AMOUNT_NON_NULL_RATIO", "0.20"))
MIN_CONTEXT_NON_NULL_RATIO = float(os.getenv("LLAMA_MIN_CONTEXT_NON_NULL_RATIO", "0.20"))
MAX_TABLE_SPARSE_COLUMN_FRACTION = float(os.getenv("LLAMA_MAX_TABLE_SPARSE_COLUMN_FRACTION", "0.40"))
MAX_CONTEXT_FK_COLUMNS = int(os.getenv("LLAMA_MAX_CONTEXT_FK_COLUMNS", "6"))
ALWAYS_INCLUDE_COLUMN_NAMES = ("approved", "record_status")
BUSINESS_PRIORITY_TABLES = get_allowed_source_tables()
CONTEXT_COLUMN_PRIORITY_TERMS = (
    "vendor",
    "central_vendor",
    "unit",
    "central_unit",
    "section",
    "office",
    "employee",
    "type",
    "status",
    
)
AMOUNT_COLUMN_PRIORITY_TERMS = (
    "amount",
    "amt",
    "claimed",
    "passed",
    "tax",
    "gst",
    "disallowed",
)
DATE_COLUMN_PRIORITY_TERMS = (
    "created",
    "modified",
    "date",
    "approved",
    "passed",
)

NUMERIC_DATA_TYPES = (
    "bigint",
    "decimal",
    "double precision",
    "integer",
    "numeric",
    "real",
    "smallint",
)
DATE_DATA_TYPES = (
    "date",
    "timestamp",
    "timestamp with time zone",
    "timestamp without time zone",
)


llama_settings = get_llama_settings()
client = OpenAI(
    base_url=llama_settings["base_url"],
    api_key=llama_settings["api_key"],
)
LLAMA_MODEL = llama_settings["model"]


def echo(message):
    print(f"[llama_architect] {message}")


def ensure_llm_is_running():
    provider = llama_settings.get("provider", "ollama")
    echo(f"Checking {provider} LLM health at {llama_settings['health_url']}")
    request = urllib.request.Request(llama_settings["health_url"])
    # Browser-like User-Agent: Groq sits behind Cloudflare, which 403s the
    # default urllib agent even with a valid key.
    request.add_header("User-Agent", "Mozilla/5.0 (tulip-anomaly-architect)")
    api_key = llama_settings.get("api_key")
    if provider == "groq" and api_key:
        request.add_header("Authorization", f"Bearer {api_key}")
    try:
        urllib.request.urlopen(request, timeout=5)
    except urllib.error.URLError as exc:
        if provider == "groq":
            # The /models probe can be blocked at the edge (Cloudflare) even when
            # the chat endpoint works. Warn and continue; the real completion call
            # raises a clear error if auth is genuinely broken.
            echo(
                f"WARNING: Groq health probe failed ({exc}); continuing because the "
                "chat endpoint is the real dependency. If completions fail, check GROQ_API_KEY."
            )
            return
        hint = (
            "Start it in another terminal with: ollama serve"
            if provider == "ollama"
            else "Verify the server is up and VLLM_BASE_URL/VLLM_HEALTH_URL are correct."
        )
        raise RuntimeError(
            f"{provider} LLM is not reachable at {llama_settings['health_url']}. {hint}"
        ) from exc
    echo(f"{provider} LLM is reachable.")


# Backwards-compatible alias.
ensure_ollama_is_running = ensure_llm_is_running


def parse_schema_file(path):
    echo(f"Reading schema from {path}")
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
                    echo(f"Skipping excluded table from LLM schema: {current_table}")
                    current_table = None
                    continue
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

    rows = prune_schema_rows_to_allowed_relationships(rows)
    tables = {row["table"] for row in rows}
    echo(f"Parsed {len(tables)} allowed root/FK-linked tables and {len(rows)} columns from schema.")
    return rows


def prune_schema_rows_to_allowed_relationships(schema_rows):
    root_tables = set(BUSINESS_PRIORITY_TABLES)
    grouped = {}
    for row in schema_rows:
        grouped.setdefault(row["table"], []).append(row)

    visible_tables = {
        table
        for table in root_tables
        if table in grouped and not is_excluded_table(table)
    }
    for table in list(visible_tables):
        for row in grouped.get(table, []):
            referenced = row["references"]
            if referenced != "None" and referenced in grouped and not is_excluded_table(referenced):
                visible_tables.add(referenced)

    for table, rows in grouped.items():
        if table in visible_tables or is_excluded_table(table):
            continue
        if any(row["references"] in root_tables for row in rows):
            visible_tables.add(table)

    return [row for row in schema_rows if row["table"] in visible_tables]


def group_schema(schema_rows):
    tables = {}
    for row in schema_rows:
        tables.setdefault(row["table"], []).append(
            {
                "column": row["column"],
                "data_type": row["data_type"],
                "key": row["key"],
                "references": row["references"],
            }
        )
    return tables


def is_numeric_column(column):
    data_type = column["data_type"]
    return any(data_type.startswith(numeric_type) for numeric_type in NUMERIC_DATA_TYPES)


def is_date_column(column):
    data_type = column["data_type"]
    return any(data_type.startswith(date_type) for date_type in DATE_DATA_TYPES)


def non_null_ratio(column) -> float:
    return 1 - float(column.get("null_fraction", 1))


def is_amount_candidate_column(column) -> bool:
    return (
        column["key"] != "PK"
        and column["key"] != "FK"
        and is_numeric_column(column)
        and name_contains_any(column, AMOUNT_COLUMN_PRIORITY_TERMS)
        and non_null_ratio(column) >= MIN_AMOUNT_NON_NULL_RATIO
    )


def is_context_candidate_column(column) -> bool:
    return (
        non_null_ratio(column) >= MIN_CONTEXT_NON_NULL_RATIO
        and (column["key"] == "FK" or name_contains_any(column, CONTEXT_COLUMN_PRIORITY_TERMS))
    )


def sparse_column_fraction(profiled_columns) -> float:
    if not profiled_columns:
        return 1
    sparse_count = sum(
        1
        for column in profiled_columns
        if column.get("non_null_count", 0) == 0 or column.get("null_fraction", 1) >= MAX_NULL_FRACTION
    )
    return sparse_count / len(profiled_columns)


def score_table_for_llama(table_name, columns):
    pk_count = sum(1 for column in columns if column["key"] == "PK")
    fk_count = sum(1 for column in columns if column["key"] == "FK")
    numeric_count = sum(1 for column in columns if is_numeric_column(column))
    date_count = sum(1 for column in columns if is_date_column(column))
    # This only limits prompt size. The LLM still chooses final columns and features.
    return (
        min(numeric_count, 8) * 5
        + min(fk_count, 8) * 3
        + min(date_count, 4) * 2
        + min(pk_count, 2)
        + min(len(columns), 40) / 40
        + (1 if table_name else 0)
    )


def select_structural_profile_tables(schema_rows):
    tables = group_schema(schema_rows)
    scored_tables = []

    for table_name, columns in tables.items():
        if is_excluded_table(table_name) or not is_allowed_source_table(table_name):
            continue
        has_pk = any(column["key"] == "PK" for column in columns)
        if not has_pk:
            continue
        scored_item = (score_table_for_llama(table_name, columns), table_name, columns)
        scored_tables.append(scored_item)

    scored_tables.sort(key=lambda item: BUSINESS_PRIORITY_TABLES.index(item[1]))
    return scored_tables[:MAX_PROFILE_TABLES]


def profile_columns_from_database(table_columns):
    echo(f"Profiling non-null column ratios for {len(table_columns)} table(s).")
    profiles = {}
    conn = psycopg2.connect(**get_database_settings())

    try:
        with conn.cursor() as cur:
            cur.execute("SET statement_timeout = '20s';")
            for table_name, columns in table_columns.items():
                count_expressions = [
                    sql.SQL("COUNT({column})").format(column=sql.Identifier(column["column"]))
                    for column in columns
                ]
                query = sql.SQL("SELECT COUNT(*)::bigint, {counts} FROM {table}").format(
                    counts=sql.SQL(", ").join(count_expressions),
                    table=sql.Identifier("public", table_name),
                )
                try:
                    cur.execute(query)
                except psycopg2.Error as exc:
                    conn.rollback()
                    echo(f"Skipped table during non-null profiling because query failed: {table_name} ({exc.pgerror or exc})")
                    cur.execute("SET statement_timeout = '20s';")
                    continue
                result = cur.fetchone()
                row_count = int(result[0] or 0)
                column_counts = result[1:]
                table_profile = {"row_count": row_count, "columns": {}}

                for column, non_null_count in zip(columns, column_counts):
                    non_null_count = int(non_null_count or 0)
                    if row_count:
                        null_fraction = 1 - (non_null_count / row_count)
                    else:
                        null_fraction = 1
                    table_profile["columns"][column["column"]] = {
                        "non_null_count": non_null_count,
                        "null_fraction": round(null_fraction, 4),
                    }

                profiles[table_name] = table_profile
    finally:
        conn.close()

    return profiles


def apply_column_profiles(columns, table_profile):
    profiled_columns = []
    column_profiles = table_profile.get("columns", {})

    for column in columns:
        profile = column_profiles.get(column["column"], {})
        profiled_column = dict(column)
        profiled_column["non_null_count"] = int(profile.get("non_null_count", 0))
        profiled_column["null_fraction"] = float(profile.get("null_fraction", 1))
        profiled_columns.append(profiled_column)

    return profiled_columns


def filter_non_empty_columns(columns):
    if columns and "non_null_count" not in columns[0]:
        return columns
    return [
        column
        for column in columns
        if column.get("non_null_count", 0) > 0 and column.get("null_fraction", 1) < MAX_NULL_FRACTION
    ]


def name_contains_any(column, terms):
    column_name = column["column"].lower()
    reference_name = str(column.get("references", "")).lower()
    return any(term in column_name or term in reference_name for term in terms)


def is_always_include_column(column):
    return column["column"].lower() in ALWAYS_INCLUDE_COLUMN_NAMES


def column_priority(column):
    column_non_null_ratio = non_null_ratio(column)
    if is_always_include_column(column):
        base_score = 120
    elif column["key"] == "PK":
        base_score = 100
    elif is_date_column(column):
        base_score = 80
    elif is_numeric_column(column):
        base_score = 70
        if name_contains_any(column, AMOUNT_COLUMN_PRIORITY_TERMS):
            base_score += 25
    elif column["key"] == "FK":
        base_score = 45
        if name_contains_any(column, CONTEXT_COLUMN_PRIORITY_TERMS):
            base_score += 35
    elif name_contains_any(column, CONTEXT_COLUMN_PRIORITY_TERMS):
        base_score = 55
    else:
        base_score = 20
    if is_date_column(column) and name_contains_any(column, DATE_COLUMN_PRIORITY_TERMS):
        base_score += 15
    return base_score + (column_non_null_ratio * 10)


def append_unique_columns(target, source):
    for column in source:
        if column not in target:
            target.append(column)


def trim_columns_for_llama(columns):
    usable_columns = filter_non_empty_columns(columns)
    always_columns = [column for column in usable_columns if is_always_include_column(column)]
    pk_columns = [column for column in usable_columns if column["key"] == "PK"]
    numeric_columns = [
        column
        for column in usable_columns
        if column["key"] != "FK" and is_numeric_column(column)
    ]
    date_columns = [column for column in usable_columns if is_date_column(column)]
    fk_columns = [column for column in usable_columns if column["key"] == "FK"]
    other_columns = [
        column
        for column in usable_columns
        if column not in pk_columns
        and column not in numeric_columns
        and column not in date_columns
        and column not in fk_columns
    ]

    ordered_columns = []
    append_unique_columns(ordered_columns, sorted(always_columns, key=column_priority, reverse=True))
    append_unique_columns(ordered_columns, sorted(pk_columns, key=column_priority, reverse=True))
    append_unique_columns(ordered_columns, sorted(numeric_columns, key=column_priority, reverse=True))
    append_unique_columns(ordered_columns, sorted(date_columns, key=column_priority, reverse=True))
    append_unique_columns(
        ordered_columns,
        sorted(fk_columns, key=column_priority, reverse=True)[:MAX_CONTEXT_FK_COLUMNS],
    )
    append_unique_columns(ordered_columns, sorted(other_columns, key=column_priority, reverse=True))

    return ordered_columns[:MAX_LLM_COLUMNS_PER_TABLE]


def removed_sparse_columns(columns):
    return [
        {
            "column": column["column"],
            "data_type": column["data_type"],
            "key": column["key"],
            "non_null_count": column.get("non_null_count", 0),
            "null_fraction": column.get("null_fraction", 1),
        }
        for column in columns
        if column.get("non_null_count", 0) == 0 or column.get("null_fraction", 1) >= MAX_NULL_FRACTION
    ]


def compact_column_for_llama(column):
    key = f":{column['key']}" if column["key"] else ""
    reference = f"->{column['references']}" if column["references"] != "None" else ""
    non_null_ratio = 1 - float(column.get("null_fraction", 0))
    return f"{column['column']}:{column['data_type']}{key}{reference}:nn={non_null_ratio:.0%}"


def write_schema_candidate_audit(candidates):
    with open(SCHEMA_CANDIDATE_AUDIT_FILE, "w", encoding="utf-8") as output_file:
        json.dump(candidates, output_file, indent=2)
    echo(f"Wrote Python-selected LLM schema candidates to {SCHEMA_CANDIDATE_AUDIT_FILE}")


def limited_compact_columns(columns, limit):
    return [compact_column_for_llama(column) for column in sorted(columns, key=column_priority, reverse=True)[:limit]]


def direct_relationship_context(table_name, columns, all_tables, max_relationships=8):
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
                "referenced_columns": limited_compact_columns(all_tables[referenced_table], 8),
            }
        )
        if len(relationships) >= max_relationships:
            break
    return relationships


def build_table_summary_for_llama(table_name, profiled_columns, table_profile, score):
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
            or is_always_include_column(column)
            or name_contains_any(column, CONTEXT_COLUMN_PRIORITY_TERMS)
        ]
    status_columns = [
        column
        for column in usable_columns
        if is_always_include_column(column) or name_contains_any(column, ("status", "approved", "active", "state"))
    ]

    return {
        "table": table_name,
        "row_count": table_profile.get("row_count", 0),
        "column_count": len(profiled_columns),
        "usable_column_count": len(usable_columns),
        "sparse_column_fraction": round(sparse_column_fraction(profiled_columns), 4),
        "score": round(score, 4),
        "primary_keys": limited_compact_columns(pk_columns, 3),
        "amount_candidates": limited_compact_columns(amount_columns, 8),
        "date_candidates": limited_compact_columns(date_columns, 8),
        "context_candidates": limited_compact_columns(context_columns, 12),
        "status_candidates": limited_compact_columns(status_columns, 8),
        "fk_relationships": [
            {
                "source_fk": column["column"],
                "referenced_table": column["references"],
            }
            for column in context_columns
            if column["key"] == "FK" and column["references"] != "None"
        ][:8],
    }


def build_llama_table_inventory(schema_rows):
    all_tables = group_schema(schema_rows)
    profile_candidates = select_structural_profile_tables(schema_rows)
    table_columns = {
        table_name: columns
        for _, table_name, columns in profile_candidates
    }
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
        context_columns = [column for column in usable_columns if is_context_candidate_column(column)]
        if not context_columns:
            context_columns = [
                column
                for column in usable_columns
                if column["key"] == "FK"
                or is_always_include_column(column)
                or name_contains_any(column, CONTEXT_COLUMN_PRIORITY_TERMS)
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
        table_score += min(len(context_columns), 6) * 3
        table_score -= table_sparse_fraction * 40
        scored_tables.append((table_score, table_name, profiled_columns, table_profile))

    priority_scored_tables = [
        item
        for item in scored_tables
        if item[1] in BUSINESS_PRIORITY_TABLES
    ]
    priority_scored_tables.sort(key=lambda item: BUSINESS_PRIORITY_TABLES.index(item[1]))
    selected_tables = priority_scored_tables[:MAX_LLM_SCHEMA_TABLES]
    summaries = []
    table_details = {}

    for score, table_name, profiled_columns, table_profile in selected_tables:
        usable_columns = filter_non_empty_columns(profiled_columns)
        summary = build_table_summary_for_llama(table_name, profiled_columns, table_profile, score)
        summaries.append(summary)
        table_details[table_name] = {
            "table": table_name,
            "row_count": table_profile.get("row_count", 0),
            "columns": sorted(usable_columns, key=column_priority, reverse=True),
            "relationship_context": direct_relationship_context(table_name, usable_columns, all_tables),
            "column_count": len(profiled_columns),
            "usable_column_count": len(usable_columns),
            "sparse_column_fraction": round(sparse_column_fraction(profiled_columns), 4),
        }
        audit_candidates.append(
            {
                **summary,
                "business_priority": table_name in BUSINESS_PRIORITY_TABLES,
                "relationship_context": direct_relationship_context(table_name, usable_columns, all_tables),
                "full_usable_columns_for_stage_2": [
                    {
                        "column": column["column"],
                        "data_type": column["data_type"],
                        "key": column["key"],
                        "references": column["references"],
                        "non_null_count": column.get("non_null_count", 0),
                        "null_fraction": column.get("null_fraction", 1),
                    }
                    for column in sorted(usable_columns, key=column_priority, reverse=True)
                ],
                "removed_sparse_columns": removed_sparse_columns(profiled_columns),
            }
        )

    echo(
        "Prepared "
        f"{len(summaries)} table summary candidate(s) for LLM planning "
        f"(max_tables={MAX_LLM_SCHEMA_TABLES}, "
        f"max_null_fraction={MAX_NULL_FRACTION})."
    )
    write_schema_candidate_audit(audit_candidates)
    return summaries, table_details


def select_schema_candidates_for_llama(schema_rows):
    summaries, _ = build_llama_table_inventory(schema_rows)
    return [
        {
            "table": summary["table"],
            "columns": (
                summary["primary_keys"]
                + summary["amount_candidates"]
                + summary["date_candidates"]
                + summary["context_candidates"][:MAX_CONTEXT_FK_COLUMNS]
                + summary["status_candidates"]
            )[:MAX_LLM_COLUMNS_PER_TABLE],
            "row_count": summary["row_count"],
            "column_count": summary["column_count"],
            "usable_column_count": summary["usable_column_count"],
        }
        for summary in summaries
    ]


def compact_schema_subset_for_llama(schema_rows, table_names):
    requested_tables = set(table_names)
    tables = group_schema(schema_rows)
    table_columns = {
        table_name: columns
        for table_name, columns in tables.items()
        if table_name in requested_tables and is_allowed_source_table(table_name)
    }
    profiles = profile_columns_from_database(table_columns)
    schema = []

    for table_name, columns in sorted(table_columns.items()):
        table_profile = profiles.get(table_name, {"row_count": 0, "columns": {}})
        profiled_columns = apply_column_profiles(columns, table_profile)
        trimmed_columns = trim_columns_for_llama(profiled_columns)
        if not trimmed_columns:
            continue
        schema.append(
            {
                "table": table_name,
                "columns": [compact_column_for_llama(column) for column in trimmed_columns],
                "row_count": table_profile.get("row_count", 0),
                "column_count": len(profiled_columns),
                "usable_column_count": len(filter_non_empty_columns(profiled_columns)),
            }
        )

    return schema


def extract_candidate_tables_from_payload(payload, schema_rows):
    known_tables = set(group_schema(schema_rows))
    candidate_tables = []

    for source in payload.get("sources", []):
        if isinstance(source, dict):
            table = str(source.get("table", "")).strip()
            if table in known_tables and is_allowed_source_table(table) and not is_excluded_table(table) and table not in candidate_tables:
                candidate_tables.append(table)

    # Some local model responses return a planning-only shape like {"tables": [{"name": "..."}]}.
    for source in payload.get("tables", []):
        if isinstance(source, dict):
            table = str(source.get("name") or source.get("table") or "").strip()
        else:
            table = str(source).strip()
        if table in known_tables and is_allowed_source_table(table) and not is_excluded_table(table) and table not in candidate_tables:
            candidate_tables.append(table)

    return candidate_tables


def extract_first_json_object(raw_text):
    text = raw_text.strip()
    if text.startswith("```"):
        fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL)
        if fence_match:
            text = fence_match.group(1).strip()

    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object start `{` found in LLM response.")

    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    raise ValueError("No balanced JSON object found in LLM response.")


def parse_llama_json_object(raw_text):
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        json_text = extract_first_json_object(raw_text)
        payload = json.loads(json_text)

    if not isinstance(payload, dict):
        raise RuntimeError("LLM architecture output must be a JSON object.")
    return payload


def save_bad_llama_response(raw_text):
    with open(LAST_BAD_RESPONSE_FILE, "w", encoding="utf-8") as output_file:
        output_file.write(raw_text)


def create_llama_architecture_completion(prompt):
    messages = [
        {
            "role": "system",
            "content": (
                "Return only valid JSON. Never invent table names, column names, "
                "feature operations, or formulas."
            ),
        },
        {"role": "user", "content": json.dumps(prompt, indent=2)},
    ]
    try:
        return client.chat.completions.create(
            model=LLAMA_MODEL,
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
        )
    except Exception as exc:
        echo(
            "JSON response_format was not accepted by the LLM endpoint; "
            f"retrying without it. Detail: {type(exc).__name__}: {exc}"
        )
        return client.chat.completions.create(
            model=LLAMA_MODEL,
            messages=messages,
            temperature=0,
        )


def ask_llama_to_plan_table(table_detail):
    table_name = table_detail["table"]
    full_usable_columns = [compact_column_for_llama(column) for column in table_detail["columns"]]
    echo(f"Asking the LLM to plan features for {table_name} using {len(full_usable_columns)} usable column(s).")

    prompt = {
        "task": (
            "Create one anomaly detection source plan for this required root table. "
            "Python removed empty and mostly-null columns before this prompt. "
            "Choose amount/date/context columns and engineered features from full_usable_columns. "
            "Use relationship_context to understand direct FK joins that runtime can enrich automatically. "
            "The user requires analysis across all 20 root tables and their table-to-table relationships. "
            "Use the business_workflow_context to prefer features that help detect wrong routing, missing stages, "
            "unexpected rejection/acceptance patterns, or unusual movement through the payment flow."
        ),
        "strict_rules": [
            "Use only column names from full_usable_columns.",
            "Do not invent columns, formulas, or feature operations.",
            "The amount_column must be a real numeric money/value column from full_usable_columns; if no money-named column exists, choose the best non-PK/non-FK numeric measure.",
            "The id_column should normally be the primary key column if present.",
            "context_columns should be useful grouping/comparison columns such as vendor, unit, central unit, section, employee, status, type, mode, approved, or record_status.",
            "date_column must be a date/timestamp column from full_usable_columns, or null if none is suitable.",
            "Each feature_plan item must obey feature_contract exactly.",
            "For amount operations, source must be amount.",
            "For date operations, source must be event_date and date_column must not be null.",
            "For group operations, group_by must be one selected context column.",
            "Prefer FK context columns when their relationship_context adds useful business meaning.",
            "Use id and FK columns as the primary relationship path between tables.",
            "For flow tables, prefer fk_dak, fk_bill, fk_cheque_slip, fk_schedule3, status, approved, passed, rejected, and date columns when they exist.",
            "Do not output referenced-table columns directly; Python will join direct FK tables safely at runtime.",
            "Do not skip this table. If the table is weak, still return the best valid source plan from visible columns.",
        ],
        "business_workflow_context": BUSINESS_WORKFLOW_CONTEXT,
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
                    "why_this_source": "short reason grounded in visible columns",
                    "feature_plan": [
                        {
                            "name": "stable feature name",
                            "op": "operation from feature_contract.supported_operations",
                            "source": "amount or event_date, required for amount/date operations",
                            "group_by": "selected context column, required for group operations",
                            "params": "optional operation parameters",
                            "reason": "why this feature is important",
                        }
                    ],
                },
                "guide_markdown": "short markdown note for this table",
            },
        },
        "table": table_name,
        "row_count": table_detail["row_count"],
        "column_count": table_detail["column_count"],
        "usable_column_count": table_detail["usable_column_count"],
        "full_usable_columns": full_usable_columns,
        "relationship_context": table_detail.get("relationship_context", []),
    }

    response = create_llama_architecture_completion(prompt)
    raw_text = response.choices[0].message.content.strip()
    echo(f"Raw LLM feature-plan response length for {table_name}: {len(raw_text)} characters.")

    try:
        payload = parse_llama_json_object(raw_text)
    except (json.JSONDecodeError, ValueError, RuntimeError) as exc:
        save_bad_llama_response(raw_text)
        raise RuntimeError(
            f"LLM returned invalid feature-plan JSON for {table_name}. "
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
    return source


def make_feature_name(table: str, suffix: str) -> str:
    base = re.sub(r"[^A-Za-z0-9_]+", "_", table).strip("_")
    if not base or not base[0].isalpha():
        base = f"source_{base}" if base else "source"
    return f"{base}_{suffix}"[:80]


def build_fallback_feature_plan(table: str, context_columns: list[str], date_column: str | None) -> list[dict]:
    raw_plan = [
        {
            "name": make_feature_name(table, "amount_log"),
            "op": "log",
            "source": "amount",
            "reason": "Stabilizes amount scale so extreme values can be compared with normal rows.",
        },
        {
            "name": make_feature_name(table, "amount_rank_pct"),
            "op": "rank_pct",
            "source": "amount",
            "reason": "Shows where the amount sits in the scanned table distribution.",
        },
        {
            "name": make_feature_name(table, "amount_to_p95"),
            "op": "ratio_to_quantile",
            "source": "amount",
            "params": {"quantile": 0.95},
            "reason": "Compares each amount against the high-value range for the table.",
        },
    ]

    for column in context_columns[:2]:
        raw_plan.extend(
            [
                {
                    "name": make_feature_name(table, f"{column}_frequency"),
                    "op": "group_frequency",
                    "group_by": column,
                    "reason": f"Captures whether this {column} appears rarely or frequently in the scan.",
                },
                {
                    "name": make_feature_name(table, f"amount_to_{column}_median"),
                    "op": "ratio_to_group_median",
                    "group_by": column,
                    "reason": f"Compares amount with the normal amount pattern for the same {column}.",
                },
            ]
        )

    if date_column:
        raw_plan.extend(
            [
                {
                    "name": make_feature_name(table, "age_days"),
                    "op": "age_days",
                    "source": "event_date",
                    "reason": "Captures recency compared with the newest scanned row.",
                },
                {
                    "name": make_feature_name(table, "day_of_week"),
                    "op": "day_of_week",
                    "source": "event_date",
                    "reason": "Captures unusual weekday timing patterns.",
                },
            ]
        )

    return validate_feature_plan(
        raw_plan,
        {
            "context_columns": context_columns,
            "date_column": date_column,
        },
    )


def ask_llama_for_architecture(schema_rows):
    ensure_ollama_is_running()
    table_summaries, table_details = build_llama_table_inventory(schema_rows)
    selected_tables = [
        table
        for table in BUSINESS_PRIORITY_TABLES
        if table in table_details
    ]
    missing_required_tables = [
        table
        for table in BUSINESS_PRIORITY_TABLES
        if table not in table_details
    ]
    echo(
        "Planning every required LLAMA_BUSINESS_PRIORITY_TABLES root table. "
        f"Available={len(selected_tables)}, missing_or_unscorable={len(missing_required_tables)}."
    )
    if missing_required_tables:
        echo(f"Missing/unscorable required table(s): {', '.join(missing_required_tables)}")

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
            echo(f"Rejected LLM source for {table}: required columns were not in full usable columns.")
            continue
        sources.append(source)
        if guide_note:
            guide_notes.append(f"### {table}\n\n{guide_note}")

    if not sources:
        raise RuntimeError("LLM did not produce any usable source plan in stage 2.")

    return {
        "sources": sources,
        "guide_markdown": "\n\n".join(guide_notes),
    }


def repair_architecture_payload(payload, schema_rows, validation_error):
    candidate_tables = extract_candidate_tables_from_payload(payload, schema_rows)
    if candidate_tables:
        schema = compact_schema_subset_for_llama(schema_rows, candidate_tables)
    else:
        schema = select_schema_candidates_for_llama(schema_rows)
    echo(f"Asking the LLM to repair architecture JSON using {len(schema)} table schema(s).")

    prompt = {
        "task": (
            "Repair your previous architecture JSON. The previous answer failed validation. "
            "Return only the required JSON object with top-level `sources` and `guide_markdown`."
        ),
        "validation_error": str(validation_error),
        "previous_response": payload,
        "strict_rules": [
            "Use only the table and column names present in schema.",
            "Do not use excluded_tables.",
            "Each source must include table, id_column, amount_column, context_columns, date_column, why_this_source, and feature_plan.",
            "Each feature_plan item must obey feature_contract exactly.",
            "Return at least one source with at least two valid feature_plan items.",
        ],
        "excluded_tables": sorted(EXCLUDED_TABLES),
        "feature_contract": get_feature_contract(),
        "output_contract": {
            "sources": [
                {
                    "table": "exact table name from schema",
                    "id_column": "exact id/primary key column from that table",
                    "amount_column": "exact numeric money/value column from that table",
                    "context_columns": ["exact columns useful for grouping/comparison"],
                    "date_column": "exact date/timestamp column or null",
                    "why_this_source": "short reason grounded in schema columns",
                    "feature_plan": [
                        {
                            "name": "stable feature name",
                            "op": "operation from feature_contract.supported_operations",
                            "source": "amount or event_date, required for amount/date operations",
                            "group_by": "selected context column, required for group operations",
                            "params": "optional operation parameters",
                            "reason": "why this feature is important",
                        }
                    ],
                }
            ],
            "guide_markdown": "concise markdown explaining the selected architecture",
        },
        "schema": schema,
    }

    response = create_llama_architecture_completion(prompt)
    raw_text = response.choices[0].message.content.strip()
    echo(f"Raw repaired LLM architecture response length: {len(raw_text)} characters.")

    try:
        repaired_payload = parse_llama_json_object(raw_text)
    except (json.JSONDecodeError, ValueError, RuntimeError) as exc:
        save_bad_llama_response(raw_text)
        raise RuntimeError(
            "LLM returned invalid repaired architecture JSON. "
            f"Raw response saved to {LAST_BAD_RESPONSE_FILE}. Detail: {exc}"
        ) from exc

    if "sources" not in repaired_payload:
        save_bad_llama_response(raw_text)
        raise RuntimeError(
            "LLM repair returned JSON, but still missed the required top-level `sources` array. "
            f"Raw response saved to {LAST_BAD_RESPONSE_FILE}."
        )

    return repaired_payload


def validate_architecture(payload, schema_rows):
    tables = group_schema(schema_rows)
    accepted_sources = []
    rejected = 0

    for raw_source in payload.get("sources", []):
        if not isinstance(raw_source, dict):
            rejected += 1
            continue

        table = str(raw_source.get("table", "")).strip()
        if is_excluded_table(table):
            rejected += 1
            echo(f"Rejected excluded table: {table}")
            continue
        if not is_allowed_source_table(table):
            rejected += 1
            echo(f"Rejected non-priority table outside LLAMA_BUSINESS_PRIORITY_TABLES: {table}")
            continue
        if table not in tables:
            rejected += 1
            echo(f"Rejected hallucinated table: {table}")
            continue

        columns = {column["column"] for column in tables[table]}
        id_column = str(raw_source.get("id_column", "")).strip()
        amount_column = str(raw_source.get("amount_column", "")).strip()
        date_column = raw_source.get("date_column")
        date_column = str(date_column).strip() if date_column else None

        if id_column not in columns or amount_column not in columns:
            rejected += 1
            echo(f"Rejected invalid source columns for {table}")
            continue
        if date_column and date_column not in columns:
            rejected += 1
            echo(f"Rejected invalid date column for {table}: {date_column}")
            continue

        context_columns = []
        for column in raw_source.get("context_columns", []):
            if isinstance(column, str) and column in columns and column not in context_columns:
                context_columns.append(column)

        source_for_validation = {
            "context_columns": context_columns,
            "date_column": date_column,
        }
        feature_plan = validate_feature_plan(raw_source.get("feature_plan", []), source_for_validation)

        if not feature_plan:
            feature_plan = build_fallback_feature_plan(table, context_columns, date_column)
            if feature_plan:
                echo(
                    f"Repaired source with deterministic fallback feature plan: "
                    f"{table} ({len(feature_plan)} feature(s))."
                )
            else:
                rejected += 1
                echo(f"Rejected source without usable feature plan: {table}")
                continue

        accepted_sources.append(
            {
                "table": table,
                "id_column": id_column,
                "amount_column": amount_column,
                "context_columns": context_columns,
                "date_column": date_column,
                "why_this_source": str(raw_source.get("why_this_source", "")).strip()[:300],
                "feature_plan": feature_plan,
            }
        )

    if not accepted_sources:
        raise RuntimeError("LLM did not return any schema-valid source with a usable feature plan.")

    echo(f"Accepted {len(accepted_sources)} source plan(s); rejected {rejected}.")
    return accepted_sources


def write_source_config(runtime_sources):
    with open(SOURCE_CONFIG_FILE, "w", encoding="utf-8") as output_file:
        json.dump(runtime_sources, output_file, indent=2)
    echo(f"Wrote {len(runtime_sources)} runtime source candidates to {SOURCE_CONFIG_FILE}")


def write_anomaly_guide(payload, runtime_sources):
    guide_markdown = str(payload.get("guide_markdown", "")).strip()
    lines = [
        "# Tulip 2.0 Anomaly Feature Guide",
        "",
        "This guide is generated by the configured local LLM from `tulip2.0_schema.md`.",
        "Python validates that every selected table, column, and feature operation exists before writing runtime config.",
        "",
        "## LLM Architecture Notes",
        "",
        guide_markdown or "The LLM did not provide additional narrative notes.",
        "",
        "## Runtime Sources And Feature Plans",
        "",
    ]

    for source in runtime_sources:
        lines.extend(
            [
                f"### {source['table']}",
                "",
                f"- ID column: `{source['id_column']}`",
                f"- Amount column: `{source['amount_column']}`",
                f"- Context columns: `{', '.join(source['context_columns']) or 'none'}`",
                f"- Date column: `{source['date_column'] or 'none'}`",
                f"- Why this source: {source['why_this_source'] or 'Selected by the LLM.'}",
                "",
                "Feature plan:",
            ]
        )
        for feature in source["feature_plan"]:
            column_text = f" by `{feature['group_by']}`" if feature.get("group_by") else ""
            source_text = f" from `{feature['source']}`" if feature.get("source") else ""
            param_text = f" params={feature['params']}" if feature.get("params") else ""
            lines.append(
                f"- `{feature['name']}` (`{feature['op']}`{source_text}{column_text}{param_text}): "
                f"{feature.get('reason') or 'Selected by the LLM.'}"
            )
        lines.append("")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
        output_file.write("\n".join(lines))
    echo(f"Wrote {len(lines)} markdown lines to {OUTPUT_FILE}")


def run_architect_loop():
    echo(f"Starting local-LLM schema architecture flow. version={ARCHITECT_VERSION}")
    schema_rows = parse_schema_file(SCHEMA_FILE)
    payload = ask_llama_for_architecture(schema_rows)
    try:
        runtime_sources = validate_architecture(payload, schema_rows)
    except RuntimeError as exc:
        echo(f"Initial LLM architecture failed validation: {exc}")
        payload = repair_architecture_payload(payload, schema_rows, exc)
        runtime_sources = validate_architecture(payload, schema_rows)
    write_source_config(runtime_sources)
    write_anomaly_guide(payload, runtime_sources)
    echo("Done. anomaly_sources.json and anomaly_guide.md were generated from LLM selections.")


if __name__ == "__main__":
    run_architect_loop()
