# Pre-Sales AI

> Minimal FastAPI micro-service scaffold for the Adobe pre-sales consulting workflow.

## Services

Each service lives under `services/<name>` with its own `Dockerfile` and startup
script.

| Name      | Path                | Purpose                         |
|-----------|--------------------|---------------------------------|
| `gateway` | `services/gateway` | Main API entrypoint             |
| `martech` | `services/martech` | Detects marketing technology    |


Environment variables expected by the services include:

- `MARTECH_URL` – URL for the Martech service used by the gateway
- `N8N_URL` – base URL for the n8n instance
- `N8N_WORKFLOW_ID` – ID of the workflow to execute (default `1`)
- `PORT` – port the service listens on (set automatically by Railway)
- `PGUSER` – optional PostgreSQL user
- `PGPASSWORD` – optional PostgreSQL password
- `PGDATABASE` – optional PostgreSQL database name
- `PGHOST` – optional PostgreSQL host
- `RAILWAY_ENVIRONMENT` – automatically provided during deploy but unused by the Dockerfiles

The gateway's `/health` endpoint simply returns `{"status": "ok"}` as a liveness probe. Use `/ready` to check downstream services and obtain a consolidated status.

## Quick Start (Local)

```bash
docker compose up --build
```

The gateway API will be available at
**[http://localhost:8000/docs](http://localhost:8000/docs)**. The martech service is exposed on port `8001`.

## Deployment

Deployment is handled by [Railway](https://railway.app/). The `railway.toml`
file defines two services, `unitron` and `martech`, each built from its
directory under `services/`. On every push to `main`, the workflow in
`.github/workflows/railway.yml` deploys both services with
`railwayapp/railway-deploy@v2`.

Both services run in **service mode**, so Railway keeps the containers
running and performs repeated health checks instead of treating them as
one-off jobs.

