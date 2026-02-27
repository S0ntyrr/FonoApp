from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette import status
from bson import ObjectId

from ..database import get_db
from ..models import ActividadCategoria, Asignacion, HistorialActividad

router = APIRouter(prefix="/doctor", tags=["doctor-web"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/home", response_class=HTMLResponse)
async def home_doctor(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Página de inicio del doctor con accesos rápidos a sus secciones.
    """
    # Obtener estado actual del doctor
    email_doctor = "doctor@tesis.com"
    doctor_doc = await db["usuarios"].find_one({"email": email_doctor})
    estado_actual = doctor_doc.get("estado", "activo") if doctor_doc else "activo"

    return templates.TemplateResponse(
        "doctor/home.html",
        {
            "request": request,
            "titulo_pagina": "Panel del doctor",
            "estado_actual": estado_actual,
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
    El doctor ve las categorías de actividades y su contenido
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


@router.post("/asignaciones/{asignacion_id}/aceptar", response_class=RedirectResponse)
async def aceptar_asignacion(
    asignacion_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Acepta una asignación cambiando su estado a 'aceptada'.
    Redirige al panel de pacientes para acceder a las actividades.
    """
    result = await db["asignaciones"].update_one(
        {"_id": ObjectId(asignacion_id)},
        {"$set": {"estado": "aceptada"}}
    )
    if result.modified_count == 0:
        # Manejar error, pero por simplicidad, redirigir igual
        pass
    return RedirectResponse(url="/doctor/pacientes", status_code=303)


@router.post("/asignaciones/{asignacion_id}/cancelar", response_class=RedirectResponse)
async def cancelar_asignacion(
    asignacion_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Cancela una asignación cambiando su estado a 'cancelada'.
    """
    result = await db["asignaciones"].update_one(
        {"_id": ObjectId(asignacion_id)},
        {"$set": {"estado": "cancelada"}}
    )
    if result.modified_count == 0:
        # Manejar error
        pass
    return RedirectResponse(url="/doctor/asignaciones", status_code=303)


@router.get("/historial", response_class=HTMLResponse)
async def vista_historial_doctor(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    El doctor ve el historial de actividades realizadas por los pacientes.
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


@router.get("/resultados", response_class=HTMLResponse)
async def vista_resultados_doctor(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    El doctor ve los resultados de juegos de todos los pacientes.
    """
    cursor = db["resultados_juegos"].find({}).sort("fecha", -1).limit(100)
    resultados = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        resultados.append(doc)

    return templates.TemplateResponse(
        "doctor/resultados.html",
        {
            "request": request,
            "titulo_pagina": "Resultados de juegos",
            "resultados": resultados,
        },
    )


@router.get("/evaluaciones-pendientes", response_class=HTMLResponse)
async def vista_evaluaciones_pendientes(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    El doctor ve las actividades del historial que aún no tienen feedback (evaluaciones pendientes).
    """
    cursor = db["historial_actividades"].find({"feedback": None}).sort("fecha", -1)
    evaluaciones: list[HistorialActividad] = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        evaluaciones.append(HistorialActividad(**doc))

    return templates.TemplateResponse(
        "doctor/evaluaciones_pendientes.html",
        {
            "request": request,
            "titulo_pagina": "Evaluaciones Pendientes",
            "evaluaciones": evaluaciones,
        },
    )


@router.post("/estado", response_class=RedirectResponse)
async def cambiar_estado_doctor(
    estado: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Cambia el estado del doctor (activo, ocupado, consulta).
    """
    # En el futuro, este email vendrá del usuario logueado
    email_doctor = "doctor@tesis.com"
    
    result = await db["usuarios"].update_one(
        {"email": email_doctor},
        {"$set": {"estado": estado}}
    )
    if result.modified_count == 0:
        # Manejar error
        pass
    return RedirectResponse(url="/doctor/home", status_code=303)
