# CivicPulse Assignment Requirement Checklist

This checklist is derived from the supplied Assignment 01 specification and is used as the implementation plan. “Implemented” means the repository contains the required code/configuration; it does not substitute for experimental or GitHub evidence that must be collected by the two students.

## Phase 1 — Architecture and repository

- [x] React 18 + Vite + TypeScript frontend.
- [x] FastAPI + Pydantic v2 + Python 3.12 backend.
- [x] PostgreSQL 16 + SQLAlchemy + Alembic.
- [x] Redis 7 for stats cache, triage cache, rate limiter and recent outcomes.
- [x] Four backend layers: `routes/`, `services/`, `repositories/`, `providers/`.
- [x] Required repository directories for k8s, load, docs, ADRs, evidence, scripts and workflows.

## Phase 2 — API and domain

- [x] `POST /api/complaints` — validate → triage → persist; 201; field-level 400; 429 rate limit.
- [x] `GET /api/complaints/{id}` — 200/404.
- [x] `GET /api/complaints` — category/priority/status filtering and page/page_size ≤100 with total.
- [x] `PATCH /api/complaints/{id}/status` — explicit transition table and 409 attempted transition detail.
- [x] `GET /api/stats` — aggregate cache with `X-Cache: HIT|MISS`.
- [x] `GET /api/meta/providers` — active provider and last 20 outcomes.
- [x] `/health` liveness without DB/Redis access.
- [x] `/ready` checks PostgreSQL and Redis and names failures.
- [x] `/metrics` Prometheus request/latency/triage/fallback/cache metrics.
- [x] Full complaint schema, application validation and DB check constraints.
- [x] `(status, priority)` and `created_at` indexes with query justification in engineering notes.
- [x] UTC timestamps and server-generated UUIDs.

## Phase 3 — AI triage and resilience

- [x] `TriageProvider` protocol.
- [x] `LLMTriage` (Groq/OpenAI-compatible).
- [x] `OllamaTriage` offline path.
- [x] `RuleBasedTriage` deterministic always-available fallback.
- [x] `SimulatedTriage` deterministic CI provider with failure injection.
- [x] Provider selected with `TRIAGE_PROVIDER`.
- [x] Structured output requested and Pydantic validation enforced at the service boundary.
- [x] 10-second configured timeout.
- [x] One jittered retry only for timeout, 429 and 5xx.
- [x] Safe `rules:fallback` behavior; intake remains successful.
- [x] 24-hour Redis cache by content hash.
- [x] Prompt text clearly delimited as untrusted data; enum/schema validation; injection test.
- [x] API keys are environment/Secret only.
- [x] Hosted-path PII redaction decision documented in ADR 0004.
- [x] Triage latency/fallback/provider outcomes observable.
- [ ] Measure and report real triage cache hit rate (manual experiment).
- [ ] Demonstrate hosted LLM with a real external key (external credential).

## Phase 4 — Persistence and seeding

- [x] Schema created only through Alembic migration; no startup `CREATE TABLE`.
- [x] Idempotent deterministic seed command.
- [x] 36 realistic Pakistan/Urdu-influenced English complaints across all categories.
- [ ] Capture Compose persistence evidence (manual Docker run).
- [ ] Capture Kubernetes PostgreSQL pod-deletion persistence evidence (manual cluster run).

## Phase 5 — Frontend

- [x] Submit view with mirrored client validation, honest AI loading state and category/priority/summary/provider result.
- [x] Dashboard with filters, pagination and backend-provided allowed status transitions.
- [x] Backend 409 detail surfaced rather than replaced with a generic error.
- [x] Stats view renders category/priority aggregates and `X-Cache` HIT/MISS.
- [x] Same-origin relative API client; nginx proxies `/api`; no environment-specific Vite URL.
- [x] Typed client surface checked against OpenAPI and regeneration command.
- [x] React error boundary.
- [x] At least five meaningful Vitest tests (seven test functions across five test files).
- [ ] Capture real UI screenshots (manual evidence).

## Phase 6 — Logging and shutdown

- [x] JSON logs to stdout.
- [x] `X-Request-ID` accepted/generated and returned; request context is propagated to logs.
- [x] Exactly one warning from the orchestration layer per final triage fallback with complaint ID/provider/error class.
- [x] Graceful application lifespan closes Redis/database resources; drain middleware stops new non-health work while draining.
- [x] Kubernetes preStop and termination grace period configured for rolling updates.

## Phase 7 — Docker and Compose

- [x] Backend multi-stage, pinned Python base, cache-friendly dependency build, non-root, exec-form command and healthcheck.
- [x] Frontend Node build → nginx runtime; no Node/node_modules/source in final; non-root; healthcheck.
- [x] `.dockerignore` in each build context.
- [x] `compose.yaml` dev build + backend source bind mounts.
- [x] `compose.prod.yaml` image-only deployment; no `build:`; no DB/cache published ports.
- [x] Two networks: `edge` and `internal` with `internal: true`.
- [x] Frontend edge only; backend edge+internal; PostgreSQL/Redis internal only.
- [x] `pgdata`, `redisdata`, `ollama_models` named volumes with justification.
- [x] Redis AOF enabled.
- [x] Healthchecks and `depends_on: condition: service_healthy`.
- [x] Environment-sourced credentials; `.env.example`; `.env` ignored.
- [ ] Measure before/after Docker build-context sizes.
- [ ] Measure Docker stage/final image sizes.
- [ ] Capture failed frontend→Postgres connectivity command.

## Phase 8 — Kubernetes

- [x] Kustomize `base`, `overlays/dev`, `overlays/prod`.
- [x] Namespace `civicpulse`.
- [x] Backend and frontend Deployments with ≥2 replicas.
- [x] PostgreSQL StatefulSet + `volumeClaimTemplates`.
- [x] Redis Deployment + PVC.
- [x] ClusterIP Services only for frontend/backend/PostgreSQL/Redis.
- [x] Ingress `/` → frontend and `/api` → backend.
- [x] ConfigMap and Secret separated; Secret contains placeholders only.
- [x] Backend startup/liveness `/health`, readiness `/ready` probes.
- [x] Rolling update `maxSurge:1`, `maxUnavailable:0`, preStop and termination grace.
- [x] Requests/limits on every container.
- [x] HPA autoscaling/v2: min2/max10, CPU60, down300/up0.
- [x] VPA recommender-only `updateMode: Off`.
- [x] Backend PDB `minAvailable: 1`.
- [x] `load/k6-script.js` for scale-out load.
- [ ] Real HPA watch + replicas-vs-load chart.
- [ ] Real VPA Target/Lower/Upper; update backend request values based on recommendation; repeat load test.

## Phase 9 — Backend/frontend tests

- [x] ≥14 backend unit/integration tests (22 test functions currently).
- [x] Required always-raises provider fallback test.
- [x] Malformed provider output test.
- [x] Prompt-injection test.
- [x] State transition and invalid 409 tests.
- [x] Health/readiness tests.
- [x] Stats MISS/HIT and invalidation tests.
- [x] Rate-limit test.
- [x] Filtering/pagination/404 tests.
- [x] No `time.sleep()`-based test synchronization.
- [x] ≥5 frontend component tests.
- [ ] Execute full dependency-backed test suite in an environment with package-network access or Docker and record green output.

## Phase 10 — CI/CD and release

- [x] `ci.yml`: PR→main and push→dev.
- [x] Backend ruff/mypy/pytest coverage ≥65; frontend eslint/tsc/Vitest.
- [x] Build images in CI without push from PR CI.
- [x] Trivy HIGH/CRITICAL fixed-version gate.
- [x] Kustomize + kubeconform validation.
- [x] Compose integration path verifies ready, POST/GET/category and X-Cache MISS→HIT.
- [x] Least-privilege permissions blocks.
- [x] `cd.yml`: push→main, test → build-push → deploy-k8s with `needs:`.
- [x] GHCR images tagged with `github.sha`; no `latest` deployment.
- [x] SBOM generated for both images and image digests exposed.
- [x] Ephemeral kind deployment, rollout waits, Ingress smoke test and HPA print.
- [x] `release.yml` for `v*` tags and generated release notes.
- [ ] Configure GitHub branch protection and required checks (manual repository setting).
- [ ] Run real CD and provide successful run/GHCR links (requires GitHub repository/token context).
- [ ] Capture deliberately red PR, blocked merge and repaired green checks.

## Phase 11 — Documentation

- [x] Professional README with problem, badges placeholders, Mermaid architecture, quickstart, API table, Docker, Kubernetes, testing, CI/CD, security, screenshots/evidence instructions.
- [x] ADR 0001 provider interface.
- [x] ADR 0002 frontend runtime configuration.
- [x] ADR 0003 deploy by SHA.
- [x] ADR 0004 PII/data governance.
- [x] RUNBOOK for deploy, rollback, logs and dependency/triage/rate-limit failures.
- [x] AI-USAGE disclosure template that does not falsely claim manual authorship.
- [x] TRIAGE provider/runtime notes.
- [x] ENGINEERING-NOTES answers all eight assignment questions with file/line references; real measurements intentionally blank.
- [x] Evidence README tells students exactly what to capture.
- [ ] ≤5-minute demo video with both partners speaking.

## Phase 12 — Genuine collaboration evidence

These cannot be synthesized by code generation and must be real.

- [ ] `main` protected: PR, required CI, ≥1 approval, no direct push.
- [ ] `dev` + `feature/*` workflow used in practice.
- [ ] ≥5 merged PRs linked to Issues, each with substantive partner review comment.
- [ ] ≥35 conventional commits; neither partner below 35% by `git shortlog -sn`.
- [ ] One real merge conflict on code, resolution evidence and explanation.

## Phase 13 — Automatic-deduction guardrails

- [x] No `.env` committed in generated package.
- [x] No real API key/token/password stored in source or committed Secret manifest.
- [x] Base images tagged/pinned to explicit versions.
- [x] No `localhost`/`127.0.0.1` for container-to-container communication (loopback is used only for self-healthchecks).
- [x] Frontend is not on internal data network.
- [x] Production Compose does not publish DB/cache.
- [x] PostgreSQL Kubernetes Service is ClusterIP and workload is StatefulSet with PVC.
- [x] Publish/deploy jobs are gated by `needs:`.
- [x] No deployed `:latest` reference.
- [x] Clean-clone Compose path defaults to simulated provider so no API key is necessary.
