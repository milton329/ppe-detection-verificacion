# ppe-detection-verificacion

![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)
![uv](https://img.shields.io/badge/managed%20with-uv-DE5FE9)
![Ruff](https://img.shields.io/badge/lint-ruff-D7FF64?logo=ruff&logoColor=black)
![pytest](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)
![Docker](https://img.shields.io/badge/container-docker-2496ED?logo=docker&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Sistema de verificación automática de EPP (casco y chaleco) en entornos
industriales mediante visión por computador, usando el modelo preentrenado
YOLOv11 [`melihuzunoglu/ppe-detection`](https://huggingface.co/melihuzunoglu/ppe-detection).

## Tabla de contenidos

- [Vista previa](#vista-previa)
- [Stack tecnológico](#stack-tecnológico)
- [Arquitectura](#arquitectura)
- [Cómo levantar el proyecto](#cómo-levantar-el-proyecto)
- [Endpoints REST](#endpoints-rest)
- [Descarga del modelo](#descarga-del-modelo)
- [Captura por cámara](#captura-por-cámara)
- [Pruebas unitarias](#pruebas-unitarias)
- [Deploy](#deploy)
- [Herramientas de desarrollo con IA](#herramientas-de-desarrollo-con-ia)
- [Documentación adicional](#documentación-adicional)
- [Licencia](#licencia)

## Vista previa

| Pantalla principal | Resultado de detección |
|---|---|
| ![Interfaz de verificación](docs/img/interfaz-principal.png) | ![Resultado con detecciones dibujadas](docs/img/resultado-deteccion.png) |

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| API / backend | [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn |
| Modelo de detección | YOLOv11 (`melihuzunoglu/ppe-detection`) vía [Ultralytics](https://docs.ultralytics.com/) |
| Descarga de pesos | [Hugging Face Hub](https://huggingface.co/docs/huggingface_hub) |
| Interfaz web | Jinja2 + CSS/JS propios (sin Gradio/Streamlit) |
| Imágenes | Pillow |
| Gestión de dependencias | [uv](https://docs.astral.sh/uv/) |
| Contenedor / deploy | Docker + DigitalOcean (vía GitLab CI/CD) |
| Pruebas | pytest + pytest-cov |
| Lint / tipos | ruff + mypy |

## Arquitectura

Arquitectura hexagonal (puertos y adaptadores):

- `domain/` — entidades y reglas de negocio (sin dependencias externas),
  incluyendo `Detection`, las entidades de cumplimiento y la evaluación de
  casco/chaleco por persona.
- `application/` — casos de uso (`DetectPPEUseCase`) y puertos
  (`inbound`/`outbound`).
- `infrastructure/adapters/inbound/` — adaptadores de entrada:
  - `api/` — endpoints REST (FastAPI), ej. `POST /detect`.
  - `web/` — interfaz web (Jinja2 + CSS/JS propios, sin Gradio/Streamlit),
    servida por el mismo FastAPI en `/app`.
- `infrastructure/adapters/outbound/model/` — adaptadores de salida:
  `HuggingFaceModelProvider` (descarga los pesos) y `YoloDetector` (ejecuta
  la inferencia).

### Flujo de verificación

El flujo actual es:

```text
imagen → detección YOLO → detecciones → evaluación de cumplimiento → respuesta API → panel
```

El backend es la única fuente de verdad para el cumplimiento. El panel
presenta los estados y valores recibidos de la API, sin recalcular las reglas.

El estado global de `summary.status` puede ser:

- `COMPLIANT` — todas las personas detectadas cumplen con casco y chaleco.
- `NON_COMPLIANT` — al menos una persona detectada no cumple.
- `NO_PERSONS` — no se detectaron personas.

Cada elemento de `persons` también incluye su estado individual (`COMPLIANT` o
`NON_COMPLIANT`), además de indicar si tiene casco y chaleco.

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

<details>
<summary>Alternativa con pip + venv</summary>

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e .
uvicorn ppe_detection.main:app --reload --app-dir src
```

</details>

## Endpoints REST

- `POST /detect?confidence=0.25` — recibe una imagen (`multipart/form-data`,
  campo `file`) y devuelve las detecciones crudas junto con la evaluación de
  cumplimiento. La respuesta contiene `detections`, `persons` y `summary`.
- `GET /health` — healthcheck.

Ejemplo breve de respuesta de `POST /detect`:

```json
{
  "detections": [
    {
      "class_name": "human",
      "confidence": 0.88,
      "bbox": [100.0, 20.0, 200.0, 300.0]
    }
  ],
  "persons": [
    {
      "id": 1,
      "status": "COMPLIANT",
      "helmet": true,
      "vest": true,
      "confidence": 0.88,
      "bbox": [100.0, 20.0, 200.0, 300.0]
    }
  ],
  "summary": {
    "total_persons": 1,
    "compliant": 1,
    "non_compliant": 0,
    "status": "COMPLIANT"
  }
}
```

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

## Captura por cámara

La interfaz web permite tomar la foto directo desde la cámara (PC o celular)
usando `getUserMedia`, sin subir ningún archivo previo. Funciona sin HTTPS
mientras se accede por `localhost`/`127.0.0.1`, porque los navegadores tratan
esas direcciones como contexto seguro. **En producción (Docker, servidor
remoto) la cámara solo funcionará si el sitio se sirve por HTTPS.**

### Pruebas unitarias

56 pruebas, con 100% de cobertura de línea sobre `src/ppe_detection`. Todas
mockean el modelo y cualquier dependencia externa (Hugging Face, red), por
lo que corren en segundos y no requieren internet.

```bash
uv sync
uv run pytest tests/unit -v
```

Con reporte de cobertura:
```bash
uv run pytest tests/unit --cov=src/ppe_detection --cov-report=term-missing
```

**Qué cubren:**

| Módulo | Qué se prueba |
|---|---|
| `domain/entities/compliance.py` | Propiedades de cumplimiento (`is_compliant`, estado global) |
| `domain/services/compliance_service.py` | Regla de negocio: cruce de personas con casco/chaleco, incluyendo casos de una y de varias personas con estados mixtos en la misma imagen |
| `application/use_cases/detect_ppe.py` | Caso de uso, aislado de HTTP y del modelo real |
| `infrastructure/adapters/outbound/model/yolo_detector.py` | Adaptador YOLO: mapeo de resultados a entidades, carga perezosa del modelo, umbral de confianza |
| `infrastructure/adapters/outbound/model/huggingface_model_provider.py` | Descarga de pesos desde Hugging Face Hub (mockeada) |
| `infrastructure/config/dependencies.py` | Composition root: wiring correcto de adaptadores y cacheo como singleton |
| `infrastructure/adapters/inbound/api/routers/detection_router.py` | Endpoint `POST /detect`: contrato de respuesta, umbral de confianza, ejecución no bloqueante |
| `infrastructure/adapters/inbound/api/routers/health_router.py` | Endpoint `GET /health` |
| `infrastructure/adapters/inbound/web/web_router.py` | Rutas de la interfaz web (`/`, `/app`, `/help`) |
| `infrastructure/adapters/inbound/api/schemas/detection_schema.py` | Conversión de entidades de dominio a schemas Pydantic |
| `main.py` | Ensamblaje completo de la app: que todos los routers queden registrados y respondan juntos (verificado vía `/openapi.json`, no inspeccionando `app.routes` directamente, para no depender de detalles internos que cambian entre versiones de FastAPI) |

### Pruebas de integración (modelo real)

5 pruebas que usan el modelo YOLOv11 real (descargado de Hugging Face) contra
imágenes reales de `docs/evidencia/`. No mockean nada — por eso están
separadas del suite normal: requieren red la primera vez y tardan más.

```bash
uv run pytest tests/integration -v
```

**Resultado esperado:** `4 passed, 1 xfailed`. El `xfail` es intencional y
está documentado — ver más abajo.

###  Limitación conocida: fotografía de estudio

El modelo detecta con buena confianza personas (`human`) y, en general,
cascos (`helmet`), pero **puede no detectar el chaleco (`vest`) en
fotografías de estudio** (fondo de color sólido, pose posada, iluminación
artificial) — incluso cuando el chaleco es perfectamente visible para un
observador humano. En pruebas de integración, esto ocurrió incluso bajando
el umbral de confianza a 0.01.

La causa probable es que el modelo fue entrenado con fotos reales de obra
(fondos de construcción, iluminación natural), un contexto visual distinto
al de la fotografía de banco de imágenes/estudio. Esta limitación está
cubierta por una prueba marcada como `xfail` (fallo esperado y
documentado) en `tests/integration/test_real_model_detection.py.

## Deploy

El proyecto incluye lo necesario para desplegarse como contenedor.

### Docker

```bash
make docker-build
docker run -p 8000:8000 ppe-detection-verificacion
```

El `Dockerfile` construye la imagen e instala dependencias con `uv`; `.dockerignore`
excluye archivos de desarrollo local (entorno virtual, caché, specs, etc.).

### CI/CD y despliegue

El repositorio se espeja automáticamente a GitLab
(`.github/workflows/mirror-gitlab.yml`, push mirror en cada commit a `main`,
ya que el pull mirroring de GitLab.com requiere plan Premium). El pipeline
`.gitlab-ci.yml` corre en ese espejo con tres etapas:

1. **test** — `pytest` + `ruff` + `mypy`.
2. **build** — construye la imagen Docker y la sube al Container Registry
   de GitLab.
3. **deploy** — se conecta por SSH a un droplet de DigitalOcean, hace pull
   de la imagen y reinicia el contenedor.

> **Nota:** la captura por cámara (ver [sección anterior](#captura-por-cámara))
> solo funciona en producción si el sitio se sirve por HTTPS.

## Herramientas de desarrollo con IA

El proyecto usa ayudas de desarrollo asistido con IA (Spec Kit y agent
skills), opcionales para ejecutar la aplicación. Ver
[`docs/desarrollo-ia.md`](docs/desarrollo-ia.md) para instrucciones de
instalación y uso.

## Documentación adicional

- [`docs/pruebas_inferencia_umbrales.md`](docs/pruebas_inferencia_umbrales.md) —
  pruebas iniciales de inferencia, ajuste de umbral de confianza, y hallazgo
  sobre las limitaciones del modelo con fotos de estudio/banco de imágenes.
- [`docs/gitlab-ci-explicado.md`](docs/gitlab-ci-explicado.md) — el
  pipeline de CI/CD (`.gitlab-ci.yml`) explicado línea por línea, con los
  errores reales que se depuraron al armarlo.

## Licencia

Este proyecto se distribuye bajo la licencia [MIT](LICENSE).
