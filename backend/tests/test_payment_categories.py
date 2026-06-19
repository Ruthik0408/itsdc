import json

import pytest

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
            "GEM_BILLS": {
                "source_tables": ["gem_bill"],
                "dak_section_ids": [113, 127],
            },
        },
    )
    monkeypatch.setenv("PAYMENT_CATEGORY_CONFIG_FILE", str(config_path))
    monkeypatch.setenv("LLAMA_BUSINESS_PRIORITY_TABLES", "THIRD_PARTY_PAYMENTS,GEM_BILLS,ecs")
    table_exclusions.load_payment_category_config.cache_clear()

    try:
        assert table_exclusions.get_payment_category_source_tables() == {
            "THIRD_PARTY_PAYMENTS": ("dak", "bill", "cheque_slip", "punching_medium", "schedule3", "ecs"),
            "GEM_BILLS": ("gem_bill",),
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
            "gem_bill",
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
