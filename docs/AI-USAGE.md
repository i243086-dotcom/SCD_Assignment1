# AI assistance disclosure

AI assistance was used in this assignment to understand the specification, create an implementation checklist, scaffold and review application and infrastructure code, generate and refine deterministic tests, troubleshoot CI/CD issues, and prepare documentation.

The initial repository implementation was substantially assisted by AI tools. Both students reviewed, tested, modified, and validated the AI-assisted work retained in the final repository and are expected to be able to explain and modify it during the viva.

## Tools actually used

- OpenAI ChatGPT/Codex — requirements analysis, architecture and code scaffolding, backend debugging, test generation and refinement, Docker and CI/CD troubleshooting, evidence preparation, and documentation.
- Anthropic Claude — additional code review, implementation assistance, debugging, and refinement during development.

## Files/components influenced

AI-assisted work was used across several parts of the project, including:

- Backend FastAPI services, providers, routes, schemas, configuration, and tests.
- LLM triage integration and provider abstraction.
- Structured-output validation using Pydantic.
- Prompt-injection protection and related tests.
- Deterministic simulated/fallback triage behavior for CI.
- Redis cache logic and cache-related validation.
- React frontend implementation and tests.
- Dockerfiles and Docker Compose configuration.
- Kubernetes and Kustomize manifests.
- GitHub Actions CI/CD workflows.
- Submission and verification scripts.
- README, ADRs, Engineering Notes, Runbook, and evidence documentation.

## Modifications made afterwards

The team reviewed and modified AI-assisted output after implementation and testing. Examples include:

- Fixed backend type-checking and linting issues identified by `mypy` and `ruff`.
- Corrected backend tests and maintained the required coverage threshold.
- Changed the Groq/LLM triage request from `json_object` mode to strict `json_schema` structured output after the prompt-injection/schema-mode test exposed the mismatch.
- Verified prompt-injection handling using deterministic automated tests.
- Tested fallback behavior and verified deterministic CI operation when the external LLM provider is unavailable.
- Verified cache behavior by submitting duplicate complaints and recording cache hit/miss metrics.
- Updated the PII and data-governance ADR after reviewing how complaint data is sent to the external AI provider.
- Measured Docker build-context sizes and final image sizes rather than relying on estimated values.
- Corrected GitHub Actions workflow configuration, including Trivy action versions and workflow structure.
- Created and reviewed CI failure and recovery evidence.
- Updated README badges, screenshots, evidence references, and project documentation based on actual project results.

## Why those modifications were made

The modifications were made based on real testing, CI failures, security checks, and measured project behavior.

In particular:

- Type and lint fixes were required to make the backend pass automated quality gates.
- The strict JSON Schema change was required because the automated test showed that the implementation was still requesting `json_object` output rather than schema-constrained output.
- Fallback and simulated-provider validation was necessary to keep CI deterministic and independent of external AI availability.
- Cache measurements were recorded to provide actual evidence of cache effectiveness.
- Docker measurements were collected to document real build-context and image-size characteristics.
- CI workflow changes were made after GitHub Actions exposed invalid or outdated action references and workflow configuration errors.
- Trivy findings were reviewed as part of the container security process.
- Documentation was updated to match the implementation and evidence actually produced during development.

AI-generated or AI-assisted material was not treated as automatically correct. Code and documentation retained in the repository were reviewed, tested, and modified where issues were identified.
