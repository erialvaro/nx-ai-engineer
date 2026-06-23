# ADR-0020: The Engineering Contract — how knowledge reaches the agent

- **Status:** Accepted
- **Date:** 2026-06-23
- **Builds on:** ADR-0003 (Context Engine), ADR-0013 (Knowledge Providers),
  ADR-0015/0018 (Knowledge Engine doctrine), the Engineering Packs

## Context
The platform organizes Brain, Knowledge, Context and Providers, but *how that
reaches an agent* was implicit and imperative — you had to remember to ask for the
right ADRs, rules and packs. There was no single, predictable object that says
"this is what applies to this task for this agent."

## Decision
Introduce the **Engineering Contract** as the declarative brief delivered to an
agent, and make the flow explicit:

```
Task → EngineeringContract → Context Builder → model → result → Knowledge Update
```

A contract assembles (it never reasons): `context` (files/areas), `knowledge`
(ADRs/patterns), `engineering` (the Engineering Packs that apply), `constraints`
(project + pack policies), `requirements` (mandatory tests/validations/checklists/
ADRs) and `brain` (which Brain facets enter the context).

**Engineering Packs become contracts.** Each pack declares `applies_to` (agents or
`"*"`), plus `required_adrs`, `mandatory_tests`, `validations` and `brain_facets`.
Packs **auto-attach** to an agent by `applies_to`, with per-agent overrides in
`config.json` (`contracts.agents.<agent>`). So the Backend Agent automatically
receives the Security, LGPD and Multi-Tenant contracts.

**Enforcement.** The contract is enforced at delivery: a Governance/Delivery
**contract gate** blocks `deliver` when an applicable pack mandates tests but
changed code files lack them, and the PR surfaces the contract's required
validations/checklists.

## Where it lives
`EngineeringContract` + `ContractBuilder` live in the knowledge layer
(`nx_knowledge/knowledge/contract.py`); the Knowledge Engine exposes
`build_contract(task, agent)` (part of `deliver_context`). The CLI exposes
`nxai contract`. Enforcement is in the Delivery engine (it composes the
governance gates with the contract requirements). The Pack Provider surfaces the
`applies_to`/requirements declared in each `pack.json`.

## Consequences
- The platform stops being only a knowledge organizer and becomes a framework that
  **guarantees** reusable engineering standards on every implementation.
- The doctrine holds: the contract only **organizes** declared data; all
  intelligence remains the model's.
- Adding a domain standard is declarative (author/extend a pack) — no core change.
