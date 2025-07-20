# Property Analyzer Service

The property service verifies DNS for a target domain. It exposes two endpoints:

- `GET /health` – liveness probe returning `{ "status": "ok" }`.
- `POST /analyze` – body `{ "domain": "example.com" }` returns JSON with
  `domains`, `confidence`, and `notes`.

Example request using `curl`:

```bash
curl -X POST http://localhost:8082/analyze \
  -H 'Content-Type: application/json' \
  -d '{"domain": "example.com"}'
```

Run this service locally via Docker Compose or by setting `SERVICE=property` and executing `uvicorn app:app`.
