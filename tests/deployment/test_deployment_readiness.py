from __future__ import annotations

import unittest
from pathlib import Path


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
        workflow_text = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("Unit test suite", workflow_text)
        self.assertIn("Integration test suite", workflow_text)
        self.assertIn("Deployment test suite", workflow_text)


if __name__ == "__main__":
    unittest.main()
