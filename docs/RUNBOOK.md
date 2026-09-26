# CivicPulse operations runbook

## Deploy
Local Compose: `docker compose up -d --build`. Local Kubernetes: `./scripts/k8s_up.sh`. CI production-style deployment is `.github/workflows/cd.yml`: tests gate image publication, SHA-tagged images are pushed, then an ephemeral kind cluster applies the production overlay.

Production Compose requires immutable image tags and a trusted-proxy CIDR. Create a local, uncommitted environment file with real deployment values, then run:

```bash
export GHCR_OWNER=<owner-or-organization>
export IMAGE_TAG=<immutable-commit-sha>
export POSTGRES_DB=civicpulse POSTGRES_USER=civicpulse POSTGRES_PASSWORD='<secret>'
export TRUSTED_PROXY_CIDRS='<reverse-proxy-cidr>'
docker compose -f compose.prod.yaml up -d
```

## Check workload status

```bash
kubectl get pods,deploy,statefulset,svc,ingress,hpa -n civicpulse
kubectl rollout status deployment/backend -n civicpulse
kubectl rollout status deployment/frontend -n civicpulse
kubectl get events -n civicpulse --sort-by=.lastTimestamp
```

## Read structured logs

```bash
kubectl logs -n civicpulse deployment/backend --tail=200
kubectl logs -n civicpulse deployment/backend -f | jq .
```

Search a user-visible `X-Request-ID` in logs to follow one request. A triage fallback WARNING includes `complaint_id`, provider and error class.

## Troubleshoot readiness
`/health` must remain 200 as long as the process is alive. `/ready` is allowed to return 503 and names `postgres`, `redis`, or both.

```bash
kubectl port-forward -n civicpulse service/backend 8000:8000
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/ready
```

If health fails, inspect the backend process/container. If only readiness fails, do not restart-loop the backend; investigate the named dependency.

## PostgreSQL failure

```bash
kubectl get pod -n civicpulse -l app=postgres
kubectl logs -n civicpulse statefulset/postgres
kubectl get pvc -n civicpulse
kubectl exec -n civicpulse statefulset/postgres -- pg_isready -U civicpulse -d civicpulse
```

Deleting the Postgres pod should recreate it against the same StatefulSet PVC. Verify a known complaint before/after the deletion as persistence evidence.

## Redis failure

```bash
kubectl get pod -n civicpulse -l app=redis
kubectl logs -n civicpulse deployment/redis
kubectl exec -n civicpulse deployment/redis -- redis-cli ping
kubectl get pvc redisdata -n civicpulse
```

Redis AOF is persisted on a PVC/named volume. While Redis is unavailable `/ready` returns 503 and POST rate limiting returns 503 rather than silently replacing the distributed limiter with an incorrect in-process counter.

## Triage / LLM failure
1. Check `/api/meta/providers` for active provider, latency and fallback flags.
2. Search backend WARNING logs by request id/complaint id.
3. Check Groq HTTP/rate-limit status and `GROQ_API_KEY` secret presence without printing its value.
4. Keep service available: fallback should persist `rules:fallback` rather than return 500.
5. If the hosted provider is degraded, set `TRIAGE_PROVIDER=rules` (or Ollama after its model is available), apply config and restart backend.

Never log or echo the API key during troubleshooting.

## Rate-limit problems
A genuine exceeded window returns 429 with `Retry-After`. Unexpected 503 on POST indicates Redis/rate-limiter infrastructure is unavailable. Confirm client IP handling through the proxy and inspect Redis keys only in a safe environment.

## Rollback mechanism 1 — imperative emergency
Use during an active incident when the immediately previous ReplicaSet is known-good:

```bash
kubectl rollout history deployment/backend -n civicpulse
kubectl rollout undo deployment/backend -n civicpulse
kubectl rollout status deployment/backend -n civicpulse
curl -H 'Host: civicpulse.local' http://127.0.0.1/api/complaints?page=1
```

This is fast but changes cluster state imperatively, so follow with the declarative record below.

## Rollback mechanism 2 — declarative/auditable
Identify the previous good Git commit/SHA-tagged images. Set both image references in the production overlay to that SHA, render with secrets at deploy time, apply, and wait for rollouts:

```bash
cd k8s/overlays/prod
kustomize edit set image \
  ghcr.io/OWNER/civicpulse-backend=ghcr.io/<owner>/civicpulse-backend:<previous-sha> \
  ghcr.io/OWNER/civicpulse-frontend=ghcr.io/<owner>/civicpulse-frontend:<previous-sha>
cd ../../..
kustomize build k8s/overlays/prod | envsubst | kubectl apply -f -
kubectl rollout status deployment/backend -n civicpulse
```

Use this once the immediate incident is controlled because it restores the cluster to an auditable desired state.

## Zero-downtime rollout evidence (bonus)
Run k6 continuously, change the backend image, and record failed requests:

```bash
k6 run -e BASE_URL=http://civicpulse.local load/k6-script.js
kubectl set image deployment/backend backend=ghcr.io/<owner>/civicpulse-backend:<new-sha> -n civicpulse
kubectl rollout status deployment/backend -n civicpulse
```

Final observed failures: **REQUIRES REAL MEASUREMENT BEFORE SUBMISSION**. Do not claim zero until measured.
