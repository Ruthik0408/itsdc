import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler

from db_config import get_sqlalchemy_url


BACKEND_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BACKEND_DIR / "outputs"
FEATURE_DICTIONARY_FILE = BACKEND_DIR / "gem_bill_feature_dictionary.json"
GEM_DAK_SECTION_IDS = (113, 127, 128, 129, 219, 348)
DEFAULT_AMOUNT_TOLERANCE = float(os.getenv("GEM_AMOUNT_TOLERANCE", "1"))
DEFAULT_CONTAMINATION = float(os.getenv("GEM_IFOREST_CONTAMINATION", "0.02"))
REVIEW_COLUMNS = {
    "gem_bill_id",
    "dak_id",
    "dakid_no",
    "transaction_id",
    "order_id",
    "supply_order_no",
    "crac_no",
    "invoice_no",
    "gem_invoice_no",
    "unit_id",
    "unit_code",
    "vendor_name",
    "vendor_pan",
    "bill_amount",
    "amount_passed",
    "amount_to_be_paid",
    "gem_bill_record_status",
    "dak_record_status",
    "approved",
    "payment_status",
    "reason",
    "failure_reason",
    "normalized_crac",
    "normalized_order_id",
    "normalized_supply_order_no",
    "dak_list_date",
    "bill_date",
    "final_bill_date",
    "approval_date",
    "pm_latest_date",
    "cheque_slip_latest_date",
    "schedule3_latest_date",
    "ecs_latest_date",
}
TEXT_EXCLUDE_TERMS = (
    "id",
    "no",
    "name",
    "reason",
    "status",
    "transaction",
    "order",
    "invoice",
    "crac",
    "pan",
    "code",
    "normalized",
)


@dataclass(frozen=True)
class Schema:
    columns_by_table: dict[str, set[str]]

    def has_table(self, table: str) -> bool:
        return table in self.columns_by_table

    def has_column(self, table: str, column: str) -> bool:
        return column in self.columns_by_table.get(table, set())


@dataclass(frozen=True)
class FeatureSpec:
    feature_name: str
    source_tables: tuple[str, ...]
    source_columns: tuple[str, ...]
    rule_description: str
    anomaly_meaning: str
    available: bool = True
    limitation: str | None = None


def build_engine():
    return create_engine(get_sqlalchemy_url(), pool_pre_ping=True)


def quote_identifier(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


def get_schema_columns(engine) -> Schema:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = 'public';
                """
            )
        )
        columns_by_table: dict[str, set[str]] = {}
        for row in rows:
            columns_by_table.setdefault(str(row.table_name), set()).add(str(row.column_name))
    return Schema(columns_by_table)


def qcol(alias: str, column: str) -> str:
    return f"{alias}.{quote_identifier(column)}"


def col(schema: Schema, table: str, alias: str, column: str, fallback: str = "NULL") -> str:
    if schema.has_column(table, column):
        return qcol(alias, column)
    return fallback


def text_col(schema: Schema, table: str, alias: str, column: str, fallback: str = "NULL") -> str:
    return f"{col(schema, table, alias, column, fallback)}::text"


def num_col(schema: Schema, table: str, alias: str, column: str, fallback: str = "NULL") -> str:
    return f"{col(schema, table, alias, column, fallback)}::double precision"


def bool_flag(condition: str) -> str:
    return f"CASE WHEN {condition} THEN 1 ELSE 0 END"


def missing_expr(expression: str) -> str:
    return f"({expression} IS NULL OR BTRIM({expression}::text) = '')"


def normalize_sql(expression: str, prefixes: Iterable[str] = ()) -> str:
    normalized = f"UPPER(REGEXP_REPLACE(COALESCE({expression}::text, ''), '[^A-Za-z0-9]+', '', 'g'))"
    for prefix in prefixes:
        clean_prefix = prefix.upper().replace("-", "")
        normalized = f"REGEXP_REPLACE({normalized}, '^{clean_prefix}', '')"
    return normalized


def timestamp_coalesce(schema: Schema, table: str, alias: str, columns: Iterable[str]) -> str:
    parts = [f"{qcol(alias, column)}::timestamp" for column in columns if schema.has_column(table, column)]
    if not parts:
        return "NULL::timestamp"
    return f"COALESCE({', '.join(parts)})"


def count_table_cte(schema: Schema, table: str, cte_name: str, valid_only: bool = False) -> str:
    if not schema.has_table(table) or not schema.has_column(table, "fk_dak"):
        return f"""
            {cte_name} AS (
                SELECT
                    NULL::bigint AS fk_dak,
                    0::bigint AS total_count,
                    0::bigint AS valid_count,
                    0::double precision AS amount_total,
                    NULL::timestamp AS latest_date,
                    0::bigint AS approved_count
                WHERE FALSE
            )
        """
    valid_condition = f"{qcol(table, 'record_status')} = 'V'" if schema.has_column(table, "record_status") else "TRUE"
    valid_filter = f"COUNT(*) FILTER (WHERE {valid_condition})" if valid_only else "COUNT(*)"
    amount_column = next(
        (column for column in ("amount", "schedule3_amount", "amount_passed", "bill_amount") if schema.has_column(table, column)),
        None,
    )
    amount_expression = num_col(schema, table, table, amount_column, "0") if amount_column else "0"
    date_column = next(
        (
            column
            for column in (
                "pm_date",
                "cheque_slip_date",
                "dp_sheet_date",
                "cmp_file_gen_date",
                "utr_date",
                "scroll_date",
                "created_at",
            )
            if schema.has_column(table, column)
        ),
        None,
    )
    latest_date_expression = f"MAX({qcol(table, date_column)}::timestamp)" if date_column else "NULL::timestamp"
    approved_count = (
        f"COUNT(*) FILTER (WHERE COALESCE({qcol(table, 'approved')}, FALSE))"
        if schema.has_column(table, "approved")
        else "0"
    )
    return f"""
        {cte_name} AS (
            SELECT
                {qcol(table, 'fk_dak')} AS fk_dak,
                COUNT(*)::bigint AS total_count,
                {valid_filter}::bigint AS valid_count,
                COALESCE(SUM({amount_expression}) FILTER (WHERE {valid_condition}), 0)::double precision AS amount_total,
                {latest_date_expression} AS latest_date,
                {approved_count}::bigint AS approved_count
            FROM {quote_identifier(table)}
            WHERE {qcol(table, 'fk_dak')} IS NOT NULL
            GROUP BY {qcol(table, 'fk_dak')}
        )
    """


def product_agg_cte(schema: Schema) -> str:
    if not schema.has_table("gem_product"):
        return """
            product_agg AS (
                SELECT
                    NULL::bigint AS fk_gem_bill,
                    NULL::text AS transaction_id,
                    0::bigint AS product_count,
                    0::double precision AS product_total_value,
                    0::double precision AS product_avg_unit_price,
                    0::double precision AS product_max_unit_price,
                    0::double precision AS product_max_accepted_quantity,
                    0::double precision AS product_freight_total,
                    0::double precision AS product_total_with_freight,
                    0::double precision AS product_gst_total,
                    0::integer AS is_service_bill_flag,
                    0::bigint AS missing_product_code_count,
                    0::bigint AS missing_code_head_count,
                    0::bigint AS invalid_code_head_length_count,
                    0::bigint AS rnd_code_head_missing_project_code_count
                WHERE FALSE
            )
        """
    gp = "gp"
    link_select = (
        f"{qcol(gp, 'fk_gem_bill')} AS fk_gem_bill"
        if schema.has_column("gem_product", "fk_gem_bill")
        else "NULL::bigint AS fk_gem_bill"
    )
    transaction_select = (
        f"{qcol(gp, 'transaction_id')}::text AS transaction_id"
        if schema.has_column("gem_product", "transaction_id")
        else "NULL::text AS transaction_id"
    )
    product_code_missing = (
        f"COUNT(*) FILTER (WHERE {missing_expr(qcol(gp, 'product_code'))})"
        if schema.has_column("gem_product", "product_code")
        else "0"
    )
    code_head_missing = (
        f"COUNT(*) FILTER (WHERE {missing_expr(qcol(gp, 'code_head'))})"
        if schema.has_column("gem_product", "code_head")
        else "0"
    )
    invalid_code_head = (
        f"COUNT(*) FILTER (WHERE NOT {missing_expr(qcol(gp, 'code_head'))} AND LENGTH(BTRIM({qcol(gp, 'code_head')}::text)) <> 10)"
        if schema.has_column("gem_product", "code_head")
        else "0"
    )
    service_bill = (
        f"MAX(CASE WHEN LOWER(COALESCE({qcol(gp, 'offering_type')}::text, '')) = 'services' THEN 1 ELSE 0 END)"
        if schema.has_column("gem_product", "offering_type")
        else "0"
    )
    rnd_missing_project = (
        f"COUNT(*) FILTER (WHERE {qcol(gp, 'code_head')}::text LIKE 'R%' AND {missing_expr(qcol(gp, 'project_code'))})"
        if schema.has_column("gem_product", "code_head") and schema.has_column("gem_product", "project_code")
        else "0"
    )
    group_columns = ["fk_gem_bill", "transaction_id"]
    return f"""
        product_agg AS (
            SELECT
                {link_select},
                {transaction_select},
                COUNT(*)::bigint AS product_count,
                COALESCE(SUM({num_col(schema, 'gem_product', gp, 'total_value', '0')}), 0)::double precision AS product_total_value,
                AVG(NULLIF({num_col(schema, 'gem_product', gp, 'unit_price', '0')}, 0))::double precision AS product_avg_unit_price,
                MAX({num_col(schema, 'gem_product', gp, 'unit_price', '0')})::double precision AS product_max_unit_price,
                MAX({num_col(schema, 'gem_product', gp, 'accepted_quantity', '0')})::double precision AS product_max_accepted_quantity,
                COALESCE(SUM({num_col(schema, 'gem_product', gp, 'frieght_charge', '0')}), 0)::double precision AS product_freight_total,
                COALESCE(SUM({num_col(schema, 'gem_product', gp, 'total_value', '0')} + {num_col(schema, 'gem_product', gp, 'frieght_charge', '0')}), 0)::double precision AS product_total_with_freight,
                COALESCE(SUM(
                    {num_col(schema, 'gem_product', gp, 'sgst', '0')} +
                    {num_col(schema, 'gem_product', gp, 'cgst', '0')} +
                    {num_col(schema, 'gem_product', gp, 'igst', '0')} +
                    {num_col(schema, 'gem_product', gp, 'utgst', '0')} +
                    {num_col(schema, 'gem_product', gp, 'cess', '0')} +
                    {num_col(schema, 'gem_product', gp, 'freight_sgst', '0')} +
                    {num_col(schema, 'gem_product', gp, 'freight_cgst', '0')} +
                    {num_col(schema, 'gem_product', gp, 'freight_igst', '0')} +
                    {num_col(schema, 'gem_product', gp, 'freight_utgst', '0')} +
                    {num_col(schema, 'gem_product', gp, 'freight_cess', '0')}
                ), 0)::double precision AS product_gst_total,
                {service_bill}::integer AS is_service_bill_flag,
                {product_code_missing}::bigint AS missing_product_code_count,
                {code_head_missing}::bigint AS missing_code_head_count,
                {invalid_code_head}::bigint AS invalid_code_head_length_count,
                {rnd_missing_project}::bigint AS rnd_code_head_missing_project_code_count
            FROM {quote_identifier('gem_product')} AS {gp}
            GROUP BY {", ".join(group_columns)}
        )
    """


def amount_agg_cte(schema: Schema, table: str, cte_name: str, amount_columns: tuple[str, ...]) -> str:
    if not schema.has_table(table) or not schema.has_column(table, "fk_dak"):
        return f"{cte_name} AS (SELECT NULL::bigint AS fk_dak, 0::double precision AS amount_total, 0::bigint AS row_count WHERE FALSE)"
    amount_parts = [num_col(schema, table, table, column, "0") for column in amount_columns if schema.has_column(table, column)]
    amount_expression = " + ".join(amount_parts) if amount_parts else "0"
    valid_condition = f"{qcol(table, 'record_status')} = 'V'" if schema.has_column(table, "record_status") else "TRUE"
    return f"""
        {cte_name} AS (
            SELECT
                {qcol(table, 'fk_dak')} AS fk_dak,
                COUNT(*) FILTER (WHERE {valid_condition})::bigint AS row_count,
                COALESCE(SUM(({amount_expression})::double precision) FILTER (WHERE {valid_condition}), 0)::double precision AS amount_total
            FROM {quote_identifier(table)}
            WHERE {qcol(table, 'fk_dak')} IS NOT NULL
            GROUP BY {qcol(table, 'fk_dak')}
        )
    """


def gst_tds_agg_cte(schema: Schema) -> str:
    if not schema.has_table("gst_tds") or not schema.has_column("gst_tds", "fk_dak"):
        return "gst_tds_agg AS (SELECT NULL::bigint AS fk_dak, 0::double precision AS gst_tds_total, 0::bigint AS gst_tds_missing_bill_amount_count, 0::bigint AS gst_tds_missing_type_count WHERE FALSE)"
    gt = "gst_tds"
    valid_condition = f"{qcol(gt, 'record_status')} = 'V'" if schema.has_column("gst_tds", "record_status") else "TRUE"
    missing_bill_amount = (
        f"COUNT(*) FILTER (WHERE {valid_condition} AND {missing_expr(qcol(gt, 'bill_amount'))})"
        if schema.has_column("gst_tds", "bill_amount")
        else "0"
    )
    missing_type = (
        f"COUNT(*) FILTER (WHERE {valid_condition} AND {missing_expr(qcol(gt, 'gst_type'))})"
        if schema.has_column("gst_tds", "gst_type")
        else "0"
    )
    return f"""
        gst_tds_agg AS (
            SELECT
                {qcol(gt, 'fk_dak')} AS fk_dak,
                COALESCE(SUM((
                    {num_col(schema, 'gst_tds', gt, 'tds_igst', '0')} +
                    {num_col(schema, 'gst_tds', gt, 'tds_cgst', '0')} +
                    {num_col(schema, 'gst_tds', gt, 'tds_sgst', '0')} +
                    {num_col(schema, 'gst_tds', gt, 'tds_utgst', '0')}
                )::double precision) FILTER (WHERE {valid_condition}), 0)::double precision AS gst_tds_total,
                {missing_bill_amount}::bigint AS gst_tds_missing_bill_amount_count,
                {missing_type}::bigint AS gst_tds_missing_type_count
            FROM {quote_identifier('gst_tds')} AS {gt}
            WHERE {qcol(gt, 'fk_dak')} IS NOT NULL
            GROUP BY {qcol(gt, 'fk_dak')}
        )
    """


def ch_booking_agg_cte(schema: Schema) -> str:
    if not schema.has_table("ch_booking") or not schema.has_column("ch_booking", "fk_dak"):
        return "ch_booking_agg AS (SELECT NULL::bigint AS fk_dak, 0::bigint AS chbooking_valid_count, 0::double precision AS chbooking_amount_total WHERE FALSE)"
    cb = "ch_booking"
    valid_condition = f"{qcol(cb, 'record_status')} = 'V'" if schema.has_column("ch_booking", "record_status") else "TRUE"
    amount_column = "amount" if schema.has_column("ch_booking", "amount") else None
    amount_expression = num_col(schema, "ch_booking", cb, amount_column, "0") if amount_column else "0"
    return f"""
        ch_booking_agg AS (
            SELECT
                {qcol(cb, 'fk_dak')} AS fk_dak,
                COUNT(*) FILTER (WHERE {valid_condition})::bigint AS chbooking_valid_count,
                COALESCE(SUM({amount_expression}) FILTER (WHERE {valid_condition}), 0)::double precision AS chbooking_amount_total
            FROM {quote_identifier('ch_booking')} AS {cb}
            WHERE {qcol(cb, 'fk_dak')} IS NOT NULL
            GROUP BY {qcol(cb, 'fk_dak')}
        )
    """


def duplicate_agg_cte(schema: Schema) -> str:
    gb = "gbd"
    transaction = text_col(schema, "gem_bill", gb, "transaction_id")
    gem_invoice = normalize_sql(text_col(schema, "gem_bill", gb, "gem_invoice_no"), ("GEM-",))
    invoice = normalize_sql(text_col(schema, "gem_bill", gb, "invoice_no"), ("GEM-",))
    crac = normalize_sql(text_col(schema, "gem_bill", gb, "crac_no"), ("GEMCRAC-", "GEMC-"))
    order_id = normalize_sql(text_col(schema, "gem_bill", gb, "order_id"), ("GEMC-", "GEMD-"))
    supply_order = normalize_sql(text_col(schema, "gem_bill", gb, "supply_order_no"), ("GEMC-", "GEMD-"))
    record_filter = f"COALESCE({qcol(gb, 'record_status')}::text, '') <> 'R'" if schema.has_column("gem_bill", "record_status") else "TRUE"
    return f"""
        duplicate_base AS (
            SELECT
                {qcol(gb, 'id')} AS gem_bill_id,
                NULLIF({transaction}, '') AS transaction_id_key,
                NULLIF({gem_invoice}, '') AS gem_invoice_key,
                NULLIF({invoice}, '') AS invoice_key,
                NULLIF({crac}, '') AS crac_key,
                NULLIF({order_id}, '') AS order_key,
                NULLIF({supply_order}, '') AS supply_order_key
            FROM {quote_identifier('gem_bill')} AS {gb}
            WHERE {record_filter}
        ),
        duplicate_agg AS (
            SELECT
                gem_bill_id,
                CASE WHEN transaction_id_key IS NULL THEN 0 ELSE COUNT(*) OVER (PARTITION BY transaction_id_key) END AS transaction_id_count,
                CASE WHEN gem_invoice_key IS NULL THEN 0 ELSE COUNT(*) OVER (PARTITION BY gem_invoice_key) END AS gem_invoice_count,
                CASE WHEN invoice_key IS NULL THEN 0 ELSE COUNT(*) OVER (PARTITION BY invoice_key) END AS invoice_count,
                CASE WHEN crac_key IS NULL THEN 0 ELSE COUNT(*) OVER (PARTITION BY crac_key) END AS crac_count,
                CASE WHEN order_key IS NULL THEN 0 ELSE COUNT(*) OVER (PARTITION BY order_key) END AS order_count,
                CASE WHEN supply_order_key IS NULL THEN 0 ELSE COUNT(*) OVER (PARTITION BY supply_order_key) END AS supply_order_count
            FROM duplicate_base
        )
    """


def advanced_pattern_ctes(schema: Schema) -> str:
    gb = "gba"
    vendor_bank_expr = normalize_sql(
        f"COALESCE({text_col(schema, 'gem_bill', gb, 'vendor_enc_bank_account')}, "
        f"{text_col(schema, 'gem_bill', gb, 'vendor_bank_account_no')}, "
        f"{text_col(schema, 'gem_bill', gb, 'vendor_bank_account')})"
    )
    vendor_pan_expr = normalize_sql(text_col(schema, "gem_bill", gb, "vendor_pan"))
    unit_expr = col(schema, "gem_bill", gb, "fk_unit")
    bill_amount = num_col(schema, "gem_bill", gb, "bill_amount", "0")
    crac_key = normalize_sql(text_col(schema, "gem_bill", gb, "crac_no"), ("GEMCRAC-", "GEMC-"))
    invoice_key = normalize_sql(text_col(schema, "gem_bill", gb, "invoice_no"), ("GEM-",))
    order_key = normalize_sql(text_col(schema, "gem_bill", gb, "order_id"), ("GEMC-", "GEMD-"))
    transaction_key = normalize_sql(text_col(schema, "gem_bill", gb, "transaction_id"))
    utr_key = normalize_sql(text_col(schema, "gem_bill", gb, "utr_no"))
    payment_ref_key = normalize_sql(text_col(schema, "gem_bill", gb, "payment_reference_no"))
    record_status = text_col(schema, "gem_bill", gb, "record_status")
    approved_expr = f"COALESCE({qcol(gb, 'approved')}, FALSE)" if schema.has_column("gem_bill", "approved") else "FALSE"
    dak_section_join = (
        f"LEFT JOIN {quote_identifier('dak')} AS da ON {qcol(gb, 'fk_dak')} = da.{quote_identifier('id')}"
        if schema.has_table("dak") and schema.has_column("gem_bill", "fk_dak")
        else ""
    )
    section_filter = ", ".join(str(section_id) for section_id in GEM_DAK_SECTION_IDS)
    dak_section_where = (
        f"da.{quote_identifier('fk_section')} IN ({section_filter})"
        if schema.has_table("dak") and schema.has_column("dak", "fk_section")
        else "TRUE"
    )
    return f"""
        advanced_bill_base AS (
            SELECT
                {qcol(gb, 'id')} AS gem_bill_id,
                {col(schema, 'gem_bill', gb, 'fk_dak')} AS dak_id,
                NULLIF({vendor_bank_expr}, '') AS vendor_bank_key,
                NULLIF({vendor_pan_expr}, '') AS vendor_pan_key,
                {unit_expr} AS unit_id,
                ROUND(COALESCE({bill_amount}, 0)::numeric, 0) AS rounded_bill_amount,
                COALESCE({bill_amount}, 0)::double precision AS bill_amount,
                NULLIF(COALESCE(NULLIF({crac_key}, ''), NULLIF({invoice_key}, ''), NULLIF({order_key}, ''), NULLIF({transaction_key}, '')), '') AS reprocess_key,
                NULLIF({utr_key}, '') AS utr_key,
                NULLIF({payment_ref_key}, '') AS payment_reference_key,
                UPPER(COALESCE({record_status}, '')) AS record_status,
                {approved_expr} AS approved
            FROM {quote_identifier('gem_bill')} AS {gb}
            {dak_section_join}
            WHERE {dak_section_where}
        ),
        vendor_bank_stats AS (
            SELECT vendor_bank_key, COUNT(DISTINCT vendor_pan_key)::bigint AS bank_vendor_count
            FROM advanced_bill_base
            WHERE vendor_bank_key IS NOT NULL AND vendor_pan_key IS NOT NULL
            GROUP BY vendor_bank_key
        ),
        vendor_pan_bank_stats AS (
            SELECT vendor_pan_key, COUNT(DISTINCT vendor_bank_key)::bigint AS vendor_bank_count
            FROM advanced_bill_base
            WHERE vendor_bank_key IS NOT NULL AND vendor_pan_key IS NOT NULL
            GROUP BY vendor_pan_key
        ),
        repeated_amount_stats AS (
            SELECT vendor_pan_key, unit_id, rounded_bill_amount, COUNT(*)::bigint AS repeated_amount_count
            FROM advanced_bill_base
            WHERE vendor_pan_key IS NOT NULL AND unit_id IS NOT NULL AND rounded_bill_amount > 0
            GROUP BY vendor_pan_key, unit_id, rounded_bill_amount
        ),
        reprocess_stats AS (
            SELECT
                reprocess_key,
                vendor_pan_key,
                COUNT(*)::bigint AS same_document_attempt_count,
                COUNT(*) FILTER (WHERE record_status = 'R')::bigint AS rejected_attempt_count,
                COUNT(*) FILTER (WHERE record_status = 'V' OR approved)::bigint AS valid_or_approved_attempt_count
            FROM advanced_bill_base
            WHERE reprocess_key IS NOT NULL
            GROUP BY reprocess_key, vendor_pan_key
        ),
        payment_reference_stats AS (
            SELECT
                gem_bill_id,
                CASE WHEN utr_key IS NULL THEN 0 ELSE COUNT(*) OVER (PARTITION BY utr_key) END::bigint AS duplicate_utr_count,
                CASE WHEN payment_reference_key IS NULL THEN 0 ELSE COUNT(*) OVER (PARTITION BY payment_reference_key) END::bigint AS duplicate_payment_reference_count
            FROM advanced_bill_base
        ),
        unit_behavior_stats AS (
            SELECT
                unit_id,
                COUNT(*)::bigint AS unit_bill_count,
                AVG(bill_amount)::double precision AS unit_avg_bill_amount,
                COALESCE(STDDEV_SAMP(bill_amount), 0)::double precision AS unit_std_bill_amount
            FROM advanced_bill_base
            WHERE unit_id IS NOT NULL
            GROUP BY unit_id
        ),
        vendor_behavior_stats AS (
            SELECT
                vendor_pan_key,
                COUNT(*)::bigint AS vendor_bill_count,
                COUNT(DISTINCT unit_id)::bigint AS vendor_distinct_unit_count,
                AVG(bill_amount)::double precision AS vendor_avg_bill_amount,
                COALESCE(STDDEV_SAMP(bill_amount), 0)::double precision AS vendor_std_bill_amount
            FROM advanced_bill_base
            WHERE vendor_pan_key IS NOT NULL
            GROUP BY vendor_pan_key
        )
    """


def build_base_query(schema: Schema, amount_tolerance: float = DEFAULT_AMOUNT_TOLERANCE) -> str:
    gb = "gb"
    d = "d"
    dak_join = (
        f"LEFT JOIN {quote_identifier('dak')} AS {d} ON {qcol(gb, 'fk_dak')} = {qcol(d, 'id')}"
        if schema.has_table("dak") and schema.has_column("gem_bill", "fk_dak")
        else ""
    )
    product_join = (
        "LEFT JOIN product_agg pa ON "
        f"(pa.fk_gem_bill = {qcol(gb, 'id')} OR (pa.fk_gem_bill IS NULL AND pa.transaction_id = {text_col(schema, 'gem_bill', gb, 'transaction_id')}))"
    )
    section_filter = ", ".join(str(section_id) for section_id in GEM_DAK_SECTION_IDS)
    dak_section_where = (
        f"{qcol(d, 'fk_section')} IN ({section_filter})"
        if schema.has_table("dak") and schema.has_column("dak", "fk_section")
        else "TRUE"
    )
    date_filter = (
        f"AND {qcol(d, 'list_date')} BETWEEN :start_date AND :end_date"
        if schema.has_column("dak", "list_date")
        else ""
    )
    normalized_crac = normalize_sql(text_col(schema, "gem_bill", gb, "crac_no"), ("GEMCRAC-", "GEMC-"))
    normalized_order = normalize_sql(text_col(schema, "gem_bill", gb, "order_id"), ("GEMC-", "GEMD-"))
    normalized_supply = normalize_sql(text_col(schema, "gem_bill", gb, "supply_order_no"), ("GEMC-", "GEMD-"))
    bill_amount = num_col(schema, "gem_bill", gb, "bill_amount", "0")
    amount_passed = num_col(schema, "gem_bill", gb, "amount_passed", "0")
    amount_to_be_paid = num_col(schema, "gem_bill", gb, "amount_to_be_paid", "0")
    ld_amount = num_col(schema, "gem_bill", gb, "ld_amount", "0")
    disallowance_total = "COALESCE(dis.amount_total, 0)"
    recovery_total = "COALESCE(rec.amount_total, 0)"
    gst_tds_total = "COALESCE(gst.gst_tds_total, 0)"
    product_total = "COALESCE(pa.product_total_with_freight, 0)"
    expected_amount_passed = f"({product_total} - {disallowance_total})"
    expected_amount_to_be_paid = f"({amount_passed} - {disallowance_total} - {recovery_total} - {ld_amount})"
    valid_bill = f"{qcol(gb, 'record_status')} = 'V'" if schema.has_column("gem_bill", "record_status") else "FALSE"
    rejected_bill = f"{qcol(gb, 'record_status')} = 'R'" if schema.has_column("gem_bill", "record_status") else "FALSE"
    invalid_bill = f"{qcol(gb, 'record_status')} = 'I'" if schema.has_column("gem_bill", "record_status") else "FALSE"
    approved = f"COALESCE({qcol(gb, 'approved')}, FALSE)" if schema.has_column("gem_bill", "approved") else "FALSE"
    dak_rejected_condition = f"{qcol(d, 'record_status')} = 'R'" if schema.has_column("dak", "record_status") else "FALSE"
    dak_not_starting_with_g_condition = (
        f"{qcol(d, 'dakid_no')} IS NULL OR {qcol(d, 'dakid_no')}::text NOT LIKE 'G%'"
        if schema.has_column("dak", "dakid_no")
        else "TRUE"
    )
    rejection_dak_mismatch_condition = (
        f"{rejected_bill} AND {approved} AND NOT ({dak_rejected_condition})"
        if schema.has_column("dak", "record_status")
        else "FALSE"
    )
    ch_count = "COALESCE(ch.chbooking_valid_count, 0)"
    cs_count = "COALESCE(cs.valid_count, 0)"
    pm_count = "COALESCE(pm.valid_count, 0)"
    schedule_count = "COALESCE(s3.valid_count, 0)"
    ecs_count = "COALESCE(ecs.valid_count, 0)"
    product_count = "COALESCE(pa.product_count, 0)"
    order_amount = num_col(schema, "gem_bill", gb, "order_amount", "0")
    same_order_total = f"SUM({bill_amount}) OVER (PARTITION BY NULLIF({normalized_order}, ''))"
    dak_list_date = f"{qcol(d, 'list_date')}::timestamp" if schema.has_column("dak", "list_date") else "NULL::timestamp"
    bill_date = f"{qcol(gb, 'bill_date')}::timestamp" if schema.has_column("gem_bill", "bill_date") else "NULL::timestamp"
    final_bill_date = f"{qcol(gb, 'final_bill_date')}::timestamp" if schema.has_column("gem_bill", "final_bill_date") else "NULL::timestamp"
    approval_date = timestamp_coalesce(schema, "gem_bill", gb, ("go_date", "ao_date", "aao_date", "auditor_date", "updated_at"))
    vendor_bank_key = normalize_sql(
        f"COALESCE({text_col(schema, 'gem_bill', gb, 'vendor_enc_bank_account')}, "
        f"{text_col(schema, 'gem_bill', gb, 'vendor_bank_account_no')}, "
        f"{text_col(schema, 'gem_bill', gb, 'vendor_bank_account')})"
    )
    vendor_pan_key = normalize_sql(text_col(schema, "gem_bill", gb, "vendor_pan"))

    return f"""
        SELECT
            {qcol(gb, 'id')} AS gem_bill_id,
            {col(schema, 'gem_bill', gb, 'fk_dak')} AS dak_id,
            {text_col(schema, 'dak', d, 'dakid_no')} AS dakid_no,
            {text_col(schema, 'gem_bill', gb, 'transaction_id')} AS transaction_id,
            {text_col(schema, 'gem_bill', gb, 'order_id')} AS order_id,
            {text_col(schema, 'gem_bill', gb, 'supply_order_no')} AS supply_order_no,
            {text_col(schema, 'gem_bill', gb, 'crac_no')} AS crac_no,
            {text_col(schema, 'gem_bill', gb, 'invoice_no')} AS invoice_no,
            {text_col(schema, 'gem_bill', gb, 'gem_invoice_no')} AS gem_invoice_no,
            {col(schema, 'gem_bill', gb, 'fk_unit')} AS unit_id,
            {text_col(schema, 'gem_bill', gb, 'unit_code')} AS unit_code,
            {text_col(schema, 'gem_bill', gb, 'vendor_name')} AS vendor_name,
            {text_col(schema, 'gem_bill', gb, 'vendor_pan')} AS vendor_pan,
            {bill_amount} AS bill_amount,
            {amount_passed} AS amount_passed,
            {amount_to_be_paid} AS amount_to_be_paid,
            {text_col(schema, 'gem_bill', gb, 'record_status')} AS gem_bill_record_status,
            {text_col(schema, 'dak', d, 'record_status')} AS dak_record_status,
            {col(schema, 'gem_bill', gb, 'approved', 'FALSE')} AS approved,
            {text_col(schema, 'gem_bill', gb, 'payment_status')} AS payment_status,
            {text_col(schema, 'gem_bill', gb, 'reason')} AS reason,
            {text_col(schema, 'gem_bill', gb, 'failure_reason')} AS failure_reason,
            NULLIF({normalized_crac}, '') AS normalized_crac,
            NULLIF({normalized_order}, '') AS normalized_order_id,
            NULLIF({normalized_supply}, '') AS normalized_supply_order_no,
            {dak_list_date} AS dak_list_date,
            {bill_date} AS bill_date,
            {final_bill_date} AS final_bill_date,
            {approval_date} AS approval_date,
            pm.latest_date AS pm_latest_date,
            cs.latest_date AS cheque_slip_latest_date,
            s3.latest_date AS schedule3_latest_date,
            ecs.latest_date AS ecs_latest_date,

            1 AS has_gem_bill,
            {bool_flag(f'{qcol(d, "id")} IS NOT NULL' if schema.has_table('dak') else 'FALSE')} AS has_dak,
            {bool_flag(f'{product_count} > 0')} AS has_gem_product,
            {bool_flag(f'{ch_count} > 0')} AS has_ch_booking,
            {bool_flag(f'{cs_count} > 0')} AS has_cheque_slip,
            {bool_flag(f'{pm_count} > 0')} AS has_punching_medium,
            {bool_flag(f'{schedule_count} > 0')} AS has_schedule3,
            {bool_flag(f'{ecs_count} > 0')} AS has_ecs,
            {bool_flag(f'{qcol(d, "id")} IS NULL' if schema.has_table('dak') else 'TRUE')} AS gem_bill_without_dak_flag,
            0 AS gem_product_without_gem_bill_flag,
            {bool_flag(f'{cs_count} > 0 AND {qcol(gb, "id")} IS NULL')} AS cheque_slip_without_gem_bill_flag,
            {bool_flag(f'{pm_count} > 0 AND {cs_count} = 0')} AS punching_medium_without_cheque_slip_flag,
            {bool_flag(f'{schedule_count} > 0 AND {pm_count} = 0')} AS schedule3_without_punching_medium_flag,
            {bool_flag(f'{ecs_count} > 0 AND {schedule_count} = 0')} AS ecs_without_schedule3_flag,
            {bool_flag(f'{ecs_count} > 0 AND {cs_count} = 0')} AS ecs_without_cheque_slip_flag,
            {bool_flag(f'{ecs_count} > 0 AND {pm_count} = 0')} AS ecs_without_punching_medium_flag,

            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'fk_unit')))} AS missing_unit_flag,
            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'msme')))} AS missing_msme_flag,
            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'make_type')))} AS missing_make_type_flag,
            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'fk_dak')))} AS missing_dak_flag,
            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'transaction_id')))} AS missing_transaction_id_flag,
            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'crac_no')))} AS missing_crac_flag,
            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'order_id')))} AS missing_order_id_flag,
            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'supply_order_no')))} AS missing_supply_order_no_flag,
            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'final_bill_date')))} AS missing_final_bill_date_flag,
            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'vendor_name')))} AS missing_vendor_name_flag,
            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'vendor_enc_bank_account')))} AS missing_vendor_bank_account_flag,
            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'vendor_enc_bank_ifsc')))} AS missing_vendor_ifsc_flag,
            {bool_flag(f'{product_count} = 0')} AS missing_product_details_flag,
            {bool_flag(f'COALESCE(pa.missing_product_code_count, 0) > 0')} AS missing_product_code_flag,
            {bool_flag(f'COALESCE(pa.missing_code_head_count, 0) > 0')} AS missing_code_head_flag,
            {bool_flag(f'{bill_amount} IS NULL OR {bill_amount} <= 0')} AS missing_bill_amount_flag,

            {bool_flag(f'{qcol(d, "id")} IS NULL' if schema.has_table('dak') else 'TRUE')} AS dak_missing_flag,
            {bool_flag(dak_not_starting_with_g_condition)} AS dak_not_starting_with_g_flag,
            0 AS dak_type_not_gem_flag,
            {bool_flag('COALESCE(dup.transaction_id_count, 0) > 1')} AS duplicate_transaction_id_flag,
            {bool_flag('COALESCE(dup.gem_invoice_count, 0) > 1')} AS duplicate_gem_invoice_flag,
            {bool_flag('COALESCE(dup.crac_count, 0) > 1')} AS duplicate_crac_flag,
            {bool_flag('COALESCE(dup.order_count, 0) > 1 AND COALESCE(dup.crac_count, 0) > 1')} AS duplicate_order_same_crac_flag,
            {bool_flag('COALESCE(dup.supply_order_count, 0) > 1')} AS duplicate_supply_order_flag,

            {bool_flag(f"NULLIF({normalized_crac}, '') IS NOT NULL AND NULLIF({normalized_order}, '') IS NOT NULL AND POSITION(NULLIF({normalized_order}, '') IN NULLIF({normalized_crac}, '')) = 0")} AS crac_order_mismatch_flag,
            {bool_flag(f"NULLIF({normalized_crac}, '') IS NOT NULL AND NULLIF({normalized_supply}, '') IS NOT NULL AND POSITION(NULLIF({normalized_supply}, '') IN NULLIF({normalized_crac}, '')) = 0")} AS crac_supply_order_mismatch_flag,
            {same_order_total}::double precision AS same_order_total_bill_amount,
            {order_amount} AS order_amount,
            GREATEST(COALESCE({same_order_total}, 0) - CEIL(COALESCE({order_amount}, 0)), 0)::double precision AS order_overpayment_amount,
            CASE WHEN COALESCE({order_amount}, 0) > 0 THEN GREATEST(COALESCE({same_order_total}, 0) - CEIL(COALESCE({order_amount}, 0)), 0) / {order_amount} ELSE 0 END AS order_overpayment_ratio,
            {bool_flag(f'COALESCE({same_order_total}, 0) > CEIL(COALESCE({order_amount}, 0)) AND COALESCE({order_amount}, 0) > 0')} AS paid_amount_exceeds_order_amount_flag,

            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'final_bill_date')))} AS final_bill_date_missing_flag,
            0 AS office_gem_start_date_missing_flag,
            0 AS final_bill_before_gem_start_date_flag,
            {bool_flag(f"{qcol(gb, 'bill_date')} > {qcol(gb, 'final_bill_date')}" if schema.has_column('gem_bill', 'bill_date') and schema.has_column('gem_bill', 'final_bill_date') else 'FALSE')} AS bill_date_after_final_date_flag,
            {bool_flag(f"({qcol(gb, 'bill_date')} > CURRENT_DATE OR {qcol(gb, 'invoice_date')} > CURRENT_DATE OR {qcol(gb, 'final_bill_date')} > CURRENT_DATE)" if schema.has_column('gem_bill', 'bill_date') and schema.has_column('gem_bill', 'invoice_date') and schema.has_column('gem_bill', 'final_bill_date') else 'FALSE')} AS suspicious_future_date_flag,

            {bool_flag(f"LENGTH(COALESCE({text_col(schema, 'gem_bill', gb, 'vendor_enc_bank_ifsc')}, {text_col(schema, 'gem_bill', gb, 'vendor_bank_ifsc_code')})) NOT IN (0, 11)")} AS invalid_ifsc_length_flag,
            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'vendor_pan')))} AS vendor_pan_missing_flag,
            {bool_flag(missing_expr(col(schema, 'gem_bill', gb, 'vendor_gstn')))} AS vendor_gstin_missing_flag,
            {bool_flag(f'{gst_tds_total} > 0 AND {missing_expr(col(schema, "gem_bill", gb, "vendor_gstn"))}')} AS gst_tds_applied_but_vendor_gstin_missing_flag,

            {product_count} AS product_count,
            COALESCE(pa.product_total_value, 0)::double precision AS product_total_value,
            COALESCE(pa.product_avg_unit_price, 0)::double precision AS product_avg_unit_price,
            COALESCE(pa.product_max_unit_price, 0)::double precision AS product_max_unit_price,
            COALESCE(pa.product_max_accepted_quantity, 0)::double precision AS product_max_accepted_quantity,
            COALESCE(pa.product_freight_total, 0)::double precision AS product_freight_total,
            {product_total}::double precision AS product_total_with_freight,
            COALESCE(pa.product_gst_total, 0)::double precision AS product_gst_total,
            COALESCE(pa.is_service_bill_flag, 0)::integer AS is_service_bill_flag,
            COALESCE(pa.missing_product_code_count, 0)::bigint AS missing_product_code_count,
            COALESCE(pa.missing_code_head_count, 0)::bigint AS missing_code_head_count,
            COALESCE(pa.invalid_code_head_length_count, 0)::bigint AS invalid_code_head_length_count,
            COALESCE(pa.rnd_code_head_missing_project_code_count, 0)::bigint AS rnd_code_head_missing_project_code_count,
            ({bill_amount} - ({product_total} - {ld_amount}))::double precision AS bill_product_total_diff,
            ABS({bill_amount} - ({product_total} - {ld_amount}))::double precision AS bill_product_total_abs_diff,
            {bool_flag(f'ABS({bill_amount} - ({product_total} - {ld_amount})) > {amount_tolerance}')} AS product_total_bill_amount_mismatch_flag,

            {ch_count} AS chbooking_valid_count,
            {bool_flag(f'{ch_count} = 0')} AS chbooking_missing_flag,
            COALESCE(ch.chbooking_amount_total, 0)::double precision AS chbooking_amount_total,
            ({bill_amount} - COALESCE(ch.chbooking_amount_total, 0))::double precision AS chbooking_bill_amount_diff,
            {bool_flag(f'ABS({bill_amount} - COALESCE(ch.chbooking_amount_total, 0)) > {amount_tolerance}')} AS chbooking_amount_mismatch_flag,
            {bool_flag(f'{valid_bill} AND {ch_count} = 0')} AS fund_verification_failed_flag,

            {disallowance_total}::double precision AS disallowance_total,
            {recovery_total}::double precision AS recovery_total,
            {gst_tds_total}::double precision AS gst_tds_total,
            {bool_flag('COALESCE(gst.gst_tds_missing_bill_amount_count, 0) > 0')} AS gst_tds_missing_bill_amount_flag,
            {bool_flag('COALESCE(gst.gst_tds_missing_type_count, 0) > 0')} AS gst_tds_missing_type_flag,
            {bool_flag(f'{gst_tds_total} > 0 AND ({missing_expr(col(schema, "gem_bill", gb, "vendor_gstn"))} OR COALESCE(gst.gst_tds_missing_bill_amount_count, 0) > 0 OR COALESCE(gst.gst_tds_missing_type_count, 0) > 0)')} AS gst_tds_invalid_flag,
            {ld_amount} AS ld_amount,
            {expected_amount_passed}::double precision AS expected_amount_passed,
            {bool_flag(f'ABS({amount_passed} - ({expected_amount_passed})) > {amount_tolerance}')} AS amount_passed_mismatch_flag,
            {expected_amount_to_be_paid}::double precision AS expected_amount_to_be_paid,
            {bool_flag(f'ABS({amount_to_be_paid} - ({expected_amount_to_be_paid})) > {amount_tolerance}')} AS amount_to_be_paid_mismatch_flag,
            {bool_flag(f'{amount_to_be_paid} < 0')} AS negative_amount_to_be_paid_flag,
            ({disallowance_total} + {recovery_total} + {gst_tds_total})::double precision AS deduction_recovery_total,

            {pm_count} AS pm_valid_count,
            {cs_count} AS cheque_slip_valid_count,
            COALESCE(pm.total_count, 0)::bigint AS pm_total_count,
            COALESCE(cs.total_count, 0)::bigint AS cheque_slip_total_count,
            COALESCE(s3.total_count, 0)::bigint AS schedule3_total_count,
            COALESCE(ecs.total_count, 0)::bigint AS ecs_total_count,
            COALESCE(pm.amount_total, 0)::double precision AS pm_amount_total,
            COALESCE(cs.amount_total, 0)::double precision AS cheque_slip_amount_total,
            COALESCE(s3.amount_total, 0)::double precision AS schedule3_amount_total,
            COALESCE(ecs.amount_total, 0)::double precision AS ecs_amount_total,
            COALESCE(pm.approved_count, 0)::bigint AS pm_approved_count,
            COALESCE(cs.approved_count, 0)::bigint AS cheque_slip_approved_count,
            {bool_flag(f'{pm_count} > 0')} AS pm_generated_flag,
            {bool_flag(f'{cs_count} > 0')} AS cheque_slip_generated_flag,
            {bool_flag(f'{pm_count} > 0 AND NOT ({valid_bill})')} AS pm_generated_without_valid_bill_flag,
            {bool_flag(f'{cs_count} > 0 AND NOT ({valid_bill})')} AS cheque_slip_generated_without_valid_bill_flag,
            {bool_flag(f'{pm_count} > 0 AND {cs_count} = 0')} AS pm_without_cheque_slip_flag,
            {bool_flag(f'{cs_count} > 0 AND {pm_count} = 0')} AS cheque_slip_without_pm_flag,
            {bool_flag(f'{cs_count} > 0 AND NOT ({approved})')} AS approved_cheque_slip_without_bill_approval_flag,
            {bool_flag(f'{pm_count} > 0 AND NOT ({approved})')} AS approved_pm_without_bill_approval_flag,
            {bool_flag(f"LOWER(COALESCE({text_col(schema, 'gem_bill', gb, 'reason')}, '')) LIKE '%pm not tallied%'")} AS pm_not_tallied_reason_flag,
            {bool_flag(f'{pm_count} > 0 AND {rejected_bill}')} AS pm_generated_after_rejection_flag,

            {bool_flag(f'{schedule_count} > 0')} AS schedule3_exists_flag,
            {bool_flag(f'{ecs_count} > 0')} AS ecs_exists_flag,
            {bool_flag(f'{schedule_count} > 0 AND {pm_count} = 0')} AS schedule3_without_pm_flag,
            {bool_flag(f'{approved} AND {ecs_count} = 0')} AS approved_bill_without_ecs_flag,
            {bool_flag(f'{ecs_count} > 0 AND {invalid_bill}')} AS ecs_exists_for_invalid_bill_flag,
            {bool_flag(f'{ecs_count} > 0 AND {rejected_bill}')} AS ecs_exists_for_rejected_bill_flag,
            {bool_flag(f'{approved} AND {ecs_count} = 0')} AS approved_but_payment_not_completed_flag,
            {bool_flag(f'{product_count} > 0 AND {cs_count} > 0 AND {pm_count} > 0 AND {schedule_count} > 0 AND {ecs_count} > 0')} AS payment_completed_flow_flag,

            {bool_flag(f'{rejected_bill}')} AS rejection_started_flag,
            {bool_flag(f'{rejected_bill} AND {approved}')} AS rejection_final_approved_flag,
            {bool_flag(f'{rejected_bill} AND {missing_expr(col(schema, "gem_bill", gb, "reason"))}')} AS rejection_reason_missing_flag,
            {bool_flag(dak_rejected_condition)} AS dak_rejected_flag,
            {bool_flag(f"UPPER(COALESCE({text_col(schema, 'gem_bill', gb, 'payment_status')}, '')) = 'FAILURE'")} AS payment_failure_flag,
            {bool_flag(f'{rejected_bill} AND {schedule_count} > 0')} AS rejected_bill_has_schedule3_flag,
            {bool_flag(f'{rejected_bill} AND {pm_count} > 0')} AS rejected_bill_has_approved_pm_flag,
            {bool_flag(rejection_dak_mismatch_condition)} AS record_status_r_but_dak_not_r_after_approval_flag,
            {bool_flag(f"{rejected_bill} AND {approved} AND UPPER(COALESCE({text_col(schema, 'gem_bill', gb, 'payment_status')}, '')) <> 'FAILURE'")} AS rejection_approved_but_payment_status_not_failure_flag,

            COALESCE(vbs.bank_vendor_count, 0)::bigint AS same_bank_account_vendor_count,
            COALESCE(vpbs.vendor_bank_count, 0)::bigint AS same_vendor_bank_account_count,
            {bool_flag('COALESCE(vbs.bank_vendor_count, 0) > 1')} AS same_bank_account_multiple_vendors_flag,
            {bool_flag('COALESCE(vpbs.vendor_bank_count, 0) > 1')} AS same_vendor_multiple_bank_accounts_flag,
            COALESCE(ras.repeated_amount_count, 0)::bigint AS repeated_vendor_unit_amount_count,
            COALESCE(rs.same_document_attempt_count, 0)::bigint AS same_document_attempt_count,
            COALESCE(rs.rejected_attempt_count, 0)::bigint AS rejected_attempt_count,
            COALESCE(rs.valid_or_approved_attempt_count, 0)::bigint AS valid_or_approved_attempt_count,
            COALESCE(prs.duplicate_utr_count, 0)::bigint AS duplicate_utr_count,
            COALESCE(prs.duplicate_payment_reference_count, 0)::bigint AS duplicate_payment_reference_count,
            COALESCE(ubs.unit_bill_count, 0)::bigint AS unit_bill_count,
            COALESCE(ubs.unit_avg_bill_amount, 0)::double precision AS unit_avg_bill_amount,
            COALESCE(ubs.unit_std_bill_amount, 0)::double precision AS unit_std_bill_amount,
            COALESCE(vbeh.vendor_bill_count, 0)::bigint AS vendor_bill_count,
            COALESCE(vbeh.vendor_distinct_unit_count, 0)::bigint AS vendor_distinct_unit_count,
            COALESCE(vbeh.vendor_avg_bill_amount, 0)::double precision AS vendor_avg_bill_amount,
            COALESCE(vbeh.vendor_std_bill_amount, 0)::double precision AS vendor_std_bill_amount,
            CASE WHEN COALESCE(ubs.unit_std_bill_amount, 0) > 0 THEN ABS({bill_amount} - ubs.unit_avg_bill_amount) / ubs.unit_std_bill_amount ELSE 0 END AS unit_bill_amount_zscore,
            CASE WHEN COALESCE(vbeh.vendor_std_bill_amount, 0) > 0 THEN ABS({bill_amount} - vbeh.vendor_avg_bill_amount) / vbeh.vendor_std_bill_amount ELSE 0 END AS vendor_bill_amount_zscore,
            {bool_flag(f'COALESCE({bill_amount}, 0) > 0 AND MOD(ROUND(COALESCE({bill_amount}, 0))::bigint, 1000) = 0')} AS round_bill_amount_flag,
            {bool_flag(f'COALESCE({amount_passed}, 0) > 0 AND MOD(ROUND(COALESCE({amount_passed}, 0))::bigint, 1000) = 0')} AS round_amount_passed_flag
        FROM {quote_identifier('gem_bill')} AS {gb}
        {dak_join}
        {product_join}
        LEFT JOIN ch_booking_agg ch ON ch.fk_dak = {col(schema, 'gem_bill', gb, 'fk_dak')}
        LEFT JOIN disallowance_agg dis ON dis.fk_dak = {col(schema, 'gem_bill', gb, 'fk_dak')}
        LEFT JOIN recovery_agg rec ON rec.fk_dak = {col(schema, 'gem_bill', gb, 'fk_dak')}
        LEFT JOIN gst_tds_agg gst ON gst.fk_dak = {col(schema, 'gem_bill', gb, 'fk_dak')}
        LEFT JOIN cheque_slip_agg cs ON cs.fk_dak = {col(schema, 'gem_bill', gb, 'fk_dak')}
        LEFT JOIN punching_medium_agg pm ON pm.fk_dak = {col(schema, 'gem_bill', gb, 'fk_dak')}
        LEFT JOIN schedule3_agg s3 ON s3.fk_dak = {col(schema, 'gem_bill', gb, 'fk_dak')}
        LEFT JOIN ecs_agg ecs ON ecs.fk_dak = {col(schema, 'gem_bill', gb, 'fk_dak')}
        LEFT JOIN duplicate_agg dup ON dup.gem_bill_id = {qcol(gb, 'id')}
        LEFT JOIN vendor_bank_stats vbs ON vbs.vendor_bank_key = NULLIF({vendor_bank_key}, '')
        LEFT JOIN vendor_pan_bank_stats vpbs ON vpbs.vendor_pan_key = NULLIF({vendor_pan_key}, '')
        LEFT JOIN repeated_amount_stats ras ON ras.vendor_pan_key = NULLIF({vendor_pan_key}, '')
            AND ras.unit_id = {col(schema, 'gem_bill', gb, 'fk_unit')}
            AND ras.rounded_bill_amount = ROUND(COALESCE({bill_amount}, 0)::numeric, 0)
        LEFT JOIN reprocess_stats rs ON rs.reprocess_key = NULLIF(COALESCE(NULLIF({normalized_crac}, ''), NULLIF({normalize_sql(text_col(schema, 'gem_bill', gb, 'invoice_no'), ('GEM-',))}, ''), NULLIF({normalized_order}, ''), NULLIF({normalize_sql(text_col(schema, 'gem_bill', gb, 'transaction_id'))}, '')), '')
            AND (rs.vendor_pan_key = NULLIF({vendor_pan_key}, '') OR rs.vendor_pan_key IS NULL)
        LEFT JOIN payment_reference_stats prs ON prs.gem_bill_id = {qcol(gb, 'id')}
        LEFT JOIN unit_behavior_stats ubs ON ubs.unit_id = {col(schema, 'gem_bill', gb, 'fk_unit')}
        LEFT JOIN vendor_behavior_stats vbeh ON vbeh.vendor_pan_key = NULLIF({vendor_pan_key}, '')
        WHERE {dak_section_where}
        {date_filter}
    """


def build_feature_query(schema: Schema, amount_tolerance: float = DEFAULT_AMOUNT_TOLERANCE) -> str:
    ctes = [
        product_agg_cte(schema),
        ch_booking_agg_cte(schema),
        amount_agg_cte(schema, "disallowance", "disallowance_agg", ("amount",)),
        amount_agg_cte(schema, "recoveries", "recovery_agg", ("amount",)),
        gst_tds_agg_cte(schema),
        count_table_cte(schema, "cheque_slip", "cheque_slip_agg", valid_only=True),
        count_table_cte(schema, "punching_medium", "punching_medium_agg", valid_only=True),
        count_table_cte(schema, "schedule3", "schedule3_agg", valid_only=True),
        count_table_cte(schema, "ecs", "ecs_agg", valid_only=True),
        duplicate_agg_cte(schema),
        advanced_pattern_ctes(schema),
    ]
    base_query = build_base_query(schema, amount_tolerance=amount_tolerance)
    return f"WITH {', '.join(ctes)} {base_query}"


def _sum_flags(df: pd.DataFrame, columns: Iterable[str]) -> pd.Series:
    available = [column for column in columns if column in df.columns]
    if not available:
        return pd.Series(0, index=df.index, dtype="float64")
    return df[available].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)


def _numeric_series(df: pd.DataFrame, column: str, default: float = 0) -> pd.Series:
    if column not in df.columns:
        return pd.Series(default, index=df.index, dtype="float64")
    return pd.to_numeric(df[column], errors="coerce").fillna(default)


def _datetime_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(pd.NaT, index=df.index)
    return pd.to_datetime(df[column], errors="coerce")


def _date_gap_days(df: pd.DataFrame, later: str, earlier: str) -> pd.Series:
    later_dates = _datetime_series(df, later)
    earlier_dates = _datetime_series(df, earlier)
    return (later_dates - earlier_dates).dt.days


def add_derived_rule_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    flow_flags = [
        "gem_bill_without_dak_flag",
        "gem_product_without_gem_bill_flag",
        "cheque_slip_without_gem_bill_flag",
        "punching_medium_without_cheque_slip_flag",
        "schedule3_without_punching_medium_flag",
        "ecs_without_schedule3_flag",
        "ecs_without_cheque_slip_flag",
        "ecs_without_punching_medium_flag",
        "schedule3_without_pm_flag",
    ]
    required_flags = [
        "missing_unit_flag",
        "missing_msme_flag",
        "missing_make_type_flag",
        "missing_dak_flag",
        "missing_transaction_id_flag",
        "missing_crac_flag",
        "missing_order_id_flag",
        "missing_supply_order_no_flag",
        "missing_final_bill_date_flag",
        "missing_vendor_name_flag",
        "missing_vendor_bank_account_flag",
        "missing_vendor_ifsc_flag",
        "missing_product_details_flag",
        "missing_product_code_flag",
        "missing_code_head_flag",
        "missing_bill_amount_flag",
    ]
    duplicate_flags = [
        "duplicate_transaction_id_flag",
        "duplicate_gem_invoice_flag",
        "duplicate_crac_flag",
        "duplicate_order_same_crac_flag",
        "duplicate_supply_order_flag",
    ]
    amount_flags = [
        "paid_amount_exceeds_order_amount_flag",
        "crac_order_mismatch_flag",
        "crac_supply_order_mismatch_flag",
        "product_total_bill_amount_mismatch_flag",
        "amount_passed_mismatch_flag",
        "amount_to_be_paid_mismatch_flag",
        "negative_amount_to_be_paid_flag",
    ]
    budget_flags = ["chbooking_missing_flag", "chbooking_amount_mismatch_flag", "fund_verification_failed_flag"]
    gst_flags = [
        "gst_tds_applied_but_vendor_gstin_missing_flag",
        "gst_tds_missing_bill_amount_flag",
        "gst_tds_missing_type_flag",
        "gst_tds_invalid_flag",
    ]
    pm_cheque_flags = [
        "pm_generated_without_valid_bill_flag",
        "cheque_slip_generated_without_valid_bill_flag",
        "pm_without_cheque_slip_flag",
        "cheque_slip_without_pm_flag",
        "approved_cheque_slip_without_bill_approval_flag",
        "approved_pm_without_bill_approval_flag",
        "pm_not_tallied_reason_flag",
        "pm_generated_after_rejection_flag",
        "approved_but_payment_not_completed_flag",
    ]
    rejection_flags = [
        "rejection_reason_missing_flag",
        "ecs_exists_for_rejected_bill_flag",
        "rejected_bill_has_schedule3_flag",
        "rejected_bill_has_approved_pm_flag",
        "record_status_r_but_dak_not_r_after_approval_flag",
        "rejection_approved_but_payment_status_not_failure_flag",
    ]
    approval_flags = [
        "approved_bill_without_ecs_flag",
        "approved_but_payment_not_completed_flag",
    ]

    stage_columns = [
        "has_dak",
        "has_gem_bill",
        "has_gem_product",
        "has_ch_booking",
        "has_cheque_slip",
        "has_punching_medium",
        "has_schedule3",
        "has_ecs",
    ]
    df["flow_stage_count"] = _sum_flags(df, stage_columns)
    df["flow_skip_count"] = _sum_flags(df, flow_flags)
    df["flow_missing_stage_count"] = len(stage_columns) - df["flow_stage_count"]
    df["flow_anomaly_score"] = df["flow_skip_count"]
    df["later_stage_exists_but_previous_missing_flag"] = (df["flow_skip_count"] > 0).astype(float)
    df["missing_required_field_count"] = _sum_flags(df, required_flags)
    df["duplicate_identifier_count"] = _sum_flags(df, duplicate_flags)
    df["required_field_violation_count"] = df["missing_required_field_count"]
    df["duplicate_violation_count"] = df["duplicate_identifier_count"]
    df["flow_violation_count"] = df["flow_skip_count"]
    df["amount_violation_count"] = _sum_flags(df, amount_flags)
    df["budget_violation_count"] = _sum_flags(df, budget_flags)
    df["gst_recovery_violation_count"] = _sum_flags(df, gst_flags)
    df["pm_cheque_violation_count"] = _sum_flags(df, pm_cheque_flags)
    df["approval_violation_count"] = _sum_flags(df, approval_flags)
    df["rejection_violation_count"] = _sum_flags(df, rejection_flags)
    df["total_rule_violation_count"] = _sum_flags(
        df,
        [
            "required_field_violation_count",
            "duplicate_violation_count",
            "flow_violation_count",
            "amount_violation_count",
            "budget_violation_count",
            "gst_recovery_violation_count",
            "pm_cheque_violation_count",
            "approval_violation_count",
            "rejection_violation_count",
        ],
    )
    df["rule_based_risk_score"] = (
        df["duplicate_violation_count"] * 5
        + df["flow_violation_count"] * 5
        + df["pm_cheque_violation_count"] * 5
        + df["amount_violation_count"] * 4
        + df["budget_violation_count"] * 4
        + df["rejection_violation_count"] * 4
        + df["required_field_violation_count"] * 2
        + df["gst_recovery_violation_count"] * 3
    )
    df["likely_invalid_by_rules_flag"] = (df["required_field_violation_count"] + df["budget_violation_count"] + df["gst_recovery_violation_count"] > 0).astype(float)
    df["likely_rejected_by_rules_flag"] = (_numeric_series(df, "rejection_started_flag") > 0).astype(float)
    df["likely_flow_fraud_flag"] = (df["flow_violation_count"] > 0).astype(float)
    df["likely_duplicate_fraud_flag"] = (df["duplicate_violation_count"] > 0).astype(float)
    df["likely_payment_stage_fraud_flag"] = (df["pm_cheque_violation_count"] + df["rejection_violation_count"] > 0).astype(float)

    bill_amount = _numeric_series(df, "bill_amount")
    amount_passed = _numeric_series(df, "amount_passed")
    product_count = _numeric_series(df, "product_count")
    product_total = _numeric_series(df, "product_total_with_freight")
    product_freight = _numeric_series(df, "product_freight_total")
    product_gst = _numeric_series(df, "product_gst_total")
    product_avg_price = _numeric_series(df, "product_avg_unit_price")
    product_max_price = _numeric_series(df, "product_max_unit_price")
    pm_amount = _numeric_series(df, "pm_amount_total")
    cheque_amount = _numeric_series(df, "cheque_slip_amount_total")
    schedule_amount = _numeric_series(df, "schedule3_amount_total")
    ecs_amount = _numeric_series(df, "ecs_amount_total")

    dak_to_bill_days = _date_gap_days(df, "bill_date", "dak_list_date")
    bill_to_final_days = _date_gap_days(df, "final_bill_date", "bill_date")
    approval_to_pm_days = _date_gap_days(df, "pm_latest_date", "approval_date")
    pm_to_cheque_days = _date_gap_days(df, "cheque_slip_latest_date", "pm_latest_date")
    cheque_to_schedule_days = _date_gap_days(df, "schedule3_latest_date", "cheque_slip_latest_date")
    schedule_to_ecs_days = _date_gap_days(df, "ecs_latest_date", "schedule3_latest_date")

    df["negative_stage_gap_count"] = (
        (dak_to_bill_days < 0).fillna(False).astype(float)
        + (bill_to_final_days < 0).fillna(False).astype(float)
        + (approval_to_pm_days < 0).fillna(False).astype(float)
        + (pm_to_cheque_days < 0).fillna(False).astype(float)
        + (cheque_to_schedule_days < 0).fillna(False).astype(float)
        + (schedule_to_ecs_days < 0).fillna(False).astype(float)
    )
    df["slow_stage_gap_count"] = (
        (bill_to_final_days > 30).fillna(False).astype(float)
        + (approval_to_pm_days > 15).fillna(False).astype(float)
        + (pm_to_cheque_days > 15).fillna(False).astype(float)
        + (cheque_to_schedule_days > 15).fillna(False).astype(float)
        + (schedule_to_ecs_days > 15).fillna(False).astype(float)
    )
    df["timing_anomaly_count"] = (
        df["negative_stage_gap_count"]
        + df["slow_stage_gap_count"]
        + _sum_flags(df, ["bill_date_after_final_date_flag", "suspicious_future_date_flag"])
    )

    near_threshold = ((bill_amount >= 190000) & (bill_amount < 200000)).astype(float)
    same_order_over_threshold = (_numeric_series(df, "same_order_total_bill_amount") >= 200000).astype(float)
    repeated_near_threshold = ((_numeric_series(df, "repeated_vendor_unit_amount_count") > 1) & (bill_amount < 200000)).astype(float)
    df["threshold_anomaly_count"] = near_threshold + repeated_near_threshold + same_order_over_threshold

    df["vendor_bank_anomaly_count"] = _sum_flags(
        df,
        [
            "same_bank_account_multiple_vendors_flag",
            "same_vendor_multiple_bank_accounts_flag",
            "missing_vendor_bank_account_flag",
            "invalid_ifsc_length_flag",
        ],
    )
    df["product_similarity_anomaly_count"] = _sum_flags(
        df,
        [
            "duplicate_order_same_crac_flag",
            "duplicate_supply_order_flag",
            "duplicate_crac_flag",
            "duplicate_gem_invoice_flag",
        ],
    )
    df["unit_behavior_anomaly_count"] = (
        (_numeric_series(df, "unit_bill_amount_zscore") > 3).astype(float)
        + ((_numeric_series(df, "unit_bill_count") >= 5) & (bill_amount > (_numeric_series(df, "unit_avg_bill_amount") * 3).replace(0, np.inf))).astype(float)
    )
    df["vendor_behavior_anomaly_count"] = (
        (_numeric_series(df, "vendor_bill_amount_zscore") > 3).astype(float)
        + (_numeric_series(df, "vendor_distinct_unit_count") > 5).astype(float)
        + ((_numeric_series(df, "vendor_bill_count") >= 5) & (bill_amount > (_numeric_series(df, "vendor_avg_bill_amount") * 3).replace(0, np.inf))).astype(float)
    )
    df["code_head_anomaly_count"] = _sum_flags(
        df,
        [
            "missing_code_head_flag",
            "invalid_code_head_length_count",
            "rnd_code_head_missing_project_code_count",
        ],
    )
    df["rejected_reprocess_anomaly_count"] = (
        ((_numeric_series(df, "rejected_attempt_count") > 0) & (_numeric_series(df, "valid_or_approved_attempt_count") > 0)).astype(float)
        + (_numeric_series(df, "same_document_attempt_count") > 2).astype(float)
        + df["rejection_violation_count"]
    )
    df["user_behavior_anomaly_count"] = _sum_flags(
        df,
        [
            "approved_cheque_slip_without_bill_approval_flag",
            "approved_pm_without_bill_approval_flag",
            "approval_violation_count",
        ],
    )

    bill_dates = _datetime_series(df, "bill_date").fillna(_datetime_series(df, "dak_list_date"))
    df["month_end_anomaly_count"] = ((bill_dates.dt.day >= 28) | ((bill_dates.dt.month == 3) & (bill_dates.dt.day >= 25))).fillna(False).astype(float)
    df["repeated_amount_anomaly_count"] = (
        (_numeric_series(df, "repeated_vendor_unit_amount_count") > 1).astype(float)
        + _sum_flags(df, ["round_bill_amount_flag", "round_amount_passed_flag"])
    )
    df["advanced_ecs_payment_anomaly_count"] = (
        _sum_flags(df, ["ecs_exists_for_invalid_bill_flag", "ecs_exists_for_rejected_bill_flag", "approved_bill_without_ecs_flag"])
        + (_numeric_series(df, "duplicate_utr_count") > 1).astype(float)
        + (_numeric_series(df, "duplicate_payment_reference_count") > 1).astype(float)
        + ((ecs_amount > 0) & (abs(ecs_amount - schedule_amount) > DEFAULT_AMOUNT_TOLERANCE)).astype(float)
    )
    df["pm_cheque_amount_mismatch_count"] = (
        ((pm_amount > 0) & (cheque_amount > 0) & (abs(pm_amount - cheque_amount) > DEFAULT_AMOUNT_TOLERANCE)).astype(float)
        + ((schedule_amount > 0) & (cheque_amount > 0) & (abs(schedule_amount - cheque_amount) > DEFAULT_AMOUNT_TOLERANCE)).astype(float)
    )
    df["product_price_anomaly_count"] = (
        ((product_count > 0) & (product_max_price > 0) & (product_avg_price > 0) & (product_max_price > product_avg_price * 5)).astype(float)
        + ((product_total > 0) & ((product_freight / product_total.replace(0, np.nan)).fillna(0) > 0.25)).astype(float)
        + ((product_total > 0) & ((product_gst / product_total.replace(0, np.nan)).fillna(0) > 0.35)).astype(float)
        + _sum_flags(df, ["product_total_bill_amount_mismatch_flag"])
    )
    extra_pattern_columns = [
        "timing_anomaly_count",
        "threshold_anomaly_count",
        "vendor_bank_anomaly_count",
        "product_similarity_anomaly_count",
        "unit_behavior_anomaly_count",
        "vendor_behavior_anomaly_count",
        "code_head_anomaly_count",
        "rejected_reprocess_anomaly_count",
        "user_behavior_anomaly_count",
        "month_end_anomaly_count",
        "repeated_amount_anomaly_count",
        "advanced_ecs_payment_anomaly_count",
        "pm_cheque_amount_mismatch_count",
        "product_price_anomaly_count",
    ]
    df["extra_pattern_anomaly_count"] = _sum_flags(df, extra_pattern_columns)
    df["extra_pattern_risk_score"] = (
        df["vendor_bank_anomaly_count"] * 6
        + df["threshold_anomaly_count"] * 6
        + df["rejected_reprocess_anomaly_count"] * 5
        + df["advanced_ecs_payment_anomaly_count"] * 5
        + df["pm_cheque_amount_mismatch_count"] * 4
        + df["product_similarity_anomaly_count"] * 4
        + df["product_price_anomaly_count"] * 4
        + df["timing_anomaly_count"] * 3
        + df["unit_behavior_anomaly_count"] * 3
        + df["vendor_behavior_anomaly_count"] * 3
        + df["code_head_anomaly_count"] * 3
        + df["user_behavior_anomaly_count"] * 3
        + df["repeated_amount_anomaly_count"] * 2
        + df["month_end_anomaly_count"]
    )
    df["total_rule_violation_count"] = df["total_rule_violation_count"] + df["extra_pattern_anomaly_count"]
    df["rule_based_risk_score"] = df["rule_based_risk_score"] + df["extra_pattern_risk_score"]
    return df


def load_features(engine, start_date: str, end_date: str, row_limit: int | None = None) -> pd.DataFrame:
    schema = get_schema_columns(engine)
    query = build_feature_query(schema)
    params = {"start_date": start_date, "end_date": end_date}
    if row_limit:
        query = f"SELECT * FROM ({query}) AS gem_features ORDER BY gem_bill_id DESC LIMIT :row_limit"
        params["row_limit"] = row_limit
    df = pd.read_sql(text(query), engine, params=params)
    return add_derived_rule_features(df)


def ml_feature_columns(df: pd.DataFrame) -> list[str]:
    columns = []
    for column in df.columns:
        if column in REVIEW_COLUMNS:
            continue
        lower = column.lower()
        if any(term in lower for term in TEXT_EXCLUDE_TERMS) and not lower.endswith(("_flag", "_count", "_score", "_ratio", "_diff", "_total")):
            continue
        if pd.api.types.is_bool_dtype(df[column]) or pd.api.types.is_numeric_dtype(df[column]):
            columns.append(column)
    return columns


def prepare_ml_matrix(df: pd.DataFrame) -> tuple[np.ndarray, list[str], RobustScaler]:
    feature_columns = ml_feature_columns(df)
    if not feature_columns:
        raise RuntimeError("No numeric GEM bill feature columns available for Isolation Forest.")
    matrix_df = df[feature_columns].apply(pd.to_numeric, errors="coerce")
    matrix_df = matrix_df.replace([np.inf, -np.inf], np.nan)
    matrix_df = matrix_df.fillna(matrix_df.median(numeric_only=True)).fillna(0)
    scaler = RobustScaler()
    return scaler.fit_transform(matrix_df.to_numpy(dtype=float)), feature_columns, scaler


def train_isolation_forest(
    df: pd.DataFrame,
    contamination: float = DEFAULT_CONTAMINATION,
    random_state: int = 42,
) -> tuple[pd.DataFrame, IsolationForest, list[str]]:
    matrix, feature_columns, _ = prepare_ml_matrix(df)
    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )
    labels = model.fit_predict(matrix)
    scores = -model.decision_function(matrix)
    result = df.copy()
    result["anomaly_label"] = (labels == -1).astype(int)
    result["anomaly_score"] = scores
    result["top_rule_reasons"] = explain_rule_reasons(result)
    return result, model, feature_columns


RULE_REASON_MAP = {
    "flow_violation_count": "GEM payment table flow is broken or skipped",
    "duplicate_violation_count": "duplicate GEM bill identifiers were found",
    "amount_violation_count": "amount, product total, order, or payable calculation mismatch",
    "budget_violation_count": "budget/ch_booking evidence is missing or mismatched",
    "gst_recovery_violation_count": "GST TDS/recovery validation failed",
    "pm_cheque_violation_count": "PM/cheque slip payment stage is inconsistent",
    "approval_violation_count": "approval exists without expected payment completion",
    "rejection_violation_count": "rejection workflow conflicts with payment/Dak state",
    "required_field_violation_count": "mandatory GEM bill fields are missing",
    "timing_anomaly_count": "GEM bill has unusual date gaps or stage ordering",
    "threshold_anomaly_count": "Possible bill splitting around approval/procurement thresholds",
    "vendor_bank_anomaly_count": "Vendor bank/PAN pattern is unusual",
    "product_similarity_anomaly_count": "Similar or duplicate GEM product/order identifiers were found",
    "unit_behavior_anomaly_count": "Unit payment behavior is unusual for this bill amount",
    "vendor_behavior_anomaly_count": "Vendor payment behavior is unusual",
    "code_head_anomaly_count": "Code-head/product classification pattern is invalid or missing",
    "rejected_reprocess_anomaly_count": "Rejected bill appears to be reprocessed or paid later",
    "user_behavior_anomaly_count": "Approval/payment stage behavior is inconsistent",
    "month_end_anomaly_count": "Bill activity is concentrated near month-end or financial year-end",
    "repeated_amount_anomaly_count": "Repeated or round GEM bill amounts were found",
    "advanced_ecs_payment_anomaly_count": "ECS/payment reference or amount pattern is inconsistent",
    "pm_cheque_amount_mismatch_count": "Punching medium and cheque/schedule amounts do not match",
    "product_price_anomaly_count": "Product price, freight, GST, or bill total pattern is unusual",
}


def explain_rule_reasons(df: pd.DataFrame) -> pd.Series:
    reasons = []
    for _, row in df.iterrows():
        row_reasons = [
            reason
            for column, reason in RULE_REASON_MAP.items()
            if column in row and pd.notna(row[column]) and float(row[column]) > 0
        ]
        reasons.append("; ".join(row_reasons[:5]))
    return pd.Series(reasons, index=df.index)


def feature_dictionary(schema: Schema | None = None) -> list[dict]:
    specs = [
        FeatureSpec("has_gem_product", ("gem_bill", "gem_product"), ("gem_bill.id", "gem_product.fk_gem_bill", "gem_product.transaction_id"), "At least one product row must exist for a GEM bill.", "Missing product detail can indicate invalid or incomplete bill."),
        FeatureSpec("punching_medium_without_cheque_slip_flag", ("punching_medium", "cheque_slip"), ("fk_dak",), "PM should not exist without cheque slip evidence in the GEM payment flow.", "Payment flow skipped cheque slip."),
        FeatureSpec("schedule3_without_punching_medium_flag", ("schedule3", "punching_medium"), ("fk_dak",), "Schedule3 should follow punching_medium.", "Final schedule exists without PM stage."),
        FeatureSpec("ecs_without_schedule3_flag", ("ecs", "schedule3"), ("fk_dak",), "ECS should follow schedule3.", "Final payment exists without schedule3."),
        FeatureSpec("missing_required_field_count", ("gem_bill", "gem_product"), ("unit/msme/make_type/dak/transaction/crac/order/final_bill/vendor/bank/product/code_head/bill_amount",), "Counts mandatory GEM validation field failures.", "Bill would likely fail deterministic validation."),
        FeatureSpec("duplicate_identifier_count", ("gem_bill",), ("transaction_id", "gem_invoice_no", "crac_no", "order_id", "supply_order_no"), "Counts duplicate GEM identifiers among non-rejected bills.", "Possible duplicate or repeated payment."),
        FeatureSpec("product_total_bill_amount_mismatch_flag", ("gem_bill", "gem_product"), ("bill_amount", "ld_amount", "total_value", "frieght_charge"), "Bill amount should match product total with freight minus LD tolerance.", "Product and bill amount do not reconcile."),
        FeatureSpec("chbooking_missing_flag", ("gem_bill", "ch_booking"), ("fk_dak", "record_status"), "Valid ch_booking should exist after bill validation.", "Fund/budget verification evidence is missing."),
        FeatureSpec("gst_tds_invalid_flag", ("gem_bill", "gst_tds"), ("vendor_gstn", "bill_amount", "gst_type", "tds_*"), "GST TDS requires vendor GSTIN and complete GST TDS rows.", "GST/recovery validation is incomplete."),
        FeatureSpec("pm_generated_without_valid_bill_flag", ("gem_bill", "punching_medium"), ("record_status", "fk_dak"), "PM should only be generated for valid GEM bills.", "Payment stage exists for invalid/rejected bill."),
        FeatureSpec("approved_but_payment_not_completed_flag", ("gem_bill", "ecs"), ("approved", "fk_dak"), "Approved GEM bills should normally reach ECS or remain explainably pending.", "Approved bill has no completed payment evidence."),
        FeatureSpec("record_status_r_but_dak_not_r_after_approval_flag", ("gem_bill", "dak"), ("record_status", "approved", "dak.record_status"), "Final rejection should also reject Dak.", "Rejected bill workflow did not update Dak rejection state."),
        FeatureSpec("timing_anomaly_count", ("dak", "gem_bill", "cheque_slip", "punching_medium", "schedule3", "ecs"), ("list_date", "bill_date", "final_bill_date", "approval dates", "stage dates"), "Counts negative, future, or unusually slow GEM payment stage gaps.", "Stage timing may indicate backdated, delayed, or out-of-order processing."),
        FeatureSpec("threshold_anomaly_count", ("gem_bill",), ("bill_amount", "order_amount", "fk_unit", "vendor_pan"), "Counts bills just below threshold values and repeated small bills that together cross threshold.", "Possible bill splitting around approval or procurement thresholds."),
        FeatureSpec("vendor_bank_anomaly_count", ("gem_bill",), ("vendor_pan", "vendor_enc_bank_account", "vendor_ifsc"), "Counts shared bank accounts across vendors, multiple accounts per vendor, and invalid/missing bank evidence.", "Vendor bank identity pattern is suspicious."),
        FeatureSpec("product_similarity_anomaly_count", ("gem_bill", "gem_product"), ("crac_no", "order_id", "supply_order_no", "gem_invoice_no", "product identifiers"), "Counts duplicate product/order/invoice identifiers as a deterministic fallback for similarity detection.", "Possible repeated product billing or duplicate procurement claim."),
        FeatureSpec("unit_behavior_anomaly_count", ("gem_bill",), ("fk_unit", "bill_amount"), "Counts unit-level bill amount outliers using historical unit averages and standard deviation.", "Bill amount is unusual for the unit."),
        FeatureSpec("vendor_behavior_anomaly_count", ("gem_bill",), ("vendor_pan", "fk_unit", "bill_amount"), "Counts vendor-level bill amount outliers and vendors spread across many units.", "Vendor behavior differs from normal historical pattern."),
        FeatureSpec("code_head_anomaly_count", ("gem_product",), ("code_head", "project_code"), "Counts missing/invalid code head and R&D code heads without project code.", "Accounting/product classification is incomplete or invalid."),
        FeatureSpec("rejected_reprocess_anomaly_count", ("gem_bill", "dak"), ("record_status", "approved", "crac_no", "invoice_no", "order_id"), "Counts rejected documents that later appear valid/approved or repeat many times.", "Rejected bill may have been reprocessed into payment."),
        FeatureSpec("advanced_ecs_payment_anomaly_count", ("gem_bill", "schedule3", "ecs"), ("utr_no", "payment_reference_no", "amount", "fk_dak"), "Counts duplicate payment references, ECS for invalid/rejected bills, and ECS/schedule amount mismatches.", "Payment settlement evidence is suspicious."),
        FeatureSpec("extra_pattern_risk_score", ("gem_bill", "gem_product", "dak", "cheque_slip", "punching_medium", "schedule3", "ecs"), ("derived counters",), "Weighted score over all advanced GEM fraud patterns.", "Higher score means more advanced GEM-specific risk signals."),
    ]
    output = []
    for spec in specs:
        available = spec.available
        limitation = spec.limitation
        if schema:
            missing_tables = [table for table in spec.source_tables if not schema.has_table(table)]
            if missing_tables:
                available = False
                limitation = f"Missing table(s): {', '.join(missing_tables)}"
        output.append({**spec.__dict__, "available": available, "limitation": limitation})
    return output


def export_results(features: pd.DataFrame, anomalies: pd.DataFrame, output_dir: Path = OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_dir / "gem_bill_features.csv", index=False)
    anomalies.to_csv(output_dir / "gem_bill_anomalies.csv", index=False)


def export_feature_dictionary(engine=None) -> None:
    schema = get_schema_columns(engine) if engine is not None else None
    with open(FEATURE_DICTIONARY_FILE, "w", encoding="utf-8") as output_file:
        json.dump(feature_dictionary(schema), output_file, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Build GEM bill ML features and Isolation Forest anomalies.")
    parser.add_argument("--start-date", required=True, help="Dak list_date start date, YYYY-MM-DD.")
    parser.add_argument("--end-date", required=True, help="Dak list_date end date, YYYY-MM-DD.")
    parser.add_argument("--row-limit", type=int, default=None)
    parser.add_argument("--contamination", type=float, default=DEFAULT_CONTAMINATION)
    args = parser.parse_args()

    engine = build_engine()
    features = load_features(engine, args.start_date, args.end_date, row_limit=args.row_limit)
    scored, _, _ = train_isolation_forest(features, contamination=args.contamination)
    anomalies = scored[scored["anomaly_label"] == 1].sort_values("anomaly_score", ascending=False)
    export_results(features, anomalies)
    export_feature_dictionary(engine)
    print(f"Wrote {len(features)} GEM feature row(s) and {len(anomalies)} anomaly row(s) to {OUTPUT_DIR}.")


if __name__ == "__main__":
    main()
