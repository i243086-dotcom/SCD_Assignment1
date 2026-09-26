# ADR 0001 — Replaceable triage provider interface

## Context
CivicPulse depends on classification but must not depend on one inference vendor. Hosted LLMs can be rate-limited or unavailable, local inference has different latency/quality characteristics, and CI must be deterministic.

## Decision
All triage implementations satisfy `TriageProvider` and return the same validated `TriageResult`. `TRIAGE_PROVIDER` selects LLMTriage (Groq), OllamaTriage, RuleBasedTriage or SimulatedTriage. Orchestration, caching, retry and fallback live in `TriageService`, not in routes.

## Alternatives considered
Direct Groq calls from the route were rejected because transport/vendor behavior would leak into HTTP code. A large `if provider == ...` block in the service was rejected because adding providers would modify orchestration. A single hosted provider was rejected because it makes tests flaky and creates a hard availability dependency.

## Consequences
Providers are swappable without changing API or persistence code. Tests can inject deterministic failures. The interface adds small abstraction overhead and requires provider-specific adapters, but failure semantics remain centralized and observable.
