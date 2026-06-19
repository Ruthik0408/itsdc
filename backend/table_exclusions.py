import json
import os
from functools import lru_cache
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
PAYMENT_CATEGORY_CONFIG_FILE = str(BACKEND_DIR / "payment_categories.json")


EXCLUDED_TABLES = frozenset(
    {
        "product_embedding",
        "detected_anomalies",
        "ML_Features",
    }
)

DEFAULT_BUSINESS_PRIORITY_TABLES = (
    "dak",
    "bill",
    "cheque_slip",
    "punching_medium",
    "schedule3",
    "ecs",
)

def _clean_string_list(value, field_name: str, category: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise RuntimeError(f"{PAYMENT_CATEGORY_CONFIG_FILE}: {category}.{field_name} must be a list.")
    cleaned = tuple(item.strip() for item in value if isinstance(item, str) and item.strip())
    if not cleaned:
        raise RuntimeError(f"{PAYMENT_CATEGORY_CONFIG_FILE}: {category}.{field_name} cannot be empty.")
    return cleaned


def _clean_int_list(value, field_name: str, category: str) -> tuple[int, ...]:
    if not isinstance(value, list):
        raise RuntimeError(f"{PAYMENT_CATEGORY_CONFIG_FILE}: {category}.{field_name} must be a list.")
    cleaned = tuple(item for item in value if isinstance(item, int) and item > 0)
    if len(cleaned) != len(value) or not cleaned:
        raise RuntimeError(
            f"{PAYMENT_CATEGORY_CONFIG_FILE}: {category}.{field_name} must contain positive integer IDs only."
        )
    return cleaned


def validate_payment_category_entry(category: str, source_tables, dak_section_ids) -> dict[str, tuple]:
    category = str(category).strip()
    if not category:
        raise RuntimeError("Payment category name cannot be empty.")
    return {
        "source_tables": _clean_string_list(source_tables, "source_tables", category),
        "dak_section_ids": _clean_int_list(dak_section_ids, "dak_section_ids", category),
    }


@lru_cache(maxsize=1)
def load_payment_category_config() -> dict[str, dict[str, tuple]]:
    configured_path = os.getenv("PAYMENT_CATEGORY_CONFIG_FILE", PAYMENT_CATEGORY_CONFIG_FILE)
    with open(configured_path, "r", encoding="utf-8") as config_file:
        raw_config = json.load(config_file)

    if not isinstance(raw_config, dict):
        raise RuntimeError(f"{configured_path} must contain a JSON object.")

    categories: dict[str, dict[str, tuple]] = {}
    for raw_category, raw_value in raw_config.items():
        category = str(raw_category).strip()
        if not category:
            raise RuntimeError(f"{configured_path} contains an empty payment category name.")
        if not isinstance(raw_value, dict):
            raise RuntimeError(f"{configured_path}: {category} must be a JSON object.")

        categories[category] = validate_payment_category_entry(
            category,
            raw_value.get("source_tables"),
            raw_value.get("dak_section_ids"),
        )

    if not categories:
        raise RuntimeError(f"{configured_path} must define at least one payment category.")
    return categories


def get_payment_category_source_tables() -> dict[str, tuple[str, ...]]:
    return {
        category: config["source_tables"]
        for category, config in load_payment_category_config().items()
    }


def get_payment_category_dak_sections() -> dict[str, tuple[int, ...]]:
    return {
        category: config["dak_section_ids"]
        for category, config in load_payment_category_config().items()
    }


def is_excluded_table(table_name: str) -> bool:
    return table_name in EXCLUDED_TABLES


def get_allowed_source_tables() -> tuple[str, ...]:
    configured = os.getenv("LLAMA_BUSINESS_PRIORITY_TABLES")
    raw_tables = configured if configured is not None else ",".join(DEFAULT_BUSINESS_PRIORITY_TABLES)
    tables = []
    seen = set()
    for table in raw_tables.split(","):
        table = table.strip()
        if not table or table in seen or is_excluded_table(table):
            continue
        tables.append(table)
        seen.add(table)
    return tuple(tables)


def get_allowed_physical_source_tables() -> tuple[str, ...]:
    payment_category_source_tables = get_payment_category_source_tables()
    tables = []
    seen = set()
    for table in get_allowed_source_tables():
        physical_tables = payment_category_source_tables.get(table, (table,))
        for physical_table in physical_tables:
            if physical_table in seen or is_excluded_table(physical_table):
                continue
            tables.append(physical_table)
            seen.add(physical_table)
    return tuple(tables)


def is_allowed_source_table(table_name: str) -> bool:
    return table_name in set(get_allowed_source_tables()) or table_name in set(get_allowed_physical_source_tables())
