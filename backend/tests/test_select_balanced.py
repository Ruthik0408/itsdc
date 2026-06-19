import ml_engine

Anomaly = ml_engine.Anomaly


def _model_anomaly(i, score):
    return Anomaly(
        transaction_id=f"bill:{i}",
        table_name="bill",
        source_record_id=str(i),
        score=score,
        context={"isolation_score": score},  # no detector_type -> model anomaly
    )


def _feature_anomaly(i, score, feature):
    return Anomaly(
        transaction_id=f"bill:{feature}:{i}",
        table_name="bill",
        source_record_id=str(i),
        score=score,
        context={
            "isolation_score": score,
            "row_top_feature_contributions": [{"feature": feature, "contribution": 0.9}],
        },
    )


def _workflow_anomaly(i, score=100.0):
    return Anomaly(
        transaction_id=f"workflow:missing:{i}",
        table_name="workflow_process",
        source_record_id=str(i),
        score=score,
        context={"detector_type": "workflow_process"},
    )


def test_model_anomalies_reserved_against_workflow_flood():
    # 10 model anomalies drowned by 1000 fixed-score workflow anomalies.
    model = [_model_anomaly(i, score=20 + i) for i in range(10)]
    workflow = [_workflow_anomaly(i) for i in range(1000)]
    budget = 100

    chosen = ml_engine.select_balanced_anomalies(model + workflow, budget)

    assert len(chosen) == budget
    kept_model = [a for a in chosen if not a.context.get("detector_type")]
    # All 10 model anomalies survive despite the workflow flood.
    assert len(kept_model) == 10


def test_budget_backfills_when_few_model_anomalies():
    model = [_model_anomaly(i, score=50) for i in range(3)]
    workflow = [_workflow_anomaly(i) for i in range(1000)]
    budget = 100

    chosen = ml_engine.select_balanced_anomalies(model + workflow, budget)

    assert len(chosen) == budget
    kept_model = [a for a in chosen if not a.context.get("detector_type")]
    kept_workflow = [a for a in chosen if a.context.get("detector_type")]
    assert len(kept_model) == 3          # only 3 exist
    assert len(kept_workflow) == 97       # leftover budget went to workflow


def test_returns_all_when_under_budget():
    items = [_model_anomaly(i, score=i) for i in range(5)] + [_workflow_anomaly(0)]
    chosen = ml_engine.select_balanced_anomalies(items, budget=100)
    assert len(chosen) == len(items)
    # Sorted by score descending.
    scores = [a.score for a in chosen]
    assert scores == sorted(scores, reverse=True)


def test_limits_anomalies_to_two_per_primary_feature():
    items = [
        _feature_anomaly(1, 99, "wf_bill_count"),
        _feature_anomaly(2, 98, "wf_bill_count"),
        _feature_anomaly(3, 97, "wf_bill_count"),
        _feature_anomaly(4, 96, "wf_ecs_count"),
        _feature_anomaly(5, 95, "wf_ecs_count"),
        _feature_anomaly(6, 94, "wf_ecs_count"),
    ]

    chosen = ml_engine.limit_anomalies_per_feature(items, max_per_feature=2)

    assert [item.source_record_id for item in chosen] == ["1", "2", "4", "5"]
