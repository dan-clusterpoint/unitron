# Property Analyzer Service

The property service verifies DNS for a target domain. It exposes three endpoints:

- `GET /health` – liveness probe returning `{ "status": "ok" }`.
- `GET /ready` – readiness probe returning `{ "ready": true }`.
- `POST /analyze` – body `{ "domain": "example.com" }` returns JSON with
  `domains`, `confidence`, and `notes`.

Example request using `curl`:

```bash
curl -X POST http://localhost:8082/analyze \
  -H 'Content-Type: application/json' \
  -d '{"domain": "example.com"}'
```

Run this service locally via Docker Compose or by executing `uvicorn property.app:app`.

The `Dockerfile` expects the repository root as the build context. It copies the shared
`requirements.txt` before installing dependencies and then adds the service code.
Railway builds this service from the repository root (`projectPath = "."` in `railway.toml`),
so no special build arguments are needed.

The gateway aggregates this DNS check with martech analysis. Send
`POST /analyze` to the gateway with `{ "url": "https://example.com" }`
for combined results. The gateway respects `MARTECH_URL` and `PROPERTY_URL`
environment variables and optionally exposes `/metrics` for call stats.

