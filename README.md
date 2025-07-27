# 🟠 Unitron – Autonomous Pre-Sales Assistant

## Why “local-first”?
* Every contributor should `git clone`, `docker compose up`, and immediately see `/health` = **OK**.
* Builds are deterministic: no hidden network I/O during image build.
* External infra (Postgres, S3, Redis) are **optional adapters** behind ENV flags.

## Quick-start
```bash
# local dev
docker compose up --build
# gateway -> http://localhost:8080
# martech -> http://localhost:8081
# property -> http://localhost:8082
open http://localhost:8080/docs
# Compose passes `SERVICE` so `docker/python.Dockerfile` starts the correct FastAPI app
# MARTECH_URL and PROPERTY_URL control where the gateway proxies requests
```

All Python APIs build from `docker/python.Dockerfile`. The `SERVICE` environment
variable selects which module to run and `ops/entrypoint.sh` validates imports
before starting Uvicorn. Health checks hit `/health` by default. Docker Compose
passes this variable automatically for each service.

To launch the web interface during development:
```bash
cd interface && npm install && VITE_API_BASE_URL=http://localhost:8080 npm run dev
```
The `VITE_API_BASE_URL` variable should match the gateway address.

Set `UI_ORIGIN` to the domain where the frontend is served so the backend will
allow cross-origin requests. For a local Vite dev server this is typically
`http://localhost:5173`.

### Full-stack with Docker Compose

Run all services including the React interface:

```bash
docker compose --profile ui up --build
```


The `ui` profile builds the `interface` service defined in `docker-compose.yml`.
When omitted, the gateway, martech, and property APIs run without the frontend.
The interface reads the `VITE_API_BASE_URL` variable to reach the gateway (default `http://localhost:8080`).
Running `docker compose --profile ui up` sets this variable automatically so the frontend talks to the locally exposed gateway on port 8080.

### Frontend build variable

The React interface must be compiled with `VITE_API_BASE_URL` pointing at the
gateway. Running `docker compose --profile ui up --build` now forwards this
variable automatically so the baked-in API endpoint matches the running
services.

### Cross-origin requests

All backend services read `UI_ORIGIN` to decide which frontend domain may make
requests. Set this to `http://localhost:5173` during local development or to the
full production URL of your deployed interface.

### Gateway service
The gateway orchestrates the other APIs. Key endpoints:

* `GET /health` – liveness probe.
* `GET /ready` – checks that downstream services are healthy.
* `GET /metrics` – optional stats about service calls.
* `POST /analyze` – body `{"url": "https://example.com", "headless": false, "force": false}` returns:
  `{"property": {...}, "martech": {...}}`.
* `POST /generate` – body `{"url": "https://example.com", "martech": {...}, "cms": [], "cms_manual": "WordPress"}` returns generated personas and demo flow.

`MARTECH_URL` and `PROPERTY_URL` configure the upstream URLs used by the gateway.

Example:

```bash
curl -X POST http://localhost:8080/analyze \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com"}'
```

Example (generate with manual CMS):

```bash
curl -X POST http://localhost:8080/generate \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com", "martech": {}, "cms": [], "cms_manual": "WordPress"}'
```

### Martech analyzer service
The martech service exposes several endpoints:

* `GET /health` – liveness probe.
* `GET /ready` – returns `{"ready": true}` once the fingerprint list is loaded.
* `GET /diagnose` – checks outbound connectivity.
* `POST /analyze` – body `{"url": "https://example.com", "debug": false, "headless": false, "force": false}` returns
  detected marketing vendors grouped into four buckets. When `debug=true` the
  response includes detection evidence for each vendor. Set `headless=true` to
  allow a deeper crawl using a headless browser. Pass `force=true` to bypass the
  in-memory cache and refresh the analysis immediately.
* `POST /generate` – body `{"url": "https://example.com", "martech": {...}, "cms": [], "cms_manual": "WordPress"}` returns generated personas and demo suggestions.
* `GET /fingerprints` – returns the loaded fingerprint definitions. When
  `debug=true` the service runs detection on a sample page and reports which
  evidence types triggered for each vendor. Results are cached so repeated calls
  are instant.

If the fingerprint files cannot be loaded at startup, the analyzer still boots
with empty vendor lists. Analytics and CMS detection will then return no
matches, but the API endpoints continue to respond with HTTP 200.

If fetching the page fails, the service falls back to analyzing just the URL.
Results are still returned but include a `"network_error"` indicator set to
`true`.

Example:

```bash
curl -X POST http://localhost:8081/analyze \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com", "debug": true}'
```

```bash
curl -X POST http://localhost:8081/generate \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com", "martech": {}, "cms": [], "cms_manual": "WordPress"}'
```

Fingerprint definitions live in `fingerprints.yaml`. A separate
`cms_fingerprints.yaml` catalogs detection rules for common CMS platforms such as
WordPress, AEM and Shopify. When you call `POST /analyze` the response now
includes a `cms` object grouped by category. Edit these files and restart the
service to update the vendor lists.

Detections use an **additive scoring** model. Each matcher contributes its
assigned weight to a vendor's score; once the cumulative score meets the vendor
threshold (default is 1) the vendor is reported with confidence capped at 1.0.

CMS output example:

```bash
curl -s -X POST http://localhost:8081/analyze \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://wordpress.com"}'
# {
#   "core": {...},
#   "cms": {"oss_cms": {"WordPress": {"confidence": 1.0}}},
#   "network_error": false
# }
```

### CMS detection

The analyzer detects popular content management systems alongside martech
vendors. Definitions live in `cms_fingerprints.yaml`. When analyzing a URL the
response includes a `cms` object grouping detected systems by category.

If outbound HTTP access must go through a proxy, export `HTTP_PROXY` and
`HTTPS_PROXY` or set `OUTBOUND_HTTP_PROXY` to override both. The compose file
shows example values for local testing. On Railway, define these variables under
the **Variables** tab for the `martech` service.

Set `ENABLE_WAPPALYZER=1` to include technology detections from
python‑wappalyzer. It is disabled by default to keep startup fast.

### Manual CMS input

The `/generate` endpoint lets you provide a `cms_manual` string when the
analyzer cannot detect a CMS. The gateway forwards this value to the martech
service so personas can still reference a specific platform.

The React interface exposes a dropdown for this field only when the analysis
returns an empty CMS list.

Example request:

```bash
curl -X POST http://localhost:8080/generate \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://example.com", "martech": {}, "cms": [], "cms_manual": "Drupal"}'
```

Set `CMS_MANUAL_LOG_PATH` to a file path to record submitted `cms_manual`
values. Reviewing these logs helps refine `cms_fingerprints.yaml` with real
world platforms not yet covered by automated detection.

## Deployment

* GitHub Actions installs dependencies from `pyproject.toml` and runs our test
  suite on every push.
* Railway auto-detects the project with Nixpacks and runs each service with the
  same start command used locally.
* Health-checks: `/health` = liveness; `/ready` = readiness.

## Build-stability contract 🔒

1. Zero network calls in `docker/python.Dockerfile`.
2. `uvicorn services.gateway.app:app` **must start < 2 s** locally and on Railway.
3. CI blocks merges if lint/type/test fail.

## Architecture overview
Unitron is composed of three lightweight FastAPI services: **gateway**, **martech**, and **property**. The gateway acts as the entrypoint and orchestrator. The martech service performs analysis and persona generation, while the property service verifies domain ownership via DNS lookups.

The `docker-compose.yml` file wires them together with sensible defaults for local development. No external databases are required; an in-memory SQLite URL is the default for the martech component. Contributors may swap in Postgres or S3 simply by exporting `DB_URL` or other environment variables.

### Local dev loops
1. Clone the repo.
2. Run `docker compose up --build`.
3. Watch the logs for all services to report `Uvicorn running` within two seconds.
4. Navigate to `http://localhost:8080/docs` for API docs.

### Reliability principles
- The single Dockerfile (`docker/python.Dockerfile`) copies only local files and never reaches out to the internet during build.
- Health checks for Railway and Compose are identical so behaviour matches across environments.
- CI must pass flake8, mypy, and pytest before Docker images are built or published.

### Contributing
We encourage small PRs that keep the local build fast and stable. Use the `Makefile` shortcuts for common tasks. The devcontainer ensures a consistent Python and Node toolchain and editor setup.

## Testing
Run the automated checks with:

```bash
make lint
make test
```

To verify that the gateway service is reachable, export `GATEWAY_URL` and execute:

```bash
GATEWAY_URL=http://localhost:8080 ./test-gateway.sh
```

## FAQ

**Why Docker instead of running Python directly?**
We want all contributors to share the same environment. Docker ensures Python version and dependencies are identical across machines without polluting host systems.

**Can I use Postgres locally?**
Yes. Set `DB_URL=postgresql://user:pass@localhost/db` before running Compose. The martech service will use it instead of SQLite.

**Where do I put new features?**
Start in `src/martech` for analysis-related functions. If it’s a new API endpoint, you may mount it through `gateway` so all external traffic goes through one ingress point.

**How do I run just one service?**
`docker compose run --service-ports gateway` or `martech` as needed.

**Is there a devcontainer?**
Yes. Visual Studio Code will prompt to reopen in container, giving you a ready-to-go Python and Node environment with our tools pre-installed.

**What if I see a build error?**
Run `make lint` and `make test` to ensure your environment passes checks. If issues persist, ensure your Docker daemon has access to network for dependency downloads during the first build.

Happy hacking!

### Proxy & Connectivity
Set a proxy for outbound HTTP traffic if needed:

```bash
export OUTBOUND_HTTP_PROXY="http://my-proxy:3128"
```

Use `GET /diagnose` to verify that the service can reach the internet.
Successful example response: `{"success": true}`.
On failure it returns `{"success": false, "error": "..."}`.

