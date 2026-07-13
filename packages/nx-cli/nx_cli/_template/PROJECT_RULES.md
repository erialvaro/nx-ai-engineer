# PROJECT RULES

Non-negotiable rules every agent (human or AI) must follow on this project.
The orchestrator and Reviewer enforce as many of these as can be checked
mechanically; the rest are on you. Project-specific invariants live in
`config.json > domain_rules` and are surfaced into tasks automatically.

## Compatibility
- Never break backward compatibility of public APIs or contracts.
- Never create duplicate endpoints — reuse existing ones.
- Never duplicate services or documentation — extend what exists.

## Safety
- Never remove logs or weaken observability.
- Never change authentication/authorization without tests.
- Never modify billing/payments without explicit approval and tests.
- Never touch another agent's forbidden paths.

## Data
- Never cause data loss; migrations must be reversible.
- Preserve data-isolation invariants (e.g. multi-tenant scoping) — see
  `docs/tenant-rules.md`.
- Respect privacy/PII handling — see `docs/lgpd.md`.

## Process
- Always audit before planning; always plan before implementing.
- Always add/update tests for behavior changes.
- Always run the existing test suite and report results faithfully.
- Always document changes (code, changelog, ADR when non-obvious).
- Always follow existing patterns and conventions (`docs/coding-standards.md`,
  `docs/patterns.md`).
- Never refactor opportunistically — only what the task requires.

## Knowledge & history (use the framework as your memory)
- **Start from memory.** Before planning or editing, consult the project's three
  memories so you never lose context or repeat a past decision: run
  `nxai knowledge status` / `nxai knowledge list`, and read the **Project Brain**
  (`.ai-project-assistant/brain/`), the **ADRs** (`docs/adr/`) and the git history.
  `nxai contract --agent <a> "<task>"` assembles this context for an agent.
- **Record decisions.** Capture non-obvious choices as **ADRs**, then run
  `nxai knowledge sync` so the Project Brain (operational), the Obsidian vault
  (organizational) and — opt-in — a Git snapshot (historical) stay current. This
  is how the platform helps future sessions: decisions, agents and outcomes accrue.
- **Never lose history.** The framework's snapshots are additive and live under
  `.ai-project-assistant/`; they never rewrite or replace the project's own Git
  history (GitHub stays the source of truth for code).

## Scope discipline
- Each task has one set of allowed paths per agent; stay inside them.
- Check locks before claiming files; release locks after delivery.
- Keep changes small, additive and reviewable.
