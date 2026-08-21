"""Descarga (o reutiliza desde caché) los pesos del modelo PPE detection.

Uso:
    uv run python scripts/download_model.py
"""

from ppe_detection.infrastructure.adapters.outbound.model.huggingface_model_provider import (
    HuggingFaceModelProvider,
)


def main() -> None:
    provider = HuggingFaceModelProvider()
    model_path = provider.get_model_path()
    print(f"Modelo disponible en: {model_path}")


if __name__ == "__main__":
    main()
