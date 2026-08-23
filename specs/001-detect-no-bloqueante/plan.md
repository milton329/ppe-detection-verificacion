# Implementation Plan: Verificación de EPP sin bloqueo del servicio

**Branch**: `001-detect-no-bloqueante` | **Date**: 2026-08-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-detect-no-bloqueante/spec.md`

## Summary

El endpoint de verificación ejecuta la inferencia dentro del hilo principal de
eventos, congelando el servicio. El enfoque técnico: convertir el manejador de
la ruta a una función síncrona para que el servidor lo despache a su pool de
hilos (todo el pipeline subyacente ya es síncrono), sin alterar el contrato
REST. Además se paga la deuda declarada por la constitución: infraestructura de
pruebas con pytest y pruebas unitarias/integración que cubren la corrección sin
modelo ni red.

## Technical Context

**Language/Version**: Python 3.11 (fijado en `.python-version`), gestionado con `uv`

**Primary Dependencies**: FastAPI + Uvicorn (API/web), Jinja2, ultralytics (solo tras el puerto outbound), Pillow

**Storage**: N/A (sin base de datos; pesos del modelo vía caché de Hugging Face Hub)

**Testing**: pytest (+ httpx para el cliente de pruebas; pytest-cov opcional) — se incorpora en esta feature al grupo dev

**Target Platform**: Servidor local/Docker en CPU (Windows dev, Linux contenedor)

**Project Type**: web-service (arquitectura hexagonal puertos-y-adaptadores)

**Performance Goals**: Presupuestos constitución v1.0.0: inferencia p95 < 2 s por imagen en CPU; `GET /health` < 100 ms

**Constraints**: `make check` (ruff + mypy strict) en verde antes de merge; contrato REST de `POST /detect` y `GET /health` sin cambios rompientes

**Scale/Scope**: Carga baja/moderada (pocas verificaciones concurrentes); 1 endpoint modificado + suite de pruebas inicial

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Evidencia |
|-----------|--------|-----------|
| I. Calidad de Código | ✅ PASS | El cambio vive en el adaptador inbound (`detection_router.py`); límites hexagonales intactos (dominio y aplicación sin tocar); compuerta `make check` se mantiene como criterio de aceptación |
| II. Estándares de Pruebas | ✅ PASS (paga deuda) | La feature incorpora pytest al grupo dev y crea las primeras pruebas en `tests/unit/` e `tests/integration/` usando fakes del puerto outbound (sin modelo ni red), exactamente lo que declara la deuda del principio |
| III. Consistencia de UX | ✅ PASS | Contrato REST estable (FR-003): mismas rutas, firma y formato de respuesta; sin cambios de interfaz web → no requiere actualización de README ni `/help` |
| IV. Rendimiento | ✅ PASS | Mejora el presupuesto de `/health` (< 100 ms) bajo carga: deja de verse afectado por inferencias en curso; los presupuestos de latencia de inferencia no cambian. Nota documentada: la descarga perezosa de pesos en primera petición ya queda cubierta si se ejecuta `make download-model` en preparación (comportamiento actual, sin cambio en esta feature) |

Re-check post-diseño (Phase 1): sin nuevas violaciones — ver `research.md` D1–D4.

## Project Structure

### Documentation (this feature)

```text
specs/001-detect-no-bloqueante/
├── plan.md              # Este archivo (/speckit.plan)
├── research.md          # Phase 0 output (/speckit.plan)
├── data-model.md        # Phase 1 output (/speckit.plan)
├── quickstart.md        # Phase 1 output (/speckit.plan)
├── contracts/           # Phase 1 output (/speckit.plan)
│   └── api.md           #   contrato REST vigente (línea base de regresión)
└── tasks.md             # Phase 2 output (/speckit.tasks — NO creado aquí)
```

### Source Code (repository root)

```text
src/ppe_detection/
├── domain/entities/                  # SIN CAMBIOS
├── application/
│   ├── ports/outbound/detector_port.py   # SIN CAMBIOS (contrato existente habilita el fake)
│   └── use_cases/detect_ppe.py       # SIN CAMBIOS
└── infrastructure/adapters/inbound/
    └── api/routers/detection_router.py   # MODIFICADO: handler síncrono (despacho a threadpool)

tests/
├── unit/
│   ├── __init__.py                   # NUEVO
│   ├── conftest.py                   # NUEVO: fixtures (detector fake, cliente)
│   ├── test_detect_endpoint.py       # NUEVO: contrato de /detect con detector sustituto
│   └── test_detect_handler_offload.py# NUEVO: el handler no es corrutina → threadpool garantizado
└── integration/
    └── (reservado; sin cambios en esta feature)

pyproject.toml                        # MODIFICADO: grupo dev += pytest, pytest-cov, httpx
```

**Structure Decision**: proyecto único existente (opción 1 adaptada al layout
hexagonal real). Las pruebas viven bajo `tests/unit/` según la división que
define el Principio II; no se crean proyectos ni paquetes nuevos.

## Complexity Tracking

> Sin violaciones de constitución que justificar: la tabla queda vacía.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
