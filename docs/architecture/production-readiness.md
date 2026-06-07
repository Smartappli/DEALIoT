# Production Readiness Architecture

This document defines the current production target for DEALIoT.

Detailed audit history is maintained in `docs/architecture/scalable-production-audit.md`.
Versioned GitHub Wiki source pages are maintained in `docs/wiki/`.

## Production Target

Kubernetes is the primary production target. Docker Swarm remains supported as a simpler runtime
target, but Kubernetes is where strict production controls are enforced first.

## Non-Negotiable Production Rules

1. Do not deploy mutable `latest` tags.
2. Deploy images by immutable release SHA tags.
3. Keep stateful dependencies outside the application manifests unless they are managed by a
   dedicated operator.
4. Require TLS or private connectivity for all external dependencies.
5. Apply default-deny NetworkPolicies in Kubernetes production.
6. Replace base runtime defaults with production-specific external endpoints.
7. Provide secrets through a secret manager or External Secrets Operator, not literal manifests.
8. Validate production manifests in CI before merge.
9. Generate image SBOM and provenance attestations for pushed images.
10. Enforce Kubernetes Pod Security `restricted` on runtime namespaces.

## Stateful Dependency Strategy

| Dependency | Production Strategy |
|---|---|
| Kafka | Managed Kafka or Strimzi-operated cluster |
| PostgreSQL / TimescaleDB | Managed PostgreSQL or CloudNativePG/Crunchy operator |
| Redis | Managed Redis or operator-managed Redis |
| MQTT broker | Managed MQTT or operator/Helm-managed VerneMQ/EMQX with TLS and ACLs |
| S3-compatible object storage | Managed S3-compatible storage or operator-backed on-prem object storage |

## WildFi Ingestion

WildFi is integrated as an MQTT data source, using the upstream firmware/gateway project at
`https://github.com/trichl/WildFiOpenSource` and the decoder project at
`https://github.com/wildlab/WildFiDecoder`. DEALIoT subscribes to `$share/ingestors/wildfi/#`;
decoded GPS messages are mapped to `raw.gps`, while decoded IMU, environment, proximity, movement,
and metadata messages are mapped to `raw.sensor`.

Native WildFi binary logs should be decoded with the packaged `wildfi-decoder` image before
publication or stored as object artifacts with metadata. They should not become an implicit binary
telemetry contract inside the bridge.

## Runtime Security

Production runtime clients are expected to use authenticated and encrypted dependency connections:

- Kafka defaults to `SASL_SSL` with SCRAM credentials provided by `dealiot-secrets`.
- MQTT defaults to TLS on port `8883`; certificates can be mounted and referenced through runtime
  config.
- Management Console mutation and API routes require a bearer token when
  `MANAGEMENT_CONSOLE_TOKEN` is set.
- Airflow, Flink, Apicurio, the MQTT bridge, and media backfill share the same Kafka security
  environment contract.

The production manifests wire readiness/liveness probes for application services and expose Flink
Prometheus metrics on port `9250`.

Kubernetes workload manifests declare `seccompProfile: RuntimeDefault`, disable service-account
token automount, drop Linux capabilities, prevent privilege escalation, and run containers as
non-root. Deployment tests enforce these guardrails.

## CI Gates

The repository currently enforces:

- Kubernetes base render and server-side dry-run.
- Kubernetes production overlay render and server-side dry-run.
- Rejection of mutable `latest` tags in the production overlay.
- Rejection of unresolved production placeholders in the rendered production overlay.
- Swarm production stack render.
- Swarm smoke deployment.
- kind smoke deployment for the bridge image.
- Runtime unit tests for Kafka SASL/SSL, MQTT TLS, and Management Console bearer-token auth.
- Python coverage threshold of 90% in the Sonar workflow.

## Remaining Before Real Go-Live

- Replace example endpoint values with private production endpoints.
- Narrow production `ipBlock` ranges in NetworkPolicies to the real private endpoint CIDRs.
- Add runtime E2E tests against a staging cluster with real Kafka/MQTT/S3 dependencies.
- Add image signature verification policy at cluster admission.
- Decide whether to migrate the Flink session deployment to a Flink Operator CRD model for
  savepoint-driven upgrades and native checkpoint lifecycle management.
- Define SLOs and alert thresholds for ingest latency, Kafka lag, DLQ rate, Flink checkpointing,
  Airflow DAG failures, and storage availability.
