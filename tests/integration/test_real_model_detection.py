"""Pruebas de integración: usan el modelo YOLO REAL (descargado de Hugging
Face) contra las imágenes reales de docs/evidencia/. No mockean nada.

A diferencia de tests/unit, estas pruebas:
- Requieren conexión a internet la primera vez (para descargar los pesos).
- Tardan varios segundos (carga del modelo + inferencia real).
- Pueden ser sensibles a cambios de versión de ultralytics/el modelo.

Por eso NO corren con el comando normal (`pytest tests/unit`). Se ejecutan
aparte, a propósito, con:

    uv run pytest tests/integration -v -m integration

o, si el marker "integration" está registrado en pyproject.toml:

    uv run pytest -m integration

Ver docs/pruebas_inferencia_umbrales.md para el detalle de los hallazgos
sobre limitaciones del modelo con fotografía de estudio.
"""

from pathlib import Path

import pytest

from ppe_detection.infrastructure.adapters.outbound.model.huggingface_model_provider import (
    HuggingFaceModelProvider,
)
from ppe_detection.infrastructure.adapters.outbound.model.yolo_detector import YoloDetector

EVIDENCIA_DIR = Path(__file__).resolve().parents[2] / "docs" / "evidencia"

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def detector() -> YoloDetector:
    """El modelo se descarga/carga una sola vez para todo el módulo de
    pruebas (no por cada test), porque es costoso."""
    return YoloDetector(HuggingFaceModelProvider())


def _cargar_imagen(nombre: str) -> bytes:
    ruta = EVIDENCIA_DIR / nombre
    assert ruta.exists(), f"No se encontró la imagen de evidencia: {ruta}"
    return ruta.read_bytes()


def test_modelo_real_detecta_al_menos_una_persona_en_imagen_con_epp(detector: YoloDetector):
    imagen = _cargar_imagen("hombre_casco_chaleco.jpg")

    detecciones = detector.detect(imagen, confidence=0.25)

    clases_detectadas = {d.class_name for d in detecciones}
    assert "human" in clases_detectadas, (
        f"Se esperaba detectar al menos una persona. Clases detectadas: {clases_detectadas}"
    )


def test_modelo_real_detecta_casco_en_imagen_con_epp(detector: YoloDetector):
    imagen = _cargar_imagen("hombre_casco_chaleco.jpg")

    detecciones = detector.detect(imagen, confidence=0.25)

    clases_detectadas = {d.class_name for d in detecciones}
    assert "helmet" in clases_detectadas, (
        f"Se esperaba detectar un casco. Clases detectadas: {clases_detectadas}"
    )


@pytest.mark.xfail(
    reason=(
        "Hallazgo documentado en docs/pruebas_inferencia_umbrales.md: el modelo "
        "no detecta 'vest' en hombre_casco_chaleco.jpg ni siquiera a confidence=0.01, "
        "pese a que el chaleco es claramente visible. Se atribuye a que es una foto "
        "de estudio (fondo sólido, pose posada) — un tipo de imagen distinto al que "
        "probablemente vio el modelo en entrenamiento (fotos reales de obra). "
        "Pendiente: re-evaluar con el banco de imágenes reales de David (Etapa 1)."
    ),
    strict=True,
)
def test_modelo_real_detecta_chaleco_en_imagen_con_epp(detector: YoloDetector):
    imagen = _cargar_imagen("hombre_casco_chaleco.jpg")

    detecciones = detector.detect(imagen, confidence=0.25)

    clases_detectadas = {d.class_name for d in detecciones}
    assert "vest" in clases_detectadas, (
        f"Se esperaba detectar un chaleco. Clases detectadas: {clases_detectadas}"
    )


def test_todas_las_detecciones_superan_el_umbral_de_confianza_pedido(detector: YoloDetector):
    imagen = _cargar_imagen("deteccion_conf_0.25.jpg")
    umbral = 0.25

    detecciones = detector.detect(imagen, confidence=umbral)

    assert all(d.confidence >= umbral for d in detecciones), (
        "El modelo devolvió una detección con confianza menor al umbral solicitado"
    )


def test_bounding_boxes_tienen_coordenadas_validas(detector: YoloDetector):
    imagen = _cargar_imagen("hombre_casco_chaleco.jpg")

    detecciones = detector.detect(imagen, confidence=0.25)

    assert len(detecciones) > 0, "No se detectó nada en una imagen que sí tiene EPP visible"
    for d in detecciones:
        x1, y1, x2, y2 = d.bbox
        assert x1 < x2, f"x1 debería ser menor que x2 en {d.class_name}: {d.bbox}"
        assert y1 < y2, f"y1 debería ser menor que y2 en {d.class_name}: {d.bbox}"
        assert x1 >= 0 and y1 >= 0, f"Coordenadas negativas inesperadas en {d.class_name}: {d.bbox}"
