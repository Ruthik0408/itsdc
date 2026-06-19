import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from sqlalchemy import text

from ml_engine import (
    DEFAULT_DETECTION_STAGE,
    DEFAULT_MAX_EXPLANATIONS,
    DEFAULT_MAX_TABLES_PER_SCAN,
    DEFAULT_ROWS_PER_TABLE,
    build_engine,
    build_llama_client,
    init_alert_tables,
    load_payment_categories_from_db,
    load_runtime_sources,
    run_scan,
    update_payment_category_config,
)
from supervision import append_negative_supervision, append_positive_supervision
from db_config import (
    SUPPORTED_LLM_PROVIDERS,
    get_llama_settings,
    get_llm_provider,
    set_llm_provider,
)


REVIEW_DECISIONS = {"accept", "reject", "maybe"}
MAX_FEEDBACK_LENGTH = 100


def llm_provider_state() -> dict:
    settings = get_llama_settings()
    return {
        "provider": get_llm_provider(),
        "available": list(SUPPORTED_LLM_PROVIDERS),
        "model": settings["model"],
        "base_url": settings["base_url"],
    }

scan_status = {
    "running": False,
    "last_result": None,
    "last_error": None,
}
scan_lock = threading.Lock()


MAX_PAGE_SIZE = 200
DEFAULT_PAGE_SIZE = 25
SORTABLE_COLUMNS = {
    "detected_at": "detected_at",
    "anomaly_score": "anomaly_score",
    "table_name": "table_name",
    "transaction_id": "transaction_id",
}


def fetch_anomaly_rows(
    engine,
    limit: int = DEFAULT_PAGE_SIZE,
    offset: int = 0,
    table: str | None = None,
    query: str | None = None,
    sort: str = "detected_at",
    direction: str = "desc",
) -> dict:
    """Return a paginated, filterable page of unreviewed anomalies.

    Filtering and pagination happen in SQL so the grid can browse the full
    result set instead of only the newest rows of one table.
    """
    limit = max(1, min(int(limit), MAX_PAGE_SIZE))
    offset = max(0, int(offset))
    sort_column = SORTABLE_COLUMNS.get(sort, "detected_at")
    sort_direction = "ASC" if str(direction).lower() == "asc" else "DESC"

    filters = ["review_status IS NULL"]
    params: dict = {}
    if table:
        filters.append("table_name = :table")
        params["table"] = table
    if query:
        filters.append("transaction_id ILIKE :query")
        params["query"] = f"%{query}%"
    where_clause = " AND ".join(filters)

    with engine.connect() as conn:
        total = conn.execute(
            text(f"SELECT COUNT(*) FROM detected_anomalies WHERE {where_clause};"),
            params,
        ).scalar_one()

        tables = [
            row[0]
            for row in conn.execute(
                text(
                    """
                    SELECT DISTINCT table_name
                    FROM detected_anomalies
                    WHERE review_status IS NULL AND table_name IS NOT NULL
                    ORDER BY table_name;
                    """
                )
            ).all()
        ]

        rows = conn.execute(
            text(
                f"""
                SELECT
                    transaction_id,
                    COALESCE(table_name, 'unknown') AS table_name,
                    COALESCE(source_record_id, transaction_id) AS source_record_id,
                    anomaly_score,
                    COALESCE(isolation_score, anomaly_score) AS isolation_score,
                    autoencoder_score,
                    COALESCE(feature_snapshot, '{{}}'::jsonb) AS feature_snapshot,
                    explanation,
                    detected_at
                FROM detected_anomalies
                WHERE {where_clause}
                ORDER BY {sort_column} {sort_direction}, transaction_id ASC
                LIMIT :limit OFFSET :offset;
                """
            ),
            {**params, "limit": limit, "offset": offset},
        ).mappings()

        items = []
        for row in rows:
            feature_snapshot = row["feature_snapshot"]
            if isinstance(feature_snapshot, str):
                feature_snapshot = json.loads(feature_snapshot)
            items.append(
                {
                    "transaction_id": row["transaction_id"],
                    "table_name": row["table_name"],
                    "source_record_id": row["source_record_id"],
                    "anomaly_score": float(row["anomaly_score"] or 0),
                    "isolation_score": float(row["isolation_score"] or 0),
                    "autoencoder_score": (
                        float(row["autoencoder_score"])
                        if row["autoencoder_score"] is not None
                        else None
                    ),
                    "feature_snapshot": feature_snapshot,
                    "explanation": row["explanation"],
                    "detected_at": row["detected_at"].isoformat() if row["detected_at"] else None,
                }
            )
    print(
        f"[api] /api/anomalies returned {len(items)} of {total} row(s) "
        f"(table={table or 'all'}, q={query or ''}, offset={offset}).",
        flush=True,
    )
    return {
        "items": items,
        "total": int(total),
        "tables": tables,
        "limit": limit,
        "offset": offset,
    }


def load_feature_plan(engine) -> list[dict]:
    try:
        runtime_sources = load_runtime_sources(engine)
    except Exception as exc:
        print(f"[api] Could not load runtime feature plan: {type(exc).__name__}: {exc}", flush=True)
        return []

    feature_plan = []
    for source in runtime_sources:
        if not source.feature_plan:
            continue
        feature_plan.append(
            {
                "table": source.table,
                "scan_name": source.scan_name,
                "dak_section_filter": list(source.dak_section_ids),
                "amount_column": source.amount_column,
                "context_columns": list(source.context_columns),
                "base_context_columns": list(source.base_context_columns or source.context_columns),
                "joined_context_columns": [
                    {
                        "source_column": joined.source_column,
                        "reference_table": joined.reference_table,
                        "reference_column": joined.reference_column,
                        "alias": joined.alias,
                    }
                    for joined in source.joined_context_columns
                ],
                "date_column": source.date_column,
                "feature_plan": list(source.feature_plan),
            }
        )
    return feature_plan


def list_payment_categories(engine) -> list[dict]:
    categories = load_payment_categories_from_db(engine, include_disabled=True)
    return [
        {
            "category_name": category,
            "source_tables": list(config["source_tables"]),
            "dak_section_ids": list(config["dak_section_ids"]),
            "enabled": bool(config["enabled"]),
        }
        for category, config in categories.items()
    ]


def review_anomaly(engine, transaction_id: str, decision: str, feedback: str) -> dict:
    decision = str(decision).strip().lower()
    feedback = str(feedback or "").strip()[:MAX_FEEDBACK_LENGTH]

    if decision not in REVIEW_DECISIONS:
        raise ValueError("decision must be one of: accept, reject, maybe")
    if not transaction_id:
        raise ValueError("transaction_id is required")

    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                UPDATE detected_anomalies
                SET
                    review_status = :decision,
                    review_feedback = :feedback,
                    reviewed_at = NOW()
                WHERE transaction_id = :transaction_id;
                """
            ),
            {
                "transaction_id": transaction_id,
                "decision": decision,
                "feedback": feedback,
            },
        )

    if result.rowcount != 1:
        raise LookupError(f"Anomaly not found: {transaction_id}")

    print(
        f"[api] Reviewed anomaly transaction_id={transaction_id} "
        f"decision={decision} feedback_length={len(feedback)}.",
        flush=True,
    )

    if decision == "accept":
        record_review_supervision(engine, transaction_id, feedback, append_positive_supervision, "positive")
    elif decision == "reject":
        record_review_supervision(engine, transaction_id, feedback, append_negative_supervision, "negative")

    return {
        "transaction_id": transaction_id,
        "review_status": decision,
        "review_feedback": feedback,
    }


def record_review_supervision(engine, transaction_id: str, feedback: str, append_func, label: str) -> None:
    """Append a reviewed anomaly to an append-only supervision log."""
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT
                        transaction_id,
                        table_name,
                        source_record_id,
                        anomaly_score,
                        isolation_score,
                        autoencoder_score,
                        feature_snapshot,
                        explanation
                    FROM detected_anomalies
                    WHERE transaction_id = :transaction_id;
                    """
                ),
                {"transaction_id": transaction_id},
            ).mappings().first()

        if row is None:
            return

        feature_snapshot = row["feature_snapshot"]
        if isinstance(feature_snapshot, str):
            feature_snapshot = json.loads(feature_snapshot)
        feature_snapshot = feature_snapshot or {}

        append_func(
            {
                "transaction_id": row["transaction_id"],
                "table_name": row["table_name"],
                "source_record_id": row["source_record_id"],
                "anomaly_score": float(row["anomaly_score"]) if row["anomaly_score"] is not None else None,
                "isolation_score": float(row["isolation_score"]) if row["isolation_score"] is not None else None,
                "autoencoder_score": (
                    float(row["autoencoder_score"]) if row["autoencoder_score"] is not None else None
                ),
                "engineered_feature_values": feature_snapshot.get("engineered_feature_values", {}),
                "explanation": row["explanation"],
                "reviewer_feedback": feedback,
            }
        )
        print(f"[api] Appended {label} supervision for anomaly {transaction_id}.", flush=True)
    except Exception as exc:
        # Supervision logging must never break the review response.
        print(
            f"[api] Could not append {label} supervision for {transaction_id}: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )


def make_api_handler(
    engine,
    llama_client,
    max_explanations: int,
    max_tables: int,
    rows_per_table: int,
    detection_stage: str,
):
    class ApiHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            message = format % args
            if "/api/scan-status" in message:
                return
            print(f"[api] {self.address_string()} - {message}", flush=True)

        def send_json(self, status_code: int, payload) -> bool:
            body = json.dumps(payload).encode("utf-8")
            try:
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
                self.wfile.write(body)
                return True
            except BrokenPipeError:
                print("[api] Client disconnected before response completed; ignoring.", flush=True)
                return False

        def do_OPTIONS(self):
            self.send_json(200, {"ok": True})

        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path
            try:
                if path == "/api/anomalies":
                    params = parse_qs(parsed.query)

                    def first(name, default=None):
                        values = params.get(name)
                        return values[0] if values else default

                    try:
                        limit = int(first("limit", DEFAULT_PAGE_SIZE))
                        offset = int(first("offset", 0))
                    except ValueError:
                        self.send_json(400, {"error": "limit and offset must be integers"})
                        return

                    self.send_json(
                        200,
                        fetch_anomaly_rows(
                            engine,
                            limit=limit,
                            offset=offset,
                            table=first("table") or None,
                            query=first("q") or None,
                            sort=first("sort", "detected_at"),
                            direction=first("direction", "desc"),
                        ),
                    )
                    return
                if path == "/api/scan-status":
                    with scan_lock:
                        payload = dict(scan_status)
                    self.send_json(200, payload)
                    return
                if path == "/api/feature-plan":
                    self.send_json(200, load_feature_plan(engine))
                    return
                if path == "/api/payment-categories":
                    self.send_json(200, list_payment_categories(engine))
                    return
                if path == "/api/llm-provider":
                    self.send_json(200, llm_provider_state())
                    return
                if path == "/api/health":
                    self.send_json(200, {"ok": True})
                    return
                self.send_json(404, {"error": "Not found"})
            except Exception as exc:
                if isinstance(exc, BrokenPipeError):
                    print("[api] Client disconnected during GET; ignoring.", flush=True)
                    return
                print(f"[api] GET {path} failed: {type(exc).__name__}: {exc}", flush=True)
                self.send_json(500, {"error": f"{type(exc).__name__}: {exc}"})

        def do_POST(self):
            path = urlparse(self.path).path
            if path == "/api/anomaly-review":
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                    raw_body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
                    payload = json.loads(raw_body)
                    result = review_anomaly(
                        engine,
                        transaction_id=str(payload.get("transaction_id", "")),
                        decision=str(payload.get("decision", "")),
                        feedback=str(payload.get("feedback", "")),
                    )
                    self.send_json(200, result)
                except ValueError as exc:
                    self.send_json(400, {"error": str(exc)})
                except LookupError as exc:
                    self.send_json(404, {"error": str(exc)})
                except json.JSONDecodeError:
                    self.send_json(400, {"error": "Request body must be valid JSON"})
                except Exception as exc:
                    print(f"[api] POST {path} failed: {type(exc).__name__}: {exc}", flush=True)
                    self.send_json(500, {"error": f"{type(exc).__name__}: {exc}"})
                return

            if path == "/api/llm-provider":
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                    raw_body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
                    payload = json.loads(raw_body)
                    set_llm_provider(str(payload.get("provider", "")))
                    print(f"[api] LLM provider switched to {get_llm_provider()}.", flush=True)
                    self.send_json(200, llm_provider_state())
                except ValueError as exc:
                    self.send_json(400, {"error": str(exc)})
                except json.JSONDecodeError:
                    self.send_json(400, {"error": "Request body must be valid JSON"})
                except Exception as exc:
                    print(f"[api] POST {path} failed: {type(exc).__name__}: {exc}", flush=True)
                    self.send_json(500, {"error": f"{type(exc).__name__}: {exc}"})
                return

            if path != "/api/run-scan":
                self.send_json(404, {"error": "Not found"})
                return

            with scan_lock:
                already_running = scan_status["running"]
                if not already_running:
                    scan_status["running"] = True
                    scan_status["last_error"] = None

            if already_running:
                with scan_lock:
                    payload = dict(scan_status)
                self.send_json(200, {"started": False, "status": payload})
                return

            def scan_job():
                try:
                    # Rebuild the client each scan so a UI provider switch
                    # (local/groq) takes effect without a server restart.
                    active_client = build_llama_client()
                    result = run_scan(
                        engine,
                        active_client,
                        max_explanations=max_explanations,
                        max_tables=max_tables,
                        rows_per_table=rows_per_table,
                        detection_stage=detection_stage,
                    )
                    with scan_lock:
                        scan_status["last_result"] = result
                except Exception as exc:
                    with scan_lock:
                        scan_status["last_error"] = f"{type(exc).__name__}: {exc}"
                    print(f"[api] Manual scan failed: {type(exc).__name__}: {exc}", flush=True)
                finally:
                    with scan_lock:
                        scan_status["running"] = False

            threading.Thread(target=scan_job, daemon=True).start()
            with scan_lock:
                payload = dict(scan_status)
            self.send_json(202, {"started": True, "status": payload})

        def do_PUT(self):
            path = urlparse(self.path).path
            if path != "/api/payment-categories":
                self.send_json(404, {"error": "Not found"})
                return

            try:
                content_length = int(self.headers.get("Content-Length", "0"))
                raw_body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
                payload = json.loads(raw_body)
                updated = update_payment_category_config(
                    engine,
                    category_name=str(payload.get("category_name", "")),
                    source_tables=payload.get("source_tables"),
                    dak_section_ids=payload.get("dak_section_ids"),
                    enabled=bool(payload.get("enabled", True)),
                )
                self.send_json(200, updated)
            except RuntimeError as exc:
                self.send_json(400, {"error": str(exc)})
            except json.JSONDecodeError:
                self.send_json(400, {"error": "Request body must be valid JSON"})
            except Exception as exc:
                print(f"[api] PUT {path} failed: {type(exc).__name__}: {exc}", flush=True)
                self.send_json(500, {"error": f"{type(exc).__name__}: {exc}"})

    return ApiHandler


def create_api_server(
    host: str,
    port: int,
    engine,
    llama_client,
    max_explanations: int,
    max_tables: int,
    rows_per_table: int,
    detection_stage: str,
) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(
        (host, port),
        make_api_handler(engine, llama_client, max_explanations, max_tables, rows_per_table, detection_stage),
    )


def start_api_server(
    host: str = "127.0.0.1",
    port: int = 5000,
    max_explanations: int = DEFAULT_MAX_EXPLANATIONS,
    max_tables: int = DEFAULT_MAX_TABLES_PER_SCAN,
    rows_per_table: int = DEFAULT_ROWS_PER_TABLE,
    detection_stage: str = DEFAULT_DETECTION_STAGE,
) -> None:
    print("[startup] API server mode starting.", flush=True)
    print(f"[startup] API will listen at http://{host}:{port}", flush=True)
    print("[startup] React UI command: cd frontend && npm run dev", flush=True)
    print("[startup] React UI URL is usually http://127.0.0.1:5173", flush=True)
    engine = build_engine()
    llama_client = build_llama_client()
    init_alert_tables(engine)
    server = create_api_server(
        host=host,
        port=port,
        engine=engine,
        llama_client=llama_client,
        max_explanations=max_explanations,
        max_tables=max_tables,
        rows_per_table=rows_per_table,
        detection_stage=detection_stage,
    )
    print("[api] Endpoints ready:", flush=True)
    print(f"[api]   GET  http://{host}:{port}/api/health", flush=True)
    print(f"[api]   GET  http://{host}:{port}/api/anomalies", flush=True)
    print(f"[api]   GET  http://{host}:{port}/api/scan-status", flush=True)
    print(f"[api]   GET  http://{host}:{port}/api/feature-plan", flush=True)
    print(f"[api]   GET  http://{host}:{port}/api/payment-categories", flush=True)
    print(f"[api]   POST http://{host}:{port}/api/anomaly-review", flush=True)
    print(f"[api]   POST http://{host}:{port}/api/run-scan", flush=True)
    print(f"[api]   PUT  http://{host}:{port}/api/payment-categories", flush=True)
    server.serve_forever()
