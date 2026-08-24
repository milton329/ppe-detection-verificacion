"""Pruebas del schema Pydantic (infrastructure/.../detection_schema.py) de
forma aislada, sin pasar por el endpoint HTTP."""

from ppe_detection.domain.entities.detection import Detection
from ppe_detection.infrastructure.adapters.inbound.api.schemas.detection_schema import (
    DetectionResponse,
    DetectionSchema,
)


def test_from_entity_copia_todos_los_campos_de_la_deteccion():
    deteccion = Detection(class_name="vest", confidence=0.77, bbox=(1.0, 2.0, 3.0, 4.0))

    schema = DetectionSchema.from_entity(deteccion)

    assert schema.class_name == "vest"
    assert schema.confidence == 0.77
    assert schema.bbox == (1.0, 2.0, 3.0, 4.0)


def test_detection_response_agrupa_varias_detecciones():
    detecciones = [
        Detection(class_name="human", confidence=0.9, bbox=(0.0, 0.0, 1.0, 1.0)),
        Detection(class_name="helmet", confidence=0.8, bbox=(0.1, 0.1, 0.9, 0.9)),
    ]

    respuesta = DetectionResponse(
        detections=[DetectionSchema.from_entity(d) for d in detecciones]
    )

    assert len(respuesta.detections) == 2
    assert respuesta.detections[0].class_name == "human"
    assert respuesta.detections[1].class_name == "helmet"


def test_detection_response_con_lista_vacia():
    respuesta = DetectionResponse(detections=[])

    assert respuesta.detections == []
