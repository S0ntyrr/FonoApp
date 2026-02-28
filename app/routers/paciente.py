from datetime import datetime
from collections import defaultdict
from random import sample

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database import get_db
from ..models import PerfilPaciente, SesionApp

router = APIRouter(prefix="/paciente", tags=["paciente-app"])

templates = Jinja2Templates(directory="app/templates")

# Actividades reales que corresponden a juegos implementados
ACTIVIDADES_REALES = [
    {"categoria": "Respiración", "actividad": "Infla el globo", "url": "/juegos/respiracion/globo"},
    {"categoria": "Respiración", "actividad": "El molino de Pepe", "url": "/juegos/respiracion/molino"},
    {"categoria": "Fonación", "actividad": "¡Haz un gol!", "url": "/juegos/fonacion/gol"},
    {"categoria": "Fonación", "actividad": "Escala musical", "url": "/juegos/fonacion/escala"},
    {"categoria": "Resonancia", "actividad": "Escaleras de tono", "url": "/juegos/resonancia/escaleras"},
    {"categoria": "Resonancia", "actividad": "Piano - Estrellita", "url": "/juegos/resonancia/piano"},
    {"categoria": "Resonancia", "actividad": "¡Veo, veo!", "url": "/juegos/resonancia/veoveo"},
    {"categoria": "Articulación", "actividad": "Letra B", "url": "/juegos/articulacion/letra-b"},
    {"categoria": "Articulación", "actividad": "Letra D", "url": "/juegos/articulacion/letra-d"},
    {"categoria": "Articulación", "actividad": "Letra F", "url": "/juegos/articulacion/letra-f"},
    {"categoria": "Articulación", "actividad": "Letra R", "url": "/juegos/articulacion/letra-r"},
    {"categoria": "Articulación", "actividad": "Completa la palabra", "url": "/juegos/articulacion/completa-palabra"},
    {"categoria": "Articulación", "actividad": "¡Acelera la moto!", "url": "/juegos/articulacion/moto-voz"},
    {"categoria": "Prosodia", "actividad": "Adivina el animal", "url": "/juegos/prosodia/adivina-animal"},
    {"categoria": "Prosodia", "actividad": "Trabalenguas", "url": "/juegos/prosodia/trabalenguas"},
    {"categoria": "Prosodia", "actividad": "Relaciona la adivinanza", "url": "/juegos/prosodia/adivinanza-imagen"},
    {"categoria": "Prosodia", "actividad": "Completa la canción", "url": "/juegos/prosodia/completa-cancion"},
    {"categoria": "Discriminación Auditiva", "actividad": "Sonidos de animales", "url": "/juegos/discriminacion/sonidos-animales"},
    {"categoria": "Discriminación Auditiva", "actividad": "Sonidos de objetos", "url": "/juegos/discriminacion/sonidos-objetos"},
    {"categoria": "Discriminación Auditiva", "actividad": "Arrastra al sonido", "url": "/juegos/discriminacion/arrastra-sonido"},
    {"categoria": "Practica Conmigo", "actividad": "Rompecabezas", "url": "/juegos/practica/rompecabezas"},
    {"categoria": "Practica Conmigo", "actividad": "Crea tu personaje", "url": "/juegos/practica/cara"},
    {"categoria": "Practica Conmigo", "actividad": "Asociación de imágenes", "url": "/juegos/practica/asociacion"},
]


@router.get("/perfil", response_class=HTMLResponse)
async def vista_perfil_paciente(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    email: str = "paciente@tesis.com",
):
    """
    Muestra el dashboard del paciente con actividades aleatorias de la sesión.
    """
    perfil_doc = await db["perfiles_pacientes"].find_one({"paciente_email": email})
    perfil: PerfilPaciente | None = None
    if perfil_doc:
        perfil_doc["_id"] = str(perfil_doc["_id"])
        perfil = PerfilPaciente(**perfil_doc)

    # Sesiones del mes actual
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

    # Actividades aleatorias de la sesión (4 actividades de diferentes categorías)
    # Primero intentar obtener de la BD (asignaciones del médico)
    asignacion = await db["asignaciones"].find_one({"paciente_email": email, "estado": "aceptada"})
    
    if asignacion and asignacion.get("actividades_asignadas"):
        # Usar actividades asignadas por el médico, mapeadas a juegos reales
        actividades_asignadas = asignacion.get("actividades_asignadas", [])
        actividades_disponibles_raw = []
        for act in actividades_asignadas:
            cat = act.get("categoria", "")
            nombre = act.get("actividad", "")
            # Buscar en actividades reales
            match = next((a for a in ACTIVIDADES_REALES if a["categoria"].lower() == cat.lower()), None)
            if match:
                actividades_disponibles_raw.append(match)
            else:
                # Agregar actividad genérica con link al hub
                actividades_disponibles_raw.append({
                    "categoria": cat or "General",
                    "actividad": nombre or "Actividad",
                    "url": "/juegos/"
                })
    else:
        # Selección aleatoria de actividades reales (4 de diferentes categorías)
        categorias = list({a["categoria"] for a in ACTIVIDADES_REALES})
        actividades_disponibles_raw = []
        for cat in sample(categorias, min(4, len(categorias))):
            opciones_cat = [a for a in ACTIVIDADES_REALES if a["categoria"] == cat]
            if opciones_cat:
                actividades_disponibles_raw.append(sample(opciones_cat, 1)[0])

    # Agrupar por categoría para la plantilla
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
    escolaridad: str = Form(...),
    genero: str = Form(...),
    tutor: str = Form(...),
    parentesco: str = Form(...),
):
    """
    Crea o actualiza el perfil del paciente.
    """
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
        datos["fecha_registro"] = existente.get("fecha_registro", datetime.utcnow())
        await db["perfiles_pacientes"].update_one(
            {"_id": existente["_id"]},
            {"$set": datos},
        )
    else:
        datos["fecha_registro"] = datetime.utcnow()
        await db["perfiles_pacientes"].insert_one(datos)

    return RedirectResponse(url=f"/paciente/perfil?email={paciente_email}", status_code=303)
