# ADR 0004 — PII minimization for hosted triage

## Context
Municipal complaints can contain phone numbers, email addresses, CNIC-like identifiers, house numbers and detailed locations. A hosted LLM is a third party, so sending raw complaint payloads creates a privacy/data-governance decision.

## Decision
`reporter_contact` never enters `TriageProvider` and never leaves the machine. Before LLMTriage calls Groq, CivicPulse redacts phone numbers, email addresses and CNIC-like identifiers from complaint text and removes explicit house/unit numbers from location. The hosted provider receives only the redacted complaint text and redacted location required for classification. API keys stay in environment/Kubernetes/GitHub secrets and are never logged. Ollama and rules remain available when data must not leave the machine at all.

## Alternatives considered
Sending the entire request was rejected because contact information is unnecessary for classification. Sending complaint text unchanged was rejected because citizens can embed contact identifiers in the free-text field. Sending no location was considered but can materially reduce classification/priority quality for complaints whose risk depends on place context. Fully local Ollama avoids third-party exposure but has higher local compute cost and may classify less accurately.

## Consequences
Hosted inference sees less identifying data while retaining useful context. Regex-based redaction is not a formal anonymization guarantee; highly specific prose can still identify a place/person, so deployments with stricter data rules should select Ollama/rules or add stronger redaction/DLP. This trade-off is explicit rather than hidden.
