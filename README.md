# ppe-detection-verificacion

Sistema de verificación automática de EPP (casco y chaleco) en entornos industriales mediante visión por computador, usando el modelo preentrenado YOLOv11 `melihuzunoglu/ppe-detection`.

## Arquitectura

Arquitectura hexagonal (puertos y adaptadores):

- `domain/` — entidades y reglas de negocio (sin dependencias externas). Por
  ahora solo la entidad `Detection`; el `ComplianceRuleService` (¿la persona
  cumple con casco/chaleco?) está pendiente de implementar.
- `application/` — casos de uso (`DetectPPEUseCase`) y puertos
  (`inbound`/`outbound`).
- `infrastructure/adapters/inbound/` — adaptadores de entrada:
  - `api/` — endpoints REST (FastAPI), ej. `POST /detect`.
  - `web/` — interfaz web (Jinja2 + CSS/JS propios, sin Gradio/Streamlit),
    servida por el mismo FastAPI en `/app`.
- `infrastructure/adapters/outbound/model/` — adaptadores de salida:
  `HuggingFaceModelProvider` (descarga los pesos) y `YoloDetector` (ejecuta
  la inferencia).

## Cómo levantar el proyecto

Este proyecto se gestiona con [uv](https://docs.astral.sh/uv/). La versión de Python
queda fijada en `.python-version` y las dependencias resueltas en `uv.lock`.

```bash
uv sync
uv run uvicorn ppe_detection.main:app --reload --app-dir src
```

`uv sync` crea el entorno virtual (`.venv`) e instala el proyecto junto con sus
dependencias a partir de `pyproject.toml` / `uv.lock`.

Atajo con `make` (equivale al `uv run uvicorn ...` de arriba):

```bash
make r
```

Luego abre **http://127.0.0.1:8000/app** — interfaz web para subir una imagen
(o tomar una foto con la cámara del PC/celular) y ver las detecciones
dibujadas sobre ella. Incluye menú con:

- **Verificación** (`/app`) — la pantalla principal.
- **Ayuda** (`/help`) — qué detecta el modelo, cómo funciona el umbral de
  confianza, consejos para buenas fotos y limitaciones conocidas.
- **Documentación API** (`/docs`) — Swagger autogenerado por FastAPI.

`/` redirige automáticamente a `/app`. `/health` sigue disponible para checks
de salud del servicio.

### Endpoints REST

- `POST /detect?confidence=0.25` — recibe una imagen (`multipart/form-data`,
  campo `file`) y devuelve las detecciones crudas del modelo (clase,
  confianza, caja delimitadora), sin aplicar todavía reglas de cumplimiento.
- `GET /health` — healthcheck.

## Descarga del modelo

Los pesos del modelo `melihuzunoglu/ppe-detection` (YOLOv11) se descargan desde
Hugging Face Hub mediante `hf_hub_download`, a través del adaptador
`HuggingFaceModelProvider`
(`src/ppe_detection/infrastructure/adapters/outbound/model/huggingface_model_provider.py`).

```bash
make download-model
```

El archivo `best.pt` queda cacheado en `~/.cache/huggingface/hub/` (no se
vuelve a descargar en ejecuciones posteriores). No requiere autenticación al
ser un repositorio público, aunque configurar `HF_TOKEN` evita límites de
tasa más estrictos.

<details>
<summary>Alternativa con pip + venv</summary>

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e .
uvicorn ppe_detection.main:app --reload --app-dir src
```

</details>

## Captura por cámara

La interfaz web permite tomar la foto directo desde la cámara (PC o celular)
usando `getUserMedia`, sin subir ningún archivo previo. Funciona sin HTTPS
mientras se accede por `localhost`/`127.0.0.1`, porque los navegadores tratan
esas direcciones como contexto seguro. **En producción (Docker, servidor
remoto) la cámara solo funcionará si el sitio se sirve por HTTPS.**

## Documentación adicional

- [`docs/pruebas_inferencia_umbrales.md`](docs/pruebas_inferencia_umbrales.md) —
  pruebas iniciales de inferencia, ajuste de umbral de confianza, y hallazgo
  sobre las limitaciones del modelo con fotos de estudio/banco de imágenes.
