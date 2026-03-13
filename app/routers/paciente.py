"""
FonoApp - Router del Paciente
==============================
Maneja el dashboard y perfil del paciente.

Rutas:
  GET  /paciente/perfil?email=... → Dashboard del paciente
  POST /paciente/perfil           → Guardar/actualizar perfil

Dashboard del paciente incluye:
  1. Tarjeta de bienvenida personalizada
  2. Acceso rápido al hub de juegos
  3. Actividades del día (4 actividades deterministas por día/email)
  4. Calendario de uso mensual

Sistema de actividades del día:
  - Si el paciente tiene una asignación aceptada con actividades específicas,
    se muestran esas actividades mapeadas a los juegos reales.
  - Si no hay asignación, se seleccionan 4 actividades aleatorias pero
    DETERMINISTAS (mismas actividades todo el día para el mismo paciente).
  - La semilla aleatoria se basa en: fecha + email del paciente.
  - Las actividades son clickables y llevan directamente al juego.
  - El progreso se guarda en localStorage del navegador (por URL de actividad).

Colecciones MongoDB usadas:
  - perfiles_pacientes: datos del perfil
  - sesiones_app: historial de uso para el calendario
  - asignaciones: actividades asignadas por el médico
"""

from datetime import datetime
from collections import defaultdict
from random import sample, seed as random_seed

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database import get_db
from ..models import PerfilPaciente, SesionApp
from ..security import get_current_user

router = APIRouter(prefix="/paciente", tags=["paciente-app"])
templates = Jinja2Templates(directory="app/templates")

# ── Catálogo de actividades reales ─────────────────────────────────────────────
# Cada actividad tiene: categoria, nombre para mostrar, y URL del juego.
# Este catálogo se usa para mostrar actividades clickables en el dashboard.
# Debe mantenerse sincronizado con las rutas en routes_juegos.py.
ACTIVIDADES_REALES = [
    # Respiración (2 juegos)
    {"categoria": "Respiración", "actividad": "Infla el globo", "url": "/juegos/respiracion/globo"},
    {"categoria": "Respiración", "actividad": "El molino de Pepe", "url": "/juegos/respiracion/molino"},
    # Fonación (2 juegos)
    {"categoria": "Fonación", "actividad": "¡Haz un gol!", "url": "/juegos/fonacion/gol"},
    {"categoria": "Fonación", "actividad": "Escala musical", "url": "/juegos/fonacion/escala"},
    # Resonancia (3 juegos)
    {"categoria": "Resonancia", "actividad": "Escaleras de tono", "url": "/juegos/resonancia/escaleras"},
    {"categoria": "Resonancia", "actividad": "Piano - Estrellita", "url": "/juegos/resonancia/piano"},
    {"categoria": "Resonancia", "actividad": "¡Veo, veo!", "url": "/juegos/resonancia/veoveo"},
    # Articulación (6 juegos)
    {"categoria": "Articulación", "actividad": "Letra B", "url": "/juegos/articulacion/letra-b"},
    {"categoria": "Articulación", "actividad": "Letra D", "url": "/juegos/articulacion/letra-d"},
    {"categoria": "Articulación", "actividad": "Letra F", "url": "/juegos/articulacion/letra-f"},
    {"categoria": "Articulación", "actividad": "Letra R", "url": "/juegos/articulacion/letra-r"},
    {"categoria": "Articulación", "actividad": "Completa la palabra", "url": "/juegos/articulacion/completa-palabra"},
    {"categoria": "Articulación", "actividad": "¡Acelera la moto!", "url": "/juegos/articulacion/moto-voz"},
    # Prosodia (4 juegos)
    {"categoria": "Prosodia", "actividad": "Adivina el animal", "url": "/juegos/prosodia/adivina-animal"},
    {"categoria": "Prosodia", "actividad": "Trabalenguas", "url": "/juegos/prosodia/trabalenguas"},
    {"categoria": "Prosodia", "actividad": "Relaciona la adivinanza", "url": "/juegos/prosodia/adivinanza-imagen"},
    {"categoria": "Prosodia", "actividad": "Completa la canción", "url": "/juegos/prosodia/completa-cancion"},
    # Discriminación Auditiva (3 juegos)
    {"categoria": "Discriminación Auditiva", "actividad": "Sonidos de animales", "url": "/juegos/discriminacion/sonidos-animales"},
    {"categoria": "Discriminación Auditiva", "actividad": "Sonidos de objetos", "url": "/juegos/discriminacion/sonidos-objetos"},
    {"categoria": "Discriminación Auditiva", "actividad": "Arrastra al sonido", "url": "/juegos/discriminacion/arrastra-sonido"},
    # Practica Conmigo (3 juegos)
    {"categoria": "Practica Conmigo", "actividad": "Rompecabezas", "url": "/juegos/practica/rompecabezas"},
    {"categoria": "Practica Conmigo", "actividad": "Crea tu personaje", "url": "/juegos/practica/cara"},
    {"categoria": "Practica Conmigo", "actividad": "Asociación de imágenes", "url": "/juegos/practica/asociacion"},
]


@router.get("/perfil", response_class=HTMLResponse)
async def vista_perfil_paciente(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    email: str = "",  # Se obtiene del URL param o de la cookie de sesión
):
    """
    Dashboard principal del paciente.
    
    Muestra:
    1. Perfil del paciente (si existe en perfiles_pacientes)
    2. Tarjeta de bienvenida con el nombre
    3. Acceso rápido al hub de juegos
    4. 4 actividades del día (deterministas por fecha+email)
    5. Calendario de uso del mes actual
    
    Las actividades del día:
    - Son deterministas: mismas actividades todo el día para el mismo paciente
    - Cambian automáticamente al día siguiente
    - Si hay asignación aceptada del médico, se usan esas actividades
    - Si no, se seleccionan 4 de diferentes categorías aleatoriamente
    
    El progreso de actividades se guarda en localStorage del navegador
    usando la URL de cada actividad como clave (no el índice).
    """
    # Verificar que el usuario sea paciente (o admin/médico que revisa)
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    # ── Obtener email del paciente ─────────────────────────────────────────────
    # Prioridad: URL param → cookie de sesión → fallback
    if not email:
        email = request.cookies.get("usuario_email", "paciente@tesis.com")
    
    # ── Cargar perfil del paciente ─────────────────────────────────────────────
    perfil_doc = await db["perfiles_pacientes"].find_one({"paciente_email": email})
    perfil: PerfilPaciente | None = None
    if perfil_doc:
        perfil_doc["_id"] = str(perfil_doc["_id"])
        perfil = PerfilPaciente(**perfil_doc)

    # ── Cargar sesiones del mes actual para el calendario ──────────────────────
    hoy = datetime.utcnow()
    cursor = db["sesiones_app"].find({
        "paciente_email": email,
        "fecha": {"$gte": datetime(hoy.year, hoy.month, 1)},
    })
    sesiones_por_dia: dict[str, int] = defaultdict(int)
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        sesion = SesionApp(**doc)
        dia_str = sesion.fecha.strftime("%Y-%m-%d")
        sesiones_por_dia[dia_str] += sesion.minutos_conectado

    # ── Determinar actividades del día ─────────────────────────────────────────
    # Primero intentar obtener actividades asignadas por el médico
    asignacion = await db["asignaciones"].find_one({"paciente_email": email, "estado": "aceptada"})
    
    if asignacion and asignacion.get("actividades_asignadas"):
        # Usar actividades asignadas por el médico, mapeadas a juegos reales
        actividades_asignadas = asignacion.get("actividades_asignadas", [])
        actividades_disponibles_raw = []
        for act in actividades_asignadas:
            cat = act.get("categoria", "")
            nombre = act.get("actividad", "")
            # Buscar la actividad real correspondiente por categoría
            match = next((a for a in ACTIVIDADES_REALES if a["categoria"].lower() == cat.lower()), None)
            if match:
                actividades_disponibles_raw.append(match)
            else:
                # Si no hay match, crear una actividad genérica que lleva al hub
                actividades_disponibles_raw.append({
                    "categoria": cat or "General",
                    "actividad": nombre or "Actividad",
                    "url": "/juegos/"
                })
    else:
        # Selección DETERMINISTA por día y email
        # La misma semilla garantiza las mismas actividades todo el día
        import time as _time
        seed_str = f"{hoy.strftime('%Y-%m-%d')}-{email}"
        seed_val = sum(ord(c) for c in seed_str)
        random_seed(seed_val)
        
        # Usar lista ORDENADA de categorías para garantizar determinismo
        # (los sets de Python tienen orden no determinista)
        categorias = sorted(list({a["categoria"] for a in ACTIVIDADES_REALES}))
        categorias_elegidas = sample(categorias, min(4, len(categorias)))
        actividades_disponibles_raw = []
        for cat in categorias_elegidas:
            # Ordenar opciones por nombre para garantizar determinismo
            opciones_cat = sorted(
                [a for a in ACTIVIDADES_REALES if a["categoria"] == cat],
                key=lambda x: x["actividad"]
            )
            if opciones_cat:
                actividades_disponibles_raw.append(sample(opciones_cat, 1)[0])
        
        # Resetear la semilla aleatoria para no afectar otras partes del código
        random_seed(int(_time.time()))

    # ── Agrupar actividades por categoría para la plantilla ────────────────────
    categorias_dict = defaultdict(list)
    for act in actividades_disponibles_raw:
        categorias_dict[act["categoria"]].append(act)
    
    actividades_disponibles = [
        {"categoria": cat, "actividades": acts}
        for cat, acts in categorias_dict.items()
    ]

    return templates.TemplateResponse(
        "paciente/perfil.html",
        {
            "request": request,
            "titulo_pagina": "Mi perfil",
            "perfil": perfil,
            "sesiones_por_dia": sesiones_por_dia,
            "email_paciente": email,
            "actividades_disponibles": actividades_disponibles,
        },
    )


@router.post("/perfil")
async def guardar_perfil_paciente(
    db: AsyncIOMotorDatabase = Depends(get_db),
    paciente_email: str = Form(...),
    nombre: str = Form(...),
    edad: int = Form(...),
    escolaridad: str = Form(...),   # Preescolar, Primaria, Secundaria, etc.
    genero: str = Form(...),        # Masculino, Femenino, Otro
    tutor: str = Form(...),
    parentesco: str = Form(...),    # Madre, Padre, Abuelo, etc.
):
    """
    Crea o actualiza el perfil extendido del paciente.
    
    Si ya existe un perfil para el email, lo actualiza manteniendo
    la fecha_registro original.
    
    Si no existe, crea uno nuevo con la fecha_registro actual.
    
    Después de guardar, redirige de vuelta al dashboard del paciente.
    """
    # Buscar si ya existe un perfil para este paciente
    existente = await db["perfiles_pacientes"].find_one({"paciente_email": paciente_email})

    datos = {
        "paciente_email": paciente_email,
        "nombre": nombre,
        "edad": edad,
        "escolaridad": escolaridad,
        "genero": genero,
        "tutor": tutor,
        "parentesco": parentesco,
    }

    if existente:
        # Actualizar perfil existente, manteniendo la fecha de registro original
        datos["fecha_registro"] = existente.get("fecha_registro", datetime.utcnow())
        await db["perfiles_pacientes"].update_one(
            {"_id": existente["_id"]},
            {"$set": datos},
        )
    else:
        # Crear nuevo perfil con la fecha actual
        datos["fecha_registro"] = datetime.utcnow()
        await db["perfiles_pacientes"].insert_one(datos)

    # Redirigir de vuelta al dashboard del paciente
    return RedirectResponse(url=f"/paciente/perfil?email={paciente_email}", status_code=303)
