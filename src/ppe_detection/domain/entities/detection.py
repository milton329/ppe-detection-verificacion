from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    """Una detección individual devuelta por el modelo: una clase
    (`human`, `helmet`, `no-helmet`, `vest`) con su confianza y caja
    delimitadora en píxeles (x1, y1, x2, y2)."""

    class_name: str
    confidence: float
    bbox: tuple[float, float, float, float]
