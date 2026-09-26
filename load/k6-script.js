import http from 'k6/http'
import { check, sleep } from 'k6'

export const options = {
  stages: [
    { duration: '20s', target: 20 },
    { duration: '40s', target: 80 },
    { duration: '60s', target: 160 },
    { duration: '30s', target: 20 },
    { duration: '20s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.02'],
    http_req_duration: ['p(95)<1500'],
  },
}

const baseUrl = __ENV.BASE_URL || 'http://civicpulse.local'

export default function () {
  const page = 1 + (__VU % 3)
  const response = http.get(`${baseUrl}/api/complaints?page=${page}&page_size=100`, {
    headers: { Host: 'civicpulse.local' },
  })
  check(response, { 'queue responds 200': (r) => r.status === 200 })
  sleep(0.05)
}
