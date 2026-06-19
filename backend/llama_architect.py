import json
import os
import re
import urllib.error
import urllib.request
from functools import lru_cache
from pathlib import Path

import psycopg2
from psycopg2 import sql
from openai import OpenAI

from db_config import get_database_settings, get_llama_settings
from feature_dsl import get_feature_contract, validate_feature_plan
from table_exclusions import DEFAULT_BUSINESS_PRIORITY_TABLES, EXCLUDED_TABLES, is_excluded_table


BACKEND_DIR = Path(__file__).resolve().parent

SCHEMA_FILE = str(BACKEND_DIR / "tulip2.0_schema.md")
OUTPUT_FILE = str(BACKEND_DIR / "anomaly_guide.md")
SOURCE_CONFIG_FILE = str(BACKEND_DIR / "anomaly_sources.json")
LAST_BAD_RESPONSE_FILE = BACKEND_DIR / "last_llama_architect_response.txt"
SCHEMA_CANDIDATE_AUDIT_FILE = BACKEND_DIR / "llama_schema_candidates.json"
ARCHITECT_VERSION = "2026-06-18-validation-context-v9"
DEFAULT_THIRD_PARTY_ARCHITECT_TABLES = (
    *DEFAULT_BUSINESS_PRIORITY_TABLES,
)
DEFAULT_VALIDATION_CONTEXT_FILES = (
    Path("/home/ruthikreddy/Documents/validation_files/THIRD_PARTY_PAYMENTS_VALIDATION.md"),
)
BUSINESS_WORKFLOW_CONTEXT = {
    "normal_flow": (
        "dak -> bill -> cheque_slip -> punching_medium -> schedule3 -> ecs"
    ),
    "business_rules": [
        "Only THIRD_PARTY_PAYMENTS dak rows are in scope: dak.fk_section IN (142, 228, 265, 383).",
        "A dak normally flows through bill, cheque_slip, punching_medium, schedule3, and ecs.",
        "Rejected records can stop in the middle and should not be forced into later stages.",
        "Verified or accepted records should continue to the next stage in the common flow.",
        "Later-stage rows without the expected earlier-stage row are suspicious.",
        "A valid-looking final payment with broken upstream trail is suspicious.",
        "Approved/valid records that do not move forward can be suspicious.",
        "Rejected/invalid records that move forward into payment stages are suspicious.",
        "Multiple downstream records for one upstream record can indicate duplicate or split payment behavior.",
        "Use id, fk_dak, fk_bill, fk_cheque_slip, fk_schedule3, fk_punching_medium, amount, date, status, approved, passed, rejected, invoice, reference, and payment columns to understand movement between tables.",
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
MAX_VALIDATION_RULES_PER_TABLE = int(os.getenv("LLAMA_MAX_VALIDATION_RULES_PER_TABLE", "60"))
MAX_VALIDATION_RULES_PER_PROMPT = int(os.getenv("LLAMA_MAX_VALIDATION_RULES_PER_PROMPT", "100"))
ALWAYS_INCLUDE_COLUMN_NAMES = ("approved", "record_status")
def get_architect_source_tables() -> tuple[str, ...]:
    configured = os.getenv("ARCHITECT_SOURCE_TABLES")
    raw_tables = configured if configured is not None else ",".join(DEFAULT_THIRD_PARTY_ARCHITECT_TABLES)
    tables = []
    seen = set()
    for table in raw_tables.split(","):
        table = table.strip()
        if not table or table in seen or is_excluded_table(table):
            continue
        tables.append(table)
        seen.add(table)
    return tuple(tables)


BUSINESS_PRIORITY_TABLES = get_architect_source_tables()


def is_architect_source_table(table_name: str) -> bool:
    return table_name in set(BUSINESS_PRIORITY_TABLES)


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


def configured_validation_context_paths() -> tuple[Path, ...]:
    configured = os.getenv("ARCHITECT_VALIDATION_CONTEXT_FILES", "").strip()
    if configured:
        raw_paths = re.split(r"[,;]", configured)
        return tuple(Path(path.strip()).expanduser() for path in raw_paths if path.strip())

    paths = [path for path in DEFAULT_VALIDATION_CONTEXT_FILES if path.exists()]
    context_dir = BACKEND_DIR / "validation_contexts"
    if context_dir.exists():
        paths.extend(sorted(context_dir.glob("*.md")))
    return tuple(paths)


def parse_validation_markdown(path: Path) -> list[dict]:
    rules = []
    table_row_pattern = re.compile(
        r"^\|\s*(?P<table>[^|]+?)\s*\|\s*(?P<column>[^|]+?)\s*\|\s*(?P<validation>.+?)\s*\|$"
    )

    with open(path, "r", encoding="utf-8") as validation_file:
        for raw_line in validation_file:
            line = raw_line.strip()
            if not line.startswith("|") or line.startswith("|---"):
                continue
            match = table_row_pattern.match(line)
            if not match:
                continue

            table = match.group("table").strip()
            column = match.group("column").strip()
            validation = match.group("validation").strip()
            if table == "table_name" or column == "column_name" or not validation:
                continue
            rules.append(
                {
                    "context_name": path.stem,
                    "table": table,
                    "column": column,
                    "validation": validation,
                }
            )
    return rules


@lru_cache(maxsize=1)
def load_validation_context_rules() -> tuple[dict, ...]:
    rules = []
    for path in configured_validation_context_paths():
        if not path.exists():
            echo(f"Validation context file not found, skipping: {path}")
            continue
        try:
            parsed_rules = parse_validation_markdown(path)
        except OSError as exc:
            echo(f"Could not read validation context file {path}: {exc}")
            continue
        echo(f"Loaded {len(parsed_rules)} validation rule(s) from {path}")
        rules.extend(parsed_rules)
    return tuple(rules)


def validation_rules_for_table(table_name: str) -> list[dict]:
    return [
        dict(rule)
        for rule in load_validation_context_rules()
        if rule["table"] == table_name
    ][:MAX_VALIDATION_RULES_PER_TABLE]


def validation_context_for_table_detail(table_detail: dict) -> list[dict]:
    selected_rules = validation_rules_for_table(table_detail["table"])
    seen = {(rule["table"], rule["column"], rule["validation"]) for rule in selected_rules}
    for relationship in table_detail.get("relationship_context", []):
        referenced_table = relationship.get("referenced_table")
        if not referenced_table:
            continue
        for rule in validation_rules_for_table(referenced_table):
            key = (rule["table"], rule["column"], rule["validation"])
            if key in seen:
                continue
            selected_rules.append(rule)
            seen.add(key)
            if len(selected_rules) >= MAX_VALIDATION_RULES_PER_PROMPT:
                return selected_rules
    return selected_rules[:MAX_VALIDATION_RULES_PER_PROMPT]


def validation_column_names_by_table() -> dict[str, set[str]]:
    by_table: dict[str, set[str]] = {}
    for rule in load_validation_context_rules():
        by_table.setdefault(rule["table"], set()).add(rule["column"])
    return by_table


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
    echo(f"Parsed {len(tables)} architect table(s) and {len(rows)} columns from schema.")
    return rows


def prune_schema_rows_to_allowed_relationships(schema_rows):
    root_tables = set(BUSINESS_PRIORITY_TABLES)
    return [
        row
        for row in schema_rows
        if row["table"] in root_tables and not is_excluded_table(row["table"])
    ]


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
        if is_excluded_table(table_name) or not is_architect_source_table(table_name):
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


def column_priority(column, validation_columns_by_table=None):
    validation_columns_by_table = validation_columns_by_table or {}
    column_non_null_ratio = non_null_ratio(column)
    is_validation_column = column["column"] in validation_columns_by_table.get(column.get("table"), set())
    if is_always_include_column(column):
        base_score = 120
    elif is_validation_column:
        base_score = 115
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


def trim_columns_for_llama(columns, validation_columns_by_table=None):
    validation_columns_by_table = validation_columns_by_table or {}
    usable_columns = filter_non_empty_columns(columns)
    validation_columns = [
        column
        for column in usable_columns
        if column["column"] in validation_columns_by_table.get(column.get("table"), set())
    ]
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
    append_unique_columns(
        ordered_columns,
        sorted(validation_columns, key=lambda column: column_priority(column, validation_columns_by_table), reverse=True),
    )
    append_unique_columns(
        ordered_columns,
        sorted(always_columns, key=lambda column: column_priority(column, validation_columns_by_table), reverse=True),
    )
    append_unique_columns(
        ordered_columns,
        sorted(pk_columns, key=lambda column: column_priority(column, validation_columns_by_table), reverse=True),
    )
    append_unique_columns(
        ordered_columns,
        sorted(numeric_columns, key=lambda column: column_priority(column, validation_columns_by_table), reverse=True),
    )
    append_unique_columns(
        ordered_columns,
        sorted(date_columns, key=lambda column: column_priority(column, validation_columns_by_table), reverse=True),
    )
    append_unique_columns(
        ordered_columns,
        sorted(fk_columns, key=lambda column: column_priority(column, validation_columns_by_table), reverse=True)[:MAX_CONTEXT_FK_COLUMNS],
    )
    append_unique_columns(
        ordered_columns,
        sorted(other_columns, key=lambda column: column_priority(column, validation_columns_by_table), reverse=True),
    )

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


def limited_compact_columns(columns, limit, validation_columns_by_table=None):
    return [
        compact_column_for_llama(column)
        for column in sorted(
            columns,
            key=lambda column: column_priority(column, validation_columns_by_table),
            reverse=True,
        )[:limit]
    ]


def direct_relationship_context(
    table_name,
    columns,
    all_tables,
    max_relationships=8,
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
                "referenced_columns": limited_compact_columns(
                    all_tables[referenced_table],
                    8,
                    validation_columns_by_table=validation_columns_by_table,
                ),
            }
        )
        if len(relationships) >= max_relationships:
            break
    return relationships


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
        "primary_keys": limited_compact_columns(pk_columns, 3, validation_columns_by_table),
        "amount_candidates": limited_compact_columns(amount_columns, 8, validation_columns_by_table),
        "date_candidates": limited_compact_columns(date_columns, 8, validation_columns_by_table),
        "context_candidates": limited_compact_columns(context_columns, 12, validation_columns_by_table),
        "status_candidates": limited_compact_columns(status_columns, 8, validation_columns_by_table),
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
    validation_columns = validation_column_names_by_table()
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
            "relationship_context": direct_relationship_context(
                table_name,
                usable_columns,
                all_tables,
                validation_columns_by_table=validation_columns,
            ),
            "validation_context": validation_rules_for_table(table_name),
            "column_count": len(profiled_columns),
            "usable_column_count": len(usable_columns),
            "sparse_column_fraction": round(sparse_column_fraction(profiled_columns), 4),
        }
        audit_candidates.append(
            {
                **summary,
                "business_priority": table_name in BUSINESS_PRIORITY_TABLES,
                "relationship_context": direct_relationship_context(
                    table_name,
                    usable_columns,
                    all_tables,
                    validation_columns_by_table=validation_columns,
                ),
                "validation_context": validation_rules_for_table(table_name),
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
    validation_columns = validation_column_names_by_table()
    table_columns = {
        table_name: columns
        for table_name, columns in tables.items()
        if table_name in requested_tables and is_architect_source_table(table_name)
    }
    profiles = profile_columns_from_database(table_columns)
    schema = []

    for table_name, columns in sorted(table_columns.items()):
        table_profile = profiles.get(table_name, {"row_count": 0, "columns": {}})
        profiled_columns = apply_column_profiles(columns, table_profile)
        trimmed_columns = trim_columns_for_llama(
            profiled_columns,
            validation_columns_by_table=validation_columns,
        )
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
            if table in known_tables and is_architect_source_table(table) and not is_excluded_table(table) and table not in candidate_tables:
                candidate_tables.append(table)

    # Some local model responses return a planning-only shape like {"tables": [{"name": "..."}]}.
    for source in payload.get("tables", []):
        if isinstance(source, dict):
            table = str(source.get("name") or source.get("table") or "").strip()
        else:
            table = str(source).strip()
        if table in known_tables and is_architect_source_table(table) and not is_excluded_table(table) and table not in candidate_tables:
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


FORENSIC_FEATURE_PRIORITIES = (
    {
        "signal": "broken_or_skipped_payment_flow",
        "design_hint": (
            "Prefer features that expose missing middle stages, downstream rows without upstream trail, "
            "weak final ECS/payment trail, dak-to-bill multiplicity, bill-to-payment multiplicity, "
            "and unusual movement across dak -> bill -> cheque_slip -> punching_medium -> schedule3 -> ecs."
        ),
    },
    {
        "signal": "status_approval_rejection_contradiction",
        "design_hint": (
            "Use record_status, approved, passed, cancelled, rejection/reason columns, payment-stage "
            "presence, and dates to detect approved records stuck upstream or rejected/invalid records "
            "moving forward into payment stages."
        ),
    },
    {
        "signal": "amount_and_payment_relationship_contradiction",
        "design_hint": (
            "Use claimed, passed, disallowed, recovery, cheque/payment, PM, schedule, ECS, and related "
            "amount columns where visible to compare amount-to-amount and amount-to-payment consistency."
        ),
    },
    {
        "signal": "date_sequence_and_stage_timing",
        "design_hint": (
            "Use date_after, date_in_future, age_days, day_of_week, hour, and rolling-window features "
            "to detect dates moving backwards in the payment chain, unusually fast movement, and delayed stages."
        ),
    },
    {
        "signal": "invoice_splitting_or_sanction_evasion",
        "design_hint": (
            "Use duplicate_normalized_key, rolling_window_count, rolling_window_amount_sum, "
            "duplicate_key, duplicate_distinct, group_frequency, group_rank_pct, "
            "ratio_to_group_median, and amount/date context to find the same vendor, "
            "invoice/reference, DAK, unit, supply order, contract, or GST identity split "
            "across multiple bills, nearby dates, or payment rows."
        ),
    },
    {
        "signal": "same_vendor_same_item_or_invoice_different_rate",
        "design_hint": (
            "Where item, invoice, vendor, bill type, supply order, contract, unit, GST, "
            "or narration columns are visible, compare amount against vendor/context group "
            "medians and use duplicate_distinct to flag same identity with different "
            "amounts, dates, DAKs, units, or beneficiaries."
        ),
    },
    {
        "signal": "fake_or_manipulated_invoice_identity",
        "design_hint": (
            "Prioritize invoice_number, bill_no, reference_no, fis_doc_no, invoice_date, "
            "bill_date, vendor, PAN/GSTIN-related FK context, duplicate invoice keys, "
            "future dates, impossible date order, and suspicious FIS prefix handling."
        ),
    },
    {
        "signal": "tax_or_payment_detail_evasion_inside_allowed_tables",
        "design_hint": (
            "Use gst_applicable, tax recovery, payment narration/detail, invoice, reference, "
            "vendor, beneficiary, and amount columns available inside the six allowed tables "
            "to surface fake-invoice or tax/payment detail inconsistencies."
        ),
    },
    {
        "signal": "bill_or_payment_overpayment_and_identity_mismatch",
        "design_hint": (
            "Use bill amount, claimed/passed/CDA/unit paid, cheque, PM, schedule, ECS, "
            "vendor/unit FK context, and grouped ratios to detect excess payment, duplicate "
            "payment identities, and vendor/unit mismatches implied by validation_context."
        ),
    },
    {
        "signal": "payment_routing_or_beneficiary_diversion",
        "design_hint": (
            "Use beneficiary, vendor, bank/account, payment mode, cheque slip, ECS, "
            "schedule, status, approval, and date columns to detect paid-to-party or "
            "account routing patterns that differ from the bill/vendor context."
        ),
    },
)


def build_table_feature_prompt(table_detail):
    table_name = table_detail["table"]
    full_usable_columns = [compact_column_for_llama(column) for column in table_detail["columns"]]
    validation_context = validation_context_for_table_detail(table_detail)

    return {
        "task": (
            "Act as a senior Government Accounts, Defence Audit, Payment Flow, and Forensic Analytics architect. "
            "Create one anomaly detection source plan for THIRD_PARTY_PAYMENTS only. "
            "The final model is Isolation Forest; your job is not to label fraud, but to design deterministic, "
            "machine-computable forensic features that help the model detect hidden suspicious payment behavior. "
            "Python removed empty and mostly-null columns before this prompt. Choose amount/date/context columns "
            "and engineered features from full_usable_columns. Use relationship_context to understand direct FK "
            "joins that runtime can enrich automatically. Strict table scope is dak, bill, cheque_slip, "
            "punching_medium, schedule3, ecs. Strict section scope is dak.fk_section IN (142, 228, 265, 383); "
            "all downstream records must belong to those dak rows. "
            "Use validation_context as business evidence, but do not turn it into a missing-column checklist. "
            "Design features for column-to-column contradictions, row-to-row repeated patterns, table-to-table "
            "flow breaks, skipped stages, status/payment contradictions, approval/downstream contradictions, "
            "rejection/payment contradictions, amount inconsistencies, date sequence violations, duplicate "
            "invoice/payment behavior, multiplicity, weak final payment trails, abnormal stage timing, and "
            "records that look normal alone but suspicious when compared with related rows."
        ),
        "strict_rules": [
            "Use only column names from full_usable_columns.",
            "Use only these tables in reasoning: dak, bill, cheque_slip, punching_medium, schedule3, ecs.",
            "Use only THIRD_PARTY_PAYMENTS section ids: 142, 228, 265, 383.",
            "Do not invent columns, formulas, or feature operations.",
            "Do not create final labels like fraud=true.",
            "Do not require LLM reasoning during scan time.",
            "Every feature must be deterministic, numeric, safe for null values, and explainable to an auditor.",
            "Do not convert validation_context into free-form SQL or boolean formulas; translate it into supported feature_contract operations only.",
            "The amount_column must be a real numeric money/value column from full_usable_columns; if no money-named column exists, choose the best non-PK/non-FK numeric measure.",
            "The id_column should normally be the primary key column if present.",
            "context_columns should be useful forensic grouping/comparison columns such as DAK, bill, cheque slip, schedule, ECS, vendor, beneficiary, bank/account, invoice/reference number, unit, section, bill type, payment mode, approval, passed, cancelled, rejection, and record_status.",
            "date_column must be a date/timestamp column from full_usable_columns, or null if none is suitable.",
            "Each feature_plan item must obey feature_contract exactly.",
            "Highest priority order: broken flow, skipped stages, downstream without upstream, rejected/invalid moving forward, approved/valid not moving forward, payment without approval trail, date sequence contradiction, amount relationship contradiction, duplicate invoice/payment pattern, abnormal row-to-row repetition, multiplicity, final ECS/payment with weak trail.",
            "Start feature_plan with forensic identity/amount/tax features when visible columns allow them; do not fill the plan with is_missing features.",
            "Use duplicate_key for repeated invoice/reference/FIS/DAK/bill/vendor/beneficiary/payment identities.",
            "Use duplicate_normalized_key when invoice/reference/FIS/DAK/bill/vendor/beneficiary/payment identifiers may differ only by spaces, punctuation, case, or formatting.",
            "Use duplicate_distinct when the same identity appears across different DAKs, beneficiaries, units, dates, invoice numbers, amounts, or vendors.",
            "Use rolling_window_count and rolling_window_amount_sum with params.window_days when vendor/invoice/reference/DAK/bill/payment identities repeat across nearby dates; this is the preferred expression for possible bill splitting.",
            "Use ratio_to_group_median, group_rank_pct, and group_frequency for vendor/unit/bill-type/payment-mode/routing amount inconsistency.",
            "Use numeric_gt and numeric_lt for amount integrity checks such as passed greater than claimed, CDA plus unit payment mismatch proxies, cheque/PM/schedule/ECS amount inconsistencies, or recovery/payment totals when comparable columns exist.",
            "Use date_after and date_in_future for invoice, bill, reference, FIS, cheque, PM, schedule, CMP, and ECS chronology issues.",
            "Use starts_with/equal flags for documented risky identifiers or statuses, such as FIS prefix 29 in normal TPP context, cancelled rows, invalid statuses, or payment modes when validation_context says they matter.",
            "Use is_missing, all_missing, missing_when_equals, and missing_when_present only when absence directly supports a forensic risk such as fake invoice identity, missing vendor/beneficiary for a payable row, missing payment trail, or missing tax/payment evidence on GST-applicable bills.",
            "For amount operations, source must be amount.",
            "For date operations, source must be event_date and date_column must not be null.",
            "For group operations, group_by must be one selected context column.",
            "When validation_context names a visible amount/date/context column, prefer it over generic columns if it helps detect third-party payment risk.",
            "Prefer FK context columns when their relationship_context adds useful business meaning.",
            "Use id and FK columns as the primary relationship path between tables.",
            "For flow tables, prefer fk_dak, fk_bill, fk_cheque_slip, fk_schedule3, status, approved, passed, rejected, and date columns when they exist.",
            "Do not output referenced-table columns directly; Python will join direct FK tables safely at runtime.",
            "Do not skip this table. If the table is weak, still return the best valid source plan from visible columns.",
        ],
        "forensic_feature_priorities": FORENSIC_FEATURE_PRIORITIES,
        "business_workflow_context": BUSINESS_WORKFLOW_CONTEXT,
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
                    "why_this_source": "short reason grounded in visible columns",
                    "feature_plan": [
                        {
                            "name": "stable feature name",
                            "op": "operation from feature_contract.supported_operations",
                            "source": "amount or event_date, required for amount/date operations",
                            "group_by": "selected context column, required for group operations",
                            "column": "selected column, required for single-column rule operations",
                            "columns": "selected columns, required for all_missing, duplicate, normalized duplicate, and rolling-window operations",
                            "left": "selected left column, required for date_after",
                            "right": "selected right column, required for date_after or numeric column comparison",
                            "condition_column": "selected condition column for conditional missing rules",
                            "value": "literal value for equals, starts_with, missing_when_equals, or numeric threshold",
                            "params": "optional operation parameters, e.g. {'window_days': 7} for rolling-window operations",
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


def ask_llama_to_plan_table(table_detail):
    table_name = table_detail["table"]
    full_usable_columns = [compact_column_for_llama(column) for column in table_detail["columns"]]
    echo(f"Asking the LLM to plan features for {table_name} using {len(full_usable_columns)} usable column(s).")

    prompt = build_table_feature_prompt(table_detail)

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
        "Planning every required ARCHITECT_SOURCE_TABLES root table. "
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
    repair_tables = [table["table"] for table in schema if isinstance(table, dict) and table.get("table")]
    validation_context = {
        table: validation_rules_for_table(table)
        for table in repair_tables
        if validation_rules_for_table(table)
    }
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
            "Use validation_context as business-rule guidance, but only with supported feature_contract operations.",
            "Return at least one source with at least two valid feature_plan items.",
        ],
        "excluded_tables": sorted(EXCLUDED_TABLES),
        "validation_context": validation_context,
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
        if not is_architect_source_table(table):
            rejected += 1
            echo(f"Rejected non-priority table outside ARCHITECT_SOURCE_TABLES: {table}")
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
    validation_paths = configured_validation_context_paths()
    lines = [
        "# Tulip 2.0 Anomaly Feature Guide",
        "",
        "This guide is generated by the configured local LLM from `tulip2.0_schema.md`.",
        "Python validates that every selected table, column, and feature operation exists before writing runtime config.",
        "",
        "## Validation Context Files",
        "",
        *(
            [f"- `{path}`" for path in validation_paths]
            if validation_paths
            else ["No validation context files were loaded."]
        ),
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
