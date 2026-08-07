# ppe-detection-verificacion

Sistema de verificación automática de EPP (casco y chaleco) en entornos industriales mediante visión por computador, usando el modelo preentrenado YOLOv11 `melihuzunoglu/ppe-detection`.

## Arquitectura

Arquitectura hexagonal (puertos y adaptadores):

- `domain/` — entidades y reglas de negocio (sin dependencias externas).
- `application/` — casos de uso y puertos (`inbound`/`outbound`).
- `infrastructure/` — adaptadores concretos: API (FastAPI), modelo (YOLO), almacenamiento.

## Cómo levantar el proyecto

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e .
uvicorn ppe_detection.main:app --reload --app-dir src
```

Luego abre http://127.0.0.1:8000 (hola mundo) y http://127.0.0.1:8000/health.

Documentación interactiva: http://127.0.0.1:8000/docs
