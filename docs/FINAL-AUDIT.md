# CivicPulse Final Rubric Audit

Status vocabulary required by the build brief:

- **COMPLETE** — implementation/documentation exists in this package and can be mechanically verified here.
- **REQUIRES MANUAL EVIDENCE** — implementation support exists, but the rubric requires a real GitHub/Docker/Kubernetes/UI/video/measurement artifact that must be captured by the students.
- **REQUIRES EXTERNAL CREDENTIAL** — the path is implemented but a real hosted provider/GitHub context is required to demonstrate it.
- **NOT COMPLETE** — required implementation is absent.

## Verification performed while generating this package

- Backend test suite: **22 passed**, **75.25% app coverage** (requirement: ≥14 tests and ≥65%).
- Python source: `compileall` completed successfully.
- `python scripts/check_submission.py`: **passed all mechanical checks**; it correctly warns that manual evidence is still required.
- Kubernetes/GitHub workflow YAML: parsed successfully as YAML.
- Frontend dependency-backed tests/typecheck were **not executed in this environment** because npm package downloads were unavailable and the required packages were not cached.
- Docker/Compose/kind/Kubernetes runtime demonstrations were **not executed in this environment** because Docker/kind/kustomize were not installed. No runtime screenshots, scaling measurements, image sizes, or GitHub history were fabricated.

## A · Collaboration and version control — 15

| Rubric item | Implementation / evidence location | Status |
|---|---|---|
| `main` protected; PR required; CI required; ≥1 approval | `README.md` Collaboration; `docs/evidence/README.md` capture instructions | **REQUIRES MANUAL EVIDENCE** |
| `dev` + feature branches; no direct work on `main` | `README.md` Collaboration workflow | **REQUIRES MANUAL EVIDENCE** |
| ≥5 merged PRs, linked Issues, substantive partner review | `docs/evidence/README.md` | **REQUIRES MANUAL EVIDENCE** |
| ≥35 conventional commits; neither partner below 35% | commit convention documented in `README.md`; capture `git shortlog -sn` | **REQUIRES MANUAL EVIDENCE** |
| One real merge conflict + explanation | `docs/evidence/README.md` | **REQUIRES MANUAL EVIDENCE** |

## B · Frontend — 18

| Rubric item | Implementation / test | Status |
|---|---|---|
| Submit validation, honest loading, category/priority/summary/provider | `frontend/src/pages/SubmitPage.tsx`; `frontend/tests/SubmitPage.test.tsx` | **COMPLETE** |
| Dashboard pagination, filters, status transitions, verbatim 409 detail | `DashboardPage.tsx`; backend `allowed_transitions`; `DashboardPage.test.tsx` | **COMPLETE** |
| Stats aggregates + `X-Cache` state | `StatsPage.tsx`; `StatsPage.test.tsx` | **COMPLETE** |
| Runtime config: no baked API URL | `frontend/src/api/client.ts` relative base; `frontend/nginx.conf`; ADR 0002 | **COMPLETE** |
| ≥5 meaningful component tests passing in CI | 7 frontend test functions exist; real npm/CI run still required | **REQUIRES MANUAL EVIDENCE** |

## C · Backend — 25

| Rubric item | Implementation / test | Status |
|---|---|---|
| API contract/status codes/field-level errors | `backend/app/routes/*`, schemas, middleware; backend tests | **COMPLETE** |
| Four-layer separation; no SQL outside repositories; no route business logic | `routes/`, `services/`, `repositories/`, `providers/`; DB readiness SQL moved to `repositories/health.py` | **COMPLETE** |
| Explicit transition table; invalid transition 409 | `backend/app/domain.py`, `services/complaints.py`; tests | **COMPLETE** |
| `/health` vs `/ready`, liveness does not touch DB | `routes/health.py`, `services/health.py`, `repositories/health.py`; tests | **COMPLETE** |
| JSON stdout logging + request ID propagation | `logging.py`, `middleware.py`; request-ID test | **COMPLETE** |
| SIGTERM/graceful drain/close pools | FastAPI lifespan + drain middleware; Kubernetes preStop/grace period | **COMPLETE** |
| ≥14 deterministic tests and coverage ≥65% | 22 tests passed locally at 75.25% coverage | **COMPLETE** |

## D · Data layer — 12

| Rubric item | Implementation / evidence | Status |
|---|---|---|
| Alembic migrations; no startup schema DDL | `backend/alembic/versions/0001_create_complaints.py`; startup runs `alembic upgrade head` | **COMPLETE** |
| Complete complaint schema | `models.py`, migration, schemas | **COMPLETE** |
| Required indexes + named-query justification | migration/models; `docs/ENGINEERING-NOTES.md` | **COMPLETE** |
| Idempotent seed ≥30 realistic complaints | `backend/app/seed.py` contains 36 deterministic UUID5 rows | **COMPLETE** |

## E · Cache layer — 10

| Rubric item | Implementation / test | Status |
|---|---|---|
| Stats read-through 30 s + HIT/MISS | `providers/cache.py`, `services/complaints.py`, stats route; tests | **COMPLETE** |
| Stats cache invalidated on writes | create/status update service; test | **COMPLETE** |
| Distributed Redis IP limiter + 429 + Retry-After | `middleware.py`, `providers/cache.py`; test | **COMPLETE** |
| Redis AOF named volume + justification | Compose files; `docs/ENGINEERING-NOTES.md` | **COMPLETE** |

## F · AI layer — 25

| Rubric item | Implementation / evidence | Status |
|---|---|---|
| `TriageProvider` + ≥3 working implementations selected by env | Protocol + Groq/Ollama/rules/simulated + factory | **COMPLETE** |
| Structured output + Pydantic validation; malformed rejected | `llm.py`, `ollama.py`, service-boundary validation; malformed test | **COMPLETE** |
| 10 s timeout, one jittered retry only timeout/429/5xx, fallback + `triaged_by` | config, `services/triage.py`; retry/fallback tests | **COMPLETE** |
| Content-hash cache + measured hit rate | implementation/metric complete; real representative hit rate must be captured | **REQUIRES MANUAL EVIDENCE** |
| Prompt-injection guardrail + injection test | provider prompts/schema constraints; backend test | **COMPLETE** |
| `triage_latency_ms` + `/api/meta/providers` | persistence, outcome list, MetaService/route; endpoint test | **COMPLETE** |
| PII/data-governance ADR | `docs/adr/0004-pii-and-data-governance.md`; hosted-path redaction | **COMPLETE** |
| Demonstrate real hosted LLM path | `LLMTriage` implemented; requires Groq key/network | **REQUIRES EXTERNAL CREDENTIAL** |

## G · Docker and Compose — 15

| Rubric item | Implementation / evidence | Status |
|---|---|---|
| Both images multi-stage, version-pinned, non-root, exec command, cache-correct order | both Dockerfiles | **COMPLETE** |
| `.dockerignore` + before/after context sizes | ignore files complete; actual sizes require Docker experiment | **REQUIRES MANUAL EVIDENCE** |
| Two networks + `internal:true`; frontend provably cannot reach DB | Compose topology complete; actual failing command capture required | **REQUIRES MANUAL EVIDENCE** |
| Three named volumes; dev bind mount absent from prod; justifications | Compose files + engineering notes | **COMPLETE** |
| Healthchecks + `depends_on: service_healthy` | Compose files | **COMPLETE** |
| prod uses images/no build/no DB/cache ports | `compose.prod.yaml` | **COMPLETE** |

## H · Kubernetes — 20

| Rubric item | Implementation / evidence | Status |
|---|---|---|
| Namespace, deployments, Postgres StatefulSet/PVC, ClusterIP, Ingress | `k8s/base/*` | **COMPLETE** |
| ConfigMap vs Secret; placeholders only | `configmap.yaml`, `secret.yaml` | **COMPLETE** |
| startup/liveness `/health`, readiness `/ready` | `backend.yaml` | **COMPLETE** |
| requests/limits every container | backend/frontend/postgres/redis/migration manifests | **COMPLETE** |
| HPA v2 tuned + real watch/chart | HPA and k6 implementation complete; real watch/chart required | **REQUIRES MANUAL EVIDENCE** |
| VPA Off + real recommendation, requests updated, comparison | VPA/notes complete; actual Target/Bounds/request update/retest required | **REQUIRES MANUAL EVIDENCE** |

## I · CI/CD — 20

| Rubric item | Implementation / evidence | Status |
|---|---|---|
| CI lint/type/backend/frontend tests and required checks | `.github/workflows/ci.yml` exists; branch required-check setting/run evidence is external | **REQUIRES MANUAL EVIDENCE** |
| Compose integration smoke path | `ci.yml` integration job checks ready, POST, GET, category, MISS→HIT | **COMPLETE** |
| Trivy + kubeconform | `ci.yml` | **COMPLETE** |
| CD gated by `needs`, SHA-tagged GHCR images | `cd.yml` | **COMPLETE** |
| Ephemeral Kubernetes deploy + rollout + Ingress smoke | `cd.yml` | **COMPLETE** |
| Secrets/GITHUB_TOKEN + least privilege | workflow `permissions` blocks and Secrets references | **COMPLETE** |
| Real red pipeline blocks merge then fixed green | evidence instructions only; requires GitHub PR | **REQUIRES MANUAL EVIDENCE** |
| Successful CD run and GHCR packages | implementation complete but requires a real GitHub repository/run | **REQUIRES EXTERNAL CREDENTIAL** |

## J · Documentation, portfolio and reflection — 15

| Rubric item | Implementation / evidence | Status |
|---|---|---|
| README problem/badges/Mermaid/quickstart/API/screenshots instructions | `README.md`; badges need OWNER/REPO replacement; real UI screenshots required | **REQUIRES MANUAL EVIDENCE** |
| Four required ADRs | `docs/adr/0001...0004` | **COMPLETE** |
| Runbook deploy/rollback/logs/triage failure | `docs/RUNBOOK.md` | **COMPLETE** |
| ≤5 minute demo, both partners, required scenes | `docs/evidence/README.md` capture plan | **REQUIRES MANUAL EVIDENCE** |
| Engineering Notes eight questions with file/line refs | `docs/ENGINEERING-NOTES.md`; Q5/Q8 and VPA measurements intentionally need real evidence | **REQUIRES MANUAL EVIDENCE** |

## Bonus — not claimed automatically

Zero-downtime rollout, GitOps, digest-based deploy + Cosign, Grafana dashboard and OpenTelemetry are **not claimed**. Do not claim bonus points without implementing and capturing real evidence. The current CD captures image digests/SBOMs but deliberately deploys the required commit SHA tag, not a bonus digest/Cosign flow.

## Automatic-deduction guardrail review (§5.3)

| Guardrail | Result |
|---|---|
| `.env`, key, token/password committed | Mechanical checker passes; `.env` ignored. **COMPLETE** |
| API key in Kubernetes manifest | Placeholder only. **COMPLETE** |
| Unpinned base image / untagged postgres/redis/node | Explicit version tags. **COMPLETE** |
| `localhost` for service-to-service communication | Service names used (`postgres`, `redis`, `backend`, `ollama`); loopback only for a container's own healthcheck. **COMPLETE** |
| Frontend can reach DB | Topology prevents it; runtime proof still **REQUIRES MANUAL EVIDENCE** |
| DB/cache published in prod / DB NodePort | Not present. **COMPLETE** |
| Ungated publishing/deploy job | CD jobs gated with `needs:`. **COMPLETE** |
| Deploy `:latest` | Not present. **COMPLETE** |
| PostgreSQL Deployment/no PVC | StatefulSet + volumeClaimTemplates. **COMPLETE** |
| Direct pushes to `main` | Cannot be proved from generated files. **REQUIRES MANUAL EVIDENCE** |
| Quickstart from clean clone | Configuration is implemented; real clean-clone Docker run still **REQUIRES MANUAL EVIDENCE** |

## Remaining actions before submission

1. Put this repository in GitHub and replace `OWNER/REPO` badge placeholders.
2. Use the real two-person Issue → feature branch → PR → review workflow; collect the collaboration evidence rather than fabricating history.
3. Configure `main` branch protection with required CI checks and one approval.
4. Run CI; fix any environment-specific issue; capture one deliberately red/blocked PR and the corrected green state.
5. Run `docker compose up --build` from a clean clone and collect persistence/network-isolation/UI/context-size/image-size/cache-hit evidence.
6. Run the kind/Kubernetes load experiment; capture HPA watch/chart and VPA Target/Lower/Upper, then update backend resource requests from the real VPA recommendation and rerun the load test.
7. If demonstrating Groq, create a real API key in the environment/GitHub Secret only; never commit it.
8. Demonstrate both rollback mechanisms and record the ≤5-minute video with both partners speaking.
9. Replace each **REQUIRES REAL MEASUREMENT BEFORE SUBMISSION** entry and the real-incident section in `docs/ENGINEERING-NOTES.md` using your own runs.
10. Final command before submission: `python scripts/check_submission.py`.
