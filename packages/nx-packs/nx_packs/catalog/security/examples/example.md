# Example — Application Security

A centralized authorization middleware checks the caller's permission for the target resource on every request; handlers cannot run without an explicit allow decision, so 'broken access control' (OWASP A01) is prevented by design.
