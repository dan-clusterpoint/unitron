## Vision
Unitron automatically reverse-engineers a prospect’s website, generates synthetic buyer personas, crafts tailored demo flows, and surfaces “next-best-action” insights for Sales Engineers.

## Personas
| Persona | Goal | Core Metric | Key Objection |
|---------|------|-------------|---------------|
| ⚡ **The Speed Runner** | Build a POC in 10 min | Time-to-first-demo | “Too many steps” |
| 🤔 **The Analyst** | Deep tech audit | Thoroughness score | “Opaque analysis” |
| 🤝 **The SE** | Deliver wow demo | Close-rate | “No tailored story” |

*(extend as needed…)*

### Build stability philosophy
We believe reliability starts with deterministic builds. Docker images for both services install dependencies from `requirements.txt` with no network calls after the initial dependency fetch. Health checks ensure that Railway deploys never wait more than a few seconds for readiness.

Developers are encouraged to extend the services but should preserve the quick startup time and the clean separation between gateway orchestration and martech analysis logic. Unit tests in `tests/` serve as living documentation and prevent regressions.
