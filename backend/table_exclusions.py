import os


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
    "gem_bill",
    "cheque_slip",
    "punching_medium",
    "schedule3",
    "ecs",
    "cash_requisition",
    "gem_product",
    "civ_medical_bill",
    "civ_paybill",
    "civ_tada_ltc_bill",
    "echs_medical_bill",
    "cmp_scroll",
    "civ_employee_earning",
    "civ_employee",
    "civ_employee_recovery",
    "civ_emp_allowances",
    "recoveries",
    "vendor",
)


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


def is_allowed_source_table(table_name: str) -> bool:
    return table_name in set(get_allowed_source_tables())
