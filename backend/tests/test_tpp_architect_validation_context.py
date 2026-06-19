import json

import tpp_architect


def test_parse_validation_markdown_table_rows(tmp_path):
    path = tmp_path / "THIRD_PARTY_PAYMENTS_VALIDATION.md"
    path.write_text(
        "\n".join(
            [
                "# Context",
                "",
                "| table_name | column_name | validation |",
                "|---|---|---|",
                "| bill | amount_claimed | Claim amount validation. |",
                "| dak | bill_no | Required for normal third party bills. |",
            ]
        ),
        encoding="utf-8",
    )

    rules = tpp_architect.parse_validation_markdown(path)

    assert rules == [
        {
            "context_name": "THIRD_PARTY_PAYMENTS_VALIDATION",
            "table": "bill",
            "column": "amount_claimed",
            "validation": "Claim amount validation.",
        },
        {
            "context_name": "THIRD_PARTY_PAYMENTS_VALIDATION",
            "table": "dak",
            "column": "bill_no",
            "validation": "Required for normal third party bills.",
        },
    ]


def test_validation_context_includes_direct_fk_related_rules(monkeypatch):
    rules = (
        {
            "context_name": "THIRD_PARTY_PAYMENTS_VALIDATION",
            "table": "bill",
            "column": "amount_claimed",
            "validation": "Claim amount validation.",
        },
        {
            "context_name": "THIRD_PARTY_PAYMENTS_VALIDATION",
            "table": "dak",
            "column": "bill_no",
            "validation": "Required for normal third party bills.",
        },
    )
    monkeypatch.setattr(tpp_architect, "load_validation_context_rules", lambda: rules)

    context = tpp_architect.validation_context_for_table_detail(
        {
            "table": "bill",
            "relationship_context": [{"referenced_table": "dak"}],
        }
    )

    assert [rule["table"] for rule in context] == ["bill", "dak"]


def test_architect_schema_pruning_keeps_only_third_party_tables():
    rows = [
        {"table": "dak", "column": "id", "data_type": "bigint", "key": "PK", "references": "None"},
        {"table": "bill", "column": "fk_dak", "data_type": "bigint", "key": "FK", "references": "dak"},
        {"table": "cheque_slip", "column": "fk_dak", "data_type": "bigint", "key": "FK", "references": "dak"},
        {"table": "gst_tds", "column": "bill_amount", "data_type": "numeric", "key": "", "references": "None"},
        {"table": "gem_bill", "column": "fk_dak", "data_type": "bigint", "key": "FK", "references": "dak"},
        {"table": "vendor", "column": "id", "data_type": "integer", "key": "PK", "references": "None"},
    ]

    pruned = tpp_architect.prune_schema_rows_to_allowed_relationships(rows)

    assert {row["table"] for row in pruned} == {"dak", "bill", "cheque_slip"}


def test_table_feature_prompt_prioritizes_forensic_signals_over_missing_columns(monkeypatch):
    monkeypatch.setattr(tpp_architect, "validation_context_for_table_detail", lambda _: [])

    prompt = tpp_architect.build_table_feature_prompt(
        {
            "table": "bill",
            "row_count": 100,
            "column_count": 9,
            "usable_column_count": 9,
            "columns": [
                {"column": "id", "data_type": "bigint", "key": "PK", "references": "None"},
                {"column": "amount_claimed", "data_type": "numeric", "key": "", "references": "None"},
                {"column": "amount_passed", "data_type": "numeric", "key": "", "references": "None"},
                {"column": "fk_central_vendor", "data_type": "bigint", "key": "FK", "references": "aaa_central_vendor"},
                {"column": "invoice_number", "data_type": "character varying", "key": "", "references": "None"},
                {"column": "invoice_date", "data_type": "date", "key": "", "references": "None"},
                {"column": "fis_doc_no", "data_type": "character varying", "key": "", "references": "None"},
                {"column": "gst_applicable", "data_type": "character varying", "key": "", "references": "None"},
                {"column": "fk_dak", "data_type": "bigint", "key": "FK", "references": "dak"},
            ],
            "relationship_context": [],
        }
    )

    prompt_text = json.dumps(prompt)

    assert "invoice splitting" in prompt_text
    assert "Government Accounts, Defence Audit, Payment Flow, and Forensic Analytics architect" in prompt_text
    assert "dak.fk_section IN (142, 228, 265, 383)" in prompt_text
    assert "dak, bill, cheque_slip, punching_medium, schedule3, ecs" in prompt_text
    assert "runtime_workflow_feature" in prompt_text
    assert "wf_bill_count" in prompt_text
    assert "numeric_column" in prompt_text
    assert "date_gap_days" in prompt_text
    assert "broken flow" in prompt_text
    assert "skipped stages" in prompt_text
    assert "downstream without upstream" in prompt_text
    assert "same vendor/item/context paid at different rates" in prompt_text
    assert "tax/payment detail inconsistencies" in prompt_text
    assert "do not fill the plan with is_missing features" in prompt_text
    assert "Use duplicate_key" in prompt_text
    assert "Use duplicate_normalized_key" in prompt_text
    assert "Use duplicate_distinct" in prompt_text
    assert "rolling_window_amount_sum" in prompt_text
