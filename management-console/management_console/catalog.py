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
        "name": "DGA intermediation gateway",
        "service": "management-console",
        "plane": "governance",
        "role": "Mediates access between collected data, applications and researchers.",
        "probe": "http://management-console:8080/healthz",
        "ui": "http://localhost:8090",
        "depends_on": ["kafka", "apicurio", "flink"],
        "data_scope": (
            "data product catalogue, access decisions, permissions and activity evidence."
        ),
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
    {
        "name": "governance.research.projects",
        "plane": "governance",
        "owner": "research-governance",
        "classification": "research-project-record",
        "retention": "compacted project register",
    },
    {
        "name": "governance.research.outputs",
        "plane": "governance",
        "owner": "research-governance",
        "classification": "research-output-record",
        "retention": "one year minimum, site policy required",
    },
    {
        "name": "dataact.product.catalog",
        "plane": "governance",
        "owner": "data-act-governance",
        "classification": "connected-product-metadata",
        "retention": "compacted catalogue",
    },
    {
        "name": "dataact.user.access.requests",
        "plane": "governance",
        "owner": "data-act-governance",
        "classification": "user-access-request",
        "retention": "one year minimum, site policy required",
    },
    {
        "name": "dataact.third_party.sharing",
        "plane": "governance",
        "owner": "data-act-governance",
        "classification": "third-party-sharing-authorization",
        "retention": "one year minimum, site policy required",
    },
    {
        "name": "dataact.user.exports",
        "plane": "governance",
        "owner": "data-act-governance",
        "classification": "user-export-evidence",
        "retention": "one year minimum, site policy required",
    },
    {
        "name": "dataact.safeguards",
        "plane": "governance",
        "owner": "data-act-governance",
        "classification": "trade-secret-security-safeguard",
        "retention": "compacted control register",
    },
]

DATA_PRODUCTS: list[dict[str, Any]] = [
    {
        "product_id": "telemetry.raw.gps",
        "title": "Raw GPS telemetry",
        "data_category": "personal",
        "source_topics": ["raw.gps"],
        "allowed_purposes": [
            "scientific research",
            "livestock behaviour research",
            "agronomic research",
        ],
        "access_mode": "mediated",
        "format": "JSON",
        "interoperability_standard": "Apicurio JSON Schema",
        "dga_gate": "requires approved research project, permission and GPS minimisation",
    },
    {
        "product_id": "telemetry.raw.sensor",
        "title": "Raw sensor telemetry",
        "data_category": "mixed",
        "source_topics": ["raw.sensor"],
        "allowed_purposes": [
            "scientific research",
            "device reliability research",
            "environmental research",
        ],
        "access_mode": "mediated",
        "format": "JSON",
        "interoperability_standard": "Apicurio JSON Schema",
        "dga_gate": "requires approved research project and field minimisation",
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
        "allowed_purposes": ["scientific research", "computer vision research"],
        "access_mode": "restricted",
        "format": "JSON",
        "interoperability_standard": "Apicurio JSON Schema",
        "dga_gate": "requires ethics review and object-level access controls",
    },
    {
        "product_id": "features.latest-state",
        "title": "Derived features and latest state",
        "data_category": "mixed",
        "source_topics": ["features.events", "state.latest"],
        "allowed_purposes": ["scientific research", "aggregate analytics"],
        "access_mode": "mediated",
        "format": "JSON",
        "interoperability_standard": "DEALIoT normalized event contract",
        "dga_gate": "preferred research sharing layer over raw topics",
    },
]

DATA_ACT_CONNECTED_PRODUCTS: list[dict[str, Any]] = [
    {
        "product_id": "connected-device.telemetry",
        "connected_product": "DEALIoT connected telemetry devices",
        "related_services": ["MQTT ingestion", "WildFi decoding", "media metadata ingestion"],
        "generated_data": ["raw.gps", "raw.sensor", "media object metadata"],
        "user_roles": ["device owner", "field operator", "research data holder"],
        "access_channels": ["dataact.direct-access", "dataact.research-mediated"],
        "default_access": "available through mediated access, not unrestricted raw topics",
        "third_party_sharing": "allowed only after user authorization and scope review",
        "contract_status": "terms and user notices required before production",
    },
    {
        "product_id": "related-service.analytics",
        "connected_product": "DEALIoT derived analytics service",
        "related_services": ["Flink feature projection", "latest-state API consumers"],
        "generated_data": ["features.events", "state.latest"],
        "user_roles": ["service customer", "research sponsor"],
        "access_channels": ["dataact.direct-access", "dataact.third-party-transfer"],
        "default_access": "preferred Data Act release layer for applications and researchers",
        "third_party_sharing": "supported through scoped application or research packages",
        "contract_status": "recipient terms and misuse restrictions required",
    },
]

DATA_ACT_ACCESS_CHANNELS: list[dict[str, Any]] = [
    {
        "channel_id": "dataact.direct-access",
        "name": "User direct access",
        "consumer": "user",
        "delivery": "secure API, controlled object access or minimised export",
        "default_policy": "grant access to generated data after identity and entitlement checks",
        "evidence_topics": [
            "dataact.user.access.requests",
            "dataact.user.exports",
            "governance.intermediation.log",
        ],
    },
    {
        "channel_id": "dataact.third-party-transfer",
        "name": "Third-party sharing by user request",
        "consumer": "third party selected by user",
        "delivery": "purpose-bound service account, signed export or controlled data package",
        "default_policy": "share only fields, time windows and purpose authorized by the user",
        "evidence_topics": [
            "dataact.third_party.sharing",
            "dataact.safeguards",
            "governance.transfer.notices",
        ],
    },
    {
        "channel_id": "dataact.research-mediated",
        "name": "Research access package",
        "consumer": "scientist or research organisation",
        "delivery": "DGA-mediated data product with Data Act user entitlement evidence",
        "default_policy": "prefer derived or pseudonymised datasets before raw generated data",
        "evidence_topics": [
            "governance.research.projects",
            "governance.access.requests",
            "dataact.user.access.requests",
        ],
    },
]

DATA_ACT_OBLIGATIONS: list[dict[str, str]] = [
    {
        "id": "user-access",
        "article": "Data Act Ch. II",
        "status": "partial",
        "control": (
            "Expose generated connected-product data to entitled users through clear channels."
        ),
    },
    {
        "id": "third-party-sharing",
        "article": "Data Act Ch. II",
        "status": "partial",
        "control": (
            "Enable user-authorized sharing to third parties with purpose and scope records."
        ),
    },
    {
        "id": "fair-contractual-terms",
        "article": "Data Act Ch. IV",
        "status": "todo",
        "control": "Review data-sharing terms for unfair clauses and transparent restrictions.",
    },
    {
        "id": "interoperability-export",
        "article": "Data Act Ch. VIII",
        "status": "implemented",
        "control": "Use JSON schemas, explicit formats and logged exports for portability.",
    },
    {
        "id": "trade-secret-safeguards",
        "article": "Data Act Ch. II",
        "status": "partial",
        "control": "Record proportionate safeguards before sharing sensitive generated data.",
    },
    {
        "id": "no-dark-pattern-release",
        "article": "Data Act Ch. II",
        "status": "todo",
        "control": "Define SLA, UX copy and operational path so user access is not obstructed.",
    },
]

DATA_ACT_USER_JOURNEY: list[dict[str, str]] = [
    {
        "step": "1",
        "name": "Connected product inventory",
        "control": "Register product, related service, generated data and user role.",
        "evidence": "dataact.product.catalog",
    },
    {
        "step": "2",
        "name": "User request",
        "control": "Capture entitlement, requested scope, time range, purpose and recipient.",
        "evidence": "dataact.user.access.requests",
    },
    {
        "step": "3",
        "name": "Safeguard check",
        "control": "Apply security, privacy, trade-secret and misuse controls before release.",
        "evidence": "dataact.safeguards",
    },
    {
        "step": "4",
        "name": "Delivery or third-party share",
        "control": (
            "Deliver data in a transparent format or transfer it to the user-selected party."
        ),
        "evidence": "dataact.user.exports, dataact.third_party.sharing",
    },
    {
        "step": "5",
        "name": "Audit and withdrawal",
        "control": "Log access, stop sharing on withdrawal and retain evidence under policy.",
        "evidence": "governance.intermediation.log",
    },
]

INTERMEDIATION_FLOW: list[dict[str, Any]] = [
    {
        "step": 1,
        "name": "Collected data landing",
        "source": "MQTT, media object storage, Kafka raw topics",
        "control": "raw data is retained in restricted ingestion/storage zones",
    },
    {
        "step": 2,
        "name": "Data product registration",
        "source": "governance.data.products",
        "control": "purpose, format, category, source topics and sharing mode are declared",
    },
    {
        "step": 3,
        "name": "Access request and review",
        "source": "governance.access.requests",
        "control": "application or researcher requests are reviewed against purpose and policy",
    },
    {
        "step": 4,
        "name": "Permission and project checks",
        "source": "governance.permission.events, governance.research.projects",
        "control": "permission, consent, protocol and ethics status are verified",
    },
    {
        "step": 5,
        "name": "Mediated delivery",
        "source": "derived topics, minimised exports, controlled object access",
        "control": "raw access is exceptional; derived or pseudonymised datasets are preferred",
    },
    {
        "step": 6,
        "name": "Activity and output logging",
        "source": "governance.intermediation.log, governance.research.outputs",
        "control": "retrieval, sharing, conversion, withdrawal and publication review are logged",
    },
]

CONSUMER_PROFILES: list[dict[str, Any]] = [
    {
        "profile_id": "application.operational",
        "name": "Operational application",
        "consumer_type": "application",
        "default_access": ["features.latest-state"],
        "raw_access": "denied by default",
        "required_evidence": ["access request", "service purpose", "least privilege scope"],
    },
    {
        "profile_id": "application.analytics",
        "name": "Analytics or decision-support application",
        "consumer_type": "application",
        "default_access": ["features.latest-state", "telemetry.raw.sensor"],
        "raw_access": "exceptional and field-minimised",
        "required_evidence": ["access request", "data protection review", "retention scope"],
    },
    {
        "profile_id": "researcher.internal",
        "name": "Internal scientist",
        "consumer_type": "researcher",
        "default_access": ["features.latest-state", "telemetry.raw.sensor"],
        "raw_access": "requires protocol and ethics status",
        "required_evidence": ["research project", "permission model", "publication review"],
    },
    {
        "profile_id": "researcher.external",
        "name": "External researcher or research organisation",
        "consumer_type": "researcher",
        "default_access": ["features.latest-state"],
        "raw_access": "restricted and contract-bound",
        "required_evidence": [
            "research project",
            "data sharing agreement",
            "permission or consent",
            "third-country check if applicable",
        ],
    },
]

RESEARCH_CONTEXT: dict[str, Any] = {
    "primary_purpose": "scientific research",
    "dga_mode": "research collection with possible data altruism workflow",
    "general_interest_objectives": [
        "livestock welfare research",
        "precision agriculture research",
        "environmental monitoring research",
    ],
    "required_release_gates": [
        "documented research protocol",
        "ethics review decision or documented exemption",
        "DPIA or risk assessment for GPS, media and linked identifiers",
        "data holder permission or data subject consent where applicable",
        "pseudonymisation before researcher access",
        "publication disclosure review before external release",
    ],
    "intermediation_position": (
        "applications and scientists consume data through mediated data products, not direct raw "
        "topic access"
    ),
}

RESEARCH_PROJECTS: list[dict[str, Any]] = [
    {
        "project_id": "research.template.livestock-behaviour",
        "title": "Livestock behaviour and welfare research",
        "objective": "Analyse telemetry and derived movement patterns for animal welfare research.",
        "data_products": ["telemetry.raw.gps", "telemetry.raw.sensor", "features.latest-state"],
        "permission_model": "data_holder_permission",
        "ethics_review_status": "pending",
        "sharing_layer": "derived data preferred; raw GPS restricted",
    },
    {
        "project_id": "research.template.precision-agriculture",
        "title": "Precision agriculture and environmental research",
        "objective": "Study environmental telemetry and field context for agronomic research.",
        "data_products": ["telemetry.raw.sensor", "features.latest-state"],
        "permission_model": "data_holder_permission",
        "ethics_review_status": "pending",
        "sharing_layer": "minimised sensor fields and aggregated outputs",
    },
]

RESEARCH_CONTROLS: list[dict[str, str]] = [
    {
        "id": "research-protocol",
        "status": "todo",
        "control": "Register each research protocol before data access.",
    },
    {
        "id": "ethics-review",
        "status": "todo",
        "control": "Record ethics approval, rejection or exemption for each project.",
    },
    {
        "id": "research-permission",
        "status": "partial",
        "control": "Link project access to data holder permission or data subject consent.",
    },
    {
        "id": "research-minimisation",
        "status": "partial",
        "control": "Prefer derived, pseudonymised and aggregated data over raw GPS/media.",
    },
    {
        "id": "publication-review",
        "status": "todo",
        "control": "Review outputs for re-identification risk before publication or sharing.",
    },
]

DGA_OBLIGATIONS: list[dict[str, str]] = [
    {
        "id": "notification",
        "article": "DGA Art. 11",
        "status": "organisational",
        "control": (
            "Notify the competent authority if research sharing becomes data intermediation."
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
        "status": "implemented",
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
        "control": "Require mediated delivery, TLS/SASL/mTLS and least privilege scopes.",
    },
    {
        "id": "consent-permission",
        "article": "DGA Art. 12(n), Art. 21, Art. 25",
        "status": "partial",
        "control": "Provide tools to give and withdraw research consent or permission.",
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
        "name": "Data Act",
        "path": "docs/runbooks/data-act.md",
        "scope": "User access, third-party sharing and generated connected-product data.",
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
    {
        "id": "review-data-act-readiness",
        "name": "Review Data Act readiness",
        "method": "GET",
        "endpoint": "/api/data-act",
        "scope": "safe",
        "description": (
            "Lists connected products, user access channels, sharing evidence and open gaps."
        ),
    },
    {
        "id": "review-intermediation-flow",
        "name": "Review intermediation flow",
        "method": "GET",
        "endpoint": "/api/intermediation",
        "scope": "safe",
        "description": "Lists consumer profiles, mediated delivery steps and required evidence.",
    },
    {
        "id": "review-research-readiness",
        "name": "Review research readiness",
        "method": "GET",
        "endpoint": "/api/research",
        "scope": "safe",
        "description": "Lists research purpose, project templates, gates and publication controls.",
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
        "id": "mediated-access",
        "status": "implemented",
        "regulation": "DGA",
        "control": "Route applications and researchers through mediated data products.",
    },
    {
        "id": "dga-permissions",
        "status": "partial",
        "regulation": "DGA",
        "control": "Track research permissions, consent and withdrawals.",
    },
    {
        "id": "research-governance",
        "status": "partial",
        "regulation": "DGA, GDPR",
        "control": "Require research protocol, ethics status and disclosure review.",
    },
    {
        "id": "dga-activity-log",
        "status": "implemented",
        "regulation": "DGA",
        "control": "Maintain a log record of data intermediation activity.",
    },
    {
        "id": "data-act-user-access",
        "status": "partial",
        "regulation": "Data Act",
        "control": (
            "Provide user access to generated connected-product data through logged channels."
        ),
    },
    {
        "id": "data-act-third-party-sharing",
        "status": "partial",
        "regulation": "Data Act",
        "control": "Share data with third parties only on user authorization and scoped evidence.",
    },
    {
        "id": "data-act-portability",
        "status": "implemented",
        "regulation": "Data Act",
        "control": "Publish portable JSON contracts and export logs for released datasets.",
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
        "data_act_connected_products": DATA_ACT_CONNECTED_PRODUCTS,
        "data_act_access_channels": DATA_ACT_ACCESS_CHANNELS,
        "data_act_obligations": DATA_ACT_OBLIGATIONS,
        "data_act_user_journey": DATA_ACT_USER_JOURNEY,
        "intermediation_flow": INTERMEDIATION_FLOW,
        "consumer_profiles": CONSUMER_PROFILES,
        "dga_obligations": DGA_OBLIGATIONS,
        "research_context": RESEARCH_CONTEXT,
        "research_projects": RESEARCH_PROJECTS,
        "research_controls": RESEARCH_CONTROLS,
        "runbooks": RUNBOOKS,
        "operations": OPERATIONS,
        "compliance_controls": COMPLIANCE_CONTROLS,
    }


def data_act_payload() -> dict[str, Any]:
    return {
        "connected_products": DATA_ACT_CONNECTED_PRODUCTS,
        "access_channels": DATA_ACT_ACCESS_CHANNELS,
        "obligations": DATA_ACT_OBLIGATIONS,
        "user_journey": DATA_ACT_USER_JOURNEY,
        "evidence_topics": [
            topic
            for topic in TOPICS
            if topic["name"].startswith("dataact.")
            or topic["name"] in {"governance.intermediation.log", "governance.transfer.notices"}
        ],
        "default_policy": {
            "raw_topics": "denied by default unless scope, entitlement and safeguards are approved",
            "preferred_delivery": [
                "direct secure API",
                "minimised export",
                "controlled object access",
                "DGA-mediated research data product",
            ],
            "third_party_sharing": (
                "requires user authorization, recipient identity and purpose scope"
            ),
            "research_access": "combine Data Act user entitlement with DGA research governance",
        },
    }


def dga_payload() -> dict[str, Any]:
    return {
        "data_products": DATA_PRODUCTS,
        "intermediation_flow": INTERMEDIATION_FLOW,
        "consumer_profiles": CONSUMER_PROFILES,
        "obligations": DGA_OBLIGATIONS,
        "research_context": RESEARCH_CONTEXT,
        "research_projects": RESEARCH_PROJECTS,
        "research_controls": RESEARCH_CONTROLS,
        "evidence_topics": [
            topic
            for topic in TOPICS
            if topic["name"].startswith("governance.") or topic["name"] == "dlq.events"
        ],
        "architectural_principles": [
            "separate governance plane for intermediation metadata",
            "no own reuse of mediated data by the intermediation layer",
            "purpose-bound access requests and decisions",
            "consumer profiles for applications and scientists",
            "mediated delivery before raw access",
            "consent and permission withdrawal evidence",
            "activity logging for every data-sharing action",
            "research protocol and ethics status before project access",
            "publication disclosure review before external release",
            "schema-based interoperability and transparent formats",
            "unauthorised access, transfer and use notice trail",
        ],
    }


def research_payload() -> dict[str, Any]:
    return {
        "research_context": RESEARCH_CONTEXT,
        "projects": RESEARCH_PROJECTS,
        "controls": RESEARCH_CONTROLS,
        "research_topics": [
            topic
            for topic in TOPICS
            if topic["name"].startswith("governance.research.")
        ],
        "recommended_default": (
            "share derived or pseudonymised research datasets before raw GPS, raw payloads or media"
        ),
    }


def intermediation_payload() -> dict[str, Any]:
    return {
        "flow": INTERMEDIATION_FLOW,
        "consumer_profiles": CONSUMER_PROFILES,
        "default_policy": {
            "raw_topics": "restricted",
            "derived_topics": "preferred",
            "applications": "purpose-bound service accounts",
            "scientists": "project-bound access packages",
            "evidence": [
                "governance.access.requests",
                "governance.permission.events",
                "governance.intermediation.log",
                "governance.research.projects",
                "governance.research.outputs",
            ],
        },
    }
