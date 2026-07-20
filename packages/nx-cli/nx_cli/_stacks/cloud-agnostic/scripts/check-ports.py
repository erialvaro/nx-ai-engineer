#!/usr/bin/env python3
"""Pre-flight port check for {{project_title}}.

Before `make up` binds the stack to http://localhost, verify the host ports it
needs are free — and suggest a free alternative for any that is busy (a stale
container, another dev server). Advisory only: it never fails the build, it just
tells you which port to set in `.env`. Stdlib-only; no nxai dependency required.
"""
import os
import socket
import sys

HOST = "127.0.0.1"
DEFAULTS = {"BACKEND_PORT": {{backend_port}}, "FRONTEND_PORT": {{frontend_port}}}


def is_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, port))
            return True
        except OSError:
            return False


def suggest(port):
    for candidate in range(port + 1, min(port + 100, 65536)):
        if is_free(candidate):
            return candidate
    return None


def main():
    busy = False
    for var, default in DEFAULTS.items():
        try:
            port = int(os.environ.get(var, default))
        except ValueError:
            port = default
        if is_free(port):
            print(f"  [ok]   {var}={port} is free")
        else:
            busy = True
            alt = suggest(port)
            hint = f"  ->  set {var}={alt} in .env" if alt else ""
            print(f"  [busy] {var}={port} is in use{hint}")
    if busy:
        print("\n  A port is taken. Pick a free one in .env before `make up`.")
    return 0  # advisory: never block the build


if __name__ == "__main__":
    sys.exit(main())
