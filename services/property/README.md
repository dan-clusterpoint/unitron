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

Run this service locally via Docker Compose or by setting `SERVICE=property` and executing `uvicorn app:app`.

The `Dockerfile` works with either the repository root or `services/property` as the build context.
It defines a `SERVICE_PATH` build argument (default `services/property`) used in `COPY` instructions.
When building from within `services/property`, override this argument:

```bash
docker build --build-arg SERVICE_PATH=. .
```

Railway builds this service from the repository root (`projectPath = "."` in `railway.toml`), so no override is needed there.

The gateway aggregates this DNS check with martech analysis. Send
`POST /analyze` to the gateway with `{ "url": "https://example.com" }`
for combined results. The gateway respects `MARTECH_URL` and `PROPERTY_URL`
environment variables and optionally exposes `/metrics` for call stats.

