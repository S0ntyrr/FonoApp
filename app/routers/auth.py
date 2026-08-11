"""
FonoApp - Router de Autenticación
===================================
Maneja el login y registro de usuarios con seguridad mejorada.

ARQUITECTURA DE SEGURIDAD:
  
  REGISTRO (nuevos usuarios):
    - Las contraseñas se HASHEAN INMEDIATAMENTE con bcrypt
    - No se almacenan nunca en texto plano
    - Hash con 12 rounds de complejidad
  
  LOGIN:
    - Verifica únicamente hashes bcrypt válidos
    - Usa sesión firmada del servidor (SessionMiddleware)
  
  ÍNDICES:
    - Email indexado (UNIQUE) para búsquedas rápidas (~50ms)
    - Mejora rendimiento de login

RUTAS:
  GET  /auth/login              → Muestra el formulario de login
  POST /auth/login              → Procesa el login
  GET  /auth/registro           → Muestra el formulario de registro
  POST /auth/registro           → Crea nuevo paciente (contraseña ya hasheada)
  GET  /auth/logout             → Cierra sesión
  POST /auth/logout             → Cierra sesión
  GET  /auth/terminos-condiciones → Muestra la página de términos y condiciones

FLUJO DE LOGIN:
  1. Usuario ingresa email y contraseña
  2. Se busca usuario en MongoDB (con índice rápido)
  3. Se verifica contraseña bcrypt
  4. Se guarda sesión firmada
  5. Se redirige según el rol

FLUJO DE REGISTRO:
  1. Usuario completa formulario
  2. Se valida email único
  3. Se hashea la contraseña inmediatamente
  4. Se almacena en BD (SIEMPRE hasheada)
  5. Se redirige a login

NOTES:
  - La cookie de sesión es HttpOnly y firmada.
"""

from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..config import settings
from ..database import get_db
from ..security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def mostrar_pantalla_login(request: Request):
    """
    Muestra la pantalla de inicio de sesión.
    
    Template: auth/login.html
    Accesible por todos los usuarios (no requiere autenticación).
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
    Muestra la pantalla de registro para nuevos pacientes.
    
    Template: auth/registro.html
    Solo los pacientes pueden registrarse por sí mismos.
    Los médicos y admins son creados por el administrador.
    """
    return templates.TemplateResponse(
        "auth/registro.html",
        {
            "request": request,
            "titulo_pagina": "Crear cuenta",
        },
    )


@router.get("/terminos-condiciones", response_class=HTMLResponse)
async def mostrar_terminos_condiciones(request: Request):
    """
    Muestra la página de términos y condiciones de FonoApp.
    
    Template: auth/terminos_condiciones.html
    Accesible por todos (especialmente desde el formulario de registro).
    Se puede abrir en modal o en nueva pestaña.
    """
    return templates.TemplateResponse(
        "auth/terminos_condiciones.html",
        {
            "request": request,
            "titulo_pagina": "Términos y Condiciones",
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
    Procesa el formulario de registro de nuevos pacientes.
    
    Validaciones:
    - Debe aceptar los términos y condiciones
    - El email no debe estar ya registrado
    
    Al registrarse exitosamente:
    - Crea un documento en la colección 'usuarios' con rol='paciente'
    - Redirige al login para que el usuario inicie sesión
    
    Campos del documento creado:
    {
        nombre, email, password (bcrypt),
        rol: "paciente", nivel: 1, puntos: 0, estado: "activo"
    }
    """
    # Validar aceptación de términos
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

    # Verificar si el email ya está registrado
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

    # Crear el nuevo paciente en la BD con contraseña hasheada
    nuevo_usuario = {
        "nombre": nombre,
        "email": email,
        "password": hash_password(password),  # Hash seguro con bcrypt
        "rol": "paciente",
        "nivel": 1,
        "puntos": 0,
        "estado": "activo",
    }
    await db["usuarios"].insert_one(nuevo_usuario)

    # Redirigir al login después del registro exitoso
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/login")
async def procesar_login(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
):
    """
    Procesa el formulario de login.
    
    Flujo:
    1. Busca el usuario por email en la colección 'usuarios'
    2. Verifica la contraseña bcrypt
    3. Redirige según el rol del usuario:
       - admin   → /admin/dashboard
       - medico  → /doctor/home?email=...
       - paciente → /paciente/perfil?email=...
       - emisor  → /emisor/home
    """
    # Buscar usuario en la BD (indexed por email para búsquedas rápidas)
    usuario = await db["usuarios"].find_one({"email": email})

    # Verificar que exista el usuario
    if not usuario:
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "titulo_pagina": "Iniciar sesión",
                "error": "Credenciales inválidas. Verifica tu correo y contraseña.",
                "email": email,
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    
    # Verificar contraseña
    stored_password = usuario.get("password", "")
    if not verify_password(password, stored_password):
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "titulo_pagina": "Iniciar sesión",
                "error": "Credenciales inválidas. Verifica tu correo y contraseña.",
                "email": email,
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    
    # Determinar destino según el rol
    rol = usuario.get("rol", "paciente")
    email_usuario = usuario.get("email", email)

    if rol == "admin":
        destino = "/admin/dashboard"
    elif rol in ("medico", "doctor"):
        destino = f"/doctor/home?email={email_usuario}"
    elif rol == "paciente":
        destino = f"/paciente/perfil?email={email_usuario}"
    else:
        destino = "/emisor/home"

    request.session.clear()
    request.session["user"] = {"email": email_usuario, "rol": rol}

    response = RedirectResponse(url=destino, status_code=status.HTTP_303_SEE_OTHER)
    return response


@router.get("/logout")
async def cerrar_sesion_get(request: Request):
    request.session.clear()
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(settings.SESSION_COOKIE_NAME)
    return response


@router.post("/logout")
async def cerrar_sesion_post(request: Request):
    request.session.clear()
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(settings.SESSION_COOKIE_NAME)
    return response
