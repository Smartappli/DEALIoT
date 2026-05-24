from __future__ import annotations

import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from typing import Any, ClassVar, cast
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[2]
FLINK_JOB_PATH = REPO_ROOT / "flink" / "jobs" / "streaming_minimal.py"


def _type_string():
    return "STRING"


def _type_int():
    return "INT"


def _type_boolean():
    return "BOOLEAN"


def _row_named(names, types_):
    return ("ROW_NAMED", tuple(names), tuple(types_))


def _tuple_type(types_):
    return ("TUPLE", tuple(types_))


class _FakeTypes:
    STRING = staticmethod(_type_string)
    INT = staticmethod(_type_int)
    BOOLEAN = staticmethod(_type_boolean)
    ROW_NAMED = staticmethod(_row_named)
    TUPLE = staticmethod(_tuple_type)


def _fake_row(*values):
    return tuple(values)


class _FakeSimpleStringSchema:
    pass


class _FakeFlinkKafkaConsumer:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class _FakeValueStateDescriptor:
    def __init__(self, name, type_info):
        self.name = name
        self.type_info = type_info


class _FakeState:
    def __init__(self, initial=None):
        self.current = initial
        self.updates: list[Any] = []

    def value(self):
        return self.current

    def update(self, value):
        self.current = value
        self.updates.append(value)


class _FakeRuntimeContext:
    def __init__(self, state):
        self.state = state
        self.descriptor: _FakeValueStateDescriptor | None = None

    def get_state(self, descriptor):
        self.descriptor = descriptor
        return self.state


class _FakeStream:
    def __init__(self, name):
        self.name = name
        self.unions: list[Any] = []
        self.operations: list[Any] = []

    def map(self, mapper, output_type=None):
        self.operations.append(("map", mapper, output_type))
        return self

    def union(self, other):
        self.unions.append(other)
        return self

    def flat_map(self, mapper, output_type=None):
        self.operations.append(("flat_map", mapper, output_type))
        return self

    def key_by(self, key_selector, key_type=None):
        self.operations.append(("key_by", key_selector, key_type))
        return self

    def process(self, processor, output_type=None):
        self.operations.append(("process", processor, output_type))
        return self


class _FakeStreamExecutionEnvironment:
    latest: ClassVar[_FakeStreamExecutionEnvironment | None] = None

    def __init__(self):
        self.runtime_mode = None
        self.parallelism = None
        self.checkpointing = None
        self.sources: list[Any] = []

    @classmethod
    def get_execution_environment(cls):
        cls.latest = cls()
        return cls.latest

    def set_runtime_mode(self, mode):
        self.runtime_mode = mode

    def set_parallelism(self, parallelism):
        self.parallelism = parallelism

    def enable_checkpointing(self, interval_ms, mode):
        self.checkpointing = (interval_ms, mode)

    def add_source(self, consumer):
        stream = _FakeStream(consumer.kwargs["topics"])
        self.sources.append((consumer, stream))
        return stream


class _FakeRuntimeExecutionMode:
    STREAMING = "STREAMING"


class _FakeCheckpointingMode:
    EXACTLY_ONCE = "EXACTLY_ONCE"


class _FakeSchemaBuilder:
    def __init__(self):
        self.columns: list[tuple[str, Any]] = []

    def column(self, name, data_type):
        self.columns.append((name, data_type))
        return self

    def build(self):
        return tuple(self.columns)


class _FakeSchema:
    @staticmethod
    def new_builder():
        return _FakeSchemaBuilder()


class _FakeDataTypes:
    STRING = staticmethod(_type_string)
    INT = staticmethod(_type_int)
    BOOLEAN = staticmethod(_type_boolean)


class _FakeStatementSet:
    def __init__(self):
        self.inserts: list[str] = []
        self.executed = False

    def add_insert_sql(self, sql):
        self.inserts.append(sql)

    def execute(self):
        self.executed = True
        return "executed"


class _FakeTableEnvironment:
    latest: ClassVar[_FakeTableEnvironment | None] = None

    def __init__(self):
        self.views: dict[str, Any] = {}
        self.sql: list[str] = []
        self.statement_set = _FakeStatementSet()
        self.stream_execution_environment: Any | None = None

    @classmethod
    def create(cls, stream_execution_environment):
        cls.latest = cls()
        cls.latest.stream_execution_environment = stream_execution_environment
        return cls.latest

    def from_data_stream(self, stream, schema=None):
        return {"stream": stream, "schema": schema}

    def create_temporary_view(self, name, table):
        self.views[name] = table

    def execute_sql(self, sql):
        self.sql.append(sql)

    def create_statement_set(self):
        return self.statement_set


def _load_streaming_module():
    fake_pyflink = types.ModuleType("pyflink")
    fake_common = types.ModuleType("pyflink.common")
    fake_serialization = types.ModuleType("pyflink.common.serialization")
    fake_datastream = types.ModuleType("pyflink.datastream")
    fake_connectors = types.ModuleType("pyflink.datastream.connectors")
    fake_kafka = types.ModuleType("pyflink.datastream.connectors.kafka")
    fake_functions = types.ModuleType("pyflink.datastream.functions")
    fake_state = types.ModuleType("pyflink.datastream.state")
    fake_table = types.ModuleType("pyflink.table")

    cast("Any", fake_common).Row = _fake_row
    cast("Any", fake_common).Types = _FakeTypes
    cast("Any", fake_serialization).SimpleStringSchema = _FakeSimpleStringSchema
    cast("Any", fake_datastream).CheckpointingMode = _FakeCheckpointingMode
    cast("Any", fake_datastream).RuntimeExecutionMode = _FakeRuntimeExecutionMode
    cast("Any", fake_datastream).StreamExecutionEnvironment = _FakeStreamExecutionEnvironment
    cast("Any", fake_kafka).FlinkKafkaConsumer = _FakeFlinkKafkaConsumer
    cast("Any", fake_functions).FlatMapFunction = object
    cast("Any", fake_functions).KeyedProcessFunction = object
    cast("Any", fake_functions).RuntimeContext = object
    cast("Any", fake_state).ValueStateDescriptor = _FakeValueStateDescriptor
    cast("Any", fake_table).DataTypes = _FakeDataTypes
    cast("Any", fake_table).Schema = _FakeSchema
    cast("Any", fake_table).StreamTableEnvironment = _FakeTableEnvironment

    with patch.dict(
        sys.modules,
        {
            "pyflink": fake_pyflink,
            "pyflink.common": fake_common,
            "pyflink.common.serialization": fake_serialization,
            "pyflink.datastream": fake_datastream,
            "pyflink.datastream.connectors": fake_connectors,
            "pyflink.datastream.connectors.kafka": fake_kafka,
            "pyflink.datastream.functions": fake_functions,
            "pyflink.datastream.state": fake_state,
            "pyflink.table": fake_table,
        },
    ):
        spec = importlib.util.spec_from_file_location(
            "streaming_minimal_under_test", FLINK_JOB_PATH
        )
        if spec is None:
            raise RuntimeError("Unable to load module spec for streaming_minimal.py")
        if spec.loader is None:
            raise RuntimeError("Unable to load streaming_minimal.py module loader")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


class StreamingMinimalUnitTests(unittest.TestCase):
    module: ClassVar[Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_streaming_module()

    def test_env_and_inference_helpers(self) -> None:
        with patch.dict(self.module.os.environ, {"SOME_VALUE": " configured "}, clear=False):
            self.assertEqual(self.module.env_or_default("SOME_VALUE", "fallback"), "configured")

        with patch.dict(self.module.os.environ, {"SOME_VALUE": "   "}, clear=False):
            self.assertEqual(self.module.env_or_default("SOME_VALUE", "fallback"), "fallback")

        self.assertEqual(self.module.infer_entity_id("/tenant/devices/device-1/sensor"), "device-1")
        self.assertEqual(self.module.infer_entity_id("wildfi/tags/WF-001/gps"), "WF-001")
        self.assertEqual(self.module.infer_entity_id("wildfi/WF-002/environment"), "WF-002")
        self.assertEqual(self.module.infer_entity_id("orphan-topic"), "orphan-topic")
        self.assertEqual(self.module.infer_entity_id("/"), "unknown")

        cases = {
            ("raw.sensor", "devices/a/sensor"): "sensor",
            ("raw.gps", "devices/a/gnss/fix"): "gps",
            ("raw.image2d.meta", "devices/a/camera/frame"): "image2d",
            ("raw.image3d.meta", "devices/a/lidar/frame"): "image3d",
            ("raw.video2d.meta", "devices/a/video/frame"): "video2d",
            ("raw.video3d.meta", "devices/a/stereo-video/frame"): "video3d",
            ("other", "devices/a/gnss/fix"): "gps",
            ("other", "devices/a/volumetric-video/frame"): "video3d",
            ("other", "devices/a/camera-stream/frame"): "video2d",
            ("other", "devices/a/pointcloud/frame"): "image3d",
            ("other", "devices/a/image/frame"): "image2d",
            ("other", "devices/a/other"): "unknown",
        }
        for args, expected in cases.items():
            self.assertEqual(self.module.infer_event_kind(*args), expected)

    def test_normalize_event_flat_map_handles_valid_and_invalid_json(self) -> None:
        normalizer = self.module.NormalizeEvent()
        raw = json.dumps(
            {
                "device_id": "dev-1",
                "timestamp": "2026-01-01T00:00:00+00:00",
                "mqtt_topic": "wildfi/tags/ignored/gnss/fix",
                "payload_b64": "abc",
                "qos": "1",
                "retain": True,
            }
        )

        rows = list(normalizer.flat_map(("raw.gps", raw)))

        self.assertEqual(
            rows,
            [
                (
                    "dev-1",
                    "2026-01-01T00:00:00+00:00",
                    "raw.gps",
                    "wildfi/tags/ignored/gnss/fix",
                    "gps",
                    "abc",
                    1,
                    True,
                    raw,
                )
            ],
        )
        self.assertEqual(normalizer.flat_map(("raw.sensor", "{bad json")), [])

    def test_latest_by_entity_keeps_newer_records_only(self) -> None:
        state = _FakeState("2026-01-01T00:00:00+00:00")
        runtime_context = _FakeRuntimeContext(state)
        processor = self.module.LatestByEntity()
        processor.open(runtime_context)

        old_record = ("dev-1", "2025-12-31T23:59:59+00:00")
        new_record = ("dev-1", "2026-01-01T00:00:01+00:00")

        self.assertEqual(list(processor.process_element(old_record, None)), [])
        self.assertEqual(list(processor.process_element(new_record, None)), [new_record])
        self.assertEqual(state.updates, ["2026-01-01T00:00:01+00:00"])
        assert runtime_context.descriptor is not None
        self.assertEqual(runtime_context.descriptor.name, "latest_event_ts")

    def test_build_topic_stream_and_table_schema(self) -> None:
        env = _FakeStreamExecutionEnvironment()

        stream = self.module.build_topic_stream(
            env=env,
            bootstrap_servers="kafka:9092",
            group_id="group",
            topic_name="raw.sensor",
        )

        consumer = env.sources[0][0]
        self.assertEqual(consumer.kwargs["topics"], "raw.sensor")
        self.assertEqual(consumer.kwargs["properties"]["bootstrap.servers"], "kafka:9092")
        self.assertEqual(stream.operations[0][0], "map")

        schema = self.module.build_table_schema()
        column_names = [name for name, _data_type in schema]
        self.assertEqual(
            column_names,
            [
                "entity_id",
                "event_ts",
                "source_topic",
                "mqtt_topic",
                "event_kind",
                "payload_b64",
                "qos",
                "retain",
                "raw_json",
            ],
        )

    def test_main_configures_streaming_pipeline(self) -> None:
        with patch.dict(
            self.module.os.environ,
            {
                "KAFKA_BOOTSTRAP_SERVERS": "kafka:9092",
                "FLINK_CONSUMER_GROUP": "group",
                "FLINK_SOURCE_TOPICS": "raw.sensor, raw.gps",
                "FLINK_PARALLELISM": "2",
                "FLINK_CHECKPOINT_INTERVAL_MS": "5000",
                "FEATURES_TOPIC": "features.custom",
                "STATE_TOPIC": "state.custom",
            },
            clear=False,
        ):
            self.module.main()

        env = _FakeStreamExecutionEnvironment.latest
        table_env = _FakeTableEnvironment.latest
        assert env is not None
        assert table_env is not None

        self.assertEqual(env.runtime_mode, "STREAMING")
        self.assertEqual(env.parallelism, 2)
        self.assertEqual(env.checkpointing, (5000, "EXACTLY_ONCE"))
        self.assertEqual(
            [consumer.kwargs["topics"] for consumer, _stream in env.sources],
            ["raw.sensor", "raw.gps"],
        )
        self.assertIn("features_view", table_env.views)
        self.assertIn("latest_view", table_env.views)
        self.assertTrue(any("features.custom" in sql for sql in table_env.sql))
        self.assertTrue(any("state.custom" in sql for sql in table_env.sql))
        self.assertEqual(len(table_env.statement_set.inserts), 2)
        self.assertTrue(table_env.statement_set.executed)


if __name__ == "__main__":
    unittest.main()
