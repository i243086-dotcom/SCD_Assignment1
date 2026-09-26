# CivicPulse

Before submission, replace `<owner>/<repository>` in these badge URLs with the real GitHub repository, then verify each link after the first workflow run.

[![CI](https://github.com/<owner>/<repository>/actions/workflows/ci.yml/badge.svg)](https://github.com/<owner>/<repository>/actions/workflows/ci.yml)
[![CD](https://github.com/<owner>/<repository>/actions/workflows/cd.yml/badge.svg)](https://github.com/<owner>/<repository>/actions/workflows/cd.yml)

CivicPulse is an end-to-end municipal complaint intake, AI triage and operations platform. Citizens submit free text; a replaceable triage provider classifies category and priority, creates a one-line summary, and the backend persists the result. Operators work from a paginated dashboard and can inspect aggregate statistics, while Docker, Kubernetes and CI/CD enforce the same operational contracts used by the application.

## Architecture

```mermaid
flowchart TB
  Citizen[Citizen / Operator] -->|HTTP| Ingress[nginx / Kubernetes Ingress]
  Ingress --> Frontend[React 18 + Vite\nnginx static image]
  Ingress --> Backend[FastAPI + Pydantic]
  Frontend -->|relative /api| Backend
  Backend --> Postgres[(PostgreSQL 16)]
  Backend --> Redis[(Redis 7\nstats cache + triage cache + rate limiter)]
  Backend --> Provider{TriageProvider}
  Provider --> Groq[Groq hosted LLM]
  Provider --> Ollama[Ollama offline]
  Provider --> Rules[Rule-based fallback]
  Provider --> Sim[Simulated CI provider]
```

The frontend never joins the Docker `internal` network. Backend is the only application service bridging `edge` and `internal`; PostgreSQL and Redis are internal-only.

## Prerequisites

For the one-command laptop path: Docker Engine/Desktop with Docker Compose v2. For Kubernetes: Docker, kind, kubectl, kustomize, `envsubst`, Git and enough RAM for the cluster. Node 22 and Python 3.12 are only required when running tests outside containers.

## Clean-clone quickstart

```bash
cp .env.example .env
# keep TRIAGE_PROVIDER=simulated for a no-key demo
# optionally add GROQ_API_KEY and set TRIAGE_PROVIDER=llm

docker compose up --build
```

Open `http://localhost:8080`. Backend migrations and the idempotent seed run before the API starts; at least 30 seeded complaints are present. Stop without deleting data using `docker compose down`. `docker compose down` followed by `docker compose up` preserves PostgreSQL and Redis AOF data because named volumes remain attached.

To prove network isolation:

```bash
docker compose exec frontend ping postgres
# Expected: resolution/routing failure. A failing command is the evidence.
```

To reset all local data intentionally:

```bash
docker compose down -v
```

## Hosted AI and offline AI

The default is `TRIAGE_PROVIDER=simulated`, so a clean clone needs no external credential. Set `TRIAGE_PROVIDER=llm` with `GROQ_API_KEY` for the hosted path, `TRIAGE_PROVIDER=ollama` for the offline path, or `TRIAGE_PROVIDER=rules` for deterministic keyword classification. The LLM path requests schema-constrained JSON, validates it with Pydantic, applies a 10-second timeout, retries once only for retryable failures, and falls back to rules. See `docs/TRIAGE.md` and ADR 0004 for data-governance details.

For Ollama, preload the model into the named volume from a network-enabled container before selecting the provider:

```bash
docker run --rm -v civicpulse_ollama_models:/root/.ollama ollama/ollama:0.11.10 pull llama3.2:1b
```

## API

| Method | Path | Contract |
|---|---|---|
| POST | `/api/complaints` | Validate → triage → persist; 201, 400 field errors, 429 with `Retry-After` |
| GET | `/api/complaints/{id}` | 200 / 404 |
| GET | `/api/complaints` | category/priority/status filters; `page`, `page_size <= 100`, total |
| PATCH | `/api/complaints/{id}/status` | Explicit state machine; invalid transition returns 409 with attempted transition |
| GET | `/api/stats` | Aggregates; 30 s Redis read-through cache; `X-Cache: HIT|MISS` |
| GET | `/api/meta/providers` | Active provider + latest 20 provider outcomes |
| GET | `/health` | Liveness only; no dependency access |
| GET | `/ready` | 200 only when PostgreSQL and Redis are reachable |
| GET | `/metrics` | Prometheus text metrics |

OpenAPI is available at `http://localhost:8000/docs` and `http://localhost:8000/openapi.json` in development. The frontend client uses relative paths and a typed OpenAPI surface; regenerate it with `npm --prefix frontend run api:generate` while the backend is running.

## Status state machine

`open → in_progress → resolved`, `open → rejected`, and `in_progress → rejected`. `resolved` and `rejected` are terminal. The backend returns each complaint's `allowed_transitions`; the React UI renders those values instead of duplicating the state machine.

## Tests and quality checks

Backend:

```bash
python -m venv .venv
# activate the environment
pip install -e './backend[dev]'
cd backend
ruff check app
mypy app
pytest --cov=app --cov-fail-under=65
```

Frontend:

```bash
npm install --prefix frontend
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend test
```

Mechanical submission audit:

```bash
python scripts/check_submission.py
```

## Docker production file

`compose.prod.yaml` contains no `build:` entries and does not publish PostgreSQL or Redis ports. It deploys frontend/backend by `${IMAGE_TAG}`:

```bash
export GHCR_OWNER=your-user-or-org
export IMAGE_TAG=<commit-sha>
export POSTGRES_DB=civicpulse POSTGRES_USER=civicpulse POSTGRES_PASSWORD='<secret>'
docker compose -f compose.prod.yaml up -d
```

Do not use `latest` as the deployed tag.

## Kubernetes

Local one-command helper (creates a kind cluster, builds/loads images, installs ingress-nginx, metrics-server and VPA, applies the dev overlay, runs migrations/seed, and waits for rollouts):

```bash
make k8s
```

Then map `civicpulse.local` to `127.0.0.1` if needed and browse `http://civicpulse.local`.

Manual render:

```bash
export TRIAGE_PROVIDER=simulated
export POSTGRES_PASSWORD='local-only'
export DATABASE_URL="postgresql+psycopg://civicpulse:${POSTGRES_PASSWORD}@postgres:5432/civicpulse"
export GROQ_API_KEY=''
kustomize build k8s/overlays/dev | envsubst | kubectl apply -f -
kubectl get pods,hpa -n civicpulse
```

PostgreSQL is a StatefulSet with `volumeClaimTemplates`; Redis is a Deployment with a PVC. All Services are ClusterIP and the Ingress routes `/` to frontend and `/api` to backend.

## Autoscaling evidence

After metrics-server and VPA are installed:

```bash
kubectl get hpa -n civicpulse -w
k6 run -e BASE_URL=http://civicpulse.local load/k6-script.js
kubectl describe vpa backend-vpa -n civicpulse
```

Capture the real HPA watch, offered-load/replica data and VPA bounds under `docs/evidence/`. Do not fabricate output. See `docs/EVIDENCE-CHECKLIST.md` for the exact capture and chart commands.

## CI/CD

- `ci.yml`: PRs to `main`, pushes to `dev`; lint/type checks, backend and frontend tests, image builds, Trivy scanning, kubeconform validation and Compose smoke testing.
- `cd.yml`: push to `main`; full test gate → SHA-tagged GHCR images + SBOM → ephemeral kind deploy → Ingress smoke test. Publishing and deployment are gated by `needs:`.
- `release.yml`: `v*` tags build/push semver-tagged images and create generated release notes.

The deployed reference is always the commit SHA, never `latest`. Configure repository branch protection so `main` requires a PR, all required CI checks and at least one approval.

## Rollback

Fast incident rollback:

```bash
kubectl rollout undo deployment/backend -n civicpulse
kubectl rollout status deployment/backend -n civicpulse
```

Auditable rollback: render the production overlay with the previous known-good commit SHA and re-apply it. See `docs/RUNBOOK.md` for both procedures and verification steps.

## Security notes

- No keys/passwords belong in Git. `.env` is ignored; Kubernetes Secret manifests contain placeholders only.
- Hosted LLM calls never include `reporter_contact`; phone/email/CNIC patterns in complaint text and house numbers in location are redacted first.
- The frontend uses same-origin `/api`; no environment-specific backend URL is baked into the Vite bundle.
- Redis rate limiting is distributed by client IP, so HPA scale-out does not multiply the allowed request rate.
- Database and cache are not publicly published in production Compose and never use NodePort/LoadBalancer in Kubernetes.

## Screenshots / demo evidence

Add real captures to `docs/evidence/` following its README: UI submit result, dashboard and stats; branch protection; PR review; merge conflict; deliberate red CI/block; network isolation; HPA scale-out; VPA recommendation; rollback; and optional zero-downtime rollout.

## Collaboration workflow

Use `main` (protected/deployable), `dev` (integration) and `feature/*`. Recommended flow: Issue → feature branch → conventional commits (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `ci:`, `chore:`) → PR → partner review → merge. Do not manufacture PRs, reviews, commits or contribution history; the rubric requires genuine evidence.

## License

MIT; see `LICENSE`.
