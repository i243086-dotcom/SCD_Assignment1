# Evidence checklist — capture real evidence only

Do not fabricate screenshots, terminal output, Git history, reviews or measurements. Capture and commit evidence from the actual repository/team workflow.

1. `branch-protection.png` — `main` requires PR, required CI checks and at least one approval; direct push disabled.
2. `prs.md` or screenshots — at least 5 merged PRs, each linked to an Issue, each with a substantive partner review comment.
3. `shortlog.txt` — real `git shortlog -sn` output; at least 35 commits and neither partner below 35%.
4. `merge-conflict-*` — a real code conflict with conflict markers/resolution plus 2–4 sentences explaining why the chosen version won.
5. `failed-ci.png` + `blocked-merge.png` — deliberately failing PR check and blocked merge button.
6. `green-ci.png` — same PR corrected and green.
7. `network-isolation.txt/png` — `docker compose exec frontend ping postgres` failing as expected.
8. `compose-persistence.txt/png` — create a complaint, `docker compose down`, `up`, prove row remains.
9. `k8s-postgres-persistence.txt/png` — delete Postgres pod and prove row remains.
10. `hpa-watch.txt` — real `kubectl get hpa -n civicpulse -w` showing backend replicas rise under load.
11. `scaling-data.csv` + `scaling-chart.png` — timestamp, offered VUs/RPS and replica count from the same load run.
12. `vpa-recommendation.txt` — `kubectl describe vpa backend-vpa -n civicpulse` showing Target/Lower/Upper bounds.
13. `rollback-*` — demonstrate both rollout undo and re-applying previous SHA.
14. `zero-downtime-*` — bonus only; load during rolling update and real zero-failure evidence if achieved.
15. UI screenshots — submit/triage result, dashboard/filtering/status transition, stats with visible `X-Cache` HIT/MISS state.
16. Demo video (≤5 min) — both partners speaking: clean clone → running system, AI triage, fallback, network isolation failure, HPA scaling, rollback.
