# ADR-0001 — Cloud-Agnostic, Docker-First Foundation

- **Status:** Accepted
- **Context:** {{project_title}} must run locally and in production on any of
  GCP, Azure, AWS, Oracle Cloud, a VPS, a dedicated server, Kubernetes or Docker
  Swarm — without rewrites and without lock-in.

## Decision

All infrastructure is expressed as **Docker Compose** with a portable base
(`docker-compose.yml`) plus environment overlays (`.override.yml` for dev,
`.prod.yml` for production). No component may depend on a proprietary cloud
service. All configuration is supplied through **environment variables**
(Twelve-Factor). The application tier is **stateless**; the only state lives in
an external database.

## Consequences

- ➕ The same artifacts run anywhere; migration between providers is a deploy
  concern, not a code change.
- ➕ Local/prod parity; trivial onboarding (`make up`).
- ➖ Provider-managed conveniences (e.g. native queues) are not used by default;
  add them as **optional, swappable adapters** behind an interface if needed.
- Verified continuously by `nxai platform-audit` (Cloud-Agnostic dimension).
