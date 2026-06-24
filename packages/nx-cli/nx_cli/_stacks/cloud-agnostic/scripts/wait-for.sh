#!/usr/bin/env sh
# Block until host:port accepts TCP — portable (no nc dependency assumed).
# Usage: ./scripts/wait-for.sh <host> <port> [timeout_seconds]
set -e
host="$1"; port="$2"; timeout="${3:-30}"
i=0
while [ "$i" -lt "$timeout" ]; do
  if (exec 3<>"/dev/tcp/$host/$port") 2>/dev/null; then
    echo "[wait-for] $host:$port is up"
    exit 0
  fi
  i=$((i + 1)); sleep 1
done
echo "[wait-for] timeout waiting for $host:$port" >&2
exit 1
