# Repository Standards — Engineering Pack

_Domain: **repo-standards**_

Open-source repository standards: governance files, CI/CD, issue/PR templates, security policy and a conventional structure. Applied with `nxai scaffold`.

## What this pack provides
- **Policies / checklists / patterns** for a healthy open-source repository.
- A **`scaffold/`** set of concrete files (governance, issue/PR templates, CI per
  stack) applied to a project's repo root with **`nxai scaffold`**.

```bash
nxai scaffold --stack auto        # lay standards into this repo (idempotent)
nxai scaffold --stack python --dry-run
```

Like every pack it contains **no code and no AI** — it organizes conventions so
the model and the team apply them consistently.
