from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('civicpulse_http_requests_total', 'HTTP requests', ['method', 'path', 'status'])
REQUEST_LATENCY = Histogram('civicpulse_http_request_duration_seconds', 'HTTP request latency', ['method', 'path'])
TRIAGE_LATENCY = Histogram('civicpulse_triage_duration_seconds', 'Triage provider latency', ['provider'])
TRIAGE_FALLBACKS = Counter('civicpulse_triage_fallback_total', 'Triage fallbacks', ['provider', 'error_class'])
TRIAGE_CACHE = Counter('civicpulse_triage_cache_total', 'Triage cache outcomes', ['result'])
