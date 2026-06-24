#!/usr/bin/env sh
# Block until host:port accepts TCP. Portable: uses Python (present in the
# backend image) instead of bash's /dev/tcp, so it works under sh/dash too.
# Usage: ./scripts/wait-for.sh <host> <port> [timeout_seconds]
set -e
host="$1"; port="$2"; timeout="${3:-30}"

python3 - "$host" "$port" "$timeout" <<'PY'
import socket, sys, time
host, port, timeout = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
deadline = time.time() + timeout
while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"[wait-for] {host}:{port} is up")
            sys.exit(0)
    except OSError:
        time.sleep(1)
print(f"[wait-for] timeout waiting for {host}:{port}", file=sys.stderr)
sys.exit(1)
PY
