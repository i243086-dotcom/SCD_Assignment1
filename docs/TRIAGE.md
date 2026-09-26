# Triage design

## Contract
Every provider returns `TriageResult(category, priority, summary, confidence)`. Categories are `water`, `electricity`, `sanitation`, `roads`, `streetlights`, `other`; priorities are `high`, `normal`, `low`; summary is one line and at most 140 characters; confidence is `[0,1]`.

## Implementations
- `LLMTriage` — hosted Groq/OpenAI-compatible endpoint, schema-constrained JSON, Pydantic validation.
- `OllamaTriage` — local Ollama `/api/generate`, same JSON schema, no data leaves the machine.
- `RuleBasedTriage` — deterministic keyword classifier, always available and used as fallback.
- `SimulatedTriage` — deterministic CI fake with configurable failure injection.

## Resilience sequence
1. Hash normalized complaint text + location and check Redis (24-hour TTL).
2. Call the selected provider with a hard 10-second timeout.
3. Retry once with deterministic jitter only for timeout, HTTP 429 or HTTP 5xx.
4. Validate provider output against `TriageResult`.
5. On any final provider/validation failure, call RuleBasedTriage and persist `triaged_by=rules:fallback`.
6. Record latency/fallback metadata in a Redis list capped to the latest 20 outcomes.
7. Emit exactly one WARNING for the fallback with complaint id, provider and error class.

## Prompt-injection boundary
Complaint text is enclosed in explicit `<complaint_data>` tags and the hosted prompt states that it is untrusted data, never an instruction. Output is constrained to a JSON schema and validated again by Pydantic; no model output is evaluated or used to construct SQL. The test suite submits an injection phrase and verifies that actual complaint content still determines the classification.

## Trusted reverse proxies and rate-limit identity
The rate limiter uses the immediate TCP peer by default. It accepts `X-Forwarded-For` only when that peer belongs to `TRUSTED_PROXY_CIDRS`; untrusted direct callers cannot choose their own bucket by sending a forged forwarding header. nginx overwrites `X-Forwarded-For` with `$remote_addr` before proxying, and Uvicorn proxy-header parsing is disabled so this boundary has one explicit owner. Local Compose defaults to Docker bridge CIDRs; production Compose requires an explicit deployment-specific CIDR, while the Kubernetes ConfigMap must be reviewed against the cluster's Ingress Pod CIDR before deployment.

## Hosted provider reference checked 2026-09-25
Groq's official documentation states that its API is OpenAI-client compatible by changing the base URL to `https://api.groq.com/openai/v1`, and that Structured Outputs can use a `json_schema` response format. The official rate-limit page lists organization-level limits and, for `openai/gpt-oss-20b` on the Free Plan at the time checked, 30 RPM, 1,000 RPD, 8,000 TPM and 200,000 TPD. Limits are changeable: verify again before the final demo.

Sources to re-check during submission:
- https://console.groq.com/docs/openai
- https://console.groq.com/docs/structured-outputs
- https://console.groq.com/docs/rate-limits

## Cache hit-rate measurement
Run a representative replay twice, then query Prometheus metrics:

```bash
curl -s http://localhost:8000/metrics | grep civicpulse_triage_cache_total
```

Compute `hits / (hits + misses)`. Final measured hit rate: **REQUIRES REAL MEASUREMENT BEFORE SUBMISSION**; record the command output in `docs/evidence/triage-cache-metrics.txt`.
