import pandas as pd

from gem_ml_feature_builder import (
    Schema,
    add_derived_rule_features,
    build_feature_query,
    explain_rule_reasons,
    prepare_ml_matrix,
)


def _base_row(**overrides):
    row = {
        "gem_bill_id": 1,
        "bill_amount": 1000.0,
        "has_dak": 1,
        "has_gem_bill": 1,
        "has_gem_product": 1,
        "has_ch_booking": 1,
        "has_cheque_slip": 1,
        "has_punching_medium": 1,
        "has_schedule3": 1,
        "has_ecs": 1,
        "gem_bill_without_dak_flag": 0,
        "gem_product_without_gem_bill_flag": 0,
        "cheque_slip_without_gem_bill_flag": 0,
        "punching_medium_without_cheque_slip_flag": 0,
        "schedule3_without_punching_medium_flag": 0,
        "ecs_without_schedule3_flag": 0,
        "ecs_without_cheque_slip_flag": 0,
        "ecs_without_punching_medium_flag": 0,
        "schedule3_without_pm_flag": 0,
        "duplicate_transaction_id_flag": 0,
        "duplicate_gem_invoice_flag": 0,
        "duplicate_crac_flag": 0,
        "duplicate_order_same_crac_flag": 0,
        "duplicate_supply_order_flag": 0,
        "crac_order_mismatch_flag": 0,
        "product_total_bill_amount_mismatch_flag": 0,
        "chbooking_missing_flag": 0,
        "gst_tds_invalid_flag": 0,
        "pm_generated_without_valid_bill_flag": 0,
        "approved_but_payment_not_completed_flag": 0,
        "ecs_exists_for_rejected_bill_flag": 0,
        "record_status_r_but_dak_not_r_after_approval_flag": 0,
    }
    row.update(overrides)
    return row


def test_skipped_flow_stage_counts_as_flow_violation():
    df = add_derived_rule_features(
        pd.DataFrame([_base_row(has_punching_medium=0, schedule3_without_punching_medium_flag=1)])
    )

    assert df.loc[0, "flow_violation_count"] == 1
    assert df.loc[0, "likely_flow_fraud_flag"] == 1


def test_duplicate_identifier_flags_count_transaction_invoice_and_crac():
    df = add_derived_rule_features(
        pd.DataFrame(
            [
                _base_row(
                    duplicate_transaction_id_flag=1,
                    duplicate_gem_invoice_flag=1,
                    duplicate_crac_flag=1,
                    duplicate_order_same_crac_flag=1,
                    duplicate_supply_order_flag=1,
                )
            ]
        )
    )

    assert df.loc[0, "duplicate_violation_count"] == 5
    assert df.loc[0, "likely_duplicate_fraud_flag"] == 1


def test_crac_order_and_product_total_mismatch_count_as_amount_violations():
    df = add_derived_rule_features(
        pd.DataFrame(
            [
                _base_row(
                    crac_order_mismatch_flag=1,
                    product_total_bill_amount_mismatch_flag=1,
                )
            ]
        )
    )

    assert df.loc[0, "amount_violation_count"] == 2


def test_missing_chbooking_counts_as_budget_violation():
    df = add_derived_rule_features(pd.DataFrame([_base_row(chbooking_missing_flag=1)]))

    assert df.loc[0, "budget_violation_count"] == 1


def test_gst_tds_invalid_counts_as_gst_recovery_violation():
    df = add_derived_rule_features(pd.DataFrame([_base_row(gst_tds_invalid_flag=1)]))

    assert df.loc[0, "gst_recovery_violation_count"] == 1


def test_pm_generated_without_valid_bill_counts_as_payment_stage_violation():
    df = add_derived_rule_features(pd.DataFrame([_base_row(pm_generated_without_valid_bill_flag=1)]))

    assert df.loc[0, "pm_cheque_violation_count"] == 1
    assert df.loc[0, "likely_payment_stage_fraud_flag"] == 1


def test_approved_without_pm_or_ecs_counts_as_payment_gap():
    df = add_derived_rule_features(pd.DataFrame([_base_row(approved_but_payment_not_completed_flag=1)]))

    assert df.loc[0, "pm_cheque_violation_count"] == 1
    assert df.loc[0, "approval_violation_count"] == 1


def test_ecs_exists_for_rejected_bill_counts_as_rejection_violation():
    df = add_derived_rule_features(pd.DataFrame([_base_row(ecs_exists_for_rejected_bill_flag=1)]))

    assert df.loc[0, "rejection_violation_count"] == 1


def test_rejection_approved_but_dak_not_rejected_counts_as_rejection_violation():
    df = add_derived_rule_features(
        pd.DataFrame([_base_row(record_status_r_but_dak_not_r_after_approval_flag=1)])
    )

    assert df.loc[0, "rejection_violation_count"] == 1


def test_explain_rule_reasons_returns_human_readable_reasons():
    df = add_derived_rule_features(
        pd.DataFrame([_base_row(duplicate_crac_flag=1, chbooking_missing_flag=1)])
    )

    reasons = explain_rule_reasons(df)

    assert "duplicate GEM bill identifiers" in reasons.iloc[0]
    assert "budget/ch_booking" in reasons.iloc[0]


def test_prepare_ml_matrix_excludes_review_identifiers_and_text():
    df = add_derived_rule_features(
        pd.DataFrame(
            [
                _base_row(gem_bill_id=1, dakid_no="G123", transaction_id="TXN1", duplicate_crac_flag=0),
                _base_row(gem_bill_id=2, dakid_no="G124", transaction_id="TXN2", duplicate_crac_flag=1),
            ]
        )
    )

    matrix, feature_columns, _ = prepare_ml_matrix(df)

    assert matrix.shape[0] == 2
    assert "gem_bill_id" not in feature_columns
    assert "transaction_id" not in feature_columns
    assert "duplicate_crac_flag" in feature_columns


def test_gem_feature_query_uses_dak_section_filter_and_gem_product_link():
    schema = Schema(
        {
            "dak": {"id", "fk_section", "list_date", "dakid_no", "record_status"},
            "gem_bill": {
                "id",
                "fk_dak",
                "fk_unit",
                "transaction_id",
                "order_id",
                "supply_order_no",
                "crac_no",
                "invoice_no",
                "gem_invoice_no",
                "vendor_name",
                "vendor_pan",
                "vendor_enc_bank_account",
                "vendor_enc_bank_ifsc",
                "bill_amount",
                "amount_passed",
                "amount_to_be_paid",
                "record_status",
                "approved",
                "payment_status",
                "reason",
                "failure_reason",
                "bill_date",
                "final_bill_date",
            },
            "gem_product": {
                "id",
                "fk_gem_bill",
                "transaction_id",
                "product_code",
                "code_head",
                "project_code",
                "unit_price",
                "accepted_quantity",
                "total_value",
                "frieght_charge",
                "sgst",
                "cgst",
                "igst",
                "utgst",
                "cess",
            },
            "cheque_slip": {"id", "fk_dak", "record_status", "amount", "cheque_slip_date"},
            "punching_medium": {"id", "fk_dak", "record_status", "amount", "pm_date"},
            "schedule3": {"id", "fk_dak", "record_status", "schedule3_amount", "dp_sheet_date"},
            "ecs": {"id", "fk_dak", "record_status", "amount", "utr_date"},
        }
    )

    query = build_feature_query(schema)

    assert "pa.fk_gem_bill = gb.\"id\"" in query
    assert "gb.\"fk_dak\" = d.\"id\"" in query
    assert 'd."fk_section" IN (113, 127, 128, 129, 219, 348)' in query
    assert 'd."list_date" BETWEEN :start_date AND :end_date' in query
    assert "timing_anomaly_count" not in query
    assert "same_bank_account_vendor_count" in query
    assert "duplicate_utr_count" in query


def test_advanced_vendor_bank_and_threshold_patterns_increase_extra_risk():
    df = add_derived_rule_features(
        pd.DataFrame(
            [
                _base_row(
                    bill_amount=199500.0,
                    same_order_total_bill_amount=250000.0,
                    same_bank_account_multiple_vendors_flag=1,
                    same_vendor_multiple_bank_accounts_flag=1,
                    repeated_vendor_unit_amount_count=2,
                )
            ]
        )
    )

    assert df.loc[0, "threshold_anomaly_count"] >= 2
    assert df.loc[0, "vendor_bank_anomaly_count"] == 2
    assert df.loc[0, "extra_pattern_anomaly_count"] > 0
    assert df.loc[0, "extra_pattern_risk_score"] > 0


def test_advanced_payment_and_reprocess_patterns_are_counted():
    df = add_derived_rule_features(
        pd.DataFrame(
            [
                _base_row(
                    rejected_attempt_count=1,
                    valid_or_approved_attempt_count=1,
                    same_document_attempt_count=3,
                    duplicate_utr_count=2,
                    ecs_exists_for_rejected_bill_flag=1,
                    pm_amount_total=1000,
                    cheque_slip_amount_total=900,
                    schedule3_amount_total=900,
                    ecs_amount_total=1000,
                )
            ]
        )
    )

    assert df.loc[0, "rejected_reprocess_anomaly_count"] >= 2
    assert df.loc[0, "advanced_ecs_payment_anomaly_count"] >= 2
    assert df.loc[0, "pm_cheque_amount_mismatch_count"] == 1


def test_advanced_timing_month_end_and_product_price_patterns_are_counted():
    df = add_derived_rule_features(
        pd.DataFrame(
            [
                _base_row(
                    dak_list_date="2026-03-20",
                    bill_date="2026-03-29",
                    final_bill_date="2026-03-25",
                    product_count=2,
                    product_total_with_freight=1000,
                    product_freight_total=400,
                    product_gst_total=500,
                    product_avg_unit_price=100,
                    product_max_unit_price=800,
                    product_total_bill_amount_mismatch_flag=1,
                )
            ]
        )
    )

    assert df.loc[0, "timing_anomaly_count"] > 0
    assert df.loc[0, "month_end_anomaly_count"] == 1
    assert df.loc[0, "product_price_anomaly_count"] >= 3
