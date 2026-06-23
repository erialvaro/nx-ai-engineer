# Context — Containers / Docker

Build minimal, non-root, multi-stage images with no secrets baked in, and scan them.

## Non-negotiables
- Use a minimal, pinned base image; multi-stage builds.
- Run as a non-root user; drop capabilities.
- Never bake secrets into the image or layers.
- Add a healthcheck; set resource limits.
- Scan images for vulnerabilities in CI.

## Always verify
- Minimal pinned base
- Runs non-root
- No secrets in image
- Healthcheck + limits
- Image scanned in CI
