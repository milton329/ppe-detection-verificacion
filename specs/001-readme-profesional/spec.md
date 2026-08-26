# Spec: README profesional

## Objetivo

Convertir el `README.md` actual —funcional pero sin jerarquía visual, con
secciones desordenadas y contenido de bajo nivel (herramientas de IA)
compitiendo con lo esencial (cómo correr el proyecto)— en una portada
profesional del repositorio.

## Contexto / diagnóstico

- Buen contenido técnico, pero sin badges ni tabla de contenidos.
- La sección "Herramientas de desarrollo con IA" (Spec Kit + agent skills) es
  la más larga del documento y le resta protagonismo a lo esencial.
- Espacios en blanco huérfanos al final del archivo.
- Heading inconsistente: `##  Pruebas Unitarias` (doble espacio).
- Sin capturas de la interfaz web.
- Sin sección de deploy, pese a existir `Dockerfile` y `render.yaml`.
- Sin archivo `LICENSE` en el repo.

## Alcance

### Incluye
- Reescritura completa de `README.md` con la estructura definida abajo.
- Extracción de la sección de herramientas IA (Spec Kit / agent skills) a un
  archivo nuevo: `docs/desarrollo-ia.md`.
- Capturas reales de la interfaz web (`/app`), levantando la app localmente.
- Badges: Python 3.11+, FastAPI, licencia MIT (badge apuntando a `LICENSE`,
  sin crear el archivo).
- Sección "Deploy" nueva, documentando Docker + Render a partir de
  `Dockerfile` / `render.yaml` existentes.

### No incluye (fuera de alcance de este spec)
- Crear el archivo `LICENSE` — **a cargo de otro integrante del equipo**. El
  README solo referenciará "MIT" y enlazará a `LICENSE`, asumiendo que
  existirá.
- Cambios de código, tests o arquitectura del proyecto.
- CI/CD (no existe `.github/workflows/` hoy; no se agrega en este spec).

## Estructura final del README

1. Título + badges (Python 3.11+, FastAPI, MIT)
2. Descripción corta (1-2 líneas, existente)
3. Tabla de contenidos
4. Captura(s) reales de la interfaz web
5. Stack tecnológico (tabla o lista)
6. Arquitectura (contenido existente)
7. Instalación y ejecución rápida (contenido existente de uv/make)
8. Uso — endpoints REST + interfaz web (contenido existente)
9. Descarga del modelo (contenido existente)
10. Pruebas (contenido existente, heading corregido)
11. Deploy (Docker/Render) — nuevo
12. Herramientas de desarrollo con IA → link corto a `docs/desarrollo-ia.md`
13. Documentación adicional (contenido existente)
14. Licencia (mención MIT + link a `LICENSE`, sin crear el archivo)
15. Contribución (breve, opcional)

## Archivos afectados

| Archivo | Acción |
|---|---|
| `README.md` | Reescrito completo |
| `docs/desarrollo-ia.md` | Nuevo — contenido movido de la sección IA |
| `docs/img/` (o `docs/screenshots/`) | Nuevo — capturas reales de `/app` |
| `LICENSE` | **No se toca** (otro integrante) |

## Criterios de aceptación

- [ ] README reescrito sigue la estructura de 15 secciones definida arriba.
- [ ] Sección de IA/Spec Kit/skills ya no aparece completa en `README.md`,
      solo un link a `docs/desarrollo-ia.md`.
- [ ] `docs/desarrollo-ia.md` contiene el contenido íntegro que se movió.
- [ ] README incluye al menos una captura real de la interfaz web (no
      placeholder).
- [ ] Badges de Python, FastAPI y MIT visibles en la cabecera.
- [ ] Nueva sección "Deploy" documenta Docker y Render.
- [ ] No se crea ni modifica ningún archivo `LICENSE`.
- [ ] No quedan espacios en blanco huérfanos ni headings con espacios
      dobles.

## Pendientes / dependencias

- Confirmar con el integrante responsable cuándo estará listo `LICENSE` para
  que el link del README no quede roto.
