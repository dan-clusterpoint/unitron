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

The gateway aggregates this DNS check with martech analysis. Send
`POST /analyze` to the gateway with `{ "url": "https://example.com" }`
for combined results. The gateway respects `MARTECH_URL` and `PROPERTY_URL`
environment variables and optionally exposes `/metrics` for call stats.

