---
description: "Task list for feature implementation"
---

# Tasks: Verificación de EPP sin bloqueo del servicio

**Input**: Design documents from `/specs/001-detect-no-bloqueante/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅

**Tests**: Incluidos por decisión del usuario (fix + pytest + test) y exigidos
por el Principio II de la constitución v1.0.0.

**Organization**: Agrupadas por historia de usuario para implementación y
prueba independientes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Ejecutable en paralelo (archivos distintos, sin dependencias)
- **[Story]**: Historia de usuario propietaria (US1, US2)
- Rutas exactas incluidas en cada descripción

## Path Conventions

Proyecto único con layout hexagonal: `src/ppe_detection/`, `tests/unit/`
(rutas reales según plan.md; `tests/integration/` queda reservado sin cambios).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Infraestructura de pruebas compartida por ambas historias

- [x] T001 Añadir dependencias de prueba ejecutando `uv add --dev pytest pytest-cov httpx` (actualiza pyproject.toml y uv.lock)
- [x] T002 [P] Añadir atajo `test` al Makefile que ejecute `uv run pytest` (FR-005)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Compuerta previa obligatoria para cualquier historia de usuario

**⚠️ CRITICAL**: Ninguna historia puede empezar hasta completar esta fase

- [x] T003 Ejecutar `uv sync`; verificar compuerta base: `make check` en verde y `uv run pytest` corriendo la suite aún vacía

**Checkpoint**: Infraestructura lista — las historias pueden comenzar

---

## Phase 3: User Story 1 - Servicio responsivo durante una verificación (Priority: P1) 🎯 MVP

**Goal**: El servicio sigue respondiendo otras peticiones mientras procesa una
verificación de EPP (FR-001, FR-002)

**Independent Test**: Con el servicio levantado, enviar una imagen para
verificación y consultar `/health` sin esperar: responde < 1 s mientras la
verificación sigue en curso (detalle en quickstart.md §2)

### Tests for User Story 1 (TDD recomendado por constitución) ⚠️

> **NOTE: Escribir primero; debe FALLAR con el handler async actual**

- [x] T004 [P] [US1] Escribir prueba unitaria que afirme que el handler de POST /detect NO es corrutina (`inspect.iscoroutinefunction`) en tests/unit/test_detect_handler_offload.py

### Implementation for User Story 1

- [x] T005 [US1] Convertir el handler de `POST /detect` a función síncrona (`def detect`, lectura con `file.file.read()`) en src/ppe_detection/infrastructure/adapters/inbound/api/routers/detection_router.py (depends T004)

**Checkpoint**: `uv run pytest` con T004 en verde; `/health` responsivo bajo
inferencia (validación manual opcional con modelo, quickstart.md §2)

---

## Phase 4: User Story 2 - Verificación automatizada sin modelo real (Priority: P2)

**Goal**: Suite automatizada cubre el contrato del endpoint sin pesos ni red
(FR-003, FR-004, SC-004)

**Independent Test**: Desde clon fresco y sin red, `uv run pytest` pasa completo

### Tests for User Story 2

> **NOTE: Estas pruebas protegen el contrato vigente (contracts/api.md); su
> valor es antirregresión, por lo que pueden pasar desde el inicio**

- [x] T006 [US2] Crear fixtures compartidas en tests/unit/conftest.py: detector sustituto que implementa DetectorPort con detecciones predefinidas y cliente de pruebas con override de la dependencia get_detect_ppe_use_case
- [x] T007 [P] [US2] Escribir pruebas de contrato de POST /detect en tests/unit/test_detect_endpoint.py: respuesta 200 con esquema exacto (class_name/confidence/bbox), valores del sustituto y paso del umbral confidence (según contracts/api.md)

### Implementation for User Story 2

- [x] T008 [US2] Verificar suite completa en verde (`uv run pytest`) y cruzar resultados contra los invariantes de specs/001-detect-no-bloqueante/contracts/api.md

**Checkpoint**: Stories 1 y 2 funcionan independientemente; suite protege el
contrato sin modelo ni red

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Compuertas finales de calidad y trazabilidad

- [x] T009 [P] Ejecutar `make format` sobre el código Python modificado (flujo de trabajo constitución, paso 2)
- [x] T010 Ejecutar validación completa de specs/001-detect-no-bloqueante/quickstart.md: sección automatizada obligatoria; secciones manuales (§2-§4) opcionales con modelo descargado; confirmar `make check` verde

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — iniciar inmediatamente; T001 y T002 en paralelo
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEA ambas historias
- **US1 (Phase 3)**: Depende de Foundational; independiente de US2
- **US2 (Phase 4)**: Depende de Foundational; independiente de US1 (puede hacerse en paralelo con US1 si hay capacidad; sus pruebas de contrato son válidas tanto antes como después del cambio del handler)
- **Polish (Phase 5)**: Depende de todas las historias deseadas

### User Story Dependencies

- **User Story 1 (P1)**: Solo Foundational. T005 depende de T004 (rojo→verde)
- **User Story 2 (P2)**: Solo Foundational. T007 depende de T006 (fixtures); T008 cierra

### Within Each User Story

- Tests primero (fallan o protegen), luego implementación
- Handler síncrono antes de re-validar suite completa
- Story completa antes del siguiente checkpoint

### Parallel Opportunities

- T001 ∥ T002 (Setup)
- T006–T007 (US2) pueden ejecutarse mientras US1 está en progreso por otra persona
- T009 es paralelizable con nada crítico (fase final)

---

## Parallel Example: User Story 2

```bash
# Lanzar juntos (archivos distintos):
Task: "Crear fixtures compartidas en tests/unit/conftest.py"
Task: "Escribir pruebas de contrato en tests/unit/test_detect_endpoint.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (CRITICAL — bloquea historias)
3. Completar Phase 3: US1 (TDD: T004 rojo → T005 verde)
4. **STOP and VALIDATE**: quickstart.md §2 manual (opcional) + suite en verde
5. El defecto central queda corregido aunque US2 siga en progreso

### Incremental Delivery

1. Setup + Foundational → fundación lista
2. US1 → validar → defecto corregido (MVP!)
3. US2 → validar → contrato protegido + deuda Principio II saldada
4. Polish → compuertas constitución verificadas

### Single Developer Strategy

Orden secuencial recomendado: T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010

---

## Notes

- [P] = archivos distintos, sin dependencias pendientes
- [Story] traza cada tarea a su historia del spec.md
- Commits tras cada tarea o grupo lógico (constitución: `make format` antes de commit con código Python)
- Detenerse en cada checkpoint para validar la historia de forma independiente
- Evitar: tareas vagas, conflictos de mismo archivo, dependencias entre historias que rompan independencia
