"""
FonoApp - App web de fono interactiva
=======================================================
Punto de entrada principal de la app FastAPI.

Arquitectura:
- /auth/*      → Autenticación (login, registro)
- /paciente/*  → Dashboard del paciente (perfil, actividades)
- /emisor/*    → Panel del emisor (placeholder)
- /admin/*     → Panel de administración (CRUD completo)
- /doctor/*    → Panel del médico/terapeuta
- /juegos/*    → Hub de juegos fonoaudiológicos (23 juegos, 7 categorías)
- /            → Redirige al login

Base de datos: MongoDB Atlas (colección 'tesis')
Colecciones principales:
  - usuarios: pacientes, médicos, admins
  - perfiles_pacientes: datos extendidos del paciente
  - actividades: catálogo de juegos por categoría
  - asignaciones: médico asignado a cada paciente
  - resultados_juegos: resultados de cada juego jugado
  - historial_actividades: actividades completadas (para evaluación del médico)
  - sesiones_app: días y minutos de uso del paciente
  - contenido_admin: textos, imágenes y videos del sistema
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .database import connect_to_mongo, close_mongo_connection
from .config import settings
from .routers import auth, emisor, paciente
from .routers import routes_admin, routes_doctor, routes_juegos

@asynccontextmanager
async def lifespan(app):
    """
    Ciclo de vida de la app:
    - Al iniciar: conecta a MongoDB Atlas
    - Al apagar: cierra la conexión
    """
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="FonoApp",
    description="Plataforma web de fonoaudiología interactiva con juegos terapéuticos.",
    version="2.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE_NAME,
    max_age=settings.SESSION_MAX_AGE,
    same_site="lax",
    https_only=settings.SESSION_HTTPS_ONLY,
)


@app.exception_handler(HTTPException)
async def manejar_error_autenticacion(request: Request, exc: HTTPException):
    """Evita mostrar un JSON crudo 401/403 al navegar: redirige al login en peticiones de página."""
    if exc.status_code in (401, 403):
        acepta_html = "text/html" in request.headers.get("accept", "")
        if request.method == "GET" and acepta_html:
            return RedirectResponse(url="/auth/login", status_code=303)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/", include_in_schema=False)
async def raiz():
    """
    Ruta raiz: redirige automaticamente al login.
    Todos los usuarios deben autenticarse antes de acceder.
    """
    return RedirectResponse(url="/auth/login")


# ── Registrar routers ──────────────────────────────────────────────────────────
# Autenticación (login, registro)
app.include_router(auth.router)

# App del emisor (placeholder para futuras funcionalidades)
app.include_router(emisor.router)

# Dashboard del paciente (perfil, actividades del día, calendario)
app.include_router(paciente.router)

# Panel de administración (CRUD de usuarios, asignaciones, contenido)
app.include_router(routes_admin.router)

# Panel del médico/terapeuta (pacientes, evaluaciones, historial)
app.include_router(routes_doctor.router)

# Hub de juegos fonoaudiológicos (23 juegos en 7 categorías)
app.include_router(routes_juegos.router)

# ── Archivos estáticos ─────────────────────────────────────────────────────────
# CSS, imágenes, JavaScript del cliente
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates Jinja2 (usado en algunos routers directamente)
templates = Jinja2Templates(directory="app/templates")
