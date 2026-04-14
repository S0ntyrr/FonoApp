# Explicación: Secuencia y Colaboración

**Archivos:** `diagrama_colaboracion.puml` y `diagrama_secuencia.puml`

## Descripción
Estos diagramas (hermanos desde la perspectiva UML) se enfocan en procesos inter-servicios de FonoApp. Entienden qué hace cada capa del servidor y en qué momento o milisegundo transfiere su resultado.

### Diagrama de Secuencia (El flujo Administrativo-Médico)
El Caso de Asignación Automática:
- Muestra una línea de vida vertical de cada *router* de FastAPI y a MongoDB de fondo.
1. Admin da click. 
2. Router `POST` -> llama la capa de Lógica (`UsuariosRepo` y luego `AsignacionesRepo`).
3. El Repositorio extrae los perfiles médicos de Base de Datos.
4. Elige uno *Random* / Balanceado según la heurística y lo inserta en `Asignaciones`.
5. Se responde el ciclo completo devolviendo a la UI la confirmación.

Un cambio en el código no debe saltarse la Lógica o "Repositorios" para consultar la DB de frente, por ello, respeta la arquitectura en capas.

### Diagrama de Colaboración (El flujo del Paciente)
El Caso de Completar el Juego:
- Expresado libremente, los nodos no tienen tiempo vertical. FonoApp, el Web Client del niño y el Motor FastAPI envían mensajes del número **(1)** al **(8)**:
1. Ejecución del Web Audio JS/Micrófono.
2. Éxito de la lógica cliente JS.
3. Se invoca **`POST /juegos/resultado`**.
4. Pydantic procesa como Resultado_juegos.
5. El sistema paraleliza (o condiciona) y si se acreditó éxito, crea a la vez una fila en Estadísticas Globales (Historial).
6. FastAPI manda un HTTP 200 al Client.
7. Dispara la visualización de Victoria.

> Falla sin este flujo: Un juego en FonoApp que no guarde a BD, es inútil para la Terapia, porque carece de "Evidencia objetiva para el médico". Todo juego agregado en el panel Admin debe terminar cumpliendo este flujo de colaboración REST.