from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class PlatformIntegrationTests(unittest.TestCase):
    def test_seaweed_cluster_services_are_defined(self) -> None:
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        services = [
            "seaweedfs-master1",
            "seaweedfs-master2",
            "seaweedfs-master3",
            "seaweedfs-volume1",
            "seaweedfs-volume2",
            "seaweedfs-volume3",
            "seaweedfs-filer",
            "seaweedfs-s3",
        ]

        for service in services:
            self.assertIn(f"  {service}:", compose_text, f"Missing SeaweedFS service: {service}")

    def test_seaweed_s3_depends_on_filer(self) -> None:
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertIn("  seaweedfs-s3:", compose_text)
        self.assertIn("      seaweedfs-filer:", compose_text)

    def test_airflow_and_streaming_components_coexist(self) -> None:
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        expected_services = [
            "airflow-scheduler",
            "airflow-worker",
            "kafka1",
            "kafka2",
            "kafka3",
            "flink-jobmanager",
            "flink-taskmanager-1",
            "beam-jobserver",
            "mqtt-kafka-bridge",
        ]
        for service in expected_services:
            self.assertIn(f"  {service}:", compose_text, f"Missing integration service: {service}")


if __name__ == "__main__":
    unittest.main()
