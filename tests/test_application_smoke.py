from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ApplicationSmokeTests(unittest.TestCase):
    def test_compose_contains_required_seaweedfs_services(self) -> None:
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")

        required_services = [
            "seaweedfs-master1",
            "seaweedfs-master2",
            "seaweedfs-master3",
            "seaweedfs-volume1",
            "seaweedfs-volume2",
            "seaweedfs-volume3",
            "seaweedfs-filer",
            "seaweedfs-s3",
        ]

        for service in required_services:
            self.assertIn(f"  {service}:", compose_text, f"Missing service: {service}")

    def test_compose_contains_core_platform_services(self) -> None:
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")

        core_services = [
            "kafka1",
            "kafka2",
            "kafka3",
            "airflow-scheduler",
            "airflow-worker",
            "mqtt-kafka-bridge",
            "apicurio-registry",
        ]

        for service in core_services:
            self.assertIn(f"  {service}:", compose_text, f"Missing service: {service}")

    def test_expected_workflows_are_present(self) -> None:
        workflow_dir = REPO_ROOT / ".github" / "workflows"
        expected_workflows = [
            "ci.yml",
            "shellcheck.yml",
            "compose-deployment-test.yml",
            "codeql.yml",
            "renovate.yml",
        ]

        for workflow in expected_workflows:
            self.assertTrue(
                (workflow_dir / workflow).is_file(), f"Missing workflow: {workflow}"
            )

    def test_critical_bootstrap_json_files_are_valid(self) -> None:
        bootstrap_dir = REPO_ROOT / "apicurio" / "bootstrap"
        json_files = [
            "media.object.events.json",
            "raw.sensor.json",
            "raw.image2d.meta.json",
            "raw.video2d.meta.json",
        ]

        for json_file in json_files:
            content = (bootstrap_dir / json_file).read_text(encoding="utf-8")
            parsed = json.loads(content)
            self.assertIsInstance(parsed, dict, f"Unexpected JSON root for {json_file}")

    def test_critical_startup_scripts_are_present(self) -> None:
        scripts = [
            REPO_ROOT / "scripts" / "post-bootstrap.sh",
            REPO_ROOT / "scripts" / "start-patroni.sh",
            REPO_ROOT / "scripts" / "start-pgbouncer-ro.sh",
            REPO_ROOT / "scripts" / "start-pgbouncer-rw.sh",
            REPO_ROOT / "flink" / "jobs" / "run-streaming-minimal.sh",
            REPO_ROOT / "beam" / "flink-job-server.sh",
        ]

        for script in scripts:
            self.assertTrue(script.is_file(), f"Missing script: {script}")


if __name__ == "__main__":
    unittest.main()
