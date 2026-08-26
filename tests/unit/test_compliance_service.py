"""Pruebas del servicio de dominio que evalúa cumplimiento de EPP."""

from ppe_detection.domain.entities.detection import Detection
from ppe_detection.domain.services.compliance_service import evaluate_compliance

PERSON_BBOX = (100.0, 20.0, 200.0, 300.0)


def _person() -> Detection:
    return Detection(class_name="human", confidence=0.88, bbox=PERSON_BBOX)


def test_persona_con_casco_y_chaleco_cumple() -> None:
    detections = [
        _person(),
        Detection(class_name="helmet", confidence=0.9, bbox=(120.0, 30.0, 160.0, 60.0)),
        Detection(class_name="vest", confidence=0.9, bbox=(120.0, 100.0, 180.0, 200.0)),
    ]

    report = evaluate_compliance(detections)

    assert len(report.people) == 1
    assert report.people[0].is_compliant
    assert report.all_compliant


def test_persona_sin_casco_no_cumple() -> None:
    detections = [
        _person(),
        Detection(class_name="vest", confidence=0.9, bbox=(120.0, 100.0, 180.0, 200.0)),
    ]

    report = evaluate_compliance(detections)

    assert report.people[0].has_helmet is False
    assert report.people[0].is_compliant is False
    assert report.all_compliant is False


def test_no_helmet_explicito_invalida_casco_superpuesto() -> None:
    detections = [
        _person(),
        Detection(class_name="helmet", confidence=0.4, bbox=(120.0, 30.0, 160.0, 60.0)),
        Detection(class_name="no-helmet", confidence=0.9, bbox=(120.0, 30.0, 160.0, 60.0)),
        Detection(class_name="vest", confidence=0.9, bbox=(120.0, 100.0, 180.0, 200.0)),
    ]

    report = evaluate_compliance(detections)

    assert report.people[0].has_helmet is False
    assert report.all_compliant is False


def test_persona_sin_ningun_epp_cercano_no_cumple() -> None:
    detections = [_person()]

    report = evaluate_compliance(detections)

    assert report.people[0].has_helmet is False
    assert report.people[0].has_vest is False
    assert report.all_compliant is False


def test_epp_fuera_de_la_bbox_de_la_persona_no_cuenta() -> None:
    detections = [
        _person(),
        Detection(class_name="helmet", confidence=0.9, bbox=(500.0, 500.0, 540.0, 540.0)),
    ]

    report = evaluate_compliance(detections)

    assert report.people[0].has_helmet is False


def test_reporte_vacio_sin_personas_no_es_conforme_y_tiene_estado_no_persons() -> None:
    report = evaluate_compliance([])

    assert report.people == ()
    assert report.all_compliant is False
    assert report.status.value == "NO_PERSONS"
