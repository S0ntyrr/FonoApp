from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def mostrar_pantalla_login(request: Request):
    """
    Muestra la pantalla de inicio de sesión para la parte móvil.
    """
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "titulo_pagina": "Iniciar sesión",
        },
    )


@router.get("/registro", response_class=HTMLResponse)
async def mostrar_pantalla_registro(request: Request):
    """
    Muestra la pantalla de registro para nuevos usuarios móviles (emisor).
    """
    return templates.TemplateResponse(
        "auth/registro.html",
        {
            "request": request,
            "titulo_pagina": "Crear cuenta",
        },
    )


@router.post("/registro")
async def procesar_registro(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    acepta_terminos: bool = Form(False),
):
    """
    Procesa el formulario de registro para nuevos pacientes (rol 'paciente').

    Crea documentos compatibles con la estructura actual de la colección:
    {
        nombre, email, password, rol, nivel, puntos, estado
    }
    """

    if not acepta_terminos:
        return templates.TemplateResponse(
            "auth/registro.html",
            {
                "request": request,
                "titulo_pagina": "Crear cuenta",
                "error": "Debes aceptar los términos y condiciones.",
                "nombre": nombre,
                "email": email,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Verificar si ya existe un usuario con ese email
    existente = await db["usuarios"].find_one({"email": email})
    if existente:
        return templates.TemplateResponse(
            "auth/registro.html",
            {
                "request": request,
                "titulo_pagina": "Crear cuenta",
                "error": "Ya existe una cuenta con este correo.",
                "nombre": nombre,
                "email": email,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Documento compatible con tus registros actuales de tipo "paciente"
    nuevo_usuario = {
        "nombre": nombre,
        "email": email,
        "password": password,   # IMPORTANTE: en producción encriptar
        "rol": "paciente",
        "nivel": 1,
        "puntos": 0,
        "estado": "activo",
    }

    await db["usuarios"].insert_one(nuevo_usuario)

    # Después de registrarse, redirigir al login
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/login")
async def procesar_login(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
):
    """
    Procesa el formulario de login:
    - Verifica usuario y contraseña.
    - Redirige según el rol:
        admin   -> /admin/dashboard
        medico  -> /doctor/home
        paciente-> /paciente/perfil
        emisor  -> /emisor/home
    """
    usuario = await db["usuarios"].find_one({"email": email})

    if not usuario or usuario.get("password") != password:
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "titulo_pagina": "Iniciar sesión",
                "error": "Credenciales inválidas.",
                "email": email,
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    rol = usuario.get("rol", "paciente")

    if rol == "admin":
        destino = "/admin/dashboard"
    elif rol in ("medico", "doctor"):
        destino = "/doctor/home"
    elif rol == "paciente":
        destino = f"/paciente/perfil?email={email}"
    else:  # emisor u otros
        destino = "/emisor/home"

    return RedirectResponse(url=destino, status_code=status.HTTP_303_SEE_OTHER)