from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from bson.errors import InvalidId

from ..database import get_db
from ..security import get_current_user, require_role

router = APIRouter(
    prefix="/doctor",
    tags=["doctor-web"],
    dependencies=[Depends(require_role(["medico", "doctor"]))],
)
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


def _doctor_email_desde_request(request: Request) -> str:
    return request.query_params.get("email") or request.cookies.get("usuario_email", "")


def _parse_object_id(value: str) -> ObjectId | None:
    try:
        return ObjectId(value)
    except InvalidId:
        return None


async def _obtener_doctor_actual(request: Request, db: AsyncIOMotorDatabase):
    email_doctor = _doctor_email_desde_request(request)
    if not email_doctor:
        return None
    return await db["usuarios"].find_one({"email": email_doctor, "rol": "medico"})


async def _emails_pacientes_asignados(
    db: AsyncIOMotorDatabase,
    doctor_email: str,
    estados: tuple[str, ...] = ("aceptada",),
) -> set[str]:
    query = {"medico_email": doctor_email}
    if estados:
        query["estado"] = {"$in": list(estados)}
    cursor = db["asignaciones"].find(query, {"paciente_email": 1})
    emails = set()
    async for doc in cursor:
        email = doc.get("paciente_email")
        if email:
            emails.add(email)
    return emails


@router.get("/home", response_class=HTMLResponse)
async def home_doctor(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_email = doctor_doc.get("email", "")
    pacientes_asignados = await _emails_pacientes_asignados(db, doctor_email)
    pendientes = 0
    if pacientes_asignados:
        pendientes = await db["historial_actividades"].count_documents({
            "paciente_email": {"$in": list(pacientes_asignados)},
            "$or": [{"feedback": None}, {"feedback": ""}],
        })

    return templates.TemplateResponse("doctor/home.html", {
        "request": request,
        "titulo_pagina": "Panel del doctor",
        "estado_actual": doctor_doc.get("estado", "activo"),
        "nombre_doctor": doctor_doc.get("nombre", "Doctor"),
        "email_doctor": doctor_email,
        "evaluaciones_pendientes": pendientes,
    })


@router.get("/pacientes", response_class=HTMLResponse)
async def vista_pacientes_doctor(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    pacientes_asignados = await _emails_pacientes_asignados(db, doctor_doc["email"])
    pacientes = []
    if pacientes_asignados:
        cursor = db["usuarios"].find({"rol": "paciente", "email": {"$in": list(pacientes_asignados)}})
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            total_j = await db["resultados_juegos"].count_documents({"paciente_email": doc["email"]})
            completados_j = await db["resultados_juegos"].count_documents({"paciente_email": doc["email"], "completado": True})
            doc["total_juegos"] = total_j
            doc["juegos_completados"] = completados_j
            pacientes.append(doc)

    return templates.TemplateResponse("doctor/pacientes.html", {
        "request": request,
        "titulo_pagina": "Mis pacientes",
        "pacientes": pacientes,
    })


@router.get("/pacientes/{paciente_id}", response_class=HTMLResponse)
async def perfil_paciente_doctor(paciente_id: str, request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    object_id = _parse_object_id(paciente_id)
    if not object_id:
        return RedirectResponse(url="/doctor/pacientes", status_code=303)

    paciente = await db["usuarios"].find_one({"_id": object_id, "rol": "paciente"})
    if not paciente:
        return RedirectResponse(url="/doctor/pacientes", status_code=303)

    asignacion = await db["asignaciones"].find_one({
        "paciente_email": paciente["email"],
        "medico_email": doctor_doc["email"],
        "estado": "aceptada",
    })
    if not asignacion:
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
        "request": request,
        "titulo_pagina": f"Perfil de {paciente.get('nombre', paciente['email'])}",
        "paciente": paciente,
        "perfil": perfil,
        "resultados": resultados_raw[:10],
        "stats_por_categoria": stats_por_categoria,
        "historial": historial,
    })


@router.post("/pacientes/{paciente_id}/editar")
async def editar_paciente_doctor(
    paciente_id: str,
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    object_id = _parse_object_id(paciente_id)
    if not object_id:
        return RedirectResponse(url="/doctor/pacientes", status_code=303)

    paciente_actual = await db["usuarios"].find_one({"_id": object_id, "rol": "paciente"})
    if not paciente_actual:
        return RedirectResponse(url="/doctor/pacientes", status_code=303)

    asignacion = await db["asignaciones"].find_one({
        "paciente_email": paciente_actual["email"],
        "medico_email": doctor_doc["email"],
        "estado": "aceptada",
    })
    if not asignacion:
        return RedirectResponse(url="/doctor/pacientes", status_code=303)

    email_anterior = paciente_actual.get("email", "")
    await db["usuarios"].update_one({"_id": object_id}, {"$set": {"nombre": nombre, "email": email}})

    if email_anterior and email_anterior != email:
        await db["perfiles_pacientes"].update_many({"paciente_email": email_anterior}, {"$set": {"paciente_email": email}})
        await db["asignaciones"].update_many({"paciente_email": email_anterior}, {"$set": {"paciente_email": email}})
        await db["resultados_juegos"].update_many({"paciente_email": email_anterior}, {"$set": {"paciente_email": email}})
        await db["historial_actividades"].update_many({"paciente_email": email_anterior}, {"$set": {"paciente_email": email}})
        await db["sesiones_app"].update_many({"paciente_email": email_anterior}, {"$set": {"paciente_email": email}})
    return RedirectResponse(url=f"/doctor/pacientes/{paciente_id}", status_code=303)


@router.get("/actividades", response_class=HTMLResponse)
async def vista_actividades_doctor(request: Request):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("doctor/actividades.html", {
        "request": request, "titulo_pagina": "Juegos disponibles", "juegos_disponibles": JUEGOS_DISPONIBLES,
    })


@router.get("/asignaciones", response_class=HTMLResponse)
async def vista_asignaciones_doctor(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_email = doctor_doc["email"]
    cursor = db["asignaciones"].find({"medico_email": doctor_email}).sort("fecha_asignacion", -1)
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
async def aceptar_asignacion(asignacion_id: str, request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    object_id = _parse_object_id(asignacion_id)
    if object_id:
        await db["asignaciones"].update_one(
            {"_id": object_id, "medico_email": doctor_doc["email"]},
            {"$set": {"estado": "aceptada"}},
        )
    return RedirectResponse(url="/doctor/asignaciones", status_code=303)


@router.post("/asignaciones/{asignacion_id}/cancelar", response_class=RedirectResponse)
async def cancelar_asignacion(asignacion_id: str, request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    object_id = _parse_object_id(asignacion_id)
    if object_id:
        await db["asignaciones"].update_one(
            {"_id": object_id, "medico_email": doctor_doc["email"]},
            {"$set": {"estado": "cancelada"}},
        )
    return RedirectResponse(url="/doctor/asignaciones", status_code=303)


@router.get("/historial", response_class=HTMLResponse)
async def vista_historial_doctor(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    pacientes_asignados = await _emails_pacientes_asignados(db, doctor_doc["email"])
    historial = []
    if pacientes_asignados:
        cursor = db["historial_actividades"].find({"paciente_email": {"$in": list(pacientes_asignados)}}).sort("fecha", -1)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            historial.append(doc)

    return templates.TemplateResponse("doctor/historial.html", {
        "request": request, "titulo_pagina": "Historial de actividades", "historial": historial,
    })


@router.get("/resultados", response_class=HTMLResponse)
async def vista_resultados_doctor(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    pacientes_asignados = await _emails_pacientes_asignados(db, doctor_doc["email"])
    resultados = []
    if pacientes_asignados:
        cursor = db["resultados_juegos"].find({"paciente_email": {"$in": list(pacientes_asignados)}}).sort("fecha", -1).limit(100)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            resultados.append(doc)

    return templates.TemplateResponse("doctor/resultados.html", {
        "request": request, "titulo_pagina": "Resultados de juegos", "resultados": resultados,
    })


@router.get("/evaluaciones-pendientes", response_class=HTMLResponse)
async def vista_evaluaciones_pendientes(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    pacientes_asignados = await _emails_pacientes_asignados(db, doctor_doc["email"])
    evaluaciones = []
    if pacientes_asignados:
        cursor = db["historial_actividades"].find({
            "paciente_email": {"$in": list(pacientes_asignados)},
            "$or": [{"feedback": None}, {"feedback": ""}],
        }).sort("fecha", -1)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            evaluaciones.append(doc)

    return templates.TemplateResponse("doctor/evaluaciones_pendientes.html", {
        "request": request, "titulo_pagina": "Evaluaciones Pendientes", "evaluaciones": evaluaciones,
    })


@router.post("/evaluaciones/{historial_id}/feedback")
async def guardar_feedback(
    historial_id: str,
    request: Request,
    feedback: str = Form(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    object_id = _parse_object_id(historial_id)
    if not object_id:
        return RedirectResponse(url="/doctor/evaluaciones-pendientes", status_code=303)

    historial = await db["historial_actividades"].find_one({"_id": object_id})
    if not historial:
        return RedirectResponse(url="/doctor/evaluaciones-pendientes", status_code=303)

    pacientes_asignados = await _emails_pacientes_asignados(db, doctor_doc["email"])
    if historial.get("paciente_email") not in pacientes_asignados:
        return RedirectResponse(url="/doctor/evaluaciones-pendientes", status_code=303)

    await db["historial_actividades"].update_one({"_id": object_id}, {"$set": {"feedback": feedback}})
    return RedirectResponse(url="/doctor/evaluaciones-pendientes", status_code=303)


@router.post("/estado", response_class=RedirectResponse)
async def cambiar_estado_doctor(
    request: Request,
    estado: str = Form(...),
    email: str = Form(""),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    email_objetivo = email or doctor_doc.get("email", "")
    if email_objetivo != doctor_doc.get("email", ""):
        email_objetivo = doctor_doc.get("email", "")

    await db["usuarios"].update_one({"email": email_objetivo, "rol": "medico"}, {"$set": {"estado": estado}})
    return RedirectResponse(url="/doctor/home", status_code=303)
