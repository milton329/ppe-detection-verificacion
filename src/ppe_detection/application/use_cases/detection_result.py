from dataclasses import dataclass

from ppe_detection.domain.entities.compliance import ComplianceReport
from ppe_detection.domain.entities.detection import Detection


@dataclass(frozen=True)
class DetectionResult:
    detections: list[Detection]
    compliance: ComplianceReport
