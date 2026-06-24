"""ClaudeCodeAdapter — runs real agent work through the Claude Code CLI.

This is the boundary the rest of the platform never imports directly. It
encapsulates *all* communication with Claude Code and returns a standardized
`AgentResult`, so Claude Code can be swapped for any other model later without
touching a single Engine.

Guarantees / features (architecture §11, §13; ADR-0009):
- **Mode-aware** (Dry Run → Test → Execute):
    * DRY_RUN  — composes the prompt, invokes nothing, zero side effects.
    * TEST     — validation pass: instructs the model to assess feasibility and
                 NOT modify files (and may pass read-only CLI args if configured).
    * EXECUTE  — real run that may change files.
- **Timeout** — each invocation is bounded; a timeout fails the attempt.
- **Retry**   — up to `max_retries` extra attempts on failure/timeout.
- **Cancel**  — `cancel()` aborts pending/next attempts and kills an in-flight
                process.
- **Standardized AgentResult** — ok / changed_files / notes / error / duration_ms.

The actual CLI call is injectable (`command_runner`) so the adapter is fully
testable without invoking Claude Code, and stdlib-only.
"""
from __future__ import annotations

import shutil
import subprocess
import time
from typing import Callable, Optional

from nx_core.foundation import util
from nx_core.kernel.domain import AgentContext, AgentResult
from nx_core.kernel.engine import ExecutionMode

# A command runner returns (returncode, stdout, stderr) or raises TimeoutError.
CommandRunner = Callable[[str, ExecutionMode, int], "tuple[int, str, str]"]


class ClaudeCodeAdapter:
    name = "claude-code"

    def __init__(
        self,
        *,
        command: Optional[list[str]] = None,
        model: Optional[str] = None,
        timeout: int = 600,
        max_retries: int = 1,
        command_runner: Optional[CommandRunner] = None,
        detect_changes: bool = True,
        prompt_via: str = "arg",          # "arg" => append prompt; "stdin" => pipe it
        test_args: Optional[list[str]] = None,
        execute_args: Optional[list[str]] = None,
    ) -> None:
        # Default headless invocation; override `command` for your environment.
        self._command = command or ["claude", "-p"]
        self._model = model
        self._timeout = timeout
        self._max_retries = max_retries
        self._command_runner = command_runner or self._default_command_runner
        self._detect_changes = detect_changes
        self._prompt_via = prompt_via
        self._test_args = test_args or []
        self._execute_args = execute_args or []
        self._cancelled = False
        self._proc: Optional[subprocess.Popen] = None

    # -- availability ----------------------------------------------------- #
    @staticmethod
    def available(command: Optional[list[str]] = None) -> bool:
        exe = (command or ["claude"])[0]
        return shutil.which(exe) is not None

    # -- cancellation ----------------------------------------------------- #
    def cancel(self) -> None:
        self._cancelled = True
        proc = self._proc
        if proc is not None:
            try:
                proc.kill()
            except Exception:
                pass

    def reset(self) -> None:
        self._cancelled = False

    # -- main entrypoint -------------------------------------------------- #
    def run(self, *, agent: str, context: AgentContext, instructions: str,
            mode: ExecutionMode = ExecutionMode.EXECUTE) -> AgentResult:
        if self._cancelled:
            return AgentResult(ok=False, error="cancelled")

        prompt = self._build_prompt(agent, context, instructions, mode)

        # DRY_RUN never talks to the model — it only prepares the plan.
        if mode is ExecutionMode.DRY_RUN:
            return AgentResult(ok=True, changed_files=[],
                               notes=f"[claude-code dry-run] prompt prepared "
                                     f"({len(prompt)} chars) for '{agent}'")

        last_error: Optional[str] = None
        attempts = 0
        started = time.monotonic()
        while attempts <= self._max_retries:
            if self._cancelled:
                return AgentResult(ok=False, error="cancelled",
                                   duration_ms=_ms(started))
            attempts += 1
            attempt_start = time.monotonic()
            try:
                rc, out, err = self._command_runner(prompt, mode, self._timeout)
            except (TimeoutError, subprocess.TimeoutExpired):
                last_error = f"timeout after {self._timeout}s"
                continue
            except FileNotFoundError:
                return AgentResult(ok=False, duration_ms=_ms(attempt_start),
                                   error="Claude Code CLI not found on PATH "
                                         "(configure `command=`).")
            except Exception as exc:  # never let a CLI hiccup crash the engine
                last_error = repr(exc)
                continue

            if self._cancelled:
                return AgentResult(ok=False, error="cancelled", duration_ms=_ms(started))

            duration = _ms(attempt_start)
            if rc == 0:
                changed = self._changed_files() if (
                    mode is ExecutionMode.EXECUTE and self._detect_changes) else []
                return AgentResult(ok=True, changed_files=changed,
                                   notes=(out or "").strip()[:2000], duration_ms=duration)
            last_error = (err or out or f"exit code {rc}").strip()[:500]

        return AgentResult(ok=False, error=last_error or "failed after retries",
                           duration_ms=_ms(started))

    # -- internals -------------------------------------------------------- #
    def _build_prompt(self, agent: str, context: AgentContext, instructions: str,
                      mode: ExecutionMode) -> str:
        lines = [
            f"You are the AIES '{agent}' agent. Follow .ai-project-assistant/PROJECT_RULES.md "
            f"and .ai-project-assistant/agents/{agent}.md strictly.",
            "",
            f"## Objective\n{instructions}",
        ]
        if mode is ExecutionMode.TEST:
            lines += ["", "## MODE: TEST (VALIDATION ONLY)",
                      "Do NOT modify any files. Assess feasibility, list the changes "
                      "you WOULD make, and flag risks. Output a short report only."]
        else:
            lines += ["", "## MODE: EXECUTE",
                      "Implement the objective. Stay within your allowed paths. "
                      "Add/adjust tests. Do not touch forbidden paths."]
        if context.acceptance:
            lines += ["", "## Acceptance criteria"] + [f"- {a}" for a in context.acceptance]
        if context.files:
            lines += ["", "## Relevant files"] + [f"- {f}" for f in context.files[:20]]
        if context.apis:
            lines += ["", "## Relevant APIs"] + [f"- {a}" for a in context.apis[:10]]
        return "\n".join(lines)

    def _default_command_runner(self, prompt: str, mode: ExecutionMode,
                                timeout: int) -> "tuple[int, str, str]":
        cmd = list(self._command)
        if self._model:
            cmd += ["--model", self._model]
        if mode is ExecutionMode.TEST and self._test_args:
            cmd += self._test_args
        if mode is ExecutionMode.EXECUTE and self._execute_args:
            cmd += self._execute_args
        input_data: Optional[str] = None
        if self._prompt_via == "arg":
            cmd += [prompt]
        else:
            input_data = prompt

        self._proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE if input_data is not None else None,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace",
        )
        try:
            out, err = self._proc.communicate(input=input_data, timeout=timeout)
            return self._proc.returncode, out, err
        except subprocess.TimeoutExpired:
            self._proc.kill()
            self._proc.communicate()
            raise
        finally:
            self._proc = None

    def _changed_files(self) -> list[str]:
        try:
            return util.changed_files("HEAD")
        except Exception:
            return []


def _ms(start: float) -> int:
    return int((time.monotonic() - start) * 1000)
