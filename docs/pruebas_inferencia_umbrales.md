# Pruebas iniciales de inferencia y ajuste de umbrales

**Tarea:** Etapa 1 del cronograma — Milton Jaramillo.
**Script:** `scripts/test_inference.py`
**Modelo:** `melihuzunoglu/ppe-detection` (YOLOv11), vía `HuggingFaceModelProvider`.
**Imagen usada:** `sample_image.jpg` del propio repositorio del modelo en Hugging Face.

## Resultados por umbral de confianza

| Umbral | Detecciones |
|---|---|
| 0.15 | `human` 0.88, `human` 0.16 |
| 0.25 | `human` 0.88 |
| 0.35 | `human` 0.88 |
| 0.50 | `human` 0.88 |

Con un umbral aún más bajo (0.01, solo para diagnóstico) sí aparecen `helmet`,
`no-helmet` y `vest`, pero todos con confianza menor a 0.13 — muy por debajo
de un umbral utilizable.

## Hallazgo clave

`sample_image.jpg` **no es una foto de prueba individual**: es un collage
promocional de 4 escenas distintas con overlays de texto ("PPE Detection
YOLOv11") y cajas ya dibujadas de una demo anterior del autor del modelo. Al
comprimir 4 escenas en una sola imagen, cada persona ocupa una fracción muy
pequeña del cuadro, lo que degrada la confianza de las detecciones de casco y
chaleco (aunque la clase `human` sigue detectándose bien, con 0.88).

Ver evidencia en `docs/evidencia/deteccion_conf_0.25.jpg`.

## Conclusión y recomendación

- No es posible calibrar de forma confiable el umbral de casco/chaleco con
  esta única imagen — se necesita el banco de imágenes curado por David
  (tarea paralela de Etapa 1: "Recopilación y curación de imágenes de
  prueba", escenarios reales con y sin EPP, una persona por escena).
- Como punto de partida provisional para el módulo de reglas de cumplimiento
  (Etapa 2), se recomienda `conf=0.25` (valor por defecto habitual en YOLO):
  es lo bastante alto para filtrar el ruido visto en `conf=0.15` (la segunda
  detección `human` a 0.16 es un falso positivo/recorte parcial) sin ser tan
  restrictivo como 0.5.
- **Pendiente:** repetir esta prueba con el set de imágenes reales de David
  en cuanto esté disponible, y ajustar el umbral de casco/chaleco con datos
  representativos.

## Cómo reproducir

```bash
uv run python scripts/test_inference.py
```

Genera las imágenes anotadas por umbral en
`tests/fixtures/inference_output/` (no versionado, se regenera localmente).
