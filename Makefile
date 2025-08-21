.PHONY: dev run lint test docker up down retry-queue dev-rebuild dev-api

dev:
	docker compose run --service-ports dev

run:
	. .venv/bin/activate && python -m signalhub.app

lint:
	ruff src/signalhub

test:
	pytest

docker:
	docker build -t signalhub .

up:
	docker compose up -d

down:
	docker compose down

retry-queue:
	. .venv/bin/activate && python -c 'from signalhub.queue import replay_queue; from signalhub.pushover import send_message; import os; replay_queue(os.getenv("QUEUE_DIR", "./queue"), send_message)'

dev-rebuild:
	docker compose down -v --remove-orphans dev
	docker compose build dev
	make dev

dev-api:
	python -m uvicorn src.signalhub.api.main:app --reload --host 0.0.0.0 --port 8000
