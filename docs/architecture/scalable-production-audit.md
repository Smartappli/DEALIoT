# Scalable Production Architecture Audit

This audit records the production-readiness iterations applied to DEALIoT.

## Objective

Prepare the repository for a scalable production deployment while preserving operational compatibility. The audit prioritizes changes that are verifiable through tests, renders, and CI workflows.

## Iteration 1: Runtime Dependency Security

Findings:

- Runtime producers and processors needed one consistent Kafka security contract.
- MQTT production defaults needed TLS rather than plaintext port `1883`.
- Management Console API routes needed an authentication boundary.

Corrections:

- Added Kafka `SASL_SSL` support to the MQTT-Kafka bridge, media backfill, and Flink job configuration.
- Added MQTT TLS configuration to the bridge.
- Added Management Console bearer-token enforcement for `/api/*` and mutation routes while keeping `/healthz` public.
- Added unit tests for Kafka security, MQTT TLS, and Management Console authorization.

## Iteration 2: Kubernetes Production Scaling

Findings:

- Production manifests needed explicit HPA/PDB coverage for scalable workloads.
- Runtime probes and disruption controls needed to be enforced by tests.
- Production overlay needed to reject placeholders during CI render.

Corrections:

- Added HPA for bridge, Flink TaskManager, Airflow worker, and Management Console.
- Added PDBs for application tiers.
- Added topology spread constraints for horizontally scaled workloads.
- Added probes and metrics exposure where appropriate.
- Added CI checks that reject mutable tags, placeholder tags, example endpoints, and example secrets in rendered production manifests.

## Iteration 3: Pod Security And Workload Hardening

Findings:

- Several Kubernetes workloads did not explicitly declare the full Pod Security `restricted` intent.
- CI smoke namespace did not enforce the same admission baseline.
- Some workload containers did not have a test preventing missing resources or security context regressions.

Corrections:

- Added Pod Security `restricted` labels to runtime namespaces.
- Added `seccompProfile: RuntimeDefault` to workload pod specs.
- Added `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]`, and `runAsNonRoot: true` to workload containers.
- Added liveness probing for Management Console.
- Added deployment tests that validate workload security context, resources, service-account token automount, and namespace Pod Security labels.

## Iteration 4: CI/CD Contract Hardening

Findings:

- Production Swarm render validation used local placeholder image values for some runtime images.
- Smoke image validation and production image contract validation were coupled through one environment variable.

Corrections:

- Split the smoke bridge image (`DEALIOT_SMOKE_BRIDGE_IMAGE`) from production image variables.
- Swarm production render now uses immutable `sha-${{ github.sha }}` images.
- Swarm render fails if placeholder or mutable production image tags are rendered.
- Deployment tests assert the workflow separation and render guardrail.

## Iteration 5: Documentation And Wiki Source

Findings:

- The README had grown into a mixed audit log, runbook, and architecture note.
- A GitHub Wiki was requested, but `https://github.com/Smartappli/DEALIoT.wiki.git` was not accessible from the local environment.

Corrections:

- Rewrote the README as a professional project entry point.
- Added versioned wiki source pages under `docs/wiki` so documentation can be published as soon as the GitHub Wiki is enabled.
- Added this audit record as a durable architecture decision trail.

## Rust Conversion Decision

Rust was considered for performance-sensitive ingestion paths. No Rust refactor was applied in this iteration because:

- The local environment has no Rust toolchain, so a Rust component could not be compiled or tested.
- The current bottlenecks are deployment, security, and scaling contracts rather than CPU-bound parsing.
- Replacing the MQTT-Kafka bridge without binary CI and operational soak tests would increase production risk.

Recommended future Rust candidates:

- A standalone high-throughput MQTT-Kafka bridge once a Rust toolchain, container build, integration tests, and canary rollout path are added.
- CPU-heavy binary decoding or validation steps that can be isolated behind stable input/output contracts.

## Current Go-Live Readiness

Ready for staging:

- Runtime security defaults are wired.
- Kubernetes and Swarm production render contracts are tested.
- Pod Security `restricted` is declared and tested.
- CI validates deployment manifests and runtime behavior.
- Documentation source is versioned.

Still environment-specific before real production:

- Replace example endpoints with private production endpoints.
- Provide secrets through a real secret manager.
- Narrow NetworkPolicy CIDRs.
- Configure image signature admission verification.
- Run E2E tests against real staging Kafka, MQTT, S3, PostgreSQL, and Redis.
- Define SLOs and alert thresholds.
- Decide whether Flink should move from session deployment to Flink Operator for savepoint-driven lifecycle management.