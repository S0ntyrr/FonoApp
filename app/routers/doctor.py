from bson import ObjectId
from datetime import datetime

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette import status

from ..database import get_db
from ..models import ActividadCategoria, Asignacion, HistorialActividad

router = APIRouter(prefix="/doctor", tags=["doctor-web"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/home", response_class=HTMLResponse)
async def home_doctor(
    request: Request,
):
    """
    Home de inicio del doctor con accesos a sus secciones.
    """
    return templates.TemplateResponse(
        "doctor/home.html",
        {
            "request": request,
            "titulo_pagina": "Panel del doctor",
        },
    )


@router.get("/pacientes", response_class=HTMLResponse)
async def vista_pacientes_doctor(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Vista para el doctor donde ve la lista de pacientes.
    """
    cursor = db["usuarios"].find({"rol": "paciente"})
    pacientes = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        pacientes.append(doc)

    return templates.TemplateResponse(
        "doctor/pacientes.html",
        {
            "request": request,
            "titulo_pagina": "Pacientes - Doctor",
            "pacientes": pacientes,
        },
    )


@router.get("/actividades", response_class=HTMLResponse)
async def vista_actividades_doctor(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    El doctor ve las catg de actividades y su contenido
    """
    cursor = db["actividades"].find({})
    categorias: list[ActividadCategoria] = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        categorias.append(ActividadCategoria(**doc))

    return templates.TemplateResponse(
        "doctor/actividades.html",
        {
            "request": request,
            "titulo_pagina": "Actividades disponibles",
            "categorias": categorias,
        },
    )


@router.get("/asignaciones", response_class=HTMLResponse)
async def vista_asignaciones_doctor(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    El doctor ve todas las asignaciones.
    (En el futuro se puede filtrar por medico_email).
    """
    cursor = db["asignaciones"].find({})
    asignaciones: list[Asignacion] = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        asignaciones.append(Asignacion(**doc))

    return templates.TemplateResponse(
        "doctor/asignaciones.html",
        {
            "request": request,
            "titulo_pagina": "Mis asignaciones",
            "asignaciones": asignaciones,
        },
    )


@router.post("/asignaciones/{asignacion_id}/aceptar")
async def aceptar_asignacion_doctor(
    asignacion_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    El doctor acepta la asig (estado -> 'aceptada').
    """
    await db["asignaciones"].update_one(
        {"_id": ObjectId(asignacion_id)},
        {"$set": {"estado": "aceptada"}},
    )
    return RedirectResponse(
        url="/doctor/asignaciones",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/asignaciones/{asignacion_id}/cancelar")
async def cancelar_asignacion_doctor(
    asignacion_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    El doctor cancela/rechaza la solicitud/asig (estado -> 'cancelada').
    """
    await db["asignaciones"].update_one(
        {"_id": ObjectId(asignacion_id)},
        {"$set": {"estado": "cancelada"}},
    )
    return RedirectResponse(
        url="/doctor/asignaciones",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/historial", response_class=HTMLResponse)
async def vista_historial_doctor(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    El doctor ve el historial de actividades realizado por los pacientes.
    """
    cursor = db["historial_actividades"].find({}).sort("fecha", -1)
    historial: list[HistorialActividad] = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        historial.append(HistorialActividad(**doc))

    return templates.TemplateResponse(
        "doctor/historial.html",
        {
            "request": request,
            "titulo_pagina": "Historial de pacientes",
            "historial": historial,
        },
    )

