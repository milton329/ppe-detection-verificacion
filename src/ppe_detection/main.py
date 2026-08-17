from fastapi import FastAPI

from ppe_detection.infrastructure.adapters.inbound.api.routers.detection_router import (
    router as detection_router,
)
from ppe_detection.infrastructure.adapters.inbound.api.routers.health_router import (
    router as health_router,
)

app = FastAPI(title="PPE Detection Verificacion")

app.include_router(health_router)
app.include_router(detection_router)
