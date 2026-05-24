from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

DLQ_TOPIC = "dlq.events"
STATE_LATEST_TOPIC = "state.latest"
LATITUDE_MIN = -90
LATITUDE_MAX = 90
LONGITUDE_MIN = -180
LONGITUDE_MAX = 180
HEADING_MIN = 0
HEADING_MAX = 360

MEDIA_TOPICS = {
    "raw.image2d.meta",
    "raw.image3d.meta",
    "raw.video2d.meta",
    "raw.video3d.meta",
}

REQUIRED_FIELDS: dict[str, set[str]] = {
    "raw.sensor": {"device_id", "timestamp", "payload"},
    "raw.gps": {"device_id", "timestamp", "latitude", "longitude"},
    "raw.image2d.meta": {"device_id", "timestamp", "bucket", "object_key", "object_uri", "format"},
    "raw.image3d.meta": {"device_id", "timestamp", "bucket", "object_key", "object_uri", "format"},
    "raw.video2d.meta": {"device_id", "timestamp", "bucket", "object_key", "object_uri", "format"},
    "raw.video3d.meta": {"device_id", "timestamp", "bucket", "object_key", "object_uri", "format"},
}

MEDIA_ALLOWED_FIELDS: dict[str, set[str]] = {
    "raw.image2d.meta": {
        "bucket",
        "camera_id",
        "checksum",
        "content_type",
        "device_id",
        "format",
        "height",
        "ingested_at",
        "mqtt_topic",
        "object_key",
        "object_uri",
        "qos",
        "retain",
        "size_bytes",
        "source",
        "tags",
        "timestamp",
        "width",
    },
    "raw.image3d.meta": {
        "bucket",
        "capture_type",
        "checksum",
        "content_type",
        "coordinate_frame",
        "device_id",
        "format",
        "ingested_at",
        "mqtt_topic",
        "object_key",
        "object_uri",
        "point_count",
        "qos",
        "retain",
        "sensor_id",
        "size_bytes",
        "source",
        "tags",
        "timestamp",
    },
    "raw.video2d.meta": {
        "bucket",
        "camera_id",
        "checksum",
        "codec",
        "content_type",
        "device_id",
        "duration_ms",
        "format",
        "frame_count",
        "frame_rate",
        "height",
        "ingested_at",
        "mqtt_topic",
        "object_key",
        "object_uri",
        "qos",
        "retain",
        "size_bytes",
        "source",
        "tags",
        "timestamp",
        "width",
    },
    "raw.video3d.meta": {
        "bucket",
        "checksum",
        "codec",
        "content_type",
        "device_id",
        "duration_ms",
        "format",
        "frame_count",
        "frame_rate",
        "height",
        "ingested_at",
        "mqtt_topic",
        "object_key",
        "object_uri",
        "qos",
        "representation",
        "retain",
        "rig_id",
        "size_bytes",
        "source",
        "tags",
        "timestamp",
        "views",
        "width",
    },
}

STRING_FIELDS = {
    "bucket",
    "camera_id",
    "capture_type",
    "checksum",
    "codec",
    "content_type",
    "coordinate_frame",
    "device_id",
    "format",
    "ingested_at",
    "mqtt_topic",
    "object_key",
    "object_uri",
    "representation",
    "rig_id",
    "sensor_id",
    "source",
    "timestamp",
}

INTEGER_FIELDS = {
    "duration_ms",
    "frame_count",
    "height",
    "point_count",
    "qos",
    "size_bytes",
    "views",
    "width",
}

NUMBER_FIELDS = {"altitude_m", "frame_rate", "heading_deg", "latitude", "longitude", "speed_m_s"}


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def event_time(record: dict[str, Any]) -> str:
    value = record.get("timestamp") or record.get("ingested_at")
    if value is None:
        return ""
    return str(value)


def build_dlq_event(
    *,
    source: str,
    intended_topic: str,
    errors: list[str],
    raw_event: dict[str, Any],
    source_topic: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    return {
        "timestamp": timestamp or now_iso(),
        "source": source,
        "intended_topic": intended_topic,
        "source_topic": source_topic or raw_event.get("mqtt_topic", ""),
        "device_id": str(raw_event.get("device_id", "unknown")),
        "errors": errors,
        "raw_event": raw_event,
    }


def validate_event(topic: str, event: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    required = REQUIRED_FIELDS.get(topic)
    if required is None:
        return errors

    for field in sorted(required):
        if field not in event or event[field] in (None, ""):
            errors.append(f"missing required field: {field}")

    if topic in MEDIA_TOPICS:
        allowed = MEDIA_ALLOWED_FIELDS[topic]
        for field in sorted(set(event) - allowed):
            errors.append(f"field not allowed by {topic}: {field}")

    _validate_types(event, errors)
    _validate_ranges(event, errors)
    return errors


def _validate_types(event: dict[str, Any], errors: list[str]) -> None:
    for field in sorted(STRING_FIELDS & set(event)):
        if event[field] is not None and not isinstance(event[field], str):
            errors.append(f"field must be a string: {field}")

    for field in sorted(INTEGER_FIELDS & set(event)):
        if event[field] is not None and not isinstance(event[field], int):
            errors.append(f"field must be an integer: {field}")

    for field in sorted(NUMBER_FIELDS & set(event)):
        if event[field] is not None and not isinstance(event[field], int | float):
            errors.append(f"field must be numeric: {field}")

    if "payload" in event and not isinstance(event["payload"], dict):
        errors.append("field must be an object: payload")
    if "tags" in event and not isinstance(event["tags"], dict):
        errors.append("field must be an object: tags")
    if "retain" in event and not isinstance(event["retain"], bool):
        errors.append("field must be a boolean: retain")


def _validate_ranges(event: dict[str, Any], errors: list[str]) -> None:
    latitude = event.get("latitude")
    if isinstance(latitude, int | float) and not LATITUDE_MIN <= latitude <= LATITUDE_MAX:
        errors.append("latitude out of range: -90..90")

    longitude = event.get("longitude")
    if isinstance(longitude, int | float) and not LONGITUDE_MIN <= longitude <= LONGITUDE_MAX:
        errors.append("longitude out of range: -180..180")

    heading = event.get("heading_deg")
    if isinstance(heading, int | float) and not HEADING_MIN <= heading <= HEADING_MAX:
        errors.append("heading_deg out of range: 0..360")

    non_negative = [
        "duration_ms",
        "frame_count",
        "point_count",
        "size_bytes",
        "speed_m_s",
    ]
    for field in non_negative:
        value = event.get(field)
        if isinstance(value, int | float) and value < 0:
            errors.append(f"{field} must be non-negative")

    positive = ["frame_rate", "height", "views", "width"]
    for field in positive:
        value = event.get(field)
        if isinstance(value, int | float) and value <= 0:
            errors.append(f"{field} must be positive")
