# Context — Billing / Payments

Treat money exactly: integer minor units, idempotent operations, verified webhooks, and a full audit trail — never double-charge.

## Non-negotiables
- Represent money as integer minor units (cents); never floats.
- Every charge/refund is idempotent (idempotency key).
- Verify payment-provider webhook signatures before acting.
- Keep an immutable audit trail of money movements.
- Reconcile with the provider; alert on mismatches.

## Always verify
- Money is integer minor units
- Operations idempotent
- Webhooks signature-verified
- Audit trail recorded
- Reconciliation in place
