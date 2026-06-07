# Operations And Scaling

## Scaling Model

| Component | Scaling unit | Production control |
|---|---|---|
| MQTT-Kafka bridge | Stateless replicas | HPA, shared MQTT subscriptions, PDB, topology spread |
| Flink TaskManager | TaskManager replicas and slots | HPA, task slots, checkpoints, savepoints |
| Airflow workers | Celery workers | HPA, queue depth and task duration SLOs |
| Management Console | Stateless replicas | HPA and PDB |
| Apicurio Registry | Registry replicas | PDB and KafkaSQL storage |
| Kafka | Broker count and partitions | Managed service or operator |
| PostgreSQL | Primary/replica topology | Managed service or operator |
| Object storage | Bucket and backend capacity | Managed S3 or operator-backed storage |

## Horizontal Scaling Rules

- Increase Kafka partitions before increasing high-volume bridge replicas beyond current partition parallelism.
- Keep MQTT shared subscriptions enabled for bridge replicas.
- Scale Flink TaskManagers with matching task-slot and parallelism changes.
- Use savepoints before Flink job upgrades that change state schema.
- Keep Airflow backfills bounded by time window and rate limits.
- Monitor DLQ rate before treating increased throughput as healthy.

## Availability Controls

Production overlay includes:

- HPA for bridge, Flink TaskManager, Airflow worker, and Management Console.
- PDBs for bridge, Flink TaskManager, Apicurio, Airflow API, Airflow workers, and Management Console.
- Topology spread constraints for horizontally scaled workloads.
- Readiness/liveness probes for runtime services.

## Observability

Required dashboards and alerts should cover:

- MQTT connection failures and reconnect loops.
- Kafka producer failures and broker latency.
- Kafka consumer lag by consumer group.
- DLQ event rate and top error categories.
- Flink checkpoint duration, failures, and backpressure.
- Airflow DAG failures and queue latency.
- Object storage request errors and capacity.
- PostgreSQL availability and connection pool saturation.
- Management Console dependency health.

## Incident Response

1. Check Management Console `/healthz` and `/api/health`.
2. Check Kafka topic lag and DLQ rate.
3. Check Flink checkpoint health before restarting jobs.
4. Check Airflow task failures for replay/backfill jobs.
5. Use runbooks in `docs/runbooks/` for backup, restore, security, WildFi, and dataset export procedures.
6. Record incident and remediation evidence in security and resilience topics.
