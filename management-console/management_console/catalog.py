from __future__ import annotations

from typing import Any

COMPONENTS: list[dict[str, Any]] = [
    {
        "id": "vernemq",
        "name": "VerneMQ",
        "service": "vernemq1",
        "plane": "ingestion",
        "role": "MQTT broker cluster for device telemetry and WildFi gateways.",
        "probe": "tcp://vernemq1:1883",
        "ui": None,
        "depends_on": [],
        "data_scope": "device identifiers, telemetry, GPS and media metadata topics.",
        "risk": "high",
    },
    {
        "id": "mqtt-kafka-bridge",
        "name": "MQTT to Kafka bridge",
        "service": "mqtt-kafka-bridge",
        "plane": "ingestion",
        "role": "Validates and routes MQTT payloads to raw Kafka topics or DLQ.",
        "probe": None,
        "ui": None,
        "depends_on": ["vernemq", "kafka"],
        "data_scope": "raw payloads, device identifiers, MQTT topics and timestamps.",
        "risk": "high",
    },
    {
        "id": "kafka",
        "name": "Kafka KRaft cluster",
        "service": "kafka1",
        "plane": "backbone",
        "role": "Event backbone for raw, derived, state and platform topics.",
        "probe": "tcp://kafka1:9092",
        "ui": None,
        "depends_on": [],
        "data_scope": "all platform event streams.",
        "risk": "high",
    },
    {
        "id": "kafka-connect",
        "name": "Kafka Connect",
        "service": "kafka-connect",
        "plane": "backbone",
        "role": "Runs Debezium and integration connectors.",
        "probe": "http://kafka-connect:8083/connectors",
        "ui": None,
        "depends_on": ["kafka", "timescaledb"],
        "data_scope": "database change events and connector offsets.",
        "risk": "medium",
    },
    {
        "id": "apicurio",
        "name": "Apicurio Registry",
        "service": "apicurio-registry",
        "plane": "backbone",
        "role": "Schema registry and event contract governance.",
        "probe": "http://apicurio-registry:9000/health/ready",
        "ui": "http://localhost:8888",
        "depends_on": ["kafka"],
        "data_scope": "schema metadata and registry events.",
        "risk": "medium",
    },
    {
        "id": "seaweedfs",
        "name": "SeaweedFS S3",
        "service": "seaweedfs-s3",
        "plane": "storage",
        "role": "S3-compatible object storage for raw media and processing state.",
        "probe": "http://seaweedfs-s3:8333/",
        "ui": "http://localhost:8889",
        "depends_on": ["seaweedfs-filer"],
        "data_scope": "media objects, Flink checkpoints and savepoints.",
        "risk": "high",
    },
    {
        "id": "timescaledb",
        "name": "TimescaleDB HA",
        "service": "haproxy",
        "plane": "storage",
        "role": "HA PostgreSQL/TimescaleDB entrypoint through HAProxy.",
        "probe": "tcp://haproxy:5432",
        "ui": "http://localhost:5050",
        "depends_on": ["etcd"],
        "data_scope": "application database records and derived state.",
        "risk": "high",
    },
    {
        "id": "flink",
        "name": "Flink",
        "service": "flink-jobmanager",
        "plane": "processing",
        "role": "Stateful stream processing and latest-state projection.",
        "probe": "http://flink-jobmanager:8081/overview",
        "ui": "http://localhost:8081",
        "depends_on": ["kafka", "seaweedfs"],
        "data_scope": "raw events, features, state and checkpoint data.",
        "risk": "high",
    },
    {
        "id": "beam",
        "name": "Beam job server",
        "service": "beam-jobserver",
        "plane": "processing",
        "role": "Portable batch/stream pipeline execution endpoint.",
        "probe": "tcp://beam-jobserver:8099",
        "ui": None,
        "depends_on": ["flink"],
        "data_scope": "pipeline artifacts and runtime data depending on submitted jobs.",
        "risk": "medium",
    },
    {
        "id": "airflow",
        "name": "Airflow",
        "service": "airflow-apiserver",
        "plane": "orchestration",
        "role": "Schedules backfills and operational workflows.",
        "probe": "http://airflow-apiserver:8080/api/v2/version",
        "ui": "http://localhost:8088",
        "depends_on": ["airflow-postgres", "airflow-redis", "kafka", "seaweedfs"],
        "data_scope": "DAG metadata, task logs, replay windows and object references.",
        "risk": "medium",
    },
    {
        "id": "prometheus",
        "name": "Prometheus",
        "service": "prometheus",
        "plane": "observability",
        "role": "Metrics collection, retention and alert evaluation.",
        "probe": "http://prometheus:9090/-/ready",
        "ui": "http://localhost:9090",
        "depends_on": [],
        "data_scope": "operational metrics and service labels.",
        "risk": "medium",
    },
    {
        "id": "grafana",
        "name": "Grafana",
        "service": "grafana",
        "plane": "observability",
        "role": "Operational dashboards for streaming, storage, database and alerts.",
        "probe": "http://grafana:3000/api/health",
        "ui": "http://localhost:3000",
        "depends_on": ["prometheus"],
        "data_scope": "dashboards, users and metrics queries.",
        "risk": "medium",
    },
    {
        "id": "data-governance",
        "name": "DGA governance control plane",
        "service": "management-console",
        "plane": "governance",
        "role": "Tracks data products, permissions, access requests and intermediation logs.",
        "probe": "http://management-console:8080/healthz",
        "ui": "http://localhost:8090",
        "depends_on": ["kafka", "apicurio"],
        "data_scope": "DGA metadata, data-sharing decisions and activity evidence.",
        "risk": "high",
    },
]

TOPICS: list[dict[str, str]] = [
    {
        "name": "raw.gps",
        "plane": "raw",
        "owner": "ingestion",
        "classification": "personal-location",
        "retention": "define before production",
    },
    {
        "name": "raw.sensor",
        "plane": "raw",
        "owner": "ingestion",
        "classification": "personal-or-device",
        "retention": "define before production",
    },
    {
        "name": "raw.image2d.meta",
        "plane": "raw",
        "owner": "media",
        "classification": "media-metadata",
        "retention": "define before production",
    },
    {
        "name": "raw.image3d.meta",
        "plane": "raw",
        "owner": "media",
        "classification": "media-metadata",
        "retention": "define before production",
    },
    {
        "name": "raw.video2d.meta",
        "plane": "raw",
        "owner": "media",
        "classification": "media-metadata",
        "retention": "define before production",
    },
    {
        "name": "raw.video3d.meta",
        "plane": "raw",
        "owner": "media",
        "classification": "media-metadata",
        "retention": "define before production",
    },
    {
        "name": "features.events",
        "plane": "derived",
        "owner": "processing",
        "classification": "derived",
        "retention": "define before production",
    },
    {
        "name": "state.latest",
        "plane": "state",
        "owner": "processing",
        "classification": "derived-current-state",
        "retention": "compacted plus delete tombstones",
    },
    {
        "name": "dlq.events",
        "plane": "platform",
        "owner": "platform",
        "classification": "raw-error-copy",
        "retention": "short retention required",
    },
    {
        "name": "governance.data.products",
        "plane": "governance",
        "owner": "data-governance",
        "classification": "metadata",
        "retention": "compacted catalogue",
    },
    {
        "name": "governance.access.requests",
        "plane": "governance",
        "owner": "data-governance",
        "classification": "access-decision-record",
        "retention": "one year minimum, site policy required",
    },
    {
        "name": "governance.permission.events",
        "plane": "governance",
        "owner": "data-governance",
        "classification": "consent-or-permission-record",
        "retention": "compacted with withdrawal evidence",
    },
    {
        "name": "governance.intermediation.log",
        "plane": "governance",
        "owner": "data-governance",
        "classification": "intermediation-activity-log",
        "retention": "one year minimum, site policy required",
    },
    {
        "name": "governance.transfer.notices",
        "plane": "governance",
        "owner": "data-governance",
        "classification": "incident-notice-record",
        "retention": "one year minimum, site policy required",
    },
]

DATA_PRODUCTS: list[dict[str, Any]] = [
    {
        "product_id": "telemetry.raw.gps",
        "title": "Raw GPS telemetry",
        "data_category": "personal",
        "source_topics": ["raw.gps"],
        "allowed_purposes": ["livestock monitoring", "agronomic analysis"],
        "access_mode": "mediated",
        "format": "JSON",
        "interoperability_standard": "Apicurio JSON Schema",
        "dga_gate": "requires permission and purpose review",
    },
    {
        "product_id": "telemetry.raw.sensor",
        "title": "Raw sensor telemetry",
        "data_category": "mixed",
        "source_topics": ["raw.sensor"],
        "allowed_purposes": ["device monitoring", "research with approved purpose"],
        "access_mode": "mediated",
        "format": "JSON",
        "interoperability_standard": "Apicurio JSON Schema",
        "dga_gate": "requires field minimisation before sharing",
    },
    {
        "product_id": "media.metadata",
        "title": "Media object metadata",
        "data_category": "mixed",
        "source_topics": [
            "raw.image2d.meta",
            "raw.image3d.meta",
            "raw.video2d.meta",
            "raw.video3d.meta",
        ],
        "allowed_purposes": ["media processing", "quality analysis"],
        "access_mode": "restricted",
        "format": "JSON",
        "interoperability_standard": "Apicurio JSON Schema",
        "dga_gate": "requires object-level access controls",
    },
    {
        "product_id": "features.latest-state",
        "title": "Derived features and latest state",
        "data_category": "mixed",
        "source_topics": ["features.events", "state.latest"],
        "allowed_purposes": ["operational monitoring", "analytics"],
        "access_mode": "mediated",
        "format": "JSON",
        "interoperability_standard": "DEALIoT normalized event contract",
        "dga_gate": "preferred sharing layer over raw topics",
    },
]

DGA_OBLIGATIONS: list[dict[str, str]] = [
    {
        "id": "notification",
        "article": "DGA Art. 11",
        "status": "organisational",
        "control": (
            "Notify the competent authority before operating as a data intermediation service."
        ),
    },
    {
        "id": "neutrality",
        "article": "DGA Art. 12(a)-(b)",
        "status": "partial",
        "control": (
            "Keep intermediation logically separated and do not use mediated data for own purposes."
        ),
    },
    {
        "id": "activity-metadata-purpose",
        "article": "DGA Art. 12(c)",
        "status": "implemented",
        "control": (
            "Use intermediation activity metadata only to operate, secure and improve the service."
        ),
    },
    {
        "id": "format-interoperability",
        "article": "DGA Art. 12(d),(i)",
        "status": "implemented",
        "control": (
            "Publish data products through explicit JSON schemas and avoid conversion by default."
        ),
    },
    {
        "id": "fair-access",
        "article": "DGA Art. 12(f)",
        "status": "partial",
        "control": "Track access requests, decisions and reasons in governance.access.requests.",
    },
    {
        "id": "abuse-prevention",
        "article": "DGA Art. 12(g)",
        "status": "todo",
        "control": "Define sanctions, suspension and exclusion workflow for abusive data users.",
    },
    {
        "id": "continuity",
        "article": "DGA Art. 12(h)",
        "status": "partial",
        "control": "Back up governance topics and document retrieval/transfer procedures.",
    },
    {
        "id": "security",
        "article": "DGA Art. 12(j)-(l)",
        "status": "partial",
        "control": "Require TLS/SASL/mTLS, least privilege and unauthorised transfer notices.",
    },
    {
        "id": "consent-permission",
        "article": "DGA Art. 12(n), Art. 21, Art. 25",
        "status": "partial",
        "control": "Provide tools to give and withdraw consent or permission before data sharing.",
    },
    {
        "id": "intermediation-log",
        "article": "DGA Art. 12(o)",
        "status": "implemented",
        "control": (
            "Reserve governance.intermediation.log as immutable evidence of sharing activity."
        ),
    },
]

RUNBOOKS: list[dict[str, str]] = [
    {
        "name": "Operations",
        "path": "docs/runbooks/operations.md",
        "scope": "startup validation, runtime checks and troubleshooting.",
    },
    {
        "name": "Backup and restore",
        "path": "docs/runbooks/backup-restore.md",
        "scope": "database, object storage and platform recovery.",
    },
    {
        "name": "Security hardening",
        "path": "docs/runbooks/security-hardening.md",
        "scope": "TLS, authentication, secret handling and rotation.",
    },
    {
        "name": "Data Governance Act",
        "path": "docs/runbooks/data-governance-act.md",
        "scope": "DGA role decision, intermediation evidence and data-sharing controls.",
    },
    {
        "name": "WildFi ingestion",
        "path": "docs/runbooks/wildfi-ingestion.md",
        "scope": "WildFi topic mapping, decoder use and data contracts.",
    },
]

OPERATIONS: list[dict[str, Any]] = [
    {
        "id": "refresh-health",
        "name": "Refresh service health",
        "method": "GET",
        "endpoint": "/api/health",
        "scope": "safe",
        "description": "Re-runs HTTP and TCP probes from inside the platform networks.",
    },
    {
        "id": "trigger-media-backfill",
        "name": "Trigger media backfill DAG",
        "method": "POST",
        "endpoint": "/api/operations/trigger-media-backfill",
        "scope": "controlled",
        "description": (
            "Triggers the Airflow media_backfill DAG when Airflow API credentials are set."
        ),
        "requires": ["AIRFLOW_API_USERNAME", "AIRFLOW_API_PASSWORD"],
    },
    {
        "id": "open-runbooks",
        "name": "Open runbooks",
        "method": "GET",
        "endpoint": "/api/runbooks",
        "scope": "safe",
        "description": "Lists operational runbooks included in the repository.",
    },
    {
        "id": "review-dga-readiness",
        "name": "Review DGA readiness",
        "method": "GET",
        "endpoint": "/api/dga",
        "scope": "safe",
        "description": "Lists DGA data products, obligations, evidence topics and open gaps.",
    },
]

COMPLIANCE_CONTROLS: list[dict[str, str]] = [
    {
        "id": "data-map",
        "status": "partial",
        "regulation": "GDPR, Data Act, DGA",
        "control": (
            "Maintain topic-level and data-product inventory, purpose, owner and recipients."
        ),
    },
    {
        "id": "dga-neutrality",
        "status": "partial",
        "regulation": "DGA",
        "control": "Operate data intermediation as a separated governance plane with no own reuse.",
    },
    {
        "id": "dga-permissions",
        "status": "partial",
        "regulation": "DGA",
        "control": "Track data-holder permissions, data-subject consent and withdrawals.",
    },
    {
        "id": "dga-activity-log",
        "status": "implemented",
        "regulation": "DGA",
        "control": "Maintain a log record of data intermediation activity.",
    },
    {
        "id": "retention",
        "status": "todo",
        "regulation": "GDPR, Data Act",
        "control": "Apply retention policies to raw Kafka topics, S3 buckets, DLQ and backups.",
    },
    {
        "id": "pseudonymisation",
        "status": "todo",
        "regulation": "GDPR",
        "control": "Pseudonymise device identifiers and restrict raw GPS/media access.",
    },
    {
        "id": "transport-security",
        "status": "partial",
        "regulation": "GDPR, CRA, NIS2",
        "control": "Replace local plaintext protocols with TLS/SASL/mTLS in production.",
    },
    {
        "id": "supply-chain",
        "status": "partial",
        "regulation": "CRA, NIS2",
        "control": "Publish SBOM/provenance and add image signature admission policy.",
    },
    {
        "id": "ai-governance",
        "status": "todo",
        "regulation": "AI Act",
        "control": "Classify and document future AI use cases before model deployment.",
    },
]


def catalog_payload() -> dict[str, Any]:
    return {
        "components": COMPONENTS,
        "topics": TOPICS,
        "data_products": DATA_PRODUCTS,
        "dga_obligations": DGA_OBLIGATIONS,
        "runbooks": RUNBOOKS,
        "operations": OPERATIONS,
        "compliance_controls": COMPLIANCE_CONTROLS,
    }


def dga_payload() -> dict[str, Any]:
    return {
        "data_products": DATA_PRODUCTS,
        "obligations": DGA_OBLIGATIONS,
        "evidence_topics": [
            topic
            for topic in TOPICS
            if topic["name"].startswith("governance.") or topic["name"] == "dlq.events"
        ],
        "architectural_principles": [
            "separate governance plane for intermediation metadata",
            "no own reuse of mediated data by the intermediation layer",
            "purpose-bound access requests and decisions",
            "consent and permission withdrawal evidence",
            "activity logging for every data-sharing action",
            "schema-based interoperability and transparent formats",
            "unauthorised access, transfer and use notice trail",
        ],
    }
