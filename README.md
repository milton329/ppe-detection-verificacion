# ppe-detection-verificacion

Sistema de verificación automática de EPP (casco y chaleco) en entornos industriales mediante visión por computador, usando el modelo preentrenado YOLOv11 `melihuzunoglu/ppe-detection`.

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

### Endpoints REST

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

## Herramientas de desarrollo con IA (opcional)

El proyecto usa dos ayudas de desarrollo asistido con IA
([opencode](https://opencode.ai)): **Spec Kit** (workflow de especificación →
plan → tareas mediante los comandos `/speckit.*`) y **agent skills**
(instrucciones reutilizables en `.agents/skills/`). Ninguna es necesaria para
ejecutar la aplicación.

### Spec Kit (comandos `/speckit.*`)

Los comandos `speckit.*` de opencode (`.opencode/commands/`) sí están
versionados, pero sus scripts y plantillas viven en `.specify/`, carpeta que se
excluye del repositorio porque contiene estado local de cada checkout. Al
clonar, hay que regenerarla con el CLI `specify` (requiere `uv`, que ya usa el
proyecto):

```bash
uvx --from git+https://github.com/github/spec-kit.git specify init --here --integration opencode --script ps
```

- `--integration opencode` — genera/actualiza los comandos para opencode.
- `--script ps` — scripts en PowerShell (Windows).
- Si el directorio no está vacío, el comando pide confirmación antes de
  mezclar archivos.
- Para fijar la versión usada en este proyecto, ancla el tag:
  `git+https://github.com/github/spec-kit.git@v0.16.5`.

### Skills del agente (`.agents/skills/`)

A diferencia de `.specify/`, los skills **viajan con el repo** junto con su
lock (`skills-lock.json`): al clonar ya están disponibles en opencode, sin
instalar nada.

Para reconstruirlos manualmente o agregar más (requiere Node.js; CLI
[npx skills](https://skills.sh)):

```bash
npx skills add mindrally/skills --skill deep-learning-pytorch
npx skills add mindrally/skills --skill fastapi-python
npx skills add mattpocock/skills --skill improve-codebase-architecture
npx skills add google-gemini/gemini-cli --skill pr-creator
npx skills add github/awesome-copilot --skill readme-blueprint-generator
npx skills add obra/superpowers --skill test-driven-development
npx skills add anthropics/skills --skill webapp-testing
```

Para actualizarlos a su última versión:

```bash
npx skills update
```

##  Pruebas Unitarias

El proyecto cuenta con 50 pruebas unitarias, con 100% de cobertura de línea
sobre `src/ppe_detection`.

### Cómo ejecutarlas

```bash
uv sync
uv run pytest tests/unit -v
```

Con reporte de cobertura:
```bash
uv run pytest tests/unit --cov=src/ppe_detection --cov-report=term-missing
```

### Qué se prueba

| Módulo | Descripción |
|---|---|
| `domain/entities/compliance.py` | Estados `COMPLIANT`, `NON_COMPLIANT` y `NO_PERSONS`, además de las propiedades de las entidades de cumplimiento |
| `domain/services/compliance_service.py` | Regla de negocio: cruce de personas con casco/chaleco, incluyendo casos de una y de varias personas en la misma imagen con estados mixtos |
| `application/use_cases/detect_ppe.py` | Caso de uso `DetectPPEUseCase`: detección y evaluación de cumplimiento, aislado de HTTP y del modelo real |
| `application/use_cases/detection_result.py` | Resultado de aplicación que agrupa las detecciones y el reporte de cumplimiento |
| `infrastructure/adapters/outbound/model/yolo_detector.py` | Adaptador YOLO: mapeo de resultados del modelo a entidades `Detection`, carga perezosa del modelo (una sola vez), umbral de confianza |
| `infrastructure/adapters/outbound/model/huggingface_model_provider.py` | Descarga de pesos desde Hugging Face Hub (mockeada, sin red real) |
| `infrastructure/config/dependencies.py` | Composition root: verifica el wiring correcto de adaptadores y el cacheo como singleton |
| `infrastructure/adapters/inbound/api/routers/detection_router.py` | Endpoint `POST /detect`: detecciones, cumplimiento, contrato de respuesta, umbral de confianza y ejecución no bloqueante |
| `infrastructure/adapters/inbound/api/routers/health_router.py` | Endpoint `GET /health` |
| `infrastructure/adapters/inbound/web/web_router.py` | Rutas de la interfaz web (`/`, `/app`, `/help`): redirecciones y respuestas HTML |
| `infrastructure/adapters/inbound/api/schemas/detection_schema.py` | Schemas Pydantic para detecciones, personas evaluadas y resumen de cumplimiento |

### Enfoque

Las pruebas unitarias de infraestructura (YOLO, Hugging Face y endpoints) usan
`unittest.mock` para aislar por completo el modelo real y la red — ninguna
prueba unitaria descarga pesos ni ejecuta inferencia real. Las pruebas de
integración del modelo real se ejecutan por separado y requieren los pesos y
la red.





## Documentación adicional

- [`docs/pruebas_inferencia_umbrales.md`](docs/pruebas_inferencia_umbrales.md) —
  pruebas iniciales de inferencia, ajuste de umbral de confianza, y hallazgo
  sobre las limitaciones del modelo con fotos de estudio/banco de imágenes.
