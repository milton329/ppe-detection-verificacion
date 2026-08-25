"""Pruebas del router web (infrastructure/adapters/inbound/web/web_router.py):
verifica las rutas de la interfaz que muestra la imagen procesada y el
estado de cumplimiento.

Nota: estas pruebas verifican status code, redirecciones y tipo de
contenido. No hacen aserciones sobre texto específico dentro de los
templates (index.html/help.html) porque no se revisó su contenido interno
— si quieres validar textos puntuales (títulos, botones, etc.), se pueden
ampliar una vez confirmemos el HTML real.
"""

from fastapi.testclient import TestClient

from ppe_detection.main import app

client = TestClient(app)


def test_root_redirige_a_app():
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/app"


def test_app_responde_200_con_html():
    response = client.get("/app")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_help_responde_200_con_html():
    response = client.get("/help")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_app_y_help_devuelven_contenido_no_vacio():
    respuesta_app = client.get("/app")
    respuesta_help = client.get("/help")

    assert len(respuesta_app.text) > 0
    assert len(respuesta_help.text) > 0


def test_ruta_raiz_no_aparece_en_el_schema_openapi():
    # root_redirect() usa include_in_schema=False explícitamente en el código;
    # confirmamos que "/" no aparece en la documentación autogenerada de Swagger.
    schema = client.get("/openapi.json").json()

    assert "/" not in schema["paths"]
