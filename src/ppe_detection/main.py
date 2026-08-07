from fastapi import FastAPI

from ppe_detection.infrastructure.adapters.inbound.api.routers.health_router import (
    router as health_router,
)

app = FastAPI(title="PPE Detection Verificacion")

app.include_router(health_router)
