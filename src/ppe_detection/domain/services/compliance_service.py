"""Regla de negocio: evaluar el cumplimiento de EPP a partir de detecciones crudas."""

from ppe_detection.domain.entities.compliance import ComplianceReport, PersonCompliance
from ppe_detection.domain.entities.detection import Detection

_HELMET_CLASSES = {"helmet"}
_NO_HELMET_CLASSES = {"no-helmet"}
_VEST_CLASSES = {"vest"}


def _center(bbox: tuple[float, float, float, float]) -> tuple[float, float]:
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def _center_within(item_bbox: tuple[float, float, float, float],
                    person_bbox: tuple[float, float, float, float]) -> bool:
    cx, cy = _center(item_bbox)
    px1, py1, px2, py2 = person_bbox
    return px1 <= cx <= px2 and py1 <= cy <= py2


def evaluate_compliance(detections: list[Detection]) -> ComplianceReport:
    """Cruza cada persona detectada con el EPP cuya caja cae dentro de la suya.

    Una persona tiene casco si existe una detección `helmet` cuyo centro cae
    dentro de su bbox y ninguna detección `no-helmet` con centro también
    dentro de su bbox la contradice. El chaleco se evalúa de forma análoga.
    """
    people = [d for d in detections if d.class_name == "human"]
    helmets = [d for d in detections if d.class_name in _HELMET_CLASSES]
    no_helmets = [d for d in detections if d.class_name in _NO_HELMET_CLASSES]
    vests = [d for d in detections if d.class_name in _VEST_CLASSES]

    evaluations = tuple(
        PersonCompliance(
            person=person,
            has_helmet=(
                any(_center_within(h.bbox, person.bbox) for h in helmets)
                and not any(_center_within(nh.bbox, person.bbox) for nh in no_helmets)
            ),
            has_vest=any(_center_within(v.bbox, person.bbox) for v in vests),
        )
        for person in people
    )
    return ComplianceReport(people=evaluations)
