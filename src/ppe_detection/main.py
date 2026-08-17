from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ppe_detection.infrastructure.adapters.inbound.api.routers.detection_router import (
    router as detection_router,
)
from ppe_detection.infrastructure.adapters.inbound.api.routers.health_router import (
    router as health_router,
)
from ppe_detection.infrastructure.adapters.inbound.web.web_router import (
    router as web_router,
)

app = FastAPI(title="PPE Detection Verificacion")

_static_dir = Path(__file__).resolve().parent / "infrastructure" / "adapters" / "inbound" / "web" / "static"
app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

app.include_router(health_router)
app.include_router(detection_router)
app.include_router(web_router)
