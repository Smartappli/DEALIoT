from __future__ import annotations

import argparse
import datetime as dt
import importlib
import io
import json
import os
import sys
import types
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch


class MediaBackfillUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fake_kafka = types.ModuleType("kafka")
        fake_kafka.KafkaProducer = object
        with patch.dict(sys.modules, {"kafka": fake_kafka}):
            cls.module = importlib.import_module("pipelines.media_backfill")

    def test_parse_iso8601_and_guess_format(self):
        parsed = self.module.parse_iso8601("2026-02-01T10:11:12Z")
        self.assertEqual(parsed.tzinfo, dt.UTC)
        self.assertEqual(parsed.hour, 10)

        naive = self.module.parse_iso8601("2026-02-01T10:11:12")
        self.assertEqual(naive.tzinfo, dt.UTC)

        self.assertEqual(self.module.guess_format("folder/file.JPG"), "jpg")
        self.assertEqual(self.module.guess_format("folder/noext"), "bin")

    def test_build_record_adds_media_defaults(self):
        obj = {
            "bucket": "media-raw-2d-images",
            "object_key": "capture/frame.png",
            "object_uri": "s3://media-raw-2d-images/capture/frame.png",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "size_bytes": 42,
        }

        record = self.module.build_record(obj, "image2d")
        self.assertEqual(record["camera_id"], "unknown")
        self.assertEqual(record["format"], "png")
        self.assertEqual(record["content_type"], "image/png")
        self.assertEqual(record["tags"]["source"], "airflow-backfill")

    def test_resolve_window_from_explicit_range_and_since_minutes(self):
        args = argparse.Namespace(
            window_start="2026-01-01T00:00:00Z",
            window_end="2026-01-01T01:00:00Z",
            since_minutes=None,
        )
        start, end = self.module.resolve_window(args)
        self.assertEqual(start.isoformat(), "2026-01-01T00:00:00+00:00")
        self.assertEqual(end.isoformat(), "2026-01-01T01:00:00+00:00")

        fixed_now = dt.datetime(2026, 1, 1, 2, 0, 0, tzinfo=dt.UTC)
        fake_datetime = types.SimpleNamespace(now=Mock(return_value=fixed_now))
        with patch.object(self.module, "datetime", fake_datetime):
            args = argparse.Namespace(window_start=None, window_end=None, since_minutes=30)
            start, end = self.module.resolve_window(args)

        self.assertEqual(end, fixed_now)
        self.assertEqual(start, fixed_now - dt.timedelta(minutes=30))

    def test_resolve_window_requires_arguments(self):
        args = argparse.Namespace(window_start=None, window_end=None, since_minutes=None)
        with self.assertRaises(ValueError):
            self.module.resolve_window(args)

    def test_iter_objects_between_filters_time_window(self):
        inside = dt.datetime(2026, 1, 1, 0, 10, tzinfo=dt.UTC)
        outside = dt.datetime(2026, 1, 1, 2, 0, tzinfo=dt.UTC)

        paginator = Mock()
        paginator.paginate.return_value = [
            {
                "Contents": [
                    {"Key": "ok/a.jpg", "Size": 1, "LastModified": inside},
                    {"Key": "skip/b.jpg", "Size": 2, "LastModified": outside},
                ]
            }
        ]

        s3 = Mock()
        s3.get_paginator.return_value = paginator

        with patch.object(self.module, "get_s3_client", return_value=s3):
            rows = list(
                self.module.iter_objects_between(
                    bucket="bucket",
                    prefix="ok/",
                    window_start=dt.datetime(2026, 1, 1, 0, 0, tzinfo=dt.UTC),
                    window_end=dt.datetime(2026, 1, 1, 1, 0, tzinfo=dt.UTC),
                )
            )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["object_key"], "ok/a.jpg")
        self.assertEqual(rows[0]["object_uri"], "s3://bucket/ok/a.jpg")

    def test_get_s3_client_and_kafka_producer_use_environment(self):
        with patch.dict(
            os.environ,
            {
                "S3_ENDPOINT_URL": "http://s3.local",
                "AWS_ACCESS_KEY_ID": "k",
                "AWS_SECRET_ACCESS_KEY": "s",
                "KAFKA_BOOTSTRAP_SERVERS": "k1:9092,k2:9092",
            },
            clear=True,
        ):
            with (
                patch.object(self.module.boto3, "client", return_value="s3-client") as mock_client,
                patch.object(self.module, "KafkaProducer", return_value="producer") as mock_prod,
            ):
                self.assertEqual(self.module.get_s3_client(), "s3-client")
                self.assertEqual(self.module.get_kafka_producer(), "producer")

        mock_client.assert_called_once()
        mock_prod.assert_called_once()

    def test_main_sends_records_and_prints_summary(self):
        args = argparse.Namespace(
            bucket="media-raw-2d-images",
            prefix="cam/",
            since_minutes=15,
            window_start=None,
            window_end=None,
            media_kind="image2d",
        )
        start = dt.datetime(2026, 1, 1, 0, 0, tzinfo=dt.UTC)
        end = dt.datetime(2026, 1, 1, 0, 15, tzinfo=dt.UTC)

        producer = Mock()
        objects = [
            {
                "bucket": "media-raw-2d-images",
                "object_key": "cam/frame-1.jpg",
                "size_bytes": 5,
                "timestamp": "2026-01-01T00:01:00+00:00",
                "object_uri": "s3://media-raw-2d-images/cam/frame-1.jpg",
            }
        ]

        with (
            patch.object(self.module.argparse.ArgumentParser, "parse_args", return_value=args),
            patch.object(self.module, "resolve_window", return_value=(start, end)),
            patch.object(self.module, "get_kafka_producer", return_value=producer),
            patch.object(self.module, "iter_objects_between", return_value=objects),
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                self.module.main()

        producer.send.assert_called_once()
        producer.flush.assert_called_once_with(timeout=30)

        payload = json.loads(output.getvalue())
        self.assertEqual(payload["records_sent"], 1)
        self.assertEqual(payload["topic"], "raw.image2d.meta")


if __name__ == "__main__":
    unittest.main()
