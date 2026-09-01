"""Escenarios con varias personas en la misma imagen y estados de
cumplimiento mixtos — el caso de uso real del proyecto (una obra con
varios trabajadores, algunos con EPP completo y otros no).

Estas pruebas no suben el porcentaje de cobertura de línea (compliance_service.py
ya estaba en 100%), pero ejercitan una combinación de comportamiento que
ningún test existente prueba: el cruce de MÚLTIPLES personas con MÚLTIPLES
ítems de EPP en la misma imagen.
"""

from ppe_detection.domain.entities.detection import Detection
from ppe_detection.domain.services.compliance_service import evaluate_compliance


def test_dos_personas_una_cumple_y_otra_no():
    persona_1 = Detection(class_name="human", confidence=0.9, bbox=(0.0, 0.0, 100.0, 200.0))
    persona_2 = Detection(class_name="human", confidence=0.9, bbox=(300.0, 0.0, 400.0, 200.0))

    detections = [
        persona_1,
        persona_2,
        # Persona 1: casco y chaleco completos
        Detection(class_name="helmet", confidence=0.9, bbox=(20.0, 10.0, 60.0, 40.0)),
        Detection(class_name="vest", confidence=0.9, bbox=(20.0, 80.0, 80.0, 160.0)),
        # Persona 2: solo casco, sin chaleco
        Detection(class_name="helmet", confidence=0.9, bbox=(320.0, 10.0, 360.0, 40.0)),
    ]

    report = evaluate_compliance(detections)

    assert len(report.people) == 2
    assert report.people[0].is_compliant is True
    assert report.people[1].has_helmet is True
    assert report.people[1].has_vest is False
    assert report.people[1].is_compliant is False
    assert report.all_compliant is False


def test_tres_personas_todas_cumplen():
    personas = [
        Detection(class_name="human", confidence=0.9, bbox=(0.0, 0.0, 100.0, 200.0)),
        Detection(class_name="human", confidence=0.9, bbox=(200.0, 0.0, 300.0, 200.0)),
        Detection(class_name="human", confidence=0.9, bbox=(400.0, 0.0, 500.0, 200.0)),
    ]
    epp = []
    for persona in personas:
        x1, y1, _, _ = persona.bbox
        epp.append(
            Detection(
                class_name="helmet", confidence=0.9, bbox=(x1 + 10, y1 + 10, x1 + 40, y1 + 40)
            )
        )
        epp.append(
            Detection(
                class_name="vest", confidence=0.9, bbox=(x1 + 10, y1 + 60, x1 + 60, y1 + 140)
            )
        )

    report = evaluate_compliance(personas + epp)

    assert len(report.people) == 3
    assert report.all_compliant is True
    assert all(p.is_compliant for p in report.people)


def test_item_de_epp_no_se_asigna_a_una_persona_lejana_aunque_este_libre():
    persona_1 = Detection(class_name="human", confidence=0.9, bbox=(0.0, 0.0, 100.0, 200.0))
    persona_2 = Detection(class_name="human", confidence=0.9, bbox=(500.0, 0.0, 600.0, 200.0))
    # El casco está dentro del área de persona_1, lejos de persona_2
    casco = Detection(class_name="helmet", confidence=0.9, bbox=(20.0, 10.0, 60.0, 40.0))

    report = evaluate_compliance([persona_1, persona_2, casco])

    persona_1_result = next(p for p in report.people if p.person == persona_1)
    persona_2_result = next(p for p in report.people if p.person == persona_2)

    assert persona_1_result.has_helmet is True
    assert persona_2_result.has_helmet is False
