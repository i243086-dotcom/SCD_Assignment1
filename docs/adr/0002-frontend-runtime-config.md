# ADR 0002 — Same-origin nginx proxy instead of baked API URLs

## Context
Vite replaces `import.meta.env` at build time. Baking a backend URL into the JavaScript bundle would make a frontend image environment-specific and break build-once-deploy-many.

## Decision
The browser calls relative `/api` paths. nginx proxies `/api` to the backend service by Docker/Kubernetes DNS. The same built frontend image therefore runs in laptop Compose, CI and Kubernetes without rebuilding for a different API origin.

## Alternatives considered
A startup-generated `/config.js` was viable but introduces a runtime script and global typing. Build-time `VITE_API_URL` was rejected because each environment would require a new image. Direct browser calls to a second origin were rejected because they create avoidable CORS/runtime configuration work.

## Consequences
One immutable frontend image is portable across environments. nginx becomes responsible for API routing, and local Vite development uses a matching proxy so application code never needs an absolute backend URL.
