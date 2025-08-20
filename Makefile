.PHONY: dev run lint test docker up down retry-queue

dev:
	python -m venv .venv && . .venv/bin/activate && pip install --upgrade pip && pip install .[dev]

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
