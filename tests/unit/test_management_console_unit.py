from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "management-console"))

from management_console.app import configured_probe, first_host_port  # noqa: E402
from management_console.catalog import catalog_payload, dga_payload  # noqa: E402


class ManagementConsoleUnitTests(unittest.TestCase):
    def test_catalog_payload_contains_core_management_surfaces(self) -> None:
        payload = catalog_payload()
        component_ids = {component["id"] for component in payload["components"]}
        topic_names = {topic["name"] for topic in payload["topics"]}
        operation_ids = {operation["id"] for operation in payload["operations"]}
        data_product_ids = {product["product_id"] for product in payload["data_products"]}

        self.assertIn("kafka", component_ids)
        self.assertIn("airflow", component_ids)
        self.assertIn("flink", component_ids)
        self.assertIn("data-governance", component_ids)
        self.assertIn("raw.gps", topic_names)
        self.assertIn("dlq.events", topic_names)
        self.assertIn("governance.intermediation.log", topic_names)
        self.assertIn("telemetry.raw.gps", data_product_ids)
        self.assertIn("refresh-health", operation_ids)
        self.assertIn("review-dga-readiness", operation_ids)
        self.assertIn("trigger-media-backfill", operation_ids)

    def test_dga_payload_exposes_evidence_topics_and_obligations(self) -> None:
        payload = dga_payload()
        evidence_topics = {topic["name"] for topic in payload["evidence_topics"]}
        obligation_ids = {obligation["id"] for obligation in payload["obligations"]}

        self.assertIn("governance.data.products", evidence_topics)
        self.assertIn("governance.permission.events", evidence_topics)
        self.assertIn("governance.intermediation.log", evidence_topics)
        self.assertIn("neutrality", obligation_ids)
        self.assertIn("intermediation-log", obligation_ids)

    def test_first_host_port_accepts_common_kafka_listener_prefixes(self) -> None:
        self.assertEqual(
            first_host_port("SASL_SSL://kafka1.example.net:9093,kafka2.example.net:9093"),
            "kafka1.example.net:9093",
        )
        self.assertEqual(first_host_port("kafka1:9092,kafka2:9092"), "kafka1:9092")
        self.assertIsNone(first_host_port(""))

    def test_configured_probe_uses_runtime_environment(self) -> None:
        kafka_component = {"id": "kafka", "probe": "tcp://kafka1:9092"}
        mqtt_component = {"id": "vernemq", "probe": "tcp://vernemq1:1883"}
        airflow_component = {"id": "airflow", "probe": "http://airflow-apiserver:8080/api/v2"}

        with patch.dict(
            "os.environ",
            {
                "KAFKA_BOOTSTRAP_SERVERS": "SASL_SSL://kafka.example.net:9093",
                "MQTT_HOST": "mqtt.example.net",
                "MQTT_PORT": "8883",
                "AIRFLOW_API_URL": "https://airflow.example.net/api/v2",
            },
            clear=False,
        ):
            self.assertEqual(configured_probe(kafka_component), "tcp://kafka.example.net:9093")
            self.assertEqual(configured_probe(mqtt_component), "tcp://mqtt.example.net:8883")
            self.assertEqual(
                configured_probe(airflow_component),
                "https://airflow.example.net/api/v2/version",
            )


if __name__ == "__main__":
    unittest.main()
