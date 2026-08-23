# Quickstart — Validación de la feature 001-detect-no-bloqueante

Guía de validación end-to-end. Prerequisito: `uv sync` (instala también las
dev-dependencies nuevas) y, para la validación con modelo real,
`make download-model`.

## 1. Pruebas automatizadas (sin modelo ni red)

```bash
uv run pytest
```

Esperado: todas las pruebas en verde en segundos, sin descargar pesos.
Cubren: contrato de `POST /detect` con detector sustituto, paso del umbral
`confidence` y handler síncrono (fuera del hilo de eventos).

Complementos de calidad obligatorios:

```bash
make check    # ruff + mypy strict
```

## 2. Responsividad bajo carga real (manual)

```bash
make run
```

En dos terminales simultáneas:

- Terminal A — verificación lenta (imagen grande):
  ```bash
  curl -X POST "http://127.0.0.1:8000/detect?confidence=0.25" -F "file=@imagen_grande.jpg"
  ```
- Terminal B — inmediatamente después, repetir varias veces:
  ```bash
  curl -w "\n%{time_total}s\n" http://127.0.0.1:8000/health -o NUL
  ```

Esperado (SC-001): cada `/health` responde `200` en **< 1 s** mientras A sigue
procesando. Antes del cambio, B quedaba clavado hasta que A terminara.

## 3. Verificaciones concurrentes (manual, SC-002)

Repetir el comando de la terminal A en dos terminales a la vez: ambas deben
terminar con sus propias detecciones correctas y sin errores de servidor.

## 4. Regresión de resultado (manual, SC-003)

Comparar la respuesta de `POST /detect` para una misma imagen y umbral contra
la salida registrada en `docs/pruebas_inferencia_umbrales.md`: mismas clases,
confianzas y cajas.

## Referencias

- Contrato REST que no debe romperse: [contracts/api.md](contracts/api.md)
- Decisiones técnicas: [research.md](research.md)
