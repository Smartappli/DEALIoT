import atexit
import base64
import json
import logging
import os
import time
import uuid
from datetime import UTC, datetime
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from kafka import KafkaProducer
from kafka.errors import KafkaError
from paho.mqtt import client as mqtt_client

from dealiot_contracts import DLQ_TOPIC, build_dlq_event, now_iso, validate_event

LOGGER = logging.getLogger(__name__)
RAW_SENSOR_TOPIC = "raw.sensor"
RAW_GPS_TOPIC = "raw.gps"
DEFAULT_MQTT_TOPICS = "$share/ingestors/devices/#,$share/ingestors/wildfi/#"
UNIX_MILLISECONDS_THRESHOLD = 10_000_000_000
WILDFI_TOPIC_MARKERS = {"wildfi", "wild-fi"}
WILDFI_TAG_MARKERS = {"tags", "tag", "devices"}
WILDFI_SENSOR_MARKERS = {
    "acc",
    "accelerometer",
    "bme",
    "decoded",
    "environment",
    "gateway",
    "imu",
    "mag",
    "metadata",
    "move",
    "movement",
    "prox",
    "proximity",
    "sensor",
    "telemetry",
}


def env_or_secret_file(name: str) -> str | None:
    value = os.getenv(name)
    if value:
        return value

    secret_file = os.getenv(f"{name}_FILE")
    if not secret_file:
        return None

    with Path(secret_file).open(encoding="utf-8") as handle:
        return handle.read().strip()


def csv_env_or_default(name: str, default: str) -> tuple[str, ...]:
    value = os.getenv(name, default)
    topics = tuple(item.strip() for item in value.split(",") if item.strip())
    if not topics:
        return tuple(item.strip() for item in default.split(",") if item.strip())
    return topics


MQTT_HOST = os.getenv("MQTT_HOST", "vernemq1")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = env_or_secret_file("MQTT_PASSWORD")
legacy_mqtt_topic = os.getenv("MQTT_TOPIC")
MQTT_TOPICS_DEFAULT = (
    legacy_mqtt_topic if legacy_mqtt_topic and legacy_mqtt_topic.strip() else DEFAULT_MQTT_TOPICS
)
MQTT_TOPICS = csv_env_or_default("MQTT_TOPICS", MQTT_TOPICS_DEFAULT)
MQTT_TOPIC = MQTT_TOPICS[0]
WILDFI_TOPIC_PREFIXES = csv_env_or_default("WILDFI_TOPIC_PREFIXES", "wildfi,wild-fi")

KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "kafka1:9092,kafka2:9092,kafka3:9092",
).split(",")

DEFAULT_KAFKA_TOPIC = os.getenv("DEFAULT_KAFKA_TOPIC", RAW_SENSOR_TOPIC)


def decode_payload(payload: bytes) -> Any:
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, JSONDecodeError):
        return {
            "payload_b64": base64.b64encode(payload).decode("ascii"),
        }


def is_wildfi_topic(topic: str) -> bool:
    parts = {part.lower() for part in topic.split("/") if part}
    prefixes = {prefix.lower() for prefix in WILDFI_TOPIC_PREFIXES}
    return bool(parts & (WILDFI_TOPIC_MARKERS | prefixes))


def normalized_timestamp(value: Any, fallback: str) -> str:
    if value in (None, ""):
        return fallback
    if isinstance(value, int | float):
        seconds = value / 1000 if value > UNIX_MILLISECONDS_THRESHOLD else value
        return datetime.fromtimestamp(seconds, UTC).isoformat()
    return str(value)


def pick_event_timestamp(decoded: Any, fallback: str) -> str:
    if not isinstance(decoded, dict):
        return fallback

    for field in ("timestamp", "utcTimestamp", "utc_timestamp", "time"):
        if field in decoded:
            return normalized_timestamp(decoded[field], fallback)

    return fallback


def pick_kafka_topic(topic: str) -> str:
    lowered = topic.lower()

    if "gps" in lowered or "/gnss/" in lowered or "rawgps" in lowered:
        kafka_topic = RAW_GPS_TOPIC
    elif "video3d" in lowered or "/stereo-video/" in lowered or "/volumetric-video/" in lowered:
        kafka_topic = "raw.video3d.meta"
    elif "video2d" in lowered or "/video/" in lowered or "/camera-stream/" in lowered:
        kafka_topic = "raw.video2d.meta"
    elif "image2d" in lowered or "/camera/" in lowered or "/image/" in lowered:
        kafka_topic = "raw.image2d.meta"
    elif "image3d" in lowered or "/lidar/" in lowered or "/pointcloud/" in lowered:
        kafka_topic = "raw.image3d.meta"
    elif "sensor" in lowered or (
        is_wildfi_topic(topic) and any(marker in lowered for marker in WILDFI_SENSOR_MARKERS)
    ):
        kafka_topic = RAW_SENSOR_TOPIC
    else:
        kafka_topic = DEFAULT_KAFKA_TOPIC

    return kafka_topic


def derive_device_id(topic: str) -> str:
    parts = [part for part in topic.split("/") if part]
    lowered_parts = [part.lower() for part in parts]

    for marker in WILDFI_TAG_MARKERS:
        if marker in lowered_parts:
            idx = lowered_parts.index(marker)
            if idx + 1 < len(parts):
                return parts[idx + 1]

    for marker in WILDFI_TOPIC_MARKERS | {prefix.lower() for prefix in WILDFI_TOPIC_PREFIXES}:
        if marker in lowered_parts:
            idx = lowered_parts.index(marker)
            next_idx = idx + 1
            if next_idx < len(parts) and lowered_parts[next_idx] not in WILDFI_SENSOR_MARKERS:
                return parts[next_idx]
            if next_idx + 1 < len(parts):
                return parts[next_idx + 1]

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


def on_send_error(exc: KafkaError) -> None:
    LOGGER.error("Kafka send failed: %s", exc)


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
        for topic in MQTT_TOPICS:
            client.subscribe(topic, qos=1)
            LOGGER.info("Subscribed to %s", topic)
        return

    LOGGER.error("Failed to connect to MQTT broker, rc=%s", rc)


def event_source_for_topic(topic: str) -> str:
    if is_wildfi_topic(topic):
        return "wildfi-mqtt"
    return "mqtt-bridge"


def build_event(msg) -> tuple[str, bytes, dict[str, Any]]:
    kafka_topic = pick_kafka_topic(msg.topic)
    device_id = derive_device_id(msg.topic)
    decoded = decode_payload(msg.payload)
    ingested_at = now_iso()
    timestamp = pick_event_timestamp(decoded, ingested_at)
    source = event_source_for_topic(msg.topic)

    if kafka_topic == RAW_SENSOR_TOPIC:
        payload = decoded if isinstance(decoded, dict) else {"value": decoded}
        event = {
            "device_id": device_id,
            "timestamp": timestamp,
            "ingested_at": ingested_at,
            "payload": payload,
            "mqtt_topic": msg.topic,
            "qos": msg.qos,
            "retain": msg.retain,
            "source": source,
        }
    elif kafka_topic == RAW_GPS_TOPIC:
        payload = decoded if isinstance(decoded, dict) else {}
        event = {
            "device_id": device_id,
            "timestamp": pick_event_timestamp(payload, timestamp),
            "ingested_at": ingested_at,
            "latitude": payload.get(
                "latitude", payload.get("latitude_deg", payload.get("lat", 0.0))
            ),
            "longitude": payload.get(
                "longitude",
                payload.get("longitude_deg", payload.get("lon", 0.0)),
            ),
            "altitude_m": payload.get("altitude_m", payload.get("altitude")),
            "speed_m_s": payload.get("speed_m_s", payload.get("speed")),
            "heading_deg": payload.get("heading_deg", payload.get("heading")),
            "mqtt_topic": msg.topic,
            "qos": msg.qos,
            "retain": msg.retain,
            "payload": payload,
            "source": source,
        }
    else:
        payload = decoded if isinstance(decoded, dict) else {}
        event = {
            **payload,
            "device_id": payload.get("device_id", device_id),
            "timestamp": payload.get("timestamp", timestamp),
            "ingested_at": ingested_at,
            "mqtt_topic": msg.topic,
            "qos": msg.qos,
            "retain": msg.retain,
            "source": source,
        }

    return kafka_topic, pick_key(msg.topic), event


def route_event(msg, kafka_topic: str, event: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    errors = validate_event(kafka_topic, event)
    if not errors:
        return kafka_topic, event

    LOGGER.warning(
        "Routing invalid MQTT event to DLQ intended_topic=%s mqtt_topic=%s errors=%s",
        kafka_topic,
        msg.topic,
        errors,
    )
    return DLQ_TOPIC, build_dlq_event(
        source="mqtt-bridge",
        intended_topic=kafka_topic,
        errors=errors,
        raw_event=event,
    )


def on_message(_client, _userdata, msg) -> None:
    kafka_topic, key, event = build_event(msg)
    send_topic, send_event = route_event(msg, kafka_topic, event)
    future = producer.send(send_topic, key=key, value=send_event)
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
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    elif MQTT_USERNAME or MQTT_PASSWORD:
        raise ValueError(
            "MQTT_USERNAME and MQTT_PASSWORD must both be set when MQTT auth is enabled",
        )
    client.on_connect = on_connect
    client.on_message = on_message

    run_bridge(client)


if __name__ == "__main__":
    main()
