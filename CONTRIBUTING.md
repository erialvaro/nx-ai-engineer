# Contributing to AIES

Thanks for contributing. AIES values **stability, simplicity and extensibility**.
Most additions should go through the **SDK** (agents/engines/workflows/adapters/
plugins/tools) — not by changing the core.

## Principles
1. **Stdlib-only core.** No third-party runtime dependencies in `aies/`.
2. **Extend, don't modify.** Prefer the SDK and the contracts (`BaseEngine`,
   `AgentAdapter`, `SelectionStrategy`, `Resolver`, `SemanticIndex`).
3. **No breaking changes** without a major version + migration note.
4. **Knowledge, never code** in the Project Brain.
5. **Dry Run by default.** New engines obey the Dry Run → Test → Execute gate.

## Workflow
1. Branch from the default branch.
2. Make the change; keep it small and focused.
3. Add/adjust tests (every public behavior is tested).
4. Update docs (and an ADR for any architectural decision).
5. Run the **Quality Gate** — it must pass:
   ```
   python scripts/quality_gate.py
   ```
6. Open a PR. The gate is the merge bar (see below).

## Quality Gate (merge bar)
A PR is **not** approved if any of these fail:
- tests fail;
- coverage of public APIs drops (add tests with new public code);
- an architecture rule is violated (import cycle, core importing upward);
- documentation becomes stale;
- a public API/CLI is broken;
- an import cycle is introduced.

## Code style
- Match the surrounding code; small functions; clear names.
- Engines are single-responsibility and talk via plain dicts/dataclasses + events.
- The core never imports a specific AI model — only `AgentAdapter`.

## Tests
```
cd framework/tools
python -m unittest discover -s tests -t . -p "test_*.py"
```

## Adding things
- **Agent:** `packages/nx-cli/nx_cli/_template/agents/_TEMPLATE.md` + `config.json > extra_agents` or
  `sdk.register_agent`. See `examples/01_create_agent.md`.
- **Engine:** subclass `BaseEngine`; see `packages/nx-cli/nx_cli/_template/docs/ENGINE_GUIDE.md`.
- **Workflow / Adapter / Plugin / Tool:** see `packages/nx-cli/nx_cli/_template/docs/SDK_GUIDE.md`.
