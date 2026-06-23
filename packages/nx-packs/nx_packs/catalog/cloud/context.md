# Context — Cloud Architecture

Provision via IaC with least-privilege IAM, segment the network, manage secrets centrally, and design for failure.

## Non-negotiables
- All infrastructure is declared as code (no click-ops).
- IAM is least-privilege; no wildcard admin roles.
- Network is segmented; private subnets for data stores.
- Secrets come from a managed secret store; rotate them.
- Backups are automated and restore-tested; multi-AZ for critical paths.

## Always verify
- IaC covers the change
- IAM least-privilege
- Network segmented
- Secrets in a managed store
- Backups + restore tested
