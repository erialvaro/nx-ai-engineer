# Example 6 — Integrate a new project (under 5 minutes)

AIES installs into any repository as a single `.ai-project/` folder.

## 1. Install (idempotent)
```bash
nxai init
```
This copies the framework template into `<project>/.ai-project/` and seeds
`config.json`. Re-running is safe — it never clobbers your config/brain/tasks.

## 2. Audit (always first — discovers your stack, no assumptions)
```bash
cd /path/to/your/project
nxai audit
```

## 3. Configure invariants (optional)
Edit `.ai-project/config.json`:
```json
{
  "domain_rules": ["Never read or write another tenant's data", "Never log PII"],
  "protected_paths": ["**/billing/**"]
}
```

## 4. Use it
```bash
# Decide how to approach a goal:
nxai decide "Add OAuth login"

# Run the full pipeline (safe by default — nothing is changed):
nxai pipeline "Add OAuth login" --mode dry_run

# Real execution via Claude Code, concurrent workers:
nxai pipeline "Add OAuth login" \
    --mode execute --adapter claude-code --workers 4
```

## 5. See what it learned
```bash
nxai insights
nxai recommend "Add OAuth logout"
```

## Requirements
- Python 3.8+ (no third-party packages).
- git (optional — needed for worktrees and diff review).
