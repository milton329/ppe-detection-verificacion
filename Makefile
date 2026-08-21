.PHONY: r run download-model lint typecheck check format docker-build

r: run

run:
	uv run uvicorn ppe_detection.main:app --reload --app-dir src

download-model:
	uv run python scripts/download_model.py

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy .

check: lint typecheck

docker-build:
	docker build -t ppe-detection-verificacion .
