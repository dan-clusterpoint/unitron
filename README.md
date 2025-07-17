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

Environment variables expected by the services include:

- `PROPERTY_URL` – URL for the Property service used by the gateway
- `MARTECH_URL` – URL for the Martech service used by the gateway
- `PORT` – port the service listens on (set automatically by Railway)
- `PGUSER`, `PGPASSWORD`, `PGDATABASE`, `PGHOST` – optional database settings
- `RAILWAY_ENVIRONMENT` – automatically provided during deploy but unused by the Dockerfiles

## Quick Start (Local)

```bash
docker compose up --build
```

The gateway API will be available at
**[http://localhost:8000/docs](http://localhost:8000/docs)**. The other
services are exposed on ports `8001` (property) and `8002` (martech).

## Deployment

Deployment is handled by [Railway](https://railway.app/). The `railway.toml`
file lists each service with its build context and health check. On every push
to `main`, the GitHub action in `.github/workflows/railway.yml` runs
`railwayapp/railway-deploy@v2` which builds the images and deploys them to
Railway using the project token.

