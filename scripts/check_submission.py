from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
failures: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    failures.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def text(path: str) -> str:
    p = ROOT / path
    if not p.exists():
        fail(f'missing required file: {path}')
        return ''
    return p.read_text(encoding='utf-8')


required = [
    'backend/Dockerfile', 'frontend/Dockerfile', 'compose.yaml', 'compose.prod.yaml',
    '.env.example', '.gitignore', 'README.md', 'docs/ENGINEERING-NOTES.md',
    'docs/RUNBOOK.md', 'docs/AI-USAGE.md', 'docs/TRIAGE.md',
    '.github/workflows/ci.yml', '.github/workflows/cd.yml', '.github/workflows/release.yml',
    'k8s/base/hpa.yaml', 'k8s/base/vpa.yaml', 'k8s/base/pdb.yaml',
]
for item in required:
    if not (ROOT / item).exists():
        fail(f'missing required file: {item}')

if (ROOT / '.env').exists():
    fail('.env is present in the repository root; never commit it')
if '.env' not in text('.gitignore'):
    fail('.gitignore does not ignore .env')
if re.search(r'^docs/evidence/\*\.(?:png|jpg|jpeg)$', text('.gitignore'), re.M):
    fail('evidence screenshots are ignored by .gitignore; rubric evidence must be committable')

for dockerfile in ('backend/Dockerfile', 'frontend/Dockerfile'):
    body = text(dockerfile)
    for line in body.splitlines():
        if line.strip().startswith('FROM '):
            image = line.split()[1]
            if ':' not in image and '@' not in image:
                fail(f'unpinned base image in {dockerfile}: {image}')
            if image.endswith(':latest'):
                fail(f'latest base image in {dockerfile}: {image}')
    if not re.search(r'^USER\s+\S+', body, re.M):
        fail(f'no non-root USER declaration in {dockerfile}')

prod = text('compose.prod.yaml')
for service in ('postgres', 'redis'):
    block_match = re.search(rf'^  {service}:\n(?P<body>(?:    .*\n|\n)*)', prod, re.M)
    if block_match and re.search(r'^    ports:', block_match.group('body'), re.M):
        fail(f'{service} publishes a port in compose.prod.yaml')
if 'build:' in prod:
    fail('compose.prod.yaml contains build:')
if ':latest' in prod:
    fail('compose.prod.yaml references :latest')

compose = text('compose.yaml')
if 'internal: true' not in compose:
    fail('compose.yaml is missing internal: true')
if re.search(r'frontend:\n(?:(?:    ).*\n)*?networks:\s*\[[^\]]*internal', compose):
    fail('frontend appears to join the internal network')

k8s_files = list((ROOT / 'k8s').rglob('*.yaml'))
k8s_all = '\n'.join(p.read_text(encoding='utf-8') for p in k8s_files)
if ':latest' in k8s_all:
    fail('Kubernetes manifests deploy :latest')
for manifest in k8s_files:
    for document in manifest.read_text(encoding='utf-8').split('\n---\n'):
        if re.search(r'^kind:\s*Deployment\s*$', document, re.M) and re.search(r'^\s*name:\s*postgres\s*$', document, re.M):
            fail(f'PostgreSQL is declared as a Deployment in {manifest.relative_to(ROOT)}')
if 'kind: StatefulSet' not in text('k8s/base/postgres.yaml'):
    fail('PostgreSQL StatefulSet missing')
if 'volumeClaimTemplates:' not in text('k8s/base/postgres.yaml'):
    fail('PostgreSQL volumeClaimTemplates missing')
if 'updateMode: "Off"' not in text('k8s/base/vpa.yaml'):
    fail('VPA is not in Off mode')
if 'averageUtilization: 60' not in text('k8s/base/hpa.yaml'):
    fail('HPA CPU target is not 60%')

secret = text('k8s/base/secret.yaml')
for key in ('POSTGRES_PASSWORD', 'DATABASE_URL', 'GROQ_API_KEY'):
    if f'${{{key}}}' not in secret:
        fail(f'Kubernetes Secret {key} is not a placeholder')

for workflow in ('ci.yml', 'cd.yml', 'release.yml'):
    body = text(f'.github/workflows/{workflow}')
    if 'permissions:' not in body:
        fail(f'{workflow} has no explicit permissions block')
if 'needs:' not in text('.github/workflows/cd.yml'):
    fail('cd.yml has no needs: dependency gating')
release = text('.github/workflows/release.yml')
release_job = re.search(r'^  release:\n(?P<body>(?:(?:    ).*\n|\n)*)', release, re.M)
if release_job and not re.search(r'^    needs:', release_job.group('body'), re.M):
    fail('release.yml publishing job is not gated by needs:')

for path in ROOT.rglob('*'):
    if not path.is_file() or '.git' in path.parts or path.name == '.env.example':
        continue
    if path.suffix.lower() not in {'.py', '.yml', '.yaml', '.md', '.toml', '.json', '.ts', '.tsx', '.js', '.conf', '.sh', ''}:
        continue
    try:
        body = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        continue
    if re.search(r'(?i)(groq_api_key|api[_-]?key|password)\s*[:=]\s*["\']?[A-Za-z0-9_-]{24,}', body):
        fail(f'possible committed credential in {path.relative_to(ROOT)}')

for evidence in ('branch-protection', 'failed-ci', 'hpa-watch', 'vpa-recommendation', 'rollback'):
    warn(f'manual evidence still required: {evidence}')

for message in warnings:
    print(f'WARN: {message}')
if failures:
    for message in failures:
        print(f'FAIL: {message}')
    print(f'\nSubmission lint failed with {len(failures)} issue(s).')
    raise SystemExit(1)
print('\nSubmission lint passed mechanical checks. Manual evidence is still required.')
