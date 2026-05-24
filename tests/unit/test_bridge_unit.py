from __future__ import annotations

import base64
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from typing import Any, ClassVar, cast
from unittest.mock import Mock, patch

REPO_ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PATH = REPO_ROOT / "mqtt-kafka-bridge" / "bridge.py"


class _FakeKafkaProducer:
    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        self.sent: list[tuple[str, bytes, dict]] = []

    def send(self, topic, key, value):
        self.sent.append((topic, key, value))

        future = Mock()
        future.add_callback = Mock()
        future.add_errback = Mock()
        return future

    def flush(self, timeout=None):
        return timeout


class _FakeClient:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.username = None
        self.password = None
        self.on_connect = None
        self.on_message = None
        self.subscriptions: list[tuple[str, int]] = []

    def username_pw_set(self, username, password):
        self.username = username
        self.password = password

    def subscribe(self, topic, qos=0):
        self.subscriptions.append((topic, qos))


class _FakeCallbackApiVersion:
    VERSION2 = object()


def _load_bridge_module():
    fake_kafka_mod = types.ModuleType("kafka")
    cast("Any", fake_kafka_mod).KafkaProducer = _FakeKafkaProducer

    fake_kafka_errors = types.ModuleType("kafka.errors")
    cast("Any", fake_kafka_errors).KafkaError = Exception

    fake_mqtt_client_mod = types.ModuleType("paho.mqtt.client")
    cast("Any", fake_mqtt_client_mod).Client = _FakeClient
    cast("Any", fake_mqtt_client_mod).CallbackAPIVersion = _FakeCallbackApiVersion

    fake_paho_mqtt_mod = types.ModuleType("paho.mqtt")
    cast("Any", fake_paho_mqtt_mod).client = fake_mqtt_client_mod

    fake_paho_mod = types.ModuleType("paho")
    cast("Any", fake_paho_mod).mqtt = fake_paho_mqtt_mod

    with patch.dict(
        sys.modules,
        {
            "kafka": fake_kafka_mod,
            "kafka.errors": fake_kafka_errors,
            "paho": fake_paho_mod,
            "paho.mqtt": fake_paho_mqtt_mod,
            "paho.mqtt.client": fake_mqtt_client_mod,
        },
    ):
        spec = importlib.util.spec_from_file_location("bridge_under_test", BRIDGE_PATH)
        if spec is None:
            raise RuntimeError("Unable to load module spec for bridge.py")
        if spec.loader is None:
            raise RuntimeError("Unable to load bridge.py module loader")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


class BridgeUnitTests(unittest.TestCase):
    bridge: ClassVar[Any]

    @classmethod
    def setUpClass(cls):
        cls.bridge = _load_bridge_module()

    def test_decode_payload_valid_json(self):
        payload = b'{"temperature": 21.5}'
        decoded = self.bridge.decode_payload(payload)
        self.assertEqual(decoded["temperature"], 21.5)

    def test_decode_payload_invalid_bytes_returns_base64(self):
        payload = b"\xff\x00\x88"
        decoded = self.bridge.decode_payload(payload)
        self.assertEqual(decoded["payload_b64"], base64.b64encode(payload).decode("ascii"))

    def test_pick_kafka_topic_and_device_id_helpers(self):
        self.assertEqual(self.bridge.pick_kafka_topic("devices/a1/gnss/fix"), "raw.gps")
        self.assertEqual(
            self.bridge.pick_kafka_topic("devices/a1/lidar/frame"),
            "raw.image3d.meta",
        )
        self.assertEqual(
            self.bridge.pick_kafka_topic("devices/a1/unknown"),
            self.bridge.DEFAULT_KAFKA_TOPIC,
        )
        self.assertEqual(self.bridge.derive_device_id("/tenant/devices/cam-07/video"), "cam-07")
        self.assertEqual(self.bridge.derive_device_id("orphan-topic"), "orphan-topic")
        self.assertEqual(self.bridge.derive_device_id("/"), "unknown")
        self.assertEqual(self.bridge.pick_key("/tenant/devices/cam-07/video"), b"cam-07")

    def test_env_or_secret_file_prefers_environment_value(self):
        with patch.dict(
            self.bridge.os.environ,
            {
                "UNIT_SECRET": "from-env",
                "UNIT_SECRET_FILE": "missing-file",
            },
            clear=False,
        ):
            self.assertEqual(self.bridge.env_or_secret_file("UNIT_SECRET"), "from-env")

    def test_env_or_secret_file_reads_file_value(self):
        secret_path = REPO_ROOT / "secrets" / "unit_bridge_secret.txt"
        secret_path.parent.mkdir(exist_ok=True)
        secret_path.write_text("from-file\n", encoding="utf-8")
        try:
            with patch.dict(
                self.bridge.os.environ,
                {"UNIT_SECRET_FILE": str(secret_path)},
                clear=False,
            ):
                self.assertEqual(self.bridge.env_or_secret_file("UNIT_SECRET"), "from-file")
        finally:
            secret_path.unlink(missing_ok=True)

    def test_build_event_sensor_and_gps_and_media(self):
        sensor_msg = types.SimpleNamespace(
            topic="tenant/devices/sensor-1/sensor",
            payload=json.dumps({"timestamp": "2026-01-01T00:00:00+00:00", "v": 4}).encode(),
            qos=1,
            retain=False,
        )
        topic, key, event = self.bridge.build_event(sensor_msg)
        self.assertEqual(topic, "raw.sensor")
        self.assertEqual(key, b"sensor-1")
        self.assertEqual(event["payload"]["v"], 4)

        gps_msg = types.SimpleNamespace(
            topic="tenant/devices/veh-1/gnss/fix",
            payload=json.dumps({"lat": 1.1, "lon": 2.2, "speed": 9.9}).encode(),
            qos=0,
            retain=False,
        )
        topic, _key, event = self.bridge.build_event(gps_msg)
        self.assertEqual(topic, "raw.gps")
        self.assertEqual(event["latitude"], 1.1)
        self.assertEqual(event["longitude"], 2.2)
        self.assertEqual(event["speed_m_s"], 9.9)

        media_msg = types.SimpleNamespace(
            topic="tenant/devices/cam-1/video2d",
            payload=json.dumps({"frame": 12}).encode(),
            qos=1,
            retain=True,
        )
        with patch.object(self.bridge, "now_iso", return_value="2026-01-01T00:00:00+00:00"):
            topic, _key, event = self.bridge.build_event(media_msg)
        self.assertEqual(topic, "raw.video2d.meta")
        self.assertEqual(event["device_id"], "cam-1")
        self.assertEqual(event["frame"], 12)

    def test_route_event_sends_invalid_media_metadata_to_dlq(self):
        msg = types.SimpleNamespace(topic="tenant/devices/cam-1/video2d")
        event = {
            "device_id": "cam-1",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "frame": 12,
        }

        topic, routed = self.bridge.route_event(msg, "raw.video2d.meta", event)

        self.assertEqual(topic, self.bridge.DLQ_TOPIC)
        self.assertEqual(routed["intended_topic"], "raw.video2d.meta")
        self.assertIn("missing required field: bucket", routed["errors"])
        self.assertIn("field not allowed by raw.video2d.meta: frame", routed["errors"])

    def test_route_event_keeps_valid_media_metadata_on_raw_topic(self):
        msg = types.SimpleNamespace(topic="tenant/devices/cam-1/video2d")
        event = {
            "device_id": "cam-1",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "ingested_at": "2026-01-01T00:00:01+00:00",
            "bucket": "media-raw-2d-videos",
            "object_key": "cam-1/file.mp4",
            "object_uri": "s3://media-raw-2d-videos/cam-1/file.mp4",
            "format": "mp4",
            "source": "mqtt-bridge",
            "mqtt_topic": msg.topic,
            "qos": 1,
            "retain": False,
        }

        topic, routed = self.bridge.route_event(msg, "raw.video2d.meta", event)

        self.assertEqual(topic, "raw.video2d.meta")
        self.assertEqual(routed, event)

    def test_on_connect_subscribes_on_success(self):
        client = _FakeClient()
        self.bridge.on_connect(client, None, None, 0)
        self.assertIn((self.bridge.MQTT_TOPIC, 1), client.subscriptions)

    def test_on_connect_failure_does_not_subscribe(self):
        client = _FakeClient()
        self.bridge.on_connect(client, None, None, 2)
        self.assertEqual(client.subscriptions, [])

    def test_on_message_sends_and_registers_callbacks(self):
        future = Mock()
        fake_producer = Mock()
        fake_producer.send.return_value = future
        msg = types.SimpleNamespace(
            topic="tenant/devices/sensor-1/sensor",
            payload=b'{"value": 5}',
            qos=0,
            retain=False,
        )

        with patch.object(self.bridge, "producer", fake_producer):
            self.bridge.on_message(None, None, msg)

        fake_producer.send.assert_called_once()
        sent_topic = fake_producer.send.call_args.args[0]
        self.assertEqual(sent_topic, "raw.sensor")
        future.add_callback.assert_called_once_with(self.bridge.on_send_success)
        future.add_errback.assert_called_once_with(self.bridge.on_send_error)

    def test_run_bridge_retries_after_oserror(self):
        client = Mock()
        client.connect.side_effect = [OSError("offline"), KeyboardInterrupt()]

        with (
            patch.object(self.bridge.time, "sleep") as mock_sleep,
            self.assertRaises(KeyboardInterrupt),
        ):
            self.bridge.run_bridge(client)

        mock_sleep.assert_called_once_with(5)
        client.loop_forever.assert_not_called()

    def test_main_sets_credentials_and_runs_bridge(self):
        client = _FakeClient()
        with (
            patch.object(self.bridge, "MQTT_USERNAME", "user"),
            patch.object(self.bridge, "MQTT_PASSWORD", "pass"),
            patch.object(self.bridge.mqtt_client, "Client", return_value=client),
            patch.object(self.bridge, "run_bridge") as mock_run,
        ):
            self.bridge.main()

        self.assertEqual(client.username, "user")
        self.assertEqual(client.password, "pass")
        self.assertEqual(client.on_connect, self.bridge.on_connect)
        self.assertEqual(client.on_message, self.bridge.on_message)
        mock_run.assert_called_once_with(client)

    def test_main_raises_when_mqtt_credentials_are_partial(self):
        with (
            patch.object(self.bridge, "MQTT_USERNAME", "user"),
            patch.object(self.bridge, "MQTT_PASSWORD", None),
            self.assertRaisesRegex(
                ValueError,
                "MQTT_USERNAME and MQTT_PASSWORD must both be set when MQTT auth is enabled",
            ),
        ):
            self.bridge.main()


if __name__ == "__main__":
    unittest.main()
