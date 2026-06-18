import re

import numpy as np
import pandas as pd


SUPPORTED_FEATURE_OPERATIONS = {
    "log",
    "rank_pct",
    "ratio_to_median",
    "ratio_to_quantile",
    "group_frequency",
    "ratio_to_group_median",
    "group_rank_pct",
    "age_days",
    "day_of_week",
    "hour",
}

AMOUNT_SOURCE = "amount"
EVENT_DATE_SOURCE = "event_date"
FEATURE_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]{1,79}$")


def get_feature_contract() -> dict:
    return {
        "feature_item_shape": {
            "name": "required stable snake_case identifier matching ^[A-Za-z][A-Za-z0-9_]{1,79}$",
            "op": "required operation from supported_operations",
            "source": "required for amount/date operations: amount or event_date",
            "group_by": "required for group_* operations: one selected context column",
            "params": "optional operation parameters, e.g. {'quantile': 0.95}",
            "reason": "required reason grounded in selected schema columns",
        },
        "supported_operations": sorted(SUPPORTED_FEATURE_OPERATIONS),
        "operation_semantics": {
            "log": "log1p(source)",
            "rank_pct": "percentile rank of source inside scanned sample",
            "ratio_to_median": "source divided by sample median of source",
            "ratio_to_quantile": "source divided by sample quantile of source; params.quantile required",
            "group_frequency": "log1p(count of rows sharing group_by value)",
            "ratio_to_group_median": "amount divided by median amount for the same group_by value",
            "group_rank_pct": "amount percentile rank within the same group_by value",
            "age_days": "days between latest event_date and row event_date",
            "day_of_week": "day-of-week number from event_date",
            "hour": "hour number from event_date timestamp",
        },
    }


def validate_feature_plan(raw_feature_plan, source: dict) -> list[dict]:
    context_columns = set(source.get("context_columns", []))
    has_date = bool(source.get("date_column"))
    validated = []
    seen_names = set()

    for raw_feature in raw_feature_plan or []:
        if not isinstance(raw_feature, dict):
            continue

        name = str(raw_feature.get("name", "")).strip()
        op = str(raw_feature.get("op", "")).strip()
        source_name = str(raw_feature.get("source", "")).strip()
        group_by = raw_feature.get("group_by")
        group_by = str(group_by).strip() if group_by else None
        reason = str(raw_feature.get("reason", "")).strip()
        params = raw_feature.get("params", {})
        params = params if isinstance(params, dict) else {}

        if not FEATURE_NAME_PATTERN.match(name) or name in seen_names:
            continue
        if op not in SUPPORTED_FEATURE_OPERATIONS:
            continue

        feature = {
            "name": name,
            "op": op,
            "reason": reason[:240],
        }

        if op in {"log", "rank_pct", "ratio_to_median", "ratio_to_quantile"}:
            if source_name != AMOUNT_SOURCE:
                continue
            feature["source"] = AMOUNT_SOURCE

        elif op in {"age_days", "day_of_week", "hour"}:
            if source_name != EVENT_DATE_SOURCE or not has_date:
                continue
            feature["source"] = EVENT_DATE_SOURCE

        elif op in {"group_frequency", "ratio_to_group_median", "group_rank_pct"}:
            if group_by not in context_columns:
                continue
            feature["group_by"] = group_by

        if op == "ratio_to_quantile":
            try:
                quantile = float(params.get("quantile"))
            except (TypeError, ValueError):
                continue
            if not 0 < quantile < 1:
                continue
            feature["params"] = {"quantile": quantile}
        elif params:
            feature["params"] = params

        validated.append(feature)
        seen_names.add(name)

    return validated


def safe_ratio(numerator: pd.Series, denominator) -> pd.Series:
    denominator = pd.Series(denominator, index=numerator.index).replace(0, np.nan)
    return numerator / denominator


def compute_feature_frame(df: pd.DataFrame, feature_plan: list[dict]) -> pd.DataFrame:
    if "amount" not in df.columns:
        return pd.DataFrame(index=df.index)

    amount = pd.to_numeric(df["amount"], errors="coerce")
    feature_data = {}

    for feature in feature_plan:
        name = feature["name"]
        op = feature["op"]
        group_by = feature.get("group_by")

        if op == "log":
            feature_data[name] = np.log1p(amount)
        elif op == "rank_pct":
            feature_data[name] = amount.rank(pct=True)
        elif op == "ratio_to_median":
            feature_data[name] = safe_ratio(amount, float(amount.dropna().median()))
        elif op == "ratio_to_quantile":
            quantile = feature.get("params", {}).get("quantile")
            feature_data[name] = safe_ratio(amount, float(amount.dropna().quantile(quantile)))
        elif op == "group_frequency":
            if group_by not in df.columns:
                continue
            feature_data[name] = np.log1p(df.groupby(group_by)[group_by].transform("size"))
        elif op == "ratio_to_group_median":
            if group_by not in df.columns:
                continue
            group_median = amount.groupby(df[group_by]).transform("median")
            feature_data[name] = safe_ratio(amount, group_median)
        elif op == "group_rank_pct":
            if group_by not in df.columns:
                continue
            feature_data[name] = amount.groupby(df[group_by]).rank(pct=True)
        elif op == "age_days":
            if "event_date" not in df.columns:
                continue
            event_dates = pd.to_datetime(df["event_date"], errors="coerce")
            feature_data[name] = (event_dates.max() - event_dates).dt.total_seconds() / 86400
        elif op == "day_of_week":
            if "event_date" not in df.columns:
                continue
            feature_data[name] = pd.to_datetime(df["event_date"], errors="coerce").dt.dayofweek
        elif op == "hour":
            if "event_date" not in df.columns:
                continue
            feature_data[name] = pd.to_datetime(df["event_date"], errors="coerce").dt.hour

    return pd.DataFrame(feature_data).replace([np.inf, -np.inf], np.nan)
