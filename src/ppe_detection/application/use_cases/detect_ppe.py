from ppe_detection.application.ports.outbound.detector_port import DetectorPort
from ppe_detection.application.use_cases.detection_result import DetectionResult
from ppe_detection.domain.services.compliance_service import evaluate_compliance


class DetectPPEUseCase:
    """Ejecuta la detección y evalúa el cumplimiento de cada persona."""

    def __init__(self, detector: DetectorPort) -> None:
        self._detector = detector

    def execute(self, image_bytes: bytes, confidence: float = 0.25) -> DetectionResult:
        detections = self._detector.detect(image_bytes, confidence)
        return DetectionResult(
            detections=detections,
            compliance=evaluate_compliance(detections),
        )
