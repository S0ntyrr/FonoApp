"""
FonoApp - Router del Médico/Terapeuta
=======================================
Panel del médico con acceso a sus pacientes y herramientas de evaluación.

Rutas principales:
  GET  /doctor/home                          → Panel principal del médico
  POST /doctor/estado                        → Cambiar estado (activo/ocupado/consulta)
  
  Gestión de pacientes:
  GET  /doctor/pacientes                     → Lista de pacientes con stats de juegos
  GET  /doctor/pacientes/{id}                → Perfil detallado con gráfica de progreso
  POST /doctor/pacientes/{id}/editar         → Editar datos básicos del paciente
  
  Actividades y juegos:
  GET  /doctor/actividades                   → Lista de juegos disponibles (23 juegos)
  
  Asignaciones:
  GET  /doctor/asignaciones                  → Ver asignaciones + pacientes sin asignar
  POST /doctor/asignaciones/{id}/aceptar     → Aceptar asignación
  POST /doctor/asignaciones/{id}/cancelar    → Cancelar asignación
  
  Evaluación y seguimiento:
  GET  /doctor/historial                     → Historial de actividades con filtros
  GET  /doctor/resultados                    → Resultados de juegos de todos los pacientes
  GET  /doctor/evaluaciones-pendientes       → Actividades sin feedback del médico
  POST /doctor/evaluaciones/{id}/feedback    → Guardar evaluación/feedback

Estado del médico:
  El estado se guarda en la colección 'usuarios' y es visible desde el panel admin.
  Estados: 'activo' (disponible), 'ocupado', 'consulta' (en sesión activa)
  
  NOTA: El email del médico se pasa como query param (?email=...).
  En producción, obtener del token de sesión.

Colecciones MongoDB usadas:
  - usuarios: datos del médico y pacientes
  - asignaciones: asignaciones médico-paciente
  - historial_actividades: actividades completadas (con/sin feedback)
  - resultados_juegos: resultados detallados de juegos
  - perfiles_pacientes: datos extendidos del paciente
"""

from datetime import datetime
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette import status
from bson import ObjectId
from ..database import get_db
from ..models import Asignacion, HistorialActividad
from ..security import get_current_user

router = APIRouter(prefix="/doctor", tags=["doctor-web"])
templates = Jinja2Templates(directory="app/templates")

JUEGOS_DISPONIBLES = [
    {"categoria": "Respiración", "juegos": [
        {"nombre": "Infla el globo", "url": "/juegos/respiracion/globo"},
        {"nombre": "El molino de Pepe", "url": "/juegos/respiracion/molino"},
    ]},
    {"categoria": "Fonación", "juegos": [
        {"nombre": "¡Haz un gol!", "url": "/juegos/fonacion/gol"},
        {"nombre": "Escala musical", "url": "/juegos/fonacion/escala"},
    ]},
    {"categoria": "Resonancia", "juegos": [
        {"nombre": "Escaleras de tono", "url": "/juegos/resonancia/escaleras"},
        {"nombre": "Piano - Estrellita", "url": "/juegos/resonancia/piano"},
        {"nombre": "¡Veo, veo!", "url": "/juegos/resonancia/veoveo"},
    ]},
    {"categoria": "Articulación", "juegos": [
        {"nombre": "Letra B", "url": "/juegos/articulacion/letra-b"},
        {"nombre": "Letra D", "url": "/juegos/articulacion/letra-d"},
        {"nombre": "Letra F", "url": "/juegos/articulacion/letra-f"},
        {"nombre": "Letra R", "url": "/juegos/articulacion/letra-r"},
    ]},
    {"categoria": "Practica Conmigo", "juegos": [
        {"nombre": "Rompecabezas", "url": "/juegos/practica/rompecabezas"},
        {"nombre": "Crea tu personaje", "url": "/juegos/practica/cara"},
        {"nombre": "Asociación de imágenes", "url": "/juegos/practica/asociacion"},
    ]},
]


@router.get("/home", response_class=HTMLResponse)
async def home_doctor(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    # Verificar que el usuario sea médico
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)
    
    # Obtener email del médico: URL param → cookie de sesión → fallback
    email_doctor = request.query_params.get("email") or request.cookies.get("usuario_email", "doctor@tesis.com")
    doctor_doc = await db["usuarios"].find_one({"email": email_doctor, "rol": "medico"})
    if not doctor_doc:
        doctor_doc = await db["usuarios"].find_one({"rol": "medico"})
    estado_actual = doctor_doc.get("estado", "activo") if doctor_doc else "activo"
    nombre_doctor = doctor_doc.get("nombre", "Doctor") if doctor_doc else "Doctor"
    email_doctor = doctor_doc.get("email", email_doctor) if doctor_doc else email_doctor
    pendientes = await db["historial_actividades"].count_documents({"$or": [{"feedback": None}, {"feedback": ""}]})
    return templates.TemplateResponse("doctor/home.html", {
        "request": request, "titulo_pagina": "Panel del doctor",
        "estado_actual": estado_actual, "nombre_doctor": nombre_doctor,
        "email_doctor": email_doctor, "evaluaciones_pendientes": pendientes,
    })


@router.get("/pacientes", response_class=HTMLResponse)
async def vista_pacientes_doctor(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    cursor = db["usuarios"].find({"rol": "paciente"})
    pacientes = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        total_j = await db["resultados_juegos"].count_documents({"paciente_email": doc["email"]})
        completados_j = await db["resultados_juegos"].count_documents({"paciente_email": doc["email"], "completado": True})
        doc["total_juegos"] = total_j
        doc["juegos_completados"] = completados_j
        pacientes.append(doc)
    return templates.TemplateResponse("doctor/pacientes.html", {
        "request": request, "titulo_pagina": "Pacientes del sistema", "pacientes": pacientes,
    })


@router.get("/pacientes/{paciente_id}", response_class=HTMLResponse)
async def perfil_paciente_doctor(paciente_id: str, request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    paciente = await db["usuarios"].find_one({"_id": ObjectId(paciente_id)})
    if not paciente:
        return RedirectResponse(url="/doctor/pacientes", status_code=303)
    paciente["_id"] = str(paciente["_id"])
    perfil = await db["perfiles_pacientes"].find_one({"paciente_email": paciente["email"]})
    if perfil:
        perfil["_id"] = str(perfil["_id"])
    cursor_res = db["resultados_juegos"].find({"paciente_email": paciente["email"]}).sort("fecha", -1)
    resultados_raw = []
    async for doc in cursor_res:
        doc["_id"] = str(doc["_id"])
        resultados_raw.append(doc)
    stats_por_categoria = {}
    for r in resultados_raw:
        cat = r.get("categoria", "otro")
        if cat not in stats_por_categoria:
            stats_por_categoria[cat] = {"completados": 0, "en_progreso": 0, "total": 0}
        stats_por_categoria[cat]["total"] += 1
        if r.get("completado"):
            stats_por_categoria[cat]["completados"] += 1
        else:
            stats_por_categoria[cat]["en_progreso"] += 1
    cursor_hist = db["historial_actividades"].find({"paciente_email": paciente["email"]}).sort("fecha", -1).limit(10)
    historial = []
    async for doc in cursor_hist:
        doc["_id"] = str(doc["_id"])
        historial.append(doc)
    return templates.TemplateResponse("doctor/perfil_paciente.html", {
        "request": request, "titulo_pagina": f"Perfil de {paciente.get('nombre', paciente['email'])}",
        "paciente": paciente, "perfil": perfil, "resultados": resultados_raw[:10],
        "stats_por_categoria": stats_por_categoria, "historial": historial,
    })


@router.post("/pacientes/{paciente_id}/editar")
async def editar_paciente_doctor(paciente_id: str, nombre: str = Form(...), email: str = Form(...), db: AsyncIOMotorDatabase = Depends(get_db)):
    await db["usuarios"].update_one({"_id": ObjectId(paciente_id)}, {"$set": {"nombre": nombre, "email": email}})
    return RedirectResponse(url=f"/doctor/pacientes/{paciente_id}", status_code=303)


@router.get("/actividades", response_class=HTMLResponse)
async def vista_actividades_doctor(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    return templates.TemplateResponse("doctor/actividades.html", {
        "request": request, "titulo_pagina": "Juegos disponibles", "juegos_disponibles": JUEGOS_DISPONIBLES,
    })


@router.get("/asignaciones", response_class=HTMLResponse)
async def vista_asignaciones_doctor(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    cursor = db["asignaciones"].find({})
    asignaciones = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        asignaciones.append(doc)
    emails_asignados = {a["paciente_email"] for a in asignaciones}
    cursor_pac = db["usuarios"].find({"rol": "paciente"})
    sin_asignar = []
    async for doc in cursor_pac:
        doc["_id"] = str(doc["_id"])
        if doc["email"] not in emails_asignados:
            sin_asignar.append(doc)
    return templates.TemplateResponse("doctor/asignaciones.html", {
        "request": request, "titulo_pagina": "Asignaciones",
        "asignaciones": asignaciones, "sin_asignar": sin_asignar,
    })


@router.post("/asignaciones/{asignacion_id}/aceptar", response_class=RedirectResponse)
async def aceptar_asignacion(asignacion_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    await db["asignaciones"].update_one({"_id": ObjectId(asignacion_id)}, {"$set": {"estado": "aceptada"}})
    return RedirectResponse(url="/doctor/asignaciones", status_code=303)


@router.post("/asignaciones/{asignacion_id}/cancelar", response_class=RedirectResponse)
async def cancelar_asignacion(asignacion_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    await db["asignaciones"].update_one({"_id": ObjectId(asignacion_id)}, {"$set": {"estado": "cancelada"}})
    return RedirectResponse(url="/doctor/asignaciones", status_code=303)


@router.get("/historial", response_class=HTMLResponse)
async def vista_historial_doctor(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    cursor = db["historial_actividades"].find({}).sort("fecha", -1)
    historial = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        historial.append(doc)
    return templates.TemplateResponse("doctor/historial.html", {
        "request": request, "titulo_pagina": "Historial de actividades", "historial": historial,
    })


@router.get("/resultados", response_class=HTMLResponse)
async def vista_resultados_doctor(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    cursor = db["resultados_juegos"].find({}).sort("fecha", -1).limit(100)
    resultados = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        resultados.append(doc)
    return templates.TemplateResponse("doctor/resultados.html", {
        "request": request, "titulo_pagina": "Resultados de juegos", "resultados": resultados,
    })


@router.get("/evaluaciones-pendientes", response_class=HTMLResponse)
async def vista_evaluaciones_pendientes(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    cursor = db["historial_actividades"].find({"$or": [{"feedback": None}, {"feedback": ""}]}).sort("fecha", -1)
    evaluaciones = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        evaluaciones.append(doc)
    return templates.TemplateResponse("doctor/evaluaciones_pendientes.html", {
        "request": request, "titulo_pagina": "Evaluaciones Pendientes", "evaluaciones": evaluaciones,
    })


@router.post("/evaluaciones/{historial_id}/feedback")
async def guardar_feedback(historial_id: str, feedback: str = Form(...), db: AsyncIOMotorDatabase = Depends(get_db)):
    await db["historial_actividades"].update_one({"_id": ObjectId(historial_id)}, {"$set": {"feedback": feedback}})
    return RedirectResponse(url="/doctor/evaluaciones-pendientes", status_code=303)


@router.post("/estado", response_class=RedirectResponse)
async def cambiar_estado_doctor(
    request: Request,
    estado: str = Form(...),
    email: str = Form(""),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Cambia el estado del médico. Lee el email de la cookie si no viene en el form."""
    if not email:
        email = request.cookies.get("usuario_email", "doctor@tesis.com")
    await db["usuarios"].update_one({"email": email, "rol": "medico"}, {"$set": {"estado": estado}})
    return RedirectResponse(url="/doctor/home", status_code=303)
