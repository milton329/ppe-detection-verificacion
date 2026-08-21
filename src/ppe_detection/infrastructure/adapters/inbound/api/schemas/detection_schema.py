from pydantic import BaseModel

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


class DetectionResponse(BaseModel):
    detections: list[DetectionSchema]
