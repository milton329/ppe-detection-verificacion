from pydantic import BaseModel

from ppe_detection.domain.entities.compliance import ComplianceStatus, PersonCompliance
from ppe_detection.domain.entities.detection import Detection


class DetectionSchema(BaseModel):
    class_name: str
    confidence: float
    bbox: tuple[float, float, float, float]

    @classmethod
    def from_entity(cls, detection: Detection) -> "DetectionSchema":
        return cls(
            class_name=detection.class_name,
            confidence=detection.confidence,
            bbox=detection.bbox,
        )


class PersonComplianceSchema(BaseModel):
    id: int
    status: ComplianceStatus
    helmet: bool
    vest: bool
    confidence: float
    bbox: tuple[float, float, float, float]

    @classmethod
    def from_entity(cls, identifier: int, result: PersonCompliance) -> "PersonComplianceSchema":
        return cls(
            id=identifier,
            status=result.status,
            helmet=result.has_helmet,
            vest=result.has_vest,
            confidence=result.person.confidence,
            bbox=result.person.bbox,
        )


class ComplianceSummarySchema(BaseModel):
    total_persons: int
    compliant: int
    non_compliant: int
    status: ComplianceStatus


class DetectionResponse(BaseModel):
    detections: list[DetectionSchema]
    persons: list[PersonComplianceSchema]
    summary: ComplianceSummarySchema
