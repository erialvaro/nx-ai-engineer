# ADR-0009: ClaudeCodeAdapter — real execution via the Claude Code CLI

- **Status:** Accepted
- **Date:** 2026-06-22
- **Follow-up to:** ADR-0001 (Execution Engine), ADR-0006 (Pipeline)

## Context
AIES could plan, dispatch, contextualize and *simulate* execution, but every
`execute` used the `DryRunAdapter` (no real changes). To become a platform that
actually implements work, it needs to drive a real model — Claude Code — while
keeping the core model-agnostic: no Engine may ever import or know about Claude.

## Decision
Implement a `ClaudeCodeAdapter` (`adapters/claude_code.py`) behind the existing
`AgentAdapter` boundary. It encapsulates **all** Claude Code communication and:
- is **mode-aware** (Dry Run → Test → Execute): DRY_RUN composes the prompt and
  invokes nothing; TEST runs a validation-only pass (no file changes); EXECUTE
  runs the real work and detects `changed_files` via git (best-effort);
- supports **timeout** (bounded invocation), **retry** (`max_retries`) and
  **cancel()** (aborts pending attempts and kills the in-flight process);
- returns the standardized `AgentResult` (ok/changed_files/notes/error/duration_ms).

To let the adapter respect all three phases through the engine, the
`AgentAdapter` contract gains an **optional** keyword `mode` (default EXECUTE).
`schedulers.execution.adapter_runner` passes `mode` **only** to adapters that
declare it (via signature inspection), so the existing `DryRunAdapter` and any
3-argument adapter remain fully compatible. `ExecutionEngine` accepts an
`adapter=` and, when present, drives dry/test/execute through it (mode-aware);
the legacy `runner=` path is unchanged. `cancel()` propagates from engine to
adapter. The CLI exposes `--adapter dry-run|claude-code|<sdk-name>` on `run` and
`pipeline` (default stays `dry-run`, safe).

The real CLI call is **injectable** (`command_runner`), so the adapter is fully
unit-tested without ever invoking Claude Code.

## Alternatives considered
- **Engine calls Claude directly.** Rejected: couples the core to a model;
  violates the Adapter boundary and the "swap models without touching Engines".
- **New required `mode` argument on the contract.** Rejected: breaks existing
  adapters/tests. Made it optional + signature-detected → fully backward compatible.
- **Execute as the CLI default.** Rejected: unsafe. Default remains `dry-run`;
  `claude-code` is explicit opt-in. Even then, TEST cannot modify files.
- **An SDK/library binding instead of the CLI.** Deferred: the CLI is portable
  and stdlib-only (`subprocess`); a different binding is just another adapter.

## Consequences
- `run`/`pipeline --adapter claude-code` performs real implementations under the
  mandatory Dry Run → Test → Execute gate; `dry-run` stays the safe default.
- The core remains model-agnostic; replacing Claude Code = registering another
  `AgentAdapter`, with zero Engine changes.
- Covered by `test_claude_adapter.py` (contract, modes, retry, timeout, cancel,
  missing-CLI, engine integration). Full suite: 106 tests, green. No regressions.
- Real CLI flags (`command`, `model`, `test_args`, `execute_args`, `prompt_via`)
  are configurable per environment; defaults target headless `claude -p`.
