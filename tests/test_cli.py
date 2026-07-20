"""RC1 — public CLI surface tests (parser + handlers + adapter resolution)."""
import unittest

from nx_cli import orchestrator

EXPECTED = {
    "audit": "cmd_audit", "plan": "cmd_plan", "decide": "cmd_decide",
    "dispatch": "cmd_dispatch", "context": "cmd_context", "run": "cmd_run",
    "review": "cmd_review", "deliver": "cmd_deliver", "pipeline": "cmd_pipeline",
    "metrics": "cmd_metrics", "insights": "cmd_insights", "recommend": "cmd_recommend",
    "knowledge": "cmd_knowledge", "obsidian": "cmd_obsidian",
    "tasks": "cmd_tasks", "locks": "cmd_locks", "unlock": "cmd_unlock",
    "status": "cmd_status", "worktree": "cmd_worktree", "port": "cmd_port",
}

MINIMAL_ARGS = {
    "audit": ["audit"], "plan": ["plan", "x"], "decide": ["decide", "x"],
    "dispatch": ["dispatch", "x"], "context": ["context", "--plan", "t", "--agent", "backend"],
    "run": ["run", "--plan", "t"], "review": ["review"], "deliver": ["deliver", "--plan", "t"],
    "pipeline": ["pipeline", "x"], "metrics": ["metrics"], "insights": ["insights"],
    "recommend": ["recommend", "x"], "knowledge": ["knowledge", "index"],
    "obsidian": ["obsidian", "status"],
    "tasks": ["tasks"], "locks": ["locks"],
    "unlock": ["unlock"], "status": ["status"], "worktree": ["worktree", "backend"],
    "port": ["port"],
}


class TestCLIParser(unittest.TestCase):
    def setUp(self):
        self.parser = orchestrator.build_parser()

    def test_every_command_registered_and_routes_to_handler(self):
        for cmd, handler in EXPECTED.items():
            args = self.parser.parse_args(MINIMAL_ARGS[cmd])
            self.assertTrue(hasattr(args, "fn"), f"{cmd} has no handler")
            self.assertEqual(args.fn.__name__, handler, f"{cmd} routes wrong")

    def test_run_modes_and_workers(self):
        args = self.parser.parse_args(["run", "--plan", "t", "--mode", "execute",
                                       "--adapter", "claude-code", "--workers", "4"])
        self.assertEqual(args.mode, "execute")
        self.assertEqual(args.adapter, "claude-code")
        self.assertEqual(args.workers, 4)

    def test_knowledge_graph_action(self):
        args = self.parser.parse_args(["knowledge", "graph", "--format", "mermaid"])
        self.assertEqual(args.action, "graph")
        self.assertEqual(args.format, "mermaid")

    def test_pipeline_defaults_safe(self):
        args = self.parser.parse_args(["pipeline", "do something"])
        self.assertEqual(args.mode, "dry_run")     # safe by default
        self.assertEqual(args.adapter, "dry-run")

    def test_unknown_command_exits(self):
        with self.assertRaises(SystemExit):
            self.parser.parse_args(["frobnicate"])


class TestAdapterResolution(unittest.TestCase):
    def test_dry_run_default(self):
        self.assertEqual(orchestrator._make_adapter("dry-run").name, "dry-run")

    def test_claude_code(self):
        self.assertEqual(orchestrator._make_adapter("claude-code").name, "claude-code")

    def test_unknown_adapter_exits(self):
        with self.assertRaises(SystemExit):
            orchestrator._make_adapter("nonexistent-xyz")


if __name__ == "__main__":
    unittest.main()
