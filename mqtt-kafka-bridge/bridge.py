import atexit
import base64
import json
import logging
import os
import time
import uuid
from datetime import UTC, datetime
from json import JSONDecodeError
from typing import Any

from kafka import KafkaProducer
from kafka.errors import KafkaError
from paho.mqtt import client as mqtt_client

LOGGER = logging.getLogger(__name__)

MQTT_HOST = os.getenv("MQTT_HOST", "vernemq1")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "admin")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "change-this-password")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "$share/ingestors/devices/#")

KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "kafka1:9092,kafka2:9092,kafka3:9092",
).split(",")

DEFAULT_KAFKA_TOPIC = os.getenv("DEFAULT_KAFKA_TOPIC", "raw.sensor")


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def decode_payload(payload: bytes) -> Any:
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, JSONDecodeError):
        return {
            "payload_b64": base64.b64encode(payload).decode("ascii"),
        }


def pick_kafka_topic(topic: str) -> str:
    lowered = topic.lower()

    if "gps" in lowered or "/gnss/" in lowered:
        kafka_topic = "raw.gps"
    elif "video3d" in lowered or "/stereo-video/" in lowered or "/volumetric-video/" in lowered:
        kafka_topic = "raw.video3d.meta"
    elif "video2d" in lowered or "/video/" in lowered or "/camera-stream/" in lowered:
        kafka_topic = "raw.video2d.meta"
    elif "image2d" in lowered or "/camera/" in lowered or "/image/" in lowered:
        kafka_topic = "raw.image2d.meta"
    elif "image3d" in lowered or "/lidar/" in lowered or "/pointcloud/" in lowered:
        kafka_topic = "raw.image3d.meta"
    elif "sensor" in lowered:
        kafka_topic = "raw.sensor"
    else:
        kafka_topic = DEFAULT_KAFKA_TOPIC

    return kafka_topic


def derive_device_id(topic: str) -> str:
    parts = [part for part in topic.split("/") if part]

    if "devices" in parts:
        idx = parts.index("devices")
        if idx + 1 < len(parts):
            return parts[idx + 1]

    if parts:
        return parts[-1]

    return "unknown"


def pick_key(topic: str) -> bytes:
    return derive_device_id(topic).encode("utf-8", errors="ignore")


def on_send_success(record_metadata) -> None:
    LOGGER.info(
        "Forwarded MQTT message to Kafka topic=%s partition=%s offset=%s",
        record_metadata.topic,
        record_metadata.partition,
        record_metadata.offset,
    )


def on_send_error(_exc: KafkaError) -> None:
    LOGGER.exception("Kafka send failed")


producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    acks="all",
    retries=10,
    linger_ms=50,
    batch_size=131072,
    buffer_memory=67108864,
    compression_type="lz4",
    max_in_flight_requests_per_connection=1,
)

atexit.register(lambda: producer.flush(timeout=10))

mqtt_client_id = f"mqtt-kafka-bridge-{uuid.uuid4().hex[:12]}"


def on_connect(client, _userdata, _flags, rc, properties=None) -> None:
    del properties

    if rc == 0:
        LOGGER.info("Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC, qos=1)
        LOGGER.info("Subscribed to %s", MQTT_TOPIC)
        return

    LOGGER.error("Failed to connect to MQTT broker, rc=%s", rc)


def build_event(msg) -> tuple[str, bytes, dict[str, Any]]:
    kafka_topic = pick_kafka_topic(msg.topic)
    device_id = derive_device_id(msg.topic)
    decoded = decode_payload(msg.payload)
    timestamp = decoded.get("timestamp", now_iso()) if isinstance(decoded, dict) else now_iso()

    if kafka_topic == "raw.sensor":
        payload = decoded if isinstance(decoded, dict) else {"value": decoded}
        event = {
            "device_id": device_id,
            "timestamp": timestamp,
            "payload": payload,
            "mqtt_topic": msg.topic,
            "qos": msg.qos,
            "retain": msg.retain,
            "source": "mqtt-bridge",
        }
    elif kafka_topic == "raw.gps":
        payload = decoded if isinstance(decoded, dict) else {}
        event = {
            "device_id": device_id,
            "timestamp": payload.get("timestamp", timestamp),
            "latitude": payload.get("latitude", payload.get("lat", 0.0)),
            "longitude": payload.get("longitude", payload.get("lon", 0.0)),
            "altitude_m": payload.get("altitude_m", payload.get("altitude")),
            "speed_m_s": payload.get("speed_m_s", payload.get("speed")),
            "heading_deg": payload.get("heading_deg", payload.get("heading")),
            "mqtt_topic": msg.topic,
            "payload": payload,
            "source": "mqtt-bridge",
        }
    else:
        payload = decoded if isinstance(decoded, dict) else {}
        event = {
            **payload,
            "device_id": payload.get("device_id", device_id),
            "timestamp": payload.get("timestamp", timestamp),
            "mqtt_topic": msg.topic,
            "qos": msg.qos,
            "retain": msg.retain,
            "source": "mqtt-bridge",
        }

    return kafka_topic, pick_key(msg.topic), event


def on_message(_client, _userdata, msg) -> None:
    kafka_topic, key, event = build_event(msg)
    future = producer.send(kafka_topic, key=key, value=event)
    future.add_callback(on_send_success)
    future.add_errback(on_send_error)


def run_bridge(client: mqtt_client.Client) -> None:
    while True:
        try:
            client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
            client.loop_forever()
        except (OSError, KafkaError):
            LOGGER.exception("Bridge error; retry in 5s")
            time.sleep(5)


def main() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    client = mqtt_client.Client(
        mqtt_client.CallbackAPIVersion.VERSION2,
        client_id=mqtt_client_id,
    )
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    run_bridge(client)


if __name__ == "__main__":
    main()
