# Contributing To DEALIoT

DEALIoT welcomes practical contributions that make the platform easier to run, verify, extend, and adopt.

## Good First Contributions

- Improve the local demo path and smoke-test diagnostics.
- Add device fixtures or schema examples with tests.
- Improve runbooks, deployment notes, or documentation gaps.
- Add dashboards, alerts, or pilot scorecard evidence.
- Harden CI checks without making local development brittle.

## Contribution Rules

- Keep production behavior testable.
- Do not commit secrets, tokens, customer data, or private endpoint values.
- Do not add mutable production image tags.
- Add or update tests for behavior changes.
- Document operational impact when touching deployment, security, or compliance files.
- Keep vendor-specific integrations optional and clearly scoped.

## Local Validation

Run the relevant gates before opening a pull request:

```bash
uv run python -m unittest discover -s tests/unit -p "test_*.py" -v
uv run python -m unittest -v tests/test_application_smoke.py
uv run --with PyYAML python -m unittest -v tests/deployment/test_deployment_readiness.py
uvx pre-commit run --all-files --show-diff-on-failure
```

For end-to-end runtime changes, also run:

```bash
bash scripts/smoke-e2e.sh
```

## Pull Request Expectations

A pull request should explain:

- The problem being solved.
- The runtime or adoption impact.
- The tests and manual checks performed.
- Any production configuration, secret, migration, or rollback consideration.

## Documentation Expectations

If a change affects users, operators, partners, or compliance evidence, update at least one of:

- `README.md`
- `docs/wiki/`
- `docs/runbooks/`
- `docs/community/`
- `deploy/kubernetes/overlays/production/README.md`
- `deploy/swarm/README.md`
