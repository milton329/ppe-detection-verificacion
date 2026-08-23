# Phase 1 — Data Model: Verificación de EPP sin bloqueo del servicio

**Feature**: 001-detect-no-bloqueante | **Date**: 2026-08-23

## Conclusión

**Sin cambios en el modelo de datos.** La feature es de comportamiento
(concurrencia/respuesta del servicio), no de información: no crea entidades,
no modifica atributos ni introduce transiciones de estado.

## Entidades existentes que fluyen por el sistema (referencia)

| Entidad | Módulo | Rol en la feature | ¿Cambia? |
|---------|--------|-------------------|----------|
| `Detection` | `domain/entities/detection.py` | Resultado individual (clase, confianza, bbox) que produce la verificación; inmutable (`frozen`) | No |
| `DetectorPort` | `application/ports/outbound/detector_port.py` | Contrato que implementa el detector real y el fake de pruebas | No |
| `DetectPPEUseCase` | `application/use_cases/detect_ppe.py` | Caso de uso que orquesta el puerto; recibe el detector inyectado | No |

## Flujo de datos (sin alteraciones respecto a develop)

```text
imagen (multipart bytes) → caso de uso → DetectorPort → list[Detection]
                                                          → respuesta JSON
```

Única diferencia de comportamiento: el tramo "manejo de la petición HTTP" ya
no se ejecuta en el hilo de eventos del servidor, sino en un hilo de trabajo
del pool. Los datos que entran y salen son idénticos (FR-003 / SC-003).
