import ml_engine


ALL_STAGES = {"bill", "cheque_slip", "punching_medium", "schedule3", "ecs"}


def _row(**overrides):
    row = {
        "dak_id": "101",
        "dak_record_status": "V",
        "bill_count": 0,
        "bill_active_forward_count": 0,
        "bill_stopped_count": 0,
        "cheque_slip_count": 0,
        "cheque_slip_active_forward_count": 0,
        "cheque_slip_stopped_count": 0,
        "punching_medium_count": 0,
        "punching_medium_active_forward_count": 0,
        "punching_medium_stopped_count": 0,
        "schedule3_count": 0,
        "schedule3_active_forward_count": 0,
        "schedule3_stopped_count": 0,
        "ecs_count": 0,
        "ecs_active_forward_count": 0,
        "ecs_stopped_count": 0,
    }
    row.update(overrides)
    return row


def test_valid_dak_without_downstream_movement_is_reported():
    issues = ml_engine.classify_workflow_row(_row(), ALL_STAGES)

    assert issues[0]["anomaly_type"] == "dak_without_downstream_movement"
    assert issues[0]["dak_id"] == "101"
    assert issues[0]["missing_step"] == "bill"
    assert issues[0]["present_later_step"] == "dak"
    assert issues[0]["has_bill"] is False


def test_invalid_dak_without_downstream_movement_is_allowed_to_stop():
    issues = ml_engine.classify_workflow_row(_row(dak_record_status="I"), ALL_STAGES)

    assert issues == []


def test_later_stage_without_required_earlier_stage_is_reported():
    issues = ml_engine.classify_workflow_row(
        _row(schedule3_count=1, ecs_count=1),
        ALL_STAGES,
    )

    issue_types = {issue["anomaly_type"] for issue in issues}
    assert "schedule3_without_punching_medium" in issue_types
    assert not any(issue["anomaly_type"] == "ecs_without_schedule3" for issue in issues)


def test_active_bill_without_cheque_slip_is_reported():
    issues = ml_engine.classify_workflow_row(
        _row(bill_count=1, bill_active_forward_count=1),
        ALL_STAGES,
    )

    assert any(issue["anomaly_type"] == "bill_active_without_cheque_slip" for issue in issues)


def test_stopped_bill_without_downstream_is_allowed_but_later_payment_is_reported():
    stopped_without_later = ml_engine.classify_workflow_row(
        _row(bill_count=1, bill_stopped_count=1),
        ALL_STAGES,
    )
    stopped_with_later = ml_engine.classify_workflow_row(
        _row(bill_count=1, bill_stopped_count=1, cheque_slip_count=1),
        ALL_STAGES,
    )

    assert stopped_without_later == []
    assert any(
        issue["anomaly_type"] == "stopped_bill_moved_to_cheque_slip"
        for issue in stopped_with_later
    )
