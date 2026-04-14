# Explicación: Casos de Uso del Sistema (Globales y Extendidos)

**Archivos:** `diagrama_casos_uso.puml` y `casos_uso_extendidos.puml`

## Descripción
Este diagrama mapea el valor aportado al usuario en funciones. Es lo primero que debe leer CUALQUIER desarrollador o Stakeholder para entender "**Qué hace la app**" con independencia técnica de lenguajes o tecnologías.

### Diagrama de Casos de Uso Global
*Muestra cada una de las cajitas organizadas por Actor:*
- **Administrador:** `Gestionar Usuarios`, `Crear Asignaciones`, `Ver Dashboard`. 
- **Doctor:** Cajas asociadas únicamente a pacientes (Historial de sus pacientes y Evaluaciones Pendientes). El doctor es un embudo de `Feedback`.
- **Paciente:** Las tareas principales de usar la aplicación que FonoApp ofrece `[Juegos Fonoaudiológicos (Escalable)]`.
  
**Punto Clave:** El diagrama agrupa las acciones de la App para el Paciente bajo `Ver Hub de Categorías` y `Acceder a Juegos / Jugar Actividad (Catálogo Dinámico)`, indicando que no está codeado de forma estricta (JuegoX). Si un nuevo juego existe en DB, entra aquí por derecho propio porque el Caso de uso abarca N catálogos.

---

### Casos de Uso Extendida (`<<include>>` y `<<extend>>`)
Cuando dibujamos el proceso interno de un **Juego**, hay flujos secundarios requeridos:

- **Incluidos OBLIGATORIOS:**
  - Jugar incluye -> Guardar el Resultado. Al finalizar el paciente, sin falta debe ocurrir o es fallo del sistema.
  - Jugar incluye -> Actualizar el Historial Global (si completó el reto).

- **Extendidos OPCIONALES (Condicionales):**
  - Permisos de Hardware: **SOLO** los ejercicios que usan Web Audio API (Micrófono para discriminar fonemas y volumen), levantan el `<<extend>>` de pedir permiso. Esta abstracción facilita depuraciones de hardware. 
  - Mostrar feedback de Victoria: Una visual de trofeo que ocurre solo si `completado=true`.