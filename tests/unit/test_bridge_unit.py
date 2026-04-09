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

import pytest

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
        self.assertEqual(self.bridge.pick_kafka_topic("devices/a1/lidar/frame"), "raw.image3d.meta")
        self.assertEqual(
            self.bridge.pick_kafka_topic("devices/a1/unknown"),
            self.bridge.DEFAULT_KAFKA_TOPIC,
        )
        self.assertEqual(self.bridge.derive_device_id("/tenant/devices/cam-07/video"), "cam-07")
        self.assertEqual(self.bridge.derive_device_id("orphan-topic"), "orphan-topic")
        self.assertEqual(self.bridge.pick_key("/tenant/devices/cam-07/video"), b"cam-07")

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

    def test_on_connect_subscribes_on_success(self):
        client = _FakeClient()
        self.bridge.on_connect(client, None, None, 0)
        self.assertIn((self.bridge.MQTT_TOPIC, 1), client.subscriptions)

    def test_on_connect_failure_does_not_subscribe(self):
        client = _FakeClient()
        self.bridge.on_connect(client, None, None, 2)
        self.assertEqual(client.subscriptions, [])

    def test_on_message_sends_and_registers_callbacks(self):
        fake_producer = _FakeKafkaProducer()
        msg = types.SimpleNamespace(
            topic="tenant/devices/sensor-1/sensor",
            payload=b'{"value": 5}',
            qos=0,
            retain=False,
        )

        with patch.object(self.bridge, "producer", fake_producer):
            self.bridge.on_message(None, None, msg)

        self.assertEqual(len(fake_producer.sent), 1)
        sent_topic, _key, _value = fake_producer.sent[0]
        self.assertEqual(sent_topic, "raw.sensor")

    def test_main_raises_when_mqtt_credentials_are_partial(self):
        with (
            patch.object(self.bridge, "MQTT_USERNAME", "user"),
            patch.object(self.bridge, "MQTT_PASSWORD", None),
            pytest.raises(
                ValueError,
                match="MQTT_USERNAME and MQTT_PASSWORD must both be set when MQTT auth is enabled",
            ),
        ):
            self.bridge.main()


if __name__ == "__main__":
    unittest.main()
