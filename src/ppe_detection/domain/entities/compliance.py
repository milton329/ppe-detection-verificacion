"""Entidades de dominio para el reporte de cumplimiento de EPP."""

from dataclasses import dataclass

from ppe_detection.domain.entities.detection import Detection


@dataclass(frozen=True)
class PersonCompliance:
    """Resultado de evaluar el EPP de una persona detectada."""

    person: Detection
    has_helmet: bool
    has_vest: bool

    @property
    def is_compliant(self) -> bool:
        return self.has_helmet and self.has_vest


@dataclass(frozen=True)
class ComplianceReport:
    """Reporte agregado de cumplimiento para todas las personas de una imagen.

    `all_compliant` es verdadero cuando ninguna persona incumple (incluido
    el caso vacío: sin personas detectadas no hay incumplimientos, aunque
    tampoco verificación positiva).
    """

    people: tuple[PersonCompliance, ...]

    @property
    def all_compliant(self) -> bool:
        return all(p.is_compliant for p in self.people)
