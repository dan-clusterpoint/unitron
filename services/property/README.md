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

Run this service locally via Docker Compose or by executing `uvicorn services.property.app:app`.

All Python APIs build from the `Dockerfile` at the repository root with the
repository root as the context. Set the `SERVICE` build argument to `property`
(Docker Compose handles this) and the container will start `services.property.app`.
The Dockerfile defines a healthcheck that queries `/health` by default.

The gateway aggregates this DNS check with martech analysis. Send
`POST /analyze` to the gateway with `{ "url": "https://example.com" }`
for combined results. The gateway respects `MARTECH_URL` and `PROPERTY_URL`
environment variables and optionally exposes `/metrics` for call stats.

