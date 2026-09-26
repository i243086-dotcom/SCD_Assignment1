# ADR 0003 — Deploy immutable commit-SHA image references

## Context
Mutable tags do not answer which source revision is running and make rollback/audit ambiguous. CI must never deploy an artifact that has not passed its test gate.

## Decision
CD builds frontend/backend only after `needs: test`, pushes both to GHCR tagged with `github.sha`, captures digests, then edits the production Kustomize image references to that SHA. The release workflow may also publish semver tags; `latest` is never used for deployment.

## Alternatives considered
Deploying `latest` was rejected as mutable. Rebuilding during deployment was rejected because production would not run the tested artifact. Digest deployment is stronger and is documented as a bonus extension, but SHA tags are the assignment baseline.

## Consequences
`git show <sha>` identifies deployed source, and rollback is either Kubernetes rollout undo or re-applying the previous SHA. Registry retention of SHA-tagged images is required.
