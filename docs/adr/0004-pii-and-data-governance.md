# ADR 0004 — PII minimization for hosted triage

## Context

Municipal complaints can contain personally identifiable information (PII), including phone numbers, email addresses, CNIC-like identifiers, house numbers, and detailed locations.

CivicPulse uses Groq as the hosted LLM provider for complaint triage. Because Groq is a third-party hosted service, sending the complete citizen complaint payload would create a privacy and data-governance risk.

The assignment specifically requires the team to document what information leaves the local system, who receives it, and why that exposure is acceptable.

## Decision

CivicPulse minimizes the information sent to the hosted LLM.

The following approach is used:

- `reporter_contact` is not required for complaint classification and should never be sent to the LLM provider.
- Complaint text is treated as untrusted user data.
- Phone numbers, email addresses, CNIC-like identifiers, and similar identifying information should be redacted before hosted inference.
- Location information should be minimized so that only the context required for classification and priority assessment is provided.
- The hosted Groq provider receives only the complaint text and location required for triage, after applicable PII minimization/redaction.
- The Groq API key is stored only in environment variables locally and through Kubernetes/GitHub Secrets for deployment.
- API keys must never be committed to Git, written into screenshots, or logged by the application.
- Rule-based triage and Ollama remain available as alternatives when complaint information must remain entirely on the local machine.

During our testing, CivicPulse successfully used the Groq provider through:

`TRIAGE_PROVIDER=llm`

and reported the active provider as:

`llm:groq`

The API key was stored in the local `.env` file, which is excluded from Git.

## Alternatives considered

### Send the complete complaint request to Groq

Rejected because fields such as `reporter_contact` are unnecessary for determining complaint category, priority, and summary. Sending unnecessary PII would increase privacy exposure without improving the required classification task.

### Send complaint text without any redaction

Rejected because citizens can include phone numbers, email addresses, identification numbers, or other personal information directly inside the free-text complaint field.

### Remove all location information

Considered, but location can provide useful context for prioritization and classification. Therefore, location should be minimized rather than automatically removed completely.

### Use Ollama only

Ollama provides a fully local alternative in which complaint data does not leave the machine. This has privacy advantages, but it requires local compute resources and may provide slower or lower-quality classification depending on the local model and hardware.

## Consequences

This decision reduces the amount of personally identifiable information exposed to a third-party LLM provider while preserving enough complaint context for useful triage.

PII redaction is not a guarantee of complete anonymization. Highly specific complaint descriptions or locations may still indirectly identify a person or property.

For environments with stricter privacy requirements, CivicPulse should use the local Ollama provider or rule-based triage, or introduce stronger data-loss-prevention and redaction controls before sending information to any hosted provider.

The privacy trade-off is therefore documented explicitly rather than being hidden from operators or users.