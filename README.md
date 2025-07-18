# Pre-Sales AI

> Minimal FastAPI micro-service scaffold for the Adobe pre-sales consulting workflow.

## Services

Each service lives under `services/<name>` with its own `Dockerfile` and startup
script.

| Name      | Path                | Purpose                         |
|-----------|--------------------|---------------------------------|
| `gateway` | `services/gateway` | Combines the other services and exposes a single API |
| `property`| `services/property`| Basic domain analysis service   |
| `martech` | `services/martech` | Detects marketing technology    |
| `insight-agent` | `services/insight-agent` | Generates research notes via LLM |
| `browse-runner` | `services/browse-runner` | Runs task scripts with Playwright |

Environment variables expected by the services include:

- `PROPERTY_URL` – URL for the Property service used by the gateway
- `MARTECH_URL` – URL for the Martech service used by the gateway
- `INSIGHT_AGENT_URL` – URL for the Insight Agent service used by the gateway
- `BROWSE_RUNNER_URL` – URL for the Browse Runner service used by the gateway
- `N8N_URL` – base URL for the n8n instance
- `N8N_WORKFLOW_ID` – ID of the workflow to execute (default `1`)
- `OPENAI_API_KEY` – API key for the Insight Agent service
- `PORT` – port the service listens on (set automatically by Railway)
- `S3_BUCKET` – optional AWS S3 bucket for screenshots captured by Browse Runner
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
**[http://localhost:8000/docs](http://localhost:8000/docs)**. The other
services are exposed on ports `8001` (property), `8002` (martech), `8003` (insight-agent) and `8004` (browse-runner).

## Deployment

Deployment is handled by [Railway](https://railway.app/). The `railway.toml`
file lists each service with its build context and health check. On every push
to `main`, the GitHub action in `.github/workflows/railway.yml` runs
`railwayapp/railway-deploy@v2` which builds the images and deploys them to
Railway using the project token.

