# CivicPulse Engineering Notes

These notes answer the eight questions in Assignment §5.2 against this repository. File/line references are deliberately concrete; update them if later edits shift line numbers. Measurements that require a real Docker/Kubernetes/GitHub run are left as explicit evidence slots rather than invented.

## 1. Three laptop/CI differences and what freezes them

1. **Python runtime can differ between developer machines and GitHub runners.** The backend build pins Python to `python:3.12.7-slim-bookworm` in both builder and runtime stages (`backend/Dockerfile:1` and `backend/Dockerfile:8`). The application therefore runs against the same Python/Linux base when built locally or in CI.
2. **Node and the production web server can differ.** The frontend build pins Node to `node:22.14.0-alpine3.21` and the final runtime to `nginx:1.27.4-alpine` (`frontend/Dockerfile:1` and `frontend/Dockerfile:9`). Node is intentionally absent from the final image.
3. **Available CPU/RAM differ sharply between a laptop, runner and Kubernetes node.** The backend pod declares a scheduling baseline and ceiling with `requests: { cpu: 150m, memory: 192Mi }` and `limits: { cpu: 750m, memory: 512Mi }` (`k8s/base/backend.yaml:58-60`). The HPA therefore has a CPU-request denominator instead of relying on host capacity.

The same principle is used for PostgreSQL, Redis, frontend and the migration Job: each container has explicit requests and limits in its manifest.

## 2. CI/CD maturity ladder

**Working classification: Continuous Delivery.** Every PR/main candidate is linted, type-checked and tested; `main` builds immutable SHA-tagged images and deploys them to an ephemeral Kubernetes cluster. Publishing is gated by the test job (`.github/workflows/cd.yml:30`) and deployment is gated by image publication (`.github/workflows/cd.yml:81`). This means the repository continuously proves that a deployable artifact can be produced and deployed, but it does **not** automatically release to a persistent production municipality environment.

The next rung is **Continuous Deployment to a persistent production environment**, where a passing change on `main` is promoted automatically to the real environment using an approved rollout strategy. That buys shorter lead time and removes the manual release step, but it also requires production-grade credentials, rollback/observability, change controls and a real target cluster.

> Course terminology check: the assignment references Lecture 03 slide 32 but the lecture slide deck was not part of the supplied assignment files. Before submission, compare the rung names above with that slide and adjust only the label if the course uses different wording; the repository behavior described here is concrete.

## 3. Exact build-once-deploy-many line

The frontend API client is same-origin: `createClient<paths>({ baseUrl: '' })` (`frontend/src/api/client.ts:10`). nginx performs runtime routing of `/api/` to the backend (`frontend/nginx.conf:37-43`). No backend hostname is baked into Vite's generated JavaScript.

The deployment side also uses the same image built once: CD rewrites the production overlay to the current immutable commit SHA (`.github/workflows/cd.yml:125-131`). If an absolute API URL were compiled into Vite, the image would become environment-specific: moving the exact same image from dev to another cluster/domain would still call the old backend. Relative `/api` plus an ingress/proxy preserves build-once-deploy-many.

## 4. Correctness for a probabilistic LLM and deterministic CI

For the live model, "correct" does **not** mean identical prose on every call. It means the response satisfies the system contract: category and priority are legal enums, the summary is one line and at most 140 characters, confidence is 0–1, the call respects the timeout/retry policy, and a provider failure never turns complaint intake into a 500.

The provider boundary is validated again by `TriageResult.model_validate(...)` (`backend/app/services/triage.py:63-65`). Only timeout/429/5xx-class failures receive the single jittered retry (`backend/app/services/triage.py:25-41, 75-78`); all final failures go to the deterministic rule provider and persist `rules:fallback` (`backend/app/services/triage.py:80-103`). CI explicitly sets `TRIAGE_PROVIDER: simulated` (`.github/workflows/ci.yml:39`), so tests never depend on network availability or probabilistic model output.

The test suite injects a provider that always raises, malformed output, and a prompt-injection complaint. These are contract tests rather than tests of one model's wording.

## 5. HPA lag

**Measured result: REQUIRES REAL MEASUREMENT BEFORE SUBMISSION.** Record seconds from offered-load increase to replica increase using the commands below.

Capture it from one real run:

```bash
# terminal 1
kubectl get hpa backend-hpa -n civicpulse -w --output=wide | tee docs/evidence/hpa-watch.txt

# terminal 2
k6 run -e BASE_URL=http://civicpulse.local load/k6-script.js

# supporting samples
while true; do
  date -Iseconds
  kubectl get hpa backend-hpa -n civicpulse
  kubectl get deploy backend -n civicpulse -o jsonpath='{.status.replicas}{"\n"}'
  sleep 5
done | tee docs/evidence/scaling-data.txt
```

The configured CPU target is 60% (`k8s/base/hpa.yaml:13-19`); scale-up stabilization is 0 seconds (`k8s/base/hpa.yaml:24-27`), while scale-down is intentionally held for 300 seconds (`k8s/base/hpa.yaml:20-23`). Even with a zero HPA scale-up stabilization window, lag remains because metrics-server samples usage periodically, HPA reconciliation is periodic, the scheduler must place a pod, the image may need to be available/pulled, and startup/readiness must complete before capacity serves traffic.

**Observed explanation: REQUIRES REAL MEASUREMENT BEFORE SUBMISSION.** Identify the dominant lag from the timestamped HPA and Deployment observations captured above.

Ways to reduce lag include maintaining a higher minimum replica count for expected bursts, smaller/faster images, faster startup, pre-pulling images, appropriately chosen CPU requests, and a workload-specific external/custom metric that signals demand earlier. Autoscaling is not a replacement for base capacity planning.

## 6. Why VPA is Off, and the HPA/VPA conflict

The VPA is deliberately recommender-only: `updateMode: "Off"` (`k8s/base/vpa.yaml:11-12`). HPA computes CPU utilization as CPU usage divided by CPU request, and this repository's HPA scales at 60% (`k8s/base/hpa.yaml:13-19`).

If VPA were in Auto mode and adjusted the backend CPU request while HPA was using CPU utilization, both controllers would act on the same denominator. A VPA increase in CPU request lowers apparent HPA utilization, which can make HPA scale in; fewer pods then raise per-pod load, which can lead VPA to raise requests again. That feedback loop makes the controllers fight. Off mode lets VPA recommend Target/Lower/Upper values, then a human updates requests and re-runs the load test.

Current guessed request before measurement: `150m` CPU / `192Mi` memory (`k8s/base/backend.yaml:59`).

Real recommendation and update loop:

```bash
kubectl describe vpa backend-vpa -n civicpulse | tee docs/evidence/vpa-recommendation.txt
# Record Target / Lower Bound / Upper Bound here, then update k8s/base/backend.yaml resources.requests.
k6 run -e BASE_URL=http://civicpulse.local load/k6-script.js
```

- Target: **REQUIRES REAL MEASUREMENT BEFORE SUBMISSION** from `kubectl describe vpa backend-vpa -n civicpulse`.
- Lower Bound: **REQUIRES REAL MEASUREMENT BEFORE SUBMISSION** from the same command.
- Upper Bound: **REQUIRES REAL MEASUREMENT BEFORE SUBMISSION** from the same command.
- Request values after applying recommendation: **REQUIRES REAL MEASUREMENT BEFORE SUBMISSION**; update and commit `k8s/base/backend.yaml` only after review.
- HPA behavior before vs after: **REQUIRES REAL MEASUREMENT BEFORE SUBMISSION**; collect a second `kubectl get hpa -w` capture.

## 7. `internal: true`, hosted LLM egress, and the resolution

`internal` is an isolated Docker bridge (`compose.yaml:112-114`). PostgreSQL and Redis join only that network (`compose.yaml:12` and `compose.yaml:28`), and the frontend joins only `edge` (`compose.yaml:90-98`). The backend is the deliberate bridge and joins **both** `edge` and `internal` (`compose.yaml:54-75`).

This means the hosted-LLM client lives in the backend: it reaches PostgreSQL/Redis over `internal` and receives normal outbound NAT through the non-internal `edge` network for Groq. The data stores never receive an internet-facing route, and the browser-facing frontend does not obtain a route to them. Ollama remains internal and is preloaded into the `ollama_models` volume before offline use.

The required proof is a real failure, not a statement:

```bash
docker compose exec frontend ping postgres
# Must fail; capture the real output in docs/evidence/network-isolation.txt or a screenshot.
```

## 8. The failure that cost more than an hour

This must describe a **real team debugging incident**. It cannot be manufactured after the fact.

**REQUIRES REAL TEAM INCIDENT BEFORE SUBMISSION.** Replace this section with one actual incident, including symptoms, initial hypothesis, commands/logs used, root cause, fix, and prevention. Preserve the evidence command or log line with the report.

A suitable format is 6–10 concrete sentences. Do not use a hypothetical problem; the rubric explicitly asks for something that actually cost the team more than an hour.

---

# Required design justifications and measured evidence

## Database indexes

`ix_complaints_status_priority (status, priority)` serves the operator queue when it filters by workflow status and urgency; those predicates are assembled in `ComplaintRepository.list` (`backend/app/repositories/complaints.py:57-68`). `ix_complaints_created_at (created_at)` supports the newest-first queue order in that same query (`backend/app/repositories/complaints.py:70-72`). These indexes are created by the Alembic migration, not by startup DDL.

## Why persist Redis AOF if a cache can be rebuilt?

Redis is not only a disposable stats cache in CivicPulse. It also contains the 24-hour triage-result cache, recent provider outcomes and distributed rate-limit counters. Losing Redis is not a data-integrity failure because PostgreSQL remains the source of truth, but preserving AOF avoids a post-restart inference burst, retains short-lived rate-limit state, and keeps the observability window. For that operational continuity, `redisdata` is justified even though the cached values are reconstructible. Redis is started with AOF enabled and mounted to `redisdata` (`compose.yaml:23-28`).

## Named-volume justification

- `pgdata`: durable complaint rows; `docker compose down/up` must preserve them.
- `redisdata`: AOF operational continuity for caches/rate limiting/outcomes as explained above.
- `ollama_models`: avoids downloading hundreds of MB of model weights on each startup.

The three volume declarations are at `compose.yaml:116-119`.

## Triage cache hit rate

The application exports `civicpulse_triage_cache_total{result="hit|miss"}` counters. After a representative workload, capture the counters and calculate:

`hit_rate = hits / (hits + misses)`

```bash
curl -s http://localhost:8080/metrics | grep civicpulse_triage_cache_total | tee docs/evidence/triage-cache-metrics.txt
```

Measured hit rate: **REQUIRES REAL MEASUREMENT BEFORE SUBMISSION**. Capture the command output above and calculate `hits / (hits + misses)`.

## Docker build-context sizes

Do not invent these values. Measure before and after temporarily moving each `.dockerignore` out of the build context, or use BuildKit's `transferring context` output:

```bash
mv backend/.dockerignore backend/.dockerignore.saved
docker build --no-cache --progress=plain backend 2>&1 | tee /tmp/backend-before.log
mv backend/.dockerignore.saved backend/.dockerignore
docker build --no-cache --progress=plain backend 2>&1 | tee /tmp/backend-after.log

mv frontend/.dockerignore frontend/.dockerignore.saved
docker build --no-cache --progress=plain frontend 2>&1 | tee /tmp/frontend-before.log
mv frontend/.dockerignore.saved frontend/.dockerignore
docker build --no-cache --progress=plain frontend 2>&1 | tee /tmp/frontend-after.log
```

- Backend before/after: **REQUIRES REAL MEASUREMENT BEFORE SUBMISSION** from the BuildKit logs above.
- Frontend before/after: **REQUIRES REAL MEASUREMENT BEFORE SUBMISSION** from the BuildKit logs above.

## Docker stage/final image sizes

```bash
docker build --target builder -t civicpulse-backend:builder backend
docker build -t civicpulse-backend:final backend
docker build --target builder -t civicpulse-frontend:builder frontend
docker build -t civicpulse-frontend:final frontend
docker image ls civicpulse-backend:builder civicpulse-backend:final civicpulse-frontend:builder civicpulse-frontend:final
```

- Backend builder/final: **REQUIRES REAL MEASUREMENT BEFORE SUBMISSION** from `docker image ls` above.
- Frontend builder/final: **REQUIRES REAL MEASUREMENT BEFORE SUBMISSION** from `docker image ls` above.

## Zero-downtime rollout bonus

Not claimed unless real evidence exists. If attempted:

```bash
# keep a request generator running while changing the backend image
kubectl set image deployment/backend backend=<new-image-sha> -n civicpulse
kubectl rollout status deployment/backend -n civicpulse
```

Record offered requests, failed requests and rollout events under `docs/evidence/`. A claimed zero-failure result must come from the actual run.
