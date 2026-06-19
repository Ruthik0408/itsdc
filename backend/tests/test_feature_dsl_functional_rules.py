import pandas as pd

from feature_dsl import compute_feature_frame, validate_feature_plan


def test_functional_rule_features_are_computed_as_binary_flags():
    df = pd.DataFrame(
        {
            "amount": [1000, 500],
            "invoice_date": ["2026-02-10", "2026-01-05"],
            "dak_bill_date": ["2026-02-01", "2026-01-10"],
            "payment_mode": ["CMP", "CHEQUE"],
            "fk_central_beneficiary": [None, "42"],
            "fk_central_vendor": ["9", None],
            "make_type": ["", "MII"],
            "amount_passed": [1200, 400],
            "amount_claimed": [1000, 500],
            "fis_doc_no": ["291234", "181234"],
            "supply_order_no": [None, "SO-1"],
            "contract_agreement_no": ["", "CA-1"],
            "cancelled": [True, False],
        }
    )
    source = {
        "context_columns": [
            "invoice_date",
            "dak_bill_date",
            "payment_mode",
            "fk_central_beneficiary",
            "fk_central_vendor",
            "make_type",
            "amount_passed",
            "amount_claimed",
            "fis_doc_no",
            "supply_order_no",
            "contract_agreement_no",
            "cancelled",
        ],
        "date_column": "invoice_date",
    }
    raw_plan = [
        {
            "name": "invoice_after_bill",
            "op": "date_after",
            "left": "invoice_date",
            "right": "dak_bill_date",
            "reason": "Invoice date after DAK bill date is inconsistent.",
        },
        {
            "name": "cmp_missing_beneficiary",
            "op": "missing_when_equals",
            "condition_column": "payment_mode",
            "value": "CMP",
            "column": "fk_central_beneficiary",
            "reason": "CMP payments require a beneficiary.",
        },
        {
            "name": "vendor_missing_make_type",
            "op": "missing_when_present",
            "condition_column": "fk_central_vendor",
            "column": "make_type",
            "reason": "Vendor payments require make type.",
        },
        {
            "name": "passed_gt_claimed",
            "op": "numeric_gt",
            "column": "amount_passed",
            "right": "amount_claimed",
            "reason": "Passed amount should not exceed claimed amount.",
        },
        {
            "name": "gem_prefix",
            "op": "starts_with",
            "column": "fis_doc_no",
            "value": "29",
            "reason": "Gem online documents should use the 29 prefix.",
        },
        {
            "name": "missing_order_and_contract",
            "op": "all_missing",
            "columns": ["supply_order_no", "contract_agreement_no"],
            "reason": "Supply order and contract cannot both be blank.",
        },
        {
            "name": "cancelled_flag",
            "op": "equals",
            "column": "cancelled",
            "value": "true",
            "reason": "Cancelled rows are high risk when still present in payment flow.",
        },
    ]

    plan = validate_feature_plan(raw_plan, source)
    features = compute_feature_frame(df, plan)

    assert features.to_dict("list") == {
        "invoice_after_bill": [1.0, 0.0],
        "cmp_missing_beneficiary": [1.0, 0.0],
        "vendor_missing_make_type": [1.0, 0.0],
        "passed_gt_claimed": [1.0, 0.0],
        "gem_prefix": [1.0, 0.0],
        "missing_order_and_contract": [1.0, 0.0],
        "cancelled_flag": [1.0, 0.0],
    }


def test_date_in_future_uses_current_day_boundary(monkeypatch):
    class FixedTimestamp(pd.Timestamp):
        @classmethod
        def utcnow(cls):
            return pd.Timestamp("2026-06-18 09:00:00")

    monkeypatch.setattr(pd, "Timestamp", FixedTimestamp)
    df = pd.DataFrame({"amount": [1, 1], "bill_date": ["2026-06-19", "2026-06-18"]})
    plan = validate_feature_plan(
        [
            {
                "name": "bill_date_future",
                "op": "date_in_future",
                "column": "bill_date",
                "reason": "Future bill dates are invalid.",
            }
        ],
        {"context_columns": ["bill_date"], "date_column": "bill_date"},
    )

    features = compute_feature_frame(df, plan)

    assert features["bill_date_future"].tolist() == [1.0, 0.0]


def test_duplicate_distinct_flags_same_invoice_across_different_daks():
    df = pd.DataFrame(
        {
            "amount": [100, 100, 100, 100],
            "fk_central_vendor": [10, 10, 10, 20],
            "invoice_number": ["INV-1", "INV-1", "INV-2", "INV-1"],
            "fk_dak": [501, 502, 503, 504],
        }
    )
    plan = validate_feature_plan(
        [
            {
                "name": "same_vendor_invoice_across_daks",
                "op": "duplicate_distinct",
                "columns": ["fk_central_vendor", "invoice_number"],
                "distinct_column": "fk_dak",
                "reason": "Same vendor and invoice number appear across different DAK IDs.",
            }
        ],
        {
            "context_columns": ["fk_central_vendor", "invoice_number", "fk_dak"],
            "date_column": None,
        },
    )

    features = compute_feature_frame(df, plan)

    assert features["same_vendor_invoice_across_daks"].tolist() == [1.0, 1.0, 0.0, 0.0]


def test_duplicate_normalized_key_ignores_invoice_formatting():
    df = pd.DataFrame(
        {
            "amount": [100, 100, 100, 100],
            "fk_central_vendor": [10, 10, 10, 10],
            "invoice_number": ["INV-001", " inv 001 ", "INV/002", None],
        }
    )
    plan = validate_feature_plan(
        [
            {
                "name": "same_vendor_invoice_normalized",
                "op": "duplicate_normalized_key",
                "columns": ["fk_central_vendor", "invoice_number"],
                "reason": "Same vendor invoice appears with formatting changes.",
            }
        ],
        {
            "context_columns": ["fk_central_vendor", "invoice_number"],
            "date_column": None,
        },
    )

    features = compute_feature_frame(df, plan)

    assert features["same_vendor_invoice_normalized"].tolist() == [1.0, 1.0, 0.0, 0.0]


def test_rolling_window_features_find_nearby_split_payments():
    df = pd.DataFrame(
        {
            "amount": [49000, 48000, 120000, 3000],
            "event_date": ["2026-06-01", "2026-06-05", "2026-06-30", "2026-06-06"],
            "fk_central_vendor": [10, 10, 10, 20],
            "reference_no": ["SO-7", "SO 7", "SO-7", "SO-7"],
        }
    )
    plan = validate_feature_plan(
        [
            {
                "name": "vendor_ref_7d_count",
                "op": "rolling_window_count",
                "columns": ["fk_central_vendor", "reference_no"],
                "params": {"window_days": 7},
                "reason": "Counts same vendor reference rows around the payment date.",
            },
            {
                "name": "vendor_ref_7d_amount",
                "op": "rolling_window_amount_sum",
                "columns": ["fk_central_vendor", "reference_no"],
                "params": {"window_days": 7},
                "reason": "Sums same vendor reference amounts around the payment date.",
            },
        ],
        {
            "context_columns": ["fk_central_vendor", "reference_no"],
            "date_column": "event_date",
        },
    )

    features = compute_feature_frame(df, plan)

    assert features["vendor_ref_7d_count"].tolist() == [2.0, 2.0, 1.0, 1.0]
    assert features["vendor_ref_7d_amount"].tolist() == [97000.0, 97000.0, 120000.0, 3000.0]
