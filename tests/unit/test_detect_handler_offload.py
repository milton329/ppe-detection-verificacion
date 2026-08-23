"""US1: el manejo de /detect no debe ejecutarse en el hilo de eventos.

Un handler síncrono es despachado por FastAPI al pool de hilos, de modo que
la inferencia (trabajo pesado y bloqueante) no congela el event loop.
"""

import inspect

from ppe_detection.infrastructure.adapters.inbound.api.routers.detection_router import (
    detect,
)


def test_detect_handler_no_es_corrutina() -> None:
    assert not inspect.iscoroutinefunction(detect)
