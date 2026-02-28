"""
FonoApp - Aplicación web de fonoaudiología interactiva
=======================================================
Punto de entrada principal de la aplicación FastAPI.

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
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import connect_to_mongo, close_mongo_connection
from .routers import auth, emisor, paciente
from .web import routes_admin, routes_doctor, routes_juegos


@asynccontextmanager
async def lifespan(app):
    """
    Ciclo de vida de la aplicación:
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


@app.get("/", include_in_schema=False)
async def raiz():
    """
    Ruta raíz: redirige automáticamente al login.
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
