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
  ghcr.io/smartappli/dealiot-flink-pyflink=ghcr.io/smartappli/dealiot-flink-pyflink:sha-"$RELEASE_SHA" \
  ghcr.io/smartappli/dealiot-orchestration=ghcr.io/smartappli/dealiot-orchestration:sha-"$RELEASE_SHA"
```

Do not deploy `latest` in production.

## Runtime Config

Use `runtime-config.production.example.env` as the source of expected runtime keys. Patch
`dealiot-runtime-config` through a site-specific overlay or through your GitOps tooling.

## Required Secret

Create `dealiot-secrets` with all keys listed in
`external-dependency-contract.yaml`. Prefer External Secrets Operator, Vault, or your cloud secret
manager over literal in-repo manifests. `dealiot-secrets.example.env` documents the required keys.

## Network Policy

The overlay applies default deny ingress/egress, then opens:

- namespace-internal traffic,
- DNS egress,
- production dependency ports for Kafka, MQTT over TLS, S3 over TLS, PostgreSQL, Redis,
- Airflow API ingress only from namespaces labeled `dealiot.io/ingress=allowed`.

Patch `network-policies.yaml` with narrower `ipBlock` ranges for your actual private networks.
