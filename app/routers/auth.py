"""
FonoApp - Router de Autenticación
===================================
Maneja el login y registro de usuarios.

Rutas:
  GET  /auth/login     → Muestra el formulario de login
  POST /auth/login     → Procesa el login y redirige según el rol
  GET  /auth/registro  → Muestra el formulario de registro
  POST /auth/registro  → Crea un nuevo paciente

Flujo de login:
  1. Usuario ingresa email y contraseña
  2. Se busca en la colección 'usuarios'
  3. Se compara la contraseña (texto plano - mejorar en producción)
  4. Se redirige según el rol:
     - admin   → /admin/dashboard
     - medico  → /doctor/home
     - paciente → /paciente/perfil?email=...
     - emisor  → /emisor/home

NOTA DE SEGURIDAD:
  Las contraseñas se almacenan en texto plano.
  En producción, usar bcrypt: pip install bcrypt
  y hashear antes de guardar.

NOTA DE SESIÓN:
  No hay sesiones JWT ni cookies de sesión.
  El email del paciente se pasa como query param (?email=...).
  En producción, implementar JWT o sesiones con cookies.
"""

from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorDatabase

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
        nombre, email, password (texto plano),
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
    2. Compara la contraseña (texto plano)
    3. Redirige según el rol del usuario:
       - admin   → /admin/dashboard
       - medico  → /doctor/home?email=...
       - paciente → /paciente/perfil?email=...
       - emisor  → /emisor/home
    
    Si las credenciales son inválidas, muestra el error en el formulario.
    """
    # Buscar usuario en la BD
    usuario = await db["usuarios"].find_one({"email": email})

    # Verificar credenciales usando verify_password (soporta bcrypt y texto plano)
    stored_password = usuario.get("password", "") if usuario else ""
    if not usuario or not verify_password(password, stored_password):
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
    
    # Migración automática: si la contraseña está en texto plano, hashearla
    if usuario and not stored_password.startswith('$2b$') and not stored_password.startswith('$2a$'):
        from ..database import get_db as _get_db
        db_instance = _get_db()
        await db_instance["usuarios"].update_one(
            {"_id": usuario["_id"]},
            {"$set": {"password": hash_password(password)}}
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

    # Crear la respuesta de redirección
    response = RedirectResponse(url=destino, status_code=status.HTTP_303_SEE_OTHER)
    
    # Guardar el email en una cookie de sesión (no segura, solo para desarrollo)
    # La cookie 'usuario_email' permite que los juegos identifiquen al usuario
    # sin necesidad de pasar el email por URL en cada página
    response.set_cookie(
        key="usuario_email",
        value=email_usuario,
        max_age=86400,  # 24 horas
        httponly=False,  # Accesible desde JavaScript para los juegos
        samesite="lax",
    )
    response.set_cookie(
        key="usuario_rol",
        value=rol,
        max_age=86400,
        httponly=False,
        samesite="lax",
    )
    
    return response
