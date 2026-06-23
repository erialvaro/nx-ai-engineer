# Example 1 — Create an agent

An agent is defined by (a) a human/Claude-facing spec and (b) a machine-routable
entry (globs/keywords). Two ways:

## A. Via config (no code) — recommended
Edit `.ai-project/config.json`:
```json
{
  "extra_agents": {
    "pentester": {
      "title": "Pentester",
      "role": "Finds vulnerabilities in changed code.",
      "keywords": ["pentest", "vulnerability", "exploit"],
      "route_globs": ["**/security/**", "**/*auth*.*"],
      "forbidden_globs": ["**/*.sql"],
      "read_only": false
    }
  }
}
```
Then add a spec at `.ai-project/agents/pentester.md` (copy `_TEMPLATE.md`).
The Dispatcher/Decision Engine will now consider `pentester` for relevant goals:
```bash
nxai decide "Pentest the OAuth flow"
```

## B. Via the SDK (at runtime)
```python
import nx_sdk as sdk
sdk.register_agent("pentester", {
    "title": "Pentester", "keywords": ["pentest", "vulnerability"],
    "route_globs": ["**/security/**"], "read_only": False,
})
```

## Verify
```bash
nxai dispatch "Find vulnerabilities in auth"
# 'pentester' appears in Selected when keywords match.
```
