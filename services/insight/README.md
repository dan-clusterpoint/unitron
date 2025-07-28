# Insight Researcher Service

This service calls the OpenAI API to generate short research reports and summary insights.
It runs at `http://localhost:8083` when using Docker Compose.

## Endpoints

- `GET /health` – liveness probe returning `{ "status": "ok" }`.
- `GET /ready` – always returns `{ "ready": true }`.
- `POST /generate-insights` – body `{ "text": "notes" }` returns `{ "insight": "..." }`.
- `POST /research` – body `{ "topic": "AI" }` returns `{ "summary": "..." }`.
- `POST /postprocess-report` – body `{ "report": {...} }` returns the same report
  plus base64-encoded downloads.
- `GET /metrics` – usage counters for requests and data gaps.

## Environment variables

- `OPENAI_API_KEY` – required key for the OpenAI client.
- `OPENAI_MODEL` – chat model name (default `gpt-4`).
- `MACRO_SECTION_CAP` – maximum number of macro sections returned by `/research`.

## Example usage

```bash
curl -X POST http://localhost:8083/research \
  -H 'Content-Type: application/json' \
  -d '{"topic": "latest AI trends"}'
```

Expected response snippet:

```json
{
  "summary": "..."
}
```
