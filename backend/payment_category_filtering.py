from dataclasses import dataclass

from table_exclusions import (
    get_allowed_source_tables,
    get_payment_category_source_tables,
    is_excluded_table,
    load_payment_category_config,
)


@dataclass(frozen=True)
class JoinedContext:
    source_column: str
    reference_table: str
    reference_pk: str
    reference_column: str
    alias: str


@dataclass(frozen=True)
class RuntimeSource:
    table: str
    id_column: str
    amount_column: str
    context_columns: tuple[str, ...]
    date_column: str | None
    feature_plan: tuple[dict, ...] = ()
    base_context_columns: tuple[str, ...] = ()
    joined_context_columns: tuple[JoinedContext, ...] = ()
    payment_category: str | None = None
    dak_section_ids: tuple[int, ...] = ()

    @property
    def scan_name(self) -> str:
        return self.payment_category or self.table


PAYMENT_CATEGORY_ALIASES = {
    "TPP": "THIRD_PARTY_PAYMENTS",
    "THIRD_PARTY": "THIRD_PARTY_PAYMENTS",
    "THIRD_PARTY_PAYMENTS": "THIRD_PARTY_PAYMENTS",
    "GEM": "GEM_BILLS",
    "GEM_BILLS": "GEM_BILLS",
    "UP": "UNIT_PAYMENTS",
    "UNIT": "UNIT_PAYMENTS",
    "UNIT_PAYMENTS": "UNIT_PAYMENTS",
}


def payment_category_source_tables_from_config(
    payment_categories: dict[str, dict[str, tuple]]
) -> dict[str, tuple[str, ...]]:
    return {
        category: config["source_tables"]
        for category, config in payment_categories.items()
        if config.get("enabled", True)
    }


def payment_category_dak_sections_from_config(
    payment_categories: dict[str, dict[str, tuple]]
) -> dict[str, tuple[int, ...]]:
    return {
        category: config["dak_section_ids"]
        for category, config in payment_categories.items()
        if config.get("enabled", True)
    }


def normalize_payment_category(
    payment_category: str | None,
    payment_categories: dict[str, dict[str, tuple]],
) -> str | None:
    if not payment_category:
        return None
    normalized = PAYMENT_CATEGORY_ALIASES.get(str(payment_category).strip().upper())
    if not normalized:
        raise RuntimeError(f"Unknown payment category: {payment_category}")
    if normalized not in payment_categories:
        raise RuntimeError(f"Payment category is not configured: {normalized}")
    if not payment_categories[normalized].get("enabled", True):
        raise RuntimeError(f"Payment category is disabled: {normalized}")
    return normalized


def resolve_allowed_physical_source_tables(
    payment_category_source_tables: dict[str, tuple[str, ...]] | None = None,
) -> tuple[str, ...]:
    payment_category_source_tables = payment_category_source_tables or get_payment_category_source_tables()
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


def _with_payment_filter(
    source: RuntimeSource,
    payment_category: str | None,
    payment_category_dak_sections: dict[str, tuple[int, ...]],
) -> RuntimeSource:
    if not payment_category:
        return source
    return RuntimeSource(
        table=source.table,
        id_column=source.id_column,
        amount_column=source.amount_column,
        context_columns=source.context_columns,
        date_column=source.date_column,
        feature_plan=source.feature_plan,
        base_context_columns=source.base_context_columns,
        joined_context_columns=source.joined_context_columns,
        payment_category=payment_category,
        dak_section_ids=payment_category_dak_sections[payment_category],
    )


def apply_payment_category_filters(
    sources: list[RuntimeSource],
    payment_categories: dict[str, dict[str, tuple]] | None = None,
    selected_payment_category: str | None = None,
) -> list[RuntimeSource]:
    configured_items = get_allowed_source_tables()
    payment_categories = payment_categories or load_payment_category_config()
    all_payment_category_source_tables = {
        category: config["source_tables"]
        for category, config in payment_categories.items()
    }
    payment_category_source_tables = payment_category_source_tables_from_config(payment_categories)
    payment_category_dak_sections = payment_category_dak_sections_from_config(payment_categories)
    selected_payment_category = normalize_payment_category(selected_payment_category, payment_categories)
    if selected_payment_category:
        source_by_table = {source.table: source for source in sources}
        return [
            _with_payment_filter(source_by_table[table], selected_payment_category, payment_category_dak_sections)
            for table in payment_category_source_tables.get(selected_payment_category, ())
            if table in source_by_table
        ]

    if any(item in all_payment_category_source_tables for item in configured_items):
        filtered_sources: list[RuntimeSource] = []
        source_by_table = {source.table: source for source in sources}
        for item in configured_items:
            if item in all_payment_category_source_tables:
                if item not in payment_category_source_tables:
                    continue
                for table in payment_category_source_tables[item]:
                    source = source_by_table.get(table)
                    if source:
                        filtered_sources.append(_with_payment_filter(source, item, payment_category_dak_sections))
                continue

            source = source_by_table.get(item)
            if source:
                filtered_sources.append(source)
        return filtered_sources

    table_category_counts: dict[str, int] = {}
    for tables in payment_category_source_tables.values():
        for table in tables:
            table_category_counts[table] = table_category_counts.get(table, 0) + 1
    default_table_payment_category = {
        table: category
        for category, tables in payment_category_source_tables.items()
        for table in tables
        if table_category_counts.get(table, 0) == 1
    }
    disabled_table_categories = {
        table: category
        for category, tables in all_payment_category_source_tables.items()
        if category not in payment_category_source_tables
        for table in tables
    }
    return [
        _with_payment_filter(
            source,
            default_table_payment_category.get(source.table),
            payment_category_dak_sections,
        )
        for source in sources
        if source.table not in disabled_table_categories
    ]
