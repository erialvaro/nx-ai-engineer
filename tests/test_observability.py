"""PR-8 — Observability: structured logging and telemetry."""
import os
import tempfile
import unittest
from pathlib import Path

from nx_core.observability.events import EventBus
from nx_core.observability.logging import EventLogger
from nx_core.observability.telemetry import Telemetry


class _Home:
    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        cfg = Path(self.tmp.name) / ".ai-project-assistant"
        cfg.mkdir()
        self._old = os.environ.get("AIES_HOME")
        os.environ["AIES_HOME"] = str(cfg)
        return cfg

    def __exit__(self, *a):
        if self._old is None:
            os.environ.pop("AIES_HOME", None)
        else:
            os.environ["AIES_HOME"] = self._old
        self.tmp.cleanup()


class TestLogging(unittest.TestCase):
    def test_writes_jsonl(self):
        with _Home() as cfg:
            bus = EventBus()
            logger = EventLogger(bus=bus)
            bus.emit("a.b", {"k": 1})
            bus.emit("c.d", {})
            self.assertEqual(logger.written, 2)
            log = cfg / "logs" / "events.jsonl"
            self.assertTrue(log.exists())
            self.assertEqual(len(log.read_text(encoding="utf-8").splitlines()), 2)


class TestTelemetry(unittest.TestCase):
    def test_counts_and_kpis(self):
        bus = EventBus()
        tel = Telemetry(bus=bus)
        bus.emit("task.started", {})
        bus.emit("task.started", {})
        bus.emit("task.completed", {})
        bus.emit("task.failed", {})
        snap = tel.snapshot()
        self.assertEqual(snap["kpis"]["tasks_started"], 2)
        self.assertEqual(snap["kpis"]["failure_rate"], 0.5)
        self.assertEqual(snap["events_total"], 4)

    def test_export(self):
        with _Home():
            bus = EventBus()
            tel = Telemetry(bus=bus)
            bus.emit("run.completed", {})
            p = tel.export()
            self.assertTrue(p.exists())


if __name__ == "__main__":
    unittest.main()
