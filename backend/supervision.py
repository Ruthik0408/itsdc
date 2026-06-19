"""Supervision feedback loop for the Tulip 2.0 anomaly engine.

When a reviewer accepts or rejects an anomaly, the case is appended (never
overwritten) to a supervision log. Each appended block carries a
machine-readable JSON payload of the engineered feature values so that later
scans can:

1. Reload the accepted feature signatures per table.
2. Give "added focus" to rows close to those signatures, by boosting their
   anomaly score and promoting near-matches that the unsupervised detector
   would otherwise miss.
3. Reload rejected feature signatures per table and suppress close matches that
   were previously marked as false positives.

The Isolation Forest and autoencoder stay unsupervised; supervision only
re-ranks, selectively promotes candidates that resemble confirmed cases, and
selectively suppresses candidates that resemble rejected cases.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


BACKEND_DIR = Path(__file__).resolve().parent
POSITIVE_SUPERVISION_FILE = BACKEND_DIR / "positive_supervision.md"
NEGATIVE_SUPERVISION_FILE = BACKEND_DIR / "negative_supervision.md"
ARCHITECTURE_GUIDE_FILE = BACKEND_DIR / "tpp_anomaly_guide.md"

# Maximum score uplift (in the same 0-100 scale as isolation_score) applied to
# a row that sits exactly on a confirmed-anomaly signature.
SUPERVISION_BOOST_MAX = 8.0
# Maximum score reduction applied to a row that sits exactly on a rejected
# false-positive signature.
SUPERVISION_PENALTY_MAX = 12.0
# Proximity (0-1) at or above which an unflagged row is promoted to an anomaly.
SUPERVISION_PROMOTE_PROXIMITY = 0.6
# Proximity (0-1) at or above which a row matching rejected feedback is removed,
# unless it also matches an accepted signature strongly enough.
SUPERVISION_SUPPRESS_PROXIMITY = 0.65
# How many accepted feature snapshots to keep in memory per table.
MAX_ACCEPTED_SIGNATURES_PER_TABLE = 200
# Bound the architecture / supervision text fed to the LLM prompt.
MAX_SUPERVISION_CONTEXT_CHARS = 6000

_JSON_BLOCK_PATTERN = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _coerce_feature_values(raw) -> dict[str, float]:
    """Keep only finite numeric feature values, keyed by feature name."""
    values: dict[str, float] = {}
    if not isinstance(raw, dict):
        return values
    for name, value in raw.items():
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if np.isfinite(number):
            values[str(name)] = number
    return values


def _append_supervision_record(
    record: dict,
    path: Path,
    decision: str,
    header: str,
) -> None:
    """Append one reviewed anomaly to a supervision file.

    Append-only: the file is opened in append mode and existing content is
    never rewritten. ``record`` is expected to contain the persisted anomaly
    fields; ``engineered_feature_values`` drives future supervision focus.
    """
    transaction_id = str(record.get("transaction_id", "unknown"))
    table_name = str(record.get("table_name", "unknown"))
    feature_values = _coerce_feature_values(record.get("engineered_feature_values"))

    payload = {
        "transaction_id": transaction_id,
        "table_name": table_name,
        "source_record_id": str(record.get("source_record_id", transaction_id)),
        "anomaly_score": record.get("anomaly_score"),
        "isolation_score": record.get("isolation_score"),
        "autoencoder_score": record.get("autoencoder_score"),
        "engineered_feature_values": feature_values,
        "reviewer_feedback": str(record.get("reviewer_feedback") or "")[:200],
        "accepted_at": _now_iso(),
    }

    explanation = str(record.get("explanation") or "No explanation recorded.").strip()
    block = (
        f"\n## {decision.upper()} {payload['accepted_at']} — {transaction_id}\n"
        f"- table: {table_name}\n"
        f"- source_record_id: {payload['source_record_id']}\n"
        f"- anomaly_score: {payload['anomaly_score']}"
        f" (isolation {payload['isolation_score']} / autoencoder {payload['autoencoder_score']})\n"
        f"- reviewer_feedback: {payload['reviewer_feedback'] or '(none)'}\n"
        f"- explanation: {explanation}\n"
        f"```json\n{json.dumps(payload)}\n```\n"
    )

    is_new_file = not path.exists()
    with open(path, "a", encoding="utf-8") as handle:
        if is_new_file:
            handle.write(header)
        handle.write(block)


def append_positive_supervision(record: dict, path: Path = POSITIVE_SUPERVISION_FILE) -> None:
    """Append one accepted anomaly to the positive supervision file."""
    _append_supervision_record(
        record,
        path=path,
        decision="accepted",
        header=(
            "# Tulip 2.0 Positive Supervision Log\n\n"
            "Append-only record of reviewer-accepted anomalies. Each block feeds the\n"
            "next scan so the Isolation Forest and autoencoder give added focus to\n"
            "confirmed patterns. Do not edit or reorder existing entries.\n"
        ),
    )


def append_negative_supervision(record: dict, path: Path = NEGATIVE_SUPERVISION_FILE) -> None:
    """Append one rejected anomaly to the negative supervision file."""
    _append_supervision_record(
        record,
        path=path,
        decision="rejected",
        header=(
            "# Tulip 2.0 Negative Supervision Log\n\n"
            "Append-only record of reviewer-rejected anomalies. Each block feeds the\n"
            "next scan so rows matching false-positive patterns are down-ranked or\n"
            "suppressed. Do not edit or reorder existing entries.\n"
        ),
    )


def parse_supervision(path: Path) -> list[dict]:
    """Parse all reviewed entries from a supervision file (append-only safe)."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    entries: list[dict] = []
    for match in _JSON_BLOCK_PATTERN.finditer(text):
        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            entries.append(payload)
    return entries


def parse_positive_supervision(path: Path = POSITIVE_SUPERVISION_FILE) -> list[dict]:
    """Parse all accepted entries from the supervision file (append-only safe)."""
    return parse_supervision(path)


def parse_negative_supervision(path: Path = NEGATIVE_SUPERVISION_FILE) -> list[dict]:
    """Parse all rejected entries from the supervision file (append-only safe)."""
    return parse_supervision(path)


def load_accepted_signatures(table_name: str, path: Path = POSITIVE_SUPERVISION_FILE) -> list[dict[str, float]]:
    """Return engineered feature dicts for accepted anomalies of one table."""
    signatures: list[dict[str, float]] = []
    for entry in parse_supervision(path):
        if entry.get("table_name") != table_name:
            continue
        values = _coerce_feature_values(entry.get("engineered_feature_values"))
        if values:
            signatures.append(values)
    if len(signatures) > MAX_ACCEPTED_SIGNATURES_PER_TABLE:
        signatures = signatures[-MAX_ACCEPTED_SIGNATURES_PER_TABLE:]
    return signatures


def load_rejected_signatures(table_name: str, path: Path = NEGATIVE_SUPERVISION_FILE) -> list[dict[str, float]]:
    """Return engineered feature dicts for rejected anomalies of one table."""
    signatures: list[dict[str, float]] = []
    for entry in parse_supervision(path):
        if entry.get("table_name") != table_name:
            continue
        values = _coerce_feature_values(entry.get("engineered_feature_values"))
        if values:
            signatures.append(values)
    if len(signatures) > MAX_ACCEPTED_SIGNATURES_PER_TABLE:
        signatures = signatures[-MAX_ACCEPTED_SIGNATURES_PER_TABLE:]
    return signatures


def _signatures_to_matrix(
    signatures: list[dict[str, float]],
    feature_names: list[str],
    scaler,
) -> np.ndarray | None:
    """Align accepted signatures to the current feature order and scale them.

    Missing features fall back to the scaler centre (median) so they map to ~0
    in scaled space. Returns the scaled matrix, or None when nothing aligns.
    """
    if not signatures or not feature_names:
        return None
    centers = getattr(scaler, "center_", None)
    if centers is None:
        centers = np.zeros(len(feature_names), dtype=float)
    raw_rows = []
    for signature in signatures:
        if not any(name in signature for name in feature_names):
            continue
        row = [float(signature.get(name, centers[idx])) for idx, name in enumerate(feature_names)]
        raw_rows.append(row)
    if not raw_rows:
        return None
    raw_matrix = np.asarray(raw_rows, dtype=float)
    try:
        return scaler.transform(raw_matrix)
    except Exception:
        return None


def compute_supervision_boost(
    scaled_features: np.ndarray,
    feature_names: list[str],
    signatures: list[dict[str, float]],
    scaler,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (boost, proximity) arrays for every scored row.

    ``proximity`` is a 0-1 closeness to the nearest accepted signature.
    ``boost`` scales that proximity by SUPERVISION_BOOST_MAX. Both arrays are
    zero when there are no accepted signatures.
    """
    row_count = len(scaled_features)
    zeros = np.zeros(row_count, dtype=float)
    if row_count == 0:
        return zeros, zeros

    accepted_matrix = _signatures_to_matrix(signatures, feature_names, scaler)
    if accepted_matrix is None or len(accepted_matrix) == 0:
        return zeros, zeros

    # Nearest accepted-signature distance for each scored row.
    diffs = scaled_features[:, None, :] - accepted_matrix[None, :, :]
    distances = np.linalg.norm(diffs, axis=2)
    nearest = distances.min(axis=1)

    sigma = float(np.median(nearest))
    if not np.isfinite(sigma) or sigma <= 0:
        sigma = 1.0
    sigma = max(sigma, 1.0)

    proximity = np.exp(-(nearest ** 2) / (2.0 * sigma ** 2))
    boost = SUPERVISION_BOOST_MAX * proximity
    return boost, proximity


def compute_supervision_penalty(
    scaled_features: np.ndarray,
    feature_names: list[str],
    signatures: list[dict[str, float]],
    scaler,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (penalty, proximity) arrays for rejected false-positive matches."""
    _, proximity = compute_supervision_boost(scaled_features, feature_names, signatures, scaler)
    penalty = SUPERVISION_PENALTY_MAX * proximity
    return penalty, proximity


def _read_capped(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8").strip()
    if len(text) > MAX_SUPERVISION_CONTEXT_CHARS:
        text = text[-MAX_SUPERVISION_CONTEXT_CHARS:]
    return text


def load_supervision_context_text(
    guide_path: Path = ARCHITECTURE_GUIDE_FILE,
    supervision_path: Path = POSITIVE_SUPERVISION_FILE,
) -> str:
    """Architecture guide + positive supervision text fed to the LLM at scan time."""
    sections = []
    guide = _read_capped(guide_path)
    if guide:
        sections.append("ARCHITECTURE GUIDE (tpp_anomaly_guide.md):\n" + guide)
    supervision = _read_capped(supervision_path)
    if supervision:
        sections.append("CONFIRMED ANOMALY PATTERNS (positive_supervision.md):\n" + supervision)
    return "\n\n".join(sections)
