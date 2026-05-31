# Data Governance Act Runbook

This runbook translates the Data Governance Act into controls for DEALIoT operations. It is a
technical control baseline, not a legal determination that DEALIoT is or is not a regulated data
intermediation service.

## Scope Decision

Before enabling external data sharing, record whether DEALIoT is acting as:

- an internal data platform only,
- a data holder exposing product or operational data,
- a data intermediation service between data holders/data subjects and data users,
- a recognised data altruism organisation.

If the deployment offers data intermediation services in the EU, complete the notification process
with the competent authority before operating that service and keep the notification evidence
outside the repository.

## DGA Architecture Controls

DEALIoT uses a dedicated governance plane for DGA evidence:

| Topic | Evidence |
|---|---|
| `governance.data.products` | data product catalogue, purpose, category, format and access mode |
| `governance.access.requests` | fair, transparent and non-discriminatory request decisions |
| `governance.permission.events` | data holder permissions, data subject consent and withdrawals |
| `governance.intermediation.log` | data intermediation activity log |
| `governance.transfer.notices` | unauthorised access, transfer or use notifications |

These topics must not contain raw telemetry or media. Store only the minimum metadata required to
prove governance decisions and operate the intermediation service.

## Operating Rules

- Do not use mediated data for the platform operator's own purposes.
- Keep data product access mediated through documented access requests.
- Publish clear allowed purposes, prohibited purposes, formats, retention and third-country rules.
- Share data in the received format by default; only convert data for interoperability, legal
  requirements, or explicit request/approval.
- Record consent or permission before making personal or non-personal data available to a data user.
- Provide a withdrawal path and log the withdrawal event.
- Keep an activity log for each catalogue view, access request, permission check, data share,
  retrieval, conversion and withdrawal.
- Notify affected data holders without delay after unauthorised access, transfer or use of
  non-personal data.
- Keep external data-sharing endpoints behind production TLS, authentication and least-privilege
  topic/object permissions.

## Release Gate

Before production data sharing:

1. Confirm the DGA role and notification status.
2. Review all data products in the management console.
3. Confirm each product has allowed purposes, access mode, retention, format and transfer policy.
4. Test permission grant, withdrawal and denial workflows.
5. Test unauthorised transfer notice handling.
6. Export the governance evidence topics and attach them to the release record.

