# Repository Guidelines

The following conventions apply when working in this repository:

- **Verify Dockerfiles**: Always run `docker compose build` before committing to ensure Dockerfiles build correctly.
- **Railway config vs. Workflow**: Keep `railway.toml` and `.github/workflows/railway.yml` in sync. Updates to one should be reflected in the other.
- **Commit messages**: Follow any commit message conventions defined by the project (for example, the conventional commit style).
