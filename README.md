# 🟠 Unitron – Autonomous Pre-Sales Assistant

## Why “local-first”?
* Every contributor should `git clone`, `docker compose up`, and immediately see `/health` = **OK**.
* Builds are deterministic: no hidden network I/O during image build.
* External infra (Postgres, S3, Redis) are **optional adapters** behind ENV flags.

## Quick-start
```bash
# local dev
docker compose up --build
# each container runs `uvicorn app:app`
open http://localhost:8080/docs
# SERVICE env var selects gateway (default) or martech
```
To launch the web interface during development:
```bash
cd interface && npm install && VITE_API_BASE_URL=http://localhost:8080 npm run dev
```

### Full-stack with Docker Compose

Run all services including the React interface:

```bash
docker compose --profile ui up --build
```

The `ui` profile builds the `interface` service defined in `docker-compose.yml`.
When omitted, only the gateway and martech APIs are started.

### Martech analyzer service
The martech service exposes three endpoints:

* `GET /health` – liveness probe.
* `GET /ready` – returns `{"ready": true}` once the fingerprint list is loaded.
* `POST /analyze` – body `{"url": "https://example.com", "debug": false}` returns
  detected marketing vendors grouped into four buckets.

Fingerprint definitions live in `fingerprints.yaml`. Edit this file and restart
the service to update the vendor list.

## Deployment

* GitHub Actions installs dependencies from `pyproject.toml` and runs our test
  suite on every push.
* Railway auto-detects the project with Nixpacks and runs each service with the
  same start command used locally.
* Health-checks: `/health` = liveness; `/ready` = readiness.

## Build-stability contract 🔒

1. Zero network calls in `Dockerfile`.
2. `uvicorn app:app` **must start < 2 s** locally and on Railway.
3. CI blocks merges if lint/type/test fail.

## Architecture overview
Unitron is composed of two lightweight FastAPI services: **gateway** and **martech**. The gateway acts as the entrypoint and orchestrator. The martech service performs analysis and persona generation.

The `docker-compose.yml` file wires them together with sensible defaults for local development. No external databases are required; an in-memory SQLite URL is the default for the martech component. Contributors may swap in Postgres or S3 simply by exporting `DB_URL` or other environment variables.

### Local dev loops
1. Clone the repo.
2. Run `docker compose up --build`.
3. Watch the logs for both services to report `Uvicorn running` within two seconds.
4. Navigate to `http://localhost:8080/docs` for API docs.

### Reliability principles
- All Dockerfiles copy only local files and never reach out to the internet during build.
- Health checks for Railway and Compose are identical so behaviour matches across environments.
- CI must pass flake8, mypy, and pytest before Docker images are built or published.

### Contributing
We encourage small PRs that keep the local build fast and stable. Use the `Makefile` shortcuts for common tasks. The devcontainer ensures a consistent Python and Node toolchain and editor setup.

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
