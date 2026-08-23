# Contract — API REST (línea base sin cambios)

**Feature**: 001-detect-no-bloqueante | **Date**: 2026-08-23

Este documento fija el contrato vigente que la feature DEBE preservar
(FR-003). Cualquier divergencia detectada en las pruebas es una regresión.

## POST /detect

Verifica EPP sobre una imagen y devuelve las detecciones crudas del modelo.

- **Request**: `multipart/form-data`
  - `file` (obligatorio): imagen (JPEG/PNG).
  - Query `confidence` (opcional, default `0.25`): umbral de confianza.
- **Response** `200 application/json`:

```json
{
  "detections": [
    {
      "class_name": "helmet",
      "confidence": 0.91,
      "bbox": [112.4, 40.2, 188.0, 121.7]
    }
  ]
}
```

- Campos por detección: `class_name` (str), `confidence` (float), `bbox`
  (tupla x1, y1, x2, y2 en píxeles).

## GET /health

- **Response** `200`: estado de salud del servicio.

## Invariantes exigibles a las pruebas

1. `POST /detect` con imagen y detector sustituto responde `200` con el
   esquema anterior y los valores exactos provistos por el sustituto.
2. El parámetro `confidence` llega al puerto como `float`.
3. Ningún cambio de esta feature altera rutas, verbos, códigos de éxito o
   forma de respuesta.
