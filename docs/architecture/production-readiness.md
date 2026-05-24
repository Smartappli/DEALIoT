# Production Readiness Architecture

This document defines the current production target for DEALIoT.

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
6. Provide secrets through a secret manager or External Secrets Operator, not literal manifests.
7. Validate production manifests in CI before merge.
8. Generate image SBOM and provenance attestations for pushed images.

## Stateful Dependency Strategy

| Dependency | Production Strategy |
|---|---|
| Kafka | Managed Kafka or Strimzi-operated cluster |
| PostgreSQL / TimescaleDB | Managed PostgreSQL or CloudNativePG/Crunchy operator |
| Redis | Managed Redis or operator-managed Redis |
| MQTT broker | Managed MQTT or operator/Helm-managed VerneMQ/EMQX with TLS and ACLs |
| S3-compatible object storage | Managed S3-compatible storage or operator-backed on-prem object storage |

## CI Gates

The repository currently enforces:

- Kubernetes base render and server-side dry-run.
- Kubernetes production overlay render and server-side dry-run.
- Rejection of mutable `latest` tags in the production overlay.
- Swarm production stack render.
- Swarm smoke deployment.
- kind smoke deployment for the bridge image.
- Python coverage threshold of 80% in the Sonar workflow.

## Remaining Before Real Go-Live

- Replace example endpoint values with private production endpoints.
- Narrow production `ipBlock` ranges in NetworkPolicies to the real private endpoint CIDRs.
- Add runtime E2E tests against a staging cluster with real Kafka/MQTT/S3 dependencies.
- Add image signature verification policy at cluster admission.
- Define SLOs and alert thresholds for ingest latency, Kafka lag, DLQ rate, Flink checkpointing,
  Airflow DAG failures, and storage availability.
