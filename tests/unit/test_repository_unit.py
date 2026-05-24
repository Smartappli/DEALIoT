from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class RepositoryUnitTests(unittest.TestCase):
    def test_critical_repository_files_exist(self) -> None:
        required_files = [
            REPO_ROOT / "docker-compose.yml",
            REPO_ROOT / "docker-compose.dev.yml",
            REPO_ROOT / "docker-compose.staging.yml",
            REPO_ROOT / "docker-compose.prod.yml",
            REPO_ROOT / ".dockerignore",
            REPO_ROOT / "README.md",
            REPO_ROOT / "scripts" / "smoke-e2e.sh",
            REPO_ROOT / "docs" / "runbooks" / "operations.md",
            REPO_ROOT / "docs" / "runbooks" / "backup-restore.md",
            REPO_ROOT / "docs" / "runbooks" / "security-hardening.md",
            REPO_ROOT / "docs" / "runbooks" / "wildfi-ingestion.md",
            REPO_ROOT / ".github" / "workflows" / "ci.yml",
            REPO_ROOT / ".github" / "dependabot.yml",
            REPO_ROOT / ".github" / "workflows" / "e2e-smoke.yml",
            REPO_ROOT / "wildfi-decoder" / "Dockerfile",
            REPO_ROOT / "wildfi-decoder" / "run-wildfi-decoder.sh",
        ]

        for file_path in required_files:
            self.assertTrue(file_path.is_file(), f"Missing file: {file_path}")

    def test_apicurio_bootstrap_json_payloads_are_strings(self) -> None:
        bootstrap_files = [
            REPO_ROOT / "apicurio" / "bootstrap" / "dlq.events.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "raw.sensor.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "media.object.events.json",
        ]

        for file_path in bootstrap_files:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
            content = payload["firstVersion"]["content"]["content"]
            self.assertIsInstance(content, str, f"Invalid embedded schema content in {file_path}")
            self.assertGreater(
                len(content), 20, f"Embedded schema content too short in {file_path}"
            )

    def test_compose_uses_canonical_state_latest_topic(self) -> None:
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        flink_text = (REPO_ROOT / "flink" / "jobs" / "streaming_minimal.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("--topic state.latest", compose_text)
        self.assertIn(
            "'topic' = '{env_or_default(\"STATE_TOPIC\", \"state.latest\")}'",
            flink_text,
        )
        self.assertNotIn("state-latest", compose_text)

    def test_apicurio_init_posts_bootstrap_payloads_directly(self) -> None:
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")

        self.assertIn('--data @"$$file"', compose_text)
        self.assertNotIn("content_escaped", compose_text)
        self.assertIn("post_artifact platform dlq.events /bootstrap/dlq.events.json", compose_text)

    def test_local_secrets_are_excluded_from_git_and_docker_contexts(self) -> None:
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        dockerignore = (REPO_ROOT / ".dockerignore").read_text(encoding="utf-8")

        for ignored_path in [".env", "secrets/"]:
            self.assertIn(ignored_path, gitignore)
            self.assertIn(ignored_path, dockerignore)

    def test_compose_does_not_define_sensitive_password_fallbacks(self) -> None:
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        forbidden_fragments = [
            "change-this-password",
            "change-this-cookie",
            "AIRFLOW_ADMIN_PASSWORD:-",
            "AIRFLOW_DB_PASSWORD:-",
            "GRAFANA_ADMIN_PASSWORD:-",
            "VERNEMQ_ADMIN_PASSWORD:-",
        ]

        for fragment in forbidden_fragments:
            self.assertNotIn(fragment, compose_text)

    def test_base_compose_does_not_publish_host_ports(self) -> None:
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")

        self.assertNotIn("\n    ports:\n", compose_text)

    def test_dev_overlay_contains_local_ports_and_prod_exposes_only_edge(self) -> None:
        dev_text = (REPO_ROOT / "docker-compose.dev.yml").read_text(encoding="utf-8")
        prod_text = (REPO_ROOT / "docker-compose.prod.yml").read_text(encoding="utf-8")

        for port in ['"8088:8080"', '"19092:19092"', '"3000:3000"', '"1883:1883"']:
            self.assertIn(port, dev_text)

        self.assertIn('"80:80"', prod_text)
        self.assertIn('"443:443"', prod_text)
        self.assertNotIn('"8088:8080"', prod_text)
        self.assertNotIn('"19092:19092"', prod_text)

    def test_e2e_smoke_script_checks_runtime_contracts(self) -> None:
        script_text = (REPO_ROOT / "scripts" / "smoke-e2e.sh").read_text(encoding="utf-8")

        for expected in [
            "raw.sensor",
            "dlq.events",
            "features.events",
            "state.latest",
            "run-streaming-minimal.sh",
            "apicurio-registry:8080",
        ]:
            self.assertIn(expected, script_text)

    def test_wildfi_ingestion_is_configured(self) -> None:
        bridge_source = (REPO_ROOT / "mqtt-kafka-bridge" / "bridge.py").read_text(encoding="utf-8")
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        runbook_text = (REPO_ROOT / "docs" / "runbooks" / "wildfi-ingestion.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("$share/ingestors/wildfi/#", compose_text)
        self.assertIn("WILDFI_TOPIC_PREFIXES", bridge_source)
        self.assertIn("WildFiDecoder", runbook_text)
        self.assertIn("WildFiOpenSource", runbook_text)
        self.assertIn("raw.gps", runbook_text)
        self.assertIn("raw.sensor", runbook_text)

    def test_wildfi_decoder_image_is_pinned_and_wrapped_for_batch_decoding(self) -> None:
        dockerfile = (REPO_ROOT / "wildfi-decoder" / "Dockerfile").read_text(encoding="utf-8")
        wrapper = (REPO_ROOT / "wildfi-decoder" / "run-wildfi-decoder.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("https://github.com/wildlab/WildFiDecoder.git", dockerfile)
        self.assertIn("b4002eb9a6111de140b95e5a35c3f3bd552d51be", dockerfile)
        self.assertIn("WildFiDecoderStandalone.jar", dockerfile)
        self.assertIn("WILDFI_DECODER_RAW_INPUT", wrapper)
        self.assertIn("WILDFI_DECODER_MODE", wrapper)

    def test_critical_shell_scripts_are_present(self) -> None:
        script_files = [
            REPO_ROOT / "scripts" / "post-bootstrap.sh",
            REPO_ROOT / "scripts" / "start-patroni.sh",
            REPO_ROOT / "scripts" / "start-pgbouncer-rw.sh",
            REPO_ROOT / "scripts" / "start-pgbouncer-ro.sh",
            REPO_ROOT / "scripts" / "smoke-e2e.sh",
        ]

        for script in script_files:
            self.assertTrue(script.is_file(), f"Missing shell script: {script}")


if __name__ == "__main__":
    unittest.main()
