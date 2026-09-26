# Local validation performed during scaffold generation

Date: 2026-09-25.

These are actual checks run in the generation environment; they are not a substitute for the assignment's required GitHub/Docker/Kubernetes evidence.

- Backend: `PYTHONPATH=backend python -m pytest -q backend/tests --disable-warnings` → **22 passed**, **75.25% app coverage**.
- OpenAPI surface: `python scripts/check_openapi_contract.py` → passed required backend-route/frontend-typed-surface checks.
- Submission lint: `python scripts/check_submission.py` → passed mechanical checks, with expected warnings for evidence that must be captured manually.
- Kubernetes and GitHub Actions YAML parsed successfully.
- Python `compileall` succeeded.

Not run here:

- Frontend Vitest/ESLint/TypeScript dependency-backed run: npm dependencies were not available in the environment's offline cache and external package downloads were unavailable.
- Docker/Compose builds and runtime integration: Docker was not installed in the generation environment.
- kind/Kubernetes HPA/VPA/rollback demonstrations: kind/kustomize/Docker were not installed.
- GitHub branch protection, PR/review/commit history and hosted CI/CD: these require the students' real repository.
- Hosted Groq demonstration: requires the student's own API credential and network access.

Do not convert any of those unrun items to “passed” until you have run them yourself. Use `docs/FINAL-AUDIT.md` and `docs/evidence/README.md` as the remaining-work checklist.
