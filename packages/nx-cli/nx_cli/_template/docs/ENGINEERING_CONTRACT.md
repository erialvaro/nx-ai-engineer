# Engineering Contract

The **Engineering Contract** is how knowledge reaches the agent. An agent does not
receive an ad-hoc prompt — it receives a **contract**: a declarative, predictable
statement of everything that applies to a task.

```
Task → Engineering Contract → Context Builder → Model → Result → Knowledge Update
```

This is the concept that ties Brain, Knowledge, Context, Providers and Packs
together. NX **organizes** the contract; the model still does all the reasoning.

## What a contract contains

```yaml
task:
  Implement Google login
agent:
  backend
context:
  files:
    - auth.py
    - login.tsx
  areas:
    - api/auth
knowledge:
  - ADR-0023: OAuth provider
  - OAuth Pattern
engineering:
  - Application Security  (security)
  - LGPD / Privacy        (lgpd)
  - Multi-Tenancy         (multi-tenant)
constraints:
  - [security] Validate and canonicalize all external input; reject by default.
  - Never read or write another tenant's data
requirements:
  tests:
    - Unauthorized caller is denied on every protected endpoint
  validations:
    - No secrets in code/config
  checklists:
    - Queries parameterized; no string-built SQL
  adrs: []
brain:
  - decisions
  - architecture
```

Build one with:

```bash
nxai contract --agent backend "Implement Google login" --files auth.py login.tsx --areas api/auth
nxai contract --plan <task-id> --agent backend --format json
```

## Engineering Packs ARE contracts

A pack does not (only) create files — it **declares**, for the framework:

- `applies_to` — which agents it auto-attaches to (or `"*"` for cross-cutting);
- `policies` → **constraints** the agent must respect;
- `checklists` / `validations` / `mandatory_tests` → **requirements**;
- `required_adrs` → ADRs to consider;
- `brain_facets` → which Project-Brain facets enter the context.

So when the **Backend Agent** gets a task, it automatically receives the
**Security**, **LGPD** and **Multi-Tenant** contracts — without anyone remembering
to ask. That is the difference between a knowledge organizer and a framework that
*guarantees* engineering standards.

### Auto-application

A pack attaches to an agent when its `applies_to` contains that agent or `"*"`.
Override per agent in `config.json`:

```json
{
  "contracts": {
    "agents": {
      "backend": { "packs": ["billing"], "exclude": ["docker"],
                   "constraints": ["No raw SQL in handlers"] }
    }
  }
}
```

## Enforcement at delivery

The contract is not just advisory. At `nxai deliver`, the **contract gate** checks
the task's contract: if an applicable pack **mandates tests** and the review shows
changed code files **without tests**, delivery is **blocked**. The generated PR
lists the contract's required validations/checklists so reviewers see exactly what
the contract demands.

This closes the loop: `Task → Contract → … → Knowledge Update`, with the contract
acting as a **guarantee**, not a suggestion.
