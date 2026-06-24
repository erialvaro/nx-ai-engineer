# Context — Redis

Engineering standard for Redis. Key-value/structure modeling on Redis: access patterns, TTL, memory.

## Non-negotiables
- Model by access pattern (key design).
- Always set TTLs for ephemeral data.
- Bound collection sizes; watch memory.
- Never use Redis as the system of record without durability.

## Always verify
- Key naming convention
- TTL set
- Memory bounded
- Persistence configured
- No blocking commands in hot path
