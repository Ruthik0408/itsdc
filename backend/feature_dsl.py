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
    "is_missing",
    "missing_when_equals",
    "missing_when_present",
    "date_after",
    "date_in_future",
    "numeric_gt",
    "numeric_lt",
    "starts_with",
    "equals",
    "all_missing",
    "duplicate_key",
    "duplicate_distinct",
    "duplicate_normalized_key",
    "rolling_window_amount_sum",
    "rolling_window_count",
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
            "column": "required for single-column validation/rule operations",
            "left": "left column for two-column validation/rule comparisons",
            "right": "right column for two-column validation/rule comparisons",
            "condition_column": "column used as the condition for conditional validation/rule operations",
            "value": "literal value for equality/prefix/numeric validation/rule operations",
            "columns": "required for multi-column validation/rule operations",
            "distinct_column": "required for duplicate_distinct to count different values inside a duplicate key",
            "params": "optional operation parameters, e.g. {'quantile': 0.95} or {'window_days': 7}",
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
            "is_missing": "1 when column is null/blank, else 0",
            "missing_when_equals": "1 when condition_column equals value and column is missing, else 0",
            "missing_when_present": "1 when condition_column is present and column is missing, else 0",
            "date_after": "1 when left date is after right date, else 0",
            "date_in_future": "1 when column date is after current date, else 0",
            "numeric_gt": "1 when column is greater than numeric literal or right column, else 0",
            "numeric_lt": "1 when column is less than numeric literal or right column, else 0",
            "starts_with": "1 when column text starts with the configured value/prefix, else 0",
            "equals": "1 when column equals the configured value, else 0",
            "all_missing": "1 when every listed column is null/blank, else 0",
            "duplicate_key": "1 when another scanned row has the same values for columns, else 0",
            "duplicate_distinct": "1 when rows sharing columns contain more than one distinct distinct_column value, else 0",
            "duplicate_normalized_key": "1 when another scanned row has the same normalized text key after removing punctuation/case differences, else 0",
            "rolling_window_amount_sum": "sum of amount for rows sharing normalized columns within +/- params.window_days of event_date",
            "rolling_window_count": "count of rows sharing normalized columns within +/- params.window_days of event_date",
        },
    }


def _selected_columns(source: dict) -> set[str]:
    return set(source.get("context_columns", [])) | {AMOUNT_SOURCE, EVENT_DATE_SOURCE}


def validate_feature_plan(raw_feature_plan, source: dict) -> list[dict]:
    context_columns = set(source.get("context_columns", []))
    selectable_columns = _selected_columns(source)
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
        column = raw_feature.get("column")
        column = str(column).strip() if column else None
        left = raw_feature.get("left")
        left = str(left).strip() if left else None
        right = raw_feature.get("right")
        right = str(right).strip() if right else None
        condition_column = raw_feature.get("condition_column")
        condition_column = str(condition_column).strip() if condition_column else None
        distinct_column = raw_feature.get("distinct_column")
        distinct_column = str(distinct_column).strip() if distinct_column else None
        reason = str(raw_feature.get("reason", "")).strip()
        value = raw_feature.get("value")
        columns = raw_feature.get("columns", [])
        columns = [str(item).strip() for item in columns if str(item).strip()] if isinstance(columns, list) else []
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

        elif op in {"is_missing", "date_in_future", "starts_with", "equals"}:
            if column not in selectable_columns:
                continue
            feature["column"] = column

        elif op == "all_missing":
            if not columns or any(item not in selectable_columns for item in columns):
                continue
            feature["columns"] = columns[:8]

        elif op in {
            "duplicate_key",
            "duplicate_distinct",
            "duplicate_normalized_key",
            "rolling_window_amount_sum",
            "rolling_window_count",
        }:
            if not columns or any(item not in selectable_columns for item in columns):
                continue
            feature["columns"] = columns[:8]
            if op == "duplicate_distinct":
                if distinct_column not in selectable_columns:
                    continue
                feature["distinct_column"] = distinct_column
            if op in {"rolling_window_amount_sum", "rolling_window_count"} and not has_date:
                continue

        elif op in {"missing_when_equals", "missing_when_present"}:
            if column not in selectable_columns or condition_column not in selectable_columns:
                continue
            feature["column"] = column
            feature["condition_column"] = condition_column

        elif op == "date_after":
            if left not in selectable_columns or right not in selectable_columns:
                continue
            feature["left"] = left
            feature["right"] = right

        elif op in {"numeric_gt", "numeric_lt"}:
            if column not in selectable_columns:
                continue
            feature["column"] = column
            if right:
                if right not in selectable_columns:
                    continue
                feature["right"] = right

        if op == "ratio_to_quantile":
            try:
                quantile = float(params.get("quantile"))
            except (TypeError, ValueError):
                continue
            if not 0 < quantile < 1:
                continue
            feature["params"] = {"quantile": quantile}
        elif op in {"missing_when_equals", "starts_with", "equals"}:
            if value is None or value == "":
                continue
            feature["value"] = str(value)
        elif op in {"numeric_gt", "numeric_lt"} and not right:
            try:
                feature["value"] = float(value)
            except (TypeError, ValueError):
                continue
        elif op in {"rolling_window_amount_sum", "rolling_window_count"}:
            try:
                window_days = int(params.get("window_days", 7))
            except (TypeError, ValueError):
                continue
            if not 1 <= window_days <= 365:
                continue
            feature["params"] = {"window_days": window_days}
        elif params:
            feature["params"] = params

        validated.append(feature)
        seen_names.add(name)

    return validated


def _is_missing(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype("string").str.strip().isin(["", "None", "nan", "<NA>"]).fillna(True)


def _equals(series: pd.Series, value: str) -> pd.Series:
    return series.astype("string").str.strip().str.upper() == str(value).strip().upper()


def _to_binary(mask: pd.Series) -> pd.Series:
    return mask.fillna(False).astype(float)


def _missing_columns_mask(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    masks = [_is_missing(df[column]) for column in columns if column in df.columns]
    if not masks:
        return pd.Series(False, index=df.index)
    mask = masks[0]
    for next_mask in masks[1:]:
        mask = mask & next_mask
    return mask


def _complete_key_mask(df: pd.DataFrame, columns: list[str]) -> pd.Series:
    masks = [~_is_missing(df[column]) for column in columns if column in df.columns]
    if not masks:
        return pd.Series(False, index=df.index)
    mask = masks[0]
    for next_mask in masks[1:]:
        mask = mask & next_mask
    return mask


def _normalized_key_frame(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    normalized = {}
    for column in columns:
        normalized[column] = (
            df[column]
            .astype("string")
            .str.upper()
            .str.replace(r"[^A-Z0-9]+", "", regex=True)
            .replace("", pd.NA)
        )
    return pd.DataFrame(normalized, index=df.index)


def _normalized_complete_key_mask(normalized_keys: pd.DataFrame) -> pd.Series:
    if normalized_keys.empty:
        return pd.Series(False, index=normalized_keys.index)
    return ~normalized_keys.isna().any(axis=1)


def _combined_normalized_key(normalized_keys: pd.DataFrame) -> pd.Series:
    complete_key = _normalized_complete_key_mask(normalized_keys)
    combined = normalized_keys.fillna("").agg("\x1f".join, axis=1)
    return combined.where(complete_key)


def _rolling_window_by_key(
    df: pd.DataFrame,
    columns: list[str],
    amount: pd.Series,
    window_days: int,
    aggregation: str,
) -> pd.Series:
    if "event_date" not in df.columns:
        return pd.Series(np.nan, index=df.index)

    normalized_keys = _normalized_key_frame(df, columns)
    keys = _combined_normalized_key(normalized_keys)
    event_dates = pd.to_datetime(df["event_date"], errors="coerce")
    values = pd.Series(np.nan, index=df.index, dtype="float64")
    window = pd.Timedelta(days=window_days)

    work = pd.DataFrame(
        {
            "_key": keys,
            "_event_date": event_dates,
            "_amount": amount,
        },
        index=df.index,
    ).dropna(subset=["_key", "_event_date"])

    for _, group in work.groupby("_key", sort=False):
        dates = group["_event_date"]
        for index, date_value in dates.items():
            in_window = (dates - date_value).abs() <= window
            if aggregation == "sum":
                values.at[index] = group.loc[in_window, "_amount"].sum(min_count=1)
            else:
                values.at[index] = float(in_window.sum())

    return values


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
        elif op == "is_missing":
            column = feature.get("column")
            if column not in df.columns:
                continue
            feature_data[name] = _to_binary(_is_missing(df[column]))
        elif op == "missing_when_equals":
            column = feature.get("column")
            condition_column = feature.get("condition_column")
            if column not in df.columns or condition_column not in df.columns:
                continue
            feature_data[name] = _to_binary(_equals(df[condition_column], feature.get("value", "")) & _is_missing(df[column]))
        elif op == "missing_when_present":
            column = feature.get("column")
            condition_column = feature.get("condition_column")
            if column not in df.columns or condition_column not in df.columns:
                continue
            feature_data[name] = _to_binary(~_is_missing(df[condition_column]) & _is_missing(df[column]))
        elif op == "date_after":
            left = feature.get("left")
            right = feature.get("right")
            if left not in df.columns or right not in df.columns:
                continue
            left_dates = pd.to_datetime(df[left], errors="coerce")
            right_dates = pd.to_datetime(df[right], errors="coerce")
            feature_data[name] = _to_binary(left_dates > right_dates)
        elif op == "date_in_future":
            column = feature.get("column")
            if column not in df.columns:
                continue
            dates = pd.to_datetime(df[column], errors="coerce")
            today = pd.Timestamp.utcnow().tz_localize(None).normalize()
            feature_data[name] = _to_binary(dates > today)
        elif op in {"numeric_gt", "numeric_lt"}:
            column = feature.get("column")
            if column not in df.columns:
                continue
            left_values = pd.to_numeric(df[column], errors="coerce")
            right_column = feature.get("right")
            if right_column:
                if right_column not in df.columns:
                    continue
                right_values = pd.to_numeric(df[right_column], errors="coerce")
            else:
                right_values = float(feature.get("value", 0))
            if op == "numeric_gt":
                feature_data[name] = _to_binary(left_values > right_values)
            else:
                feature_data[name] = _to_binary(left_values < right_values)
        elif op == "starts_with":
            column = feature.get("column")
            if column not in df.columns:
                continue
            prefix = str(feature.get("value", ""))
            feature_data[name] = _to_binary(df[column].astype("string").str.strip().str.startswith(prefix, na=False))
        elif op == "equals":
            column = feature.get("column")
            if column not in df.columns:
                continue
            feature_data[name] = _to_binary(_equals(df[column], feature.get("value", "")))
        elif op == "all_missing":
            columns = feature.get("columns", [])
            if any(column not in df.columns for column in columns):
                continue
            feature_data[name] = _to_binary(_missing_columns_mask(df, columns))
        elif op == "duplicate_key":
            columns = feature.get("columns", [])
            if any(column not in df.columns for column in columns):
                continue
            complete_key = _complete_key_mask(df, columns)
            group_sizes = df.groupby(columns, dropna=False)[columns[0]].transform("size")
            feature_data[name] = _to_binary(complete_key & (group_sizes > 1))
        elif op == "duplicate_distinct":
            columns = feature.get("columns", [])
            distinct_column = feature.get("distinct_column")
            if distinct_column not in df.columns or any(column not in df.columns for column in columns):
                continue
            complete_key = _complete_key_mask(df, columns) & ~_is_missing(df[distinct_column])
            distinct_counts = df.groupby(columns, dropna=False)[distinct_column].transform("nunique")
            feature_data[name] = _to_binary(complete_key & (distinct_counts > 1))
        elif op == "duplicate_normalized_key":
            columns = feature.get("columns", [])
            if any(column not in df.columns for column in columns):
                continue
            normalized_keys = _normalized_key_frame(df, columns)
            complete_key = _normalized_complete_key_mask(normalized_keys)
            key = _combined_normalized_key(normalized_keys)
            group_sizes = key.groupby(key, dropna=True).transform("size")
            feature_data[name] = _to_binary(complete_key & (group_sizes > 1))
        elif op in {"rolling_window_amount_sum", "rolling_window_count"}:
            columns = feature.get("columns", [])
            if any(column not in df.columns for column in columns):
                continue
            window_days = int(feature.get("params", {}).get("window_days", 7))
            aggregation = "sum" if op == "rolling_window_amount_sum" else "count"
            feature_data[name] = _rolling_window_by_key(
                df,
                columns,
                amount,
                window_days,
                aggregation,
            )

    return pd.DataFrame(feature_data).replace([np.inf, -np.inf], np.nan)
