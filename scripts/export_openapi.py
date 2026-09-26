from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
os.environ.setdefault('TRIAGE_PROVIDER', 'simulated')

from app.main import app  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='frontend/openapi.json')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = ROOT / args.output
    rendered = json.dumps(app.openapi(), indent=2, sort_keys=True) + '\n'
    if args.check:
        if not target.exists() or target.read_text(encoding='utf-8') != rendered:
            print(f'OpenAPI snapshot is stale: run python scripts/export_openapi.py --output {args.output}')
            return 1
        print('OpenAPI snapshot is current.')
        return 0
    target.write_text(rendered, encoding='utf-8')
    print(f'Wrote {target}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
