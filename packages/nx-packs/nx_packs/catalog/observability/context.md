# Context — Observability

Emit structured logs, metrics and traces with a correlation id; define SLOs and alerts; never log PII/secrets.

## Non-negotiables
- Structured logs with a correlation/request id across services.
- Key operations expose metrics (latency, errors, throughput).
- Distributed tracing on cross-service paths.
- SLOs defined with alerts on error budget burn.
- Logs/metrics/traces contain no PII or secrets.

## Always verify
- Correlation id present
- Metrics on the changed path
- Tracing on cross-service calls
- SLO/alert defined
- No PII in signals
