# Test guidance — Application Security

Turn each checklist item into a concrete, automated test where possible (unit/integration/contract). Examples to implement for your stack:

- Assert an unauthorized caller is denied on every protected endpoint.
- Assert injection payloads are neutralized (parameterized queries).
- Assert error responses contain no stack traces or internals.
