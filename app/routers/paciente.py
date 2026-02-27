from datetime import datetime
from collections import defaultdict

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database import get_db
from ..models import PerfilPaciente, SesionApp

router = APIRouter(prefix="/paciente", tags=["paciente-app"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/perfil", response_class=HTMLResponse)
async def vista_perfil_paciente(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    # En el futuro esto vendrá del usuario logueado.
    email: str = "paciente@tesis.com",
):
    """
    Muestra el perfil del paciente y un calendario simple con días conectados.
    Usa:
    - perfiles_pacientes: datos de perfil
    - sesiones_app: minutos conectados por día
    """
    perfil_doc = await db["perfiles_pacientes"].find_one({"paciente_email": email})
    perfil: PerfilPaciente | None = None
    if perfil_doc:
        perfil_doc["_id"] = str(perfil_doc["_id"])
        perfil = PerfilPaciente(**perfil_doc)

    # Traer sesiones del último mes (por ejemplo)
    hoy = datetime.utcnow()
    cursor = db["sesiones_app"].find(
        {
            "paciente_email": email,
            "fecha": {
                "$gte": datetime(hoy.year, hoy.month, 1),
            },
        }
    )

    sesiones_por_dia: dict[str, int] = defaultdict(int)
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        sesion = SesionApp(**doc)
        dia_str = sesion.fecha.strftime("%Y-%m-%d")
        sesiones_por_dia[dia_str] += sesion.minutos_conectado

    # Traer actividades disponibles para mostrar en la app móvil
    categorias_cursor = db["actividades"].find({})
    actividades_disponibles: list[dict] = []
    async for doc in categorias_cursor:
        # normalizar id y estructura sencilla para la plantilla
        doc["_id"] = str(doc["_id"])
        categoria = doc.get("categoria")
        actividades = doc.get("actividades", [])
        actividades_disponibles.append({"categoria": categoria, "actividades": actividades})

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
    # En el futuro, este email vendrá del usuario logueado
    paciente_email: str = Form(...),
    nombre: str = Form(...),
    edad: int = Form(...),
    escolaridad: str = Form(...),
    genero: str = Form(...),
    tutor: str = Form(...),
    parentesco: str = Form(...),
):
    """
    Crea o actualiza el perfil del paciente en la colección 'perfiles_pacientes'.
    Si ya existe un perfil para ese email, se actualiza.
    """
    # Buscar si ya existe perfil
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
        # Mantener la fecha_registro original
        datos["fecha_registro"] = existente.get("fecha_registro", datetime.utcnow())
        await db["perfiles_pacientes"].update_one(
            {"_id": existente["_id"]},
            {"$set": datos},
        )
    else:
        # Nuevo perfil: poner fecha_registro ahora
        datos["fecha_registro"] = datetime.utcnow()
        await db["perfiles_pacientes"].insert_one(datos)

    # Volver a la vista de perfil
    return RedirectResponse(url=f"/paciente/perfil?email={paciente_email}", status_code=303)
