from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timedelta
from collections import defaultdict
from html import escape
import re

from ..database import get_db
from ..security import email_match_filter, get_current_user, require_role

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
    user = get_current_user(request)
    if user:
        return user.get("email", "")
    return request.query_params.get("email", "")


def _parse_object_id(value: str) -> ObjectId | None:
    try:
        return ObjectId(value)
    except InvalidId:
        return None


async def _obtener_doctor_actual(request: Request, db: AsyncIOMotorDatabase):
    email_doctor = _doctor_email_desde_request(request)
    if not email_doctor:
        return None
    return await db["usuarios"].find_one({**email_match_filter(email_doctor), "rol": "medico"})


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


def _filtro_feedback(estado: str):
    if estado == "pendientes":
        return {"$or": [{"feedback": None}, {"feedback": ""}]}
    if estado == "evaluadas":
        return {"feedback": {"$nin": [None, ""]}}
    return {}


def _parse_fecha_param(fecha_texto: str) -> datetime | None:
    if not fecha_texto:
        return None
    try:
        return datetime.strptime(fecha_texto, "%Y-%m-%d")
    except ValueError:
        return None


async def _adjuntar_evidencia_historial(
    db: AsyncIOMotorDatabase,
    historial_docs: list[dict],
) -> list[dict]:
    for doc in historial_docs:
        fecha = doc.get("fecha")
        juego = doc.get("juego", "")
        paciente_email = doc.get("paciente_email", "")
        evidencia = ""
        pasos_label = "-"
        ruta_juego = ""
        puntaje_sistema = doc.get("puntaje_sistema", doc.get("puntos_obtenidos", 0))
        audio_transcripcion = (doc.get("audio_transcripcion") or "").strip()
        audio_url = (doc.get("audio_url") or "").strip()
        requiere_revision_audio = bool(doc.get("requiere_revision_audio"))

        query = {
            "paciente_email": paciente_email,
            "juego": juego,
        }
        if fecha:
            inicio = datetime(fecha.year, fecha.month, fecha.day)
            fin = inicio + timedelta(days=1)
            query["fecha"] = {"$gte": inicio, "$lt": fin}

        resultado = await db["resultados_juegos"].find_one(query, sort=[("fecha", -1)])
        if resultado:
            nota = (resultado.get("notas") or "").strip()
            ruta_juego = resultado.get("ruta", "")
            paso = resultado.get("paso_completado", 0)
            total = resultado.get("total_pasos", 0)
            pasos_label = f"{paso}/{total}" if total else "-"
            puntaje_sistema = resultado.get("puntaje_actividad", resultado.get("puntos", puntaje_sistema))
            audio_transcripcion = (resultado.get("audio_transcripcion") or audio_transcripcion).strip()
            audio_url = (resultado.get("audio_url") or audio_url).strip()
            requiere_revision_audio = bool(resultado.get("requiere_revision_audio", requiere_revision_audio))
            if nota:
                evidencia = nota
            elif audio_transcripcion:
                evidencia = f"Dijo: {audio_transcripcion}"
            elif ruta_juego:
                evidencia = f"Recorrido en {ruta_juego} con progreso {pasos_label}"
        if not evidencia:
            evidencia = f"Completó {doc.get('actividad', 'actividad')} ({doc.get('categoria', 'categoría')})"

        doc["detalle_actividad"] = evidencia
        doc["pasos_label"] = pasos_label
        doc["ruta_juego"] = ruta_juego
        doc["puntaje_sistema"] = puntaje_sistema
        doc["audio_transcripcion"] = audio_transcripcion
        doc["audio_url"] = audio_url
        doc["requiere_revision_audio"] = requiere_revision_audio
        doc["tiene_evidencia_audio"] = bool(audio_url or audio_transcripcion)
    return historial_docs


async def _construir_reporte_diario_doctor(
    db: AsyncIOMotorDatabase,
    *,
    paciente_email: str,
    fecha_base: datetime,
) -> dict:
    inicio = datetime(fecha_base.year, fecha_base.month, fecha_base.day)
    fin = inicio + timedelta(days=1)

    resultados = []
    historial_por_juego = {}
    cursor_hist = db["historial_actividades"].find(
        {
            "paciente_email": paciente_email,
            "fecha": {"$gte": inicio, "$lt": fin},
        }
    )
    async for doc in cursor_hist:
        historial_por_juego[doc.get("juego", "")] = doc

    cursor_resultados = db["resultados_juegos"].find(
        {
            "paciente_email": paciente_email,
            "fecha": {"$gte": inicio, "$lt": fin},
        }
    ).sort([("categoria", 1), ("juego", 1), ("fecha", 1)])

    async for doc in cursor_resultados:
        total_pasos = max(1, int(doc.get("total_pasos", 1)))
        paso = max(0, int(doc.get("paso_completado", 0)))
        historial = historial_por_juego.get(doc.get("juego", ""), {})
        transcripcion = (doc.get("audio_transcripcion") or historial.get("audio_transcripcion") or "").strip()
        evidencia_texto = (doc.get("notas") or historial.get("detalle_actividad") or "").strip()
        if not evidencia_texto and transcripcion:
            evidencia_texto = f"Dijo: {transcripcion}"
        resultados.append(
            {
                "categoria": doc.get("categoria", ""),
                "juego": doc.get("juego", ""),
                "actividad": historial.get("actividad", doc.get("juego", "").replace("_", " ").title()),
                "completado": bool(doc.get("completado")),
                "progreso": int((paso / total_pasos) * 100),
                "pasos_label": f"{paso}/{total_pasos}",
                "puntaje_sistema": int(doc.get("puntaje_actividad", doc.get("puntos", 0)) or 0),
                "nivel": int(doc.get("nivel", 1) or 1),
                "fecha": doc.get("fecha"),
                "detalle_actividad": evidencia_texto,
                "audio_transcripcion": transcripcion,
                "audio_url": (doc.get("audio_url") or historial.get("audio_url") or "").strip(),
                "tiene_evidencia_audio": bool(
                    (doc.get("audio_url") or historial.get("audio_url") or "").strip() or transcripcion
                ),
                "feedback": (historial.get("feedback") or "").strip(),
                "puntaje_clinico": historial.get("puntaje_clinico"),
            }
        )

    completadas = [r for r in resultados if r["completado"]]
    promedio = round(sum(r["puntaje_sistema"] for r in completadas) / len(completadas), 1) if completadas else 0
    return {
        "fecha": inicio,
        "filas": resultados,
        "resumen": {
            "total": len(resultados),
            "completadas": len(completadas),
            "promedio": promedio,
        },
    }


def _reporte_excel_xml(paciente_email: str, fecha_base: datetime, filas: list[dict]) -> str:
    def celda(valor: str | int | float) -> str:
        return (
            "<Cell><Data ss:Type=\"String\">"
            f"{escape(str(valor))}"
            "</Data></Cell>"
        )

    encabezados = [
        "Paciente",
        "Fecha",
        "Categoría",
        "Juego",
        "Actividad",
        "Completado",
        "Progreso",
        "Puntaje sistema",
        "Nivel",
        "Detalle",
        "Transcripción",
        "Audio",
        "Feedback doctor",
        "Puntaje clínico",
    ]
    rows = ["<Row>" + "".join(celda(h) for h in encabezados) + "</Row>"]
    fecha_txt = fecha_base.strftime("%Y-%m-%d")
    for fila in filas:
        rows.append(
            "<Row>"
            + "".join(
                [
                    celda(paciente_email),
                    celda(fecha_txt),
                    celda(fila.get("categoria", "")),
                    celda(fila.get("juego", "")),
                    celda(fila.get("actividad", "")),
                    celda("Sí" if fila.get("completado") else "No"),
                    celda(f"{fila.get('progreso', 0)}%"),
                    celda(fila.get("puntaje_sistema", 0)),
                    celda(fila.get("nivel", 1)),
                    celda(fila.get("detalle_actividad", "")),
                    celda(fila.get("audio_transcripcion", "")),
                    celda(fila.get("audio_url", "")),
                    celda(fila.get("feedback", "")),
                    celda(fila.get("puntaje_clinico", "")),
                ]
            )
            + "</Row>"
        )
    return (
        "<?xml version=\"1.0\"?>"
        "<?mso-application progid=\"Excel.Sheet\"?>"
        "<Workbook xmlns=\"urn:schemas-microsoft-com:office:spreadsheet\" "
        "xmlns:o=\"urn:schemas-microsoft-com:office:office\" "
        "xmlns:x=\"urn:schemas-microsoft-com:office:excel\" "
        "xmlns:ss=\"urn:schemas-microsoft-com:office:spreadsheet\">"
        "<Worksheet ss:Name=\"Reporte diario\"><Table>"
        + "".join(rows)
        + "</Table></Worksheet></Workbook>"
    )


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

    return templates.TemplateResponse(request, "doctor/home.html", {
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

    return templates.TemplateResponse(request, "doctor/pacientes.html", {
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
            stats_por_categoria[cat] = {
                "completados": 0,
                "en_progreso": 0,
                "total": 0,
                "avance_acumulado": 0,
                "puntaje_acumulado": 0,
            }
        stats_por_categoria[cat]["total"] += 1
        total_pasos = max(1, int(r.get("total_pasos", 1)))
        paso = max(0, int(r.get("paso_completado", 0)))
        avance = int((paso / total_pasos) * 100)
        stats_por_categoria[cat]["avance_acumulado"] += avance
        stats_por_categoria[cat]["puntaje_acumulado"] += int(r.get("puntaje_actividad", r.get("puntos", 0)))
        if r.get("completado"):
            stats_por_categoria[cat]["completados"] += 1
        else:
            stats_por_categoria[cat]["en_progreso"] += 1
    for cat, stats in stats_por_categoria.items():
        total = max(1, stats["total"])
        stats["avance_promedio"] = int(stats["avance_acumulado"] / total)
        stats["puntaje_promedio"] = int(stats["puntaje_acumulado"] / total)

    cursor_hist = db["historial_actividades"].find({"paciente_email": paciente["email"]}).sort("fecha", -1).limit(10)
    historial = []
    async for doc in cursor_hist:
        doc["_id"] = str(doc["_id"])
        historial.append(doc)

    return templates.TemplateResponse(request, "doctor/perfil_paciente.html", {
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
    return templates.TemplateResponse(request, "doctor/actividades.html", {
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

    return templates.TemplateResponse(request, "doctor/asignaciones.html", {
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
async def vista_historial_doctor(
    request: Request,
    paciente_email: str = "",
    categoria: str = "",
    estado: str = "todos",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    pacientes_asignados = await _emails_pacientes_asignados(db, doctor_doc["email"])
    historial = []
    pacientes_lista = sorted(list(pacientes_asignados))
    query = {"paciente_email": {"$in": pacientes_lista}}
    if paciente_email and paciente_email in pacientes_asignados:
        query["paciente_email"] = paciente_email
    if categoria:
        query["categoria"] = categoria
    query.update(_filtro_feedback(estado))

    if pacientes_asignados:
        cursor = db["historial_actividades"].find(query).sort("fecha", -1).limit(250)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            historial.append(doc)
        historial = await _adjuntar_evidencia_historial(db, historial)

    categorias = sorted({h.get("categoria", "") for h in historial if h.get("categoria")})

    return templates.TemplateResponse(request, "doctor/historial.html", {
        "request": request,
        "titulo_pagina": "Historial de actividades",
        "historial": historial,
        "pacientes_lista": pacientes_lista,
        "categorias": categorias,
        "paciente_email_sel": paciente_email,
        "categoria_sel": categoria,
        "estado_sel": estado,
    })


@router.get("/resultados", response_class=HTMLResponse)
async def vista_resultados_doctor(
    request: Request,
    paciente_email: str = "",
    categoria: str = "",
    buscar: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    pacientes_asignados = await _emails_pacientes_asignados(db, doctor_doc["email"])
    resultados = []
    pacientes_lista = sorted(list(pacientes_asignados))
    query = {"paciente_email": {"$in": pacientes_lista}}
    if paciente_email and paciente_email in pacientes_asignados:
        query["paciente_email"] = paciente_email
    if categoria:
        query["categoria"] = categoria
    if buscar:
        query["juego"] = {"$regex": re.escape(buscar.strip()), "$options": "i"}

    if pacientes_asignados:
        cursor = db["resultados_juegos"].find(query).sort("fecha", -1).limit(250)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            total_pasos = max(1, int(doc.get("total_pasos", 1)))
            paso = max(0, int(doc.get("paso_completado", 0)))
            doc["avance_pct"] = int((paso / total_pasos) * 100)
            resultados.append(doc)

    categorias = sorted({r.get("categoria", "") for r in resultados if r.get("categoria")})

    return templates.TemplateResponse(request, "doctor/resultados.html", {
        "request": request,
        "titulo_pagina": "Resultados de juegos",
        "resultados": resultados,
        "pacientes_lista": pacientes_lista,
        "categorias": categorias,
        "paciente_email_sel": paciente_email,
        "categoria_sel": categoria,
        "buscar_sel": buscar,
    })


@router.get("/reportes-diarios", response_class=HTMLResponse)
async def vista_reportes_diarios_doctor(
    request: Request,
    paciente_email: str = "",
    fecha: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    pacientes_asignados = await _emails_pacientes_asignados(db, doctor_doc["email"])
    pacientes_lista = sorted(list(pacientes_asignados))
    fecha_base = _parse_fecha_param(fecha) or datetime.utcnow()
    reporte = None

    if paciente_email and paciente_email in pacientes_asignados:
        reporte = await _construir_reporte_diario_doctor(
            db,
            paciente_email=paciente_email,
            fecha_base=fecha_base,
        )

    return templates.TemplateResponse(request, "doctor/reportes_diarios.html", {
        "request": request,
        "titulo_pagina": "Reportes diarios",
        "pacientes_lista": pacientes_lista,
        "paciente_email_sel": paciente_email,
        "fecha_sel": fecha_base.strftime("%Y-%m-%d"),
        "reporte": reporte,
    })


@router.get("/reportes-diarios/excel")
async def descargar_reporte_diario_excel(
    request: Request,
    paciente_email: str,
    fecha: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    pacientes_asignados = await _emails_pacientes_asignados(db, doctor_doc["email"])
    if paciente_email not in pacientes_asignados:
        return RedirectResponse(url="/doctor/reportes-diarios", status_code=303)

    fecha_base = _parse_fecha_param(fecha) or datetime.utcnow()
    reporte = await _construir_reporte_diario_doctor(
        db,
        paciente_email=paciente_email,
        fecha_base=fecha_base,
    )
    contenido = _reporte_excel_xml(paciente_email, reporte["fecha"], reporte["filas"])
    fecha_archivo = reporte["fecha"].strftime("%Y-%m-%d")
    headers = {
        "Content-Disposition": (
            f'attachment; filename="reporte-diario-{paciente_email}-{fecha_archivo}.xls"'
        )
    }
    return Response(content=contenido, media_type="application/vnd.ms-excel", headers=headers)


@router.get("/evaluaciones-pendientes", response_class=HTMLResponse)
async def vista_evaluaciones_pendientes(
    request: Request,
    paciente_email: str = "",
    categoria: str = "",
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return RedirectResponse(url="/auth/login", status_code=303)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return RedirectResponse(url="/auth/login", status_code=303)

    pacientes_asignados = await _emails_pacientes_asignados(db, doctor_doc["email"])
    evaluaciones = []
    pacientes_lista = sorted(list(pacientes_asignados))
    query = {
        "paciente_email": {"$in": pacientes_lista},
        "$or": [{"feedback": None}, {"feedback": ""}],
    }
    if paciente_email and paciente_email in pacientes_asignados:
        query["paciente_email"] = paciente_email
    if categoria:
        query["categoria"] = categoria

    if pacientes_asignados:
        cursor = db["historial_actividades"].find(query).sort("fecha", -1).limit(250)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            evaluaciones.append(doc)
        evaluaciones = await _adjuntar_evidencia_historial(db, evaluaciones)

    categorias = sorted({e.get("categoria", "") for e in evaluaciones if e.get("categoria")})

    return templates.TemplateResponse(request, "doctor/evaluaciones_pendientes.html", {
        "request": request,
        "titulo_pagina": "Evaluaciones Pendientes",
        "evaluaciones": evaluaciones,
        "pacientes_lista": pacientes_lista,
        "categorias": categorias,
        "paciente_email_sel": paciente_email,
        "categoria_sel": categoria,
    })


@router.get("/notificaciones/pending", response_class=JSONResponse)
async def notificaciones_pendientes_doctor(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = get_current_user(request)
    if not user or user.get("rol") not in ("medico", "doctor"):
        return JSONResponse({"items": []}, status_code=401)

    doctor_doc = await _obtener_doctor_actual(request, db)
    if not doctor_doc:
        return {"items": []}

    docs = []
    ids = []
    cursor = db["notificaciones_doctor"].find(
        {"medico_email": doctor_doc["email"], "leida": False}
    ).sort("creada_en", -1).limit(20)
    async for doc in cursor:
        ids.append(doc["_id"])
        docs.append(
            {
                "id": str(doc["_id"]),
                "paciente_email": doc.get("paciente_email", ""),
                "actividad": doc.get("actividad", ""),
                "categoria": doc.get("categoria", ""),
                "puntaje_actividad": doc.get("puntaje_actividad", 0),
            }
        )

    if ids:
        await db["notificaciones_doctor"].update_many(
            {"_id": {"$in": ids}},
            {"$set": {"leida": True, "leida_en": datetime.utcnow()}},
        )

    return {"items": docs}


@router.post("/evaluaciones/{historial_id}/feedback")
async def guardar_feedback(
    historial_id: str,
    request: Request,
    feedback: str = Form(...),
    calificacion: int = Form(3),
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

    calificacion = max(1, min(5, int(calificacion)))
    puntaje_base = int(historial.get("puntaje_sistema", historial.get("puntos_obtenidos", 0)))
    puntaje_base = max(0, min(100, puntaje_base))
    puntaje_clinico = int(round((puntaje_base * 0.7) + ((calificacion * 20) * 0.3)))
    await db["historial_actividades"].update_one(
        {"_id": object_id},
        {
            "$set": {
                "feedback": feedback,
                "calificacion_doctor": calificacion,
                "puntaje_clinico": puntaje_clinico,
                "fecha_feedback": datetime.utcnow(),
            }
        },
    )
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
