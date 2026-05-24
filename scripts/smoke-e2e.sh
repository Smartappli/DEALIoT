#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILES=(
  -f docker-compose.yml
  -f docker-compose.dev.yml
)

compose() {
  docker compose "${COMPOSE_FILES[@]}" "$@"
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 127
  fi
}

wait_for_topic_message() {
  topic="$1"
  pattern="$2"
  timeout_ms="${3:-30000}"

  echo "Waiting for Kafka topic=$topic pattern=$pattern"
  if compose exec -T kafka1 /opt/kafka/bin/kafka-console-consumer.sh \
      --bootstrap-server kafka1:9092 \
      --topic "$topic" \
      --from-beginning \
      --timeout-ms "$timeout_ms" \
      --max-messages 20 | grep -F "$pattern"; then
    return 0
  fi

  echo "Did not observe expected message on $topic: $pattern" >&2
  return 1
}

publish_mqtt_fixtures() {
  compose exec -T mqtt-kafka-bridge python - <<'PY'
import json
import os
import time

from paho.mqtt import client as mqtt

password = os.environ["MQTT_PASSWORD"]
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="dealiot-e2e-publisher")
client.username_pw_set("admin", password)
client.connect("vernemq1", 1883, keepalive=30)
client.loop_start()

sensor_payload = {
    "timestamp": "2026-01-01T00:00:00+00:00",
    "temperature_c": 21.5,
}
client.publish(
    "devices/e2e-sensor-001/sensor",
    json.dumps(sensor_payload),
    qos=1,
).wait_for_publish()

invalid_media_payload = {"frame": 12}
client.publish(
    "devices/e2e-camera-001/video2d",
    json.dumps(invalid_media_payload),
    qos=1,
).wait_for_publish()

time.sleep(2)
client.loop_stop()
client.disconnect()
PY
}

require_command docker

echo "Rendering compose configuration"
compose config -q

echo "Starting core event-flow services"
compose up -d --build --wait --wait-timeout 900 \
  kafka1 kafka2 kafka3 kafka-init \
  apicurio-registry apicurio-init \
  vernemq1 mqtt-kafka-bridge \
  flink-jobmanager flink-taskmanager-1 flink-taskmanager-2

echo "Submitting Flink streaming job"
compose run --rm flink-cli /opt/flink/usrlib/run-streaming-minimal.sh

publish_mqtt_fixtures

wait_for_topic_message "raw.sensor" "e2e-sensor-001"
wait_for_topic_message "dlq.events" "e2e-camera-001"
wait_for_topic_message "features.events" "e2e-sensor-001" 60000
wait_for_topic_message "state.latest" "e2e-sensor-001" 60000

echo "Checking Apicurio artifacts"
compose exec -T apicurio-registry sh -lc \
  'curl -fsS http://127.0.0.1:8080/apis/registry/v3/groups/platform/artifacts/dlq.events >/dev/null'
compose exec -T apicurio-registry sh -lc \
  'curl -fsS http://127.0.0.1:8080/apis/registry/v3/groups/telemetry/artifacts/raw.sensor >/dev/null'

echo "E2E smoke test passed"
