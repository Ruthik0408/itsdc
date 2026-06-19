import json

import pytest

import payment_category_filtering
import table_exclusions


def _write_config(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_payment_category_config_maps_logical_to_physical_tables(monkeypatch, tmp_path):
    config_path = tmp_path / "payment_categories.json"
    _write_config(
        config_path,
        {
            "THIRD_PARTY_PAYMENTS": {
                "source_tables": ["dak", "bill", "cheque_slip", "punching_medium", "schedule3", "ecs"],
                "dak_section_ids": [142, 228, 265, 383],
            },
            "UNIT_PAYMENTS": {
                "source_tables": ["bill", "cash_requisition"],
                "dak_section_ids": [143, 227],
            },
            "GEM_BILLS": {
                "source_tables": ["dak", "gem_bill", "gem_product", "cheque_slip", "punching_medium", "schedule3", "ecs"],
                "dak_section_ids": [113, 127],
            },
        },
    )
    monkeypatch.setenv("PAYMENT_CATEGORY_CONFIG_FILE", str(config_path))
    monkeypatch.setenv("LLAMA_BUSINESS_PRIORITY_TABLES", "THIRD_PARTY_PAYMENTS,UNIT_PAYMENTS,GEM_BILLS,ecs")
    table_exclusions.load_payment_category_config.cache_clear()

    try:
        assert table_exclusions.get_payment_category_source_tables() == {
            "THIRD_PARTY_PAYMENTS": ("dak", "bill", "cheque_slip", "punching_medium", "schedule3", "ecs"),
            "UNIT_PAYMENTS": ("bill", "cash_requisition"),
            "GEM_BILLS": ("dak", "gem_bill", "gem_product", "cheque_slip", "punching_medium", "schedule3", "ecs"),
        }
        assert table_exclusions.get_payment_category_dak_sections()["THIRD_PARTY_PAYMENTS"] == (
            142,
            228,
            265,
            383,
        )
        assert table_exclusions.get_allowed_physical_source_tables() == (
            "dak",
            "bill",
            "cheque_slip",
            "punching_medium",
            "schedule3",
            "ecs",
            "cash_requisition",
            "gem_bill",
            "gem_product",
        )
    finally:
        table_exclusions.load_payment_category_config.cache_clear()


def test_payment_category_config_rejects_bad_section_ids(monkeypatch, tmp_path):
    config_path = tmp_path / "payment_categories.json"
    _write_config(
        config_path,
        {
            "BROKEN": {
                "source_tables": ["bill"],
                "dak_section_ids": [142, "bad"],
            },
        },
    )
    monkeypatch.setenv("PAYMENT_CATEGORY_CONFIG_FILE", str(config_path))
    table_exclusions.load_payment_category_config.cache_clear()

    try:
        with pytest.raises(RuntimeError, match="positive integer IDs"):
            table_exclusions.load_payment_category_config()
    finally:
        table_exclusions.load_payment_category_config.cache_clear()


def test_shared_payment_tables_are_not_reclassified_by_default():
    sources = [
        payment_category_filtering.RuntimeSource(
            table="cheque_slip",
            id_column="id",
            amount_column="amount",
            context_columns=("fk_dak",),
            date_column="cheque_slip_date",
        ),
        payment_category_filtering.RuntimeSource(
            table="gem_product",
            id_column="id",
            amount_column="total_value",
            context_columns=("product_name",),
            date_column=None,
        ),
    ]
    payment_categories = {
        "THIRD_PARTY_PAYMENTS": {
            "source_tables": ("dak", "bill", "cheque_slip", "punching_medium", "schedule3", "ecs"),
            "dak_section_ids": (142, 228, 265, 383),
        },
        "GEM_BILLS": {
            "source_tables": ("dak", "gem_bill", "gem_product", "cheque_slip", "punching_medium", "schedule3", "ecs"),
            "dak_section_ids": (113, 127),
        },
    }

    filtered = payment_category_filtering.apply_payment_category_filters(sources, payment_categories)

    source_by_table = {source.table: source for source in filtered}
    assert source_by_table["cheque_slip"].payment_category is None
    assert source_by_table["gem_product"].payment_category == "GEM_BILLS"


def test_selected_payment_category_filters_shared_tables_to_that_category():
    sources = [
        payment_category_filtering.RuntimeSource("bill", "id", "amount", ("fk_dak",), None),
        payment_category_filtering.RuntimeSource("cash_requisition", "id", "amount", ("fk_dak",), None),
        payment_category_filtering.RuntimeSource("gem_bill", "id", "bill_amount", ("fk_dak",), None),
    ]
    payment_categories = {
        "THIRD_PARTY_PAYMENTS": {
            "source_tables": ("dak", "bill"),
            "dak_section_ids": (142,),
        },
        "UNIT_PAYMENTS": {
            "source_tables": ("bill", "cash_requisition"),
            "dak_section_ids": (143, 227),
        },
        "GEM_BILLS": {
            "source_tables": ("gem_bill",),
            "dak_section_ids": (113,),
        },
    }

    filtered = payment_category_filtering.apply_payment_category_filters(
        sources,
        payment_categories,
        selected_payment_category="up",
    )

    assert [source.table for source in filtered] == ["bill", "cash_requisition"]
    assert {source.payment_category for source in filtered} == {"UNIT_PAYMENTS"}
    assert {source.dak_section_ids for source in filtered} == {(143, 227)}
