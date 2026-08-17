.PHONY: r download-model

r:
	uv run uvicorn ppe_detection.main:app --reload --app-dir src

download-model:
	uv run python scripts/download_model.py
