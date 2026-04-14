# Explicación: Diagrama de Estados FonoApp

**Archivo:** `diagrama_estados.puml`

## Descripción
Modela el "ciclo de vida" temporal de los dos recursos más importantes de la plataforma una vez en acción.

### 1. Estado del Médico (Actor Terapeuta)
Este diagrama explica cómo se ve el status social/disponibilidad del Doctor que atiende:
- **Offline / Inactivo**.
- Pasa a `Disponible` (En su panel).
- Cambia a `Ocupado` o `En Consulta` virtual, impactando al panel de Administración, notificando indirectamente a la base si sus tareas varían o rechaza la asignación de pacientes.

### 2. Estado de una Asignación (Tarea de Terapia)
El *Core* terapéutico de FonoApp, las tareas que el doctor asigna a un niño:
- Nace como **`Pendiente`** tras asignarse manual o automáticamente.
- Puede quedar **`Cancelada`** si el médico o sistema la rechaza.
- Eventualmente transita a **`Aceptada / En Progreso`** cuando el médico acepta la tutela.
- Queda **`Completada`** cuando todas las submétricas del juego evaluaron positivo en completitud.
- Finaliza su vida cuando adopta el estado de **`Evaluada`**: Cuando el médico leyó el récord y dejó un _Feedback_ de evolución terapéutica, validando el esfuerzo.