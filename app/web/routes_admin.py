from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from bson import ObjectId

from ..database import get_db
from ..models import ActividadCategoria, ContenidoAdmin, Asignacion, HistorialActividad

router = APIRouter(prefix="/admin", tags=["admin-web"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def vista_dashboard_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Dashboard del administrador: muestra un resumen de usuarios/pacientes.
    """
    usuarios_total = await db["usuarios"].count_documents({})
    pacientes_total = await db["usuarios"].count_documents({"rol": "paciente"})
    medicos_total = await db["usuarios"].count_documents({"rol": "medico"})
    medicos_activos = await db["usuarios"].count_documents({"rol": "medico", "estado": "activo"})
    medicos_ocupados = await db["usuarios"].count_documents({"rol": "medico", "estado": "ocupado"})
    medicos_consulta = await db["usuarios"].count_documents({"rol": "medico", "estado": "consulta"})

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "titulo_pagina": "Panel de administración",
            "usuarios_total": usuarios_total,
            "pacientes_total": pacientes_total,
            "medicos_total": medicos_total,
            "medicos_activos": medicos_activos,
            "medicos_ocupados": medicos_ocupados,
            "medicos_consulta": medicos_consulta,
        },
    )


@router.get("/pacientes", response_class=HTMLResponse)
async def listar_pacientes_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Lista de pacientes para que el admin pueda gestionar el (CRUD).
    """
    cursor = db["usuarios"].find({"rol": "paciente"})
    pacientes = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        pacientes.append(doc)

    return templates.TemplateResponse(
        "admin/pacientes.html",
        {
            "request": request,
            "titulo_pagina": "Pacientes",
            "pacientes": pacientes,
        },
    )


@router.post("/pacientes/crear")
async def crear_paciente_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    """
    Crea un nuevo paciente desde el panel admin.
    """
    existente = await db["usuarios"].find_one({"email": email})
    if existente:
        # Podríamos mostrar mensaje de error, pero para simplificar, redirigimos.
        return RedirectResponse(url="/admin/pacientes", status_code=status.HTTP_303_SEE_OTHER)

    nuevo_paciente = {
        "nombre": nombre,
        "email": email,
        "password": password,
        "rol": "paciente",
        "nivel": 1,
        "puntos": 0,
        "estado": "activo",
    }
    await db["usuarios"].insert_one(nuevo_paciente)

    return RedirectResponse(url="/admin/pacientes", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/pacientes/{paciente_id}/eliminar")
async def eliminar_paciente_admin(
    paciente_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Elimina (o desactiva) un paciente.
    Para producción, es mejor marcar 'estado' = inactivo.
    """
    from bson import ObjectId

    await db["usuarios"].delete_one({"_id": ObjectId(paciente_id)})
    return RedirectResponse(url="/admin/pacientes", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/medicos", response_class=HTMLResponse)
async def listar_medicos_admin(
    request: Request,
    estado: str = "todos",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Lista de médicos para que el admin pueda gestionar.
    """
    query = {"rol": "medico"}
    if estado != "todos":
        query["estado"] = estado

    cursor = db["usuarios"].find(query)
    medicos = []
    async for doc in cursor:
        doc["tiempo_servicio"] = (datetime.now(timezone.utc) - doc["_id"].generation_time).days
        doc["_id"] = str(doc["_id"])
        medicos.append(doc)

    return templates.TemplateResponse(
        "admin/medicos.html",
        {
            "request": request,
            "titulo_pagina": "Médicos",
            "medicos": medicos,
            "estado_seleccionado": estado,
        },
    )


@router.post("/medicos/crear")
async def crear_medico_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    """
    Crea un nuevo médico desde el panel admin.
    """
    existente = await db["usuarios"].find_one({"email": email})
    if existente:
        return RedirectResponse(url="/admin/medicos", status_code=status.HTTP_303_SEE_OTHER)

    nuevo_medico = {
        "nombre": nombre,
        "email": email,
        "password": password,
        "rol": "medico",
        "nivel": 1,
        "puntos": 0,
        "estado": "activo",
    }
    await db["usuarios"].insert_one(nuevo_medico)

    return RedirectResponse(url="/admin/medicos", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/medicos/{medico_id}/eliminar")
async def eliminar_medico_admin(
    medico_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Elimina un médico.
    """
    await db["usuarios"].delete_one({"_id": ObjectId(medico_id)})
    return RedirectResponse(url="/admin/medicos", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/medicos/{medico_id}/cambiar_estado")
async def cambiar_estado_medico_admin(
    medico_id: str,
    estado: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Cambia el estado de un médico.
    """
    await db["usuarios"].update_one({"_id": ObjectId(medico_id)}, {"$set": {"estado": estado}})
    return RedirectResponse(url="/admin/medicos", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/medicos/{medico_id}/editar", response_class=HTMLResponse)
async def editar_medico_form_admin(
    medico_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Muestra el form para editar un médico.
    """
    doc = await db["usuarios"].find_one({"_id": ObjectId(medico_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Médico no encontrado")
    doc["_id"] = str(doc["_id"])
    return templates.TemplateResponse(
        "admin/editar_medico.html",
        {
            "request": request,
            "titulo_pagina": "Editar Médico",
            "medico": doc,
        },
    )


@router.post("/medicos/{medico_id}/editar")
async def editar_medico_admin(
    medico_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    """
    Edita un médico.
    """
    update_data = {
        "nombre": nombre,
        "email": email,
    }
    if password:
        update_data["password"] = password
    await db["usuarios"].update_one({"_id": ObjectId(medico_id)}, {"$set": update_data})
    return RedirectResponse(url="/admin/medicos", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/medicos/{medico_id}/consultas", response_class=HTMLResponse)
async def ver_consultas_medico_admin(
    medico_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Muestra las consultas (asignaciones) de un médico.
    """
    medico = await db["usuarios"].find_one({"_id": ObjectId(medico_id)})
    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado")
    cursor = db["asignaciones"].find({"medico_email": medico["email"]})
    asignaciones = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        asignaciones.append(doc)
    return templates.TemplateResponse(
        "admin/consultas_medico.html",
        {
            "request": request,
            "titulo_pagina": f"Consultas de {medico['nombre']}",
            "asignaciones": asignaciones,
        },
    )


@router.get("/actividades", response_class=HTMLResponse)
async def vista_actividades_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Lista todas las categorías de actividades con sus actividades asociadas.
    Usa la colección 'actividades'.
    """
    cursor = db["actividades"].find({})
    categorias: list[ActividadCategoria] = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        categorias.append(ActividadCategoria(**doc))

    return templates.TemplateResponse(
        "admin/actividades.html",
        {
            "request": request,
            "titulo_pagina": "Actividades por categoría",
            "categorias": categorias,
        },
    )


@router.get("/contenido", response_class=HTMLResponse)
async def vista_contenido_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Muestra el documento de 'contenido_admin' con imágenes, videos, audios, textos, instrucciones.
    Asumimos que solo hay un documento.
    """
    doc = await db["contenido_admin"].find_one({})
    contenido = None
    if doc:
        doc["_id"] = str(doc["_id"])
        contenido = ContenidoAdmin(**doc)

    return templates.TemplateResponse(
        "admin/contenido.html",
        {
            "request": request,
            "titulo_pagina": "Contenido del sistema",
            "contenido": contenido,
        },
    )


@router.get("/asignaciones", response_class=HTMLResponse)
async def vista_asignaciones_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Lista todas las asignaciones realizadas (vista global para admin).
    Colección: 'asignaciones'.
    """
    cursor = db["asignaciones"].find({})
    asignaciones: list[Asignacion] = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        asignaciones.append(Asignacion(**doc))

    return templates.TemplateResponse(
        "admin/asignaciones.html",
        {
            "request": request,
            "titulo_pagina": "Asignaciones",
            "asignaciones": asignaciones,
        },
    )


@router.get("/historial", response_class=HTMLResponse)
async def vista_historial_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Historial de actividades realizadas por pacientes.
    Colección: 'historial_actividades'.
    """
    cursor = db["historial_actividades"].find({}).sort("fecha", -1)
    historial: list[HistorialActividad] = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        historial.append(HistorialActividad(**doc))

    return templates.TemplateResponse(
        "admin/historial.html",
        {
            "request": request,
            "titulo_pagina": "Historial de actividades",
            "historial": historial,
        },
    )


@router.get("/resultados", response_class=HTMLResponse)
async def vista_resultados_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Admin ve todos los resultados de juegos con filtros.
    """
    cursor = db["resultados_juegos"].find({}).sort("fecha", -1).limit(200)
    resultados = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        resultados.append(doc)

    return templates.TemplateResponse(
        "admin/resultados.html",
        {
            "request": request,
            "titulo_pagina": "Resultados de juegos",
            "resultados": resultados,
        },
    )
