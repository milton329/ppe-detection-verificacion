"""Prueba del endpoint de healthcheck (health_router.py)."""

from fastapi.testclient import TestClient

from ppe_detection.main import app

client = TestClient(app)


def test_health_responde_200_con_status_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
