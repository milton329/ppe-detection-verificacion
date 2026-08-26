from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from ppe_detection.application.use_cases.detect_ppe import DetectPPEUseCase
from ppe_detection.infrastructure.adapters.inbound.api.schemas.detection_schema import (
    ComplianceSummarySchema,
    DetectionResponse,
    DetectionSchema,
    PersonComplianceSchema,
)
from ppe_detection.infrastructure.config.dependencies import get_detect_ppe_use_case

router = APIRouter(tags=["detection"])

DetectPPEUseCaseDep = Annotated[DetectPPEUseCase, Depends(get_detect_ppe_use_case)]


@router.post("/detect", response_model=DetectionResponse)
def detect(
    use_case: DetectPPEUseCaseDep, file: UploadFile, confidence: float = 0.25
) -> DetectionResponse:
    image_bytes = file.file.read()
    result = use_case.execute(image_bytes, confidence)
    report = result.compliance
    return DetectionResponse(
        detections=[DetectionSchema.from_entity(d) for d in result.detections],
        persons=[
            PersonComplianceSchema.from_entity(identifier, person)
            for identifier, person in enumerate(report.people, start=1)
        ],
        summary=ComplianceSummarySchema(
            total_persons=len(report.people),
            compliant=report.compliant_count,
            non_compliant=report.non_compliant_count,
            status=report.status,
        ),
    )
