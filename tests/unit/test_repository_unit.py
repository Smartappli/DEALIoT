from __future__ import annotations

import ast
import json
import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class RepositoryUnitTests(unittest.TestCase):
    def test_critical_repository_files_exist(self) -> None:
        required_files = [
            REPO_ROOT / "docker-compose.yml",
            REPO_ROOT / "docker-compose.dev.yml",
            REPO_ROOT / "docker-compose.staging.yml",
            REPO_ROOT / "docker-compose.prod.yml",
            REPO_ROOT / ".dockerignore",
            REPO_ROOT / "README.md",
            REPO_ROOT / "CONTRIBUTING.md",
            REPO_ROOT / "CODE_OF_CONDUCT.md",
            REPO_ROOT / "SECURITY.md",
            REPO_ROOT / "SUPPORT.md",
            REPO_ROOT / "ROADMAP.md",
            REPO_ROOT / "ADOPTERS.md",
            REPO_ROOT / "CITATION.cff",
            REPO_ROOT / "scripts" / "smoke-e2e.sh",
            REPO_ROOT / "docs" / "community" / "README.md",
            REPO_ROOT / "docs" / "community" / "adoption-playbook.md",
            REPO_ROOT / "docs" / "community" / "demo-pilot-playbook.md",
            REPO_ROOT / "docs" / "community" / "integration-partner-guide.md",
            REPO_ROOT / "docs" / "community" / "validation-scorecard.md",
            REPO_ROOT / "docs" / "community" / "adopter-story-template.md",
            REPO_ROOT / "docs" / "runbooks" / "operations.md",
            REPO_ROOT / "docs" / "runbooks" / "backup-restore.md",
            REPO_ROOT / "docs" / "runbooks" / "security-hardening.md",
            REPO_ROOT / "docs" / "runbooks" / "security-resilience-compliance.md",
            REPO_ROOT / "docs" / "runbooks" / "legal-applicability.md",
            REPO_ROOT / "docs" / "runbooks" / "data-governance-act.md",
            REPO_ROOT / "docs" / "runbooks" / "data-act.md",
            REPO_ROOT / "docs" / "runbooks" / "data-management-plan.md",
            REPO_ROOT / "docs" / "runbooks" / "zenodo-export.md",
            REPO_ROOT / "docs" / "runbooks" / "openaire-export.md",
            REPO_ROOT / "docs" / "runbooks" / "wildfi-ingestion.md",
            REPO_ROOT / "docs" / "architecture" / "scalable-production-audit.md",
            REPO_ROOT / "docs" / "wiki" / "Home.md",
            REPO_ROOT / "docs" / "wiki" / "Architecture.md",
            REPO_ROOT / "docs" / "wiki" / "Production-Deployment.md",
            REPO_ROOT / "docs" / "wiki" / "Configuration-Reference.md",
            REPO_ROOT / "docs" / "wiki" / "Security-and-Compliance.md",
            REPO_ROOT / "docs" / "wiki" / "Operations-and-Scaling.md",
            REPO_ROOT / "docs" / "wiki" / "CI-CD-and-Release.md",
            REPO_ROOT / "docs" / "wiki" / "Runbook-Index.md",
            REPO_ROOT / "docs" / "compliance" / "legal-compliance-dossier.md",
            REPO_ROOT / "docs" / "compliance" / "legal-finalization-report.md",
            REPO_ROOT / "docs" / "compliance" / "legal-readiness-review.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "ropa-template.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "dpia-template.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "privacy-notice-template.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "data-act-notice-template.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "data-sharing-agreement-checklist.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "processor-dpa-checklist.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "data-subject-rights-procedure.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "dga-role-notification-template.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "scope-decision-template.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "reporting-channel-template.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "cra-conformity-file-template.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "ai-system-inventory-template.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "eprivacy-assessment-template.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "retention-schedule-template.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "incident-notification-playbook.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "zenodo-publication-approval.md",
            REPO_ROOT / "docs" / "compliance" / "templates" / "openaire-discovery-approval.md",
            REPO_ROOT / ".github" / "workflows" / "ci.yml",
            REPO_ROOT / ".github" / "dependabot.yml",
            REPO_ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md",
            REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml",
            REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml",
            REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml",
            REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "demo_request.yml",
            REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "adopter_story.yml",
            REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "documentation.yml",
            REPO_ROOT / ".github" / "workflows" / "e2e-smoke.yml",
            REPO_ROOT / ".github" / "workflows" / "website-pages.yml",
            REPO_ROOT / "bandit.yaml",
            REPO_ROOT / "website" / "index.html",
            REPO_ROOT / "website" / "fr" / "index.html",
            REPO_ROOT / "website" / "offline.html",
            REPO_ROOT / "website" / "styles.css",
            REPO_ROOT / "website" / "app.js",
            REPO_ROOT / "website" / "sw.js",
            REPO_ROOT / "website" / "README.md",
            REPO_ROOT / "website" / "robots.txt",
            REPO_ROOT / "website" / "sitemap.xml",
            REPO_ROOT / "website" / "CNAME",
            REPO_ROOT / "website" / "eu-languages.json",
            REPO_ROOT / "website" / "llms.txt",
            REPO_ROOT / "website" / "humans.txt",
            REPO_ROOT / "website" / "site.webmanifest",
            REPO_ROOT / "website" / "assets" / "mark.svg",
            REPO_ROOT / "website" / "assets" / "icon-192.png",
            REPO_ROOT / "website" / "assets" / "icon-512.png",
            REPO_ROOT / "website" / "assets" / "icon-maskable-512.png",
            REPO_ROOT / "website" / "assets" / "social-card.svg",
            REPO_ROOT / "website" / "assets" / "social-card.png",
            REPO_ROOT / "wildfi-decoder" / "Dockerfile",
            REPO_ROOT / "wildfi-decoder" / "run-wildfi-decoder.sh",
            REPO_ROOT / "management-console" / "Dockerfile",
            REPO_ROOT / "management-console" / "management_console" / "app.py",
            REPO_ROOT / "management-console" / "management_console" / "openaire.py",
        ]

        for file_path in required_files:
            self.assertTrue(file_path.is_file(), f"Missing file: {file_path}")

    def test_readme_is_professional_project_entrypoint(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        for required_heading in (
            "# DEALIoT",
            "## Platform Scope",
            "## Architecture",
            "## Local Development",
            "## Production Deployment",
            "## Runtime Security",
            "## Testing And Quality Gates",
            "## Operations And Runbooks",
            "## Website And Adoption",
        ):
            self.assertIn(required_heading, readme)

        for forbidden_fragment in (
            "Recent reliability hardening:",
            "MQTTâ",
            "Recommended next steps",
            "Included artifacts in this finalized package",
        ):
            self.assertNotIn(forbidden_fragment, readme)

        self.assertIn("Kubernetes is the primary production target", readme)
        self.assertIn("The GitHub Wiki contains the production architecture handbook", readme)
        self.assertIn("docs/community/adoption-playbook.md", readme)
        self.assertIn("CONTRIBUTING.md", readme)

    def test_versioned_wiki_source_covers_production_operations(self) -> None:
        wiki_dir = REPO_ROOT / "docs" / "wiki"
        wiki_text = "\n".join(path.read_text(encoding="utf-8") for path in wiki_dir.glob("*.md"))

        for required_fragment in (
            "Production Deployment",
            "Configuration Reference",
            "Security And Compliance",
            "Operations And Scaling",
            "CI/CD And Release",
            "Pod Security `restricted`",
            "Kafka `SASL_SSL`",
            "MQTT TLS",
            "NetworkPolicies",
            "HPA",
            "PDB",
        ):
            self.assertIn(required_fragment, wiki_text)

    def test_apicurio_bootstrap_json_payloads_are_strings(self) -> None:
        bootstrap_files = [
            REPO_ROOT / "apicurio" / "bootstrap" / "dlq.events.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "raw.sensor.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "media.object.events.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "governance.data.products.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "governance.permission.events.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "governance.intermediation.log.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "governance.research.projects.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "governance.research.outputs.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "governance.dataset.catalog.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "governance.data_management_plans.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "governance.repository.exports.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "dataact.product.catalog.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "dataact.user.access.requests.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "dataact.third_party.sharing.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "dataact.user.exports.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "dataact.safeguards.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "dataact.legal_basis.checks.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "security.asset.inventory.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "security.incident.events.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "security.vulnerability.findings.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "security.sbom.attestations.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "security.patch.events.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "resilience.backup.tests.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "resilience.operational.risk.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "resilience.third_party.risk.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "compliance.scope.decisions.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "compliance.control.assessments.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "compliance.reporting.channels.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "compliance.legal.dossier.json",
            REPO_ROOT / "apicurio" / "bootstrap" / "cra.product.lifecycle.json",
        ]

        for file_path in bootstrap_files:
            payload = json.loads(file_path.read_text(encoding="utf-8"))
            content = payload["firstVersion"]["content"]["content"]
            self.assertIsInstance(content, str, f"Invalid embedded schema content in {file_path}")
            self.assertGreater(
                len(content), 20, f"Embedded schema content too short in {file_path}"
            )

    def test_compose_uses_canonical_state_latest_topic(self) -> None:
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        flink_text = (REPO_ROOT / "flink" / "jobs" / "streaming_minimal.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("--topic state.latest", compose_text)
        self.assertIn(
            'env_or_default("STATE_TOPIC", "state.latest")',
            flink_text,
        )
        self.assertNotIn("state-latest", compose_text)

    def test_apicurio_init_posts_bootstrap_payloads_directly(self) -> None:
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")

        self.assertIn('--data @"$$file"', compose_text)
        self.assertNotIn("content_escaped", compose_text)
        self.assertIn('"$$base/groups/$$group/artifacts/$$artifact"', compose_text)
        self.assertIn('ready_url="http://apicurio-registry:9000/health/ready"', compose_text)
        self.assertIn("ready_attempts=120", compose_text)
        self.assertIn("curl --connect-timeout 5 --max-time 10 -fsS", compose_text)
        self.assertIn("curl --connect-timeout 5 --max-time 30 -fsS -X POST", compose_text)
        self.assertNotIn("apicurio-registry:8080/health/ready", compose_text)
        self.assertIn("post_artifact platform dlq.events /bootstrap/dlq.events.json", compose_text)
        self.assertIn(
            "post_artifact governance governance.data.products "
            "/bootstrap/governance.data.products.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact governance governance.intermediation.log "
            "/bootstrap/governance.intermediation.log.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact governance governance.research.projects "
            "/bootstrap/governance.research.projects.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact governance governance.dataset.catalog "
            "/bootstrap/governance.dataset.catalog.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact governance governance.data_management_plans "
            "/bootstrap/governance.data_management_plans.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact governance governance.repository.exports "
            "/bootstrap/governance.repository.exports.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact dataact dataact.product.catalog /bootstrap/dataact.product.catalog.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact dataact dataact.third_party.sharing "
            "/bootstrap/dataact.third_party.sharing.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact dataact dataact.legal_basis.checks "
            "/bootstrap/dataact.legal_basis.checks.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact security security.incident.events "
            "/bootstrap/security.incident.events.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact security security.sbom.attestations "
            "/bootstrap/security.sbom.attestations.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact resilience resilience.operational.risk "
            "/bootstrap/resilience.operational.risk.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact compliance compliance.scope.decisions "
            "/bootstrap/compliance.scope.decisions.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact compliance compliance.reporting.channels "
            "/bootstrap/compliance.reporting.channels.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact compliance compliance.legal.dossier "
            "/bootstrap/compliance.legal.dossier.json",
            compose_text,
        )
        self.assertIn(
            "post_artifact cra cra.product.lifecycle /bootstrap/cra.product.lifecycle.json",
            compose_text,
        )

    def test_local_secrets_are_excluded_from_git_and_docker_contexts(self) -> None:
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        dockerignore = (REPO_ROOT / ".dockerignore").read_text(encoding="utf-8")

        for ignored_path in [".env", ".env.*", ".idea/", ".mypy_cache/", "secrets/*"]:
            self.assertIn(ignored_path, gitignore)

        self.assertIn("!secrets/.gitkeep", gitignore)

        for ignored_path in [".env", ".env.*", ".idea", ".mypy_cache", "secrets/"]:
            self.assertIn(ignored_path, dockerignore)

        tracked_sensitive_paths = subprocess.run(
            ["git", "ls-files", ".env", ".env.*", ".idea", "secrets"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        allowed_sensitive_paths = {".env.example", "secrets/.gitkeep"}

        for path in tracked_sensitive_paths:
            self.assertIn(path, allowed_sensitive_paths)

    def test_compose_does_not_define_sensitive_password_fallbacks(self) -> None:
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        forbidden_fragments = [
            "change-this-password",
            "change-this-cookie",
            "AIRFLOW_ADMIN_PASSWORD:-",
            "AIRFLOW_DB_PASSWORD:-",
            "GRAFANA_ADMIN_PASSWORD:-",
            "VERNEMQ_ADMIN_PASSWORD:-",
        ]

        for fragment in forbidden_fragments:
            self.assertNotIn(fragment, compose_text)

    def test_base_compose_does_not_publish_host_ports(self) -> None:
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")

        self.assertNotIn("\n    ports:\n", compose_text)

    def test_compose_and_patroni_avoid_broad_privilege_hotspots(self) -> None:
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        patroni_templates = sorted((REPO_ROOT / "patroni").glob("pg*.yml.tmpl"))

        self.assertNotIn("privileged: true", compose_text)
        self.assertIn("no-new-privileges:true", compose_text)
        for template_path in patroni_templates:
            template_text = template_path.read_text(encoding="utf-8")
            self.assertNotIn("0.0.0.0/0", template_text)
            self.assertIn("samenet scram-sha-256", template_text)

    def test_dev_overlay_contains_local_ports_and_prod_exposes_only_edge(self) -> None:
        dev_text = (REPO_ROOT / "docker-compose.dev.yml").read_text(encoding="utf-8")
        prod_text = (REPO_ROOT / "docker-compose.prod.yml").read_text(encoding="utf-8")

        for port in [
            '"8088:8080"',
            '"19092:19092"',
            '"3000:3000"',
            '"1883:1883"',
            '"8090:8080"',
        ]:
            self.assertIn(port, dev_text)

        self.assertIn('"80:80"', prod_text)
        self.assertIn('"443:443"', prod_text)
        self.assertNotIn('"8088:8080"', prod_text)
        self.assertNotIn('"8090:8080"', prod_text)
        self.assertNotIn('"19092:19092"', prod_text)

    def test_e2e_smoke_script_checks_runtime_contracts(self) -> None:
        script_text = (REPO_ROOT / "scripts" / "smoke-e2e.sh").read_text(encoding="utf-8")
        flink_job_text = (REPO_ROOT / "flink" / "jobs" / "streaming_minimal.py").read_text(
            encoding="utf-8"
        )

        for expected in [
            "raw.sensor",
            "dlq.events",
            "features.events",
            "state.latest",
            "smoke_run_id=",
            "FLINK_CONSUMER_GROUP",
            "Core event-flow services failed to become ready.",
            "SMOKE_COMPOSE_OUTPUT_TAIL",
            "wait_for_core_event_flow_services",
            "compose_service_running",
            'compose ps -a -q "$service"',
            "wait_for_compose_service kafka-init completed",
            "wait_for_compose_service seaweedfs-init completed",
            "wait_for_compose_service flink-jobmanager healthy",
            "SMOKE_COMPOSE_READY_POLL_SECONDS",
            "SMOKE_COMPOSE_READY_ATTEMPTS",
            "wait_for_flink_job_running",
            "wait_for_flink_taskmanagers",
            "dump_smoke_diagnostics",
            "flink-cli sh /opt/flink/usrlib/run-streaming-minimal.sh",
            "SMOKE_FLINK_EXPECTED_TASKMANAGERS",
            "SMOKE_FLINK_TASKMANAGER_WAIT_ATTEMPTS",
            "SMOKE_FLINK_REST_HOST",
            "SMOKE_FLINK_SUBMIT_OUTPUT_TAIL",
            "SMOKE_DIAGNOSTIC_LOG_TAIL",
            "SMOKE_KAFKA_DIAGNOSTIC_TOPICS",
            "emit_smoke_error",
            "::error title=E2E smoke",
            "GITHUB_STEP_SUMMARY",
            "http.client.HTTPConnection",
            "apicurio-registry:8080",
            "check_apicurio_artifact",
            "apicurio-registry apicurio-init kafka1 kafka2 kafka3",
            "dump_kafka_topic_state",
            "dump_flink_job_diagnostics",
            "dump_flink_rest_path",
            "/jobs/${flink_job_id}/exceptions",
            "/jobs/${flink_job_id}/checkpoints",
            "kafka-get-offsets.sh",
            "groups/${group}/artifacts/${artifact}",
            "require_command timeout",
            "compose_with_timeout",
            "SMOKE_FLINK_SUBMIT_TIMEOUT_SECONDS",
            "Flink job submission failed or timed out with status ${submit_status}",
            "Flink submit output (last ${SMOKE_FLINK_SUBMIT_OUTPUT_TAIL} lines)",
            "SMOKE_MQTT_PUBLISH_TIMEOUT_SECONDS",
            "wait_for_publish(timeout=publish_timeout)",
            "grep -F -m 1",
            "cancel --jobmanager flink-jobmanager:8081",
            '--tail="$SMOKE_DIAGNOSTIC_LOG_TAIL"',
            "mktemp",
            "Docker compose up output (last ${SMOKE_COMPOSE_OUTPUT_TAIL} lines)",
            "Flink JobManager is not running; skipping Flink job list",
            "Kafka service kafka1 is not running; skipping topic state",
            "run --no-deps --rm --entrypoint",
        ]:
            self.assertIn(expected, script_text)
        self.assertIn(" up -d --build \\", script_text)
        self.assertNotIn("--quiet-pull", script_text)
        self.assertNotIn("--quiet-build", script_text)
        self.assertNotIn(" --wait \\", script_text)
        self.assertNotIn("e2e-sensor-001", script_text)
        self.assertNotIn("e2e-camera-001", script_text)
        self.assertNotIn("http://flink-jobmanager", script_text)
        self.assertIn(
            "from pyflink.datastream.connectors.base import DeliveryGuarantee",
            flink_job_text,
        )

    def test_wildfi_ingestion_is_configured(self) -> None:
        bridge_source = (REPO_ROOT / "mqtt-kafka-bridge" / "bridge.py").read_text(encoding="utf-8")
        compose_text = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        runbook_text = (REPO_ROOT / "docs" / "runbooks" / "wildfi-ingestion.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("$share/ingestors/wildfi/#", compose_text)
        self.assertIn("WILDFI_TOPIC_PREFIXES", bridge_source)
        self.assertIn("WildFiDecoder", runbook_text)
        self.assertIn("WildFiOpenSource", runbook_text)
        self.assertIn("raw.gps", runbook_text)
        self.assertIn("raw.sensor", runbook_text)

    def test_wildfi_decoder_image_is_pinned_and_wrapped_for_batch_decoding(self) -> None:
        dockerfile = (REPO_ROOT / "wildfi-decoder" / "Dockerfile").read_text(encoding="utf-8")
        wrapper = (REPO_ROOT / "wildfi-decoder" / "run-wildfi-decoder.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("https://github.com/wildlab/WildFiDecoder.git", dockerfile)
        self.assertIn("b4002eb9a6111de140b95e5a35c3f3bd552d51be", dockerfile)
        self.assertIn('test "$(git rev-parse HEAD)" = "${WILDFI_DECODER_GIT_REF}"', dockerfile)
        self.assertIn("WildFiDecoderStandalone.jar", dockerfile)
        self.assertIn("WILDFI_DECODER_RAW_INPUT", wrapper)
        self.assertIn("WILDFI_DECODER_MODE", wrapper)
        self.assertIn("env -u JAVA_TOOL_OPTIONS -u JDK_JAVA_OPTIONS", wrapper)

    def test_ci_assets_do_not_contain_static_placeholder_secrets(self) -> None:
        scanned_paths = [
            *sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml")),
            REPO_ROOT / ".env.example",
            REPO_ROOT / "deploy" / "kubernetes" / "overlays" / "ci-smoke" / "kustomization.yaml",
        ]
        forbidden_fragments = [
            "change-me",
            "replace-with",
            "replace-me",
            "ci-api-secret",
            "ci-jwt-secret",
            "ci-access-key",
            "ci-fernet-key",
            "ci-mqtt-password",
            "ci-secret-key",
            "ci-airflow-admin-password",
            "ci-airflow-db-password",
            "ci-vernemq-admin-password",
            "ci-grafana-admin-password",
        ]

        for path in scanned_paths:
            text = path.read_text(encoding="utf-8")
            for fragment in forbidden_fragments:
                self.assertNotIn(fragment, text, f"{path} contains {fragment}")

    def test_coverage_threshold_is_at_least_90_percent(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "sonarqube.yml").read_text(
            encoding="utf-8"
        )
        pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn("--cov-fail-under=90", workflow)
        self.assertIn("fail_under = 90", pyproject)

    def test_management_console_frontend_avoids_unsafe_dom_sinks(self) -> None:
        app_js = (REPO_ROOT / "management-console" / "static" / "app.js").read_text(
            encoding="utf-8"
        )

        for forbidden in ["innerHTML", "outerHTML", "document.write"]:
            self.assertNotIn(forbidden, app_js)
        self.assertIn('fetch("/api/architecture"', app_js)
        self.assertIn('fetch("/api/health"', app_js)
        self.assertNotIn("fetch(endpoint", app_js)

    def test_public_website_presents_deal_suite(self) -> None:
        index_html = (REPO_ROOT / "website" / "index.html").read_text(encoding="utf-8")
        french_html = (REPO_ROOT / "website" / "fr" / "index.html").read_text(encoding="utf-8")
        translations = json.loads(
            (REPO_ROOT / "website" / "src" / "i18n-copy.json").read_text(encoding="utf-8")
        )
        styles_css = (REPO_ROOT / "website" / "styles.css").read_text(encoding="utf-8")
        source_styles_css = (REPO_ROOT / "website" / "src" / "styles.css").read_text(
            encoding="utf-8"
        )
        app_js = (REPO_ROOT / "website" / "app.js").read_text(encoding="utf-8")
        workflow = (REPO_ROOT / ".github" / "workflows" / "website-pages.yml").read_text(
            encoding="utf-8"
        )
        compact_styles_css = re.sub(r"\s+", "", styles_css)
        index_without_noscript = re.sub(
            r"<noscript>.*?</noscript>",
            "",
            index_html,
            flags=re.DOTALL,
        )

        for product_name in ("DEALIoT", "DEALHost", "DEALData"):
            self.assertIn(product_name, index_html)
            self.assertIn(product_name, french_html)

        self.assertIn('<html lang="en-US">', index_html)
        self.assertIn('<html lang="fr">', french_html)
        self.assertIn('href="https://smartappli.io/fr/"', index_html)
        self.assertIn('href="https://smartappli.io/"', french_html)
        self.assertIn("Operate field data like a production system.", index_html)
        self.assertIn(translations["fr"]["h1"], french_html)
        self.assertIn("Star on GitHub", index_html)
        self.assertIn("language-select", index_html)
        self.assertIn("data-language-select", index_html)
        self.assertIn("navigateToSelectedLanguage", app_js)
        self.assertIn("DOMContentLoaded", app_js)
        self.assertIn("app.js?v=20260607-render-blocking-v1", index_html)
        self.assertIn("styles.css?v=20260607-render-blocking-v1", index_html)
        self.assertIn('<link rel="preload"', index_html)
        self.assertIn('as="style"', index_html)
        self.assertIn('as="script"', index_html)
        self.assertIn("data-critical-css", index_html)
        self.assertIn("data-deferred-stylesheet", index_html)
        self.assertIn('fetchpriority="high"', index_html)
        self.assertIn('media="print"', index_html)
        self.assertNotIn("onload=", index_html)
        self.assertIn("<noscript>", index_html)
        self.assertNotIn(
            '<link rel="stylesheet" href="styles.css?v=20260607-render-blocking-v1">',
            index_without_noscript,
        )
        self.assertIn("deferredStylesheets", app_js)
        self.assertIn('stylesheet.media = "all"', app_js)
        self.assertIn("https://github.com/Smartappli/DEALIoT", index_html)
        self.assertIn("mailto:contact@smartappli.com", index_html)
        self.assertIn("actions/upload-pages-artifact@", workflow)
        self.assertIn("actions/deploy-pages@", workflow)
        self.assertIn("Prepare website artifact", workflow)
        self.assertIn("--exclude='./node_modules'", workflow)
        self.assertIn("--exclude='./src'", workflow)
        self.assertIn("path: website-dist", workflow)
        self.assertIn('href="https://smartappli.io/"', index_html)
        self.assertIn('property="og:title"', index_html)
        self.assertIn('name="twitter:card"', index_html)
        self.assertIn('type="application/ld+json"', index_html)
        self.assertIn("What is DEALIoT?", index_html)
        self.assertIn(translations["fr"]["q_dealiot"], french_html)
        self.assertIn("@media(max-width:1120px)", compact_styles_css)
        self.assertIn("@media(max-width:720px)", compact_styles_css)
        self.assertIn(
            "grid-template-columns:minmax(10rem,auto)minmax(18rem,1fr)max-content",
            compact_styles_css,
        )
        self.assertIn("overflow-x:auto", compact_styles_css)
        self.assertIn("white-space:nowrap", compact_styles_css)
        self.assertIn("min-width:max-content", compact_styles_css)
        self.assertIn("Bricolage Grotesque", styles_css)
        self.assertIn("Instrument Serif", styles_css)
        self.assertIn("JetBrains Mono", styles_css)

        for forbidden_fragment in ("innerHTML", "outerHTML", "document.write", "eval("):
            self.assertNotIn(forbidden_fragment, app_js)
        for forbidden_font in ("Inter", "Roboto", "Arial", "system-ui"):
            self.assertNotIn(forbidden_font, source_styles_css)

    def test_public_website_has_seo_and_geo_assets(self) -> None:
        index_html = (REPO_ROOT / "website" / "index.html").read_text(encoding="utf-8")
        french_html = (REPO_ROOT / "website" / "fr" / "index.html").read_text(encoding="utf-8")
        robots = (REPO_ROOT / "website" / "robots.txt").read_text(encoding="utf-8")
        sitemap = (REPO_ROOT / "website" / "sitemap.xml").read_text(encoding="utf-8")
        llms = (REPO_ROOT / "website" / "llms.txt").read_text(encoding="utf-8")
        htaccess = (REPO_ROOT / "website" / ".htaccess").read_text(encoding="utf-8")
        languages = json.loads(
            (REPO_ROOT / "website" / "eu-languages.json").read_text(encoding="utf-8")
        )
        manifest = json.loads(
            (REPO_ROOT / "website" / "site.webmanifest").read_text(encoding="utf-8")
        )

        base_url = "https://smartappli.io/"

        def localized_url(language: dict[str, str]) -> str:
            language_path = language["path"].strip("/")
            return f"{base_url}{language_path + '/' if language_path else ''}"

        canonical_url = base_url
        french_url = f"{base_url}fr/"
        expected_urls = [localized_url(language) for language in languages]

        self.assertIn(f'<link rel="canonical" href="{canonical_url}">', index_html)
        self.assertIn(f'<link rel="canonical" href="{french_url}">', french_html)
        self.assertIn('hreflang="fr"', index_html)
        self.assertIn(f'href="{french_url}"', index_html)
        self.assertIn('hreflang="en-US"', french_html)
        self.assertIn(f'href="{canonical_url}"', french_html)
        self.assertIn(f'<meta property="og:url" content="{canonical_url}">', index_html)
        self.assertIn('content="https://smartappli.io/assets/social-card.png"', index_html)
        self.assertIn('<meta property="og:image:width" content="1200">', index_html)
        self.assertIn('<meta property="og:image:height" content="630">', index_html)
        self.assertIn("Sitemap: https://smartappli.io/sitemap.xml", robots)
        self.assertIn("Allow: /assets/", robots)
        self.assertIn("Disallow: /src/", robots)
        self.assertIn("Disallow: /package.json", robots)
        self.assertIn("Options -Indexes", htaccess)
        self.assertIn("max-age=31536000, immutable", htaccess)
        self.assertIn("no-cache, must-revalidate", htaccess)
        self.assertIn("BROTLI_COMPRESS", htaccess)
        self.assertIn("DEFLATE", htaccess)
        self.assertIn("X-Content-Type-Options", htaccess)

        sitemap_urls = re.findall(r"<loc>(.*?)</loc>", sitemap)
        self.assertEqual(expected_urls, sitemap_urls)
        for language in languages:
            self.assertIn(f'hreflang="{language["hreflang"]}"', sitemap)
            self.assertIn(f'href="{localized_url(language)}"', sitemap)
        self.assertIn('hreflang="x-default" href="https://smartappli.io/"', sitemap)

        self.assertEqual("/", manifest["id"])
        self.assertEqual("/", manifest["start_url"])
        self.assertEqual("/", manifest["scope"])
        self.assertEqual("en-US", manifest["lang"])
        self.assertEqual("#0196d0", manifest["theme_color"])
        self.assertEqual("standalone", manifest["display"])
        self.assertIn("assets/icon-192.png", manifest["icons"][0]["src"])
        self.assertIn("assets/icon-512.png", manifest["icons"][1]["src"])
        self.assertEqual("maskable", manifest["icons"][2]["purpose"])

        json_ld_match = re.search(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            index_html,
            flags=re.DOTALL,
        )
        if json_ld_match is None:
            self.fail("Missing JSON-LD script")
        json_ld = json.loads(json_ld_match.group(1))
        graph = json_ld["@graph"]
        graph_types = {node["@type"] for node in graph}
        graph_names = {node.get("name") for node in graph}

        for expected_type in ("Organization", "WebSite", "SoftwareApplication", "FAQPage"):
            self.assertIn(expected_type, graph_types)
        for expected_name in ("DEALIoT", "DEALHost", "DEALData", "DEAL suite"):
            self.assertIn(expected_name, graph_names)

        faq_node = next(node for node in graph if node["@type"] == "FAQPage")
        self.assertGreaterEqual(len(faq_node["mainEntity"]), 3)

        for fragment in (
            "What is DEALIoT?",
            "What is DEALHost?",
            "What is DEALData?",
            "Default language: English US",
            "PWA status: installable",
            "ranking signal",
            "https://github.com/Smartappli/DEALIoT",
            "All 24 official EU language routes",
        ):
            self.assertIn(fragment, llms)

    def test_public_website_supports_all_official_eu_languages(self) -> None:
        languages = json.loads(
            (REPO_ROOT / "website" / "eu-languages.json").read_text(encoding="utf-8")
        )
        translations = json.loads(
            (REPO_ROOT / "website" / "src" / "i18n-copy.json").read_text(encoding="utf-8")
        )
        expected_hreflangs = {
            "en-US",
            "bg",
            "hr",
            "cs",
            "da",
            "nl",
            "et",
            "fi",
            "fr",
            "de",
            "el",
            "hu",
            "ga",
            "it",
            "lv",
            "lt",
            "mt",
            "pl",
            "pt",
            "ro",
            "sk",
            "sl",
            "es",
            "sv",
        }
        self.assertEqual(expected_hreflangs, {language["hreflang"] for language in languages})
        self.assertEqual(24, len(languages))
        self.assertEqual(expected_hreflangs - {"en-US"}, set(translations))

        names = {language["hreflang"]: language["name"] for language in languages}
        self.assertEqual("\u010ce\u0161tina", names["cs"])
        self.assertEqual("\u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac", names["el"])
        self.assertEqual("Fran\u00e7ais", names["fr"])

        flag_regions = {
            "en-US": "US",
            "bg": "BG",
            "hr": "HR",
            "cs": "CZ",
            "da": "DK",
            "nl": "NL",
            "et": "EE",
            "fi": "FI",
            "fr": "FR",
            "de": "DE",
            "el": "GR",
            "hu": "HU",
            "ga": "IE",
            "it": "IT",
            "lv": "LV",
            "lt": "LT",
            "mt": "MT",
            "pl": "PL",
            "pt": "PT",
            "ro": "RO",
            "sk": "SK",
            "sl": "SI",
            "es": "ES",
            "sv": "SE",
        }

        def flag_for(region: str) -> str:
            return "".join(chr(0x1F1E6 + ord(letter) - ord("A")) for letter in region)

        for language in languages:
            language_path = language["path"].strip("/")
            page_path = (
                REPO_ROOT / "website" / "index.html"
                if not language_path
                else REPO_ROOT / "website" / language_path / "index.html"
            )
            html = page_path.read_text(encoding="utf-8")
            localized_url = f"https://smartappli.io/{language_path + '/' if language_path else ''}"
            expected_flag = flag_for(flag_regions[language["hreflang"]])
            self.assertEqual(expected_flag, language["flag"])
            self.assertIn(f'<html lang="{language["hreflang"]}">', html)
            self.assertIn(f'<link rel="canonical" href="{localized_url}">', html)
            self.assertEqual(25, html.count('rel="alternate"'))
            self.assertIn("styles.css?v=20260607-render-blocking-v1", html)
            self.assertIn("app.js?v=20260607-render-blocking-v1", html)
            self.assertIn('<link rel="preload"', html)
            self.assertIn("data-critical-css", html)
            self.assertIn("data-deferred-stylesheet", html)
            self.assertIn('media="print"', html)
            self.assertIn("language-menu", html)
            self.assertIn("language-select", html)
            self.assertIn("data-language-select", html)
            self.assertNotIn("language-panel", html)
            self.assertNotIn("<details", html)
            self.assertIn(
                f'<option value="{localized_url}" lang="{language["hreflang"]}" selected>'
                f"{expected_flag} {language['name']}</option>",
                html,
            )
            self.assertNotIn("????", html)

            if language["hreflang"] == "en-US":
                self.assertIn("Star on GitHub", html)
                continue

            localized_copy = translations[language["hreflang"]]
            for key in (
                "choose_language",
                "star",
                "request_demo",
                "h1",
                "products_eyebrow",
                "adoption_path",
                "q_dealiot",
                "use_case_catalog",
                "champion_decision_kit",
                "open_decision_kit",
                "contributor_community",
                "start_contributing",
                "llms_context",
            ):
                self.assertIn(localized_copy[key], html)

            for english_fragment in (
                "Star on GitHub",
                "Request a demo",
                "Choose language",
                "One suite, three adoption paths",
                "A public path to evaluate without friction.",
                "Short answers for fast evaluation.",
                "What is DEALIoT?",
                "Explore the suite",
                "See the platform",
                "DEAL ecosystem",
                "LLMS context",
                "Contributor community",
                "Start contributing",
            ):
                self.assertNotIn(english_fragment, html)

    def test_public_website_is_installable_pwa(self) -> None:
        app_js = (REPO_ROOT / "website" / "app.js").read_text(encoding="utf-8")
        service_worker = (REPO_ROOT / "website" / "sw.js").read_text(encoding="utf-8")
        offline_html = (REPO_ROOT / "website" / "offline.html").read_text(encoding="utf-8")
        index_html = (REPO_ROOT / "website" / "index.html").read_text(encoding="utf-8")
        french_html = (REPO_ROOT / "website" / "fr" / "index.html").read_text(encoding="utf-8")
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn('rel="manifest"', index_html)
        self.assertIn('rel="apple-touch-icon"', index_html)
        self.assertIn("navigator.serviceWorker.register", app_js)
        self.assertIn('return "/";', app_js)
        self.assertIn("CACHE_NAME", service_worker)
        self.assertIn('const CACHE_NAME = "dealiot-pwa-v6"', service_worker)
        self.assertIn('const ASSET_VERSION = "20260607-render-blocking-v1"', service_worker)
        self.assertIn("isNetworkFirstAsset", service_worker)
        self.assertIn("staleWhileRevalidate", service_worker)
        self.assertIn("networkFirst", service_worker)
        self.assertIn("`./app.js?v=${ASSET_VERSION}`", service_worker)
        self.assertIn('requestUrl.pathname.endsWith("/sw.js")', service_worker)
        self.assertIn('"./fr/"', service_worker)
        self.assertIn('"./de/"', service_worker)
        self.assertIn('"./es/"', service_worker)
        self.assertIn('"./offline.html"', service_worker)
        self.assertIn('request.mode === "navigate"', service_worker)
        self.assertIn("The DEAL site is available offline.", offline_html)
        self.assertIn('<link rel="manifest" href="../site.webmanifest">', french_html)
        self.assertIn("website/", gitignore)

    def test_repository_has_adoption_assets(self) -> None:
        adoption_playbook = (REPO_ROOT / "docs" / "community" / "adoption-playbook.md").read_text(
            encoding="utf-8"
        )
        popularity_playbook = (
            REPO_ROOT / "docs" / "community" / "architecture-popularity-playbook.md"
        ).read_text(encoding="utf-8")
        star_growth_plan = (
            REPO_ROOT / "docs" / "community" / "github-star-growth-plan.md"
        ).read_text(encoding="utf-8")
        use_case_catalog = (REPO_ROOT / "docs" / "community" / "use-case-catalog.md").read_text(
            encoding="utf-8"
        )
        quick_evaluation_path = (
            REPO_ROOT / "docs" / "community" / "quick-evaluation-path.md"
        ).read_text(encoding="utf-8")
        comparison_guide = (
            REPO_ROOT / "docs" / "community" / "architecture-comparison-guide.md"
        ).read_text(encoding="utf-8")
        champion_kit = (REPO_ROOT / "docs" / "community" / "internal-champion-kit.md").read_text(
            encoding="utf-8"
        )
        public_launch_kit = (REPO_ROOT / "docs" / "community" / "public-launch-kit.md").read_text(
            encoding="utf-8"
        )
        first_github_discussion = (
            REPO_ROOT / "docs" / "community" / "first-github-discussion.md"
        ).read_text(encoding="utf-8")
        adoption_funnel = (REPO_ROOT / "docs" / "community" / "adoption-funnel.md").read_text(
            encoding="utf-8"
        )
        demo_playbook = (REPO_ROOT / "docs" / "community" / "demo-pilot-playbook.md").read_text(
            encoding="utf-8"
        )
        community_launch_plan = (
            REPO_ROOT / "docs" / "community" / "user-community-launch-plan.md"
        ).read_text(encoding="utf-8")
        user_onboarding_guide = (
            REPO_ROOT / "docs" / "community" / "user-onboarding-guide.md"
        ).read_text(encoding="utf-8")
        developer_community_playbook = (
            REPO_ROOT / "docs" / "community" / "developer-community-playbook.md"
        ).read_text(encoding="utf-8")
        contributor_onboarding = (
            REPO_ROOT / "docs" / "community" / "contributor-onboarding.md"
        ).read_text(encoding="utf-8")
        community_governance = (
            REPO_ROOT / "docs" / "community" / "community-governance.md"
        ).read_text(encoding="utf-8")
        community_rituals = (REPO_ROOT / "docs" / "community" / "community-rituals.md").read_text(
            encoding="utf-8"
        )
        user_feedback_loop = (REPO_ROOT / "docs" / "community" / "user-feedback-loop.md").read_text(
            encoding="utf-8"
        )
        seed_discussions = (REPO_ROOT / "docs" / "community" / "seed-discussions.md").read_text(
            encoding="utf-8"
        )
        partner_guide = (
            REPO_ROOT / "docs" / "community" / "integration-partner-guide.md"
        ).read_text(encoding="utf-8")
        validation_scorecard = (
            REPO_ROOT / "docs" / "community" / "validation-scorecard.md"
        ).read_text(encoding="utf-8")
        adopter_story_template = (
            REPO_ROOT / "docs" / "community" / "adopter-story-template.md"
        ).read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        website = (REPO_ROOT / "website" / "index.html").read_text(encoding="utf-8")
        llms_txt = (REPO_ROOT / "website" / "llms.txt").read_text(encoding="utf-8")
        issue_templates = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (REPO_ROOT / ".github" / "ISSUE_TEMPLATE").glob("*.yml")
        )
        discussion_templates = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (REPO_ROOT / ".github" / "DISCUSSION_TEMPLATE").glob("*.yml")
        )
        labels = (REPO_ROOT / ".github" / "labels.yml").read_text(encoding="utf-8")
        codeowners = (REPO_ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
        contributing = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        pull_request_template = (REPO_ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(
            encoding="utf-8"
        )

        for fragment in (
            "Primary Audiences",
            "Adoption Ladder",
            "30-Day Pilot Motion",
            "Success Metrics",
        ):
            self.assertIn(fragment, adoption_playbook)

        for fragment in (
            "Adoption Thesis",
            "Adoption Flywheel",
            "Distribution Plan",
            "Launch Metrics",
        ):
            self.assertIn(fragment, popularity_playbook)

        for fragment in (
            "Star Conversion Assets",
            "7-Day Launch Motion",
            "Distribution Channels",
            "Do Not Do",
        ):
            self.assertIn(fragment, star_growth_plan)

        for fragment in ("Use Cases", "Priority Matrix", "Public Proof Assets"):
            self.assertIn(fragment, use_case_catalog)

        for fragment in ("10-Minute Fit Check", "60-Minute Technical Check", "30-Day Decision"):
            self.assertIn(fragment, quick_evaluation_path)

        for fragment in ("Comparison Matrix", "Anti-Fit Signals", "Adoption Recommendation"):
            self.assertIn(fragment, comparison_guide)

        for fragment in ("5-Minute Sponsor Brief", "Stakeholder Map", "Objection Handling"):
            self.assertIn(fragment, champion_kit)

        for fragment in ("Launch Post", "Partner Outreach Email", "Conference Or Meetup Abstract"):
            self.assertIn(fragment, public_launch_kit)

        self.assertIn("First GitHub Discussion", public_launch_kit)
        self.assertIn("Show DEALIoT", public_launch_kit)

        for fragment in (
            "Title",
            "Body",
            "Show DEALIoT",
            "If this looks useful, star the repository",
        ):
            self.assertIn(fragment, first_github_discussion)

        for fragment in ("Funnel Stages", "Conversion Assets", "Minimum Viable Popularity"):
            self.assertIn(fragment, adoption_funnel)

        for fragment in ("Pilot Scorecard", "Local Demo Script", "Post-Pilot Decision"):
            self.assertIn(fragment, demo_playbook)

        for fragment in (
            "Community Promise",
            "30-Day Launch Motion",
            "Launch Checklist",
            "GitHub Discussions",
        ):
            self.assertIn(fragment, community_launch_plan)

        for fragment in ("First 60 Minutes", "Community Entry Points", "Good Question Template"):
            self.assertIn(fragment, user_onboarding_guide)

        for fragment in ("Contributor Tracks", "Contribution Ladder", "Good First Issue Criteria"):
            self.assertIn(fragment, developer_community_playbook)

        for fragment in ("First Contribution Paths", "Validation Shortcuts", "Asking For Help"):
            self.assertIn(fragment, contributor_onboarding)

        for fragment in ("Principles", "Roles", "Decision Process", "Recognition"):
            self.assertIn(fragment, community_governance)

        for fragment in ("Weekly Triage", "Office Hours Agenda", "Discussion Moderation Rules"):
            self.assertIn(fragment, community_rituals)

        for fragment in ("Triage Flow", "Prioritization Score", "Feedback Closure"):
            self.assertIn(fragment, user_feedback_loop)

        for fragment in (
            "Launch Discussion",
            "Q&A Seed",
            "Ideas Seed",
            "Show And Tell Seed",
            "Pilot Report Seed",
        ):
            self.assertIn(fragment, seed_discussions)

        for fragment in ("Partner Tracks", "Integration Contract", "Partner Readiness Checklist"):
            self.assertIn(fragment, partner_guide)

        for fragment in (
            "Decision Rule",
            "First event reaches Kafka",
            "Production deployment gaps",
        ):
            self.assertIn(fragment, validation_scorecard)

        for fragment in ("Publication limits", "Outcome", "Remaining gaps"):
            self.assertIn(fragment, adopter_story_template)

        for fragment in (
            "Demo or pilot request",
            "Adopter story",
            "Documentation gap",
            "User feedback",
            "Use case proposal",
        ):
            self.assertIn(fragment, issue_templates)

        for fragment in (
            "Use this for usage questions",
            "Use this for early feature",
            "Use this for approved demos",
            "Use this to share a sanitized 30-day pilot result",
            "Use this when you want to contribute",
            "Use this for launch announcements",
        ):
            self.assertIn(fragment, discussion_templates)

        for fragment in (
            "user-feedback",
            "show-and-tell",
            "pilot",
            "integration",
            "use-case",
            "contributor",
            "good first issue",
            "help wanted",
            "mentored",
            "community",
        ):
            self.assertIn(fragment, labels)

        for fragment in ("@Smartappli", "/docs/community/", "/website/"):
            self.assertIn(fragment, codeowners)

        for fragment in (
            "Contributor onboarding",
            "Developer community playbook",
            "Community governance",
            "good first issue",
        ):
            self.assertIn(fragment, contributing)

        self.assertIn("Operational Impact", pull_request_template)
        self.assertIn("Why Teams Adopt DEALIoT", readme)
        self.assertIn("Fast Adoption Path", readme)
        self.assertIn("Architecture popularity playbook", readme)
        self.assertIn("GitHub star growth plan", readme)
        self.assertIn("Use case catalog", readme)
        self.assertIn("Quick evaluation path", readme)
        self.assertIn("Architecture comparison guide", readme)
        self.assertIn("Internal champion kit", readme)
        self.assertIn("Public launch kit", readme)
        self.assertIn("First GitHub discussion", readme)
        self.assertIn("Adoption funnel", readme)
        self.assertIn("User community launch plan", readme)
        self.assertIn("Developer community playbook", readme)
        self.assertIn("Contributor onboarding", readme)
        self.assertIn("Community governance", readme)
        self.assertIn("Community discussions", readme)
        self.assertIn("Public website", readme)
        self.assertIn("Adoption path", website)
        self.assertIn("docs/community/user-community-launch-plan.md", website)
        self.assertIn("docs/community/demo-pilot-playbook.md", website)
        self.assertIn("docs/community/use-case-catalog.md", website)
        self.assertIn("docs/community/internal-champion-kit.md", website)
        self.assertIn("docs/community/contributor-onboarding.md", website)
        self.assertIn("architecture-popularity-playbook.md", llms_txt)
        self.assertIn("github-star-growth-plan.md", llms_txt)
        self.assertIn("use-case-catalog.md", llms_txt)
        self.assertIn("quick-evaluation-path.md", llms_txt)
        self.assertIn("architecture-comparison-guide.md", llms_txt)
        self.assertIn("internal-champion-kit.md", llms_txt)
        self.assertIn("developer-community-playbook.md", llms_txt)
        self.assertIn("contributor-onboarding.md", llms_txt)
        self.assertIn("community-governance.md", llms_txt)
        self.assertIn("public-launch-kit.md", llms_txt)
        self.assertIn("first-github-discussion.md", llms_txt)
        self.assertIn("adoption-funnel.md", llms_txt)

    def test_management_console_backend_avoids_scanner_hotspots(self) -> None:
        app_py = (REPO_ROOT / "management-console" / "management_console" / "app.py").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("urlopen", app_py)
        self.assertNotIn('os.getenv("MANAGEMENT_CONSOLE_BIND", "0.0.0.0")', app_py)
        self.assertIn('os.getenv("MANAGEMENT_CONSOLE_BIND", "127.0.0.1")', app_py)

    def test_critical_shell_scripts_are_present(self) -> None:
        script_files = [
            REPO_ROOT / "scripts" / "post-bootstrap.sh",
            REPO_ROOT / "scripts" / "start-patroni.sh",
            REPO_ROOT / "scripts" / "start-pgbouncer-rw.sh",
            REPO_ROOT / "scripts" / "start-pgbouncer-ro.sh",
            REPO_ROOT / "scripts" / "smoke-e2e.sh",
        ]

        for script in script_files:
            self.assertTrue(script.is_file(), f"Missing shell script: {script}")

    def test_runtime_python_sources_parse_with_ci_minimum_python(self) -> None:
        runtime_sources = [
            REPO_ROOT / "airflow" / "dags" / "media_backfill.py",
            REPO_ROOT / "dealiot_contracts" / "events.py",
            REPO_ROOT / "flink" / "jobs" / "streaming_minimal.py",
            REPO_ROOT / "management-console" / "management_console" / "app.py",
            REPO_ROOT / "management-console" / "management_console" / "catalog.py",
            REPO_ROOT / "management-console" / "management_console" / "openaire.py",
            REPO_ROOT / "management-console" / "management_console" / "zenodo.py",
            REPO_ROOT / "mqtt-kafka-bridge" / "bridge.py",
            REPO_ROOT / "pipelines" / "media_backfill.py",
        ]

        for source in runtime_sources:
            ast.parse(
                source.read_text(encoding="utf-8"),
                filename=str(source),
                feature_version=(3, 12),
            )


if __name__ == "__main__":
    unittest.main()
