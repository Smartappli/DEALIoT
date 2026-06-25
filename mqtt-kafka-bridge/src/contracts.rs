use chrono::Utc;
use serde_json::{json, Map, Value};
use std::collections::{BTreeSet, HashMap};

pub const DLQ_TOPIC: &str = "dlq.events";
pub const RAW_SENSOR_TOPIC: &str = "raw.sensor";
pub const RAW_GPS_TOPIC: &str = "raw.gps";
pub const RAW_IMAGE2D_META_TOPIC: &str = "raw.image2d.meta";
pub const RAW_IMAGE3D_META_TOPIC: &str = "raw.image3d.meta";
pub const RAW_VIDEO2D_META_TOPIC: &str = "raw.video2d.meta";
pub const RAW_VIDEO3D_META_TOPIC: &str = "raw.video3d.meta";

const LATITUDE_MIN: f64 = -90.0;
const LATITUDE_MAX: f64 = 90.0;
const LONGITUDE_MIN: f64 = -180.0;
const LONGITUDE_MAX: f64 = 180.0;
const HEADING_MIN: f64 = 0.0;
const HEADING_MAX: f64 = 360.0;

pub fn now_iso() -> String {
    Utc::now().to_rfc3339()
}

pub fn build_dlq_event(
    source: &str,
    intended_topic: &str,
    errors: Vec<String>,
    raw_event: &Map<String, Value>,
) -> Value {
    json!({
        "timestamp": now_iso(),
        "source": source,
        "intended_topic": intended_topic,
        "source_topic": raw_event
            .get("source_topic")
            .or_else(|| raw_event.get("mqtt_topic"))
            .or_else(|| raw_event.get("object_uri"))
            .and_then(Value::as_str)
            .unwrap_or(""),
        "device_id": raw_event
            .get("device_id")
            .map(value_to_string)
            .unwrap_or_else(|| "unknown".to_string()),
        "errors": errors,
        "raw_event": raw_event,
    })
}

pub fn validate_event(topic: &str, event: &Map<String, Value>) -> Vec<String> {
    let mut errors = Vec::new();
    let required_by_topic = required_fields();
    let Some(required) = required_by_topic.get(topic) else {
        return errors;
    };

    for field in required {
        if event.get(*field).is_none_or(is_empty_value) {
            errors.push(format!("missing required field: {field}"));
        }
    }

    if media_topics().contains(topic) {
        let allowed_by_topic = media_allowed_fields();
        if let Some(allowed) = allowed_by_topic.get(topic) {
            for field in sorted_keys(event) {
                if !allowed.contains(field.as_str()) {
                    errors.push(format!("field not allowed by {topic}: {field}"));
                }
            }
        }
    }

    validate_types(event, &mut errors);
    validate_ranges(event, &mut errors);
    errors
}

fn required_fields() -> HashMap<&'static str, BTreeSet<&'static str>> {
    HashMap::from([
        (
            RAW_SENSOR_TOPIC,
            fields(&["device_id", "payload", "timestamp"]),
        ),
        (
            RAW_GPS_TOPIC,
            fields(&["device_id", "latitude", "longitude", "timestamp"]),
        ),
        (
            RAW_IMAGE2D_META_TOPIC,
            fields(&[
                "bucket",
                "device_id",
                "format",
                "object_key",
                "object_uri",
                "timestamp",
            ]),
        ),
        (
            RAW_IMAGE3D_META_TOPIC,
            fields(&[
                "bucket",
                "device_id",
                "format",
                "object_key",
                "object_uri",
                "timestamp",
            ]),
        ),
        (
            RAW_VIDEO2D_META_TOPIC,
            fields(&[
                "bucket",
                "device_id",
                "format",
                "object_key",
                "object_uri",
                "timestamp",
            ]),
        ),
        (
            RAW_VIDEO3D_META_TOPIC,
            fields(&[
                "bucket",
                "device_id",
                "format",
                "object_key",
                "object_uri",
                "timestamp",
            ]),
        ),
    ])
}

fn media_allowed_fields() -> HashMap<&'static str, BTreeSet<&'static str>> {
    HashMap::from([
        (
            RAW_IMAGE2D_META_TOPIC,
            fields(&[
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
            ]),
        ),
        (
            RAW_IMAGE3D_META_TOPIC,
            fields(&[
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
            ]),
        ),
        (
            RAW_VIDEO2D_META_TOPIC,
            fields(&[
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
            ]),
        ),
        (
            RAW_VIDEO3D_META_TOPIC,
            fields(&[
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
            ]),
        ),
    ])
}

fn media_topics() -> BTreeSet<&'static str> {
    fields(&[
        RAW_IMAGE2D_META_TOPIC,
        RAW_IMAGE3D_META_TOPIC,
        RAW_VIDEO2D_META_TOPIC,
        RAW_VIDEO3D_META_TOPIC,
    ])
}

fn validate_types(event: &Map<String, Value>, errors: &mut Vec<String>) {
    for field in sorted_intersection(event, string_fields()) {
        if event
            .get(&field)
            .is_some_and(|value| !value.is_null() && !value.is_string())
        {
            errors.push(format!("field must be a string: {field}"));
        }
    }
    for field in sorted_intersection(event, integer_fields()) {
        if event
            .get(&field)
            .is_some_and(|value| !value.is_null() && !value.is_i64())
        {
            errors.push(format!("field must be an integer: {field}"));
        }
    }
    for field in sorted_intersection(event, number_fields()) {
        if event
            .get(&field)
            .is_some_and(|value| !value.is_null() && !value.is_number())
        {
            errors.push(format!("field must be numeric: {field}"));
        }
    }
    if event.get("payload").is_some_and(|value| !value.is_object()) {
        errors.push("field must be an object: payload".to_string());
    }
    if event.get("tags").is_some_and(|value| !value.is_object()) {
        errors.push("field must be an object: tags".to_string());
    }
    if event.get("retain").is_some_and(|value| !value.is_boolean()) {
        errors.push("field must be a boolean: retain".to_string());
    }
}

fn validate_ranges(event: &Map<String, Value>, errors: &mut Vec<String>) {
    if event
        .get("latitude")
        .and_then(Value::as_f64)
        .is_some_and(|value| !(LATITUDE_MIN..=LATITUDE_MAX).contains(&value))
    {
        errors.push("latitude out of range: -90..90".to_string());
    }
    if event
        .get("longitude")
        .and_then(Value::as_f64)
        .is_some_and(|value| !(LONGITUDE_MIN..=LONGITUDE_MAX).contains(&value))
    {
        errors.push("longitude out of range: -180..180".to_string());
    }
    if event
        .get("heading_deg")
        .and_then(Value::as_f64)
        .is_some_and(|value| !(HEADING_MIN..=HEADING_MAX).contains(&value))
    {
        errors.push("heading_deg out of range: 0..360".to_string());
    }

    for field in [
        "duration_ms",
        "frame_count",
        "point_count",
        "size_bytes",
        "speed_m_s",
    ] {
        if event
            .get(field)
            .and_then(Value::as_f64)
            .is_some_and(|value| value < 0.0)
        {
            errors.push(format!("{field} must be non-negative"));
        }
    }
    for field in ["frame_rate", "height", "views", "width"] {
        if event
            .get(field)
            .and_then(Value::as_f64)
            .is_some_and(|value| value <= 0.0)
        {
            errors.push(format!("{field} must be positive"));
        }
    }
}

fn value_to_string(value: &Value) -> String {
    value
        .as_str()
        .map_or_else(|| value.to_string(), ToString::to_string)
}

fn is_empty_value(value: &Value) -> bool {
    value.is_null() || value.as_str() == Some("")
}

fn fields(items: &[&'static str]) -> BTreeSet<&'static str> {
    items.iter().copied().collect()
}

fn sorted_keys(event: &Map<String, Value>) -> Vec<String> {
    let mut keys: Vec<_> = event.keys().cloned().collect();
    keys.sort();
    keys
}

fn sorted_intersection(event: &Map<String, Value>, fields: BTreeSet<&'static str>) -> Vec<String> {
    sorted_keys(event)
        .into_iter()
        .filter(|field| fields.contains(field.as_str()))
        .collect()
}

fn string_fields() -> BTreeSet<&'static str> {
    fields(&[
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
    ])
}

fn integer_fields() -> BTreeSet<&'static str> {
    fields(&[
        "duration_ms",
        "frame_count",
        "height",
        "point_count",
        "qos",
        "size_bytes",
        "views",
        "width",
    ])
}

fn number_fields() -> BTreeSet<&'static str> {
    fields(&[
        "altitude_m",
        "frame_rate",
        "heading_deg",
        "latitude",
        "longitude",
        "speed_m_s",
    ])
}
