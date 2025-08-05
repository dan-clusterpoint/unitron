# 🟠 Unitron – Autonomous Pre-Sales Assistant

## Why “local-first”?
* Every contributor should `git clone`, `docker compose up`, and immediately see `/health` = **OK**.
* Builds are deterministic: no hidden network I/O during image build.
* External infra (Postgres, S3, Redis) are **optional adapters** behind ENV flags.

Explore a hosted demo at [unitron-production.up.railway.app](https://unitron-production.up.railway.app).

```
┌ Insight Card ────────────────┐
│ ▸ Action ...                 │
│ Personas: [Avatar] ...       │
│ Evidence ▼                   │
└──────────────────────────────┘
```

* **Actions** – next steps tailored to the prospect.
* **Personas** – avatars describing key stakeholders.
* **Evidence** – supporting notes gathered from the site.

## Quick-start
```bash
# local development
uvicorn main:app --reload
open http://localhost:8000/docs
# Create a .env file for secrets (required variables shown)
# OPENAI_API_KEY=your-openai-key
```

The unified FastAPI app lives in `main.py` and can be started with `uvicorn`
as shown above.  A small `app.py` module re-exports the `app` object for
platforms that expect that filename.  The optional property lookup service
remains in `services/property` and is contacted via the `PROPERTY_URL`
environment variable (default `http://property:8000`).

To launch the web interface during development:
```bash
cd interface && npm install && VITE_API_BASE_URL=http://localhost:8080 npm run dev
```
The `VITE_API_BASE_URL` variable should match the API address.

Set `UI_ORIGIN` to the domain where the frontend is served so the backend will
allow cross-origin requests. For a local Vite dev server this is typically
`http://localhost:5173`.
full production URL of your deployed interface.

### Runtime behaviour

Each FastAPI service reuses a single shared `httpx.AsyncClient` for outbound
requests. When downstream calls fail or time out, the APIs still return any
partial data with a `degraded` flag so clients can detect limited results.

### InsightCard component

The React interface displays each insight using a reusable **InsightCard**. This
component accepts the normalized insight payload from the backend and renders
the evidence, recommended actions and any personas in a single card. The
analyzer captures optional **Industry**, **Pain Point**, and declared
**Technology Stack** details that are passed along with the URL. Markdown
fragments are styled via the Tailwind Typography plugin so the text appears
nicely formatted, and an **Export Markdown** button lets users download the
analysis.


### API endpoints
The unified API exposes three primary endpoints:

* `GET /health` – liveness probe.
* `POST /analyze` – return property information for the supplied URL. The current implementation performs a simple lookup and returns any data from the optional property service.
* `POST /generate` – merge detected and manually supplied martech data. The endpoint returns the combined list alongside any CMS values.

Example:
```bash
curl -sS -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}' | jq
```
