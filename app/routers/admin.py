from datetime import datetime
from pathlib import Path
from random import choice

from bson import ObjectId
from fastapi import (
    APIRouter,
    Request,
    Depends,
    Form,
    HTTPException,
    status,
    File,
    UploadFile,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase

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

    # Conteo de médicos por estado
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


@router.get("/medicos", response_class=HTMLResponse)
async def listar_medicos_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    estado: str | None = None,
):
    """
    Lista de médicos con filtro por estado (activo/ocupado/consulta).
    Permite al admin ver quién está disponible u ocupado.
    """
    filtro: dict = {"rol": "medico"}
    if estado and estado != "todos":
        filtro["estado"] = estado

    cursor = db["usuarios"].find(filtro)
    medicos = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        medicos.append(doc)

    return templates.TemplateResponse(
        "admin/medicos.html",
        {
            "request": request,
            "titulo_pagina": "Médicos",
            "medicos": medicos,
            "estado_seleccionado": estado or "todos",
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
    Para produ, es mejor marcar 'estado' = inactivo.
    """
    await db["usuarios"].delete_one({"_id": ObjectId(paciente_id)})
    return RedirectResponse(url="/admin/pacientes", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/actividades", response_class=HTMLResponse)
async def vista_actividades_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Lista todas las categoras de actividades con sus actividades asociadas.
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
    Muestra el documento de 'contenido_admin' con imges, videos, audios, textos, instrucciones.
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


@router.post("/contenido")
async def actualizar_contenido_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    imagen: UploadFile | None = File(None),
    video: UploadFile | None = File(None),
):
    """
    Permite agregar nuevas imágenes o videos al documento 'contenido_admin'.

    Los archivos se guardan en la carpeta 'app/static/uploads' y en la BD se
    almacena la ruta relativa para poder utilizarlos desde el front.
    """
    # Buscar (o crear) el documento único de contenido_admin
    doc = await db["contenido_admin"].find_one({})
    if not doc:
        doc = {
            "imagenes": [],
            "videos": [],
            "audios_referencia": [],
            "textos_sistema": [],
            "instrucciones": None,
        }
        await db["contenido_admin"].insert_one(doc)
        doc = await db["contenido_admin"].find_one({})

    # Asegurar que existan las listas
    imagenes = doc.get("imagenes", [])
    videos = doc.get("videos", [])

    upload_dir = Path("app/static/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Guardar imagen si viene en el formulario
    if imagen is not None and imagen.filename:
        nombre_imagen = f"{datetime.utcnow().timestamp()}_{imagen.filename}"
        ruta_imagen_fs = upload_dir / nombre_imagen
        contenido_bytes = await imagen.read()
        ruta_imagen_fs.write_bytes(contenido_bytes)
        # Ruta pública que usará el front
        ruta_publica_imagen = f"/static/uploads/{nombre_imagen}"
        imagenes.append(ruta_publica_imagen)

    # Guardar video si viene en el formulario
    if video is not None and video.filename:
        nombre_video = f"{datetime.utcnow().timestamp()}_{video.filename}"
        ruta_video_fs = upload_dir / nombre_video
        contenido_bytes_video = await video.read()
        ruta_video_fs.write_bytes(contenido_bytes_video)
        ruta_publica_video = f"/static/uploads/{nombre_video}"
        videos.append(ruta_publica_video)

    await db["contenido_admin"].update_one(
        {"_id": doc["_id"]},
        {
            "$set": {
                "imagenes": imagenes,
                "videos": videos,
            }
        },
    )

    return RedirectResponse(
        url="/admin/contenido",
        status_code=status.HTTP_303_SEE_OTHER,
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


@router.post("/asignaciones/auto")
async def crear_asignacion_automatica(
    paciente_email: str = Form(...),
    dificultad: str = Form("media"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Crea una asignación automática para el paciente indicado,
    eligiendo un doctor cualquiera (aleatorio) de la colección 'usuarios'
    que **no** esté actualmente en consulta/ocupado.
    """
    # Obtener todos los médicos disponibles que NO estén ocupados/en consulta
    cursor_medicos = db["usuarios"].find(
        {
            "rol": "medico",
            "estado": {"$nin": ["ocupado", "consulta"]},
        }
    )
    medicos: list[dict] = []
    async for m in cursor_medicos:
        medicos.append(m)

    # Si no hay médicos, simplemente volvemos a la lista de pacientes
    if not medicos:
        return RedirectResponse(
            url="/admin/pacientes",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    medico_elegido = choice(medicos)
    medico_email = medico_elegido.get("email")

    nueva_asignacion = {
        "paciente_email": paciente_email,
        "medico_email": medico_email,
        "actividades_asignadas": [],  # Se deja vacío por ahora para mantener el flujo
        "dificultad": dificultad,
        "fecha_asignacion": datetime.utcnow(),
        "estado": "pendiente",
    }

    await db["asignaciones"].insert_one(nueva_asignacion)

    return RedirectResponse(
        url="/admin/asignaciones",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/historial", response_class=HTMLResponse)
async def vista_historial_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Historial de actividades realizadas por pacientes.
    Colec: 'historial_actividades'.
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
