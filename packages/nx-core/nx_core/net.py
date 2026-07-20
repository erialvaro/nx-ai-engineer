"""Local TCP port helpers — stdlib-only.

Before a project is brought up on ``http://localhost`` the port it wants may
already be taken (another dev server, a stale container). These helpers check a
port and find the next bindable one, so ``nxai port`` and dev tooling can pick a
port that will actually start instead of failing at bind time. Pure ``socket``;
no third-party dependency (the platform stays stdlib-only).
"""
from __future__ import annotations

import socket

LOCALHOST = "127.0.0.1"
_MAX_PORT = 65535


def is_port_free(port: int, host: str = LOCALHOST) -> bool:
    """True if a fresh TCP listener can bind ``host:port`` right now.

    Binds and immediately closes a probe socket: a busy port (something already
    listening) makes ``bind`` fail with ``OSError`` -> ``False``. Ports outside
    ``1..65535`` are never free."""
    if not 0 < port <= _MAX_PORT:
        return False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind((host, port))
            return True
        except OSError:
            return False


def find_free_port(preferred: int = 8000, host: str = LOCALHOST, *,
                   span: int = 100) -> int:
    """Return ``preferred`` if free, else the next free port scanning upward.

    Scans ``preferred, preferred+1, ... preferred+span-1`` (clamped to the valid
    range) and returns the first bindable one. Raises ``RuntimeError`` if every
    candidate in the window is busy."""
    start = max(1, preferred)
    end = min(start + max(1, span), _MAX_PORT + 1)
    for port in range(start, end):
        if is_port_free(port, host):
            return port
    raise RuntimeError(f"no free port in [{start}, {end}) on {host}")
