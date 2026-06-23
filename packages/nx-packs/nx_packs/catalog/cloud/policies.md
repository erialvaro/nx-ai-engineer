# Policies — Cloud Architecture

Enforceable rules for this domain. Agents must respect these; reviewers must check them.

- All infrastructure is declared as code (no click-ops).
- IAM is least-privilege; no wildcard admin roles.
- Network is segmented; private subnets for data stores.
- Secrets come from a managed secret store; rotate them.
- Backups are automated and restore-tested; multi-AZ for critical paths.
