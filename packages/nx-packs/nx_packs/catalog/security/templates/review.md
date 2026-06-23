# Application Security — review template

Use when reviewing a change in this domain.

## Scope
- What changed:
- Domain surfaces touched:

## Checklist
- [ ] Change mapped against OWASP Top 10 (A01–A10)
- [ ] All input validated/encoded at the boundary
- [ ] Queries parameterized; no string-built SQL/commands
- [ ] Authorization checked on every new endpoint/operation
- [ ] No secrets in code/config/logs; pulled from a vault
- [ ] Dependencies scanned; no known-vulnerable versions added

## Risks & mitigations
- 

## Sign-off
- Reviewer:
