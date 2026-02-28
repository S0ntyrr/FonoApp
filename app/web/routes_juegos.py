from datetime import datetime

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database import get_db

router = APIRouter(prefix="/juegos", tags=["juegos"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def hub_juegos(request: Request):
    """
    Hub principal de juegos de Fonoaudiología.
    Accesible por admin, doctor y paciente.
    """
    return templates.TemplateResponse(
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
        "juegos/articulacion/index.html",
        {"request": request, "titulo_pagina": "Articulación"},
    )

@router.get("/articulacion/letra-b", response_class=HTMLResponse)
async def articulacion_letra_b(request: Request):
    return templates.TemplateResponse(
        "juegos/articulacion/letra_b.html",
        {"request": request, "titulo_pagina": "Articulación - Letra B"},
    )

@router.get("/articulacion/letra-d", response_class=HTMLResponse)
async def articulacion_letra_d(request: Request):
    return templates.TemplateResponse(
        "juegos/articulacion/letra_d.html",
        {"request": request, "titulo_pagina": "Articulación - Letra D"},
    )

@router.get("/articulacion/letra-f", response_class=HTMLResponse)
async def articulacion_letra_f(request: Request):
    return templates.TemplateResponse(
        "juegos/articulacion/letra_f.html",
        {"request": request, "titulo_pagina": "Articulación - Letra F"},
    )

@router.get("/articulacion/letra-r", response_class=HTMLResponse)
async def articulacion_letra_r(request: Request):
    return templates.TemplateResponse(
        "juegos/articulacion/letra_r.html",
        {"request": request, "titulo_pagina": "Articulación - Letra R"},
    )


@router.get("/articulacion/completa-palabra", response_class=HTMLResponse)
async def articulacion_completa_palabra(request: Request):
    return templates.TemplateResponse(
        "juegos/articulacion/completa_palabra.html",
        {"request": request, "titulo_pagina": "Completa la palabra"},
    )

@router.get("/articulacion/moto-voz", response_class=HTMLResponse)
async def articulacion_moto_voz(request: Request):
    return templates.TemplateResponse(
        "juegos/articulacion/moto_voz.html",
        {"request": request, "titulo_pagina": "¡Acelera la moto!"},
    )


# ─── PROSODIA ─────────────────────────────────────────────────────────────────

@router.get("/prosodia", response_class=HTMLResponse)
async def hub_prosodia(request: Request):
    return templates.TemplateResponse(
        "juegos/prosodia/index.html",
        {"request": request, "titulo_pagina": "Prosodia"},
    )

@router.get("/prosodia/adivina-animal", response_class=HTMLResponse)
async def prosodia_adivina_animal(request: Request):
    return templates.TemplateResponse(
        "juegos/prosodia/adivina_animal.html",
        {"request": request, "titulo_pagina": "Adivina el animal"},
    )

@router.get("/prosodia/trabalenguas", response_class=HTMLResponse)
async def prosodia_trabalenguas(request: Request):
    return templates.TemplateResponse(
        "juegos/prosodia/trabalenguas.html",
        {"request": request, "titulo_pagina": "Trabalenguas"},
    )

@router.get("/prosodia/adivinanza-imagen", response_class=HTMLResponse)
async def prosodia_adivinanza_imagen(request: Request):
    return templates.TemplateResponse(
        "juegos/prosodia/adivinanza_imagen.html",
        {"request": request, "titulo_pagina": "Relaciona la adivinanza"},
    )

@router.get("/prosodia/completa-cancion", response_class=HTMLResponse)
async def prosodia_completa_cancion(request: Request):
    return templates.TemplateResponse(
        "juegos/prosodia/completa_cancion.html",
        {"request": request, "titulo_pagina": "Completa la canción"},
    )


# ─── DISCRIMINACIÓN AUDITIVA ──────────────────────────────────────────────────

@router.get("/discriminacion", response_class=HTMLResponse)
async def hub_discriminacion(request: Request):
    return templates.TemplateResponse(
        "juegos/discriminacion/index.html",
        {"request": request, "titulo_pagina": "Discriminación Auditiva"},
    )

@router.get("/discriminacion/sonidos-animales", response_class=HTMLResponse)
async def discriminacion_sonidos_animales(request: Request):
    return templates.TemplateResponse(
        "juegos/discriminacion/sonidos_animales.html",
        {"request": request, "titulo_pagina": "Sonidos de animales"},
    )

@router.get("/discriminacion/sonidos-objetos", response_class=HTMLResponse)
async def discriminacion_sonidos_objetos(request: Request):
    return templates.TemplateResponse(
        "juegos/discriminacion/sonidos_objetos.html",
        {"request": request, "titulo_pagina": "Sonidos de objetos"},
    )

@router.get("/discriminacion/arrastra-sonido", response_class=HTMLResponse)
async def discriminacion_arrastra_sonido(request: Request):
    return templates.TemplateResponse(
        "juegos/discriminacion/arrastra_sonido.html",
        {"request": request, "titulo_pagina": "Arrastra al sonido"},
    )


# ─── RESULTADO DE JUEGO ───────────────────────────────────────────────────────

@router.post("/resultado", response_class=JSONResponse)
async def guardar_resultado_juego(
    db: AsyncIOMotorDatabase = Depends(get_db),
    paciente_email: str = Form(...),
    categoria: str = Form(...),
    juego: str = Form(...),
    paso_completado: int = Form(...),
    total_pasos: int = Form(...),
    completado: bool = Form(False),
    notas: str = Form(""),
    puntos: int = Form(0),
    nivel: int = Form(1),
):
    """
    Guarda el resultado de un juego completado por un paciente.
    También registra en historial_actividades para que el doctor pueda ver el progreso.
    Llamado desde el frontend JS al finalizar cada juego.
    """
    ahora = datetime.utcnow()

    # 1. Guardar en resultados_juegos (detalle técnico del juego)
    resultado = {
        "paciente_email": paciente_email,
        "categoria": categoria,
        "juego": juego,
        "paso_completado": paso_completado,
        "total_pasos": total_pasos,
        "completado": completado,
        "fecha": ahora,
        "notas": notas,
        "puntos": puntos,
        "nivel": nivel,
    }
    await db["resultados_juegos"].insert_one(resultado)

    # 2. Si el juego fue completado, registrar en historial_actividades
    # para que el doctor pueda ver y evaluar el progreso
    if completado:
        historial_entry = {
            "paciente_email": paciente_email,
            "categoria": categoria,
            "actividad": juego.replace("_", " ").replace("-", " ").title(),
            "puntos_obtenidos": puntos if puntos > 0 else paso_completado * 10,
            "nivel": nivel,
            "fecha": ahora,
            "feedback": None,  # El doctor lo completará después
        }
        await db["historial_actividades"].insert_one(historial_entry)

    return {"status": "ok", "completado": completado, "puntos": puntos}


@router.get("/seed-actividades", response_class=JSONResponse)
async def seed_actividades(db: AsyncIOMotorDatabase = Depends(get_db)):
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
