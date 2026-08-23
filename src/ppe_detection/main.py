from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ppe_detection.infrastructure.adapters.inbound.api.routers.detection_router import (
    router as detection_router,
)
from ppe_detection.infrastructure.adapters.inbound.api.routers.health_router import (
    router as health_router,
)
from ppe_detection.infrastructure.adapters.inbound.web.web_router import STATIC_DIR
from ppe_detection.infrastructure.adapters.inbound.web.web_router import (
    router as web_router,
)

app = FastAPI(title="PPE Detection Verificacion")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(health_router)
app.include_router(detection_router)
app.include_router(web_router)
