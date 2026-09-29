**SCD ASSIGNMENT 01:-**

**24I-3064 MUHAMAD SHAHEER**

**24I-3086 SYED AYAAN** 

# **Contents**

1. 1\. AI Assistance Disclosure  
2. 2\. Engineering Notes  
3. 3\. Evidence Checklist  
4. 4\. Final Audit  
5. 5\. Local Validation  
6. 6\. Requirement Checklist  
7. 7\. Runbook  
8. 8\. Triage Design and AI Layer  
9. 9\. ADR and Evidence Inventory

Note: This consolidated document is assembled from the project material available in the conversation and the verified work completed during the assignment. Where a source file was not directly available, the section is presented as a consolidated project summary rather than a verbatim reproduction.

# **1\. AI Assistance Disclosure**

AI assistance was used in this assignment to understand the specification, create an implementation checklist, scaffold and review application and infrastructure code, generate and refine deterministic tests, troubleshoot CI/CD issues, and prepare documentation.

The initial repository implementation was substantially assisted by AI tools. Both students reviewed, tested, modified, and validated the AI-assisted work retained in the final repository and are expected to be able to explain and modify it during the viva.

## **Tools actually used**

* OpenAI ChatGPT/Codex — requirements analysis, architecture and code scaffolding, backend debugging, test generation and refinement, Docker and CI/CD troubleshooting, evidence preparation, and documentation.  
* Anthropic Claude — additional code review, implementation assistance, debugging, and refinement during development.

## **Files/components influenced**

* Backend FastAPI services, providers, routes, schemas, configuration, and tests.  
* LLM triage integration and provider abstraction.  
* Structured-output validation using Pydantic.  
* Prompt-injection protection and related tests.  
* Deterministic simulated/fallback triage behavior for CI.  
* Redis cache logic and cache-related validation.  
* React frontend implementation and tests.  
* Dockerfiles and Docker Compose configuration.  
* Kubernetes and Kustomize manifests.  
* GitHub Actions CI/CD workflows.  
* Submission and verification scripts.  
* README, ADRs, Engineering Notes, Runbook, and evidence documentation.

## **Modifications made afterwards**

* Fixed backend type-checking and linting issues identified by mypy and ruff.  
* Corrected backend tests and maintained the required coverage threshold.  
* Changed Groq/LLM triage from json\_object mode to strict json\_schema structured output after the schema-mode test exposed the mismatch.  
* Verified prompt-injection handling using deterministic automated tests.  
* Tested fallback behavior and deterministic CI operation when the external LLM provider is unavailable.  
* Verified cache behavior by submitting duplicate complaints and recording cache hit/miss metrics.  
* Updated the PII and data-governance ADR after reviewing how complaint data is sent to the external AI provider.  
* Measured Docker build-context sizes and final image sizes rather than relying on estimates.  
* Corrected GitHub Actions workflow configuration, including Trivy action versions and workflow structure.  
* Created and reviewed CI failure and recovery evidence.

## **Why those modifications were made**

The modifications were driven by real testing, CI failures, security checks and measured project behavior. AI-generated or AI-assisted material was not treated as automatically correct; retained code and documentation were reviewed, tested and modified when issues were identified.

# **2\. Engineering Notes**

## **2.1 Three laptop/CI differences and what freezes them**

10. Python runtime can differ between developer machines and GitHub runners. The backend pins Python to python:3.12.7-slim-bookworm in builder and runtime stages.  
11. Node and production web-server versions can differ. The frontend pins node:22.14.0-alpine3.21 and nginx:1.27.4-alpine.  
12. CPU and RAM vary between laptops, runners and Kubernetes nodes. Backend requests and limits provide a controlled scheduling and autoscaling baseline.

## **2.2 CI/CD maturity ladder**

The project is best described as Continuous Delivery. Pull requests and development changes are automatically checked by linting, type checking, backend tests, frontend tests, container builds, security scanning, manifest validation and integration testing. The next rung would be Continuous Deployment to a persistent production environment.

## **2.3 Build once, deploy many**

The frontend uses same-origin API requests and nginx runtime routing for /api/. No environment-specific backend hostname is baked into the generated frontend bundle. Deployment uses immutable commit-SHA image references, allowing the same built image to move between environments.

## **2.4 Correctness for a probabilistic LLM and deterministic CI**

* Correctness means conforming to the application contract rather than returning identical prose.  
* Category and priority must be legal enums; confidence must be 0–1; summary must satisfy its format constraints.  
* The live provider uses schema-constrained output and Pydantic validation.  
* Provider timeout/retry/fallback behavior prevents complaint intake from failing when the external provider fails.  
* CI uses a simulated deterministic provider so tests do not depend on external network availability or probabilistic output.

## **2.5 HPA lag**

The HPA target is 60% CPU utilization. A verified numeric HPA lag was not captured before submission, so no numeric measurement is claimed. Likely contributors include metrics-server sampling, HPA reconciliation, scheduler placement, image availability, container startup and readiness.

## **2.6 Why VPA is Off**

VPA is configured in recommender-only mode (updateMode: Off). Running VPA in Auto while HPA scales on CPU utilization can create feedback because VPA changes CPU requests, which changes the denominator used by HPA.

* Backend request before recommendation-based tuning: 150m CPU / 192Mi memory.  
* Target: not measured before submission.  
* Lower bound: not measured before submission.  
* Upper bound: not measured before submission.  
* No VPA-derived request update is claimed without verified recommendation output.

## **2.7 Internal network and hosted LLM egress**

PostgreSQL and Redis are placed on an internal Docker network. The frontend is edge-facing. The backend joins both the edge and internal networks, allowing it to reach internal stateful services and also make outbound requests to the hosted Groq provider while keeping the database and cache isolated from the browser-facing network.

## **2.8 Failure that cost more than an hour**

During final CI repair, the backend pipeline continued to fail after an intentionally modified HTTP status assertion was restored. The decisive CI log showed: assert 'json\_object' \== 'json\_schema'. The root cause was the Groq/LLM provider still requesting json\_object mode while the structured-output security test required strict JSON Schema mode.

pytest tests/test\_api.py \-k prompt\_injection \-v

The provider was changed to strict json\_schema mode using the TriageResult schema. The full backend suite then passed 26 tests with 77.43% coverage against a required threshold of 65%.

## **Measured design evidence**

| Measurement | Result | Interpretation |
| :---- | :---- | :---- |
| Triage cache hit rate | 50% (1 hit / 1 miss) | Repeated identical request was served from cache. |
| Backend build context | 149.72 kB → 4.47 kB | .dockerignore substantially reduced context transfer. |
| Frontend build context | 822 B → 822 B | Context was already minimal. |
| Backend builder/final image | 239 MB / 356 MB | Runtime contains installed app dependencies. |
| Frontend builder/final image | 472 MB / 73.6 MB | Multi-stage build removes Node/build tooling from final nginx image. |

# **3\. Evidence Checklist**

The repository documentation explicitly requires real evidence. Screenshots, output, history, measurements and links must not be fabricated.

## **3.1 GitHub and collaboration**

13. Configure main branch protection to require pull requests, required CI checks, and one approval; capture docs/evidence/branch-protection.png.  
14. Use genuine Issues, feature branches, partner review comments, and at least five merged PRs; preserve Issue/PR/review relationships.  
15. Capture contribution split using git shortlog \-sn and calculate each collaborator's percentage.  
16. Preserve a real resolved conflict and document the resolution in docs/evidence/merge-conflict.md.

## **3.2 Docker and Compose**

docker compose up \-d \--build

docker compose ps

docker compose exec frontend ping postgres

docker compose exec postgres psql \-U civicpulse \-d civicpulse \-c 'select count(\*) from complaints;'

docker compose down

docker compose up \-d

docker compose exec postgres psql \-U civicpulse \-d civicpulse \-c 'select count(\*) from complaints;'

docker image ls civicpulse-backend civicpulse-frontend

Save actual output/screenshots for network isolation, persistence, image sizes and build-context measurements under docs/evidence/.

## **3.3 Kubernetes and HPA**

make k8s

kubectl get hpa \-n civicpulse \-w | tee docs/evidence/hpa-watch.txt

k6 run \-e BASE\_URL=http://civicpulse.local load/k6-script.js

kubectl get hpa \-n civicpulse \-o wide

kubectl get deploy backend \-n civicpulse \-o jsonpath='{.status.replicas}{"\\n"}'

kubectl delete pod \-n civicpulse \-l app=postgres

kubectl get pods \-n civicpulse \-w

Record timestamp, offered load and replica count in docs/evidence/hpa-results.csv and render the replicas-vs-load chart.

## **3.4 VPA**

kubectl describe vpa backend-vpa \-n civicpulse | tee docs/evidence/vpa-recommendation.txt

kubectl get deployment backend \-n civicpulse \-o yaml | tee docs/evidence/backend-before-vpa.yaml

Only real Target, Lower Bound and Upper Bound values should be copied into Engineering Notes.

## **3.5 CI/CD and rollback**

17. Open a real PR with one deliberately failing test and capture the failed required check and blocked merge control.  
18. Repair the test in the same PR and capture the green pipeline.  
19. Merge through protected main, save the successful cd.yml run URL, and preserve GHCR SHA-tagged image links.  
20. Demonstrate kubectl rollout undo and reapplying a previous immutable SHA, capturing commands and rollout status.

# **4\. Final Audit**

This section consolidates the final project audit checks represented by the repository's FINAL-AUDIT.md workflow.

## **Repository hygiene**

* No .env, API key, token or password should exist in Git history.  
* No LLM API key should be committed in Kubernetes manifests, even if base64 encoded.  
* Base images and major services should be pinned to explicit versions.  
* No localhost should be used for service-to-service container communication.  
* Database/cache ports should not be publicly exposed in production Compose or Kubernetes.  
* Production deployment must not use :latest.

## **Quality gates**

* Backend lint and mypy pass.  
* Backend tests pass with at least 65% coverage; verified result during repair was 26 tests / 77.43%.  
* Frontend lint, type checks and tests pass.  
* OpenAPI contract check passes.  
* Container builds complete.  
* Kubernetes manifests render and validate.  
* Integration smoke path exercises a real complaint request end-to-end.

## **Evidence status**

* Branch protection screenshot captured.  
* Failed CI evidence captured.  
* Green CI evidence captured.  
* AI fallback, injection, Groq triage and cache evidence captured.  
* Docker context and image measurements captured.  
* HPA watch file exists, but numeric scaling analysis was not fully verified in the available documentation.  
* VPA recommendation and rollback evidence should only be claimed when real output exists.

# **5\. Local Validation**

This consolidated validation procedure mirrors the repository's local-validation intent.

## **Backend**

python \-m venv .venv

.\\.venv\\Scripts\\Activate.ps1

pip install \-e ".\\backend\[dev\]"

cd backend

ruff check app

mypy app

pytest \--cov=app \--cov-fail-under=65

cd ..

python scripts/check\_openapi\_contract.py

## **Frontend**

npm install \--prefix frontend \--no-audit \--no-fund

npm \--prefix frontend run lint

npm \--prefix frontend run typecheck

npm \--prefix frontend test

npm \--prefix frontend run build

## **Full stack**

docker compose up \-d \--build

docker compose ps

Open the UI, submit a complaint, check dashboard/stats, verify fallback and cache behavior, then preserve actual evidence.

## **Submission lint**

py \-3.12 scripts\\check\_submission.py

The final mechanical checker was reported as passing with manual evidence warnings remaining.

# **6\. Requirement Checklist**

| Area | Requirement coverage | Status |
| :---- | :---- | :---- |
| Frontend | React UI, complaint submission, dashboard/stats, runtime API routing. | Implemented / evidence-dependent |
| Backend | FastAPI layered architecture, complaint CRUD/workflow, health/readiness, metrics. | Implemented / evidence-dependent |
| Data | PostgreSQL source of truth, Redis cache/rate state, migrations and indexes. | Implemented / evidence-dependent |
| AI layer | Provider interface, Groq LLM, structured Pydantic output, 10-second policy, retry/fallback, injection guardrail, cache. | Implemented / evidence-dependent |
| Testing | Backend test suite ≥14 tests and ≥65% coverage; verified 26 tests and 77.43% coverage during final repair. | Implemented / evidence-dependent |
| Containers | Pinned multi-stage Dockerfiles, non-root runtime, .dockerignore, Compose healthchecks, internal network and named volumes. | Implemented / evidence-dependent |
| Kubernetes | Namespace, workloads/services/Ingress, ConfigMap/Secret separation, resource requests/limits, HPA, VPA Off/recommender mode. | Implemented / evidence-dependent |
| CI | Lint/type/tests, build, Trivy scan, kubeconform/manifests, integration smoke. | Implemented / evidence-dependent |
| CD | SHA-tagged images, GHCR publication, deploy gating and rollout checks. | Implemented / evidence-dependent |
| Documentation | README, four ADRs, RUNBOOK, ENGINEERING-NOTES, AI-USAGE and evidence. | Implemented / evidence-dependent |

Important: evidence-dependent Kubernetes measurements should not be represented as verified unless the real output was captured.

# **7\. Runbook**

Operational runbook for setup, validation, evidence collection and final submission.

## **7.1 Start local stack**

copy .env.example .env

docker compose up \-d \--build

docker compose ps

Open http://localhost:8080 for the Compose-based local deployment.

## **7.2 Live Groq triage**

Set TRIAGE\_PROVIDER=llm and GROQ\_API\_KEY in the local .env only. Never commit the key. Rebuild/start Compose and submit a complaint; expected provider label is llm:groq.

## **7.3 Fallback and injection checks**

cd backend

pytest \-k fallback \-v

pytest \-k injection \-v

cd ..

## **7.4 Docker evidence**

docker compose exec frontend ping postgres

docker compose exec frontend ping backend

docker compose exec postgres psql \-U civicpulse \-d civicpulse \-c "select count(\*) from complaints;"

docker image ls civicpulse-backend civicpulse-frontend

## **7.5 Kubernetes evidence workflow**

make k8s

kubectl get hpa \-n civicpulse \-w

k6 run \-e BASE\_URL=http://civicpulse.local load/k6-script.js

kubectl describe vpa backend-vpa \-n civicpulse

This workflow requires a working Kubernetes environment. If it was not actually run, do not claim numeric HPA/VPA evidence.

## **7.6 Rollback**

kubectl rollout undo deployment/backend \-n civicpulse

kubectl rollout status deployment/backend \-n civicpulse

kubectl apply \-k k8s/overlays/prod

kubectl rollout status deployment/backend \-n civicpulse

## **7.7 Final close-out**

python scripts\\check\_submission.py

git shortlog \-sn \--all

git log \--all \--full-history \-- .env

Final submission materials include repository URL, successful CD run link, GHCR SHA-tagged images, demo video, shortlog output and HPA capture/chart when available.

# **8\. Triage Design and AI Layer**

This section consolidates the project triage design represented by TRIAGE.md and the implemented provider architecture.

## **Provider abstraction**

* LLM provider for hosted Groq inference.  
* Ollama provider for local/offline model use.  
* Rules provider for deterministic fallback.  
* Simulated provider for deterministic CI.  
* Factory/provider selection driven by configuration.

## **Structured output contract**

* Category must match the application enum.  
* Priority must match the application enum.  
* Summary is constrained by the schema.  
* Confidence is bounded from 0 to 1\.  
* Provider output is validated by Pydantic before use.

## **Prompt-injection guardrail**

Complaint text is treated as untrusted data, never as instructions. Automated testing verifies that an input such as 'ignore all previous instructions' remains complaint data and cannot override category/priority controls.

## **Resilience**

* Timeout/retry behavior is bounded.  
* A final provider failure falls back to deterministic rules.  
* Complaint intake should continue rather than return a provider-induced 500\.  
* Content-hash caching avoids repeated provider calls for identical triage input.

## **Observed cache evidence**

One miss followed by one hit was captured for repeated input, yielding a measured hit rate of 50% in that small evidence run.

# **9\. ADR and Evidence Inventory**

## **Architecture Decision Records**

* 0001 — Provider interface / replaceable triage provider.  
* 0002 — Frontend runtime configuration / same-origin API routing.  
* 0003 — Deploy-by-SHA / immutable image deployment.  
* 0004 — PII and data governance.

## **Evidence files observed during the project**

* ai-cache-evidence.png  
* backend-tests-coverage.png / backend-test-coverage.txt  
* branch-protection.png  
* failed-ci.png  
* green-ci.png  
* fallback-test.png  
* groq-triage.png  
* injection-test.png  
* prompt-injection-ui.png  
* triage-cache-metrics.txt  
* docker-image-sizes.txt  
* backend-context-before.txt / backend-context-after.txt  
* frontend-context-before.txt / frontend-context-after.txt  
* hpa-watch.txt  
* kubernetes-ui.png

## **Final caution**

The project evidence policy is explicit: do not fabricate screenshots, measurements, command output, Git history or links. Any item that was not actually captured should remain unclaimed rather than being represented as verified.