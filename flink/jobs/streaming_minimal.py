import json
import os
from collections.abc import Iterable

from pyflink.common import Row, Types
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import (
    CheckpointingMode,
    RuntimeExecutionMode,
    StreamExecutionEnvironment,
)
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from pyflink.datastream.functions import (
    FlatMapFunction,
    KeyedProcessFunction,
    RuntimeContext,
)
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.table import DataTypes, Schema, StreamTableEnvironment

EVENT_TYPE = Types.ROW_NAMED(
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
    [
        Types.STRING(),
        Types.STRING(),
        Types.STRING(),
        Types.STRING(),
        Types.STRING(),
        Types.STRING(),
        Types.INT(),
        Types.BOOLEAN(),
        Types.STRING(),
    ],
)


def env_or_default(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip()


def infer_entity_id(mqtt_topic: str) -> str:
    parts = [part for part in mqtt_topic.split("/") if part]

    if "devices" in parts:
        idx = parts.index("devices")
        if idx + 1 < len(parts):
            return parts[idx + 1]

    if parts:
        return parts[-1]

    return "unknown"


def infer_event_kind(source_topic: str, mqtt_topic: str) -> str:
    lowered_source = source_topic.lower()
    lowered_mqtt = mqtt_topic.lower()

    if lowered_source == "raw.sensor":
        return "sensor"
    if lowered_source == "raw.gps":
        return "gps"
    if lowered_source == "raw.image2d.meta":
        return "image2d"
    if lowered_source == "raw.image3d.meta":
        return "image3d"
    if lowered_source == "raw.video2d.meta":
        return "video2d"
    if lowered_source == "raw.video3d.meta":
        return "video3d"

    if "gps" in lowered_mqtt or "/gnss/" in lowered_mqtt:
        return "gps"
    if (
        "video3d" in lowered_mqtt
        or "/stereo-video/" in lowered_mqtt
        or "/volumetric-video/" in lowered_mqtt
    ):
        return "video3d"
    if (
        "video2d" in lowered_mqtt
        or "/video/" in lowered_mqtt
        or "/camera-stream/" in lowered_mqtt
    ):
        return "video2d"
    if (
        "image3d" in lowered_mqtt
        or "/lidar/" in lowered_mqtt
        or "/pointcloud/" in lowered_mqtt
    ):
        return "image3d"
    if (
        "image2d" in lowered_mqtt
        or "/camera/" in lowered_mqtt
        or "/image/" in lowered_mqtt
    ):
        return "image2d"

    return "unknown"


class NormalizeEvent(FlatMapFunction):
    def flat_map(self, value) -> Iterable[Row]:
        source_topic, raw_value = value

        try:
            record = json.loads(raw_value)
        except Exception:
            return []

        mqtt_topic = str(record.get("mqtt_topic", ""))
        entity_id = infer_entity_id(mqtt_topic)
        event_ts = str(record.get("ingested_at", ""))
        event_kind = infer_event_kind(source_topic, mqtt_topic)

        payload_b64 = str(record.get("payload_b64", ""))
        qos = int(record.get("qos", 0) or 0)
        retain = bool(record.get("retain", False))

        return [
            Row(
                entity_id,
                event_ts,
                source_topic,
                mqtt_topic,
                event_kind,
                payload_b64,
                qos,
                retain,
                raw_value,
            )
        ]


class LatestByEntity(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        self.latest_ts_state = runtime_context.get_state(
            ValueStateDescriptor("latest_event_ts", Types.STRING())
        )

    def process_element(self, value, ctx):
        current = self.latest_ts_state.value()
        incoming_ts = value[1]

        if current is None or incoming_ts >= current:
            self.latest_ts_state.update(incoming_ts)
            yield value


def build_topic_stream(
    env: StreamExecutionEnvironment,
    bootstrap_servers: str,
    group_id: str,
    topic_name: str,
):
    consumer = FlinkKafkaConsumer(
        topics=topic_name,
        deserialization_schema=SimpleStringSchema(),
        properties={
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": env_or_default("KAFKA_AUTO_OFFSET_RESET", "earliest"),
            "enable.auto.commit": "false",
        },
    )

    return env.add_source(consumer).map(
        lambda raw: (topic_name, raw),
        output_type=Types.TUPLE([Types.STRING(), Types.STRING()]),
    )


def build_table_schema() -> Schema:
    return (
        Schema.new_builder()
        .column("entity_id", DataTypes.STRING())
        .column("event_ts", DataTypes.STRING())
        .column("source_topic", DataTypes.STRING())
        .column("mqtt_topic", DataTypes.STRING())
        .column("event_kind", DataTypes.STRING())
        .column("payload_b64", DataTypes.STRING())
        .column("qos", DataTypes.INT())
        .column("retain", DataTypes.BOOLEAN())
        .column("raw_json", DataTypes.STRING())
        .build()
    )


def main():
    bootstrap_servers = env_or_default(
        "KAFKA_BOOTSTRAP_SERVERS",
        "kafka1:9092,kafka2:9092,kafka3:9092",
    )
    consumer_group = env_or_default(
        "FLINK_CONSUMER_GROUP",
        "flink-streaming-minimal-v1",
    )
    source_topics = [
        topic.strip()
        for topic in env_or_default(
            "FLINK_SOURCE_TOPICS",
            "raw.sensor,raw.gps,raw.image2d.meta,raw.image3d.meta,raw.video2d.meta,raw.video3d.meta",
        ).split(",")
        if topic.strip()
    ]

    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
    env.set_parallelism(int(env_or_default("FLINK_PARALLELISM", "4")))
    env.enable_checkpointing(
        int(env_or_default("FLINK_CHECKPOINT_INTERVAL_MS", "10000")),
        CheckpointingMode.EXACTLY_ONCE,
    )

    t_env = StreamTableEnvironment.create(stream_execution_environment=env)

    topic_streams = [
        build_topic_stream(
            env=env,
            bootstrap_servers=bootstrap_servers,
            group_id=consumer_group,
            topic_name=topic,
        )
        for topic in source_topics
    ]

    if not topic_streams:
        raise RuntimeError("No source topics configured in FLINK_SOURCE_TOPICS")

    raw_stream = topic_streams[0]
    for stream in topic_streams[1:]:
        raw_stream = raw_stream.union(stream)

    normalized = raw_stream.flat_map(NormalizeEvent(), output_type=EVENT_TYPE)

    latest = normalized.key_by(
        lambda row: row[0],
        key_type=Types.STRING(),
    ).process(
        LatestByEntity(),
        output_type=EVENT_TYPE,
    )

    table_schema = build_table_schema()

    features_table = t_env.from_data_stream(normalized, schema=table_schema)
    latest_table = t_env.from_data_stream(latest, schema=table_schema)

    t_env.create_temporary_view("features_view", features_table)
    t_env.create_temporary_view("latest_view", latest_table)

    t_env.execute_sql(
        f"""
        CREATE TABLE features_events_sink (
          entity_id STRING,
          event_ts STRING,
          source_topic STRING,
          mqtt_topic STRING,
          event_kind STRING,
          payload_b64 STRING,
          qos INT,
          retain BOOLEAN,
          raw_json STRING
        ) WITH (
          'connector' = 'kafka',
          'topic' = '{env_or_default("FEATURES_TOPIC", "features.events")}',
          'properties.bootstrap.servers' = '{bootstrap_servers}',
          'properties.acks' = 'all',
          'format' = 'json',
          'json.fail-on-missing-field' = 'false',
          'json.ignore-parse-errors' = 'true'
        )
        """
    )

    t_env.execute_sql(
        f"""
        CREATE TABLE state_latest_sink (
          entity_id STRING,
          event_ts STRING,
          source_topic STRING,
          mqtt_topic STRING,
          event_kind STRING,
          payload_b64 STRING,
          qos INT,
          retain BOOLEAN,
          raw_json STRING,
          PRIMARY KEY (entity_id) NOT ENFORCED
        ) WITH (
          'connector' = 'upsert-kafka',
          'topic' = '{env_or_default("STATE_TOPIC", "state.latest")}',
          'properties.bootstrap.servers' = '{bootstrap_servers}',
          'key.format' = 'json',
          'value.format' = 'json',
          'value.json.fail-on-missing-field' = 'false',
          'value.json.ignore-parse-errors' = 'true'
        )
        """
    )

    statement_set = t_env.create_statement_set()
    statement_set.add_insert_sql(
        """
        INSERT INTO features_events_sink
        SELECT
          entity_id,
          event_ts,
          source_topic,
          mqtt_topic,
          event_kind,
          payload_b64,
          qos,
          retain,
          raw_json
        FROM features_view
        """
    )

    statement_set.add_insert_sql(
        """
        INSERT INTO state_latest_sink
        SELECT
          entity_id,
          event_ts,
          source_topic,
          mqtt_topic,
          event_kind,
          payload_b64,
          qos,
          retain,
          raw_json
        FROM latest_view
        """
    )

    statement_set.execute()


if __name__ == "__main__":
    main()
