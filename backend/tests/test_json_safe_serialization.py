import datetime as dt
import json

import ml_engine


def test_json_safe_object_serializes_native_dates():
    payload = {
        "plain_date": dt.date(2026, 6, 19),
        "nested": {
            "timestamp": dt.datetime(2026, 6, 19, 10, 30, 5),
        },
    }

    safe_payload = ml_engine.json_safe_object(payload)

    assert safe_payload == {
        "plain_date": "2026-06-19",
        "nested": {
            "timestamp": "2026-06-19T10:30:05",
        },
    }
    json.dumps(safe_payload)
