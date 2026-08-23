# Phase 0 — Research: Verificación de EPP sin bloqueo del servicio

**Feature**: 001-detect-no-bloqueante | **Date**: 2026-08-23

Unknowns de Technical Context resueltos. Cada decisión sigue el formato
Decisión / Rationale / Alternativas consideradas.

## D1: Cómo liberar el hilo de eventos durante la inferencia

- **Decision**: convertir el manejador de `POST /detect` a función **síncrona**
  (`def`, no `async def`) y leer el archivo subido con su stream síncrono. El
  servidor ejecuta automáticamente los handlers síncronos en su pool de hilos,
  dejando el hilo de eventos libre para `/health`, la web y otras peticiones.
- **Rationale**: todo el pipeline (caso de uso → detector → provider) ya es
  síncrono; nada en este handler se beneficia de `async`. Es el cambio más
  pequeño posible (sin dependencias nuevas, sin utilidades extra) y usa el
  mecanismo estándar del framework.
- **Alternatives considered**:
  - Mantener `async def` y envolver la llamada con `anyio.to_thread.run_sync`:
    mismo resultado con código adicional; no aporta nada aquí porque no hay
    más trabajo asíncrono en el handler. Descartada por simplicidad.
  - Inferencia verdaderamente asíncrona del motor YOLO: el runtime de
    ultralytics es síncrono; requeriría un worker/proceso aparte. Descartada
    por sobredimensionada para la carga esperada (spec, Assumptions).

## D2: Cómo probar el endpoint sin modelo ni red

- **Decision**: pruebas con el cliente de pruebas oficial del framework +
  **override de dependencias** que inyecta un **fake del puerto outbound**
  (`DetectorPort`) que devuelve detecciones predefinidas sin ejecutar modelo.
- **Rationale**: la inyección por dependencias ya existente (Depends +
  lru_cache) fue diseñada justamente para esto; el fake respeta el Protocol
  del puerto, así que la prueba ejercita router + caso de uso + schemas reales
  y solo sustituye la frontera externa. Sin red, sin pesos, milisegundos.
- **Alternatives considered**:
  - Prueba contra el modelo real descargado: lenta, depende de red y de la
    caché; viola SC-004/FR-004. Descartada como prueba automática (queda como
    validación manual en quickstart).
  - Parchear el singleton global del módulo con monkeypatch: frágil y acoplado
    a la implementación; además el singleton ya fue eliminado por inyección.
    Descartada.

## D3: Cómo verificar "no bloquea el hilo de eventos" de forma determinista

- **Decision**: prueba unitaria que afirma que el handler de la ruta **no es
  una función corrutina** (`iscoroutinefunction(...) is False`), condición que
  garantiza por semántica del framework su despacho al pool de hilos.
- **Rationale**: medir concurrencia real con un modelo pesado sería lento e
  inestable en CI; la propiedad "handler síncrono ⇒ fuera del event loop" es
  determinista y suficiente para FR-002 a nivel de pruebas automáticas. La
  evidencia end-to-end (SC-001/SC-002) queda cubierta por quickstart.md como
  validación manual.
- **Alternatives considered**:
  - Test de concurrencia con dos clientes simultáneos y tiempos: posible pero
    ruidoso (depende de timings) y requiere el modelo real o fakes lentos;
    aporta poca certeza extra frente a la aserción estructural. Descartada.

## D4: Incorporación de pytest y dependencias de prueba

- **Decision**: añadir `pytest`, `pytest-cov` y `httpx` al grupo dev en
  `pyproject.toml` vía `uv add --dev`; `httpx` es requisito del cliente de
  pruebas del framework. La configuración `[tool.pytest.ini_options]`
  (testpaths) ya existe; se añade `make test` al Makefile para FR-005.
- **Rationale**: cierra la deuda declarada del Principio II con las herramientas
  mínimas necesarias; gestor exclusivamente `uv` según restricción tecnológica
  de la constitución.
- **Alternatives considered**:
  - Añadir también plugins de cobertura en CI/umbrales de cobertura: fuera de
    alcance; la constitución exige cobertura completa para reglas de negocio,
    que aún no existen (ComplianceRuleService es feature futura). Queda
    anotado como seguimiento.
