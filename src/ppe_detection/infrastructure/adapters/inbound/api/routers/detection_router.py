from fastapi import APIRouter, UploadFile

from ppe_detection.application.use_cases.detect_ppe import DetectPPEUseCase
from ppe_detection.infrastructure.adapters.inbound.api.schemas.detection_schema import (
    DetectionResponse,
    DetectionSchema,
)
from ppe_detection.infrastructure.adapters.outbound.model.huggingface_model_provider import (
    HuggingFaceModelProvider,
)
from ppe_detection.infrastructure.adapters.outbound.model.yolo_detector import YoloDetector

router = APIRouter(tags=["detection"])

_use_case = DetectPPEUseCase(YoloDetector(HuggingFaceModelProvider()))


@router.post("/detect", response_model=DetectionResponse)
async def detect(file: UploadFile, confidence: float = 0.25) -> DetectionResponse:
    image_bytes = await file.read()
    detections = _use_case.execute(image_bytes, confidence)
    return DetectionResponse(
        detections=[DetectionSchema.from_entity(d) for d in detections]
    )
