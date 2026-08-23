# Feature Specification: Verificación de EPP sin bloqueo del servicio

**Feature Branch**: `001-detect-no-bloqueante`

**Created**: 2026-08-23

**Status**: Draft

**Input**: User description: "El endpoint de detección ejecuta el procesamiento
de la imagen de forma sincrónica dentro del hilo principal de atención de
eventos del servidor, congelando todo el servicio (healthcheck, interfaz web,
otras detecciones) mientras procesa una imagen. Como operador, quiero que el
servicio siga respondiendo otras peticiones mientras infiere. Criterio: el
manejo de la petición no debe ejecutar trabajo pesado en el hilo de eventos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Servicio responsivo durante una verificación (Priority: P1)

Un operador industrial envía una imagen para verificar el uso de EPP. Mientras
el sistema procesa esa imagen, otro operador (o un monitor automático) consulta
el estado de salud del servicio o navega la interfaz web, y recibe respuesta
inmediata en lugar de quedarse esperando a que termine la verificación en
curso.

**Why this priority**: es el defecto central que motiva la feature; sin esto,
una sola verificación lenta deja todo el servicio inaccesible, lo que es
inaceptable en un entorno industrial donde el healthcheck alimenta decisiones
de operación.

**Independent Test**: con el servicio levantado, se envía una imagen para
verificación y, sin esperar su respuesta, se consulta el estado de salud; la
consulta debe responder de inmediato aunque la verificación siga en curso.

**Acceptance Scenarios**:

1. **Given** el servicio en funcionamiento, **When** se envía una imagen para
   verificar EPP, **Then** otras peticiones (estado de salud, interfaz web u
   otra verificación) reciben respuesta mientras la primera sigue procesando.
2. **Given** una verificación en curso, **When** se consulta el estado de
   salud del servicio, **Then** la respuesta llega en menos de 1 segundo.
3. **Given** dos verificaciones enviadas casi al mismo tiempo, **When**
   ambas terminan, **Then** ninguna alteró el resultado de la otra y ambas
   devuelven sus propias detecciones.

---

### User Story 2 - Verificación automatizada sin modelo real (Priority: P2)

Una persona desarrolladora clona el proyecto y quiere confirmar que el servicio
mantiene la responsividad descrita, pero no tiene los pesos del modelo ni
conexión a red. Ejecuta la suite de verificación automatizada del proyecto y
obtiene evidencia del comportamiento usando sustitutos del detector, sin
descargar nada.

**Why this priority**: garantiza que la corrección queda protegida contra
regresiones y habilita la infraestructura de pruebas que la constitución exige;
no es el valor de usuario directo (por eso P2), pero es condición para aceptar
el cambio.

**Independent Test**: desde un clon fresco y sin red, se ejecuta el comando de
pruebas del proyecto; todas pasan y cubren el contrato del endpoint de
verificación y la no-bloqueosidad del manejo de peticiones.

**Acceptance Scenarios**:

1. **Given** un entorno de desarrollo sin pesos del modelo ni acceso a red,
   **When** se ejecuta la suite de verificación automatizada, **Then** todas
   las pruebas pasan.
2. **Given** la suite de verificación en ejecución, **When** revisa el
   endpoint de verificación, **Then** valida que responde con el contrato
   actual (clases, confianza, cajas) usando un detector sustituto.

### Edge Cases

- ¿Qué pasa si llegan varias imágenes simultáneas? Deben procesarse sin
  bloquearse entre sí ni degradar la respuesta del resto del servicio.
- ¿Qué pasa cuando la primera petición tras arrancar incluye además la
  descarga inicial de los pesos? El resto del servicio debe seguir disponible
  durante esa espera prolongada.
- ¿Qué pasa si la imagen es inválida o está vacía? El comportamiento actual no
  cambia en esta feature (mejora futura separada).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El servicio DEBE seguir aceptando y respondiendo peticiones de
  cualquier funcionalidad mientras hay una verificación de EPP en curso.
- **FR-002**: El manejo de una petición de verificación NO DEBE ejecutar el
  procesamiento pesado de la imagen en el hilo principal de atención de
  eventos del servidor.
- **FR-003**: La respuesta del endpoint de verificación DEBE mantener su
  contrato actual: mismas clases detectadas, confianzas, cajas delimitadoras y
  umbral configurable.
- **FR-004**: El proyecto DEBE incluir pruebas automatizadas que verifiquen
  FR-001 a FR-003 sin requerir conexión a red ni descarga del modelo real.
- **FR-005**: Las pruebas DEBEN ejecutarse con un único comando estándar del
  proyecto y quedar integradas al flujo de calidad existente.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Durante una verificación en curso, las consultas al estado de
  salud del servicio responden en menos de 1 segundo.
- **SC-002**: Dos o más verificaciones simultáneas progresan y terminan sin
  bloquearse entre sí.
- **SC-003**: Para una misma imagen y umbral, el resultado de la verificación
  es idéntico al obtenido antes del cambio.
- **SC-004**: Una persona colaboradora ejecuta la suite de verificación en
  menos de 1 minuto desde un clon fresco, sin descargar el modelo.

## Assumptions

- El contrato público del endpoint de verificación no cambia (ni rutas ni
  formato de respuesta).
- La carga esperada es baja/moderada (pocas verificaciones concurrentes); una
  cola distribuida o workers adicionales están fuera de alcance.
- La validación de imágenes inválidas/corruptas se mantiene como hoy (mejora
  futura separada).
- Dependencia: el flujo de calidad existente (`make check`) debe seguir en
  verde conforme a la constitución v1.0.0.
