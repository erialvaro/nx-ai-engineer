# Rules — Redis

Enforceable rules. The Database Reviewer blocks a change that violates these; the Engineering Contract surfaces them to the agent.

- Model by access pattern (key design).
- Always set TTLs for ephemeral data.
- Bound collection sizes; watch memory.
- Never use Redis as the system of record without durability.
