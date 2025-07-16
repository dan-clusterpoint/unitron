# Pre-Sales AI

> Minimal FastAPI micro-service scaffold for the Adobe pre-sales consulting workflow.

## Quickstart

Build and test each service locally with the smoke script. It builds the Docker
image, launches it on a random port and performs a few basic requests.

```bash
./scripts/smoke.sh all
```

You can also run a single service:

```bash
./scripts/smoke.sh gateway
```

Each service exposes `/health` and `/docs` on the port specified by the `PORT`
environment variable. Example manual run:

```bash
export MARTECH_URL=http://localhost:8002
docker build -t unitron_gateway services/gateway
docker run -p 8000:8000 -e PORT=8000 -e MARTECH_URL=$MARTECH_URL unitron_gateway
curl -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"property":{"domain":"example.com"},"martech":{"url":"https://example.com"}}'
```

### Gateway Service

The gateway calls the Martech service via the `MARTECH_URL` environment
variable (default `http://localhost:8000`). Gateway modules are packaged in
`services/gateway/gateway` and use relative imports so the container can build
from that directory.

## Deployment

Push to `main`; Railway reads `railway.toml`, builds each service, and deploys.

