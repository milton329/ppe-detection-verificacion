### 📝 Convención del título del PR
Usa un [prefijo convencional](https://www.conventionalcommits.org/) para clasificar el tipo de trabajo:

| Prefijo | Cuándo usarlo | Ejemplo |
|---------|---------------|---------|
| `feat:` | Nueva funcionalidad | `feat: agrega endpoint de verificación` |
| `fix:` | Corrección de errores | `fix: corrige umbral de confianza por defecto` |
| `refactor:` | Cambio de estructura sin alterar comportamiento | `refactor: separa el servicio de cumplimiento en domain` |
| `test:` | Agregar o corregir pruebas | `test: agrega pruebas del servicio de cumplimiento` |
| `chore:` | Mantenimiento (docs, dependencias, configuración) | `chore: agrega workflow de CI` |

### 📝 Tipo de PR
- [ ] **Código del proyecto** 🏭 — Requiere aprobación de al menos 1 compañero y (si aplica) que pase el CI con el umbral de cobertura acordado.
- [ ] **Exploración / Docs** 🔍 — Notebooks, documentación, ajustes de configuración, README, etc. También requiere revisión de un compañero.

---

### 📚 Descripción
<!---
Describe qué logra este PR. Llena todas las secciones que apliquen — ayuda a quien revise
y a quien retome este código más adelante a entender el cambio sin tener que adivinar.
-->

**Rama origen → destino:** <!-- ej: feature/verificacion-epp → develop -->

**Resuelve / relacionado con:** <!-- Link al Issue de GitHub si existe, o descripción corta del problema -->

**Documentación relacionada (opcional):** <!-- Link a README, diagrama, etc. actualizado por este cambio -->

#### Problema
<!-- ¿Qué estaba mal o qué faltaba? Sé específico: traceback, requerimiento no cumplido, deuda técnica, etc. -->

#### Solución
<!-- ¿Qué hiciste para resolverlo? Lista los cambios clave. -->
-
-

#### Otros cambios / varios
<!---
Idealmente no debería haber nada aquí, pero si tocaste algo fuera del alcance
principal del PR, anótalo para que el revisor no se sorprenda.
-->

#### A quién/qué afecta
<!-- Menciona con @ a compañeros cuyo trabajo (otra rama feature, un módulo compartido) se ve afectado por este cambio -->

#### ¿Cómo se probó?
<!-- Cómo verificaste que funciona. Adjunta capturas de la interfaz, output de pytest, etc. -->
- [ ] Pruebas unitarias (pytest) añadidas/actualizadas
- [ ] Probado manualmente ejecutando la app
- [ ] No se probó (explica por qué)

---

### ✅ Checklist antes de pedir revisión
- [ ] El código corre sin errores
- [ ] No dejé prints/debug de más
- [ ] Las pruebas unitarias pasan localmente (`pytest`)
- [ ] Actualicé el README si aplica
- [ ] Le pedí revisión a al menos 1 compañero

---

### 🚀 Build & Post-merge
> Estos pasos aplican sobre todo a PRs de **Código del proyecto**; para **Exploración/Docs** puedes marcarlos como N/A.

#### 📦 Checklist antes de mergear
- [ ] El CI (GitHub Actions) pasó: tests + cobertura mínima acordada por el equipo
- [ ] La imagen de Docker sigue construyendo correctamente (`docker build .`)
- [ ] Confirmé que la rama destino es la correcta (`feature/* → develop`, y solo `develop → main` para entregas)

#### 🧹 Pendientes / Follow-ups
<!-- Lo que queda por hacer después de este PR, para no perderlo de vista -->
- [ ]
