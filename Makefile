.PHONY: up down test lint k8s check

up:
	docker compose up --build

down:
	docker compose down

test:
	cd backend && pytest
	cd frontend && npm test

lint:
	cd backend && ruff check app && mypy app
	cd frontend && npm run lint && npm run typecheck

k8s:
	./scripts/k8s_up.sh

check:
	python scripts/check_submission.py
