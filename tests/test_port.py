"""`nxai port` — free-localhost-port discovery before a project is brought up.

The primitive (`nx_core.net`) and the CLI both answer one question: which port
can a dev server actually bind on http://localhost right now. Tests occupy a real
port with a listening socket and assert the helpers route around it.
"""
import io
import socket
import unittest
from contextlib import closing, redirect_stdout

from nx_cli import orchestrator
from nx_core.foundation import net


def _occupy():
    """Bind + listen on an OS-chosen free port; return (socket, port). The port
    is busy until the socket is closed."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((net.LOCALHOST, 0))
    s.listen(1)
    return s, s.getsockname()[1]


class TestPortPrimitive(unittest.TestCase):
    def test_busy_port_is_not_free(self):
        s, port = _occupy()
        with closing(s):
            self.assertFalse(net.is_port_free(port))

    def test_freed_port_is_free_again(self):
        s, port = _occupy()
        s.close()
        self.assertTrue(net.is_port_free(port))

    def test_out_of_range_never_free(self):
        for bad in (0, -1, 70000, 65536):
            self.assertFalse(net.is_port_free(bad), f"{bad} reported free")

    def test_find_returns_preferred_when_free(self):
        s, port = _occupy()
        s.close()
        self.assertEqual(net.find_free_port(port), port)

    def test_find_skips_busy_preferred(self):
        s, port = _occupy()
        with closing(s):
            chosen = net.find_free_port(port, span=50)
            self.assertGreater(chosen, port)
            self.assertTrue(net.is_port_free(chosen))

    def test_find_raises_when_window_exhausted(self):
        s, port = _occupy()
        with closing(s):
            with self.assertRaises(RuntimeError):
                net.find_free_port(port, span=1)   # only the busy port in window


class TestPortCLI(unittest.TestCase):
    def setUp(self):
        self.parser = orchestrator.build_parser()

    def test_routes_to_handler(self):
        args = self.parser.parse_args(["port", "8123", "--span", "10", "-q"])
        self.assertEqual(args.fn.__name__, "cmd_port")
        self.assertEqual(args.preferred, 8123)
        self.assertEqual(args.span, 10)
        self.assertTrue(args.quiet)

    def test_defaults(self):
        args = self.parser.parse_args(["port"])
        self.assertEqual(args.preferred, 8000)
        self.assertEqual(args.host, "127.0.0.1")
        self.assertFalse(args.quiet)

    def _run(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = orchestrator.main(argv)
        return rc, buf.getvalue()

    def test_quiet_prints_only_free_number(self):
        s, port = _occupy()
        s.close()
        rc, out = self._run(["port", str(port), "-q"])
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), str(port))

    def test_busy_preferred_reports_free_alternative(self):
        s, port = _occupy()
        with closing(s):
            rc, out = self._run(["port", str(port), "-q"])
            self.assertEqual(rc, 0)
            self.assertNotEqual(out.strip(), str(port))
            self.assertTrue(net.is_port_free(int(out.strip())))

    def test_verbose_banner_mentions_localhost(self):
        s, port = _occupy()
        s.close()
        rc, out = self._run(["port", str(port)])
        self.assertEqual(rc, 0)
        self.assertIn("http://localhost:", out)


if __name__ == "__main__":
    unittest.main()
