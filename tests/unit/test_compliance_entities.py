"""Pruebas directas de las entidades del dominio PersonCompliance y
ComplianceReport (domain/entities/compliance.py), sin pasar por el
servicio evaluate_compliance."""

from ppe_detection.domain.entities.compliance import ComplianceReport, PersonCompliance
from ppe_detection.domain.entities.detection import Detection

PERSONA = Detection(class_name="human", confidence=0.9, bbox=(0.0, 0.0, 10.0, 10.0))


def test_person_compliance_es_conforme_con_casco_y_chaleco():
    resultado = PersonCompliance(person=PERSONA, has_helmet=True, has_vest=True)

    assert resultado.is_compliant is True


def test_person_compliance_no_conforme_sin_casco():
    resultado = PersonCompliance(person=PERSONA, has_helmet=False, has_vest=True)

    assert resultado.is_compliant is False


def test_person_compliance_no_conforme_sin_chaleco():
    resultado = PersonCompliance(person=PERSONA, has_helmet=True, has_vest=False)

    assert resultado.is_compliant is False


def test_person_compliance_no_conforme_sin_ningun_epp():
    resultado = PersonCompliance(person=PERSONA, has_helmet=False, has_vest=False)

    assert resultado.is_compliant is False


def test_compliance_report_all_compliant_true_cuando_todos_cumplen():
    reporte = ComplianceReport(
        people=(
            PersonCompliance(person=PERSONA, has_helmet=True, has_vest=True),
            PersonCompliance(person=PERSONA, has_helmet=True, has_vest=True),
        )
    )

    assert reporte.all_compliant is True


def test_compliance_report_all_compliant_false_si_alguno_incumple():
    reporte = ComplianceReport(
        people=(
            PersonCompliance(person=PERSONA, has_helmet=True, has_vest=True),
            PersonCompliance(person=PERSONA, has_helmet=False, has_vest=True),
        )
    )

    assert reporte.all_compliant is False


def test_compliance_report_vacio_se_considera_conforme():
    reporte = ComplianceReport(people=())

    assert reporte.all_compliant is True
