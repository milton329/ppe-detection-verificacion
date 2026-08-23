"""Composition root: cablea los casos de uso con sus adapters outbound concretos.

Los adapters inbound (routers) dependen de las funciones de este módulo en
vez de instanciar adapters outbound directamente, para no acoplar el lado
HTTP a implementaciones concretas de infraestructura.
"""

from functools import lru_cache

from ppe_detection.application.use_cases.detect_ppe import DetectPPEUseCase
from ppe_detection.infrastructure.adapters.outbound.model.huggingface_model_provider import (
    HuggingFaceModelProvider,
)
from ppe_detection.infrastructure.adapters.outbound.model.yolo_detector import YoloDetector


@lru_cache(maxsize=1)
def get_detect_ppe_use_case() -> DetectPPEUseCase:
    return DetectPPEUseCase(YoloDetector(HuggingFaceModelProvider()))
