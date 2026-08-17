from typing import Protocol

from ppe_detection.domain.entities.detection import Detection


class DetectorPort(Protocol):
    """Puerto de salida para ejecutar el modelo de detección de objetos
    sobre una imagen. Los adaptadores en
    `infrastructure/adapters/outbound/model/` implementan esta interfaz."""

    def detect(self, image_bytes: bytes, confidence: float = 0.25) -> list[Detection]:
        """Ejecuta la detección sobre una imagen y devuelve las detecciones
        con confianza mayor o igual al umbral indicado."""
        ...
