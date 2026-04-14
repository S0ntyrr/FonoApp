# Explicación: Diagrama de Clases

**Archivo:** `diagrama_clases.puml`

## Descripción
Este diagrama detalla qué clases u objetos estáticos y modelos Pydantic usa FonoApp dentro del entorno de FastAPI (Backend). Es ideal para desarrolladores backend porque mapea en software los conceptos del mundo real.

### Principales Componentes

#### 1. Mapeo a Base de Datos (Modelos Pydantic)
- `UsuarioBase`, `UsuarioCreate`, `UsuarioPublico`: Representan la tabla maestra de seguridad (login/registro) para la herencia DRY.
- `PerfilPaciente`: Expande la información base de la cuenta para mostrar características pediátricas (tutor, escolaridad).
- `SesionApp`, `HistorialActividad`, `ResultadoJuego`: Colecciones estadísticas. **Aquí es vital la escalabilidad**, dado que está estructurado para registrar cualquier juego de cualquier categoría basándose en la `ActividadCategoria` y no en tablas de base de datos individuales por juego. 

#### 2. Motores/Routers FastAPI
- Al lado del modelo de datos tenemos los **Routers** (e.g., `RoutesAdmin`, `RoutesDoctor`, `RoutesJuegos`).
- **Sistema de Juegos Escalable (Novedad):** Observamos que `RoutesJuegos` maneja `load_dynamic_game()` y no rutas atadas explícitamente a 23 juegos estáticos (antes había un endpoint *hardcodeado* por juego, lo hicimos general y parametrizado para cualquier cantidad N). De esta manera el Backend no necesita redespliegues enormes si un Terapeuta sugiere integrar 5 pasatiempos multimedia más.

### Interacción
El Backend inyecta al Frontend solo la información permitida por perfil. Al crearse una *Asignación*, el modelo `Asignacion` unifica el cruce de datos `EmailStr` (médicos <-> paciente), permitiendo saber de inmediato de quién es un Resultado y quién debe darle Feedback en el Historial a través de sus IDs relacionales.