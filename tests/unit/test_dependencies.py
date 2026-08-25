"""Pruebas del composition root (dependencies.py): verifica que el caso de
uso quede armado con los adaptadores concretos correctos, y que el cacheo
con lru_cache funcione como singleton."""

from ppe_detection.application.use_cases.detect_ppe import DetectPPEUseCase
from ppe_detection.infrastructure.adapters.outbound.model.huggingface_model_provider import (
    HuggingFaceModelProvider,
)
from ppe_detection.infrastructure.adapters.outbound.model.yolo_detector import YoloDetector
from ppe_detection.infrastructure.config.dependencies import get_detect_ppe_use_case


def test_get_detect_ppe_use_case_devuelve_una_instancia_valida():
    use_case = get_detect_ppe_use_case()

    assert isinstance(use_case, DetectPPEUseCase)


def test_el_caso_de_uso_queda_armado_con_yolo_detector():
    use_case = get_detect_ppe_use_case()

    assert isinstance(use_case._detector, YoloDetector)


def test_yolo_detector_queda_armado_con_huggingface_model_provider():
    use_case = get_detect_ppe_use_case()

    assert isinstance(use_case._detector._model_provider, HuggingFaceModelProvider)


def test_get_detect_ppe_use_case_esta_cacheado_como_singleton():
    primera_llamada = get_detect_ppe_use_case()
    segunda_llamada = get_detect_ppe_use_case()

    assert primera_llamada is segunda_llamada
