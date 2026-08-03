"""
FonoApp - Router del Administrador
====================================
Panel de administración con acceso completo al sistema.

Rutas principales:
  GET  /admin/dashboard              → Dashboard con estadísticas
  
  Gestión de pacientes:
  GET  /admin/pacientes              → Listar pacientes con stats
  POST /admin/pacientes/crear        → Crear nuevo paciente
  POST /admin/pacientes/{id}/eliminar → Eliminar paciente
  
  Gestión de médicos:
  GET  /admin/medicos                → Listar médicos con filtros
  POST /admin/medicos/crear          → Crear nuevo médico
  POST /admin/medicos/{id}/eliminar  → Eliminar médico
  POST /admin/medicos/{id}/cambiar_estado → Cambiar estado del médico
  GET  /admin/medicos/{id}/editar    → Formulario de edición
  POST /admin/medicos/{id}/editar    → Guardar edición
  GET  /admin/medicos/{id}/consultas → Ver asignaciones del médico
  
  Asignaciones:
  GET  /admin/asignaciones           → Ver todas las asignaciones
  POST /admin/asignaciones/auto      → Crear asignación automática (médico al azar)
  POST /admin/asignaciones/manual    → Crear asignación manual (médico específico)
  POST /admin/asignaciones/{id}/eliminar → Eliminar asignación
  
  Contenido y reportes:
  GET  /admin/actividades            → Ver juegos del sistema con stats
  GET  /admin/contenido              → Gestionar contenido multimedia
  POST /admin/contenido/texto        → Agregar texto/instrucción
  POST /admin/contenido/texto/{idx}/eliminar → Eliminar texto
  POST /admin/contenido/media        → Subir imagen o video
  POST /admin/contenido/media/eliminar → Eliminar imagen o video
  GET  /admin/historial              → Historial de actividades con stats
  GET  /admin/resultados             → Resultados de juegos con estadísticas

Colecciones MongoDB usadas:
  - usuarios: pacientes y médicos
  - asignaciones: asignaciones médico-paciente
  - actividades: catálogo de juegos
  - historial_actividades: actividades completadas
  - resultados_juegos: resultados detallados de juegos
  - contenido_admin: textos, imágenes y videos
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException, status, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import os
from pathlib import Path
from random import choice
from uuid import uuid4
from bson import ObjectId
from bson.errors import InvalidId
from collections import defaultdict

from ..database import get_db
from ..models import ContenidoAdmin, HistorialActividad
from ..security import hash_password, require_role

router = APIRouter(
    prefix="/admin",
    tags=["admin-web"],
    dependencies=[Depends(require_role(["admin"]))],
)

templates = Jinja2Templates(directory="app/templates")

# Juegos disponibles en el sistema
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
        {"nombre": "Completa la palabra", "url": "/juegos/articulacion/completa-palabra"},
        {"nombre": "¡Acelera la moto!", "url": "/juegos/articulacion/moto-voz"},
    ]},
    {"categoria": "Prosodia", "juegos": [
        {"nombre": "Adivina el animal", "url": "/juegos/prosodia/adivina-animal"},
        {"nombre": "Trabalenguas", "url": "/juegos/prosodia/trabalenguas"},
        {"nombre": "Relaciona la adivinanza", "url": "/juegos/prosodia/adivinanza-imagen"},
        {"nombre": "Completa la canción", "url": "/juegos/prosodia/completa-cancion"},
    ]},
    {"categoria": "Discriminación Auditiva", "juegos": [
        {"nombre": "Sonidos de animales", "url": "/juegos/discriminacion/sonidos-animales"},
        {"nombre": "Sonidos de objetos", "url": "/juegos/discriminacion/sonidos-objetos"},
        {"nombre": "Arrastra al sonido", "url": "/juegos/discriminacion/arrastra-sonido"},
    ]},
    {"categoria": "Practica Conmigo", "juegos": [
        {"nombre": "Rompecabezas", "url": "/juegos/practica/rompecabezas"},
        {"nombre": "Crea tu personaje", "url": "/juegos/practica/cara"},
        {"nombre": "Asociación de imágenes", "url": "/juegos/practica/asociacion"},
    ]},
]


def _parse_object_id(value: str) -> ObjectId | None:
    try:
        return ObjectId(value)
    except InvalidId:
        return None


def _actividades_por_dificultad(dificultad: str) -> list[dict]:
    cantidad = {"facil": 3, "media": 4, "dificil": 6}.get((dificultad or "").lower(), 4)
    catalogo = []
    for categoria in JUEGOS_DISPONIBLES:
        for juego in categoria["juegos"]:
            catalogo.append({
                "categoria": categoria["categoria"],
                "actividad": juego["nombre"],
            })
    return catalogo[:cantidad]


def _guardar_upload_seguro(
    archivo: UploadFile,
    upload_dir: Path,
    prefijo: str,
    extensiones_permitidas: set[str],
    max_bytes: int,
) -> str:
    extension = Path(archivo.filename or "").suffix.lower()
    if extension not in extensiones_permitidas:
        raise HTTPException(status_code=400, detail="Tipo de archivo no permitido")

    contenido = archivo.file.read(max_bytes + 1)
    if len(contenido) > max_bytes:
        raise HTTPException(status_code=413, detail="Archivo demasiado grande")

    nombre_archivo = f"{prefijo}_{uuid4().hex}{extension}"
    ruta_archivo = upload_dir / nombre_archivo
    with ruta_archivo.open("wb") as destino:
        destino.write(contenido)

    return f"/static/uploads/{nombre_archivo}"


@router.get("/dashboard", response_class=HTMLResponse)
async def vista_dashboard_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    usuarios_total = await db["usuarios"].count_documents({})
    pacientes_total = await db["usuarios"].count_documents({"rol": "paciente"})
    medicos_total = await db["usuarios"].count_documents({"rol": "medico"})
    medicos_activos = await db["usuarios"].count_documents({"rol": "medico", "estado": "activo"})
    medicos_ocupados = await db["usuarios"].count_documents({"rol": "medico", "estado": "ocupado"})
    medicos_consulta = await db["usuarios"].count_documents({"rol": "medico", "estado": "consulta"})
    total_juegos = await db["resultados_juegos"].count_documents({})
    asignaciones_pendientes = await db["asignaciones"].count_documents({"estado": "pendiente"})

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
            "total_juegos": total_juegos,
            "asignaciones_pendientes": asignaciones_pendientes,
        },
    )


@router.get("/pacientes", response_class=HTMLResponse)
async def listar_pacientes_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    cursor = db["usuarios"].find({"rol": "paciente"})
    pacientes = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        # Contar juegos del paciente
        total_j = await db["resultados_juegos"].count_documents({"paciente_email": doc["email"]})
        completados_j = await db["resultados_juegos"].count_documents({"paciente_email": doc["email"], "completado": True})
        # Ver si tiene asignación
        asig = await db["asignaciones"].find_one({"paciente_email": doc["email"]})
        doc["total_juegos"] = total_j
        doc["juegos_completados"] = completados_j
        doc["tiene_asignacion"] = asig is not None
        doc["estado_asignacion"] = asig.get("estado", "pendiente") if asig else None
        pacientes.append(doc)

    # Médicos disponibles para asignación manual
    cursor_med = db["usuarios"].find({"rol": "medico", "estado": {"$nin": ["ocupado", "consulta"]}})
    medicos_disponibles = []
    async for m in cursor_med:
        m["_id"] = str(m["_id"])
        medicos_disponibles.append(m)

    return templates.TemplateResponse(
        "admin/pacientes.html",
        {
            "request": request,
            "titulo_pagina": "Gestión de Pacientes",
            "pacientes": pacientes,
            "medicos_disponibles": medicos_disponibles,
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
    existente = await db["usuarios"].find_one({"email": email})
    if existente:
        return RedirectResponse(url="/admin/pacientes?error=email_existe", status_code=status.HTTP_303_SEE_OTHER)

    nuevo_paciente = {
        "nombre": nombre,
        "email": email,
        "password": hash_password(password),
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
    object_id = _parse_object_id(paciente_id)
    if not object_id:
        return RedirectResponse(url="/admin/pacientes?error=id_invalido", status_code=status.HTTP_303_SEE_OTHER)

    paciente = await db["usuarios"].find_one({"_id": object_id, "rol": "paciente"})
    if not paciente:
        return RedirectResponse(url="/admin/pacientes?error=no_encontrado", status_code=status.HTTP_303_SEE_OTHER)

    paciente_email = paciente.get("email")
    await db["usuarios"].delete_one({"_id": object_id})
    if paciente_email:
        await db["perfiles_pacientes"].delete_many({"paciente_email": paciente_email})
        await db["asignaciones"].delete_many({"paciente_email": paciente_email})
        await db["resultados_juegos"].delete_many({"paciente_email": paciente_email})
        await db["historial_actividades"].delete_many({"paciente_email": paciente_email})
        await db["sesiones_app"].delete_many({"paciente_email": paciente_email})
    return RedirectResponse(url="/admin/pacientes", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/medicos", response_class=HTMLResponse)
async def listar_medicos_admin(
    request: Request,
    estado: str = "todos",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    query = {"rol": "medico"}
    if estado != "todos":
        query["estado"] = estado

    cursor = db["usuarios"].find(query)
    medicos = []
    async for doc in cursor:
        doc["tiempo_servicio"] = (datetime.now(timezone.utc) - doc["_id"].generation_time).days
        doc["_id"] = str(doc["_id"])
        # Contar pacientes asignados
        total_asig = await db["asignaciones"].count_documents({"medico_email": doc["email"]})
        doc["total_asignaciones"] = total_asig
        medicos.append(doc)

    return templates.TemplateResponse(
        "admin/medicos.html",
        {
            "request": request,
            "titulo_pagina": "Gestión de Médicos",
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
    existente = await db["usuarios"].find_one({"email": email})
    if existente:
        return RedirectResponse(url="/admin/medicos?error=email_existe", status_code=status.HTTP_303_SEE_OTHER)

    nuevo_medico = {
        "nombre": nombre,
        "email": email,
        "password": hash_password(password),
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
    object_id = _parse_object_id(medico_id)
    if not object_id:
        return RedirectResponse(url="/admin/medicos?error=id_invalido", status_code=status.HTTP_303_SEE_OTHER)
    await db["usuarios"].delete_one({"_id": object_id})
    return RedirectResponse(url="/admin/medicos", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/medicos/{medico_id}/cambiar_estado")
async def cambiar_estado_medico_admin(
    medico_id: str,
    estado: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    object_id = _parse_object_id(medico_id)
    if not object_id:
        return RedirectResponse(url="/admin/medicos?error=id_invalido", status_code=status.HTTP_303_SEE_OTHER)
    await db["usuarios"].update_one({"_id": object_id}, {"$set": {"estado": estado}})
    return RedirectResponse(url="/admin/medicos", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/medicos/{medico_id}/editar", response_class=HTMLResponse)
async def editar_medico_form_admin(
    medico_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    object_id = _parse_object_id(medico_id)
    if not object_id:
        raise HTTPException(status_code=400, detail="ID de médico inválido")
    doc = await db["usuarios"].find_one({"_id": object_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Médico no encontrado")
    doc["_id"] = str(doc["_id"])
    return templates.TemplateResponse(
        "admin/editar_medico.html",
        {"request": request, "titulo_pagina": "Editar Médico", "medico": doc},
    )


@router.post("/medicos/{medico_id}/editar")
async def editar_medico_admin(
    medico_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(""),
):
    update_data = {"nombre": nombre, "email": email}
    if password:
        update_data["password"] = hash_password(password)
    object_id = _parse_object_id(medico_id)
    if not object_id:
        return RedirectResponse(url="/admin/medicos?error=id_invalido", status_code=status.HTTP_303_SEE_OTHER)
    await db["usuarios"].update_one({"_id": object_id}, {"$set": update_data})
    return RedirectResponse(url="/admin/medicos", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/medicos/{medico_id}/consultas", response_class=HTMLResponse)
async def ver_consultas_medico_admin(
    medico_id: str,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    object_id = _parse_object_id(medico_id)
    if not object_id:
        raise HTTPException(status_code=400, detail="ID de médico inválido")
    medico = await db["usuarios"].find_one({"_id": object_id})
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
            "medico": medico,
        },
    )


@router.get("/actividades", response_class=HTMLResponse)
async def vista_actividades_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Muestra los juegos fonoaudiológicos disponibles en el sistema.
    """
    # Estadísticas de uso por juego
    stats_juegos = {}
    cursor_res = db["resultados_juegos"].find({})
    async for doc in cursor_res:
        key = f"{doc.get('categoria','')}/{doc.get('juego','')}"
        if key not in stats_juegos:
            stats_juegos[key] = {"total": 0, "completados": 0}
        stats_juegos[key]["total"] += 1
        if doc.get("completado"):
            stats_juegos[key]["completados"] += 1

    return templates.TemplateResponse(
        "admin/actividades.html",
        {
            "request": request,
            "titulo_pagina": "Juegos del sistema",
            "juegos_disponibles": JUEGOS_DISPONIBLES,
            "stats_juegos": stats_juegos,
        },
    )


@router.get("/contenido", response_class=HTMLResponse)
async def vista_contenido_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = await db["contenido_admin"].find_one({})
    contenido = None
    if doc:
        doc["_id"] = str(doc["_id"])
        contenido = doc  # usar dict directamente para más flexibilidad

    return templates.TemplateResponse(
        "admin/contenido.html",
        {
            "request": request,
            "titulo_pagina": "Contenido del sistema",
            "contenido": contenido,
            "juegos_disponibles": JUEGOS_DISPONIBLES,
        },
    )


@router.post("/contenido/texto")
async def agregar_texto_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    texto: str = Form(...),
    tipo: str = Form("instruccion"),  # instruccion, aviso, regla
):
    """Agrega un texto/instrucción al sistema."""
    doc = await db["contenido_admin"].find_one({})
    if not doc:
        doc = {"imagenes": [], "videos": [], "audios_referencia": [], "textos_sistema": [], "instrucciones": None}
        await db["contenido_admin"].insert_one(doc)
        doc = await db["contenido_admin"].find_one({})

    entrada = {"texto": texto, "tipo": tipo, "fecha": datetime.utcnow().isoformat()}
    await db["contenido_admin"].update_one(
        {"_id": doc["_id"]},
        {"$push": {"textos_sistema": entrada}}
    )
    return RedirectResponse(url="/admin/contenido", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/contenido/texto/{idx}/eliminar")
async def eliminar_texto_admin(
    idx: int,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Elimina un texto por índice."""
    doc = await db["contenido_admin"].find_one({})
    if doc:
        textos = doc.get("textos_sistema", [])
        if 0 <= idx < len(textos):
            textos.pop(idx)
            await db["contenido_admin"].update_one(
                {"_id": doc["_id"]},
                {"$set": {"textos_sistema": textos}}
            )
    return RedirectResponse(url="/admin/contenido", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/contenido/media")
async def subir_media_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    imagen: UploadFile | None = File(None),
    video: UploadFile | None = File(None),
):
    """Sube imagen o video al sistema."""
    doc = await db["contenido_admin"].find_one({})
    if not doc:
        doc = {"imagenes": [], "videos": [], "audios_referencia": [], "textos_sistema": [], "instrucciones": None}
        await db["contenido_admin"].insert_one(doc)
        doc = await db["contenido_admin"].find_one({})

    imagenes = doc.get("imagenes", [])
    videos = doc.get("videos", [])

    upload_dir = Path("app/static/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    max_imagen_bytes = 5 * 1024 * 1024
    max_video_bytes = 30 * 1024 * 1024
    allowed_images = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    allowed_videos = {".mp4", ".webm", ".mov"}

    if imagen and imagen.filename:
        url_imagen = _guardar_upload_seguro(imagen, upload_dir, "img", allowed_images, max_imagen_bytes)
        imagenes.append(url_imagen)

    if video and video.filename:
        url_video = _guardar_upload_seguro(video, upload_dir, "vid", allowed_videos, max_video_bytes)
        videos.append(url_video)

    await db["contenido_admin"].update_one(
        {"_id": doc["_id"]},
        {"$set": {"imagenes": imagenes, "videos": videos}}
    )
    return RedirectResponse(url="/admin/contenido", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/contenido/media/eliminar")
async def eliminar_media_admin(
    tipo: str = Form(...),  # "imagen" o "video"
    url: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Elimina una imagen o video del sistema."""
    doc = await db["contenido_admin"].find_one({})
    if doc:
        if tipo == "imagen":
            imagenes = [i for i in doc.get("imagenes", []) if i != url]
            await db["contenido_admin"].update_one({"_id": doc["_id"]}, {"$set": {"imagenes": imagenes}})
            if url.startswith("/static/uploads/"):
                ruta = Path("app") / url.lstrip("/")
                if ruta.exists():
                    os.remove(ruta)
        elif tipo == "video":
            videos = [v for v in doc.get("videos", []) if v != url]
            await db["contenido_admin"].update_one({"_id": doc["_id"]}, {"$set": {"videos": videos}})
            if url.startswith("/static/uploads/"):
                ruta = Path("app") / url.lstrip("/")
                if ruta.exists():
                    os.remove(ruta)
    return RedirectResponse(url="/admin/contenido", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/asignaciones", response_class=HTMLResponse)
async def vista_asignaciones_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    cursor = db["asignaciones"].find({}).sort("fecha_asignacion", -1)
    asignaciones = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        asignaciones.append(doc)

    # Pacientes sin asignación
    emails_asignados = {a["paciente_email"] for a in asignaciones}
    cursor_pac = db["usuarios"].find({"rol": "paciente"})
    sin_asignar = []
    async for doc in cursor_pac:
        doc["_id"] = str(doc["_id"])
        if doc["email"] not in emails_asignados:
            sin_asignar.append(doc)

    # Médicos disponibles
    cursor_med = db["usuarios"].find({"rol": "medico", "estado": {"$nin": ["ocupado", "consulta"]}})
    medicos_disponibles = []
    async for m in cursor_med:
        m["_id"] = str(m["_id"])
        medicos_disponibles.append(m)

    # Estadísticas
    stats = {
        "total": len(asignaciones),
        "pendientes": sum(1 for a in asignaciones if (a.get("estado") or "pendiente") == "pendiente"),
        "aceptadas": sum(1 for a in asignaciones if a.get("estado") == "aceptada"),
        "canceladas": sum(1 for a in asignaciones if a.get("estado") == "cancelada"),
    }

    return templates.TemplateResponse(
        "admin/asignaciones.html",
        {
            "request": request,
            "titulo_pagina": "Asignaciones",
            "asignaciones": asignaciones,
            "sin_asignar": sin_asignar,
            "medicos_disponibles": medicos_disponibles,
            "stats": stats,
        },
    )


@router.post("/asignaciones/auto")
async def crear_asignacion_automatica(
    paciente_email: str = Form(...),
    dificultad: str = Form("media"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Asignación automática: elige médico disponible al azar."""
    asignacion_existente = await db["asignaciones"].find_one({
        "paciente_email": paciente_email,
        "estado": {"$in": ["pendiente", "aceptada"]},
    })
    if asignacion_existente:
        return RedirectResponse(url="/admin/asignaciones?error=asignacion_duplicada", status_code=status.HTTP_303_SEE_OTHER)

    cursor_medicos = db["usuarios"].find({"rol": "medico", "estado": {"$nin": ["ocupado", "consulta"]}})
    medicos = []
    async for m in cursor_medicos:
        medicos.append(m)

    if not medicos:
        return RedirectResponse(url="/admin/asignaciones?error=no_medicos", status_code=status.HTTP_303_SEE_OTHER)

    medico_elegido = choice(medicos)
    nueva_asignacion = {
        "paciente_email": paciente_email,
        "medico_email": medico_elegido.get("email"),
        "actividades_asignadas": _actividades_por_dificultad(dificultad),
        "dificultad": dificultad,
        "fecha_asignacion": datetime.utcnow(),
        "estado": "pendiente",
        "tipo": "automatica",
    }
    await db["asignaciones"].insert_one(nueva_asignacion)
    return RedirectResponse(url="/admin/asignaciones", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/asignaciones/manual")
async def crear_asignacion_manual(
    paciente_email: str = Form(...),
    medico_email: str = Form(...),
    dificultad: str = Form("media"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Asignación manual: el admin elige el médico específico."""
    asignacion_existente = await db["asignaciones"].find_one({
        "paciente_email": paciente_email,
        "estado": {"$in": ["pendiente", "aceptada"]},
    })
    if asignacion_existente:
        return RedirectResponse(url="/admin/asignaciones?error=asignacion_duplicada", status_code=status.HTTP_303_SEE_OTHER)

    nueva_asignacion = {
        "paciente_email": paciente_email,
        "medico_email": medico_email,
        "actividades_asignadas": _actividades_por_dificultad(dificultad),
        "dificultad": dificultad,
        "fecha_asignacion": datetime.utcnow(),
        "estado": "pendiente",
        "tipo": "manual",
    }
    await db["asignaciones"].insert_one(nueva_asignacion)
    return RedirectResponse(url="/admin/asignaciones", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/asignaciones/{asignacion_id}/eliminar")
async def eliminar_asignacion_admin(
    asignacion_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Elimina una asignación."""
    object_id = _parse_object_id(asignacion_id)
    if not object_id:
        return RedirectResponse(url="/admin/asignaciones?error=id_invalido", status_code=status.HTTP_303_SEE_OTHER)
    await db["asignaciones"].delete_one({"_id": object_id})
    return RedirectResponse(url="/admin/asignaciones", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/historial", response_class=HTMLResponse)
async def vista_historial_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    cursor = db["historial_actividades"].find({}).sort("fecha", -1)
    historial = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        historial.append(doc)

    # Estadísticas por categoría de juego
    stats_categoria = defaultdict(lambda: {"total": 0, "con_feedback": 0})
    for h in historial:
        cat = h.get("categoria", "otro")
        stats_categoria[cat]["total"] += 1
        if h.get("feedback"):
            stats_categoria[cat]["con_feedback"] += 1

    return templates.TemplateResponse(
        "admin/historial.html",
        {
            "request": request,
            "titulo_pagina": "Historial de actividades",
            "historial": historial,
            "stats_categoria": dict(stats_categoria),
        },
    )


@router.get("/resultados", response_class=HTMLResponse)
async def vista_resultados_admin(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    cursor = db["resultados_juegos"].find({}).sort("fecha", -1).limit(200)
    resultados = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        resultados.append(doc)

    # Estadísticas por paciente
    stats_paciente = defaultdict(lambda: {"total": 0, "completados": 0, "en_progreso": 0})
    for r in resultados:
        email = r.get("paciente_email", "desconocido")
        stats_paciente[email]["total"] += 1
        if r.get("completado"):
            stats_paciente[email]["completados"] += 1
        else:
            stats_paciente[email]["en_progreso"] += 1

    # Estadísticas por juego (aciertos/desaciertos)
    stats_juego = defaultdict(lambda: {"total": 0, "completados": 0})
    for r in resultados:
        key = r.get("juego", "desconocido")
        stats_juego[key]["total"] += 1
        if r.get("completado"):
            stats_juego[key]["completados"] += 1

    return templates.TemplateResponse(
        "admin/resultados.html",
        {
            "request": request,
            "titulo_pagina": "Resultados de juegos",
            "resultados": resultados,
            "stats_paciente": dict(stats_paciente),
            "stats_juego": dict(stats_juego),
        },
    )
