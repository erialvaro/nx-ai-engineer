# Policies — Containers / Docker

Enforceable rules for this domain. Agents must respect these; reviewers must check them.

- Use a minimal, pinned base image; multi-stage builds.
- Run as a non-root user; drop capabilities.
- Never bake secrets into the image or layers.
- Add a healthcheck; set resource limits.
- Scan images for vulnerabilities in CI.
