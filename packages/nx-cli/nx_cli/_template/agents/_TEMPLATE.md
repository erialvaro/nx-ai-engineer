# Agent: <Name>

> Copy this file to create a new agent. Keep every section. Register the agent's
> machine-routable globs/keywords in `tools/aies/agents.py` (or via
> `config.json > extra_agents`) so the planner and locks know what it owns.

## Mission
One sentence: what this agent is uniquely responsible for.

## Responsibilities
- …

## Scope — allowed paths
- `path/glob/**`

## Scope — forbidden paths
- `other/area/**` (owned by another agent)

## Quality criteria
- …

## Checklist (run before handing off)
- [ ] Re-read `PROJECT_RULES.md` and this spec
- [ ] No forbidden path touched
- [ ] Tests added/updated and passing
- [ ] Change documented

## Best practices
- …

## Interfaces
- **Depends on:** <agents>
- **Hands off to:** <agents>
