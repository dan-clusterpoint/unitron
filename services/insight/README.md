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
- `POST /insight-and-personas` – body `{ "url": "https://example.com", "martech": {...}, "cms": [], "cms_manual": "WordPress" }`
  returns { "insight": {"actions": [...], "evidence": "..."}, "personas": [{"id": "P1"}], "cms_manual": "WordPress", "degraded": false }. Insight and persona prompts run concurrently. The gateway will return a timeout after 20s if the insight service is slow.
- `GET /metrics` – usage counters for requests and data gaps.

## Environment variables

- `OPENAI_API_KEY` – required key for the OpenAI client.
- `OPENAI_MODEL` – chat model name (default `gpt-4`).
- `MACRO_SECTION_CAP` – maximum number of macro sections returned by `/research`.

### Normalized insight schema

The insight service replies with an object containing an `insight` field. This
field follows a consistent shape regardless of prompt details:

```json
{
  "evidence": "short summary text",
  "actions": [
    {"id": "1", "title": "Action", "reasoning": "why", "benefit": "result"}
  ],
  "personas": [
    {"id": "P1", "name": "Buyer"}
  ],
  "degraded": false
}
```

Additional keys may be included but these core fields are always present. The
frontend's `InsightCard` component expects this structure.

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

Example (insight and personas):

```bash
curl -X POST http://localhost:8083/insight-and-personas \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com", "martech": {}, "cms": [], "cms_manual": "WordPress"}'
```

Expected response snippet:

```json
{
  "insight": { "actions": [], "evidence": "..." },
  "personas": [{"id": "P1"}],
  "cms_manual": "WordPress",
  "degraded": false
}
```
