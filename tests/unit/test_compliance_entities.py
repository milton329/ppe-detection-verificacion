"""Pruebas directas de las entidades del dominio PersonCompliance y
ComplianceReport (domain/entities/compliance.py), sin pasar por el
servicio evaluate_compliance."""

from ppe_detection.domain.entities.compliance import ComplianceReport, PersonCompliance
from ppe_detection.domain.entities.detection import Detection

PERSONA = Detection(class_name="human", confidence=0.9, bbox=(0.0, 0.0, 10.0, 10.0))


def test_person_compliance_es_conforme_con_casco_y_chaleco():
    resultado = PersonCompliance(person=PERSONA, has_helmet=True, has_vest=True)

    assert resultado.is_compliant is True
    assert resultado.status.value == "COMPLIANT"


def test_person_compliance_no_conforme_sin_casco():
    resultado = PersonCompliance(person=PERSONA, has_helmet=False, has_vest=True)

    assert resultado.is_compliant is False
    assert resultado.status.value == "NON_COMPLIANT"


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


def test_compliance_report_vacio_no_se_considera_conforme():
    reporte = ComplianceReport(people=())

    assert reporte.all_compliant is False
    assert reporte.status.value == "NO_PERSONS"


def test_compliance_report_informa_estado_global_no_conforme_si_falla_una_persona():
    reporte = ComplianceReport(
        people=(
            PersonCompliance(person=PERSONA, has_helmet=True, has_vest=True),
            PersonCompliance(person=PERSONA, has_helmet=False, has_vest=True),
        )
    )

    assert reporte.status.value == "NON_COMPLIANT"
    assert reporte.compliant_count == 1
    assert reporte.non_compliant_count == 1
