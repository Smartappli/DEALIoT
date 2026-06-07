# Kubernetes Production Overlay

This overlay is the production contract for Kubernetes deployments.

It intentionally does not deploy Kafka, PostgreSQL, Redis, MQTT, or S3-compatible storage. Those
stateful dependencies must be provided by managed services or dedicated operators and exposed to
DEALIoT through `dealiot-runtime-config` plus the `dealiot-secrets` Secret.

## Release Images

Replace the placeholder tags before deployment:

```bash
RELEASE_SHA="$(git rev-parse HEAD)"
kustomize edit set image \
  ghcr.io/smartappli/dealiot-mqtt-kafka-bridge=ghcr.io/smartappli/dealiot-mqtt-kafka-bridge:sha-"$RELEASE_SHA" \
  ghcr.io/smartappli/dealiot-management-console=ghcr.io/smartappli/dealiot-management-console:sha-"$RELEASE_SHA" \
  ghcr.io/smartappli/dealiot-flink-pyflink=ghcr.io/smartappli/dealiot-flink-pyflink:sha-"$RELEASE_SHA" \
  ghcr.io/smartappli/dealiot-orchestration=ghcr.io/smartappli/dealiot-orchestration:sha-"$RELEASE_SHA"
```

Do not deploy `latest` in production.

## Runtime Config

This overlay replaces the base `dealiot-runtime-config` ConfigMap with
`runtime-config.production.example.env` so production does not inherit local development endpoints.
Before deployment, copy or patch that file through a site-specific overlay or GitOps tooling with
your private Kafka, MQTT, S3, PostgreSQL, and Redis endpoints.

Kafka is configured for `SASL_SSL` by default in the production example. MQTT is configured for TLS
on port `8883`. Keep those defaults unless the network path is already private and encrypted by a
separate control plane.

The production runtime config subscribes to both generic device telemetry and WildFi telemetry:

```text
MQTT_TOPICS=$share/ingestors/devices/#,$share/ingestors/wildfi/#
WILDFI_TOPIC_PREFIXES=wildfi,wild-fi
```

`wildfi-decoder-config.yaml` documents the `wildlab/WildFiDecoder` conversion factors and expected
MQTT topic mapping. `wildfi-decoder-job.yaml` defines a suspended offline decoding Job using
`ghcr.io/smartappli/dealiot-wildfi-decoder`. Keep native WildFi binary logs in object storage or
decode them before publication.

Create a PVC named `wildfi-decoder-workdir` containing the `.bin` files before unsuspending a copied
decoder Job. The default mode is `2`, which decodes WildFi hdLogger movement data; mode `1` targets
proxLogger data and mode `3` decodes gateway metadata.

## Required Secret

Create `dealiot-secrets` with all keys listed in
`external-dependency-contract.yaml`. Prefer External Secrets Operator, Vault, or your cloud secret
manager over literal in-repo manifests. `dealiot-secrets.example.env` documents the required keys.

The runtime services require at least:

- `MQTT_PASSWORD`
- `KAFKA_SASL_PASSWORD`
- `MANAGEMENT_CONSOLE_TOKEN`

The Management Console keeps `/healthz` public for probes, but protects `/api/*` and mutation
routes with `Authorization: Bearer <token>` when `MANAGEMENT_CONSOLE_TOKEN` is set.

## Availability

The overlay adds HorizontalPodAutoscalers for the MQTT bridge, Flink TaskManager, Airflow workers,
and Management Console. It also adds PodDisruptionBudgets for the application tiers and uses
topology spread constraints so replicas are not concentrated on one node.

## Network Policy

The overlay applies default deny ingress/egress, then opens:

- namespace-internal traffic,
- DNS egress,
- production dependency ports for Kafka, MQTT over TLS, S3 over TLS, PostgreSQL, Redis,
- Airflow API ingress only from namespaces labeled `dealiot.io/ingress=allowed`.
- Management Console ingress only from namespaces labeled `dealiot.io/ingress=allowed`.

Patch `network-policies.yaml` with narrower `ipBlock` ranges for your actual private networks.
