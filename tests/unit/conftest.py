"""Fixtures compartidas para las pruebas unitarias del endpoint de detección.

El detector sustituto implementa `DetectorPort` con respuestas fijas: las
pruebas ejercitan router, caso de uso y schemas reales sin modelo, red ni
pesos descargados.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from ppe_detection.application.use_cases.detect_ppe import DetectPPEUseCase
from ppe_detection.domain.entities.detection import Detection
from ppe_detection.infrastructure.adapters.inbound.api.routers.detection_router import (
    get_detect_ppe_use_case,
)
from ppe_detection.main import app


class FakeDetector:
    """Sustituto del puerto outbound: registra el umbral recibido y devuelve
    dos detecciones predefinidas."""

    def __init__(self) -> None:
        self.received_confidence: float | None = None

    def detect(self, image_bytes: bytes, confidence: float = 0.25) -> list[Detection]:
        self.received_confidence = confidence
        return [
            Detection(class_name="helmet", confidence=0.91, bbox=(112.4, 40.2, 188.0, 121.7)),
            Detection(class_name="human", confidence=0.88, bbox=(100.0, 20.0, 200.0, 300.0)),
        ]


@pytest.fixture
def fake_detector() -> FakeDetector:
    return FakeDetector()


@pytest.fixture
def client(fake_detector: FakeDetector) -> Iterator[TestClient]:
    def use_case_sustituto() -> DetectPPEUseCase:
        # Al envolverlo en el caso de uso real, mypy valida que FakeDetector
        # satisface estructuralmente el protocolo DetectorPort.
        return DetectPPEUseCase(fake_detector)

    app.dependency_overrides[get_detect_ppe_use_case] = use_case_sustituto
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
