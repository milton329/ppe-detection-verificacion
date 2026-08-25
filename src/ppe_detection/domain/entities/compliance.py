"""Entidades de dominio para el reporte de cumplimiento de EPP."""

from dataclasses import dataclass
from enum import StrEnum

from ppe_detection.domain.entities.detection import Detection


class ComplianceStatus(StrEnum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    NO_PERSONS = "NO_PERSONS"


@dataclass(frozen=True)
class PersonCompliance:
    """Resultado de evaluar el EPP de una persona detectada."""

    person: Detection
    has_helmet: bool
    has_vest: bool

    @property
    def is_compliant(self) -> bool:
        return self.has_helmet and self.has_vest

    @property
    def status(self) -> ComplianceStatus:
        if self.is_compliant:
            return ComplianceStatus.COMPLIANT
        return ComplianceStatus.NON_COMPLIANT


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
        return bool(self.people) and all(p.is_compliant for p in self.people)

    @property
    def status(self) -> ComplianceStatus:
        if not self.people:
            return ComplianceStatus.NO_PERSONS
        if self.all_compliant:
            return ComplianceStatus.COMPLIANT
        return ComplianceStatus.NON_COMPLIANT

    @property
    def compliant_count(self) -> int:
        return sum(person.is_compliant for person in self.people)

    @property
    def non_compliant_count(self) -> int:
        return len(self.people) - self.compliant_count
