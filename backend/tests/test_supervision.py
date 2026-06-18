import numpy as np
import pytest

import supervision


class StubScaler:
    """Duck-typed RobustScaler replacement so tests avoid the sklearn dependency."""

    def __init__(self, center, scale):
        self.center_ = np.asarray(center, dtype=float)
        self.scale_ = np.asarray(scale, dtype=float)

    def transform(self, matrix):
        return (np.asarray(matrix, dtype=float) - self.center_) / self.scale_


def _accept_record(transaction_id, table, features, score=12.0):
    return {
        "transaction_id": transaction_id,
        "table_name": table,
        "source_record_id": transaction_id.split(":")[-1],
        "anomaly_score": score,
        "isolation_score": score,
        "autoencoder_score": None,
        "engineered_feature_values": features,
        "explanation": f"Confirmed anomaly {transaction_id}.",
        "reviewer_feedback": "looks fraudulent",
    }


def test_append_is_append_only(tmp_path):
    path = tmp_path / "positive_supervision.md"

    supervision.append_positive_supervision(_accept_record("bill:1", "bill", {"a": 5.0, "b": 5.0}), path=path)
    first = path.read_text(encoding="utf-8")
    supervision.append_positive_supervision(_accept_record("bill:2", "bill", {"a": 9.0, "b": 1.0}), path=path)
    second = path.read_text(encoding="utf-8")

    # Append-only: the first entry is preserved verbatim and the file only grows.
    assert second.startswith(first)
    assert "bill:1" in second
    assert "bill:2" in second
    assert second.count("## ACCEPTED") == 2
    # Header written exactly once.
    assert second.count("# Tulip 2.0 Positive Supervision Log") == 1


def test_parse_round_trip_and_table_filter(tmp_path):
    path = tmp_path / "positive_supervision.md"
    supervision.append_positive_supervision(_accept_record("bill:1", "bill", {"a": 5.0, "b": 5.0}), path=path)
    supervision.append_positive_supervision(_accept_record("dak:7", "dak", {"x": 2.0}), path=path)

    entries = supervision.parse_positive_supervision(path)
    assert {e["transaction_id"] for e in entries} == {"bill:1", "dak:7"}

    bill_sigs = supervision.load_accepted_signatures("bill", path=path)
    assert bill_sigs == [{"a": 5.0, "b": 5.0}]
    assert supervision.load_accepted_signatures("dak", path=path) == [{"x": 2.0}]
    assert supervision.load_accepted_signatures("missing", path=path) == []


def test_negative_supervision_round_trip_and_table_filter(tmp_path):
    path = tmp_path / "negative_supervision.md"
    supervision.append_negative_supervision(_accept_record("bill:1", "bill", {"a": 5.0}), path=path)
    supervision.append_negative_supervision(_accept_record("dak:7", "dak", {"x": 2.0}), path=path)

    entries = supervision.parse_negative_supervision(path)
    assert {e["transaction_id"] for e in entries} == {"bill:1", "dak:7"}
    assert supervision.load_rejected_signatures("bill", path=path) == [{"a": 5.0}]
    assert supervision.load_rejected_signatures("missing", path=path) == []


def test_compute_boost_focuses_on_accepted_pattern():
    feature_names = ["a", "b"]
    scaler = StubScaler(center=[0.0, 0.0], scale=[1.0, 1.0])  # identity
    signatures = [{"a": 5.0, "b": 5.0}]

    # Row 0 sits on the accepted signature; row 1 is far away.
    scaled_features = np.array([[5.0, 5.0], [0.0, 0.0]])
    boost, proximity = supervision.compute_supervision_boost(
        scaled_features, feature_names, signatures, scaler
    )

    assert proximity[0] == pytest.approx(1.0, abs=1e-6)
    assert proximity[0] > proximity[1]
    assert boost[0] > boost[1]
    assert boost[0] == pytest.approx(supervision.SUPERVISION_BOOST_MAX, rel=1e-6)
    # The matched row clears the promotion bar; the distant row does not.
    assert proximity[0] >= supervision.SUPERVISION_PROMOTE_PROXIMITY


def test_compute_penalty_focuses_on_rejected_pattern():
    feature_names = ["a", "b"]
    scaler = StubScaler(center=[0.0, 0.0], scale=[1.0, 1.0])
    signatures = [{"a": 5.0, "b": 5.0}]

    scaled_features = np.array([[5.0, 5.0], [0.0, 0.0]])
    penalty, proximity = supervision.compute_supervision_penalty(
        scaled_features, feature_names, signatures, scaler
    )

    assert proximity[0] == pytest.approx(1.0, abs=1e-6)
    assert penalty[0] > penalty[1]
    assert penalty[0] == pytest.approx(supervision.SUPERVISION_PENALTY_MAX, rel=1e-6)
    assert proximity[0] >= supervision.SUPERVISION_SUPPRESS_PROXIMITY


def test_compute_boost_no_signatures_is_zero():
    feature_names = ["a"]
    scaler = StubScaler(center=[0.0], scale=[1.0])
    scaled_features = np.array([[1.0], [2.0]])
    boost, proximity = supervision.compute_supervision_boost(scaled_features, feature_names, [], scaler)
    assert np.all(boost == 0)
    assert np.all(proximity == 0)


def test_missing_feature_falls_back_to_center():
    feature_names = ["a", "b"]
    # Center b=4 so a signature lacking "b" maps b->4 (distance 0 on b axis).
    scaler = StubScaler(center=[0.0, 4.0], scale=[1.0, 1.0])
    signatures = [{"a": 3.0}]  # "b" missing -> uses center 4.0 -> scales to 0
    # Current row raw [3, 4] scales to [3, 0]; accepted signature also scales to [3, 0].
    scaled_features = np.array([[3.0, 0.0]])
    boost, proximity = supervision.compute_supervision_boost(
        scaled_features, feature_names, signatures, scaler
    )
    assert proximity[0] == pytest.approx(1.0, abs=1e-6)


def test_context_text_combines_guide_and_supervision(tmp_path):
    guide = tmp_path / "anomaly_guide.md"
    supervision_file = tmp_path / "positive_supervision.md"
    guide.write_text("# Guide\nArchitecture intent here.", encoding="utf-8")
    supervision.append_positive_supervision(_accept_record("bill:1", "bill", {"a": 1.0}), path=supervision_file)

    text = supervision.load_supervision_context_text(
        guide_path=guide, supervision_path=supervision_file
    )
    assert "ARCHITECTURE GUIDE" in text
    assert "CONFIRMED ANOMALY PATTERNS" in text
    assert "Architecture intent here." in text
    assert "bill:1" in text


def test_context_text_empty_when_no_files(tmp_path):
    assert supervision.load_supervision_context_text(
        guide_path=tmp_path / "none.md", supervision_path=tmp_path / "none2.md"
    ) == ""
