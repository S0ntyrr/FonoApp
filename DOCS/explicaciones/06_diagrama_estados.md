# Explicación: Diagramas de Estados FonoApp

**Archivos:** Carpeta `diagramas_estados/` (`01_usuario_medico.puml`, `02_paciente_asignacion.puml`, `03_resultados_historial.puml`, `04_sesion_bd.puml`)

## Descripción
Modelan el "ciclo de vida" o la máquina de estados temporal de los diferentes componentes y actores del sistema. Al dividirse por dominio, permiten analizar qué transiciones son válidas para cada recurso de FonoApp.

### 1. Estado de Usuarios y Médicos
- **Usuario General:** Nace `NoRegistrado`, fluye a `Registrado` y puede ser marcado como `Activo` o `Inactivo`.
- **Médico:** Tiene estados paralelos muy específicos; comienza `Activo` (Disponible), pero mediante su panel puede auto-marcarse `Ocupado` (no recibe nuevos pacientes) o `EnConsulta` (atendiendo en tiempo real). Esto influye directamente en las asignaciones del sistema.

### 2. Estado de Pacientes y Asignaciones
- **Paciente:** Nace `SinPerfil` tras su registro rápido en la pantalla de Auth. Cuando llena sus datos básicos (tutor, edad), queda con `PerfilCompleto`. Finalmente adopta el estado `ConActividades` una vez el terapeuta interviene.
- **Asignación (Tarea Terapéutica):** El núcleo que conecta al médico y paciente. Nace `Pendiente`. Si el médico no puede, pasa a `Cancelada`. Si asume el caso, llega a `Aceptada` y se da por finalizada una vez que es procesada.

### 3. Resultados e Historial
- **ResultadoJuego:** Cuando un niño entra a inflar un globo o atrapar letras, el juego está `EnProgreso`. Si abandona prematuramente reporta un estado `Parcial`. Si lo logra, alcanza la meta `Completado` y se congela en la base de datos.
- **HistorialActividad:** Fila maestra global. Entra en estado `Registrada` y permanece estancado a la espera del médico. Alcanza su paz final transitando a `Evaluada` (cuando el doctor redacta un texto de retrospectiva/feedback).

### 4. Sesión y Base de Datos
- **Sesión de App:** Rastrea el *screen time* terapéutico. `Iniciada` (login) -> `Activa` (sumando minutos_conectado) -> `Finalizada` (logout o cierre).
- **Conexión MongoDB:** El motor de vida de la aplicación. `Desconectada` -> `Conectando` (lifespan FastAPI) -> `Conectada` -> `Desconectando`. Si esto falla, el sistema entero entra en error.