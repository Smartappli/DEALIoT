from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


class DeploymentReadinessTests(unittest.TestCase):
    def test_compose_smoke_workflow_targets_valid_seaweed_services(self) -> None:
        workflow_text = (
            REPO_ROOT / ".github" / "workflows" / "compose-deployment-test.yml"
        ).read_text(encoding="utf-8")
        expected_targets = [
            "seaweedfs-master1",
            "seaweedfs-master2",
            "seaweedfs-master3",
            "seaweedfs-volume1",
            "seaweedfs-volume2",
            "seaweedfs-volume3",
            "seaweedfs-filer",
            "seaweedfs-s3",
        ]
        for target in expected_targets:
            self.assertIn(
                target,
                workflow_text,
                f"Missing deployment target in workflow: {target}",
            )

    def test_compose_smoke_workflow_has_cleanup_and_failure_logs(self) -> None:
        workflow_text = (
            REPO_ROOT / ".github" / "workflows" / "compose-deployment-test.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("Dump compose logs on failure", workflow_text)
        self.assertIn("if: failure()", workflow_text)
        self.assertIn("if: always()", workflow_text)
        self.assertIn(
            "docker compose -f docker-compose.yml down -v --remove-orphans",
            workflow_text,
        )

    def test_ci_workflow_executes_test_layers(self) -> None:
        workflow_text = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("Unit test suite", workflow_text)
        self.assertIn("Integration test suite", workflow_text)
        self.assertIn("Deployment test suite", workflow_text)

    def test_e2e_workflow_runs_smoke_script_and_cleans_up(self) -> None:
        workflow_text = (REPO_ROOT / ".github" / "workflows" / "e2e-smoke.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("bash scripts/smoke-e2e.sh", workflow_text)
        self.assertIn("Dump compose logs on failure", workflow_text)
        self.assertIn(
            "docker compose -f docker-compose.yml -f docker-compose.dev.yml down",
            workflow_text,
        )

    def test_production_deployment_workflow_tests_swarm_and_kubernetes(self) -> None:
        workflow_text = (
            REPO_ROOT / ".github" / "workflows" / "production-deployment-test.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("docker stack config -c deploy/swarm/dealiot-stack.yml", workflow_text)
        self.assertIn("docker stack deploy -c deploy/swarm/dealiot-smoke-stack.yml", workflow_text)
        self.assertIn("kubectl kustomize deploy/kubernetes/base", workflow_text)
        self.assertIn("kind create cluster --name dealiot-ci", workflow_text)
        self.assertIn("kubectl apply -k deploy/kubernetes/overlays/ci-smoke", workflow_text)

    def test_production_deployment_manifests_are_present_and_parseable(self) -> None:
        manifest_paths = [
            REPO_ROOT / "deploy" / "swarm" / "dealiot-stack.yml",
            REPO_ROOT / "deploy" / "swarm" / "dealiot-smoke-stack.yml",
            REPO_ROOT / "deploy" / "kubernetes" / "base" / "kustomization.yaml",
            REPO_ROOT / "deploy" / "kubernetes" / "base" / "mqtt-kafka-bridge.yaml",
            REPO_ROOT / "deploy" / "kubernetes" / "base" / "airflow.yaml",
            REPO_ROOT
            / "deploy"
            / "kubernetes"
            / "overlays"
            / "ci-smoke"
            / "kustomization.yaml",
        ]

        for manifest_path in manifest_paths:
            self.assertTrue(manifest_path.is_file(), f"Missing manifest: {manifest_path}")
            documents = list(yaml.safe_load_all(manifest_path.read_text(encoding="utf-8")))
            self.assertTrue(
                any(document is not None for document in documents),
                f"Empty manifest: {manifest_path}",
            )

    def test_production_images_package_runtime_code(self) -> None:
        orchestration_dockerfile = (REPO_ROOT / "orchestration" / "Dockerfile").read_text(
            encoding="utf-8"
        )
        flink_dockerfile = (REPO_ROOT / "flink" / "Dockerfile.pyflink").read_text(
            encoding="utf-8"
        )
        bridge_source = (REPO_ROOT / "mqtt-kafka-bridge" / "bridge.py").read_text(
            encoding="utf-8"
        )

        self.assertIn("COPY --chown=airflow:0 --chmod=0555 airflow/dags", orchestration_dockerfile)
        self.assertIn("COPY --chown=airflow:0 --chmod=0555 pipelines", orchestration_dockerfile)
        self.assertIn("COPY --chown=flink:flink --chmod=0555 ./flink/jobs", flink_dockerfile)
        self.assertIn("COPY --chown=flink:flink --chmod=0555 ./pipelines", flink_dockerfile)
        self.assertIn("def env_or_secret_file", bridge_source)


if __name__ == "__main__":
    unittest.main()
