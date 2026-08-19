# Tunnel-me — Agent Instructions

## Container-first policy (mandatory)

When installing or deploying any application or service on Iran (`2.144.13.219`) or Germany (`91.108.242.106`) servers:

1. **Always use Docker containers** — never install apps directly on the host (no apt packages for services, no systemd app units).
2. Use `docker compose` under `/opt/<service>/` with config mounted as volumes.
3. Keep compose files and configs in this repo under `configs/`.
4. Only Docker Engine, SSH, and base firewall may live on the host.
5. To rollback: `docker compose down` and optionally remove the container/volume.

## Servers

- **Iran** (client): Xray client, registry tunnel, Iranian Docker mirrors
- **Germany** (server): Xray server, Docker Registry

See `docs/servers.md` and `docs/conventions.md`.

## Secrets

Never commit passwords or keys. Use `secrets/.env` locally (gitignored).
