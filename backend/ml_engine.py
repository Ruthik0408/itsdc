import argparse
import datetime as dt
import json
import os
import re
import socket
import subprocess
import threading
import time
import warnings
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sklearn.ensemble import IsolationForest
from sklearn.exceptions import ConvergenceWarning
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import RobustScaler

try:
    from openai import OpenAI
except ModuleNotFoundError:
    OpenAI = None

from db_config import get_llama_settings, get_sqlalchemy_url
from feature_dsl import compute_feature_frame, validate_feature_plan
from gem_repeat_purchase_detector import detect_gem_repeat_purchase_anomalies
from payment_category_filtering import (
    JoinedContext,
    RuntimeSource,
    apply_payment_category_filters,
    normalize_payment_category,
    payment_category_dak_sections_from_config,
    payment_category_source_tables_from_config,
    resolve_allowed_physical_source_tables,
)
from supervision import (
    SUPERVISION_PROMOTE_PROXIMITY,
    SUPERVISION_SUPPRESS_PROXIMITY,
    compute_supervision_penalty,
    compute_supervision_boost,
    load_accepted_signatures,
    load_rejected_signatures,
    load_supervision_context_text,
)
from table_exclusions import (
    get_allowed_source_tables,
    is_excluded_table,
    is_allowed_source_table,
    load_payment_category_config,
    validate_payment_category_entry,
)


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

SCHEMA_FILE = str(BACKEND_DIR / "tulip2.0_schema.md")
SOURCE_CONFIG_FILE = str(BACKEND_DIR / "tpp_anomaly_sources.json")
SCHEMA_CANDIDATE_AUDIT_FILE = str(BACKEND_DIR / "tpp_schema_candidates.json")
DEFAULT_MAX_EXPLANATIONS = 500
DEFAULT_MAX_TABLES_PER_SCAN = 20
DEFAULT_ROWS_PER_TABLE = 1000
DEFAULT_CONTAMINATION = 0.02
DEFAULT_AUTOENCODER_CONFIRMATION_QUANTILE = 0.95
DEFAULT_DETECTION_STAGE = os.getenv("ANOMALY_DETECTION_STAGE", "isolation").strip().lower()
MAX_ANOMALIES_PER_FEATURE = int(os.getenv("MAX_ANOMALIES_PER_FEATURE", "2"))
# Persist in small batches so the dashboard fills progressively during a scan
# instead of staying empty until one giant transaction commits.
SAVE_COMMIT_BATCH_SIZE = int(os.getenv("SAVE_COMMIT_BATCH_SIZE", "25"))
# Guarantee model (IsolationForest/autoencoder) anomalies a share of the
# explanation budget so the high-volume workflow detector cannot starve them.
MODEL_ANOMALY_RESERVE_FRACTION = float(os.getenv("MODEL_ANOMALY_RESERVE_FRACTION", "0.5"))
MAX_CONFIG_CONTEXT_COLUMNS = int(os.getenv("MAX_CONFIG_CONTEXT_COLUMNS", "32"))
FUNCTIONAL_RULE_OPERATIONS = {
    "is_missing",
    "missing_when_equals",
    "missing_when_present",
    "date_after",
    "date_in_future",
    "numeric_gt",
    "numeric_lt",
    "starts_with",
    "equals",
    "all_missing",
    "duplicate_key",
    "duplicate_distinct",
}
ENABLE_FUNCTIONAL_RULE_DETECTOR = os.getenv("ENABLE_FUNCTIONAL_RULE_DETECTOR", "0").strip() == "1"

WORKFLOW_ENTRY_TABLES = ("bill",)
WORKFLOW_LINEAR_STAGES = (
    "cheque_slip",
    "punching_medium",
    "schedule3",
    "ecs",
)
THIRD_PARTY_WORKFLOW_STAGES = (
    "bill",
    "cheque_slip",
    "punching_medium",
    "schedule3",
    "ecs",
)
WORKFLOW_FEATURE_PREFIX = "wf_"
WORKFLOW_FEATURE_SUFFIXES = (
    "count",
    "active_forward_count",
    "stopped_count",
    "amount_sum",
    "latest_date",
)
WORKFLOW_AMOUNT_COLUMNS = (
    "amount_passed",
    "amount",
    "schedule3_amount",
    "civ_bill_amount",
    "claim_amount",
    "bill_amount",
    "amount_claimed",
)
WORKFLOW_DATE_COLUMNS = (
    "created_at",
    "cheque_slip_date",
    "pm_date",
    "dp_sheet_date",
    "cmp_file_gen_date",
    "npb_date",
)
THIRD_PARTY_DAK_SECTION_IDS = (142, 228, 265, 383)

EXTRA_SOURCE_JOIN_COLUMNS = {
    "bill": (
        {
            "source_column": "fk_dak",
            "reference_table": "dak",
            "reference_pk": "id",
            "reference_column": "bill_date",
            "alias": "dak_bill_date",
        },
        {
            "source_column": "fk_dak",
            "reference_table": "dak",
            "reference_pk": "id",
            "reference_column": "fis_doc_no",
            "alias": "dak_fis_doc_no",
        },
        {
            "source_column": "fk_dak",
            "reference_table": "dak",
            "reference_pk": "id",
            "reference_column": "reference_date",
            "alias": "dak_reference_date",
        },
    ),
}


@dataclass(frozen=True)
class Anomaly:
    transaction_id: str
    table_name: str
    source_record_id: str
    score: float
    context: dict


@dataclass(frozen=True)
class ColumnInfo:
    name: str
    data_type: str
    key: str
    references: str = "None"


def build_engine():
    print("[startup] Creating SQLAlchemy engine from DB_* settings.", flush=True)
    return create_engine(get_sqlalchemy_url(), pool_pre_ping=True)


def build_llama_client():
    if OpenAI is None:
        raise RuntimeError("The openai package is required for LLM explanations. Install project runtime deps.")
    settings = get_llama_settings()
    print(
        f"[startup] Creating Llama/OpenAI-compatible client: {settings['base_url']} "
        f"model={settings['model']}",
        flush=True,
    )
    return OpenAI(
        base_url=settings["base_url"],
        api_key=settings["api_key"],
        timeout=20,
        max_retries=0,
    )


def _jsonb_value(value):
    if isinstance(value, str):
        return json.loads(value)
    return value


def init_payment_category_table(conn) -> None:
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS payment_category_config (
                category_name VARCHAR(100) PRIMARY KEY,
                source_tables JSONB NOT NULL,
                dak_section_ids JSONB NOT NULL,
                enabled BOOLEAN NOT NULL DEFAULT TRUE,
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """
        )
    )
    for ddl in (
        "ALTER TABLE payment_category_config ADD COLUMN IF NOT EXISTS source_tables JSONB;",
        "ALTER TABLE payment_category_config ADD COLUMN IF NOT EXISTS dak_section_ids JSONB;",
        "ALTER TABLE payment_category_config ADD COLUMN IF NOT EXISTS enabled BOOLEAN NOT NULL DEFAULT TRUE;",
        "ALTER TABLE payment_category_config ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();",
    ):
        conn.execute(text(ddl))

    for category, config in load_payment_category_config().items():
        conn.execute(
            text(
                """
                INSERT INTO payment_category_config (
                    category_name,
                    source_tables,
                    dak_section_ids,
                    enabled,
                    updated_at
                )
                VALUES (
                    :category_name,
                    CAST(:source_tables AS JSONB),
                    CAST(:dak_section_ids AS JSONB),
                    TRUE,
                    NOW()
                )
                ON CONFLICT (category_name)
                DO UPDATE SET
                    source_tables = EXCLUDED.source_tables,
                    dak_section_ids = EXCLUDED.dak_section_ids,
                    updated_at = NOW();
                """
            ),
            {
                "category_name": category,
                "source_tables": json.dumps(list(config["source_tables"])),
                "dak_section_ids": json.dumps(list(config["dak_section_ids"])),
            },
        )


def load_payment_categories_from_db(engine, include_disabled: bool = False) -> dict[str, dict[str, tuple]]:
    where_clause = "" if include_disabled else "WHERE enabled = TRUE"
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                f"""
                SELECT category_name, source_tables, dak_section_ids, enabled
                FROM payment_category_config
                {where_clause}
                ORDER BY category_name;
                """
            )
        ).mappings()

        categories: dict[str, dict[str, tuple]] = {}
        for row in rows:
            category = str(row["category_name"])
            entry = validate_payment_category_entry(
                category,
                _jsonb_value(row["source_tables"]),
                _jsonb_value(row["dak_section_ids"]),
            )
            entry["enabled"] = bool(row["enabled"])
            categories[category] = entry
        return categories


def load_active_payment_category_config(engine=None) -> dict[str, dict[str, tuple]]:
    if engine is None:
        return load_payment_category_config()
    categories = load_payment_categories_from_db(engine, include_disabled=True)
    return categories or load_payment_category_config()


def update_payment_category_config(
    engine,
    category_name: str,
    source_tables,
    dak_section_ids,
    enabled: bool = True,
) -> dict:
    category_name = str(category_name).strip()
    entry = validate_payment_category_entry(category_name, source_tables, dak_section_ids)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO payment_category_config (
                    category_name,
                    source_tables,
                    dak_section_ids,
                    enabled,
                    updated_at
                )
                VALUES (
                    :category_name,
                    CAST(:source_tables AS JSONB),
                    CAST(:dak_section_ids AS JSONB),
                    :enabled,
                    NOW()
                )
                ON CONFLICT (category_name)
                DO UPDATE SET
                    source_tables = EXCLUDED.source_tables,
                    dak_section_ids = EXCLUDED.dak_section_ids,
                    enabled = EXCLUDED.enabled,
                    updated_at = NOW();
                """
            ),
            {
                "category_name": category_name,
                "source_tables": json.dumps(list(entry["source_tables"])),
                "dak_section_ids": json.dumps(list(entry["dak_section_ids"])),
                "enabled": bool(enabled),
            },
        )
    return {
        "category_name": category_name,
        "source_tables": list(entry["source_tables"]),
        "dak_section_ids": list(entry["dak_section_ids"]),
        "enabled": bool(enabled),
    }


def init_alert_tables(engine) -> None:
    print("[db] Ensuring detected_anomalies table exists.", flush=True)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS detected_anomalies (
                    transaction_id VARCHAR(255) PRIMARY KEY,
                    table_name VARCHAR(255),
                    source_record_id VARCHAR(255),
                    anomaly_score FLOAT NOT NULL,
                    isolation_score FLOAT,
                    autoencoder_score FLOAT,
                    feature_snapshot JSONB,
                    explanation TEXT NOT NULL,
                    review_status VARCHAR(16),
                    review_feedback VARCHAR(100),
                    reviewed_at TIMESTAMP,
                    detected_at TIMESTAMP DEFAULT NOW()
                );
                """
            )
        )
        for ddl in (
            "ALTER TABLE detected_anomalies ADD COLUMN IF NOT EXISTS table_name VARCHAR(255);",
            "ALTER TABLE detected_anomalies ADD COLUMN IF NOT EXISTS source_record_id VARCHAR(255);",
            "ALTER TABLE detected_anomalies ADD COLUMN IF NOT EXISTS isolation_score FLOAT;",
            "ALTER TABLE detected_anomalies ADD COLUMN IF NOT EXISTS autoencoder_score FLOAT;",
            "ALTER TABLE detected_anomalies ADD COLUMN IF NOT EXISTS feature_snapshot JSONB;",
            "ALTER TABLE detected_anomalies ADD COLUMN IF NOT EXISTS review_status VARCHAR(16);",
            "ALTER TABLE detected_anomalies ADD COLUMN IF NOT EXISTS review_feedback VARCHAR(100);",
            "ALTER TABLE detected_anomalies ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP;",
        ):
            conn.execute(text(ddl))
        init_payment_category_table(conn)
    print("[db] detected_anomalies and payment_category_config tables are ready.", flush=True)


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def prune_schema_to_allowed_relationships(
    tables: dict[str, list[ColumnInfo]],
    root_tables: Iterable[str] | None = None,
) -> dict[str, list[ColumnInfo]]:
    root_tables = set(root_tables or get_allowed_source_tables())
    visible_tables = {
        table
        for table in root_tables
        if table in tables and not is_excluded_table(table)
    }

    for table in list(visible_tables):
        for column in tables.get(table, []):
            if column.references != "None" and column.references in tables and not is_excluded_table(column.references):
                visible_tables.add(column.references)

    for table, columns in tables.items():
        if table in visible_tables or is_excluded_table(table):
            continue
        if any(column.references in root_tables for column in columns):
            visible_tables.add(table)

    return {
        table: columns
        for table, columns in tables.items()
        if table in visible_tables
    }


def parse_schema_file(
    path: str = SCHEMA_FILE,
    root_tables: Iterable[str] | None = None,
) -> dict[str, list[ColumnInfo]]:
    started_at = time.perf_counter()
    print(f"[schema] Reading schema from {path}.", flush=True)
    tables: dict[str, list[ColumnInfo]] = {}
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
                    print(f"[schema] Skipping excluded table: {current_table}", flush=True)
                    current_table = None
                    continue
                tables.setdefault(current_table, [])
                continue

            if not current_table or line.startswith("|---") or line.startswith("| Column Name"):
                continue

            column_match = column_pattern.match(line)
            if not column_match:
                continue

            column = column_match.group("column").strip()
            if column == "Column Name":
                continue

            tables[current_table].append(
                ColumnInfo(
                    name=column,
                    data_type=column_match.group("data_type").strip().lower(),
                    key=column_match.group("key").strip(),
                    references=column_match.group("references").strip(),
                )
            )

    raw_table_count = len(tables)
    tables = prune_schema_to_allowed_relationships(tables, root_tables=root_tables)
    column_count = sum(len(columns) for columns in tables.values())
    print(
        f"[schema] Parsed {len(tables)} allowed root/FK-linked tables "
        f"from {raw_table_count} schema table(s), {column_count} columns "
        f"in {time.perf_counter() - started_at:.2f}s.",
        flush=True,
    )
    return tables


def column_priority_for_join(column: ColumnInfo) -> int:
    name = column.name.lower()
    data_type = column.data_type
    score = 0
    if column.key in {"PK", "FK"}:
        score -= 100
    if any(term in name for term in ("name", "code", "status", "type", "mode", "category", "state")):
        score += 50
    if any(data_type.startswith(prefix) for prefix in ("character", "text", "boolean", "integer", "bigint")):
        score += 15
    return score


def find_primary_key(columns: list[ColumnInfo]) -> str | None:
    for column in columns:
        if column.key == "PK":
            return column.name
    return None


def build_joined_contexts(
    schema: dict[str, list[ColumnInfo]],
    table: str,
    base_context_columns: tuple[str, ...],
    max_joined_columns: int = 8,
) -> tuple[JoinedContext, ...]:
    table_columns = {column.name: column for column in schema.get(table, [])}
    joined_contexts: list[JoinedContext] = []
    seen_aliases = set()

    for source_column in base_context_columns:
        column = table_columns.get(source_column)
        if not column or column.key != "FK" or column.references == "None":
            continue
        reference_columns = schema.get(column.references)
        if not reference_columns:
            continue
        reference_pk = find_primary_key(reference_columns)
        if not reference_pk:
            continue

        candidates = [
            ref_column
            for ref_column in sorted(reference_columns, key=column_priority_for_join, reverse=True)
            if ref_column.name != reference_pk and ref_column.key != "FK" and column_priority_for_join(ref_column) > 0
        ][:2]
        for ref_column in candidates:
            alias = make_feature_name(table, f"{source_column}_{column.references}_{ref_column.name}")
            if alias in seen_aliases:
                continue
            joined_contexts.append(
                JoinedContext(
                    source_column=source_column,
                    reference_table=column.references,
                    reference_pk=reference_pk,
                    reference_column=ref_column.name,
                    alias=alias,
                )
            )
            seen_aliases.add(alias)
            if len(joined_contexts) >= max_joined_columns:
                return tuple(joined_contexts)

    return tuple(joined_contexts)


def build_relationship_feature_plan(table: str, joined_context_columns: tuple[JoinedContext, ...]) -> list[dict]:
    raw_plan = []
    for joined in joined_context_columns[:4]:
        raw_plan.extend(
            [
                {
                    "name": make_feature_name(table, f"{joined.alias}_frequency"),
                    "op": "group_frequency",
                    "group_by": joined.alias,
                    "reason": (
                        f"Uses FK join {joined.source_column}->{joined.reference_table} "
                        f"to find rare related {joined.reference_column} values."
                    ),
                },
                {
                    "name": make_feature_name(table, f"amount_to_{joined.alias}_median"),
                    "op": "ratio_to_group_median",
                    "group_by": joined.alias,
                    "reason": (
                        f"Compares amount with normal amounts for the joined "
                        f"{joined.reference_table}.{joined.reference_column} group."
                    ),
                },
            ]
        )
    return raw_plan


def available_extra_join_columns(
    schema: dict[str, list[ColumnInfo]],
    table: str,
    source_column_names: set[str],
) -> tuple[dict, ...]:
    available = []
    for join_column in EXTRA_SOURCE_JOIN_COLUMNS.get(table, ()):
        reference_table = str(join_column["reference_table"])
        reference_columns = {column.name for column in schema.get(reference_table, [])}
        if (
            join_column["source_column"] in source_column_names
            and join_column["reference_pk"] in reference_columns
            and join_column["reference_column"] in reference_columns
        ):
            available.append(join_column)
    return tuple(available)


def extra_join_aliases(join_columns: Iterable[dict]) -> set[str]:
    return {str(join_column["alias"]) for join_column in join_columns}


def load_configured_runtime_sources(
    schema: dict[str, list[ColumnInfo]],
    path: str = SOURCE_CONFIG_FILE,
    allowed_physical_tables: tuple[str, ...] | None = None,
) -> list[RuntimeSource]:
    if not os.path.exists(path):
        raise RuntimeError(
            f"{path} not found. Run `venv/bin/python backend/run_architecture.py architect` "
            "with Ollama running to generate LLM-selected sources."
        )

    print(f"[source] Loading configured source candidates from {path}.", flush=True)
    with open(path, "r", encoding="utf-8") as source_file:
        raw_sources = json.load(source_file)

    if not isinstance(raw_sources, list):
        raise RuntimeError(f"{path} must contain a JSON array.")

    allowed_physical_table_set = set(allowed_physical_tables or get_allowed_physical_source_tables())
    validated_sources = []
    for raw_source in raw_sources:
        if not isinstance(raw_source, dict):
            continue

        table = str(raw_source.get("table", "")).strip()
        if is_excluded_table(table):
            print(f"[source] Rejected excluded table from config: {table}", flush=True)
            continue
        if table not in allowed_physical_table_set:
            print(
                "[source] Rejected configured table outside LLAMA_BUSINESS_PRIORITY_TABLES/payment category selection: "
                f"{table}",
                flush=True,
            )
            continue
        if table not in schema:
            continue

        column_names = {column.name for column in schema[table]}
        id_column = str(raw_source.get("id_column", "")).strip()
        amount_column = str(raw_source.get("amount_column", "")).strip()
        date_column = raw_source.get("date_column")
        if date_column is not None:
            date_column = str(date_column).strip()

        if id_column not in column_names or amount_column not in column_names:
            continue
        if date_column and date_column not in column_names:
            continue

        configured_context_columns = [
            column
            for column in raw_source.get("context_columns", [])
            if isinstance(column, str)
        ]
        available_extra_joins = available_extra_join_columns(schema, table, column_names)
        extra_aliases = extra_join_aliases(available_extra_joins)
        workflow_aliases = set(workflow_feature_aliases()) if table == "dak" else set()
        base_context_columns = tuple(
            column
            for column in configured_context_columns
            if column in column_names
        )[:MAX_CONFIG_CONTEXT_COLUMNS]
        extra_context_columns = tuple(
            column
            for column in configured_context_columns
            if column in extra_aliases or column in workflow_aliases
        )
        joined_context_columns = build_joined_contexts(schema, table, base_context_columns)
        context_columns = base_context_columns + extra_context_columns + tuple(
            joined.alias for joined in joined_context_columns
        )
        feature_plan = tuple(
            feature
            for feature in raw_source.get("feature_plan", [])
            if isinstance(feature, dict)
        )
        if not feature_plan:
            feature_plan = feature_plan + tuple(build_relationship_feature_plan(table, joined_context_columns))
        feature_plan = tuple(
            validate_feature_plan(
                feature_plan,
                {
                    "context_columns": context_columns,
                    "date_column": date_column or None,
                },
            )
        )
        validated_sources.append(
            RuntimeSource(
                table=table,
                id_column=id_column,
                amount_column=amount_column,
                context_columns=context_columns,
                date_column=date_column or None,
                feature_plan=feature_plan,
                base_context_columns=base_context_columns,
                joined_context_columns=joined_context_columns,
            )
        )

    print(
        f"[source] Accepted {len(validated_sources)} configured source candidate(s) "
        "after schema validation.",
        flush=True,
    )
    return validated_sources


def parse_candidate_column_name(candidate: str) -> str:
    return str(candidate).split(":", 1)[0].strip()


def is_numeric_type(data_type: str) -> bool:
    return any(
        data_type.startswith(prefix)
        for prefix in (
            "smallint",
            "integer",
            "bigint",
            "decimal",
            "numeric",
            "real",
            "double precision",
            "serial",
            "bigserial",
        )
    )


def is_date_type(data_type: str) -> bool:
    return any(data_type.startswith(prefix) for prefix in ("date", "timestamp", "time"))


def column_name_contains_any(column_name: str, terms: tuple[str, ...]) -> bool:
    lowered = column_name.lower()
    return any(term in lowered for term in terms)


def choose_amount_column(columns: list[ColumnInfo]) -> str | None:
    numeric_columns = [
        column
        for column in columns
        if column.key not in {"PK", "FK"} and is_numeric_type(column.data_type)
    ]
    if not numeric_columns:
        return None
    priority_terms = ("amount", "amt", "claimed", "passed", "tax", "gst", "price", "value", "total")
    numeric_columns.sort(
        key=lambda column: (
            column_name_contains_any(column.name, priority_terms),
            -len(column.name),
        ),
        reverse=True,
    )
    return numeric_columns[0].name


def choose_date_column(columns: list[ColumnInfo]) -> str | None:
    date_columns = [column for column in columns if is_date_type(column.data_type)]
    if not date_columns:
        return None
    priority_terms = ("created", "modified", "date", "time", "updated")
    date_columns.sort(
        key=lambda column: column_name_contains_any(column.name, priority_terms),
        reverse=True,
    )
    return date_columns[0].name


def choose_context_columns(columns: list[ColumnInfo], limit: int = 4) -> tuple[str, ...]:
    priority_terms = (
        "vendor",
        "unit",
        "section",
        "office",
        "employee",
        "status",
        "type",
        "mode",
        "approved",
        "record_status",
    )
    candidates = [
        column
        for column in columns
        if column.key == "FK" or column_name_contains_any(column.name, priority_terms)
    ]
    candidates.sort(
        key=lambda column: (
            column.key == "FK",
            column_name_contains_any(column.name, priority_terms),
        ),
        reverse=True,
    )
    context_columns = []
    for column in candidates:
        if column.name not in context_columns:
            context_columns.append(column.name)
        if len(context_columns) >= limit:
            break
    return tuple(context_columns)


def make_feature_name(table: str, suffix: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_]+", "_", f"{table}_{suffix}").strip("_")
    if not name or not name[0].isalpha():
        name = f"feature_{name}"
    return name[:80]


def build_candidate_feature_plan(table: str, context_columns: list[str], date_column: str | None) -> list[dict]:
    raw_plan = [
        {
            "name": make_feature_name(table, "amount_log"),
            "op": "log",
            "source": "amount",
            "reason": "Reduces scale effects while preserving high-value amount patterns.",
        },
        {
            "name": make_feature_name(table, "amount_rank_pct"),
            "op": "rank_pct",
            "source": "amount",
            "reason": "Shows where the amount sits in this table's scanned distribution.",
        },
        {
            "name": make_feature_name(table, "amount_to_p95"),
            "op": "ratio_to_quantile",
            "source": "amount",
            "params": {"quantile": 0.95},
            "reason": "Compares each amount with the high-value range for this table.",
        },
    ]
    for column in context_columns[:2]:
        raw_plan.extend(
            [
                {
                    "name": make_feature_name(table, f"{column}_frequency"),
                    "op": "group_frequency",
                    "group_by": column,
                    "reason": f"Highlights rare {column} values in the scanned records.",
                },
                {
                    "name": make_feature_name(table, f"amount_to_{column}_median"),
                    "op": "ratio_to_group_median",
                    "group_by": column,
                    "reason": f"Compares amount with normal values for the same {column}.",
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


def load_candidate_audit_runtime_sources(
    schema: dict[str, list[ColumnInfo]],
    path: str = SCHEMA_CANDIDATE_AUDIT_FILE,
    allowed_physical_tables: tuple[str, ...] | None = None,
) -> list[RuntimeSource]:
    if not os.path.exists(path):
        return []

    print(
        "[source] Building fallback source plans from local schema candidate audit "
        f"{path}.",
        flush=True,
    )
    with open(path, "r", encoding="utf-8") as audit_file:
        candidates = json.load(audit_file)
    if not isinstance(candidates, list):
        return []

    allowed_physical_table_set = set(allowed_physical_tables or get_allowed_physical_source_tables())
    sources: list[RuntimeSource] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        table = str(candidate.get("table", "")).strip()
        if table not in schema or table not in allowed_physical_table_set:
            continue

        id_candidates = candidate.get("primary_keys") or []
        amount_candidates = candidate.get("amount_candidates") or []
        if not id_candidates or not amount_candidates:
            continue

        column_names = {column.name for column in schema[table]}
        id_column = parse_candidate_column_name(id_candidates[0])
        amount_column = parse_candidate_column_name(amount_candidates[0])
        if id_column not in column_names or amount_column not in column_names:
            continue

        base_context_columns = []
        for raw_context in candidate.get("context_candidates") or []:
            column = parse_candidate_column_name(raw_context)
            if column in column_names and column not in base_context_columns:
                base_context_columns.append(column)
        base_context_columns = base_context_columns[:4]
        joined_context_columns = build_joined_contexts(schema, table, tuple(base_context_columns))
        context_columns = base_context_columns + [joined.alias for joined in joined_context_columns]

        date_column = None
        for raw_date in candidate.get("date_candidates") or []:
            column = parse_candidate_column_name(raw_date)
            if column in column_names:
                date_column = column
                break

        feature_plan = tuple(
            validate_feature_plan(
                list(build_candidate_feature_plan(table, context_columns, date_column))
                + build_relationship_feature_plan(table, joined_context_columns),
                {
                    "context_columns": context_columns,
                    "date_column": date_column,
                },
            )
        )
        if not feature_plan:
            continue
        sources.append(
            RuntimeSource(
                table=table,
                id_column=id_column,
                amount_column=amount_column,
                context_columns=tuple(context_columns),
                date_column=date_column,
                feature_plan=feature_plan,
                base_context_columns=tuple(base_context_columns),
                joined_context_columns=joined_context_columns,
            )
        )

    print(
        f"[source] Built {len(sources)} fallback source plan(s) from allowed candidate audit tables.",
        flush=True,
    )
    return sources


def load_schema_runtime_sources(
    schema: dict[str, list[ColumnInfo]],
    allowed_physical_tables: tuple[str, ...] | None = None,
) -> list[RuntimeSource]:
    sources: list[RuntimeSource] = []
    for table in allowed_physical_tables or get_allowed_physical_source_tables():
        if table not in schema:
            print(f"[source] Required table missing from schema: {table}", flush=True)
            continue
        columns = schema[table]
        id_column = find_primary_key(columns)
        amount_column = choose_amount_column(columns)
        if not id_column or not amount_column:
            print(
                f"[source] Required table cannot be scored because it lacks "
                f"{'a primary key' if not id_column else 'a numeric measure'}: {table}",
                flush=True,
            )
            continue

        base_context_columns = choose_context_columns(columns)
        joined_context_columns = build_joined_contexts(schema, table, base_context_columns)
        context_columns = base_context_columns + tuple(joined.alias for joined in joined_context_columns)
        date_column = choose_date_column(columns)
        feature_plan = tuple(
            validate_feature_plan(
                list(build_candidate_feature_plan(table, list(context_columns), date_column))
                + build_relationship_feature_plan(table, joined_context_columns),
                {
                    "context_columns": context_columns,
                    "date_column": date_column,
                },
            )
        )
        if not feature_plan:
            print(f"[source] Required table has no valid feature plan: {table}", flush=True)
            continue
        sources.append(
            RuntimeSource(
                table=table,
                id_column=id_column,
                amount_column=amount_column,
                context_columns=context_columns,
                date_column=date_column,
                feature_plan=feature_plan,
                base_context_columns=base_context_columns,
                joined_context_columns=joined_context_columns,
            )
        )

    print(
        f"[source] Built {len(sources)} schema-derived source plan(s) "
        "from LLAMA_BUSINESS_PRIORITY_TABLES.",
        flush=True,
    )
    return sources


def table_exists(engine, table: str) -> bool:
    started_at = time.perf_counter()
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_name = :table
                );
                """
            ),
            {"table": table},
        )
        exists = bool(result.scalar())
    print(
        f"[source] Table check: public.{table} exists={exists} "
        f"({time.perf_counter() - started_at:.2f}s).",
        flush=True,
    )
    return exists


def load_table_columns(engine, table: str) -> set[str]:
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = :table;
                """
            ),
            {"table": table},
        )
        return {str(row.column_name) for row in result}


def first_existing_column(columns: set[str], candidates: Iterable[str]) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def sql_null_literal(alias: str, data_type: str = "text") -> str:
    return f"NULL::{data_type} AS {quote_identifier(alias)}"


def workflow_active_condition(table_alias: str, columns: set[str], require_forward_motion: bool = True) -> str:
    conditions = []
    if "record_status" in columns:
        conditions.append(f"{table_alias}.{quote_identifier('record_status')} = 'V'")
    if require_forward_motion and "approved" in columns:
        conditions.append(f"{table_alias}.{quote_identifier('approved')} IS TRUE")
    if require_forward_motion and "passed" in columns:
        conditions.append(f"{table_alias}.{quote_identifier('passed')} IS TRUE")
    if "cancelled" in columns:
        conditions.append(
            f"COALESCE({table_alias}.{quote_identifier('cancelled')}, FALSE) IS FALSE"
        )
    if "rejection_status" in columns:
        conditions.append(f"{table_alias}.{quote_identifier('rejection_status')} IS NULL")
    return " AND ".join(conditions) if conditions else "TRUE"


def workflow_stopped_condition(table_alias: str, columns: set[str]) -> str:
    conditions = []
    if "record_status" in columns:
        conditions.append(
            f"({table_alias}.{quote_identifier('record_status')} IS NOT NULL "
            f"AND {table_alias}.{quote_identifier('record_status')} <> 'V')"
        )
    if "cancelled" in columns:
        conditions.append(f"{table_alias}.{quote_identifier('cancelled')} IS TRUE")
    if "rejection_status" in columns:
        conditions.append(f"{table_alias}.{quote_identifier('rejection_status')} IS NOT NULL")
    return " OR ".join(conditions) if conditions else "FALSE"


def workflow_type_expression(table_alias: str, columns: set[str]) -> str:
    for column in ("payment_record_type", "fk_bill_type", "payment_mode"):
        if column in columns:
            return f"MIN({table_alias}.{quote_identifier(column)}::text)"
    return "NULL::text"


def build_workflow_stage_aggregate_sql(
    table: str,
    columns: set[str],
    join_dak_scope: bool = True,
    filter_to_third_party_dak: bool = False,
) -> str:
    table_alias = f"{table}_src"
    amount_column = first_existing_column(columns, WORKFLOW_AMOUNT_COLUMNS)
    date_column = first_existing_column(columns, WORKFLOW_DATE_COLUMNS)
    amount_expression = (
        f"SUM({table_alias}.{quote_identifier(amount_column)}::double precision)"
        if amount_column
        else "NULL::double precision"
    )
    latest_date_expression = (
        f"MAX({table_alias}.{quote_identifier(date_column)}::timestamp)"
        if date_column
        else "NULL::timestamp"
    )
    active_condition = workflow_active_condition(table_alias, columns)
    stopped_condition = workflow_stopped_condition(table_alias, columns)
    if join_dak_scope:
        join_clause = f"""
        INNER JOIN dak_scope
            ON {table_alias}.{quote_identifier('fk_dak')}::text = dak_scope.dak_id
        """
    elif filter_to_third_party_dak:
        dak_section_filter_sql = ", ".join(str(section_id) for section_id in THIRD_PARTY_DAK_SECTION_IDS)
        join_clause = f"""
        INNER JOIN dak AS {table_alias}_dak_filter
            ON {table_alias}.{quote_identifier('fk_dak')} = {table_alias}_dak_filter.{quote_identifier('id')}
           AND {table_alias}_dak_filter.{quote_identifier('fk_section')} IN ({dak_section_filter_sql})
        """
    else:
        join_clause = ""
    return f"""
        SELECT
            {table_alias}.{quote_identifier('fk_dak')}::text AS dak_id,
            COUNT(*)::bigint AS {quote_identifier(f'{table}_count')},
            COUNT(*) FILTER (WHERE {active_condition})::bigint AS {quote_identifier(f'{table}_active_forward_count')},
            COUNT(*) FILTER (WHERE {stopped_condition})::bigint AS {quote_identifier(f'{table}_stopped_count')},
            {amount_expression} AS {quote_identifier(f'{table}_amount_sum')},
            {latest_date_expression} AS {quote_identifier(f'{table}_latest_date')},
            {workflow_type_expression(table_alias, columns)} AS {quote_identifier(f'{table}_workflow_type')}
        FROM {quote_identifier(table)} AS {table_alias}
        {join_clause}
        WHERE {table_alias}.{quote_identifier('fk_dak')} IS NOT NULL
        GROUP BY {table_alias}.{quote_identifier('fk_dak')}
    """


def workflow_stage_inventory(engine, row_limit: int) -> tuple[list[str], dict[str, set[str]]]:
    allowed_tables = set(get_allowed_physical_source_tables())
    tables = [
        table
        for table in THIRD_PARTY_WORKFLOW_STAGES
        if table in allowed_tables
    ]
    columns_by_table: dict[str, set[str]] = {}
    usable_tables = []
    for table in tables:
        if not table_exists(engine, table):
            continue
        columns = load_table_columns(engine, table)
        if "id" not in columns or "fk_dak" not in columns:
            continue
        columns_by_table[table] = columns
        usable_tables.append(table)
    return usable_tables, columns_by_table


def build_workflow_stage_ctes(
    usable_tables: list[str],
    columns_by_table: dict[str, set[str]],
) -> list[str]:
    ctes = []
    for table in usable_tables:
        ctes.append(f"{table}_stage AS ({build_workflow_stage_aggregate_sql(table, columns_by_table[table])})")
    return ctes


def workflow_count_column(table: str, suffix: str) -> str:
    return f"{table}_{suffix}"


def workflow_feature_alias(table: str, suffix: str) -> str:
    return f"{WORKFLOW_FEATURE_PREFIX}{table}_{suffix}"


def workflow_feature_aliases() -> tuple[str, ...]:
    return tuple(
        workflow_feature_alias(table, suffix)
        for table in THIRD_PARTY_WORKFLOW_STAGES
        for suffix in WORKFLOW_FEATURE_SUFFIXES
    )


def is_workflow_feature_alias(column: str) -> bool:
    return column in set(workflow_feature_aliases())


def workflow_stage_select_columns(usable_tables: list[str]) -> list[str]:
    columns = []
    for table in THIRD_PARTY_WORKFLOW_STAGES:
        if table not in usable_tables:
            for suffix in ("count", "active_forward_count", "stopped_count"):
                columns.append(f"0::bigint AS {quote_identifier(workflow_count_column(table, suffix))}")
            columns.append(f"NULL::double precision AS {quote_identifier(workflow_count_column(table, 'amount_sum'))}")
            columns.append(f"NULL::timestamp AS {quote_identifier(workflow_count_column(table, 'latest_date'))}")
            columns.append(f"NULL::text AS {quote_identifier(workflow_count_column(table, 'workflow_type'))}")
            continue
        alias = f"{table}_stage"
        for suffix in ("count", "active_forward_count", "stopped_count"):
            column = workflow_count_column(table, suffix)
            columns.append(f"COALESCE({alias}.{quote_identifier(column)}, 0)::bigint AS {quote_identifier(column)}")
        amount_column = workflow_count_column(table, "amount_sum")
        columns.append(f"{alias}.{quote_identifier(amount_column)} AS {quote_identifier(amount_column)}")
        date_column = workflow_count_column(table, "latest_date")
        columns.append(f"{alias}.{quote_identifier(date_column)} AS {quote_identifier(date_column)}")
        type_column = workflow_count_column(table, "workflow_type")
        columns.append(f"{alias}.{quote_identifier(type_column)} AS {quote_identifier(type_column)}")
    return columns


def workflow_stage_joins(usable_tables: list[str]) -> str:
    return "\n".join(
        f"LEFT JOIN {table}_stage ON dak_scope.dak_id = {table}_stage.dak_id"
        for table in usable_tables
    )


def build_dak_workflow_feature_ctes() -> tuple[list[str], list[str], list[str]]:
    ctes = []
    joins = []
    selected_columns = []
    for table in THIRD_PARTY_WORKFLOW_STAGES:
        if table == "bill":
            columns = {
                "fk_dak",
                "amount_claimed",
                "amount_passed",
                "record_status",
                "approved",
                "passed",
                "cancelled",
                "invoice_date",
                "dp_sheet_date",
                "cmp_date",
            }
        elif table == "cheque_slip":
            columns = {"fk_dak", "amount", "record_status", "approved", "cheque_slip_date", "npb_date"}
        elif table == "punching_medium":
            columns = {"fk_dak", "amount", "record_status", "approved", "passed", "cancelled", "pm_date"}
        elif table == "schedule3":
            columns = {
                "fk_dak",
                "schedule3_amount",
                "record_status",
                "approved",
                "rejection_status",
                "dp_sheet_date",
                "npb_date",
            }
        elif table == "ecs":
            columns = {
                "fk_dak",
                "amount",
                "record_status",
                "approved",
                "rejection_status",
                "cmp_file_gen_date",
                "npb_date",
                "utr_date",
                "scroll_date",
            }
        else:
            columns = {"fk_dak"}

        stage_alias = f"{table}_wf"
        ctes.append(
            f"{stage_alias} AS ("
            f"{build_workflow_stage_aggregate_sql(table, columns, join_dak_scope=False, filter_to_third_party_dak=True)}"
            ")"
        )
        joins.append(f"LEFT JOIN {stage_alias} ON src.{quote_identifier('id')}::text = {stage_alias}.dak_id")
        for suffix in WORKFLOW_FEATURE_SUFFIXES:
            source_column = workflow_count_column(table, suffix)
            alias = workflow_feature_alias(table, suffix)
            if suffix in {"count", "active_forward_count", "stopped_count"}:
                selected_columns.append(
                    f"COALESCE({stage_alias}.{quote_identifier(source_column)}, 0)::double precision AS {quote_identifier(alias)}"
                )
            else:
                selected_columns.append(f"{stage_alias}.{quote_identifier(source_column)} AS {quote_identifier(alias)}")
    return ctes, joins, selected_columns


def workflow_anomaly_context(
    anomaly_type: str,
    dak_id: str,
    reason: str,
    stage_counts: dict | None = None,
    extra: dict | None = None,
) -> dict:
    context = {
        "detector_type": "workflow_process",
        "source_table": "dak_workflow",
        "transaction_id": dak_id,
        "workflow": "dak -> bill -> cheque_slip -> punching_medium -> schedule3 -> ecs",
        "anomaly_type": anomaly_type,
        "statistical_reason": reason,
    }
    if stage_counts:
        context["stage_counts"] = stage_counts
    if extra:
        context.update(extra)
    return context


def _row_value(row, key: str):
    if isinstance(row, pd.Series):
        return row.get(key)
    return getattr(row, key, None)


def add_display_context(context: dict, row=None, source: RuntimeSource | None = None) -> dict:
    if row is not None:
        if source and source.table == "dak":
            context.setdefault("display_dak_id", context.get("source_record_id") or _row_value(row, "transaction_id"))
        else:
            context.setdefault("display_dak_id", _row_value(row, "fk_dak"))

        bill_amount = _row_value(row, "amount_claimed")
        if bill_amount is None and source and source.table == "bill":
            bill_amount = _row_value(row, "amount")
        if bill_amount is not None and not pd.isna(bill_amount):
            context.setdefault("display_bill_amount_claimed", json_safe_value(bill_amount))

        for key in ("section_name", "bill_fk_section_section_section_name", "dak_fk_section_section_section_name"):
            value = _row_value(row, key)
            if value is not None and not pd.isna(value):
                context.setdefault("display_section_name", json_safe_value(value))
                break

        section_id = _row_value(row, "fk_section")
        if section_id is not None and not pd.isna(section_id):
            context.setdefault("display_section_id", json_safe_value(section_id))

    return context


def make_workflow_anomaly(
    anomaly_type: str,
    dak_id,
    reason: str,
    score: float,
    stage_counts: dict | None = None,
    extra: dict | None = None,
) -> Anomaly:
    normalized_dak_id = normalize_record_id(dak_id)
    return Anomaly(
        transaction_id=f"workflow:{anomaly_type}:{normalized_dak_id}",
        table_name="workflow_process",
        source_record_id=normalized_dak_id,
        score=score,
        context=workflow_anomaly_context(
            anomaly_type,
            normalized_dak_id,
            reason,
            stage_counts=stage_counts,
            extra=extra,
        ),
    )


def int_count(row: dict, key: str) -> int:
    value = row.get(key)
    if value is None or pd.isna(value):
        return 0
    return int(value)


def workflow_row_flags(row: dict) -> dict:
    return {
        "has_bill": int_count(row, "bill_count") > 0,
        "has_cheque_slip": int_count(row, "cheque_slip_count") > 0,
        "has_punching_medium": int_count(row, "punching_medium_count") > 0,
        "has_schedule3": int_count(row, "schedule3_count") > 0,
        "has_ecs": int_count(row, "ecs_count") > 0,
    }


def workflow_payment_type(row: dict) -> str:
    for key in (
        "bill_workflow_type",
        "cheque_slip_workflow_type",
        "punching_medium_workflow_type",
        "schedule3_workflow_type",
        "ecs_workflow_type",
    ):
        value = row.get(key)
        if value is not None and not pd.isna(value) and str(value).strip():
            return str(value)
    return "THIRD_PARTY_PAYMENTS"


def make_workflow_issue(
    anomaly_type: str,
    row: dict,
    missing_step: str,
    present_later_step: str,
    reason: str,
    score: float,
) -> dict:
    flags = workflow_row_flags(row)
    dak_id = normalize_record_id(row.get("dak_id"))
    stage_counts = {
        "bill_count": int_count(row, "bill_count"),
        "cheque_slip_count": int_count(row, "cheque_slip_count"),
        "punching_medium_count": int_count(row, "punching_medium_count"),
        "schedule3_count": int_count(row, "schedule3_count"),
        "ecs_count": int_count(row, "ecs_count"),
        "bill_active_forward_count": int_count(row, "bill_active_forward_count"),
        "cheque_slip_active_forward_count": int_count(row, "cheque_slip_active_forward_count"),
        "punching_medium_active_forward_count": int_count(row, "punching_medium_active_forward_count"),
        "schedule3_active_forward_count": int_count(row, "schedule3_active_forward_count"),
        "bill_stopped_count": int_count(row, "bill_stopped_count"),
        "cheque_slip_stopped_count": int_count(row, "cheque_slip_stopped_count"),
        "punching_medium_stopped_count": int_count(row, "punching_medium_stopped_count"),
        "schedule3_stopped_count": int_count(row, "schedule3_stopped_count"),
    }
    return {
        "anomaly_type": anomaly_type,
        "dak_id": dak_id,
        "payment_workflow_type": workflow_payment_type(row),
        "missing_step": missing_step,
        "present_later_step": present_later_step,
        "anomaly_reason": reason,
        "score": score,
        "stage_counts": stage_counts,
        **flags,
    }


def classify_workflow_row(row: dict, available_stages: set[str]) -> list[dict]:
    issues: list[dict] = []
    flags = workflow_row_flags(row)
    dak_id = normalize_record_id(row.get("dak_id"))
    dak_record_status = row.get("dak_record_status")
    dak_is_valid = dak_record_status is None or pd.isna(dak_record_status) or str(dak_record_status).strip() == "V"

    def has(stage: str) -> bool:
        return flags[f"has_{stage}"]

    def active(stage: str) -> int:
        return int_count(row, f"{stage}_active_forward_count")

    def stopped(stage: str) -> int:
        return int_count(row, f"{stage}_stopped_count")

    if "bill" in available_stages and dak_is_valid and not has("bill") and not any(flags.values()):
        issues.append(
            make_workflow_issue(
                "dak_without_downstream_movement",
                row,
                "bill",
                "dak",
                f"Dak {dak_id} is in the TPP section scope but has no bill or later payment-stage row.",
                82.0,
            )
        )

    downstream_checks = [
        ("cheque_slip", "bill", 96.0),
        ("punching_medium", "cheque_slip", 94.0),
        ("schedule3", "punching_medium", 92.0),
        ("ecs", "schedule3", 90.0),
    ]
    for later_step, required_step, score in downstream_checks:
        if later_step not in available_stages or required_step not in available_stages:
            continue
        if has(later_step) and not has(required_step):
            issues.append(
                make_workflow_issue(
                    f"{later_step}_without_{required_step}",
                    row,
                    required_step,
                    later_step,
                    f"Dak {dak_id} has {later_step} row(s) but no {required_step} row.",
                    score,
                )
            )

    forward_checks = [
        ("bill", "cheque_slip", 78.0),
        ("cheque_slip", "punching_medium", 76.0),
        ("punching_medium", "schedule3", 74.0),
        ("schedule3", "ecs", 72.0),
    ]
    for current_step, next_step, score in forward_checks:
        if current_step not in available_stages or next_step not in available_stages:
            continue
        if active(current_step) > 0 and not has(next_step):
            issues.append(
                make_workflow_issue(
                    f"{current_step}_active_without_{next_step}",
                    row,
                    next_step,
                    current_step,
                    (
                        f"Dak {dak_id} has active/valid {current_step} row(s) that should move forward, "
                        f"but no {next_step} row is present."
                    ),
                    score,
                )
            )

    stopped_checks = [
        ("bill", ("cheque_slip", "punching_medium", "schedule3", "ecs"), 88.0),
        ("cheque_slip", ("punching_medium", "schedule3", "ecs"), 86.0),
        ("punching_medium", ("schedule3", "ecs"), 84.0),
        ("schedule3", ("ecs",), 82.0),
    ]
    for stopped_step, later_steps, score in stopped_checks:
        if stopped_step not in available_stages or stopped(stopped_step) <= 0:
            continue
        present_later_steps = [
            later_step
            for later_step in later_steps
            if later_step in available_stages and has(later_step)
        ]
        if present_later_steps:
            present_later_step = present_later_steps[-1]
            issues.append(
                make_workflow_issue(
                    f"stopped_{stopped_step}_moved_to_{present_later_step}",
                    row,
                    "workflow_stop",
                    present_later_step,
                    (
                        f"Dak {dak_id} has stopped/rejected/invalid {stopped_step} row(s), "
                        f"but later {present_later_step} row(s) are present."
                    ),
                    score,
                )
            )

    return issues


def detect_workflow_anomalies(engine, row_limit: int = DEFAULT_ROWS_PER_TABLE) -> list[Anomaly]:
    print("[workflow] Starting dak-to-ecs process-flow anomaly checks.", flush=True)
    if not table_exists(engine, "dak"):
        print("[workflow] Required root table missing: dak.", flush=True)
        return []
    dak_columns = load_table_columns(engine, "dak")
    if "id" not in dak_columns or "fk_section" not in dak_columns:
        print("[workflow] Dak table lacks required id/fk_section columns.", flush=True)
        return []

    usable_tables, columns_by_table = workflow_stage_inventory(engine, row_limit)
    if not usable_tables:
        print("[workflow] No usable workflow tables available.", flush=True)
        return []

    if "bill" not in usable_tables:
        print("[workflow] No usable entry-stage bill tables available.", flush=True)
        return []

    dak_section_filter_sql = ", ".join(str(section_id) for section_id in THIRD_PARTY_DAK_SECTION_IDS)
    dak_order_column = first_existing_column(
        dak_columns,
        ("created_at", "bill_date", "list_date", "reference_date", "id"),
    )
    dak_scope_select = [
        f"dak_src.{quote_identifier('id')}::text AS dak_id",
        f"dak_src.{quote_identifier('fk_section')} AS fk_section",
        (
            f"dak_src.{quote_identifier('record_status')}::text AS dak_record_status"
            if "record_status" in dak_columns
            else "NULL::text AS dak_record_status"
        ),
        (
            f"dak_src.{quote_identifier('dakid_no')}::text AS dakid_no"
            if "dakid_no" in dak_columns
            else "NULL::text AS dakid_no"
        ),
    ]
    stage_ctes = build_workflow_stage_ctes(usable_tables, columns_by_table)
    ctes = [
        f"""
        dak_scope AS (
            SELECT {", ".join(dak_scope_select)}
            FROM dak AS dak_src
            WHERE dak_src.{quote_identifier('fk_section')} IN ({dak_section_filter_sql})
            ORDER BY dak_src.{quote_identifier(dak_order_column)} DESC NULLS LAST
            LIMIT :row_limit
        )
        """,
        *stage_ctes,
    ]
    selected_stage_columns = workflow_stage_select_columns(usable_tables)
    query = f"""
        WITH {", ".join(ctes)}
        SELECT
            dak_scope.dak_id,
            dak_scope.dakid_no,
            dak_scope.fk_section,
            dak_scope.dak_record_status,
            {", ".join(selected_stage_columns)}
        FROM dak_scope
        {workflow_stage_joins(usable_tables)}
        ORDER BY dak_scope.dak_id DESC;
    """
    started_at = time.perf_counter()
    rows = pd.read_sql(text(query), engine, params={"row_limit": row_limit})
    anomalies: list[Anomaly] = []
    available_stages = set(usable_tables)
    for row in rows.to_dict("records"):
        for issue in classify_workflow_row(row, available_stages):
            extra = {
                key: value
                for key, value in issue.items()
                if key not in {"score", "stage_counts"}
            }
            anomalies.append(
                make_workflow_anomaly(
                    issue["anomaly_type"],
                    issue["dak_id"],
                    issue["anomaly_reason"],
                    float(issue["score"]),
                    stage_counts=issue["stage_counts"],
                    extra=extra,
                )
            )

    print(
        f"[workflow] Produced {len(anomalies)} process-flow anomaly candidate(s) "
        f"from {len(usable_tables)} table(s) in {time.perf_counter() - started_at:.2f}s.",
        flush=True,
    )
    return anomalies


def build_source_query(source: RuntimeSource, filter_by_dak_list_date: bool = False) -> str:
    selected_columns = [
        f"src.{quote_identifier(source.id_column)} AS transaction_id",
        f"src.{quote_identifier(source.amount_column)} AS amount",
    ]
    base_context_columns = source.base_context_columns or source.context_columns
    where_columns = [source.amount_column]

    for column in base_context_columns:
        selected_columns.append(f"src.{quote_identifier(column)} AS {quote_identifier(column)}")

    if source.date_column:
        selected_columns.append(f"src.{quote_identifier(source.date_column)} AS event_date")

    join_clauses = []
    join_aliases = {}
    dak_filter_alias = None
    extra_join_alias_by_key = {}
    ctes = []
    if source.dak_section_ids:
        if source.table == "dak":
            dak_filter_alias = "src"
        elif source.table == "gem_product":
            dak_filter_alias = "dak_filter"
            extra_join_alias_by_key[("fk_gem_bill", "gem_bill", "id")] = "gem_bill_filter"
            join_clauses.append(
                "INNER JOIN gem_bill AS gem_bill_filter "
                f"ON src.{quote_identifier('fk_gem_bill')} = gem_bill_filter.{quote_identifier('id')}"
            )
            join_clauses.append(
                "INNER JOIN dak AS dak_filter "
                f"ON gem_bill_filter.{quote_identifier('fk_dak')} = dak_filter.{quote_identifier('id')}"
            )
            selected_columns.append(f"gem_bill_filter.{quote_identifier('fk_dak')} AS {quote_identifier('fk_dak')}")
        else:
            dak_filter_alias = "dak_filter"
            extra_join_alias_by_key[("fk_dak", "dak", "id")] = dak_filter_alias
            join_clauses.append(
                "INNER JOIN dak AS dak_filter "
                f"ON src.{quote_identifier('fk_dak')} = dak_filter.{quote_identifier('id')}"
            )

    if source.table == "dak":
        workflow_ctes, workflow_joins, workflow_selected_columns = build_dak_workflow_feature_ctes()
        ctes.extend(workflow_ctes)
        join_clauses.extend(workflow_joins)
        selected_columns.extend(workflow_selected_columns)

    selected_extra_aliases = set(source.context_columns).difference(base_context_columns)
    for extra_join in EXTRA_SOURCE_JOIN_COLUMNS.get(source.table, ()):
        alias = str(extra_join["alias"])
        if alias not in selected_extra_aliases:
            continue
        join_key = (
            str(extra_join["source_column"]),
            str(extra_join["reference_table"]),
            str(extra_join["reference_pk"]),
        )
        if join_key not in extra_join_alias_by_key:
            join_alias = f"rule_j{len(extra_join_alias_by_key)}"
            extra_join_alias_by_key[join_key] = join_alias
            join_clauses.append(
                "LEFT JOIN "
                f"{quote_identifier(extra_join['reference_table'])} AS {join_alias} "
                f"ON src.{quote_identifier(extra_join['source_column'])} = "
                f"{join_alias}.{quote_identifier(extra_join['reference_pk'])}"
            )
        join_alias = extra_join_alias_by_key[join_key]
        selected_columns.append(
            f"{join_alias}.{quote_identifier(extra_join['reference_column'])} AS {quote_identifier(alias)}"
        )

    for joined in source.joined_context_columns:
        join_key = (joined.source_column, joined.reference_table, joined.reference_pk)
        if join_key not in join_aliases:
            join_alias = f"j{len(join_aliases)}"
            join_aliases[join_key] = join_alias
            join_clauses.append(
                "LEFT JOIN "
                f"{quote_identifier(joined.reference_table)} AS {join_alias} "
                f"ON src.{quote_identifier(joined.source_column)} = "
                f"{join_alias}.{quote_identifier(joined.reference_pk)}"
            )
        join_alias = join_aliases[join_key]
        selected_columns.append(
            f"{join_alias}.{quote_identifier(joined.reference_column)} AS {quote_identifier(joined.alias)}"
        )

    where_parts = [f"src.{quote_identifier(column)} IS NOT NULL" for column in where_columns]
    if dak_filter_alias:
        section_ids = ", ".join(str(section_id) for section_id in source.dak_section_ids)
        where_parts.append(f"{dak_filter_alias}.{quote_identifier('fk_section')} IN ({section_ids})")
    if filter_by_dak_list_date and dak_filter_alias:
        where_parts.append(f"{dak_filter_alias}.{quote_identifier('list_date')} BETWEEN :start_date AND :end_date")
    where_clause = " AND ".join(where_parts)
    order_clause = (
        f"ORDER BY src.{quote_identifier(source.date_column)} DESC"
        if source.date_column
        else f"ORDER BY src.{quote_identifier(source.id_column)} DESC"
    )

    with_clause = f"WITH {', '.join(ctes)}" if ctes else ""
    return f"""
        {with_clause}
        SELECT {", ".join(selected_columns)}
        FROM {quote_identifier(source.table)} AS src
        {" ".join(join_clauses)}
        WHERE {where_clause}
        {order_clause}
        LIMIT :row_limit;
    """


def load_runtime_sources(engine=None, selected_payment_category: str | None = None) -> list[RuntimeSource]:
    payment_categories = load_active_payment_category_config(engine)
    selected_payment_category = normalize_payment_category(selected_payment_category, payment_categories)
    payment_category_source_tables = payment_category_source_tables_from_config(payment_categories)
    if selected_payment_category:
        allowed_tables = (selected_payment_category,)
        allowed_physical_tables = payment_category_source_tables[selected_payment_category]
    else:
        allowed_tables = get_allowed_source_tables()
        if not allowed_tables:
            raise RuntimeError("LLAMA_BUSINESS_PRIORITY_TABLES did not provide any usable table names.")
        allowed_physical_tables = resolve_allowed_physical_source_tables(payment_category_source_tables)
    print(
        "[source] Runtime table allow-list from LLAMA_BUSINESS_PRIORITY_TABLES: "
        f"{', '.join(allowed_tables)}"
        + (f" (selected_payment_category={selected_payment_category})" if selected_payment_category else ""),
        flush=True,
    )
    schema = parse_schema_file(root_tables=allowed_physical_tables)
    sources = load_configured_runtime_sources(schema, allowed_physical_tables=allowed_physical_tables)
    if not sources:
        sources = load_candidate_audit_runtime_sources(schema, allowed_physical_tables=allowed_physical_tables)
    if len({source.table for source in sources}) < len(allowed_physical_tables):
        schema_sources = load_schema_runtime_sources(schema, allowed_physical_tables=allowed_physical_tables)
        merged_sources = {source.table: source for source in sources}
        for source in schema_sources:
            merged_sources.setdefault(source.table, source)
        sources = [merged_sources[table] for table in allowed_physical_tables if table in merged_sources]
    if not sources:
        raise RuntimeError(
            f"No valid anomaly source tables from LLAMA_BUSINESS_PRIORITY_TABLES found in {SOURCE_CONFIG_FILE}. "
            "Run `venv/bin/python backend/run_architecture.py architect` after setting the allow-list."
        )
    return apply_payment_category_filters(
        sources,
        payment_categories,
        selected_payment_category=selected_payment_category,
    )


def load_recent_transactions(
    engine,
    source: RuntimeSource,
    row_limit: int = DEFAULT_ROWS_PER_TABLE,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    filter_by_dak_list_date = bool(start_date and end_date and source.dak_section_ids)
    query = build_source_query(source, filter_by_dak_list_date=filter_by_dak_list_date)
    filter_text = f", dak_sections={list(source.dak_section_ids)}" if source.dak_section_ids else ""
    date_filter_text = f", dak.list_date={start_date}..{end_date}" if filter_by_dak_list_date else ""
    print(
        f"[query] Running source query against {source.scan_name} "
        f"(db_table={source.table}{filter_text}{date_filter_text}). row_limit={row_limit}",
        flush=True,
    )
    started_at = time.perf_counter()
    params = {"row_limit": row_limit}
    if filter_by_dak_list_date:
        params.update({"start_date": start_date, "end_date": end_date})
    df = pd.read_sql(text(query), engine, params=params)
    print(
        f"[query] Loaded {len(df)} row(s) and {len(df.columns)} column(s) "
        f"from {source.scan_name} in {time.perf_counter() - started_at:.2f}s.",
        flush=True,
    )
    return df


def get_feature_plan(source: RuntimeSource) -> tuple[dict, ...]:
    if source.feature_plan:
        return source.feature_plan

    fallback_plan = tuple(
        build_candidate_feature_plan(
            source.table,
            list(source.context_columns),
            source.date_column,
        )
    )
    if fallback_plan:
        print(
            f"[features] No LLM feature_plan found for {source.table}; "
            f"using {len(fallback_plan)} deterministic fallback feature(s).",
            flush=True,
        )
        return fallback_plan

    raise RuntimeError(f"No usable feature_plan could be built for {source.table}.")


def prepare_features(
    df: pd.DataFrame, source: RuntimeSource
) -> tuple[np.ndarray, pd.DataFrame, list[str], RobustScaler | None, pd.DataFrame]:
    started_at = time.perf_counter()
    print(f"[features] Preparing numeric feature matrix from {len(df)} row(s).", flush=True)
    required_columns = {"amount"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(f"Missing payment columns: {', '.join(sorted(missing_columns))}")

    amount = pd.to_numeric(df["amount"], errors="coerce")
    feature_plan = get_feature_plan(source)
    available_columns = set(df.columns)
    usable_feature_plan = []
    skipped_features = []
    for feature in feature_plan:
        op = feature.get("op")
        group_by = feature.get("group_by")
        source_name = feature.get("source")
        if op in {"group_frequency", "ratio_to_group_median", "group_rank_pct"} and group_by not in available_columns:
            skipped_features.append(f"{feature.get('name', op)} missing group_by={group_by}")
            continue
        if op in {"age_days", "day_of_week", "hour"} and source_name == "event_date" and "event_date" not in available_columns:
            skipped_features.append(f"{feature.get('name', op)} missing event_date")
            continue
        usable_feature_plan.append(feature)

    if skipped_features:
        print(
            "[features] Skipped unusable feature(s): "
            + "; ".join(skipped_features[:8])
            + ("; ..." if len(skipped_features) > 8 else ""),
            flush=True,
        )

    features = compute_feature_frame(df, list(usable_feature_plan))
    if features.empty:
        print("[features] Feature plan produced no usable columns.", flush=True)
        return np.empty((0, 0)), df.iloc[0:0].copy(), [], None, df.iloc[0:0].copy()

    valid_rows = amount.notna()
    features = features.loc[valid_rows]
    clean_df = df.loc[valid_rows].reset_index(drop=True)
    features = features.fillna(features.median(numeric_only=True)).fillna(0)
    features = features.reset_index(drop=True)
    dropped = len(df) - len(features)
    print(
        f"[features] Prepared matrix rows={len(features)}, columns={len(features.columns)}, "
        f"dropped_rows={dropped} in {time.perf_counter() - started_at:.2f}s.",
        flush=True,
    )
    if features.empty:
        return np.empty((0, 0)), df.iloc[0:0].copy(), [], None, df.iloc[0:0].copy()

    scaler = RobustScaler()
    scaled = scaler.fit_transform(features.to_numpy(dtype=float))
    return (
        scaled,
        clean_df,
        list(features.columns),
        scaler,
        features,
    )


def estimate_feature_importance(
    features: np.ndarray,
    feature_names: list[str],
    scores: np.ndarray,
    predictions: np.ndarray,
) -> list[dict]:
    if features.size == 0 or not feature_names:
        return []

    anomaly_mask = predictions == -1
    scored_features = features[anomaly_mask] if anomaly_mask.any() else features
    scored_scores = scores[anomaly_mask] if anomaly_mask.any() else scores
    weights = np.maximum(scored_scores, 0)
    weighted_magnitude = np.abs(scored_features) * weights.reshape(-1, 1)
    raw_importance = weighted_magnitude.mean(axis=0)
    total = float(raw_importance.sum()) or 1.0
    ranked = sorted(
        (
            {
                "feature": name,
                "importance": round(float(value / total), 6),
            }
            for name, value in zip(feature_names, raw_importance)
        ),
        key=lambda item: item["importance"],
        reverse=True,
    )
    return ranked


def row_feature_contributions(
    features: np.ndarray,
    feature_names: list[str],
    row_index: int,
    limit: int = 5,
) -> list[dict]:
    if features.size == 0 or not feature_names:
        return []

    row = np.abs(features[row_index])
    total = float(row.sum()) or 1.0
    ranked = sorted(
        (
            {
                "feature": name,
                "contribution": round(float(value / total), 6),
            }
            for name, value in zip(feature_names, row)
        ),
        key=lambda item: item["contribution"],
        reverse=True,
    )
    return ranked[:limit]


def build_autoencoder(hidden_layer_sizes: tuple[int, ...]) -> MLPRegressor:
    return MLPRegressor(
        hidden_layer_sizes=hidden_layer_sizes,
        activation="relu",
        solver="adam",
        alpha=0.0005,
        batch_size="auto",
        learning_rate_init=0.001,
        max_iter=250,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=12,
        random_state=42,
    )


def autoencoder_hidden_layers(feature_count: int) -> tuple[int, int, int]:
    encoder_width = max(4, min(32, feature_count * 2))
    bottleneck_width = max(2, min(12, feature_count // 2 or 2))
    return (encoder_width, bottleneck_width, encoder_width)


def score_with_autoencoder(
    features: np.ndarray,
    isolation_predictions: np.ndarray,
    contamination: float,
    confirmation_quantile: float = DEFAULT_AUTOENCODER_CONFIRMATION_QUANTILE,
) -> tuple[np.ndarray, np.ndarray, float]:
    if len(features) < 20 or features.shape[1] == 0:
        return np.zeros(len(features), dtype=float), np.zeros(len(features), dtype=float), float("inf")

    normal_features = features[isolation_predictions != -1]
    training_features = normal_features if len(normal_features) >= 20 else features
    hidden_layers = autoencoder_hidden_layers(features.shape[1])
    print(
        f"[model] Fitting autoencoder rows={len(training_features)}, "
        f"features={features.shape[1]}, hidden_layers={hidden_layers}.",
        flush=True,
    )
    started_at = time.perf_counter()
    model = build_autoencoder(hidden_layers)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ConvergenceWarning)
        model.fit(training_features, training_features)

    reconstructed = model.predict(features)
    errors = np.mean(np.square(features - reconstructed), axis=1)
    baseline = float(np.median(errors)) or 1e-9
    scores = np.clip((errors / baseline) * 10, 0, 100)
    quantile = max(confirmation_quantile, 1 - contamination)
    threshold = float(np.quantile(errors, quantile))
    print(
        f"[model] Autoencoder score finished in {time.perf_counter() - started_at:.2f}s. "
        f"threshold={threshold:.6f}, quantile={quantile:.2f}.",
        flush=True,
    )
    return scores, errors, threshold


def build_statistical_reason(row: pd.Series, clean_df: pd.DataFrame, source: RuntimeSource, score: float) -> str:
    amount = float(row["amount"])
    amounts = pd.to_numeric(clean_df["amount"], errors="coerce").dropna()
    median = float(amounts.median()) if not amounts.empty else 0.0
    p95 = float(amounts.quantile(0.95)) if len(amounts) > 1 else median
    rank_pct = float((amounts <= amount).mean() * 100) if not amounts.empty else 0.0

    parts = [
        f"This {source.scan_name} record has {source.amount_column} of Rs {amount:,.2f}. "
        f"It is higher than about {rank_pct:.1f}% of the latest {len(clean_df):,} checked records."
    ]

    if median > 0:
        parts.append(f"A normal middle value is Rs {median:,.2f}. A very high value starts near Rs {p95:,.2f}.")

    context_bits = []
    for column in source.context_columns:
        if column not in clean_df.columns or column not in row or pd.isna(row[column]):
            continue
        group = clean_df[clean_df[column] == row[column]]
        if len(group) < 2:
            context_bits.append(
                f"{column}={format_context_value(row[column])} appears only once in the checked records"
            )
            continue
        group_amounts = pd.to_numeric(group["amount"], errors="coerce").dropna()
        group_median = float(group_amounts.median()) if not group_amounts.empty else 0.0
        if group_median > 0:
            multiple = amount / group_median
            if multiple >= 2:
                context_bits.append(
                    f"for this {column}, this amount is {multiple:.1f} times the normal middle value "
                    f"of Rs {group_median:,.2f}"
                )

    if context_bits:
        parts.append("Also, " + "; ".join(context_bits[:2]) + ".")

    parts.append(f"Overall unusual score: {score:.2f}. Higher means more unusual.")
    return " ".join(parts)


def format_context_value(value) -> str:
    if pd.isna(value):
        return "unknown"
    if isinstance(value, (float, np.floating)) and value.is_integer():
        return str(int(value))
    return str(value)


def json_safe_value(value):
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    if pd.isna(value):
        return None
    return value


def json_safe_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, np.ndarray):
        value = value.tolist()
    if isinstance(value, (list, tuple, set)):
        return [json_safe_value(item) for item in value]
    if pd.isna(value):
        return []
    return [json_safe_value(value)]


def json_safe_object(value):
    if isinstance(value, dict):
        return {str(key): json_safe_object(item) for key, item in value.items()}
    if isinstance(value, np.ndarray):
        return [json_safe_object(item) for item in value.tolist()]
    if isinstance(value, (list, tuple, set)):
        return [json_safe_object(item) for item in value]
    return json_safe_value(value)


def append_autoencoder_confirmation(
    reason: str,
    autoencoder_score: float,
    reconstruction_error: float,
    threshold: float,
) -> str:
    return (
        f"{reason} A second check also found this row unusual. "
        f"Second check score: {autoencoder_score:.2f}."
    )


def has_functional_rule_features(source: RuntimeSource) -> bool:
    if not ENABLE_FUNCTIONAL_RULE_DETECTOR:
        return False
    return any(feature.get("op") in FUNCTIONAL_RULE_OPERATIONS for feature in get_feature_plan(source))


def functional_rule_features(source: RuntimeSource, raw_features: pd.DataFrame) -> list[dict]:
    return [
        feature
        for feature in get_feature_plan(source)
        if feature.get("op") in FUNCTIONAL_RULE_OPERATIONS and feature.get("name") in raw_features.columns
    ]


def build_functional_rule_reason(
    source: RuntimeSource,
    source_record_id: str,
    triggered_features: list[dict],
) -> str:
    reasons = []
    for feature in triggered_features:
        reason = str(feature.get("reason") or feature.get("name") or "A fraud-rule check failed.").strip(" .")
        if reason and reason not in reasons:
            reasons.append(reason)

    if not reasons:
        return f"{source.scan_name} record {source_record_id} failed a configured fraud-rule check."

    joined_reasons = "; ".join(reasons[:3])
    extra = len(reasons) - 3
    if extra > 0:
        joined_reasons = f"{joined_reasons}; plus {extra} more rule check(s)"
    return f"{source.scan_name} record {source_record_id} failed fraud-rule check(s): {joined_reasons}."


def detect_functional_rule_anomalies(df: pd.DataFrame, source: RuntimeSource) -> list[Anomaly]:
    started_at = time.perf_counter()
    features, clean_df, feature_names, _scaler, raw_features = prepare_features(df, source)
    if raw_features.empty or clean_df.empty:
        print("[rules] Functional feature plan produced no usable rule columns.", flush=True)
        return []

    rule_features = functional_rule_features(source, raw_features)
    rule_names = [feature["name"] for feature in rule_features]
    if not rule_names:
        print("[rules] No usable functional rule feature columns found.", flush=True)
        return []

    rule_values = raw_features[rule_names].fillna(0)
    triggered_mask = rule_values.gt(0).any(axis=1)
    triggered_indices = np.where(triggered_mask.to_numpy())[0]
    anomalies: list[Anomaly] = []
    for idx in triggered_indices:
        row = clean_df.iloc[idx]
        source_record_id = normalize_record_id(row["transaction_id"])
        row_rule_values = rule_values.iloc[idx]
        triggered_features = [
            feature
            for feature in rule_features
            if float(row_rule_values.get(feature["name"], 0) or 0) > 0
        ]
        failed_rule_names = [feature["name"] for feature in triggered_features]
        failed_rule_count = len(failed_rule_names)
        rule_score = min(100.0, 55.0 + (failed_rule_count * 10.0))
        engineered_feature_values = {
            name: json_safe_value(value)
            for name, value in raw_features.iloc[idx].to_dict().items()
        }
        rule_reason = build_functional_rule_reason(source, source_record_id, triggered_features)
        context = {
            "source_table": source.scan_name,
            "source_db_table": source.table,
            "dak_section_filter": list(source.dak_section_ids),
            "source_amount_column": source.amount_column,
            "transaction_id": source_record_id,
            "amount_in_rupees": float(row["amount"]),
            "engineered_features_used": feature_names,
            "engineered_feature_values": engineered_feature_values,
            "failed_rule_features": failed_rule_names,
            "failed_rule_count": failed_rule_count,
            "rule_reason": rule_reason,
            "statistical_reason": rule_reason,
            "detector_type": "functional_rule",
            "isolation_score": rule_score,
            "detection_stage": "functional_rule",
        }
        add_display_context(context, row=row, source=source)
        for column in source.context_columns:
            if column in row:
                context[column] = json_safe_value(row[column])
        anomalies.append(
            Anomaly(
                transaction_id=f"{source.scan_name}:{source_record_id}",
                table_name=source.scan_name,
                source_record_id=source_record_id,
                score=rule_score,
                context=context,
            )
        )

    print(
        f"[rules] Functional rules produced {len(anomalies)} candidate(s) "
        f"from {len(rule_names)} rule feature(s) in {time.perf_counter() - started_at:.2f}s.",
        flush=True,
    )
    return anomalies


def explain_autoencoder_rejection(
    source: RuntimeSource,
    source_record_id: str,
    autoencoder_score: float,
    reconstruction_error: float,
    threshold: float,
) -> None:
    print(
        f"[model] Autoencoder rejected {source.scan_name}:{source_record_id} "
        f"score={autoencoder_score:.2f}, error={reconstruction_error:.6f}, "
        f"threshold={threshold:.6f}.",
        flush=True,
    )


def normalize_record_id(value) -> str:
    if pd.isna(value):
        return "unknown"
    if isinstance(value, (float, np.floating)) and value.is_integer():
        return str(int(value))
    return str(value)


def detect_anomalies(
    df: pd.DataFrame,
    source: RuntimeSource,
    contamination: float = DEFAULT_CONTAMINATION,
    detection_stage: str = DEFAULT_DETECTION_STAGE,
) -> list[Anomaly]:
    started_at = time.perf_counter()
    print(
        f"[model] Starting anomaly detection for {source.scan_name}.{source.amount_column}.",
        flush=True,
    )
    if df.empty:
        print("[model] No rows to score.", flush=True)
        return []

    if has_functional_rule_features(source):
        print(
            f"[rules] Using functional fraud-rule detection for {source.scan_name}; "
            "skipping IsolationForest amount-distribution scoring.",
            flush=True,
        )
        return detect_functional_rule_anomalies(df, source)

    features, clean_df, feature_names, scaler, raw_features = prepare_features(df, source)
    if len(features) < 20:
        print(f"[model] Only {len(features)} usable rows; need at least 20. Skipping.", flush=True)
        return []

    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=200,
    )
    print(
        f"[model] Fitting IsolationForest rows={len(features)}, "
        f"features={features.shape[1]}, contamination={contamination}.",
        flush=True,
    )
    fit_started_at = time.perf_counter()
    predictions = model.fit_predict(features)
    scores = -model.decision_function(features)
    print(
        f"[model] IsolationForest fit+score finished in "
        f"{time.perf_counter() - fit_started_at:.2f}s.",
        flush=True,
    )

    detection_stage = detection_stage if detection_stage in {"isolation", "autoencoder"} else "isolation"
    feature_importance = estimate_feature_importance(features, feature_names, scores, predictions)
    autoencoder_scores = np.zeros(len(features), dtype=float)
    reconstruction_errors = np.zeros(len(features), dtype=float)
    autoencoder_threshold = float("inf")
    if detection_stage == "autoencoder":
        autoencoder_scores, reconstruction_errors, autoencoder_threshold = score_with_autoencoder(
            features,
            predictions,
            contamination,
        )

    # Supervision focus: rows resembling reviewer-accepted anomalies get a score
    # boost, close near-misses are promoted, and rows resembling rejected
    # false positives are down-ranked or suppressed.
    accepted_signatures = load_accepted_signatures(source.scan_name)
    supervision_boost, supervision_proximity = compute_supervision_boost(
        features, feature_names, accepted_signatures, scaler
    )
    rejected_signatures = load_rejected_signatures(source.scan_name)
    supervision_penalty, rejection_proximity = compute_supervision_penalty(
        features, feature_names, rejected_signatures, scaler
    )
    base_anomaly_mask = predictions == -1
    promote_mask = supervision_proximity >= SUPERVISION_PROMOTE_PROXIMITY
    suppress_mask = (
        (rejection_proximity >= SUPERVISION_SUPPRESS_PROXIMITY)
        & (supervision_proximity < SUPERVISION_PROMOTE_PROXIMITY)
    )
    anomaly_indices = np.where((base_anomaly_mask | promote_mask) & ~suppress_mask)[0]
    promoted_count = int(np.count_nonzero(promote_mask & ~base_anomaly_mask))
    if accepted_signatures:
        print(
            f"[supervision] {source.scan_name}: {len(accepted_signatures)} accepted signature(s); "
            f"promoted {promoted_count} near-match row(s) beyond IsolationForest.",
            flush=True,
        )
    if rejected_signatures:
        suppressed_count = int(np.count_nonzero((base_anomaly_mask | promote_mask) & suppress_mask))
        print(
            f"[supervision] {source.scan_name}: {len(rejected_signatures)} rejected signature(s); "
            f"suppressed {suppressed_count} false-positive match(es).",
            flush=True,
        )

    anomalies: list[Anomaly] = []
    for idx in anomaly_indices:
        row = clean_df.iloc[idx]
        source_record_id = normalize_record_id(row["transaction_id"])
        autoencoder_score = float(autoencoder_scores[idx])
        reconstruction_error = float(reconstruction_errors[idx])
        row_boost = float(supervision_boost[idx])
        row_penalty = float(supervision_penalty[idx])
        row_proximity = float(supervision_proximity[idx])
        row_rejection_proximity = float(rejection_proximity[idx])
        is_promoted = bool(promote_mask[idx] and not base_anomaly_mask[idx])
        # Keep supervision near-matches even if the autoencoder would reject them.
        if (
            detection_stage == "autoencoder"
            and reconstruction_error < autoencoder_threshold
            and row_proximity < SUPERVISION_PROMOTE_PROXIMITY
        ):
            explain_autoencoder_rejection(
                source,
                source_record_id,
                autoencoder_score,
                reconstruction_error,
                autoencoder_threshold,
            )
            continue

        isolation_score = float(scores[idx] * 100) + row_boost - row_penalty
        statistical_reason = build_statistical_reason(
            row,
            clean_df,
            source,
            isolation_score,
        )
        engineered_feature_values = {
            name: json_safe_value(value)
            for name, value in raw_features.iloc[idx].to_dict().items()
        }
        context = {
            "source_table": source.scan_name,
            "source_db_table": source.table,
            "dak_section_filter": list(source.dak_section_ids),
            "source_amount_column": source.amount_column,
            "transaction_id": source_record_id,
            "amount_in_rupees": float(row["amount"]),
            "engineered_features_used": feature_names,
            "engineered_feature_values": engineered_feature_values,
            "table_feature_importance": feature_importance[:10],
            "row_top_feature_contributions": row_feature_contributions(features, feature_names, idx),
            "isolation_score": isolation_score,
            "detection_stage": detection_stage,
            "statistical_reason": statistical_reason,
            "supervision_boost": round(row_boost, 4),
            "supervision_penalty": round(row_penalty, 4),
            "supervision_proximity": round(row_proximity, 4),
            "rejection_proximity": round(row_rejection_proximity, 4),
            "supervision_match": bool(row_proximity >= SUPERVISION_PROMOTE_PROXIMITY or row_boost > 0),
            "rejection_match": bool(row_rejection_proximity >= SUPERVISION_SUPPRESS_PROXIMITY or row_penalty > 0),
            "supervision_promoted": is_promoted,
        }
        anomaly_score = isolation_score
        if detection_stage == "autoencoder":
            context.update(
                {
                    "autoencoder_score": autoencoder_score,
                    "autoencoder_reconstruction_error": reconstruction_error,
                    "autoencoder_threshold": autoencoder_threshold,
                    "statistical_reason": append_autoencoder_confirmation(
                        statistical_reason,
                        autoencoder_score,
                        reconstruction_error,
                        autoencoder_threshold,
                    ),
                }
            )
            anomaly_score = max(isolation_score, autoencoder_score)
        for column in source.context_columns:
            if column in row and pd.notna(row[column]):
                context[column] = json_safe_value(row[column])
        anomalies.append(
            Anomaly(
                transaction_id=f"{source.scan_name}:{source_record_id}",
                table_name=source.scan_name,
                source_record_id=source_record_id,
                score=anomaly_score,
                context=context,
            )
        )

    print(
        f"[model] {detection_stage} produced {len(anomalies)} anomaly candidate(s) "
        f"in {time.perf_counter() - started_at:.2f}s.",
        flush=True,
    )
    return anomalies


def generate_reasoning_via_llama(
    client: OpenAI,
    row_data: dict,
    index: int,
    total: int,
    supervision_context: str = "",
) -> str:
    statistical_reason = row_data.get("statistical_reason")
    detector_type = row_data.get("detector_type")
    if detector_type == "workflow_process":
        focus = (
            "Explain the missing step, wrong step, or duplicate step in the business flow. "
            "Do not talk about amount unless it is given."
        )
    elif detector_type == "functional_rule":
        focus = (
            "Explain only the failed fraud-rule checks in rule_reason. "
            "Do not compare this row with normal records or typical amounts."
        )
    elif detector_type == "forensic_cross_bill":
        focus = (
            "Explain the linked bill/DAK pattern in forensic_reason. "
            "Focus on repeated invoice, vendor, date, amount, or DAK relationships. "
            "Do not compare this row with normal records or typical amounts."
        )
    else:
        focus = "Explain the amount, date, status, or group value that looks different from normal records."
    grounding = ""
    if supervision_context:
        grounding = (
            "\nExtra context from past user feedback. Use it only if it helps. "
            "Do not copy it word for word:\n"
            f"{supervision_context}\n"
        )
    similarity_instruction = (
        ""
        if detector_type in {"functional_rule", "forensic_cross_bill"}
        else 'If it matches a pattern the user accepted before, say: "This is similar to a case the user accepted before."'
    )
    prompt = f"""
This row was marked as unusual:
{json.dumps(json_safe_object(row_data), indent=2)}
{grounding}
Write the explanation in very simple words.
Use 2 short sentences maximum.
Say exactly why this row looks unusual.
{focus}
Use the supplied statistical_reason, rule_reason, or forensic_reason as the facts. Do not invent anything.
Do not use technical words like algorithm, vector, model, percentile, reconstruction, threshold, anomaly, anomalous, or data profile.
{similarity_instruction}
"""
    try:
        settings = get_llama_settings()
        print(
            f"[llama] Explaining anomaly {index}/{total}: "
            f"{row_data.get('source_table')} id={row_data.get('transaction_id')}.",
            flush=True,
        )
        started_at = time.perf_counter()
        response = client.chat.completions.create(
            model=settings["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        explanation = response.choices[0].message.content.strip()
        print(
            f"[llama] Explanation {index}/{total} finished in "
            f"{time.perf_counter() - started_at:.2f}s.",
            flush=True,
        )
        return explanation
    except Exception as exc:
        print(
            f"[llama] Explanation {index}/{total} failed with {type(exc).__name__}; "
            "using deterministic statistical explanation.",
            flush=True,
        )
        return statistical_reason or "This record is unusual compared with the scanned records."


def select_balanced_anomalies(
    anomalies: list[Anomaly],
    budget: int,
    model_reserve_fraction: float = MODEL_ANOMALY_RESERVE_FRACTION,
) -> list[Anomaly]:
    """Pick which anomalies to explain, reserving a share for model detections.

    Workflow/gem detectors can emit thousands of fixed-score candidates that
    would otherwise crowd IsolationForest/autoencoder anomalies out of the
    explanation budget. Reserve a fraction of the budget for model anomalies so
    the supervision loop always has real model patterns to learn from.
    """
    by_score = lambda anomaly: anomaly.score
    model = sorted(
        (a for a in anomalies if not a.context.get("detector_type")),
        key=by_score,
        reverse=True,
    )
    other = sorted(
        (a for a in anomalies if a.context.get("detector_type")),
        key=by_score,
        reverse=True,
    )

    if budget <= 0 or len(anomalies) <= budget:
        return sorted(anomalies, key=by_score, reverse=True)

    model_quota = min(len(model), int(budget * model_reserve_fraction))
    other_quota = min(len(other), budget - model_quota)
    leftover = budget - model_quota - other_quota
    if leftover > 0:
        model_quota = min(len(model), model_quota + leftover)

    chosen = model[:model_quota] + other[:other_quota]
    chosen.sort(key=by_score, reverse=True)
    print(
        f"[persist] Explanation budget {budget}: reserved {model_quota} model "
        f"anomaly slot(s), {other_quota} workflow/gem slot(s) "
        f"(available model={len(model)}, other={len(other)}).",
        flush=True,
    )
    return chosen


def primary_contributing_feature(anomaly: Anomaly) -> str | None:
    contributions = anomaly.context.get("row_top_feature_contributions") or []
    if isinstance(contributions, list) and contributions:
        first = contributions[0]
        if isinstance(first, dict) and first.get("feature"):
            return str(first["feature"])
    failed_rules = anomaly.context.get("failed_rule_features") or []
    if isinstance(failed_rules, list) and failed_rules:
        return str(failed_rules[0])
    return None


def limit_anomalies_per_feature(
    anomalies: list[Anomaly],
    max_per_feature: int = MAX_ANOMALIES_PER_FEATURE,
) -> list[Anomaly]:
    if max_per_feature <= 0:
        return anomalies
    kept = []
    counts: dict[str, int] = {}
    for anomaly in sorted(anomalies, key=lambda item: item.score, reverse=True):
        feature = primary_contributing_feature(anomaly)
        if not feature:
            kept.append(anomaly)
            continue
        if counts.get(feature, 0) >= max_per_feature:
            continue
        counts[feature] = counts.get(feature, 0) + 1
        kept.append(anomaly)
    if len(kept) != len(anomalies):
        print(
            f"[persist] Per-feature cap kept {len(kept)} of {len(anomalies)} "
            f"candidate(s), max_per_feature={max_per_feature}.",
            flush=True,
        )
    return kept


def _insert_anomaly_row(conn, anomaly: Anomaly, explanation: str) -> int:
    safe_context = json_safe_object(anomaly.context)
    isolation_score = (
        None
        if safe_context.get("detector_type") == "gem_repeat_purchase"
        else safe_context.get("isolation_score", anomaly.score)
    )
    autoencoder_score = safe_context.get("autoencoder_score")
    result = conn.execute(
        text(
            """
            INSERT INTO detected_anomalies (
                transaction_id,
                table_name,
                source_record_id,
                anomaly_score,
                isolation_score,
                autoencoder_score,
                feature_snapshot,
                explanation
            )
            VALUES (
                :transaction_id,
                :table_name,
                :source_record_id,
                :score,
                :isolation_score,
                :autoencoder_score,
                CAST(:feature_snapshot AS JSONB),
                :explanation
            )
            ON CONFLICT (transaction_id) DO UPDATE SET
                table_name = EXCLUDED.table_name,
                source_record_id = EXCLUDED.source_record_id,
                anomaly_score = EXCLUDED.anomaly_score,
                isolation_score = EXCLUDED.isolation_score,
                autoencoder_score = EXCLUDED.autoencoder_score,
                feature_snapshot = EXCLUDED.feature_snapshot,
                explanation = EXCLUDED.explanation,
                detected_at = NOW();
            """
        ),
        {
            "transaction_id": anomaly.transaction_id,
            "table_name": anomaly.table_name,
            "source_record_id": anomaly.source_record_id,
            "score": anomaly.score,
            "isolation_score": isolation_score,
            "autoencoder_score": autoencoder_score,
            "feature_snapshot": json.dumps(safe_context),
            "explanation": explanation,
        },
    )
    return result.rowcount or 0


def save_anomalies(
    engine,
    llama_client: OpenAI,
    anomalies: Iterable[Anomaly],
    max_explanations: int = DEFAULT_MAX_EXPLANATIONS,
    batch_size: int = SAVE_COMMIT_BATCH_SIZE,
) -> int:
    anomalies = list(anomalies)
    anomalies = limit_anomalies_per_feature(anomalies)
    total = len(anomalies)
    to_explain = select_balanced_anomalies(anomalies, max_explanations)[:max_explanations]
    skipped = max(0, total - len(to_explain))
    print(
        f"[persist] Persisting {len(to_explain)} of {total} anomaly candidate(s). "
        f"Skipped_explanations={skipped}. Commit batch size={batch_size}.",
        flush=True,
    )
    supervision_context = load_supervision_context_text()
    inserted = 0
    batch_size = max(1, batch_size)

    # Generate explanations outside the DB transaction, then commit each batch so
    # rows become visible to the dashboard progressively rather than all at once.
    for batch_start in range(0, len(to_explain), batch_size):
        chunk = to_explain[batch_start : batch_start + batch_size]
        prepared: list[tuple[Anomaly, str]] = []
        for offset, anomaly in enumerate(chunk):
            index = batch_start + offset + 1
            explanation = generate_reasoning_via_llama(
                llama_client,
                json_safe_object(anomaly.context),
                index,
                len(to_explain),
                supervision_context=supervision_context,
            )
            prepared.append((anomaly, explanation))

        with engine.begin() as conn:
            for anomaly, explanation in prepared:
                inserted += _insert_anomaly_row(conn, anomaly, explanation)

        print(
            f"[persist] Committed batch ending at {batch_start + len(chunk)}/"
            f"{len(to_explain)}. Upserted so far={inserted}.",
            flush=True,
        )

    print(f"[persist] Database write complete. Upserted rows={inserted}.", flush=True)
    return inserted


def remove_unconfirmed_scan_rows(
    engine,
    scanned_table_names: Iterable[str],
    confirmed_transaction_ids: Iterable[str],
) -> int:
    table_names = sorted({table for table in scanned_table_names if table})
    if not table_names:
        return 0

    confirmed_ids = sorted({transaction_id for transaction_id in confirmed_transaction_ids if transaction_id})
    with engine.begin() as conn:
        if confirmed_ids:
            result = conn.execute(
                text(
                    """
                    DELETE FROM detected_anomalies
                    WHERE review_status IS NULL
                      AND table_name = ANY(:table_names)
                      AND NOT (transaction_id = ANY(:confirmed_ids));
                    """
                ),
                {
                    "table_names": table_names,
                    "confirmed_ids": confirmed_ids,
                },
            )
        else:
            result = conn.execute(
                text(
                    """
                    DELETE FROM detected_anomalies
                    WHERE review_status IS NULL
                      AND table_name = ANY(:table_names);
                    """
                ),
                {"table_names": table_names},
            )
    removed = result.rowcount or 0
    print(
        f"[persist] Removed {removed} unreviewed row(s) no longer confirmed "
        "by the latest scan.",
        flush=True,
    )
    return removed


def run_scan(
    engine,
    llama_client: OpenAI,
    max_explanations: int = DEFAULT_MAX_EXPLANATIONS,
    max_tables: int = DEFAULT_MAX_TABLES_PER_SCAN,
    rows_per_table: int = DEFAULT_ROWS_PER_TABLE,
    detection_stage: str = DEFAULT_DETECTION_STAGE,
    payment_category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    started_at = time.perf_counter()
    print(
        "[scan] Starting scan cycle"
        + (f" for payment_category={payment_category}" if payment_category else "")
        + (f", dak.list_date={start_date}..{end_date}" if start_date and end_date else "")
        + ".",
        flush=True,
    )
    sources = load_runtime_sources(engine, selected_payment_category=payment_category)
    all_anomalies = []
    scanned_tables = []
    skipped_tables = []

    for candidate_index, source in enumerate(sources, start=1):
        if len(scanned_tables) >= max_tables:
            print(f"[scan] Reached max_tables={max_tables}; stopping source scan.", flush=True)
            break

        print(
            "[source] Candidate "
            f"{candidate_index}/{len(sources)}: table={source.scan_name}, "
            f"db_table={source.table}, "
            f"id={source.id_column}, amount={source.amount_column}, "
            f"context={list(source.context_columns)}, "
            f"order={source.date_column or source.id_column}.",
            flush=True,
        )
        if not table_exists(engine, source.table):
            skipped_tables.append({"table": source.scan_name, "db_table": source.table, "reason": "missing"})
            continue

        df = load_recent_transactions(
            engine,
            source,
            row_limit=rows_per_table,
            start_date=start_date,
            end_date=end_date,
        )
        if df.empty:
            skipped_tables.append({"table": source.scan_name, "db_table": source.table, "reason": "empty"})
            continue

        print(f"Using schema-verified anomaly source: {source.scan_name}.{source.amount_column}", flush=True)
        anomalies = detect_anomalies(df, source, detection_stage=detection_stage)
        all_anomalies.extend(anomalies)
        scanned_tables.append(
            {
                "table": source.scan_name,
                "db_table": source.table,
                "dak_section_filter": list(source.dak_section_ids),
                "dak_list_date_start": start_date,
                "dak_list_date_end": end_date,
                "amount_column": source.amount_column,
                "rows_loaded": len(df),
                "anomaly_candidates": len(anomalies),
            }
        )

    gem_repeat_anomalies = []
    if os.getenv("ENABLE_GEM_REPEAT_DETECTOR", "0").strip() == "1" and all(
        is_allowed_source_table(table) for table in ("gem_bill", "gem_product")
    ):
        gem_repeat_anomalies = detect_gem_repeat_purchase_anomalies(engine)
        all_anomalies.extend(gem_repeat_anomalies)
    if gem_repeat_anomalies:
        scanned_tables.append(
            {
                "table": "gem_bill+gem_product",
                "amount_column": "product_embedding_similarity",
                "rows_loaded": len(gem_repeat_anomalies),
                "anomaly_candidates": len(gem_repeat_anomalies),
            }
        )

    all_anomalies.sort(key=lambda anomaly: anomaly.score, reverse=True)
    capped_anomalies = limit_anomalies_per_feature(all_anomalies)
    inserted = save_anomalies(engine, llama_client, capped_anomalies, max_explanations)
    removed = remove_unconfirmed_scan_rows(
        engine,
        (table["table"] for table in scanned_tables),
        (anomaly.transaction_id for anomaly in capped_anomalies),
    )
    duration = time.perf_counter() - started_at
    result = {
        "tables_scanned": len(scanned_tables),
        "scanned_tables": scanned_tables,
        "payment_category": payment_category,
        "dak_list_date_start": start_date,
        "dak_list_date_end": end_date,
        "skipped_tables": skipped_tables[:20],
        "rows_loaded": sum(table["rows_loaded"] for table in scanned_tables),
        "anomaly_candidates": len(all_anomalies),
        "anomaly_candidates_after_feature_cap": len(capped_anomalies),
        "anomalies_stored": inserted,
        "stale_anomalies_removed": removed,
        "detection_stage": detection_stage,
        "duration_seconds": round(duration, 2),
    }
    print(f"[scan] Finished scan cycle: {json.dumps(json_safe_object(result))}", flush=True)
    return result


def start_continuous_monitoring(
    interval_seconds: int = 10,
    once: bool = False,
    max_explanations: int = DEFAULT_MAX_EXPLANATIONS,
    max_tables: int = DEFAULT_MAX_TABLES_PER_SCAN,
    rows_per_table: int = DEFAULT_ROWS_PER_TABLE,
    detection_stage: str = DEFAULT_DETECTION_STAGE,
    payment_category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> None:
    print("[startup] ml_engine.py starting.", flush=True)
    print(
        "[startup] Mode="
        f"{'single scan' if once else 'continuous monitor'}, "
        f"interval={interval_seconds}s, max_explanations={max_explanations}, "
        f"max_tables={max_tables}, rows_per_table={rows_per_table}, "
        f"detection_stage={detection_stage}, "
        f"dak.list_date={start_date or 'any'}..{end_date or 'any'}.",
        flush=True,
    )
    print("[startup] React UI is separate. Run `cd frontend && npm run dev` for the browser UI.", flush=True)
    print("[startup] API service is separate. Run `python3 backend/api_server.py` for localhost:5000.", flush=True)
    engine = build_engine()
    llama_client = build_llama_client()

    try:
        init_alert_tables(engine)
    except SQLAlchemyError as exc:
        print(f"Database unavailable. Check DB_* settings and PostgreSQL status. Details: {exc}")
        return

    print("Anomaly Engine Active. Listening for structural anomalies...")
    while True:
        try:
            result = run_scan(
                engine,
                llama_client,
                max_explanations=max_explanations,
                max_tables=max_tables,
                rows_per_table=rows_per_table,
                detection_stage=detection_stage,
                payment_category=payment_category,
                start_date=start_date,
                end_date=end_date,
            )
            print(
                f"Scan complete. Stored/updated anomaly rows: {result['anomalies_stored']}",
                flush=True,
            )
        except SQLAlchemyError as exc:
            print(f"Scan skipped because the database query failed: {exc}")
        except ValueError as exc:
            print(f"Scan skipped because source data is invalid: {exc}")
        except RuntimeError as exc:
            print(f"Scan stopped because no verified source is available: {exc}")
            return

        if once:
            return
        print(f"[loop] Sleeping {interval_seconds}s before next scan.", flush=True)
        time.sleep(interval_seconds)


def find_available_port(host: str, preferred_port: int) -> int:
    for port in range(preferred_port, preferred_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
            except OSError:
                continue
            return port
    raise RuntimeError(f"No free port found from {preferred_port} to {preferred_port + 49}.")


def stream_process_output(prefix: str, process: subprocess.Popen) -> None:
    if not process.stdout:
        return
    for line in process.stdout:
        print(f"[{prefix}] {line.rstrip()}", flush=True)


def ensure_frontend_dependencies() -> bool:
    """Make sure the React app can start.

    Returns True when the dev server can be launched. Installs node_modules
    automatically when missing (zero-intervention goal). Returns False (with a
    clear instruction) when npm itself is unavailable so the API can still run.
    """
    from shutil import which

    if which("npm") is None:
        print(
            "[ui] npm not found on PATH. The API still runs; install Node.js, then "
            "run `cd frontend && npm install && npm run dev` for the dashboard.",
            flush=True,
        )
        return False

    if (FRONTEND_DIR / "node_modules").is_dir():
        return True

    print("[ui] frontend/node_modules missing; running `npm install` once...", flush=True)
    try:
        result = subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, check=False)
    except OSError as exc:
        print(f"[ui] npm install could not start: {exc}", flush=True)
        return False
    if result.returncode != 0:
        print(
            f"[ui] npm install failed (exit {result.returncode}). The API still runs; "
            "fix the install, then `cd frontend && npm run dev`.",
            flush=True,
        )
        return False
    print("[ui] npm install complete.", flush=True)
    return True


def start_react_dev_server(host: str, port: int, api_url: str) -> subprocess.Popen | None:
    if not ensure_frontend_dependencies():
        return None
    env = os.environ.copy()
    env["VITE_API_BASE_URL"] = api_url
    command = [
        "npm",
        "run",
        "dev",
        "--",
        "--host",
        host,
        "--port",
        str(port),
        "--strictPort",
    ]
    print(f"[ui] Starting React dev server: {' '.join(command)}", flush=True)
    print(f"[ui] VITE_API_BASE_URL={api_url}", flush=True)
    process = subprocess.Popen(
        command,
        cwd=FRONTEND_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    threading.Thread(target=stream_process_output, args=("vite", process), daemon=True).start()
    return process


def start_full_app(
    host: str = "127.0.0.1",
    api_port: int = 5000,
    ui_port: int = 5173,
    max_explanations: int = DEFAULT_MAX_EXPLANATIONS,
    max_tables: int = DEFAULT_MAX_TABLES_PER_SCAN,
    rows_per_table: int = DEFAULT_ROWS_PER_TABLE,
    detection_stage: str = DEFAULT_DETECTION_STAGE,
    payment_category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    open_browser: bool = True,
) -> None:
    ui_port = find_available_port(host, ui_port)
    api_url = f"http://{host}:{api_port}"
    ui_url = f"http://{host}:{ui_port}"
    print("[startup] Full app mode starting from ml_engine.py.", flush=True)
    print(f"[startup] Max explanations per scan: {max_explanations}", flush=True)
    print(f"[startup] Max tables per scan: {max_tables}", flush=True)
    print(f"[startup] Rows per table: {rows_per_table}", flush=True)
    print(f"[startup] Detection stage: {detection_stage}", flush=True)
    print(f"[startup] Dak list_date filter: {start_date or 'any'}..{end_date or 'any'}", flush=True)
    print(f"[startup] API URL: {api_url}", flush=True)
    print(f"[startup] UI URL: {ui_url}", flush=True)
    print("[startup] Browser will open once. Run scan from the UI button.", flush=True)

    engine = build_engine()
    llama_client = build_llama_client()
    init_alert_tables(engine)

    from api import create_api_server

    api_server = create_api_server(
        host=host,
        port=api_port,
        engine=engine,
        llama_client=llama_client,
        max_explanations=max_explanations,
        max_tables=max_tables,
        rows_per_table=rows_per_table,
        detection_stage=detection_stage,
        payment_category=payment_category,
        start_date=start_date,
        end_date=end_date,
    )
    api_thread = threading.Thread(target=api_server.serve_forever, daemon=True)
    api_thread.start()
    print("[api] API server is running in the background.", flush=True)

    ui_process = start_react_dev_server(host, ui_port, api_url)
    time.sleep(2)

    if ui_process is None:
        print(
            "[startup] Dashboard unavailable, but the API is live. "
            f"Hit it directly at {api_url}/api/health and POST {api_url}/api/run-scan.",
            flush=True,
        )
    elif open_browser:
        print(f"[ui] Opening browser once: {ui_url}", flush=True)
        webbrowser.open(ui_url, new=2)
    else:
        print("[ui] Browser auto-open disabled.", flush=True)

    print("[startup] App is ready. Use the browser Run scan button to start anomaly detection.", flush=True)
    print("[startup] If you only see 0 anomalies, that means no scan has stored rows yet.", flush=True)
    print("[startup] Press Ctrl+C here to stop services.", flush=True)
    try:
        while True:
            if ui_process is not None and ui_process.poll() is not None:
                print(
                    f"[ui] React dev server exited with code {ui_process.returncode}. "
                    "Keeping the API running.",
                    flush=True,
                )
                ui_process = None
            time.sleep(1)
    except KeyboardInterrupt:
        print("[shutdown] Ctrl+C received. Stopping services.", flush=True)
    finally:
        api_server.shutdown()
        if ui_process is not None:
            ui_process.terminate()
            try:
                ui_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                ui_process.kill()
        print("[shutdown] Services stopped.", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Tulip anomaly engine.")
    parser.add_argument(
        "payment",
        nargs="?",
        choices=["tpp", "gem", "up"],
        help="Start the full app for this payment type. Examples: python3 backend/ml_engine.py tpp|gem|up.",
    )
    parser.add_argument("--once", action="store_true", help="Run one scan and exit.")
    parser.add_argument("--api", action="store_true", help="Run only the localhost API server.")
    parser.add_argument("--monitor", action="store_true", help="Run only the terminal scanner loop.")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser in full app mode.")
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Seconds between scans in continuous mode.",
    )
    parser.add_argument(
        "--max-explanations",
        type=int,
        default=DEFAULT_MAX_EXPLANATIONS,
        help="Maximum LLM explanations to generate per scan.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="API host when using --api.")
    parser.add_argument("--port", type=int, default=5000, help="API port when using --api.")
    parser.add_argument("--ui-port", type=int, default=5173, help="React dev server port.")
    parser.add_argument(
        "--max-tables",
        type=int,
        default=DEFAULT_MAX_TABLES_PER_SCAN,
        help="Maximum schema-verified tables to scan per run.",
    )
    parser.add_argument(
        "--rows-per-table",
        type=int,
        default=DEFAULT_ROWS_PER_TABLE,
        help="Maximum recent rows to load from each table.",
    )
    parser.add_argument(
        "--detection-stage",
        choices=["isolation", "autoencoder"],
        default=DEFAULT_DETECTION_STAGE if DEFAULT_DETECTION_STAGE in {"isolation", "autoencoder"} else "isolation",
        help="Use isolation for first-pass anomalies, or autoencoder for second-pass confirmation.",
    )
    parser.add_argument(
        "--payment-category",
        choices=["tpp", "gem", "up", "THIRD_PARTY_PAYMENTS", "GEM_BILLS", "UNIT_PAYMENTS"],
        default=None,
        help="Scan only one payment type: tpp, gem, or up.",
    )
    parser.add_argument("--start-date", default=None, help="Dak list_date start date, YYYY-MM-DD.")
    parser.add_argument("--end-date", default=None, help="Dak list_date end date, YYYY-MM-DD.")
    args = parser.parse_args()
    if bool(args.start_date) != bool(args.end_date):
        parser.error("--start-date and --end-date must be provided together.")
    for value, label in ((args.start_date, "--start-date"), (args.end_date, "--end-date")):
        if value:
            try:
                dt.date.fromisoformat(value)
            except ValueError:
                parser.error(f"{label} must use YYYY-MM-DD.")
    return args


if __name__ == "__main__":
    args = parse_args()
    payment_category = args.payment or args.payment_category
    if args.once:
        start_continuous_monitoring(
            interval_seconds=args.interval,
            once=True,
            max_explanations=args.max_explanations,
            max_tables=args.max_tables,
            rows_per_table=args.rows_per_table,
            detection_stage=args.detection_stage,
            payment_category=payment_category,
            start_date=args.start_date,
            end_date=args.end_date,
        )
    elif args.api:
        from api import start_api_server

        start_api_server(
            host=args.host,
            port=args.port,
            max_explanations=args.max_explanations,
            max_tables=args.max_tables,
            rows_per_table=args.rows_per_table,
            detection_stage=args.detection_stage,
            payment_category=payment_category,
            start_date=args.start_date,
            end_date=args.end_date,
        )
    elif args.monitor:
        start_continuous_monitoring(
            interval_seconds=args.interval,
            once=False,
            max_explanations=args.max_explanations,
            max_tables=args.max_tables,
            rows_per_table=args.rows_per_table,
            detection_stage=args.detection_stage,
            payment_category=payment_category,
            start_date=args.start_date,
            end_date=args.end_date,
        )
    else:
        start_full_app(
            host=args.host,
            api_port=args.port,
            ui_port=args.ui_port,
            max_explanations=args.max_explanations,
            max_tables=args.max_tables,
            rows_per_table=args.rows_per_table,
            detection_stage=args.detection_stage,
            payment_category=payment_category,
            start_date=args.start_date,
            end_date=args.end_date,
            open_browser=not args.no_browser,
        )
