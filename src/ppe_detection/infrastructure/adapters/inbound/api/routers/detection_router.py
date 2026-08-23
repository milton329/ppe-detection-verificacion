from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

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


@lru_cache(maxsize=1)
def get_detect_ppe_use_case() -> DetectPPEUseCase:
    return DetectPPEUseCase(YoloDetector(HuggingFaceModelProvider()))


DetectPPEUseCaseDep = Annotated[DetectPPEUseCase, Depends(get_detect_ppe_use_case)]


@router.post("/detect", response_model=DetectionResponse)
def detect(
    use_case: DetectPPEUseCaseDep, file: UploadFile, confidence: float = 0.25
) -> DetectionResponse:
    image_bytes = file.file.read()
    detections = use_case.execute(image_bytes, confidence)
    return DetectionResponse(detections=[DetectionSchema.from_entity(d) for d in detections])
