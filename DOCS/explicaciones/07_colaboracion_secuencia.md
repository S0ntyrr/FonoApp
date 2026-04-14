# Explicación: Secuencia y Colaboración

**Archivos:** `diagrama_colaboracion.puml` y archivos en la carpeta `diagramas_secuencia/`

## Descripción
Estos diagramas (hermanos desde la perspectiva UML) se enfocan en los procesos e interacciones algorítmicas de FonoApp. Entienden qué hace cada capa del servidor (Frontend, Router o Base de datos) y en qué orden interactúan con el actor.

### Diagramas de Secuencia (El flujo vertical del tiempo)

La arquitectura define 4 procesos vitales desglosados en secuencias exactas:

1. **`01_asignacion.puml` (Asignación Automática):** 
   - El administrador oprime un botón, el sistema consulta a todos los médicos activos en MongoDB, aleatoriza/balancea una selección y asigna la terapia creando el documento respectivo, retornando luego la vista HTML con el resultado.
2. **`02_login_sistema.puml` (Login por Roles):**
   - Refleja el embudo inicial. El Usuario da email/contraseña. El Backend comprueba el HASH. Si es correcto, lee su variable `rol` y lo expulsa mediante una redirección HTTP 303 hacia una rama bloqueada (Panel admin, Panel de Doctor o Dashboard del Niño).
3. **`03_jugar_actividad.puml` (Jugar Actividad):**
   - El niño se enfrenta a un desafío interactivo. Si gana, el Frontend ejecuta un _POST_ Ajax hacia el Repositorio, guardando 2 cosas simultáneamente: un Resultado (técnico) y un Historial (para el médico), antes de mostrar finalmente el modal de Victoria.
4. **`04_evaluacion_medica.puml` (Dar Feedback Médico):**
   - El médico entra a la bandeja de pendientes, la Base de Datos le filtra únicamente resultados que carecen de feedback (`feedback: null`). El médico escribe, pulsa Enviar, y la DB hace un Update (PUT/PATCH conceptual) cerrando el ciclo clínico del niño.

### Diagrama de Colaboración (El flujo físico)
**Archivo:** `diagrama_colaboracion.puml` (El Caso de Completar el Juego)
- Expresado espacialmente libre, los nodos y actores se enumeran del **(1)** al **(8)** detallando el tránsito de variables cuando el niño interactúa usando el Micrófono (`Web Audio API`) y cómo ese mensaje rebota entre la API local y el Clúster de Mongo, logrando un código 200 OK de vuelta al navegador.

> Falla sin este flujo: Un juego en FonoApp que no guarde resultados en Database carece de "Evidencia objetiva para el médico". Todo juego implementado debe obedecer esta cadena Restful para certificarse en Producción.