# Cloud-Agnostic Deployment

The foundation runs identically everywhere because it is **just containers +
environment variables**. Nothing is tied to a cloud provider's proprietary API.

## The contract

- **Compute:** any Docker host runs `docker-compose.yml` + `docker-compose.prod.yml`.
- **Config:** 100% environment variables (`.env` / secret manager).
- **State:** external database only (Supabase or plain PostgreSQL). The app tier
  is stateless — scale it horizontally with `BACKEND_REPLICAS` / `FRONTEND_REPLICAS`.
- **Networking:** one bridge network; the reverse proxy / TLS terminator is
  provider-chosen (Nginx, Caddy, a cloud LB) and injected at the edge.

## Per-target notes

| Target           | How                                                            |
|------------------|---------------------------------------------------------------|
| Local / Docker   | `make up`                                                     |
| VPS / Dedicated  | `make prod` behind Nginx/Caddy + your TLS                    |
| Docker Swarm     | `docker stack deploy -c docker-compose.yml -c docker-compose.prod.yml` |
| GCP / Azure / AWS / Oracle | push images to the registry; run on their container service with the same env |
| Kubernetes       | `kompose convert`, or author manifests from the same images/env |

## Rule of thumb

If a change would only work on one provider, it does not belong in this
foundation. Keep provider specifics at the **edge** (DNS, TLS, LB, secret
store) — never in application code.
