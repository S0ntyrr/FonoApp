```markdown
## FonoApp – Backend (FastAPI + MongoDB Atlas)

Aplicación para apoyo en fonoaudiología con:

- **Panel Admin (web)**: gestión de pacientes, actividades, asignaciones, historial y contenido del sistema.
- **Panel Doctor (web)**: acceso rápido a pacientes, actividades, asignaciones y al historial de uso.
- **App Paciente (web/móvil)**: registro/login, perfil del paciente y calendario de uso.
- **App Emisor (móvil / webview)**: pantalla básica de inicio (lista para extender).

---

## Tecnologías

- **Backend**: Python 3 + FastAPI
- **Base de datos**: MongoDB Atlas (cluster remoto)
- **Driver**: Motor (async, sobre PyMongo)
- **Templates**: Jinja2
- **Estilos**: CSS simple (fondo blanco, botones y títulos rojos)

---

## Estructura de carpetas principal

```text
FonoApp/
├─ app/
│  ├─ main.py              # Punto de entrada FastAPI
│  ├─ config.py            # Configuración (MongoDB URI, nombre BD, .env)
│  ├─ database.py          # Conexión a MongoDB (Motor)
│  ├─ models.py            # Modelos Pydantic (usuarios, actividades, etc.)
│  ├─ routers/             # Rutas tipo API / vistas app
│  │  ├─ auth.py           # Login y registro
│  │  ├─ emisor.py         # Home emisor (placeholder)
│  │  ├─ paciente.py       # Perfil y calendario de uso del paciente
│  ├─ web/                 # Rutas web (HTML) para admin/doctor
│  │  ├─ routes_admin.py   # Panel admin
│  │  ├─ routes_doctor.py  # Panel doctor
│  ├─ templates/           # Vistas HTML (Jinja2)
│  │  ├─ base.html
│  │  ├─ auth/             # login / registro
│  │  ├─ admin/            # dashboard, pacientes, actividades, etc.
│  │  ├─ doctor/           # home doctor, pacientes, actividades, etc.
│  │  ├─ paciente/         # perfil + calendario
│  │  ├─ emisor/           # home emisor
│  ├─ static/
│     ├─ css/estilos.css   # paleta rojo/blanco y layout móvil
├─ requirements.txt
├─ .env                    # Configuración sensible (no se sube al repo)
└─ README.md
```

---

## Configuración de entorno

### 1. Dependencias

```bash
py -m pip install -r requirements.txt
```

Contenido de `requirements.txt`:

```txt
fastapi
uvicorn[standard]
motor
python-dotenv
jinja2
pydantic-settings
python-multipart
email-validator
pydantic
```

### 2. Variables de entorno (`.env`)

Crear un archivo `.env` en la raíz del proyecto:

```env
MONGODB_URI="mongodb+srv://USUARIO:CONTRASENA@cluster0.op2ne2d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGODB_DB_NAME="fono_app"
```

- `USUARIO` y `CONTRASENA` deben corresponder a un **Database User** de MongoDB Atlas.
- `MONGODB_DB_NAME` debe ser el nombre de la base de datos que estás usando.

---

## Esquema de base de datos (colecciones principales)

### Colección `usuarios`

Ejemplos:

```json
{
  "nombre": "Admin General",
  "email": "admin@tesis.com",
  "password": "admin123",
  "rol": "admin",
  "estado": "activo"
}
```

```json
{
  "nombre": "Dra. Ana Gómez",
  "email": "medico@tesis.com",
  "password": "medico123",
  "rol": "medico",
  "especialidad": "Fonoaudiología",
  "estado": "activo"
}
```

```json
{
  "nombre": "Paciente Ejemplo",
  "email": "paciente@tesis.com",
  "password": "paciente123",
  "rol": "paciente",
  "nivel": 1,
  "puntos": 0,
  "estado": "activo"
}
```

- Los **nuevos pacientes** creados por registro o panel admin se guardan con:
  - `rol: "paciente"`, `nivel: 1`, `puntos: 0`, `estado: "activo"`.

### Colección `actividades`

```json
{
  "categoria": "respiracion",
  "actividades": [
    "ejercicio 1",
    "ejercicio 2",
    "ejercicio 3"
  ]
}
```

Categorías esperadas (según tu BD):

- `respiracion`
- `fonacion`
- `resonancia`
- `articulacion`
- `prosodia`
- `discriminacion_auditiva`

### Colección `asignaciones`

```json
{
  "paciente_email": "paciente@tesis.com",
  "medico_email": "medico@tesis.com",
  "actividades_asignadas": [
    { "categoria": "respiracion", "actividad": "soplar velas" },
    { "categoria": "articulacion", "actividad": "completar palabras" }
  ],
  "dificultad": "medio",
  "fecha_asignacion": { "$date": "2025-01-15T00:00:00.000Z" }
}
```

- En el código, `actividades_asignadas` se trata como `list[dict]` para aceptar estos objetos.

### Colección `contenido_admin`

```json
{
  "imagenes": ["url1.png", "url2.png"],
  "videos": ["video1.mp4"],
  "audios_referencia": ["audio1.mp3"],
  "textos_sistema": ["Texto de ejemplo"],
  "instrucciones": {
    "nota": "Instrucciones generales para el sistema"
  }
}
```

### Colección `historial_actividades`

```json
{
  "paciente_email": "paciente@tesis.com",
  "categoria": "articulacion",
  "actividad": "completar palabras",
  "puntos_obtenidos": 10,
  "nivel": 1,
  "fecha": { "$date": "2025-01-15T05:00:00.000Z" },
  "feedback": "Excelente pronunciación"
}
```

### Colección `perfiles_pacientes` (creada por el propio paciente)

```json
{
  "paciente_email": "paciente@tesis.com",
  "nombre": "Paciente Ejemplo",
  "edad": 8,
  "escolaridad": "Primaria",
  "genero": "Femenino",
  "fecha_registro": { "$date": "2025-01-10T00:00:00.000Z" },
  "tutor": "María Pérez",
  "parentesco": "Madre"
}
```

- Esta colección se llena/actualiza desde la pantalla `/paciente/perfil`.

### Colección `sesiones_app`

```json
{
  "paciente_email": "paciente@tesis.com",
  "fecha": { "$date": "2025-01-15T00:00:00.000Z" },
  "minutos_conectado": 25
}
```

- Un documento por día y paciente, usado para el **calendario de uso**.

---

## Rutas principales

### Autenticación

- `GET /auth/login` – pantalla de inicio de sesión.
- `GET /auth/registro` – registro de nuevo paciente.
- `POST /auth/registro` – crea usuario `rol = "paciente"`.
- `POST /auth/login` – redirige según **rol**:

  - `admin`   → `/admin/dashboard`
  - `medico`  → `/doctor/home`
  - `paciente`→ `/paciente/perfil?email=...`
  - otros / emisor → `/emisor/home`

### Panel Admin (web)

- `GET /admin/dashboard` – resumen (usuarios, pacientes, médicos) + accesos.
- `GET /admin/pacientes` – listado y creación de pacientes.
- `POST /admin/pacientes/crear` – crear paciente.
- `POST /admin/pacientes/{id}/eliminar` – eliminar paciente.
- `GET /admin/actividades` – ver categorías y actividades (`actividades`).
- `GET /admin/asignaciones` – ver todas las asignaciones (`asignaciones`).
- `GET /admin/historial` – historial de actividades (`historial_actividades`).
- `GET /admin/contenido` – contenido multimedia y textos (`contenido_admin`).

### Panel Doctor (web)

- `GET /doctor/home` – home del doctor con menú.
- `GET /doctor/pacientes` – lista de pacientes (`usuarios.rol = "paciente"`).
- `GET /doctor/actividades` – ver categorías/actividades (`actividades`).
- `GET /doctor/asignaciones` – ver asignaciones (`asignaciones`).
- `GET /doctor/historial` – historial (`historial_actividades`).

### App Paciente

- `GET /paciente/perfil?email=correo`  
  - Muestra/edita perfil (nombre, edad, escolaridad, género, tutor, parentesco).  
  - Muestra calendario de uso usando `sesiones_app`.
- `POST /paciente/perfil`  
  - Crea o actualiza documento en `perfiles_pacientes`.

### App Emisor (placeholder)

- `GET /emisor/home` – pantalla simple de bienvenida, lista para extender (por ejemplo, envío de evaluaciones).

---

## Estilos (diseño)

- Paleta principal:
  - Fondo: blanco
  - Títulos y botones: rojo
- Archivo de estilos: `app/static/css/estilos.css`  
  - Define layout móvil (`pantalla-movil`), botones (`boton-rojo`, `boton-rojo-borde`), menú lateral del paciente (`layout-lateral`, `menu-lateral`), calendario (`calendario-grid`, etc.).

---

## Cómo ejecutar el proyecto

1. Instalar dependencias:

```bash
py -m pip install -r requirements.txt
```

2. Configurar `.env` con la URI de MongoDB Atlas y el nombre de la base.

3. Levantar el servidor de desarrollo:

```bash
py -m uvicorn app.main:app --reload
```

4. Probar desde el navegador:

- Login: `http://127.0.0.1:8000/auth/login`
- Panel admin: se entra con usuario `rol = "admin"`.
- Panel doctor: se entra con usuario `rol = "medico"`.
- Paciente: se entra con usuario `rol = "paciente"` y se redirige a su perfil.

---
