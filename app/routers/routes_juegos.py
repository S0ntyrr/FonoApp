"""
FonoApp - Router de Juegos Fonoaudiológicos
============================================
Hub principal de los 23 juegos terapéuticos organizados en 7 categorías.

Categorías y juegos:
  Respiración (2):
    - /juegos/respiracion/globo    → Infla el globo (micrófono)
    - /juegos/respiracion/molino   → El molino de Pepe (micrófono)
  
  Fonación (2):
    - /juegos/fonacion/gol         → ¡Haz un gol! (voz)
    - /juegos/fonacion/escala      → Escala musical (voz)
  
  Resonancia (3):
    - /juegos/resonancia/escaleras → Escaleras de tono (voz)
    - /juegos/resonancia/piano     → Piano - Estrellita (interactivo)
    - /juegos/resonancia/veoveo    → ¡Veo, veo! (micrófono)
  
  Articulación (6):
    - /juegos/articulacion/letra-b → Letra B (pronunciación)
    - /juegos/articulacion/letra-d → Letra D (pronunciación)
    - /juegos/articulacion/letra-f → Letra F (pronunciación)
    - /juegos/articulacion/letra-r → Letra R (pronunciación)
    - /juegos/articulacion/completa-palabra → Completa la palabra
    - /juegos/articulacion/moto-voz → ¡Acelera la moto! (micrófono)
  
  Prosodia (4):
    - /juegos/prosodia/adivina-animal    → Adivina el animal (micrófono, 4 intentos)
    - /juegos/prosodia/trabalenguas      → Trabalenguas (micrófono + registro)
    - /juegos/prosodia/adivinanza-imagen → Relaciona la adivinanza (imágenes)
    - /juegos/prosodia/completa-cancion  → Completa la canción (voz)
  
  Discriminación Auditiva (3):
    - /juegos/discriminacion/sonidos-animales → Sonidos de animales
    - /juegos/discriminacion/sonidos-objetos  → Sonidos de objetos
    - /juegos/discriminacion/arrastra-sonido  → Arrastra al sonido (drag & drop)
  
  Practica Conmigo (3):
    - /juegos/practica/rompecabezas → Rompecabezas de letras
    - /juegos/practica/cara         → Crea tu personaje
    - /juegos/practica/asociacion   → Asociación de imágenes

Rutas especiales:
  POST /juegos/resultado          → Guarda resultado en BD (llamado desde JS)
  GET  /juegos/seed-actividades   → Actualiza colección 'actividades' en MongoDB

Sistema de guardado de resultados:
  Cuando un paciente completa un juego, el JS llama a guardarResultadoJuego()
  (definida en base.html) que hace POST a /juegos/resultado.
  
  Este endpoint:
  1. Guarda en 'resultados_juegos' (detalle técnico)
  2. Si completado=True, también guarda en 'historial_actividades'
     para que el médico pueda evaluarlo en /doctor/evaluaciones-pendientes
"""

import base64
from datetime import datetime, timedelta
from pathlib import Path

from bson import ObjectId
from fastapi import APIRouter, Request, Depends, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database import get_db
from ..security import require_role

router = APIRouter(
    prefix="/juegos",
    tags=["juegos"],
    dependencies=[Depends(require_role(["admin", "medico", "doctor", "paciente", "emisor"]))],
)
templates = Jinja2Templates(directory="app/templates")
ALLOWED_AUDIO_EXTENSIONS = {".webm", ".wav", ".ogg", ".m4a", ".mp3", ".mp4"}
MAX_AUDIO_BYTES = 4 * 1024 * 1024

CONTENT_TYPE_MAP = {
    ".webm": "audio/webm",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".m4a": "audio/mp4",
    ".mp3": "audio/mpeg",
    ".mp4": "audio/mp4",
}


async def _crear_notificaciones_doctor(
    db: AsyncIOMotorDatabase,
    *,
    paciente_email: str,
    categoria: str,
    juego: str,
    actividad: str,
    puntaje_actividad: int,
    fecha: datetime,
) -> None:
    fecha_dia = datetime(fecha.year, fecha.month, fecha.day)
    asignaciones = db["asignaciones"].find(
        {
            "paciente_email": paciente_email,
            "estado": {"$in": ["aceptada", "activo", "asignada"]},
        },
        {"medico_email": 1},
    )
    async for asignacion in asignaciones:
        medico_email = (asignacion.get("medico_email") or "").strip()
        if not medico_email:
            continue
        await db["notificaciones_doctor"].update_one(
            {
                "medico_email": medico_email,
                "paciente_email": paciente_email,
                "juego": juego,
                "fecha_dia": fecha_dia,
            },
            {
                "$set": {
                    "categoria": categoria,
                    "actividad": actividad,
                    "puntaje_actividad": puntaje_actividad,
                    "fecha_actividad": fecha,
                    "leida": False,
                },
                "$setOnInsert": {
                    "medico_email": medico_email,
                    "paciente_email": paciente_email,
                    "juego": juego,
                    "fecha_dia": fecha_dia,
                    "creada_en": datetime.utcnow(),
                },
            },
            upsert=True,
        )


@router.get("/", response_class=HTMLResponse)
async def hub_juegos(request: Request):
    """
    Hub principal de juegos de Fonoaudiología.
    Accesible por admin, doctor y paciente.
    """
    return templates.TemplateResponse(
        request,
        "juegos/index.html",
        {
            "request": request,
            "titulo_pagina": "Juegos Fonoaudiológicos",
        },
    )


# ─── PRACTICA CONMIGO ────────────────────────────────────────────────────────

@router.get("/practica", response_class=HTMLResponse)
async def juego_practica(request: Request):
    """
    Hub de 'Practica Conmigo': rompecabezas, constructor de cara y asociación de imágenes.
    """
    return templates.TemplateResponse(
        request,
        "juegos/practica/index.html",
        {
            "request": request,
            "titulo_pagina": "Practica Conmigo",
        },
    )


@router.get("/practica/rompecabezas", response_class=HTMLResponse)
async def juego_rompecabezas(request: Request):
    """
    Juego de rompecabezas con letras y animales.
    """
    return templates.TemplateResponse(
        request,
        "juegos/practica/rompecabezas.html",
        {
            "request": request,
            "titulo_pagina": "Rompecabezas",
        },
    )


@router.get("/practica/cara", response_class=HTMLResponse)
async def juego_cara(request: Request):
    """
    Juego de construcción de cara: arrastra partes del rostro.
    """
    return templates.TemplateResponse(
        request,
        "juegos/practica/cara.html",
        {
            "request": request,
            "titulo_pagina": "Crea tu personaje",
        },
    )


@router.get("/practica/asociacion", response_class=HTMLResponse)
async def juego_asociacion(request: Request):
    """
    Juego de asociación de imágenes con conceptos.
    """
    return templates.TemplateResponse(
        request,
        "juegos/practica/asociacion.html",
        {
            "request": request,
            "titulo_pagina": "Asociación de imágenes",
        },
    )


# ─── RESPIRACIÓN ─────────────────────────────────────────────────────────────

@router.get("/respiracion", response_class=HTMLResponse)
async def juego_respiracion(request: Request):
    """
    Juego de respiración diafragmática con globo animado.
    Usa el micrófono para detectar el soplido.
    """
    return templates.TemplateResponse(
        request,
        "juegos/respiracion/index.html",
        {
            "request": request,
            "titulo_pagina": "Respiración",
        },
    )


@router.get("/respiracion/globo", response_class=HTMLResponse)
async def juego_globo(request: Request):
    """
    Infla el globo soplando (micrófono).
    """
    return templates.TemplateResponse(
        request,
        "juegos/respiracion/globo.html",
        {
            "request": request,
            "titulo_pagina": "Infla el globo",
        },
    )


@router.get("/respiracion/molino", response_class=HTMLResponse)
async def juego_molino(request: Request):
    """
    Ayuda a Pepe a arreglar el molino soplando.
    """
    return templates.TemplateResponse(
        request,
        "juegos/respiracion/molino.html",
        {
            "request": request,
            "titulo_pagina": "El molino de Pepe",
        },
    )


# ─── FONACIÓN ────────────────────────────────────────────────────────────────

@router.get("/fonacion", response_class=HTMLResponse)
async def juego_fonacion(request: Request):
    """
    Hub de juegos de Fonación.
    """
    return templates.TemplateResponse(
        request,
        "juegos/fonacion/index.html",
        {
            "request": request,
            "titulo_pagina": "Fonación",
        },
    )


@router.get("/fonacion/gol", response_class=HTMLResponse)
async def juego_gol(request: Request):
    """
    Juego de fútbol: emite 'goooool' con la voz para marcar goles.
    """
    return templates.TemplateResponse(
        request,
        "juegos/fonacion/gol.html",
        {
            "request": request,
            "titulo_pagina": "¡Haz un gol!",
        },
    )


@router.get("/fonacion/escala", response_class=HTMLResponse)
async def juego_escala(request: Request):
    """
    Juego de escala musical: imita sonidos /a/, /e/, /i/ con la flauta.
    """
    return templates.TemplateResponse(
        request,
        "juegos/fonacion/escala.html",
        {
            "request": request,
            "titulo_pagina": "Escala musical",
        },
    )


# ─── RESONANCIA ──────────────────────────────────────────────────────────────

@router.get("/resonancia", response_class=HTMLResponse)
async def juego_resonancia(request: Request):
    """
    Hub de juegos de Resonancia.
    """
    return templates.TemplateResponse(
        request,
        "juegos/resonancia/index.html",
        {
            "request": request,
            "titulo_pagina": "Resonancia",
        },
    )


@router.get("/resonancia/escaleras", response_class=HTMLResponse)
async def juego_escaleras(request: Request):
    """
    Personaje sube/baja escaleras según el tono de voz del usuario.
    """
    return templates.TemplateResponse(
        request,
        "juegos/resonancia/escaleras.html",
        {
            "request": request,
            "titulo_pagina": "Escaleras de resonancia",
        },
    )


@router.get("/resonancia/piano", response_class=HTMLResponse)
async def juego_piano(request: Request):
    """
    Piano interactivo: toca 'Estrellita' y luego cántala.
    """
    return templates.TemplateResponse(
        request,
        "juegos/resonancia/piano.html",
        {
            "request": request,
            "titulo_pagina": "Piano - Estrellita",
        },
    )


@router.get("/resonancia/veoveo", response_class=HTMLResponse)
async def juego_veoveo(request: Request):
    """
    Juego Veo Veo: encuentra la imagen objetivo entre muchas y luego nómbrala con el micrófono.
    """
    return templates.TemplateResponse(
        request,
        "juegos/resonancia/veoveo.html",
        {
            "request": request,
            "titulo_pagina": "¡Veo, veo!",
        },
    )


# ─── ARTICULACIÓN ─────────────────────────────────────────────────────────────

@router.get("/articulacion", response_class=HTMLResponse)
async def juego_articulacion(request: Request):
    """Hub de juegos de Articulación."""
    return templates.TemplateResponse(
        request,
        "juegos/articulacion/index.html",
        {"request": request, "titulo_pagina": "Articulación"},
    )

@router.get("/articulacion/letra-b", response_class=HTMLResponse)
async def articulacion_letra_b(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/articulacion/letra_b.html",
        {"request": request, "titulo_pagina": "Articulación - Letra B"},
    )

@router.get("/articulacion/letra-d", response_class=HTMLResponse)
async def articulacion_letra_d(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/articulacion/letra_d.html",
        {"request": request, "titulo_pagina": "Articulación - Letra D"},
    )

@router.get("/articulacion/letra-f", response_class=HTMLResponse)
async def articulacion_letra_f(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/articulacion/letra_f.html",
        {"request": request, "titulo_pagina": "Articulación - Letra F"},
    )

@router.get("/articulacion/letra-r", response_class=HTMLResponse)
async def articulacion_letra_r(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/articulacion/letra_r.html",
        {"request": request, "titulo_pagina": "Articulación - Letra R"},
    )


@router.get("/articulacion/completa-palabra", response_class=HTMLResponse)
async def articulacion_completa_palabra(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/articulacion/completa_palabra.html",
        {"request": request, "titulo_pagina": "Completa la palabra"},
    )

@router.get("/articulacion/moto-voz", response_class=HTMLResponse)
async def articulacion_moto_voz(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/articulacion/moto_voz.html",
        {"request": request, "titulo_pagina": "¡Acelera la moto!"},
    )


# ─── PROSODIA ─────────────────────────────────────────────────────────────────

@router.get("/prosodia", response_class=HTMLResponse)
async def hub_prosodia(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/prosodia/index.html",
        {"request": request, "titulo_pagina": "Prosodia"},
    )

@router.get("/prosodia/adivina-animal", response_class=HTMLResponse)
async def prosodia_adivina_animal(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/prosodia/adivina_animal.html",
        {"request": request, "titulo_pagina": "Adivina el animal"},
    )

@router.get("/prosodia/trabalenguas", response_class=HTMLResponse)
async def prosodia_trabalenguas(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/prosodia/trabalenguas.html",
        {"request": request, "titulo_pagina": "Trabalenguas"},
    )

@router.get("/prosodia/adivinanza-imagen", response_class=HTMLResponse)
async def prosodia_adivinanza_imagen(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/prosodia/adivinanza_imagen.html",
        {"request": request, "titulo_pagina": "Relaciona la adivinanza"},
    )

@router.get("/prosodia/completa-cancion", response_class=HTMLResponse)
async def prosodia_completa_cancion(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/prosodia/completa_cancion.html",
        {"request": request, "titulo_pagina": "Completa la canción"},
    )


# ─── DISCRIMINACIÓN AUDITIVA ──────────────────────────────────────────────────

@router.get("/discriminacion", response_class=HTMLResponse)
async def hub_discriminacion(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/discriminacion/index.html",
        {"request": request, "titulo_pagina": "Discriminación Auditiva"},
    )

@router.get("/discriminacion/sonidos-animales", response_class=HTMLResponse)
async def discriminacion_sonidos_animales(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/discriminacion/sonidos_animales.html",
        {"request": request, "titulo_pagina": "Sonidos de animales"},
    )

@router.get("/discriminacion/sonidos-objetos", response_class=HTMLResponse)
async def discriminacion_sonidos_objetos(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/discriminacion/sonidos_objetos.html",
        {"request": request, "titulo_pagina": "Sonidos de objetos"},
    )

@router.get("/discriminacion/arrastra-sonido", response_class=HTMLResponse)
async def discriminacion_arrastra_sonido(request: Request):
    return templates.TemplateResponse(
        request,
        "juegos/discriminacion/arrastra_sonido.html",
        {"request": request, "titulo_pagina": "Arrastra al sonido"},
    )


# ─── RESULTADO DE JUEGO ───────────────────────────────────────────────────────

@router.post("/evidencia-audio", response_class=JSONResponse)
async def subir_evidencia_audio(
    audio: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(require_role(["paciente"])),
):
    """Guarda evidencia de audio en MongoDB (evita filesystem de solo lectura en Vercel)."""
    if not audio or not audio.filename:
        return {"status": "ok", "audio_url": "", "paciente_email": user["email"]}

    ext = Path(audio.filename).suffix.lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        return JSONResponse(status_code=400, content={"detail": f"Extensión no permitida: {ext}"})

    contenido = await audio.read()
    if not contenido:
        return {"status": "ok", "audio_url": "", "paciente_email": user["email"]}
    if len(contenido) > MAX_AUDIO_BYTES:
        return JSONResponse(status_code=413, content={"detail": "Archivo demasiado grande (máx 4 MB)"})

    doc = {
        "paciente_email": user["email"],
        "extension": ext,
        "content_type": CONTENT_TYPE_MAP.get(ext, "audio/webm"),
        "data_b64": base64.b64encode(contenido).decode(),
        "fecha": datetime.utcnow(),
    }
    result = await db["evidencias_audio"].insert_one(doc)
    audio_url = f"/juegos/evidencia-audio/{result.inserted_id}"
    return {"status": "ok", "audio_url": audio_url, "paciente_email": user["email"]}


@router.get("/evidencia-audio/{audio_id}")
async def servir_evidencia_audio(
    audio_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(require_role(["paciente", "medico", "doctor", "admin"])),
):
    """Sirve un audio guardado en MongoDB."""
    try:
        oid = ObjectId(audio_id)
    except Exception:
        return Response(status_code=404)

    doc = await db["evidencias_audio"].find_one({"_id": oid})
    if not doc:
        return Response(status_code=404)

    audio_bytes = base64.b64decode(doc["data_b64"])
    return Response(
        content=audio_bytes,
        media_type=doc.get("content_type", "audio/webm"),
        headers={"Cache-Control": "private, max-age=3600"},
    )


@router.post("/resultado", response_class=JSONResponse)
async def guardar_resultado_juego(
    db: AsyncIOMotorDatabase = Depends(get_db),
    paciente_email: str = Form(""),
    categoria: str = Form(...),
    juego: str = Form(...),
    paso_completado: int = Form(...),
    total_pasos: int = Form(...),
    completado: bool = Form(False),
    notas: str = Form(""),
    audio_transcripcion: str = Form(""),
    audio_url: str = Form(""),
    requiere_revision_audio: bool = Form(False),
    puntos: int = Form(0),
    nivel: int = Form(1),
    ruta: str = Form(""),
    user: dict = Depends(require_role(["paciente"])),
):
    """
    Guarda el resultado de un juego completado por un paciente.
    También registra en historial_actividades para que el doctor pueda ver el progreso.
    Llamado desde el frontend JS al finalizar cada juego.
    """
    paciente_email = user["email"]

    ahora = datetime.now()
    inicio_dia = datetime(ahora.year, ahora.month, ahora.day)
    fin_dia = inicio_dia + timedelta(days=1)
    total_pasos_seguro = max(1, int(total_pasos))
    paso_seguro = max(0, int(paso_completado))
    progreso_pct = int((paso_seguro / total_pasos_seguro) * 100)
    puntos_norm = max(0, min(100, int(puntos)))
    puntaje_actividad = int(round((progreso_pct * 0.65) + (puntos_norm * 0.35)))
    notas_limpias = (notas or "").strip()
    transcripcion_limpia = (audio_transcripcion or "").strip()
    audio_url_limpia = (audio_url or "").strip()
    tiene_evidencia_audio = bool(requiere_revision_audio and (audio_url_limpia or transcripcion_limpia))

    # 1. Guardar/actualizar en resultados_juegos (1 registro por paciente+juego+día)
    resultado = {
        "paciente_email": paciente_email,
        "categoria": categoria,
        "juego": juego,
        "paso_completado": paso_completado,
        "total_pasos": total_pasos,
        "completado": completado,
        "fecha": ahora,
        "fecha_dia": inicio_dia,
        "ruta": ruta,
        "notas": notas_limpias,
        "audio_transcripcion": transcripcion_limpia,
        "audio_url": audio_url_limpia,
        "requiere_revision_audio": tiene_evidencia_audio,
        "puntos": puntos,
        "progreso_pct": progreso_pct,
        "puntaje_actividad": puntaje_actividad,
        "nivel": nivel,
    }
    await db["resultados_juegos"].update_one(
        {
            "paciente_email": paciente_email,
            "categoria": categoria,
            "juego": juego,
            "fecha": {"$gte": inicio_dia, "$lt": fin_dia},
        },
        {"$set": resultado},
        upsert=True,
    )

    # 2. Si el juego fue completado, registrar en historial_actividades
    # para que el doctor pueda ver y evaluar el progreso
    if completado:
        actividad = juego.replace("_", " ").replace("-", " ").title()
        detalle_actividad = notas_limpias or transcripcion_limpia
        historial_entry = {
            "paciente_email": paciente_email,
            "categoria": categoria,
            "actividad": actividad,
            "juego": juego,
            "puntos_obtenidos": puntos if puntos > 0 else paso_completado * 10,
            "puntaje_sistema": puntaje_actividad,
            "nivel": nivel,
            "fecha": ahora,
            "detalle_actividad": detalle_actividad,
            "ruta_juego": ruta,
            "audio_transcripcion": transcripcion_limpia,
            "audio_url": audio_url_limpia,
            "requiere_revision_audio": tiene_evidencia_audio,
        }
        await db["historial_actividades"].update_one(
            {
                "paciente_email": paciente_email,
                "categoria": categoria,
                "juego": juego,
                "fecha": {"$gte": inicio_dia, "$lt": fin_dia},
            },
            {"$set": historial_entry, "$setOnInsert": {"feedback": None}},
            upsert=True,
        )
        await _crear_notificaciones_doctor(
            db,
            paciente_email=paciente_email,
            categoria=categoria,
            juego=juego,
            actividad=actividad,
            puntaje_actividad=puntaje_actividad,
            fecha=ahora,
        )

    # 3. Registrar uso diario para el calendario de actividad
    await db["sesiones_app"].update_one(
        {"paciente_email": paciente_email, "fecha": inicio_dia},
        {"$inc": {"minutos_conectado": 1}, "$setOnInsert": {"fecha": inicio_dia}},
        upsert=True,
    )

    return {
        "status": "ok",
        "completado": completado,
        "puntos": puntos,
        "audio_url": audio_url_limpia,
        "audio_transcripcion": transcripcion_limpia,
    }


@router.get("/seed-actividades", response_class=JSONResponse)
async def seed_actividades(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(require_role(["admin"])),
):
    """
    Actualiza la colección 'actividades' con los juegos reales implementados.
    Llamar una vez para sincronizar la BD con el estado actual del sistema.
    """
    juegos_por_categoria = [
        {
            "categoria": "respiracion",
            "actividades": ["Infla el globo", "El molino de Pepe"]
        },
        {
            "categoria": "fonacion",
            "actividades": ["¡Haz un gol!", "Escala musical"]
        },
        {
            "categoria": "resonancia",
            "actividades": ["Escaleras de tono", "Piano - Estrellita", "¡Veo, veo!"]
        },
        {
            "categoria": "articulacion",
            "actividades": ["Letra B", "Letra D", "Letra F", "Letra R", "Completa la palabra", "¡Acelera la moto!"]
        },
        {
            "categoria": "prosodia",
            "actividades": ["Adivina el animal", "Trabalenguas", "Relaciona la adivinanza", "Completa la canción"]
        },
        {
            "categoria": "discriminacion_auditiva",
            "actividades": ["Sonidos de animales", "Sonidos de objetos", "Arrastra al sonido"]
        },
        {
            "categoria": "practica_conmigo",
            "actividades": ["Rompecabezas", "Crea tu personaje", "Asociación de imágenes"]
        },
    ]

    # Limpiar y reinsertar
    await db["actividades"].delete_many({})
    await db["actividades"].insert_many(juegos_por_categoria)

    return {"status": "ok", "categorias": len(juegos_por_categoria), "mensaje": "Colección 'actividades' actualizada con los juegos reales"}


@router.get("/anuncio-activo", response_class=JSONResponse)
async def anuncio_activo(
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    doc = await db["contenido_admin"].find_one({}, {"anuncios_globales": 1})
    anuncios = []
    if doc:
        anuncios = doc.get("anuncios_globales", [])
    activos = [a for a in anuncios if isinstance(a, dict) and a.get("activo", True)]
    if not activos:
        return {"anuncio": None}
    anuncio = activos[-1]
    return {"anuncio": anuncio}
