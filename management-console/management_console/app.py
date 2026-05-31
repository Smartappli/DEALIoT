from __future__ import annotations

import base64
import concurrent.futures
import json
import os
import socket
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib import error, request
from urllib.parse import urlparse

from management_console.catalog import COMPONENTS, catalog_payload, dga_payload

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"
DEFAULT_TIMEOUT_SECONDS = 2.0
MAX_REQUEST_BYTES = 65536


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def timeout_seconds() -> float:
    value = os.getenv("MANAGEMENT_CONSOLE_PROBE_TIMEOUT_SECONDS", "")
    if not value:
        return DEFAULT_TIMEOUT_SECONDS
    try:
        return max(0.2, min(float(value), 10.0))
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS


def probe_tcp(endpoint: str, timeout: float) -> dict[str, Any]:
    parsed = urlparse(endpoint)
    host = parsed.hostname
    port = parsed.port
    if host is None or port is None:
        return {"status": "unknown", "detail": "invalid tcp probe"}

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {"status": "healthy", "detail": f"tcp:{host}:{port}"}
    except OSError as exc:
        return {"status": "unreachable", "detail": str(exc)}


def probe_http(endpoint: str, timeout: float) -> dict[str, Any]:
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"}:
        return {"status": "unknown", "detail": "invalid http probe scheme"}

    try:
        req = request.Request(endpoint, method="GET")  # noqa: S310
        with request.urlopen(req, timeout=timeout) as response:  # noqa: S310
            status = response.getcode()
    except error.HTTPError as exc:
        if exc.code < HTTPStatus.INTERNAL_SERVER_ERROR:
            return {"status": "healthy", "detail": f"http {exc.code}"}
        return {"status": "degraded", "detail": f"http {exc.code}"}
    except OSError as exc:
        return {"status": "unreachable", "detail": str(exc)}
    else:
        if status < HTTPStatus.INTERNAL_SERVER_ERROR:
            return {"status": "healthy", "detail": f"http {status}"}
        return {"status": "degraded", "detail": f"http {status}"}


def first_host_port(value: str) -> str | None:
    first = next((item.strip() for item in value.split(",") if item.strip()), "")
    if not first:
        return None
    return first.removeprefix("PLAINTEXT://").removeprefix("SSL://").removeprefix("SASL_SSL://")


def endpoint_with_path(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def mqtt_probe() -> str | None:
    mqtt_host = os.getenv("MQTT_HOST")
    mqtt_port = os.getenv("MQTT_PORT", "1883")
    if mqtt_host:
        return f"tcp://{mqtt_host}:{mqtt_port}"
    return None


def kafka_probe() -> str | None:
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    if not bootstrap:
        return None
    host_port = first_host_port(bootstrap)
    if not host_port:
        return None
    return f"tcp://{host_port}"


def apicurio_probe() -> str | None:
    health_url = os.getenv("APICURIO_REGISTRY_HEALTH_URL")
    if health_url:
        return health_url
    registry_url = os.getenv("APICURIO_REGISTRY_URL") or os.getenv("APICURIO_REGISTRY_V3_URL")
    if registry_url:
        return endpoint_with_path(registry_url, "system/info")
    return None


def endpoint_probe(env_name: str, path: str | None = None) -> str | None:
    value = os.getenv(env_name)
    if not value:
        return None
    if path is None:
        return value
    return endpoint_with_path(value, path)


PROBE_OVERRIDES = {
    "vernemq": mqtt_probe,
    "kafka": kafka_probe,
    "apicurio": apicurio_probe,
    "seaweedfs": lambda: endpoint_probe("S3_ENDPOINT_URL"),
    "flink": lambda: endpoint_probe("FLINK_REST_URL", "overview"),
    "airflow": lambda: endpoint_probe("AIRFLOW_API_URL", "version"),
    "prometheus": lambda: endpoint_probe("PROMETHEUS_URL", "-/ready"),
    "grafana": lambda: endpoint_probe("GRAFANA_URL", "api/health"),
}


def configured_probe(component: dict[str, Any]) -> str | None:
    override = PROBE_OVERRIDES.get(component["id"])
    if override is not None:
        endpoint = override()
        if endpoint:
            return endpoint
    return component.get("probe")


def probe_component(component: dict[str, Any]) -> dict[str, Any]:
    endpoint = configured_probe(component)
    if not endpoint:
        return {
            "id": component["id"],
            "status": "unknown",
            "detail": "no probe configured",
            "checked_at": now_iso(),
        }

    timeout = timeout_seconds()
    if endpoint.startswith("tcp://"):
        result = probe_tcp(endpoint, timeout)
    else:
        result = probe_http(endpoint, timeout)

    return {
        "id": component["id"],
        "status": result["status"],
        "detail": result["detail"],
        "checked_at": now_iso(),
    }


def health_payload() -> dict[str, Any]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(COMPONENTS)) as executor:
        checks = list(executor.map(probe_component, COMPONENTS))
    counts: dict[str, int] = {}
    for check in checks:
        counts[check["status"]] = counts.get(check["status"], 0) + 1

    return {
        "checked_at": now_iso(),
        "summary": counts,
        "checks": checks,
    }


def airflow_auth_header() -> str | None:
    username = os.getenv("AIRFLOW_API_USERNAME")
    password = os.getenv("AIRFLOW_API_PASSWORD")
    if not username or not password:
        return None
    token = base64.b64encode(f"{username}:{password}".encode()).decode("ascii")
    return f"Basic {token}"


def trigger_media_backfill(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    auth_header = airflow_auth_header()
    if auth_header is None:
        return (
            HTTPStatus.CONFLICT,
            {
                "error": "missing_airflow_credentials",
                "message": "Set AIRFLOW_API_USERNAME and AIRFLOW_API_PASSWORD for this action.",
            },
        )

    airflow_api_url = os.getenv("AIRFLOW_API_URL", "http://airflow-apiserver:8080/api/v2")
    dag_run_url = f"{airflow_api_url.rstrip('/')}/dags/media_backfill/dagRuns"
    if urlparse(dag_run_url).scheme not in {"http", "https"}:
        return HTTPStatus.BAD_REQUEST, {"error": "invalid_airflow_api_url"}

    body = json.dumps(
        {
            "dag_run_id": payload.get("dag_run_id") or f"manual__management_console__{now_iso()}",
            "conf": payload.get("conf", {}),
        }
    ).encode("utf-8")

    req = request.Request(  # noqa: S310
        dag_run_url,
        data=body,
        method="POST",
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout_seconds()) as response:  # noqa: S310
            response_body = response.read().decode("utf-8")
            parsed = json.loads(response_body) if response_body else {}
            return response.getcode(), {"status": "submitted", "airflow_response": parsed}
    except error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        return exc.code, {"error": "airflow_rejected_request", "detail": body_text}
    except OSError as exc:
        return HTTPStatus.BAD_GATEWAY, {"error": "airflow_unreachable", "detail": str(exc)}


def read_json_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length > MAX_REQUEST_BYTES:
        raise ValueError("request body too large")
    if length == 0:
        return {}
    body = handler.rfile.read(length)
    parsed = json.loads(body.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise TypeError("request body must be a JSON object")
    return parsed


class ManagementConsoleHandler(BaseHTTPRequestHandler):
    server_version = "DEALIoTManagementConsole/1.0"

    def do_GET(self) -> None:
        routes = {
            "/api/architecture": lambda: self.respond_json(catalog_payload()),
            "/api/dga": lambda: self.respond_json(dga_payload()),
            "/api/health": lambda: self.respond_json(health_payload()),
            "/api/runbooks": lambda: self.respond_json({"runbooks": catalog_payload()["runbooks"]}),
            "/healthz": lambda: self.respond_json({"status": "ok", "checked_at": now_iso()}),
        }
        route = routes.get(self.path)
        if route is not None:
            route()
            return

        self.serve_static()

    def do_POST(self) -> None:
        if self.path != "/api/operations/trigger-media-backfill":
            self.respond_json({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            payload = read_json_body(self)
        except (json.JSONDecodeError, ValueError) as exc:
            self.respond_json(
                {"error": "invalid_request", "detail": str(exc)},
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        status, response_payload = trigger_media_backfill(payload)
        self.respond_json(response_payload, status=status)

    def serve_static(self) -> None:
        relative_path = "index.html" if self.path in {"/", ""} else self.path.lstrip("/")
        target = (STATIC_DIR / relative_path).resolve()
        if not target.is_relative_to(STATIC_DIR.resolve()) or not target.is_file():
            self.respond_json({"error": "not_found"}, status=HTTPStatus.NOT_FOUND)
            return

        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
        }.get(target.suffix, "application/octet-stream")

        content = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def respond_json(self, payload: dict[str, Any], status: int = HTTPStatus.OK) -> None:
        content = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, message_format: str, *args: Any) -> None:
        print(
            json.dumps(
                {
                    "time": now_iso(),
                    "client": self.client_address[0],
                    "message": message_format % args,
                },
                separators=(",", ":"),
            )
        )


def run() -> None:
    host = os.getenv("MANAGEMENT_CONSOLE_BIND", "0.0.0.0")  # noqa: S104
    port = int(os.getenv("MANAGEMENT_CONSOLE_PORT", "8080"))
    with ThreadingHTTPServer((host, port), ManagementConsoleHandler) as server:
        print(f"management-console listening on {host}:{port}")
        server.serve_forever()


if __name__ == "__main__":
    run()
