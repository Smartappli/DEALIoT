from __future__ import annotations

import io
import json
import sys
import threading
import unittest
from contextlib import contextmanager
from http import HTTPStatus
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib import error, request
from unittest.mock import Mock, patch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "management-console"))

from management_console import app  # noqa: E402


class FakeResponse:
    def __init__(self, status: int = HTTPStatus.OK, body: bytes = b"{}") -> None:
        self.status = status
        self.body = body

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def getcode(self) -> int:
        return self.status

    def read(self) -> bytes:
        return self.body


class FakeBodyHandler:
    def __init__(self, body: bytes, length: int | None = None) -> None:
        self.rfile = io.BytesIO(body)
        self.headers = {"Content-Length": str(len(body) if length is None else length)}


@contextmanager
def running_console_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), app.ManagementConsoleHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def read_json(url: str) -> dict[str, object]:
    with request.urlopen(url, timeout=5) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


class ManagementConsoleAppUnitTests(unittest.TestCase):
    def test_timeout_seconds_clamps_and_handles_invalid_values(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(app.timeout_seconds(), app.DEFAULT_TIMEOUT_SECONDS)

        for value, expected in [("0.01", 0.2), ("30", 10.0), ("invalid", 2.0)]:
            with patch.dict("os.environ", {"MANAGEMENT_CONSOLE_PROBE_TIMEOUT_SECONDS": value}):
                self.assertEqual(app.timeout_seconds(), expected)

    def test_probe_tcp_reports_invalid_healthy_and_unreachable_states(self) -> None:
        self.assertEqual(app.probe_tcp("tcp://missing-port", 0.1)["status"], "unknown")

        connection = Mock()
        connection.__enter__ = Mock(return_value=connection)
        connection.__exit__ = Mock(return_value=None)
        with patch("management_console.app.socket.create_connection", return_value=connection):
            result = app.probe_tcp("tcp://example.net:9092", 0.1)
        self.assertEqual(result, {"status": "healthy", "detail": "tcp:example.net:9092"})

        with patch(
            "management_console.app.socket.create_connection",
            side_effect=OSError("offline"),
        ):
            result = app.probe_tcp("tcp://example.net:9092", 0.1)
        self.assertEqual(result["status"], "unreachable")
        self.assertIn("offline", result["detail"])

    def test_probe_http_reports_status_classes_and_errors(self) -> None:
        self.assertEqual(app.probe_http("ftp://example.net", 0.1)["status"], "unknown")

        with patch("management_console.app.request.urlopen", return_value=FakeResponse(204)):
            self.assertEqual(app.probe_http("https://example.net", 0.1)["status"], "healthy")
        with patch("management_console.app.request.urlopen", return_value=FakeResponse(503)):
            self.assertEqual(app.probe_http("https://example.net", 0.1)["status"], "degraded")

        not_found = error.HTTPError(
            "https://example.net",
            404,
            "not found",
            hdrs=None,
            fp=io.BytesIO(b"missing"),
        )
        server_error = error.HTTPError(
            "https://example.net",
            500,
            "server error",
            hdrs=None,
            fp=io.BytesIO(b"broken"),
        )
        with patch("management_console.app.request.urlopen", side_effect=not_found):
            self.assertEqual(app.probe_http("https://example.net", 0.1)["status"], "healthy")
        with patch("management_console.app.request.urlopen", side_effect=server_error):
            self.assertEqual(app.probe_http("https://example.net", 0.1)["status"], "degraded")
        with patch("management_console.app.request.urlopen", side_effect=OSError("offline")):
            self.assertEqual(app.probe_http("https://example.net", 0.1)["status"], "unreachable")

    def test_runtime_probe_overrides_cover_registered_components(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "APICURIO_REGISTRY_URL": "https://apicurio.example/api",
                "S3_ENDPOINT_URL": "https://s3.example",
                "FLINK_REST_URL": "https://flink.example",
                "PROMETHEUS_URL": "https://prometheus.example",
                "GRAFANA_URL": "https://grafana.example",
            },
            clear=True,
        ):
            self.assertEqual(
                app.configured_probe({"id": "apicurio", "probe": None}),
                "https://apicurio.example/api/system/info",
            )
            self.assertEqual(
                app.configured_probe({"id": "seaweedfs", "probe": None}),
                "https://s3.example",
            )
            self.assertEqual(
                app.configured_probe({"id": "flink", "probe": None}),
                "https://flink.example/overview",
            )
            self.assertEqual(
                app.configured_probe({"id": "prometheus", "probe": None}),
                "https://prometheus.example/-/ready",
            )
            self.assertEqual(
                app.configured_probe({"id": "grafana", "probe": None}),
                "https://grafana.example/api/health",
            )

        with patch.dict(
            "os.environ",
            {"APICURIO_REGISTRY_HEALTH_URL": "https://apicurio.example/health"},
            clear=True,
        ):
            self.assertEqual(
                app.configured_probe({"id": "apicurio", "probe": None}),
                "https://apicurio.example/health",
            )

    def test_probe_component_and_health_payload_summarize_checks(self) -> None:
        no_probe = app.probe_component({"id": "manual", "probe": None})
        self.assertEqual(no_probe["status"], "unknown")

        components = [{"id": "healthy"}, {"id": "offline"}, {"id": "offline-2"}]

        def fake_probe(component: dict[str, str]) -> dict[str, str]:
            status = "healthy" if component["id"] == "healthy" else "unreachable"
            return {"id": component["id"], "status": status, "detail": "test"}

        with (
            patch("management_console.app.COMPONENTS", components),
            patch("management_console.app.probe_component", side_effect=fake_probe),
        ):
            payload = app.health_payload()
        self.assertEqual(payload["summary"], {"healthy": 1, "unreachable": 2})
        self.assertEqual(len(payload["checks"]), 3)

    def test_airflow_trigger_handles_credentials_url_success_and_failures(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            status, payload = app.trigger_media_backfill({})
        self.assertEqual(status, HTTPStatus.CONFLICT)
        self.assertEqual(payload["error"], "missing_airflow_credentials")

        with patch.dict(
            "os.environ",
            {
                "AIRFLOW_API_USERNAME": "u",
                "AIRFLOW_API_PASSWORD": "p",
                "AIRFLOW_API_URL": "ftp://airflow",
            },
            clear=True,
        ):
            status, payload = app.trigger_media_backfill({})
        self.assertEqual(status, HTTPStatus.BAD_REQUEST)
        self.assertEqual(payload["error"], "invalid_airflow_api_url")

        response_body = b'{"dag_run_id":"manual"}'
        with (
            patch.dict(
                "os.environ",
                {
                    "AIRFLOW_API_USERNAME": "u",
                    "AIRFLOW_API_PASSWORD": "p",
                    "AIRFLOW_API_URL": "https://airflow.example/api/v2",
                },
                clear=True,
            ),
            patch("management_console.app.request.urlopen", return_value=FakeResponse(200, response_body)),
        ):
            status, payload = app.trigger_media_backfill({"dag_run_id": "manual"})
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(payload["status"], "submitted")

        rejected = error.HTTPError(
            "https://airflow.example",
            409,
            "conflict",
            hdrs=None,
            fp=io.BytesIO(b"already exists"),
        )
        with (
            patch.dict(
                "os.environ",
                {"AIRFLOW_API_USERNAME": "u", "AIRFLOW_API_PASSWORD": "p"},
                clear=True,
            ),
            patch("management_console.app.request.urlopen", side_effect=rejected),
        ):
            status, payload = app.trigger_media_backfill({})
        self.assertEqual(status, 409)
        self.assertEqual(payload["error"], "airflow_rejected_request")

        with (
            patch.dict(
                "os.environ",
                {"AIRFLOW_API_USERNAME": "u", "AIRFLOW_API_PASSWORD": "p"},
                clear=True,
            ),
            patch("management_console.app.request.urlopen", side_effect=OSError("offline")),
        ):
            status, payload = app.trigger_media_backfill({})
        self.assertEqual(status, HTTPStatus.BAD_GATEWAY)
        self.assertEqual(payload["error"], "airflow_unreachable")

    def test_read_json_body_validates_shape_and_size(self) -> None:
        self.assertEqual(app.read_json_body(FakeBodyHandler(b"")), {})
        self.assertEqual(app.read_json_body(FakeBodyHandler(b'{"a":1}')), {"a": 1})

        with self.assertRaises(TypeError):
            app.read_json_body(FakeBodyHandler(b'["not", "object"]'))
        with self.assertRaises(ValueError):
            app.read_json_body(FakeBodyHandler(b"{}", app.MAX_REQUEST_BYTES + 1))

    def test_http_handler_serves_api_static_post_and_errors(self) -> None:
        with running_console_server() as base_url:
            health = read_json(f"{base_url}/healthz")
            self.assertEqual(health["status"], "ok")

            zenodo_config = read_json(f"{base_url}/api/datasets/zenodo")
            self.assertEqual(zenodo_config["repository"], "Zenodo")

            with request.urlopen(f"{base_url}/", timeout=5) as response:  # noqa: S310
                html = response.read().decode("utf-8")
            self.assertIn("DEALIoT Management Console", html)

            with self.assertRaises(error.HTTPError) as not_found:
                request.urlopen(f"{base_url}/missing", timeout=5)  # noqa: S310
            self.assertEqual(not_found.exception.code, HTTPStatus.NOT_FOUND)

            post = request.Request(
                f"{base_url}/api/operations/trigger-media-backfill",
                data=b"[]",
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with self.assertRaises(error.HTTPError) as bad_request:
                request.urlopen(post, timeout=5)  # noqa: S310
            self.assertEqual(bad_request.exception.code, HTTPStatus.BAD_REQUEST)

            with patch(
                "management_console.app.trigger_media_backfill",
                return_value=(HTTPStatus.ACCEPTED, {"status": "queued"}),
            ):
                post = request.Request(
                    f"{base_url}/api/operations/trigger-media-backfill",
                    data=b'{"conf":{"limit":1}}',
                    method="POST",
                    headers={"Content-Type": "application/json"},
                )
                response = read_json_from_request(post)
            self.assertEqual(response["status"], "queued")

            with patch(
                "management_console.app.export_dataset_to_zenodo",
                return_value={"status": "draft_created", "dataset_id": "dataset"},
            ):
                post = request.Request(
                    f"{base_url}/api/datasets/zenodo/export",
                    data=b'{"dataset_id":"dataset.telemetry.sensor-minimised"}',
                    method="POST",
                    headers={"Content-Type": "application/json"},
                )
                response = read_json_from_request(post)
            self.assertEqual(response["status"], "draft_created")

            post = request.Request(
                f"{base_url}/api/missing",
                data=b"{}",
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with self.assertRaises(error.HTTPError) as missing_post:
                request.urlopen(post, timeout=5)  # noqa: S310
            self.assertEqual(missing_post.exception.code, HTTPStatus.NOT_FOUND)

    def test_run_uses_configured_bind_and_port(self) -> None:
        fake_server = Mock()
        fake_server.__enter__ = Mock(return_value=fake_server)
        fake_server.__exit__ = Mock(return_value=None)

        with (
            patch.dict(
                "os.environ",
                {"MANAGEMENT_CONSOLE_BIND": "127.0.0.1", "MANAGEMENT_CONSOLE_PORT": "8181"},
            ),
            patch("management_console.app.ThreadingHTTPServer", return_value=fake_server) as ctor,
            patch("builtins.print"),
        ):
            app.run()

        ctor.assert_called_once_with(("127.0.0.1", 8181), app.ManagementConsoleHandler)
        fake_server.serve_forever.assert_called_once()


def read_json_from_request(req: request.Request) -> dict[str, object]:
    with request.urlopen(req, timeout=5) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
