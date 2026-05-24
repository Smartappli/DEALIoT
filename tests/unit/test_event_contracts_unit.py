from __future__ import annotations

import unittest

from dealiot_contracts import DLQ_TOPIC, build_dlq_event, event_time, validate_event


class EventContractsUnitTests(unittest.TestCase):
    def test_validates_required_media_metadata(self) -> None:
        event = {
            "device_id": "cam-1",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "bucket": "media-raw-2d-images",
            "object_key": "cam-1/frame.jpg",
            "object_uri": "s3://media-raw-2d-images/cam-1/frame.jpg",
            "format": "jpg",
            "size_bytes": 10,
        }

        self.assertEqual(validate_event("raw.image2d.meta", event), [])

    def test_rejects_extra_media_fields_and_invalid_ranges(self) -> None:
        event = {
            "device_id": "cam-1",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "bucket": "media-raw-2d-images",
            "object_key": "cam-1/frame.jpg",
            "object_uri": "s3://media-raw-2d-images/cam-1/frame.jpg",
            "format": "jpg",
            "size_bytes": -1,
            "frame": 12,
        }

        errors = validate_event("raw.image2d.meta", event)

        self.assertIn("field not allowed by raw.image2d.meta: frame", errors)
        self.assertIn("size_bytes must be non-negative", errors)

    def test_builds_dlq_event(self) -> None:
        dlq = build_dlq_event(
            source="unit-test",
            intended_topic="raw.sensor",
            errors=["bad payload"],
            raw_event={"device_id": "dev-1"},
            source_topic="mqtt/topic",
            timestamp="2026-01-01T00:00:00+00:00",
        )

        self.assertEqual(DLQ_TOPIC, "dlq.events")
        self.assertEqual(dlq["timestamp"], "2026-01-01T00:00:00+00:00")
        self.assertEqual(dlq["source_topic"], "mqtt/topic")
        self.assertEqual(dlq["errors"], ["bad payload"])

    def test_event_time_prefers_event_timestamp_over_ingestion_timestamp(self) -> None:
        self.assertEqual(
            event_time(
                {
                    "timestamp": "2026-01-01T00:00:00+00:00",
                    "ingested_at": "2026-01-01T00:00:01+00:00",
                }
            ),
            "2026-01-01T00:00:00+00:00",
        )


if __name__ == "__main__":
    unittest.main()
