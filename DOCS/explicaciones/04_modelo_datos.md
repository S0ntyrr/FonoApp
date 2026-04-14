# Explicación: Modelo Relacional de Base de Datos y Script

**Archivos:** `modelo_relacional.puml` y `script_db.txt`

## Descripción: Entorno NoSQL (MongoDB)

Dado que FonoApp usa **MongoDB** document-based (NoSQL), estrictamente no hay "tablas y llaves foráneas puras", sino *Colecciones y Documentos*. Este diagrama asimila la filosofía relacional tradicional adaptándola a referencias lógicas.

### Colecciones Maestras vs Dinámicas

1. **`usuarios`**: Contiene la autenticación (*Collection Root*). Toda colección que dependa de una persona lo referencia a por medio del correo único o `ObjectId` en otros motores, aquí usamos el campo de correo para legibilidad humana rápida en queries.
2. **`perfiles_pacientes`**: Colección de *1:1* para separar información pesada PII de la cuenta de sesión por seguridad.
3. **`actividades`**: Almacena dinámicamente un objeto catálogo de Juegos. 
   - *Escalabilidad*: Al venir los juegos por este JSON estructurado, agregar el campo de un nuevo módulo o juego interactivo implica un insert() de Mongo, y el menú Frontend lo dibuja en cascada; ahorrando horas de desarrollo de vistas.
4. **`historial_actividades` y `resultados_juegos`**: Se insertan masivamente. Cuando un paciente finaliza la ejecución de Web Audio o arrastrar piezas, FonoApp arroja aquí datos brutos (pasos superados / puntos).

### Relaciones Mapeadas:
- Un **Usuario Médico** *crea o posee "n"* **Asignaciones**.
- Un **Usuario Paciente** *mantiene "n"* **Historiales** y **Resultados**.
- Una **Actividad (catálogo de juego)** puede ser ejecutada miles de veces (`resultados_juegos`).

En el `script_db.txt` hallamos los comandos de `mongosh` de iniciación rápida (`createIndex`) para garantizar la unicidad de las llaves como los emails y evitar cuellos de botella de búsqueda.