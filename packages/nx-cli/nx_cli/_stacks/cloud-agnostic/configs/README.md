# configs/

Non-secret, version-controlled configuration that isn't a plain env var
(reverse-proxy snippets, log shippers, rate-limit rules, etc.). Mount these
read-only into containers via `docker-compose.*.yml`.

Secrets never live here — those come from `.env` / your secret manager
(Twelve-Factor). This directory is for **declarative, non-sensitive** config so
the platform stays cloud-agnostic and reproducible across environments.
