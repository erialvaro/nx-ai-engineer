# ADR-0010: Execution Cluster — concurrent worker pool over the Execution Engine

- **Status:** Accepted
- **Date:** 2026-06-22
- **Builds on:** ADR-0001 (Execution Engine), ADR-0009 (ClaudeCodeAdapter)

## Context
The Execution Engine ran nodes sequentially. To execute multiple agents in a
coordinated way and use available parallelism, we need a worker pool, an internal
queue, a scheduler, concurrency control, priorities — without duplicating the
node-execution logic and without breaking the existing engine.

## Decision
1. **Extract the shared core.** The per-node logic (lock check, state
   transitions + events, runner call, retry) moves into a single reusable
   `NodeExecutor` (in `schedulers/execution.py`), plus module helpers
   `build_graph` and `node_priority`. The sequential `ExecutionEngine` is
   refactored to use `NodeExecutor` — **identical behavior**, no duplication.
   `NodeExecutor` takes an optional `threading.Lock`; transitions/emits happen
   under it, the runner call happens **outside** it.
2. **Add `ExecutionCluster`** (`schedulers/cluster.py`), a `BaseEngine` (same Dry
   Run → Test → Execute gate) that adds only the new thing — a concurrent
   scheduler:
   - **Worker Pool** — N worker threads, each with its own lifecycle
     (CREATED → IDLE → BUSY → STOPPING → STOPPED), exposing `processed`/`current`.
   - **Internal Queue** — a priority heap; `node_priority(agent, plan_priority)`
     ranks ready nodes (contracts/data agents first; high-priority plans boost).
   - **Scheduler** — enqueues ready nodes (respecting `TaskGraph` dependencies
     and advisory locks), waits on a `Condition`, and re-evaluates as workers
     complete. Concurrency is bounded by the pool size.
   - **Retry / Cancel / Dependencies** — reused from `NodeExecutor` / `TaskGraph`
     / the state machine; `cancel()` is a `threading.Event` that also cancels a
     mode-aware adapter (e.g. kills an in-flight Claude Code process).
3. **Compatibility.** `ExecutionEngine` is unchanged in API and behavior. The CLI
   gains `run/pipeline --workers N` (default **1 = sequential engine**); `N>1`
   selects the cluster. Same `Run`/`EngineResult`, same events, same gate.

## Alternatives considered
- **`concurrent.futures.ThreadPoolExecutor`.** Rejected as the top-level driver:
  dependency-aware re-scheduling and priorities need a custom scheduler loop; a
  pool of `map`-style futures doesn't model the DAG well. (We use raw threads +
  a `Condition`, all stdlib.)
- **multiprocessing.** Rejected: agent work is I/O-bound (CLI/model calls), so
  threads suffice and avoid serialization/IPC overhead and complexity.
- **Reimplement node execution in the cluster.** Rejected: that is exactly the
  duplication this ADR avoids by extracting `NodeExecutor`.

## Consequences
- Independent agents now run in parallel; dependent ones still serialize
  correctly. Verified: 4 nodes × 0.15s run in ~0.2s with 4 workers vs ~0.8s with 1.
- One source of truth for node execution → engine and cluster cannot diverge.
- The event bus is shared and made thread-safe via the executor's mutex (emits
  serialized; work runs concurrently).
- Backward compatible; default path is the sequential engine. Covered by
  `test_cluster.py` (concurrency, max-parallelism bound, priorities, retry,
  failure→blocked dependents, cancel, worker lifecycle, events). Full suite: 117
  tests, green; the engine's existing 12 tests unchanged.
