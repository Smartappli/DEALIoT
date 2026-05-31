# DEALIoT Management Console

Internal web console for operating the DEALIoT platform.

It exposes:

- platform topology and component ownership,
- HTTP/TCP health probes from inside the Compose or Kubernetes networks,
- Kafka topic and data classification inventory,
- DGA data products, access/permission evidence topics and readiness controls,
- research project, ethics and output disclosure controls,
- runbook and operation catalogue,
- compliance-control tracking for GDPR, Data Act, DGA, AI Act, CRA and NIS2.

The console intentionally does not mount the Docker socket. Host-level start/stop/restart remains a
CLI or orchestrator responsibility.
