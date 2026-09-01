# `.gitlab-ci.yml` explicado línea por línea

Este documento explica en detalle el pipeline de CI/CD del proyecto, para
poder sustentarlo en la presentación. Cubre: qué hace cada línea, por qué
existe, y los problemas reales que tuvimos que resolver para dejarlo
funcionando (útil para responder preguntas del profe sobre el proceso, no
solo sobre el resultado final).

## 1. Panorama general: por qué GitLab y no solo GitHub

El código fuente vive en **GitHub** (`github.com/milton329/ppe-detection-verificacion`),
que sigue siendo la única fuente de verdad. GitLab.com solo ejecuta el
pipeline de CI/CD. La conexión entre ambos es así:

```
GitHub (main) --push mirror (GitHub Action)--> GitLab (main) --dispara--> pipeline .gitlab-ci.yml
```

**¿Por qué no usar el mirror nativo de GitLab (que él jale los cambios)?**
Porque GitLab.com movió el *pull mirroring* a planes de pago (Premium). La
alternativa gratuita fue invertir la dirección: un GitHub Action
(`.github/workflows/mirror-gitlab.yml`) hace `git push --force` hacia GitLab
en cada push a `main`, usando un *Project Access Token* de GitLab
(scope `write_repository`) guardado como secret de GitHub. El resultado es
el mismo (GitLab siempre tiene el `main` actualizado), sin pagar nada.

El pipeline en sí tiene 3 **stages** (etapas), que corren en orden y en
secuencia — si una falla, las siguientes no se ejecutan:

```yaml
stages:
  - test
  - build
  - deploy
```

- **test**: corre en cada push, a cualquier rama. Es la validación de calidad.
- **build**: solo en `main`. Empaqueta la app en una imagen Docker.
- **deploy**: solo en `main`. Pone esa imagen a correr en el servidor real.

## 2. Variables globales

```yaml
variables:
  IMAGE_SHA: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
  IMAGE_LATEST: $CI_REGISTRY_IMAGE:latest
  CONTAINER_NAME: ppe-detection
```

Estas variables están disponibles en los 3 jobs. `$CI_REGISTRY_IMAGE` y
`$CI_COMMIT_SHORT_SHA` son variables **predefinidas por GitLab** (no las
configuramos nosotros, existen automáticamente en todo pipeline):

| Variable | Qué contiene | Ejemplo |
|---|---|---|
| `$CI_REGISTRY_IMAGE` | Ruta de la imagen en el Container Registry de este proyecto | `registry.gitlab.com/milton329/ppe-detection-verificacion` |
| `$CI_COMMIT_SHORT_SHA` | Los primeros 8 caracteres del commit que disparó el pipeline | `5708b87` |
| `$CI_COMMIT_BRANCH` | Nombre de la rama del commit | `main` |
| `$CI_REGISTRY` / `$CI_REGISTRY_USER` / `$CI_REGISTRY_PASSWORD` | Credenciales automáticas para el Container Registry de **este** proyecto (un token temporal, válido solo mientras corre el job) | — |

Con esto armamos dos etiquetas (tags) para la misma imagen Docker:

- **`IMAGE_SHA`** (ej. `...:5708b87`): una etiqueta única e inmutable por
  commit. Sirve para trazabilidad — siempre se puede saber exactamente qué
  código generó una imagen específica, y hacer rollback a una versión
  anterior si hace falta.
- **`IMAGE_LATEST`** (`...:latest`): la etiqueta "móvil" que siempre apunta
  a la última build exitosa. Es la que usa el job de `deploy` para saber
  cuál imagen bajar al servidor.

`CONTAINER_NAME` es simplemente el nombre que le damos al contenedor en el
servidor, para poder referenciarlo al detenerlo/reiniciarlo.

## 3. Job `test`

```yaml
test:
  stage: test
  image: python:3.11-slim
  before_script:
    - apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 libxcb1 libxext6 libsm6 libxrender1
    - pip install uv
  script:
    - uv sync
    - uv run pytest tests/unit --cov=src/ppe_detection
    - uv run ruff check .
    - uv run mypy src
```

- `stage: test` — asocia este job con la etapa `test` definida arriba.
- `image: python:3.11-slim` — GitLab levanta un contenedor Docker limpio
  con esta imagen para correr el job. Es una imagen oficial de Python,
  liviana ("slim" = sin herramientas de compilación innecesarias).
- **`before_script`** — comandos de preparación, antes del trabajo real:
  - `apt-get install ... libgl1 libglib2.0-0 libxcb1 ...` — **esta línea
    existe por un error real que tuvimos**: `python:3.11-slim` no trae
    varias librerías gráficas del sistema operativo (no de Python) que
    necesita `opencv-python` (una dependencia de `ultralytics`, la
    librería del modelo YOLO). Sin ellas, el simple `import cv2` fallaba
    con `ImportError: libxcb.so.1: cannot open shared object file`. Es el
    mismo motivo por el que el `Dockerfile` instala `libgl1`/`libglib2.0-0`.
  - `pip install uv` — instala `uv`, el gestor de dependencias/entornos
    que usa el proyecto (más rápido que `pip` puro, y respeta el
    `uv.lock` para instalar exactamente las mismas versiones que en local).
- **`script`** — el trabajo real del job (si cualquiera de estos comandos
  falla, el job falla y el pipeline se detiene ahí):
  - `uv sync` — crea el entorno virtual e instala todas las dependencias
    exactas de `pyproject.toml`/`uv.lock`.
  - `uv run pytest tests/unit --cov=src/ppe_detection` — corre la suite de
    pruebas unitarias con reporte de cobertura de código.
  - `uv run ruff check .` — linter: revisa estilo y errores comunes
    (imports sin usar, líneas muy largas, etc.) en todo el repo.
  - `uv run mypy src` — verifica tipado estático en el código fuente.

Este job no tiene `rules`, así que corre siempre, en cualquier rama —
es la validación mínima que debe pasar cualquier cambio.

## 4. Job `build`

```yaml
build:
  stage: build
  image: docker:27
  services:
    - docker:27-dind
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
  script:
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
    - docker build -t "$IMAGE_SHA" -t "$IMAGE_LATEST" .
    - docker push "$IMAGE_SHA"
    - docker push "$IMAGE_LATEST"
```

- `image: docker:27` — la imagen del job trae el **cliente** de Docker
  (el comando `docker`), pero no un daemon de Docker corriendo dentro
  (no se puede meter Docker dentro de Docker así de simple).
- `services: [docker:27-dind]` — **dind = Docker-in-Docker**. Levanta un
  segundo contenedor, en paralelo, que sí corre el *daemon* de Docker
  real. El cliente del contenedor principal se conecta a ese daemon para
  poder construir y correr imágenes. Es el patrón estándar de GitLab CI
  para cualquier job que necesite ejecutar `docker build`.
- `rules: if $CI_COMMIT_BRANCH == "main"` — este job **no corre** en
  otras ramas. No tiene sentido construir y publicar una imagen de
  código que todavía no llegó a `main`.
- `docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"`
  — autentica contra el **GitLab Container Registry** (el registro de
  imágenes Docker integrado gratis en cada proyecto de GitLab). Las tres
  variables son automáticas, no las configuramos nosotros — es una de
  las ventajas de usar el registry propio de GitLab en vez de uno externo.
- `docker build -t "$IMAGE_SHA" -t "$IMAGE_LATEST" .` — construye la
  imagen a partir del `Dockerfile` en la raíz del repo (el `.` final),
  aplicándole **las dos etiquetas** de una sola vez (no se reconstruye
  dos veces, solo se le ponen dos nombres a la misma imagen).
- `docker push` (x2) — sube ambas etiquetas al registry. Sin este paso,
  la imagen solo existiría dentro del runner temporal de GitLab (que se
  destruye al terminar el job) y el droplet no podría descargarla.

## 5. Job `deploy`

```yaml
deploy:
  stage: deploy
  image: alpine:3.20
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
  before_script:
    - apk add --no-cache openssh-client
    - sed -i 's/\r$//' "$DO_SSH_KEY"
    - printf '\n' >> "$DO_SSH_KEY"
    - chmod 600 "$DO_SSH_KEY"
    - mkdir -p ~/.ssh
    - ssh-keyscan -H "$DO_HOST" >> ~/.ssh/known_hosts
  script:
    - >
      ssh -i "$DO_SSH_KEY" "$DO_USER@$DO_HOST"
      "docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY &&
      docker pull $IMAGE_LATEST &&
      docker stop $CONTAINER_NAME || true &&
      docker rm $CONTAINER_NAME || true &&
      docker run -d --name $CONTAINER_NAME -p 8000:8000 --restart unless-stopped $IMAGE_LATEST"
```

- `image: alpine:3.20` — una distribución de Linux mínima (unos pocos MB),
  suficiente porque este job solo necesita un cliente SSH, no Docker.
- `rules` — igual que `build`, solo corre en `main`.
- **`before_script`** — preparar la conexión SSH:
  - `apk add --no-cache openssh-client` — Alpine no trae `ssh` instalado
    por defecto; hay que agregarlo.
  - `sed -i 's/\r$//' "$DO_SSH_KEY"` y `printf '\n' >> "$DO_SSH_KEY"` —
    **estas dos líneas existen por un incidente real que tuvimos**: la
    llave privada SSH se guarda en GitLab como una *CI/CD Variable* de
    tipo `File` (GitLab la escribe a un archivo temporal y `$DO_SSH_KEY`
    apunta a esa ruta). Al pegarla desde el navegador, (1) puede quedar
    con saltos de línea estilo Windows (`\r\n` en vez de `\n`), y (2)
    puede perder el salto de línea final después de
    `-----END OPENSSH PRIVATE KEY-----`. Ambos problemas rompen el
    formato PEM y OpenSSH la rechaza con `error in libcrypto` /
    `Permission denied (publickey)`, aunque la llave en sí sea válida.
    Estas dos líneas normalizan el archivo antes de usarlo, sin tener
    que volver a pegar el secret cada vez.
  - `chmod 600 "$DO_SSH_KEY"` — SSH exige que el archivo de la llave
    privada no sea legible por "otros" usuarios (permisos estrictos);
    si no, se niega a usarla.
  - `mkdir -p ~/.ssh` — crea la carpeta donde SSH espera su configuración.
  - `ssh-keyscan -H "$DO_HOST" >> ~/.ssh/known_hosts` — descarga la
    huella pública del servidor y la guarda como "conocida", para que el
    siguiente comando `ssh` no se quede esperando una confirmación
    interactiva (`Are you sure you want to continue connecting?`), que
    en un pipeline automático nadie puede responder.
- **`script`** — un único comando `ssh` que ejecuta una cadena de
  comandos **remotos**, dentro del droplet, encadenados con `&&`:
  1. `docker login ...` — el droplet también necesita autenticarse
     contra el GitLab Container Registry para poder descargar la imagen
     (es privada por defecto).
  2. `docker pull $IMAGE_LATEST` — descarga la imagen recién publicada.
  3. `docker stop $CONTAINER_NAME || true` — detiene el contenedor
     anterior si existe. El `|| true` evita que el pipeline falle si
     **no** existe todavía (por ejemplo, en el primer deploy de la
     historia) — sin eso, `docker stop` de un contenedor inexistente
     devuelve error y cortaría la cadena de `&&`.
  4. `docker rm $CONTAINER_NAME || true` — elimina el contenedor viejo
     (ya detenido) para poder reusar el mismo nombre. Mismo motivo para
     el `|| true`.
  5. `docker run -d --name $CONTAINER_NAME -p 8000:8000 --restart unless-stopped $IMAGE_LATEST`
     — levanta el contenedor nuevo: `-d` (en segundo plano),
     `-p 8000:8000` (expone el puerto de la app), `--restart
     unless-stopped` (si el droplet se reinicia, Docker levanta el
     contenedor solo, salvo que alguien lo haya detenido a propósito).

  Todo esto viaja como **un solo string** entre comillas dobles porque
  se ejecuta remotamente vía SSH — no son 5 pasos del pipeline, es un
  solo paso que le manda 5 comandos encadenados a la terminal del droplet.

## 6. Variables/secrets configurados en GitLab

En `Settings → CI/CD → Variables` del proyecto, con **Protect variable**
activado (solo se exponen en pipelines de ramas protegidas, y `main` lo
está):

| Variable | Tipo | Visibilidad | Valor |
|---|---|---|---|
| `DO_HOST` | Variable | Masked | IP pública del droplet de DigitalOcean |
| `DO_USER` | Variable | Visible* | `root` |
| `DO_SSH_KEY` | **File** | Visible | Llave privada SSH completa (formato PEM) |

\* `DO_USER` no se pudo enmascarar porque GitLab exige mínimo 8
caracteres para el *masking*, y `root` tiene 4 — no es información
sensible de todas formas.

El tipo **File** es importante: en vez de exponer el valor como texto
plano en una variable de entorno normal, GitLab escribe el contenido a un
archivo temporal en el runner, y la variable (`$DO_SSH_KEY`) contiene la
**ruta** a ese archivo, no la llave en sí. Así es como espera trabajar un
comando `ssh -i` (necesita la ruta a un archivo, no el contenido inline).

## 7. Errores reales que debuggeamos (útil para preguntas del profe)

1. **`ImportError: libxcb.so.1`** en el job `test` → faltaban librerías
   de sistema para OpenCV en la imagen `python:3.11-slim`.
2. **Errores de `ruff` (líneas > 100 caracteres)** en tests preexistentes
   → nunca habían bloqueado nada porque no existía CI corriendo lint.
3. **`Connection refused` en el puerto 22** → el firewall (UFW) del
   droplet solo permitía 22, 2375 y 2376 por defecto; había que abrir
   también el 8000 para la app, y además el runner de GitLab disparó el
   límite de tasa (`LIMIT`) que UFW aplica por defecto al puerto 22.
4. **`error in libcrypto` / `Permission denied (publickey)`** → la llave
   privada guardada como secret en GitLab tenía saltos de línea `\r\n` y
   le faltaba el salto de línea final tras `-----END...-----`. Se
   diagnosticó con `wc -l` (contó 6 líneas en vez de 7) y `ssh-keygen -y`
   (falla igual que `ssh`, pero sin necesidad de conectarse a ningún
   servidor ni exponer la llave en el log).

Estos cuatro problemas son buen material para explicar en la
presentación: muestran troubleshooting real de un pipeline de CI/CD, no
solo un archivo YAML que "funcionó a la primera".
