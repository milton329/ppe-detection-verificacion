FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# libgl1/libglib2.0-0: requeridos por opencv-python (dependencia de ultralytics)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src

# Instala torch/torchvision CPU-only primero (el índice por defecto de PyPI
# trae build con CUDA, mucho más pesado e innecesario en el droplet).
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu torch torchvision \
    && pip install .

# Descarga los pesos del modelo en tiempo de build para que queden cacheados
# en la imagen (evita depender de Hugging Face Hub en cada arranque).
RUN python -c "from ppe_detection.infrastructure.adapters.outbound.model.huggingface_model_provider import HuggingFaceModelProvider; HuggingFaceModelProvider().get_model_path()"

EXPOSE 8000

CMD ["sh", "-c", "uvicorn ppe_detection.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
