# Policies — Observability

Enforceable rules for this domain. Agents must respect these; reviewers must check them.

- Structured logs with a correlation/request id across services.
- Key operations expose metrics (latency, errors, throughput).
- Distributed tracing on cross-service paths.
- SLOs defined with alerts on error budget burn.
- Logs/metrics/traces contain no PII or secrets.
