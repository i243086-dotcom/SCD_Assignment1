# CivicPulse Engineering Notes

These notes answer the eight Engineering Notes questions required by the assignment and document measured evidence where it was actually collected. Where a real Kubernetes measurement was not captured before submission, no numeric result is claimed.

## 1. Three laptop/CI differences and what freezes them

1. Python runtime can differ between developer machines and GitHub runners. The backend build pins Python to `python:3.12.7-slim-bookworm` in both builder and runtime stages. The application therefore runs against the same Python/Linux base when built locally or in CI.

2. Node and the production web server can differ between machines. The frontend build pins Node to `node:22.14.0-alpine3.21`, while the final runtime uses `nginx:1.27.4-alpine`. Node.js and frontend build tooling are not included in the production runtime image.

3. CPU and memory available on a laptop, GitHub runner and Kubernetes node can differ significantly. The backend Kubernetes deployment defines explicit CPU and memory requests and limits so scheduling and autoscaling are based on controlled resource values instead of machine-specific capacity.

The same approach is used for other application components where appropriate: runtime versions, container images and resource settings are explicitly declared rather than relying on local developer-machine defaults.


## 2. CI/CD maturity ladder

The current project is best described as Continuous Delivery.

Pull requests and development changes are automatically checked using linting, type checking, backend tests, frontend tests, container builds, security scanning, Kubernetes manifest validation and integration testing.

Changes reaching `main` are intended to produce immutable SHA-tagged container images and exercise deployment through the CD workflow. The system proves that a deployable artifact can be produced consistently.

It is not full Continuous Deployment to a persistent real production municipality environment because production promotion is not automatically performed against a permanent external production cluster.

The next maturity level would be Continuous Deployment, where every approved and passing change is automatically promoted to a persistent production environment using a controlled rollout strategy, production-grade secrets, monitoring, rollback procedures and change-management controls.


## 3. Exact build-once-deploy-many line

The frontend API client uses a same-origin API URL rather than compiling an environment-specific backend hostname into the frontend bundle.

The frontend calls the API using a relative path, and nginx routes `/api/` traffic to the backend service.

This supports build-once-deploy-many because the exact same frontend image can run in different environments without rebuilding the JavaScript bundle with a different backend hostname.

On the deployment side, container images are intended to be identified using immutable commit SHA tags. Environment-specific routing is handled externally through nginx, services and ingress configuration instead of being baked into the application image.


## 4. Correctness for a probabilistic LLM and deterministic CI

For the live LLM provider, correctness does not mean that the model must return identical wording on every request.

Correctness means that the response satisfies the application contract:

- category must be one of the allowed values
- priority must be one of the allowed values
- summary must comply with the required length and format
- confidence must be between 0 and 1
- provider calls must obey the configured timeout and retry policy
- provider failure must not cause complaint submission to return an uncontrolled server error

The triage result is validated using the application's Pydantic model.

The provider implementation uses strict structured-output handling. During final CI debugging, an automated prompt-injection/schema-mode test exposed that the provider was still using `json_object` output mode. The implementation was changed to strict `json_schema` mode using the `TriageResult` schema.

The application also includes deterministic fallback behavior. If the external provider fails after the permitted retry, triage falls back to the deterministic rules provider.

CI uses the simulated provider so automated tests do not depend on live network access, API availability or probabilistic LLM output.

The test suite covers failure behavior, malformed output, prompt-injection input and deterministic fallback behavior.


## 5. HPA lag

The HPA is configured to scale the backend based on CPU utilization, with a target of 60%.

The scale-up stabilization window is configured to allow prompt scaling, while scale-down is intentionally slower to reduce replica oscillation.

A verified numeric HPA scale-up lag was not captured before submission, so no measured number is claimed.

The expected sources of scaling delay are:

- metrics-server sampling interval
- HPA reconciliation interval
- scheduler placement time
- container image availability or image-pull delay
- pod startup time
- readiness probe completion

Ways to reduce observed scaling lag include:

- keeping a higher minimum replica count for predictable bursts
- reducing container image size
- reducing application startup time
- pre-pulling commonly used images
- choosing appropriate CPU requests
- using a workload-specific external or custom metric when CPU utilization reacts too late

Autoscaling should complement base-capacity planning rather than replace it.


## 6. Why VPA is Off, and the HPA/VPA conflict

The Vertical Pod Autoscaler is intentionally configured with:

`updateMode: "Off"`

This makes it recommender-only.

The HPA scales replicas using CPU utilization. CPU utilization is calculated relative to the pod CPU request.

If VPA automatically changes the CPU request while HPA is simultaneously scaling based on CPU utilization, both controllers can influence the same scaling denominator.

For example:

- VPA increases CPU request
- apparent HPA CPU utilization falls
- HPA may reduce replicas
- per-pod load then increases
- the controllers can begin reacting against each other

Using VPA in Off mode avoids this feedback loop. VPA recommendations can be reviewed manually, resource requests can then be adjusted intentionally, and the load test can be repeated.

The configured backend request before any recommendation-based change is approximately:

- CPU: `150m`
- Memory: `192Mi`

A verified VPA recommendation capture was not available before submission, so no Target, Lower Bound or Upper Bound values are claimed.

Final measurement status:

- Target: Not measured
- Lower Bound: Not measured
- Upper Bound: Not measured
- Updated request values: Not applied from VPA recommendation
- HPA before/after comparison: Not measured


## 7. Docker internal network, hosted LLM egress, and the resolution

The Docker Compose architecture separates externally reachable components from internal data services.

PostgreSQL and Redis are attached to the internal network.

The frontend is attached to the edge-facing network.

The backend intentionally connects to both networks.

This allows the backend to:

- communicate with PostgreSQL and Redis on the internal network
- communicate with the frontend/reverse-proxy path
- make outbound requests to the hosted Groq LLM provider

The database and Redis services are therefore not directly internet-facing.

The backend acts as the controlled bridge between browser-facing traffic, internal stateful services and the external hosted AI provider.

The intended isolation test is to confirm that a frontend container cannot directly reach the PostgreSQL service over the internal network.


## 8. The failure that cost more than an hour

During final CI repair, a backend test failure took more than an hour to diagnose and resolve.

The initial CI problem appeared to be associated with an intentionally modified HTTP status assertion used to demonstrate a failing pipeline.

After restoring that test, the backend CI job continued to fail.

The failing GitHub Actions log showed:

`assert 'json_object' == 'json_schema'`

inside the test:

`test_llm_prompt_injection_is_data_and_requests_schema_mode`

We reproduced the problem locally using:

`pytest tests/test_api.py -k prompt_injection -v`

The root cause was that the Groq/LLM provider still requested:

`response_format={'type': 'json_object'}`

while the security and structured-output test required strict JSON Schema mode.

The provider was changed to request `json_schema` with strict validation using the `TriageResult` model schema.

After the fix, the complete backend test suite was rerun successfully:

- 26 tests passed
- total coverage: 77.43%
- required coverage threshold: 65%

The prevention measure is that structured-output behavior is now enforced by an automated test rather than relying only on manual code inspection.


# Required design justifications and measured evidence

## Database indexes

The complaints table includes indexes designed around the operator workflow.

The combined status/priority index supports queue filtering by workflow status and urgency.

The created-at index supports newest-first ordering.

These indexes are created through database migrations rather than ad-hoc startup DDL.


## Why persist Redis AOF if a cache can be rebuilt?

Redis is not used only for disposable statistics.

It also stores short-lived operational data such as:

- triage cache entries
- recent provider outcomes
- rate-limiting state

PostgreSQL remains the durable source of truth, so losing Redis does not cause primary complaint-data loss.

However, retaining Redis AOF improves operational continuity after restart because it:

- avoids an immediate burst of repeated LLM inference
- preserves short-lived rate-limit state
- preserves recent cache behavior
- retains recent operational state

For that reason, persistent Redis storage is justified even though the data is reconstructible.


## Named-volume justification

The project uses persistent volumes for different operational reasons:

- `pgdata`: preserves complaint records across container restarts
- `redisdata`: preserves Redis AOF state and short-lived operational continuity
- `ollama_models`: avoids repeatedly downloading model weights when using local Ollama


## Triage cache hit rate

The application exports cache metrics using:

`civicpulse_triage_cache_total{result="hit|miss"}`

A representative duplicate-request test produced:

- Cache hits: 1
- Cache misses: 1

The measured cache hit rate was:

`1 / (1 + 1) = 50%`

Measured hit rate: **50%**

The raw metrics were saved in:

`docs/evidence/triage-cache-metrics.txt`

This demonstrates that repeated identical triage input can be served from cache rather than invoking the provider again.


## Docker build-context sizes

BuildKit output was captured before and after applying the `.dockerignore` files.

Measured results:

- Backend before `.dockerignore`: **149.72 kB**
- Backend after `.dockerignore`: **4.47 kB**
- Frontend before `.dockerignore`: **822 B**
- Frontend after `.dockerignore`: **822 B**

The backend `.dockerignore` substantially reduced the amount of data sent to the Docker build context.

The frontend context was already extremely small, so its measured context size remained effectively unchanged.

Evidence files include the before/after Docker build-context logs under `docs/evidence/`.


## Docker stage/final image sizes

Measured Docker image sizes:

- Backend builder: **239 MB**
- Backend final: **356 MB**
- Frontend builder: **472 MB**
- Frontend final: **73.6 MB**

The frontend demonstrates the main benefit of a multi-stage build: Node.js and frontend build tooling remain in the builder stage, while the final image contains only the nginx runtime and built static assets.

The backend final image is larger than the measured builder image because the runtime image includes the installed application dependencies required to execute the service.

The measurements are recorded in:

`docs/evidence/docker-image-sizes.txt`


## Zero-downtime rollout bonus

No zero-downtime rollout result is claimed without verified measurement evidence.

A production-quality validation would keep a request generator running during an image update, record offered requests and failed requests, and correlate those results with Kubernetes rollout events.

No unverified zero-failure result is reported.