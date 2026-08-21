<!--
SYNC IMPACT REPORT
==================
Version change: N/A (scaffold sin ratificar) -> 1.0.0
Modified principles: (ninguno previo; adopcion inicial)
  - [PRINCIPLE_1_NAME] -> I. Calidad de Codigo (No Negociable)
  - [PRINCIPLE_2_NAME] -> II. Estandares de Pruebas
  - [PRINCIPLE_3_NAME] -> III. Consistencia de Experiencia de Usuario
  - [PRINCIPLE_4_NAME] -> IV. Rendimiento
Added sections:
  - Restricciones Tecnologicas y de Arquitectura
  - Flujo de Trabajo y Compuertas de Calidad
  - Gobernanza
Removed sections: (ninguna)
Follow-up TODOs:
  - Incorporar pytest (+ pytest-cov) al grupo dev de pyproject.toml;
    exigido por el Principio II pero aun no presente en el repositorio.
-->

# Constitución del Proyecto ppe-detection-verificación

Sistema de verificación automática de EPP (casco y chaleco) mediante visión por
computador con YOLOv11 (`melihuzunoglu/ppe-detection`). Esta constitución define
los principios innegociables que gobiernan todas las contribuciones al proyecto.

## Principios Fundamentales

### I. Calidad de Código (NO NEGOCIABLE)

Todo código DEBE respetar los límites de la arquitectura hexagonal (puertos y
adaptadores): `domain/` contiene entidades y reglas de negocio SIN dependencias
externas; las dependencias siempre apuntan hacia el dominio. El repositorio DEBE
mantener `make check` (ruff + mypy `strict`) en verde: cero errores de lint,
cero errores de tipos. Se aplican las reglas ruff configuradas
(`E,F,W,I,UP,B,SIM`, longitud de línea 100). Está PROHIBIDO introducir código
muerto, funciones sin usar o marcadores pendientes sin seguimiento.

**Rationale**: la separación dominio/infraestructura permite testear las reglas
de cumplimiento de EPP sin modelo ni red, y `mypy strict` detecta en tiempo de
desarrollo los errores que en visión por computador serían fallos silenciosos
en producción.

### II. Estándares de Pruebas

Toda funcionalidad nueva o corrección DEBE incluir pruebas que la cubran:

- **Unitarias** (`tests/unit/`): entidades de dominio, casos de uso
  (`DetectPPEUseCase`, futuro `ComplianceRuleService`) con adaptadores
  simulados (mocks/fakes de los puertos).
- **Integración** (`tests/integration/`): contrato de la API REST
  (`POST /detect`, `GET /health`), adaptadores de entrada/salida y renderizado
  web.

El ciclo TDD (rojo-verde-refactorizar) es RECOMENDADO pero no obligatorio; lo
innegociable es que ningún cambio llegue a `main` sin pruebas que lo respalden.
La lógica de negocio (reglas de cumplimiento de casco/chaleco) exige cobertura
de pruebas completa.

> **Deuda declarada**: `pytest` no figura aún en las dev-dependencies. Su
> incorporación es la acción inmediata derivada de este principio; hasta que
> exista, ninguna feature puede considerarse conforme.

**Rationale**: un sistema de detección basado en ML falla de formas no obvias
(umbrales, clases faltantes, imágenes degeneradas); solo las pruebas automatizadas
hacen visibles esas regresiones antes de producción.

### III. Consistencia de Experiencia de Usuario

La interfaz web DEBE mantener una experiencia coherente y predecible:

- Idioma de la interfaz y mensajes: español.
- Patrones visuales y de interacción consistentes entre `/app` (verificación),
  `/help` (ayuda) y futuras pantallas; nuevos elementos reutilizan los
  componentes y estilos existentes (Jinja2 + CSS/JS propios, sin frameworks de
  prototipado).
- Contrato REST estable: `POST /detect` y `GET /health` mantienen su firma;
  cualquier cambio rompiente requiere versión nueva y migración documentada.
- Errores HTTP predecibles y documentados en Swagger (`/docs`): mismos formatos
  de respuesta de error en todos los endpoints.
- El comportamiento de captura por cámara (`getUserMedia`, requisito de HTTPS
  fuera de localhost) DEBE estar documentado en `/help` y en el README.

Cualquier cambio de interfaz o de contrato DEBE actualizar simultáneamente el
README y la página `/help`.

**Rationale**: la herramienta se usa en contextos industriales por usuarios no
técnicos; la previsibilidad reduce errores operativos y costos de soporte.

### IV. Rendimiento

Los siguientes presupuestos son exigibles y verificables:

| Métrica | Presupuesto |
| --- | --- |
| Latencia de inferencia p95 (`POST /detect`) | < 2 s por imagen en CPU |
| Respuesta de `GET /health` | < 100 ms |
| Descarga de pesos del modelo | Solo en instalación/preparación (`make download-model`); NUNCA durante el runtime de inferencia |

Los pesos del modelo DEBEN servirse desde la caché local de Hugging Face Hub
tras la primera descarga. El umbral de confianza por defecto (0.25) DEBE
permanecer documentado en README y `/help`; cambiarlo exige evidencia empírica
(documentada en `docs/pruebas_inferencia_umbrales.md`). Una regresión que
infrinja estos presupuestos BLOQUEA el merge hasta corregirse.

**Rationale**: la verificación de EPP solo es útil si es inmediata; latencias
mayores a 2 s disuaden el uso continuo, y re-descargas de pesos en runtime
provocan timeouts e indisponibilidad.

## Restricciones Tecnológicas y de Arquitectura

- Gestión de dependencias y entornos exclusivamente con `uv`
  (`pyproject.toml` / `uv.lock`); Python >= 3.11 fijado en `.python-version`.
- Stack: FastAPI + Uvicorn, Jinja2 con CSS/JS propios. PROHIBIDO introducir
  Gradio, Streamlit u otros frameworks de prototipado.
- Capas hexagonales obligatorias: `domain/` (sin dependencias externas) ←
  `application/` (casos de uso y puertos inbound/outbound) ←
  `infrastructure/adapters/` (API REST, web, proveedor de modelo YOLO).
- El modelo YOLOv11 se accede SOLO a través del puerto outbound
  (`DetectorPort` / `ModelProviderPort`); ningún caso de uso importa
  directamente `ultralytics`.
- Docker (`make docker-build`) debe seguir construyendo sin pasos manuales
  adicionales.

## Flujo de Trabajo y Compuertas de Calidad

1. `make check` (lint + typecheck) en verde es compuerta OBLIGATORIA antes de
   todo merge.
2. `make format` antes de commit cuando se modifique código Python.
3. Las pruebas nuevas/modificadas deben ejecutarse y pasar; la suite de
   integración debe pasar completa.
4. Cada PR/revisión verifica el cumplimiento de esta constitución; la
   complejidad adicional debe justificarse explícitamente en la descripción.
5. Preparación del entorno: `uv sync` + `make download-model`.

## Gobernanza

Esta constitución PREVALECE sobre cualquier otra práctica, convención o
documento del proyecto. Ante conflicto, manda la constitución.

- **Procedimiento de enmienda**: proponer el cambio en un PR que modifique
  este documento, documentando qué cambia y por qué; las enmiendas requieren
  aprobación explícita y plan de migración si afectan trabajo existente.
- **Política de versionado** (semántico):
  - MAJOR: eliminación o redefinición incompatible de principios/gobernanza.
  - MINOR: nuevo principio, sección o expansión material de la guía.
  - PATCH: aclaraciones, redacción y correcciones sin impacto semántico.
- **Revisión de cumplimiento**: cada revisión de PR comprueba los principios
  I–IV; los incumplimientos bloquean el merge salvo excepción documentada y
  aprobada como enmienda temporal.

**Versión**: 1.0.0 | **Ratificado**: 2026-08-20 | **Última Enmienda**: 2026-08-20
