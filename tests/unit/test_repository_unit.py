from __future__ import annotations

import json
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
            REPO_ROOT / "scripts" / "smoke-e2e.sh",
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
            REPO_ROOT / ".github" / "workflows" / "e2e-smoke.yml",
            REPO_ROOT / "bandit.yaml",
            REPO_ROOT / "wildfi-decoder" / "Dockerfile",
            REPO_ROOT / "wildfi-decoder" / "run-wildfi-decoder.sh",
            REPO_ROOT / "management-console" / "Dockerfile",
            REPO_ROOT / "management-console" / "management_console" / "app.py",
            REPO_ROOT / "management-console" / "management_console" / "openaire.py",
        ]

        for file_path in required_files:
            self.assertTrue(file_path.is_file(), f"Missing file: {file_path}")

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

        for ignored_path in [".env", "secrets/"]:
            self.assertIn(ignored_path, gitignore)
            self.assertIn(ignored_path, dockerignore)

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


if __name__ == "__main__":
    unittest.main()
