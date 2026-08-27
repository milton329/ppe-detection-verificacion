"""Prueba de ensamblaje de main.py: verifica que la app FastAPI final quede
con TODAS las rutas registradas correctamente, no cada router por separado.

Esto complementa a los tests de cada router individual (health_router,
detection_router, web_router): aquí se prueba que main.py los una bien,
que es justo el tipo de error que un test por-router no detecta (por
ejemplo, olvidar un app.include_router()).

Nota: se usa el schema de /openapi.json en vez de inspeccionar app.routes
directamente, porque la representación interna de app.routes cambia entre
versiones de FastAPI/Starlette (dejó de exponer `.path` en cada entrada de
forma directa) — el schema OpenAPI es un contrato público y estable.
"""

from fastapi.testclient import TestClient

from ppe_detection.main import app

client = TestClient(app)


def _openapi_paths() -> set[str]:
    schema = client.get("/openapi.json").json()
    return set(schema["paths"].keys())


def test_la_app_registra_la_ruta_de_health():
    assert "/health" in _openapi_paths()


def test_la_app_registra_la_ruta_de_deteccion():
    assert "/detect" in _openapi_paths()


def test_la_app_registra_las_rutas_web():
    rutas = _openapi_paths()

    assert "/app" in rutas
    assert "/help" in rutas


def test_las_tres_rutas_principales_responden_simultaneamente():
    # No es suficiente que existan: confirmamos que las tres FUNCIONAN
    # al mismo tiempo, dentro de la misma instancia de app ya ensamblada.
    salud = client.get("/health")
    interfaz = client.get("/app")
    ayuda = client.get("/help")

    assert salud.status_code == 200
    assert interfaz.status_code == 200
    assert ayuda.status_code == 200


def test_openapi_incluye_el_endpoint_de_deteccion_documentado():
    schema = client.get("/openapi.json").json()

    assert "/detect" in schema["paths"]
    assert "post" in schema["paths"]["/detect"]
