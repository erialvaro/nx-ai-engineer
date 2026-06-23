"""Prompt-1 — ClaudeCodeAdapter tests: modes, timeout, retry, cancel, result.

The CLI call is injected via `command_runner`, so these tests never invoke the
real Claude Code CLI and stay deterministic and offline.
"""
import subprocess
import unittest

from nx_runtime.adapters.base import AgentAdapter
from nx_runtime.adapters.claude_code import ClaudeCodeAdapter
from nx_core.kernel.domain import AgentContext, AgentResult
from nx_core.kernel.engine import ExecutionMode
from nx_core.observability.events import EventBus
from nx_runtime.schedulers.execution import ExecutionEngine, adapter_runner


def _ctx(agent="backend"):
    return AgentContext(agent=agent, subtask_id=agent, acceptance=["tests pass"],
                        files=["api/x.py"])


def ok_runner(out="done"):
    def r(prompt, mode, timeout):
        return 0, out, ""
    return r


def fail_runner(err="boom"):
    def r(prompt, mode, timeout):
        return 1, "", err
    return r


class TestContract(unittest.TestCase):
    def test_satisfies_adapter_protocol(self):
        self.assertIsInstance(ClaudeCodeAdapter(command_runner=ok_runner()), AgentAdapter)

    def test_returns_standardized_agent_result(self):
        a = ClaudeCodeAdapter(command_runner=ok_runner("hi"))
        r = a.run(agent="backend", context=_ctx(), instructions="do it")
        self.assertIsInstance(r, AgentResult)
        self.assertTrue(r.ok)
        self.assertIn("hi", r.notes)
        self.assertGreaterEqual(r.duration_ms, 0)


class TestModes(unittest.TestCase):
    def test_dry_run_never_invokes_cli(self):
        calls = []
        def spy(prompt, mode, timeout):
            calls.append(mode); return 0, "x", ""
        a = ClaudeCodeAdapter(command_runner=spy)
        r = a.run(agent="backend", context=_ctx(), instructions="x", mode=ExecutionMode.DRY_RUN)
        self.assertTrue(r.ok)
        self.assertEqual(calls, [])  # no CLI call in dry-run
        self.assertIn("dry-run", r.notes)

    def test_test_mode_invokes_with_validation_prompt(self):
        seen = {}
        def spy(prompt, mode, timeout):
            seen["mode"] = mode; seen["prompt"] = prompt; return 0, "feasible", ""
        a = ClaudeCodeAdapter(command_runner=spy)
        a.run(agent="backend", context=_ctx(), instructions="x", mode=ExecutionMode.TEST)
        self.assertEqual(seen["mode"], ExecutionMode.TEST)
        self.assertIn("VALIDATION ONLY", seen["prompt"])

    def test_execute_mode_runs(self):
        a = ClaudeCodeAdapter(command_runner=ok_runner(), detect_changes=False)
        r = a.run(agent="backend", context=_ctx(), instructions="x", mode=ExecutionMode.EXECUTE)
        self.assertTrue(r.ok)


class TestRetry(unittest.TestCase):
    def test_retries_then_fails(self):
        attempts = {"n": 0}
        def flaky(prompt, mode, timeout):
            attempts["n"] += 1
            return 1, "", "err"
        a = ClaudeCodeAdapter(command_runner=flaky, max_retries=2, detect_changes=False)
        r = a.run(agent="backend", context=_ctx(), instructions="x")
        self.assertFalse(r.ok)
        self.assertEqual(attempts["n"], 3)  # initial + 2 retries
        self.assertIn("err", r.error)

    def test_retry_then_success(self):
        attempts = {"n": 0}
        def recover(prompt, mode, timeout):
            attempts["n"] += 1
            return (1, "", "e") if attempts["n"] < 2 else (0, "ok", "")
        a = ClaudeCodeAdapter(command_runner=recover, max_retries=3, detect_changes=False)
        r = a.run(agent="backend", context=_ctx(), instructions="x")
        self.assertTrue(r.ok)
        self.assertEqual(attempts["n"], 2)


class TestTimeout(unittest.TestCase):
    def test_timeout_is_a_failure(self):
        def slow(prompt, mode, timeout):
            raise subprocess.TimeoutExpired(cmd="claude", timeout=timeout)
        a = ClaudeCodeAdapter(command_runner=slow, max_retries=0, timeout=1, detect_changes=False)
        r = a.run(agent="backend", context=_ctx(), instructions="x")
        self.assertFalse(r.ok)
        self.assertIn("timeout", r.error)

    def test_timeout_then_retry_success(self):
        n = {"i": 0}
        def slow_then_ok(prompt, mode, timeout):
            n["i"] += 1
            if n["i"] == 1:
                raise TimeoutError()
            return 0, "ok", ""
        a = ClaudeCodeAdapter(command_runner=slow_then_ok, max_retries=1, detect_changes=False)
        self.assertTrue(a.run(agent="backend", context=_ctx(), instructions="x").ok)


class TestCancel(unittest.TestCase):
    def test_cancel_before_run(self):
        a = ClaudeCodeAdapter(command_runner=ok_runner())
        a.cancel()
        r = a.run(agent="backend", context=_ctx(), instructions="x")
        self.assertFalse(r.ok)
        self.assertEqual(r.error, "cancelled")

    def test_cancel_between_retries(self):
        a = ClaudeCodeAdapter(command_runner=fail_runner(), max_retries=5, detect_changes=False)
        def cancel_after_first(prompt, mode, timeout):
            a.cancel()
            return 1, "", "e"
        a._command_runner = cancel_after_first
        r = a.run(agent="backend", context=_ctx(), instructions="x")
        self.assertFalse(r.ok)
        self.assertEqual(r.error, "cancelled")


class TestErrors(unittest.TestCase):
    def test_missing_cli_is_reported(self):
        def missing(prompt, mode, timeout):
            raise FileNotFoundError("claude")
        a = ClaudeCodeAdapter(command_runner=missing)
        r = a.run(agent="backend", context=_ctx(), instructions="x")
        self.assertFalse(r.ok)
        self.assertIn("not found", r.error)

    def test_available_is_boolean(self):
        self.assertIsInstance(ClaudeCodeAdapter.available(["definitely-not-a-cmd"]), bool)


class TestEngineIntegration(unittest.TestCase):
    def test_mode_aware_adapter_drives_all_phases(self):
        modes = []
        def spy(prompt, mode, timeout):
            modes.append(mode); return 0, "ok", ""
        adapter = ClaudeCodeAdapter(command_runner=spy, detect_changes=False)
        eng = ExecutionEngine(adapter=adapter)
        ctx = {"id": "t", "subtasks": [{"agent": "backend", "objective": "x",
                                        "areas": [], "depends_on": [], "acceptance": []}]}
        eng.run_full_cycle(ctx)
        # TEST and EXECUTE hit the CLI; DRY_RUN does not.
        self.assertIn(ExecutionMode.TEST, modes)
        self.assertIn(ExecutionMode.EXECUTE, modes)
        self.assertNotIn(ExecutionMode.DRY_RUN, modes)

    def test_adapter_runner_passes_mode_only_when_supported(self):
        # ClaudeCodeAdapter supports mode; a plain object without it should not error.
        adapter = ClaudeCodeAdapter(command_runner=ok_runner(), detect_changes=False)
        runner = adapter_runner(adapter, ExecutionMode.EXECUTE)
        from nx_core.kernel.domain import Node, Subtask
        node = Node(Subtask(id="backend", agent="backend", objective="x"))
        self.assertTrue(runner(node).ok)

    def test_engine_cancel_propagates_to_adapter(self):
        adapter = ClaudeCodeAdapter(command_runner=ok_runner())
        eng = ExecutionEngine(adapter=adapter)
        eng.cancel()
        self.assertTrue(adapter._cancelled)


if __name__ == "__main__":
    unittest.main()
