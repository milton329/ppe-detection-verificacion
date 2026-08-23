"""US2: contrato de POST /detect verificado con detector sustituto.

Línea base: specs/001-detect-no-bloqueante/contracts/api.md. Cualquier
divergencia aquí es una regresión del contrato REST.
"""

from fastapi.testclient import TestClient

from tests.unit.conftest import FakeDetector


def test_detect_responde_200_con_esquema_del_contrato(
    client: TestClient,
) -> None:
    response = client.post(
        "/detect",
        params={"confidence": 0.3},
        files={"file": ("imagen.png", b"datos-imagen", "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"detections"}
    assert len(body["detections"]) == 2

    primera = body["detections"][0]
    assert set(primera.keys()) == {"class_name", "confidence", "bbox"}
    assert primera == {
        "class_name": "helmet",
        "confidence": 0.91,
        "bbox": [112.4, 40.2, 188.0, 121.7],
    }

    segunda = body["detections"][1]
    assert segunda["class_name"] == "human"
    assert segunda["bbox"] == [100.0, 20.0, 200.0, 300.0]


def test_detect_pasa_el_umbral_de_confianza_al_detector(
    client: TestClient, fake_detector: FakeDetector
) -> None:
    response = client.post(
        "/detect",
        params={"confidence": 0.4},
        files={"file": ("imagen.png", b"datos-imagen", "image/png")},
    )

    assert response.status_code == 200
    assert fake_detector.received_confidence is not None
    assert abs(fake_detector.received_confidence - 0.4) < 1e-9


def test_detect_usa_umbral_por_defecto_025(client: TestClient, fake_detector: FakeDetector) -> None:
    response = client.post("/detect", files={"file": ("imagen.png", b"datos-imagen", "image/png")})

    assert response.status_code == 200
    assert fake_detector.received_confidence is not None
    assert abs(fake_detector.received_confidence - 0.25) < 1e-9
