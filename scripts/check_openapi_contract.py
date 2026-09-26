from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))

from app.main import app  # noqa: E402


REQUIRED_METHODS = {
    '/api/complaints': {'get', 'post'},
    '/api/complaints/{complaint_id}': {'get'},
    '/api/complaints/{complaint_id}/status': {'patch'},
    '/api/stats': {'get'},
    '/api/meta/providers': {'get'},
    '/health': {'get'},
    '/ready': {'get'},
    '/metrics': {'get'},
}

FRONTEND_TYPED_PATHS = {
    '/api/complaints',
    '/api/complaints/{complaint_id}',
    '/api/complaints/{complaint_id}/status',
    '/api/stats',
    '/api/meta/providers',
}


def main() -> int:
    document = app.openapi()
    paths = document.get('paths', {})
    failures: list[str] = []

    for path, methods in REQUIRED_METHODS.items():
        actual = paths.get(path)
        if actual is None:
            failures.append(f'OpenAPI missing path: {path}')
            continue
        for method in methods:
            if method not in actual:
                failures.append(f'OpenAPI missing method: {method.upper()} {path}')

    surface = (ROOT / 'frontend/src/api/schema.d.ts').read_text(encoding='utf-8')
    for path in FRONTEND_TYPED_PATHS:
        if f"'{path}'" not in surface:
            failures.append(f'frontend typed API surface missing path: {path}')

    schemas = document.get('components', {}).get('schemas', {})
    for schema_name in ('Category', 'Priority', 'Status'):
        values = schemas.get(schema_name, {}).get('enum', [])
        for value in values:
            if f"'{value}'" not in surface:
                failures.append(f'frontend typed API surface missing {schema_name} enum value: {value}')

    if failures:
        for failure in failures:
            print(f'FAIL: {failure}')
        return 1
    print('OpenAPI contract check passed: backend routes and frontend typed surface agree on required paths/enums.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
