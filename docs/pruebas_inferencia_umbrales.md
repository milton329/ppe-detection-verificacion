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



## Hallazgo adicional: chaleco no detectado en foto de estudio individual

**Tarea:** Pruebas de integración con modelo real — rama `test/integracion-modelo-real`.
**Script:** `tests/integration/test_real_model_detection.py`
**Imagen usada:** `docs/evidencia/hombre_casco_chaleco.jpg` — a diferencia de
`sample_image.jpg` (el collage original), esta es una foto individual, con
una sola persona, casco y chaleco ambos claramente visibles y sin ninguna
obstrucción.

### Resultado

| Umbral | Detecciones |
|---|---|
| 0.25 | `helmet` 0.699, `human` 0.552 |
| 0.01 (solo diagnóstico) | `helmet` 0.699, `human` 0.552, `no-helmet` 0.177 |

**El chaleco no aparece en ningún umbral, ni siquiera a 0.01.** No es un
problema de calibración de umbral como en el hallazgo anterior — el modelo
simplemente no reconoce el chaleco en esta imagen bajo ninguna confianza.

### Hipótesis

A diferencia del caso de `sample_image.jpg` (donde el problema era el
collage de 4 escenas), aquí la imagen ya es individual y el EPP es
completamente visible para un observador humano. La causa más probable es
el **tipo de fotografía**: `hombre_casco_chaleco.jpg` es una foto de estudio
posada, con fondo de color sólido e iluminación de estudio — muy distinta a
las fotos de obra real (fondos de construcción, iluminación natural, ángulos
de cámara de seguridad) con las que probablemente se entrenó el modelo.

Esto sugiere que la limitación no es exclusiva de imágenes tipo collage, sino
más ampliamente de **fotografía de banco de imágenes / estudio** en general,
reforzando la recomendación ya hecha en el hallazgo anterior.

### Conclusión y recomendación

- Se marca la prueba correspondiente como `xfail` (fallo esperado y
  documentado) en `tests/integration/test_real_model_detection.py`, en vez
  de eliminarla — así el test sigue sirviendo como registro verificable del
  problema, y si en el futuro el modelo (o las imágenes de evidencia)
  cambian y el chaleco sí se detecta, el `xfail` fallará de forma visible
  (`strict=True`), avisando que hay que actualizar la documentación.
- Se refuerza la recomendación ya hecha por Milton: **no calibrar ni
  validar el módulo de cumplimiento con fotografía de estudio/banco de
  imágenes** — se necesita el banco de imágenes reales de David (Etapa 1)
  para obtener resultados representativos del caso de uso real (obra de
  construcción).
- **Pendiente:** repetir esta prueba también con el set de imágenes reales
  de David en cuanto esté disponible.

### Cómo reproducir

```bash
uv run pytest tests/integration -v
```

O para ver el detalle de confianza por clase a un umbral bajo:
```bash
uv run python -c "
from ppe_detection.infrastructure.adapters.outbound.model.huggingface_model_provider import HuggingFaceModelProvider
from ppe_detection.infrastructure.adapters.outbound.model.yolo_detector import YoloDetector
from pathlib import Path

detector = YoloDetector(HuggingFaceModelProvider())
imagen = Path('docs/evidencia/hombre_casco_chaleco.jpg').read_bytes()
for d in detector.detect(imagen, confidence=0.01):
    print(f'{d.class_name}: {d.confidence:.3f}')
"
```
