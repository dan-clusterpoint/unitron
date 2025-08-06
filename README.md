# 🟠 Unitron – Autonomous Pre-Sales Assistant

## Why “local-first”?
* Every contributor should `git clone`, install dependencies, and immediately see `/health` = **OK**.
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
pip install -r requirements.txt
uvicorn main:app
open http://localhost:8000/docs
# Create a .env file for secrets (required variables shown)
# OPENAI_API_KEY=your-openai-key
```

The unified FastAPI app lives in `main.py` and can be started with `uvicorn`
as shown above.  A small `app.py` module re-exports the `app` object for
platforms that expect that filename.  The optional property lookup service
remains in `services/property` and is contacted via the `PROPERTY_URL`
environment variable (default `http://property:8000`).

To try the minimal web interface, start the API and open `interface/index.html`
in a browser served from the same origin. The page contains a simple URL field
and technology picker that POSTs to the `/generate` endpoint. You can also
build and run a tiny container to host the page:

```bash
docker build -t interface-image ./interface
docker run --rm -p 8080:80 interface-image
```

Set `UI_ORIGIN` to the domain where the frontend is served so the backend will
allow cross-origin requests when the page is hosted separately.

### Runtime behaviour

Each FastAPI service reuses a single shared `httpx.AsyncClient` for outbound
requests. When downstream calls fail or time out, the APIs still return any
partial data with a `degraded` flag so clients can detect limited results.

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
