import os
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("GEM_REPEAT_SIMILARITY_THRESHOLD", "0.82"))
DEFAULT_MAX_RESULTS = int(os.getenv("GEM_REPEAT_MAX_RESULTS", "100"))
DEFAULT_MAX_SOURCE_ROWS = int(os.getenv("GEM_REPEAT_MAX_SOURCE_ROWS", "1000"))
DEFAULT_STATEMENT_TIMEOUT = os.getenv("GEM_REPEAT_STATEMENT_TIMEOUT", "45s")


@dataclass(frozen=True)
class GemRepeatPurchaseAnomaly:
    transaction_id: str
    table_name: str
    source_record_id: str
    score: float
    context: dict


REQUIRED_TABLES = ("gem_bill", "gem_product", "product_embedding")


def required_tables_exist(engine) -> bool:
    with engine.connect() as conn:
        existing_tables = {
            row[0]
            for row in conn.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_name = ANY(:tables);
                    """
                ),
                {"tables": list(REQUIRED_TABLES)},
            )
        }
    missing_tables = sorted(set(REQUIRED_TABLES) - existing_tables)
    if missing_tables:
        print(
            "[gem-repeat] Skipping detector; missing table(s): "
            f"{', '.join(missing_tables)}.",
            flush=True,
        )
        return False
    return True


def build_repeat_purchase_query() -> str:
    return """
        WITH recent_valid_bills AS MATERIALIZED (
            SELECT
                transaction_id,
                order_id,
                fk_central_unit,
                supply_order_date,
                record_status,
                approved
            FROM gem_bill
            WHERE record_status = 'V'
              AND approved IS TRUE
              AND fk_central_unit IS NOT NULL
              AND order_id IS NOT NULL
              AND transaction_id IS NOT NULL
              AND supply_order_date IS NOT NULL
            ORDER BY supply_order_date DESC
            LIMIT :max_source_rows
        ),
        valid_items AS MATERIALIZED (
            SELECT
                b.transaction_id,
                b.order_id,
                b.fk_central_unit,
                b.supply_order_date,
                b.record_status,
                b.approved,
                p.product_name,
                p.total_value,
                e.embedding
            FROM recent_valid_bills b
            JOIN gem_product p
                ON p.transaction_id = b.transaction_id
            JOIN product_embedding e
                ON lower(trim(e.product_name)) = lower(trim(p.product_name))
            WHERE p.product_name IS NOT NULL
              AND trim(p.product_name) <> ''
        )
        SELECT
            a.transaction_id AS first_transaction_id,
            b.transaction_id AS second_transaction_id,
            a.order_id AS first_order_id,
            b.order_id AS second_order_id,
            a.fk_central_unit,
            a.supply_order_date AS first_supply_order_date,
            b.supply_order_date AS second_supply_order_date,
            a.product_name AS first_product_name,
            b.product_name AS second_product_name,
            a.total_value AS first_total_value,
            b.total_value AS second_total_value,
            ABS((b.supply_order_date - a.supply_order_date))::integer AS days_between,
            1 - (a.embedding <=> b.embedding) AS similarity
        FROM valid_items a
        JOIN valid_items b
            ON a.fk_central_unit = b.fk_central_unit
           AND a.order_id <> b.order_id
           AND a.transaction_id < b.transaction_id
           AND b.supply_order_date BETWEEN a.supply_order_date - INTERVAL '2 months'
                                      AND a.supply_order_date + INTERVAL '2 months'
        WHERE 1 - (a.embedding <=> b.embedding) >= :similarity_threshold
        ORDER BY similarity DESC, days_between ASC
        LIMIT :max_results;
    """


def build_reason(row) -> str:
    return (
        f"Central unit {row.fk_central_unit} purchased `{row.first_product_name}` "
        f"under order {row.first_order_id} on {row.first_supply_order_date}. "
        f"The same central unit purchased `{row.second_product_name}` under order "
        f"{row.second_order_id} on {row.second_supply_order_date}. "
        f"The purchases are {row.days_between} day(s) apart, use different order IDs, "
        f"and product-name embedding similarity is {float(row.similarity):.2f}. "
        "This may indicate repeat procurement of a semantically similar product within two months."
    )


def detect_gem_repeat_purchase_anomalies(
    engine,
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    max_results: int = DEFAULT_MAX_RESULTS,
    max_source_rows: int = DEFAULT_MAX_SOURCE_ROWS,
) -> list[GemRepeatPurchaseAnomaly]:
    print(
        "[gem-repeat] Starting GEM repeat-purchase detector "
        f"(similarity_threshold={similarity_threshold}, max_results={max_results}, "
        f"max_source_rows={max_source_rows}).",
        flush=True,
    )
    if not required_tables_exist(engine):
        return []

    try:
        with engine.connect() as conn:
            conn.execute(text("SET statement_timeout = :statement_timeout"), {"statement_timeout": DEFAULT_STATEMENT_TIMEOUT})
            rows = conn.execute(
                text(build_repeat_purchase_query()),
                {
                    "similarity_threshold": similarity_threshold,
                    "max_results": max_results,
                    "max_source_rows": max_source_rows,
                },
            ).fetchall()
    except SQLAlchemyError as exc:
        print(f"[gem-repeat] Detector query failed: {exc}", flush=True)
        return []

    anomalies = []
    for row in rows:
        first_transaction_id = str(row.first_transaction_id)
        second_transaction_id = str(row.second_transaction_id)
        source_record_id = f"{first_transaction_id}|{second_transaction_id}"
        similarity = float(row.similarity)
        context = {
            "detector_type": "gem_repeat_purchase",
            "source_table": "gem_bill+gem_product+product_embedding",
            "first_transaction_id": first_transaction_id,
            "second_transaction_id": second_transaction_id,
            "first_order_id": str(row.first_order_id),
            "second_order_id": str(row.second_order_id),
            "fk_central_unit": int(row.fk_central_unit),
            "first_supply_order_date": str(row.first_supply_order_date),
            "second_supply_order_date": str(row.second_supply_order_date),
            "first_product_name": row.first_product_name,
            "second_product_name": row.second_product_name,
            "first_total_value": float(row.first_total_value) if row.first_total_value is not None else None,
            "second_total_value": float(row.second_total_value) if row.second_total_value is not None else None,
            "days_between": int(row.days_between),
            "similarity": similarity,
            "similarity_threshold": similarity_threshold,
            "business_rule": (
                "same fk_central_unit, approved valid GEM bills, different order_id, "
                "supply_order_date within two months, and similar product_name embedding"
            ),
            "statistical_reason": build_reason(row),
        }
        anomalies.append(
            GemRepeatPurchaseAnomaly(
                transaction_id=f"gem_repeat_purchase:{first_transaction_id}:{second_transaction_id}",
                table_name="gem_bill+gem_product",
                source_record_id=source_record_id,
                score=similarity * 100,
                context=context,
            )
        )

    print(f"[gem-repeat] Detected {len(anomalies)} repeat-purchase candidate(s).", flush=True)
    return anomalies
