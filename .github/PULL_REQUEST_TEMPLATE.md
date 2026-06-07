## Summary

Describe the change and the problem it solves.

## Type Of Change

- [ ] Runtime behavior
- [ ] Deployment or operations
- [ ] Documentation
- [ ] Security or compliance
- [ ] Community or adoption
- [ ] Test-only change

## Validation

List commands run and important manual checks.

```bash
# example
uv run python -m unittest discover -s tests/unit -p "test_*.py" -v
```

## Operational Impact

Explain any change to secrets, deployment targets, data contracts, migrations, SLOs, rollback, or support expectations.

## Checklist

- [ ] Tests or documentation updated where needed
- [ ] No secrets, private endpoints, or customer data committed
- [ ] Production image tags remain immutable where applicable
- [ ] README, runbook, wiki, or community docs updated when user-facing behavior changed
