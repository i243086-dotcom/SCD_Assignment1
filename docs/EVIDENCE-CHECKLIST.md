# CivicPulse evidence checklist

This repository contains code and documentation evidence only. Do not fabricate screenshots, output, history, measurements, or links. Each item below requires a real run in the student's own repository or environment.

## GitHub and collaboration

1. Configure `main` branch protection to require pull requests, all CI checks, and one approval. Capture the GitHub settings screen as `docs/evidence/branch-protection.png`.
2. Create genuine Issues, feature branches, partner review comments, and at least five merged PRs. Capture each PR/Issue relationship and review in GitHub.
3. Capture the real contribution split with `git shortlog -sn | tee docs/evidence/git-shortlog.txt` and calculate each collaborator's percentage from the resulting commit counts.
4. Preserve a real, resolved conflict from normal work. Capture the conflict markers, resolution, and merge in `docs/evidence/merge-conflict.md`, with a short explanation of the chosen resolution.

## Docker and Compose

```bash
docker compose up -d --build
docker compose ps
docker compose exec frontend ping postgres
docker compose exec postgres psql -U civicpulse -d civicpulse -c 'select count(*) from complaints;'
docker compose down
docker compose up -d
docker compose exec postgres psql -U civicpulse -d civicpulse -c 'select count(*) from complaints;'
docker image ls civicpulse-backend civicpulse-frontend
```

Save actual output/screenshots for network isolation, persistence, image sizes, and build-context measurements under `docs/evidence/`. For context size, use `docker build --no-cache --progress=plain backend` and `frontend` and preserve the `transferring context` lines.

## Kubernetes and HPA

```bash
make k8s
kubectl get hpa -n civicpulse -w | tee docs/evidence/hpa-watch.txt
k6 run -e BASE_URL=http://civicpulse.local load/k6-script.js
kubectl get hpa -n civicpulse -o wide
kubectl get deploy backend -n civicpulse -o jsonpath='{.status.replicas}{"\n"}'
kubectl delete pod -n civicpulse -l app=postgres
kubectl get pods -n civicpulse -w
```

Record each observation as `timestamp,offered_load,replicas` in `docs/evidence/hpa-results.csv`, then render the required chart:

```bash
python -m pip install matplotlib
python scripts/plot_hpa_results.py docs/evidence/hpa-results.csv
```

## VPA

```bash
kubectl describe vpa backend-vpa -n civicpulse | tee docs/evidence/vpa-recommendation.txt
kubectl get deployment backend -n civicpulse -o yaml | tee docs/evidence/backend-before-vpa.yaml
```

Copy the real Target, Lower Bound, and Upper Bound into `docs/ENGINEERING-NOTES.md`; update backend resource requests only after reviewing those measurements. Re-run the HPA sequence and capture the before/after behavior.

## CI/CD and rollback

1. Open a real PR with one deliberately failing test; capture the failed required check and blocked merge control.
2. Repair the test in the same PR and capture the green pipeline.
3. Merge through protected `main`, then save the real `cd.yml` run URL and GHCR SHA-tagged package links.
4. Demonstrate both `kubectl rollout undo deployment/backend -n civicpulse` and reapplying a previous immutable SHA; capture commands and rollout status.

## Five-minute demo sequence

1. Clean clone and `docker compose up --build`.
2. Submit a complaint and show the triage result/provider.
3. Force and show the deterministic fallback.
4. Show stats cache `MISS` then `HIT`.
5. Show the frontend-to-PostgreSQL isolation failure.
6. Show the real HPA scaling capture and chart.
7. Show an immutable-SHA rollback.

Both team members should speak and be able to explain the code shown.
