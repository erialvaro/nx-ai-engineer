# Environments

Per-environment configuration **examples** (Twelve-Factor: config is env, not code).
Copy the one you need into the project root `.env` (or load it in your
orchestrator / CI secret store). **Never commit real secrets** — the `.env`
variants here are templates only.

| File                         | Use                                  |
|------------------------------|--------------------------------------|
| `development.env.example`    | local Docker dev                     |
| `staging.env.example`        | pre-production                       |
| `production.env.example`     | production (inject secrets at deploy)|

```bash
cp environments/production.env.example .env   # then fill real values via your secret manager
```
