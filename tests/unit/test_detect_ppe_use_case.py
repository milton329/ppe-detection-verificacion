"""Pruebas aisladas de DetectPPEUseCase (application/use_cases/detect_ppe.py),
llamando el caso de uso directamente en vez de a través del endpoint HTTP."""

from ppe_detection.application.use_cases.detect_ppe import DetectPPEUseCase
from ppe_detection.domain.entities.detection import Detection


class FakeDetector:
    """Sustituto mínimo de DetectorPort para probar el caso de uso aislado."""

    def __init__(self, detections: list[Detection] | None = None) -> None:
        self._detections = detections or []
        self.received_bytes: bytes | None = None
        self.received_confidence: float | None = None

    def detect(self, image_bytes: bytes, confidence: float = 0.25) -> list[Detection]:
        self.received_bytes = image_bytes
        self.received_confidence = confidence
        return self._detections


def test_execute_delega_en_el_detector_y_devuelve_su_resultado():
    esperado = [Detection(class_name="human", confidence=0.9, bbox=(0.0, 0.0, 1.0, 1.0))]
    detector = FakeDetector(detections=esperado)
    caso_de_uso = DetectPPEUseCase(detector)

    resultado = caso_de_uso.execute(b"imagen-de-prueba", confidence=0.5)

    assert resultado == esperado


def test_execute_pasa_los_bytes_de_la_imagen_al_detector():
    detector = FakeDetector()
    caso_de_uso = DetectPPEUseCase(detector)

    caso_de_uso.execute(b"contenido-exacto", confidence=0.5)

    assert detector.received_bytes == b"contenido-exacto"


def test_execute_pasa_el_umbral_de_confianza_al_detector():
    detector = FakeDetector()
    caso_de_uso = DetectPPEUseCase(detector)

    caso_de_uso.execute(b"imagen", confidence=0.7)

    assert detector.received_confidence == 0.7


def test_execute_usa_025_como_confianza_por_defecto():
    detector = FakeDetector()
    caso_de_uso = DetectPPEUseCase(detector)

    caso_de_uso.execute(b"imagen")

    assert detector.received_confidence == 0.25


def test_execute_con_detector_que_no_encuentra_nada():
    detector = FakeDetector(detections=[])
    caso_de_uso = DetectPPEUseCase(detector)

    resultado = caso_de_uso.execute(b"imagen-sin-personas")

    assert resultado == []
