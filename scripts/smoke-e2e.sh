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
  local command_name="$1"

  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    exit 127
  fi
}

wait_for_topic_message() {
  local topic="$1"
  local pattern="$2"
  local timeout_ms="${3:-30000}"

  echo "Waiting for Kafka topic=$topic pattern=$pattern"
  if compose exec -T kafka1 /opt/kafka/bin/kafka-console-consumer.sh \
      --bootstrap-server kafka1:9092 \
      --topic "$topic" \
      --from-beginning \
      --timeout-ms "$timeout_ms" \
      --max-messages 200 | grep -F "$pattern"; then
    return 0
  fi

  echo "Did not observe expected message on $topic: $pattern" >&2
  dump_smoke_diagnostics
  return 1
}

dump_smoke_diagnostics() {
  echo "Docker compose status" >&2
  compose ps >&2 || true

  echo "Flink running jobs" >&2
  compose run --rm --entrypoint sh flink-cli -lc \
    "/opt/flink/bin/flink list -r --jobmanager flink-jobmanager:8081 || true" >&2 || true

  echo "Recent event-flow logs" >&2
  compose logs --no-color --tail=250 \
    flink-jobmanager flink-taskmanager-1 flink-taskmanager-2 \
    mqtt-kafka-bridge kafka1 kafka2 kafka3 >&2 || true
}

wait_for_flink_job_running() {
  local job_id="$1"
  local attempts="${2:-30}"
  local list_output

  for _ in $(seq 1 "$attempts"); do
    list_output="$(
      compose run --rm --entrypoint sh flink-cli -lc \
        "/opt/flink/bin/flink list -r --jobmanager flink-jobmanager:8081" 2>&1 || true
    )"
    printf '%s\n' "$list_output"

    if printf '%s\n' "$list_output" | grep -F "$job_id" >/dev/null; then
      return 0
    fi

    sleep 2
  done

  echo "Flink job $job_id did not reach RUNNING state." >&2
  dump_smoke_diagnostics
  return 1
}

publish_mqtt_fixtures() {
  local sensor_id="$1"
  local camera_id="$2"

  compose exec -T mqtt-kafka-bridge python - "$sensor_id" "$camera_id" <<'PY'
import json
import os
import sys
import time

from paho.mqtt import client as mqtt

sensor_id = sys.argv[1]
camera_id = sys.argv[2]
password = os.environ["MQTT_PASSWORD"]
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id=f"dealiot-e2e-publisher-{sensor_id}",
)
client.username_pw_set("admin", password)
client.connect("vernemq1", 1883, keepalive=30)
client.loop_start()

sensor_payload = {
    "timestamp": "2026-01-01T00:00:00+00:00",
    "temperature_c": 21.5,
}
client.publish(
    f"devices/{sensor_id}/sensor",
    json.dumps(sensor_payload),
    qos=1,
).wait_for_publish()

invalid_media_payload = {"frame": 12}
client.publish(
    f"devices/{camera_id}/video2d",
    json.dumps(invalid_media_payload),
    qos=1,
).wait_for_publish()

time.sleep(2)
client.loop_stop()
client.disconnect()
PY
}

require_command docker

smoke_run_id="$(date -u +%Y%m%dT%H%M%SZ)-$$-${RANDOM}"
sensor_id="e2e-sensor-${smoke_run_id}"
camera_id="e2e-camera-${smoke_run_id}"
flink_consumer_group="flink-streaming-minimal-e2e-${smoke_run_id}"

echo "Using smoke run id: ${smoke_run_id}"

echo "Rendering compose configuration"
compose config -q

echo "Starting core event-flow services"
compose up -d --build --wait --wait-timeout 900 \
  kafka1 kafka2 kafka3 kafka-init \
  apicurio-registry apicurio-init \
  vernemq1 mqtt-kafka-bridge \
  flink-jobmanager flink-taskmanager-1 flink-taskmanager-2

echo "Submitting Flink streaming job"
submit_output="$(
  compose run --rm \
    -e FLINK_CONSUMER_GROUP="$flink_consumer_group" \
    flink-cli sh /opt/flink/usrlib/run-streaming-minimal.sh
)"
printf '%s\n' "$submit_output"

flink_job_id="$(
  printf '%s\n' "$submit_output" |
    sed -n 's/.*JobID \([0-9a-fA-F]\{32\}\).*/\1/p' |
    tail -n 1
)"
if [ -z "$flink_job_id" ]; then
  echo "Unable to parse Flink JobID from submit output." >&2
  dump_smoke_diagnostics
  exit 1
fi

wait_for_flink_job_running "$flink_job_id"

publish_mqtt_fixtures "$sensor_id" "$camera_id"

wait_for_topic_message "raw.sensor" "$sensor_id"
wait_for_topic_message "dlq.events" "$camera_id"
wait_for_topic_message "features.events" "$sensor_id" 60000
wait_for_topic_message "state.latest" "$sensor_id" 60000

echo "Checking Apicurio artifacts"
registry_scheme="${APICURIO_REGISTRY_SCHEME:-http}"
registry_host="${APICURIO_REGISTRY_HOST:-apicurio-registry:8080}"
registry_base="${registry_scheme}://${registry_host}/apis/registry/v3"
compose run --rm --entrypoint sh apicurio-init -lc \
  "curl -fsS ${registry_base}/groups/platform/artifacts/dlq.events >/dev/null"
compose run --rm --entrypoint sh apicurio-init -lc \
  "curl -fsS ${registry_base}/groups/telemetry/artifacts/raw.sensor >/dev/null"

echo "E2E smoke test passed"
