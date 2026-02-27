# FonoApp – Backend (FastAPI + MongoDB Atlas)

Aplicación web/móvil para apoyo en fonoaudiología con:

- **Panel Admin (web)**: gestión de pacientes, médicos, actividades, asignaciones, historial, resultados de juegos y contenido del sistema.
- **Panel Doctor (web)**: revisión de pacientes, asignaciones, historial, resultados de juegos y evaluaciones pendientes.
- **App Paciente (web/móvil)**: registro/login, perfil del paciente, calendario de uso y acceso a juegos fonoaudiológicos.
- **Juegos Fonoaudiológicos**: respiración, fonación, resonancia, articulación y practica conmigo.
- **App Emisor (móvil / webview)**: pantalla básica de inicio (lista para extender).

---

## Tecnologías

- **Backend**: Python 3.11+ + FastAPI
- **Base de datos**: MongoDB Atlas (cluster remoto)
- **Driver**: Motor (async, sobre PyMongo)
- **Templates**: Jinja2
- **Estilos**: CSS simple (fondo blanco, botones y títulos rojos)

---

## Estructura de carpetas

```text
FonoApp/
├─ app/
│  ├─ main.py              # Punto de entrada FastAPI (incluye ruta raíz /)
│  ├─ config.py            # Configuración (MongoDB URI, nombre BD, .env)
│  ├─ database.py          # Conexión a MongoDB (Motor async)
│  ├─ models.py            # Modelos Pydantic (usuarios, actividades, etc.)
│  ├─ routers/             # Rutas tipo API / vistas app
│  │  ├─ auth.py           # Login y registro (/auth/*)
│  │  ├─ emisor.py         # Home emisor (/emisor/*)
│  │  └─ paciente.py       # Perfil y calendario del paciente (/paciente/*)
│  ├─ web/                 # Rutas web (HTML) para admin/doctor/juegos
│  │  ├─ routes_admin.py   # Panel admin (/admin/*)
│  │  ├─ routes_doctor.py  # Panel doctor (/doctor/*)
│  │  └─ routes_juegos.py  # Juegos fonoaudiológicos (/juegos/*)
│  ├─ templates/           # Vistas HTML (Jinja2)
│  │  ├─ base.html
│  │  ├─ auth/             # login / registro
│  │  ├─ admin/            # dashboard, pacientes, médicos, actividades, etc.
│  │  ├─ doctor/           # home, pacientes, actividades, resultados, etc.
│  │  ├─ paciente/         # perfil + calendario
│  │  ├─ emisor/           # home emisor
│  │  └─ juegos/           # hub + categorías (respiracion, fonacion, etc.)
│  └─ static/
│     ├─ css/estilos.css   # paleta rojo/blanco y layout móvil
│     ├─ img/              # imágenes estáticas
│     └─ js/               # scripts del cliente
├─ DOCS/                   # Diagramas PlantUML
│  ├─ actores_roles.puml
│  ├─ diagrama_casos_uso.puml
│  ├─ diagrama_clases.puml
│  └─ diagrama_estados.puml
├─ requirements.txt
├─ .env                    # Configuración sensible (NO subir al repo)
└─ README.md
```

---

## Cómo ejecutar el proyecto localmente

### 1. Requisitos previos

- Python 3.11 o superior instalado
- Acceso a MongoDB Atlas (o MongoDB local)

### 2. Clonar el repositorio

```bash
git clone https://github.com/S0ntyrr/FonoApp.git
cd FonoApp
```

### 3. Crear entorno virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
# Windows
py -m pip install -r requirements.txt

# Linux / macOS
python3 -m pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Crear (o editar) el archivo `.env` en la raíz del proyecto:

```env
MONGODB_URI="mongodb+srv://USUARIO:CONTRASENA@cluster0.op2ne2d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGODB_DB_NAME="tesis"
```

> **Nota**: Reemplaza `USUARIO` y `CONTRASENA` con las credenciales de tu Database User en MongoDB Atlas.

### 6. Levantar el servidor de desarrollo

```bash
# Windows
py -m uvicorn app.main:app --reload

# Linux / macOS
python3 -m uvicorn app.main:app --reload
```

### 7. Abrir en el navegador

| URL | Descripción |
|-----|-------------|
| `http://127.0.0.1:8000/` | Redirige automáticamente al login |
| `http://127.0.0.1:8000/auth/login` | Pantalla de inicio de sesión |
| `http://127.0.0.1:8000/auth/registro` | Registro de nuevo paciente |
| `http://127.0.0.1:8000/admin/dashboard` | Panel admin (requiere rol admin) |
| `http://127.0.0.1:8000/doctor/home` | Panel doctor (requiere rol medico) |
| `http://127.0.0.1:8000/paciente/perfil` | Dashboard paciente |
| `http://127.0.0.1:8000/juegos/` | Hub de juegos fonoaudiológicos |
| `http://127.0.0.1:8000/docs` | Documentación automática de la API (Swagger) |

---

## Usuarios de prueba (insertar en MongoDB)

Insertar en la colección `usuarios` de la base de datos `tesis`:

```json
{ "nombre": "Admin General", "email": "admin@tesis.com", "password": "admin123", "rol": "admin", "estado": "activo" }
{ "nombre": "Dra. Ana Gómez", "email": "medico@tesis.com", "password": "medico123", "rol": "medico", "estado": "activo" }
{ "nombre": "Paciente Ejemplo", "email": "paciente@tesis.com", "password": "paciente123", "rol": "paciente", "nivel": 1, "puntos": 0, "estado": "activo" }
```

---

## Flujo principal de la aplicación

```
1. Usuario accede a / → redirige a /auth/login
2. Login exitoso → redirige según rol:
   - admin   → /admin/dashboard
   - medico  → /doctor/home
   - paciente→ /paciente/perfil?email=...
   - emisor  → /emisor/home

3. Paciente:
   - Completa su perfil en /paciente/perfil
   - Accede a juegos en /juegos/
   - Los resultados se guardan en 'resultados_juegos'

4. Admin:
   - Crea asignación automática (POST /admin/asignaciones/auto)
   - Asigna un médico disponible al paciente

5. Doctor:
   - Acepta la asignación (POST /doctor/asignaciones/{id}/aceptar)
   - Revisa resultados de juegos en /doctor/resultados
   - Ve evaluaciones pendientes en /doctor/evaluaciones-pendientes
   - Proporciona feedback al historial de actividades
```

---

## Esquema de base de datos (colecciones)

### `usuarios`
```json
{
  "nombre": "string",
  "email": "string",
  "password": "string (texto plano - encriptar en producción)",
  "rol": "admin | medico | paciente | emisor",
  "nivel": 1,
  "puntos": 0,
  "estado": "activo | ocupado | consulta"
}
```

### `perfiles_pacientes`
```json
{
  "paciente_email": "string",
  "nombre": "string",
  "edad": 8,
  "escolaridad": "Primaria",
  "genero": "Femenino",
  "fecha_registro": "datetime",
  "tutor": "string",
  "parentesco": "Madre"
}
```

### `actividades`
```json
{
  "categoria": "respiracion | fonacion | resonancia | articulacion | prosodia",
  "actividades": ["ejercicio 1", "ejercicio 2"]
}
```

### `asignaciones`
```json
{
  "paciente_email": "string",
  "medico_email": "string",
  "actividades_asignadas": [{"categoria": "respiracion", "actividad": "soplar velas"}],
  "dificultad": "facil | media | dificil",
  "fecha_asignacion": "datetime",
  "estado": "pendiente | aceptada | cancelada"
}
```

### `historial_actividades`
```json
{
  "paciente_email": "string",
  "categoria": "string",
  "actividad": "string",
  "puntos_obtenidos": 10,
  "nivel": 1,
  "fecha": "datetime",
  "feedback": "string | null"
}
```

### `resultados_juegos`
```json
{
  "paciente_email": "string",
  "categoria": "articulacion | resonancia | respiracion | fonacion | practica",
  "juego": "letra_b | veoveo | globo | gol | ...",
  "paso_completado": 3,
  "total_pasos": 5,
  "completado": true,
  "fecha": "datetime",
  "notas": "string | null"
}
```

### `sesiones_app`
```json
{
  "paciente_email": "string",
  "fecha": "datetime",
  "minutos_conectado": 25
}
```

### `contenido_admin`
```json
{
  "imagenes": ["ruta/imagen.png"],
  "videos": ["ruta/video.mp4"],
  "audios_referencia": ["ruta/audio.mp3"],
  "textos_sistema": ["Texto de ejemplo"],
  "instrucciones": {}
}
```

---

## Rutas disponibles

### Autenticación (`/auth`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/auth/login` | Pantalla de login |
| POST | `/auth/login` | Procesar login → redirige según rol |
| GET | `/auth/registro` | Pantalla de registro |
| POST | `/auth/registro` | Crear nuevo paciente |

### Panel Admin (`/admin`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/admin/dashboard` | Dashboard con estadísticas |
| GET | `/admin/pacientes` | Listar pacientes |
| POST | `/admin/pacientes/crear` | Crear paciente |
| POST | `/admin/pacientes/{id}/eliminar` | Eliminar paciente |
| GET | `/admin/medicos` | Listar médicos |
| POST | `/admin/medicos/crear` | Crear médico |
| POST | `/admin/medicos/{id}/eliminar` | Eliminar médico |
| POST | `/admin/medicos/{id}/cambiar_estado` | Cambiar estado médico |
| GET | `/admin/medicos/{id}/editar` | Formulario editar médico |
| POST | `/admin/medicos/{id}/editar` | Guardar edición médico |
| GET | `/admin/medicos/{id}/consultas` | Ver consultas de un médico |
| GET | `/admin/actividades` | Ver categorías de actividades |
| GET | `/admin/asignaciones` | Ver todas las asignaciones |
| POST | `/admin/asignaciones/auto` | Crear asignación automática |
| GET | `/admin/historial` | Historial de actividades |
| GET | `/admin/resultados` | Resultados de juegos |
| GET | `/admin/contenido` | Contenido multimedia |
| POST | `/admin/contenido` | Subir imagen/video |

### Panel Doctor (`/doctor`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/doctor/home` | Panel principal del doctor |
| POST | `/doctor/estado` | Cambiar estado del doctor |
| GET | `/doctor/pacientes` | Ver pacientes |
| GET | `/doctor/actividades` | Ver actividades disponibles |
| GET | `/doctor/asignaciones` | Ver asignaciones |
| POST | `/doctor/asignaciones/{id}/aceptar` | Aceptar asignación |
| POST | `/doctor/asignaciones/{id}/cancelar` | Cancelar asignación |
| GET | `/doctor/historial` | Historial de actividades |
| GET | `/doctor/resultados` | Resultados de juegos |
| GET | `/doctor/evaluaciones-pendientes` | Actividades sin feedback |

### App Paciente (`/paciente`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/paciente/perfil` | Dashboard del paciente |
| POST | `/paciente/perfil` | Guardar/actualizar perfil |

### Juegos (`/juegos`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/juegos/` | Hub principal de juegos |
| GET | `/juegos/respiracion` | Hub respiración |
| GET | `/juegos/respiracion/globo` | Juego: infla el globo |
| GET | `/juegos/respiracion/molino` | Juego: el molino de Pepe |
| GET | `/juegos/fonacion` | Hub fonación |
| GET | `/juegos/fonacion/gol` | Juego: haz un gol |
| GET | `/juegos/fonacion/escala` | Juego: escala musical |
| GET | `/juegos/resonancia` | Hub resonancia |
| GET | `/juegos/resonancia/escaleras` | Juego: escaleras |
| GET | `/juegos/resonancia/piano` | Juego: piano Estrellita |
| GET | `/juegos/resonancia/veoveo` | Juego: veo veo |
| GET | `/juegos/articulacion` | Hub articulación |
| GET | `/juegos/articulacion/letra-b` | Juego: letra B |
| GET | `/juegos/articulacion/letra-d` | Juego: letra D |
| GET | `/juegos/articulacion/letra-f` | Juego: letra F |
| GET | `/juegos/articulacion/letra-r` | Juego: letra R |
| GET | `/juegos/practica` | Hub practica conmigo |
| GET | `/juegos/practica/rompecabezas` | Juego: rompecabezas |
| GET | `/juegos/practica/cara` | Juego: crea tu personaje |
| GET | `/juegos/practica/asociacion` | Juego: asociación de imágenes |
| POST | `/juegos/resultado` | Guardar resultado de juego |

---

## Notas de desarrollo

- **Autenticación**: Actualmente usa sesión simple por query param (`?email=...`). En producción se debe implementar JWT o sesiones con cookies.
- **Contraseñas**: Se guardan en texto plano. En producción usar `bcrypt` o similar.
- **Estado del doctor**: Hardcodeado como `doctor@tesis.com`. En producción debe venir del usuario logueado.
- **Diagramas**: Ver carpeta `DOCS/` con diagramas PlantUML (casos de uso, clases, estados, actores).
