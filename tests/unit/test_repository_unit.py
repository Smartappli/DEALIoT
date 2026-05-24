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
            REPO_ROOT / ".github" / "workflows" / "ci.yml",
            REPO_ROOT / ".github" / "dependabot.yml",
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

    def test_critical_shell_scripts_are_present(self) -> None:
        script_files = [
            REPO_ROOT / "scripts" / "post-bootstrap.sh",
            REPO_ROOT / "scripts" / "start-patroni.sh",
            REPO_ROOT / "scripts" / "start-pgbouncer-rw.sh",
            REPO_ROOT / "scripts" / "start-pgbouncer-ro.sh",
        ]

        for script in script_files:
            self.assertTrue(script.is_file(), f"Missing shell script: {script}")


if __name__ == "__main__":
    unittest.main()
