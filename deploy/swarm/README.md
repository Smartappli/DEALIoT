# Docker Swarm Production Deployment

`dealiot-stack.yml` deploys the DEALIoT application/runtime plane on Docker Swarm.

Before deploying, provision these external production dependencies:

- Kafka bootstrap endpoint
- MQTT broker endpoint
- S3-compatible object storage endpoint and credentials
- Airflow PostgreSQL metadata database
- Airflow Redis broker
- container registry images built by `.github/workflows/build-and-push-images.yml`

Create required Swarm secrets:

```bash
printf '%s\n' "$MQTT_PASSWORD" | docker secret create mqtt_password -
```

Render and deploy:

```bash
export DEALIOT_MQTT_KAFKA_BRIDGE_IMAGE=ghcr.io/smartappli/dealiot-mqtt-kafka-bridge:latest
export DEALIOT_FLINK_PYFLINK_IMAGE=ghcr.io/smartappli/dealiot-flink-pyflink:latest
export DEALIOT_ORCHESTRATION_IMAGE=ghcr.io/smartappli/dealiot-orchestration:latest
export KAFKA_BOOTSTRAP_SERVERS=kafka1.example.net:9092,kafka2.example.net:9092
export MQTT_HOST=mqtt.example.net
export S3_ENDPOINT_URL=https://s3.example.net
export AWS_ACCESS_KEY_ID=replace-me
export AWS_SECRET_ACCESS_KEY=replace-me
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg://airflow:replace-me@postgres.example.net:5432/airflow
export AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:replace-me@postgres.example.net:5432/airflow
export AIRFLOW__CELERY__BROKER_URL=redis://redis.example.net:6379/0
export AIRFLOW__CORE__FERNET_KEY=replace-me
export AIRFLOW__API__SECRET_KEY=replace-me
export AIRFLOW__API_AUTH__JWT_SECRET=replace-me
export AIRFLOW_ADMIN_PASSWORD=replace-me

docker stack deploy -c deploy/swarm/dealiot-stack.yml dealiot
```

Use `dealiot-smoke-stack.yml` only in CI or temporary validation environments.
