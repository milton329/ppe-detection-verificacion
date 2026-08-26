# Herramientas de desarrollo con IA (opcional)

El proyecto usa dos ayudas de desarrollo asistido con IA
([opencode](https://opencode.ai)): **Spec Kit** (workflow de especificación →
plan → tareas mediante los comandos `/speckit.*`) y **agent skills**
(instrucciones reutilizables en `.agents/skills/`). Ninguna es necesaria para
ejecutar la aplicación.

## Spec Kit (comandos `/speckit.*`)

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

## Skills del agente (`.agents/skills/`)

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
