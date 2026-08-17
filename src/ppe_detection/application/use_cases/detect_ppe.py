from ppe_detection.application.ports.outbound.detector_port import DetectorPort
from ppe_detection.domain.entities.detection import Detection


class DetectPPEUseCase:
    """Caso de uso: ejecutar la detección de EPP sobre una imagen.

    Por ahora devuelve las detecciones crudas del modelo (persona, casco,
    sin-casco, chaleco). La lógica de reglas de cumplimiento (¿la persona
    tiene puesto el EPP requerido?) se aplica en un paso posterior, sobre
    el resultado de este caso de uso.
    """

    def __init__(self, detector: DetectorPort) -> None:
        self._detector = detector

    def execute(self, image_bytes: bytes, confidence: float = 0.25) -> list[Detection]:
        return self._detector.detect(image_bytes, confidence)
