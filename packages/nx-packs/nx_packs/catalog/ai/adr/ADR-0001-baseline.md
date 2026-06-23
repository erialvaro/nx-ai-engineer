# ADR-0001: AI / LLM Integration baseline

- **Status:** Accepted
- **Domain:** ai

## Context
Safely USING AI models in the product (prompt-injection, output validation, data minimization, cost/limits). NX never implements AI — this governs how the product calls models.

## Decision
Adopt the policies and patterns in this pack as the domain baseline.

## Consequences
Changes in this domain are reviewed against `checklists.md`; violations of `policies.md` block delivery.
