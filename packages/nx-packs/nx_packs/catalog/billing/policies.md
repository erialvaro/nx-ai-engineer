# Policies — Billing / Payments

Enforceable rules for this domain. Agents must respect these; reviewers must check them.

- Represent money as integer minor units (cents); never floats.
- Every charge/refund is idempotent (idempotency key).
- Verify payment-provider webhook signatures before acting.
- Keep an immutable audit trail of money movements.
- Reconcile with the provider; alert on mismatches.
