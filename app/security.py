"""
FonoApp - Utilidades de Seguridad
===================================
Módulo centralizado para manejo de seguridad:
- Hash de contraseñas con bcrypt
- Verificación de contraseñas hasheadas
- Lectura de sesión firmada
- Protección de rutas por rol
"""

import re

import bcrypt
from fastapi import Request, HTTPException, status

EMAIL_UNIQUE_INDEX_NAME = "email_unique_case_insensitive"
EMAIL_UNIQUE_INDEX_OPTIONS = {
    "name": EMAIL_UNIQUE_INDEX_NAME,
    "unique": True,
    "collation": {"locale": "en", "strength": 2},
}


def normalize_email(email: str | None) -> str:
    """Normaliza un correo para que el sistema sea insensible a mayúsculas."""
    if not email:
        return ""
    return str(email).strip().lower()


def email_match_filter(email: str | None) -> dict:
    """Genera un filtro MongoDB para buscar emails sin importar mayúsculas/minúsculas."""
    normalized = normalize_email(email)
    if not normalized:
        return {}
    return {"email": {"$regex": rf"^{re.escape(normalized)}$", "$options": "i"}}


def hash_password(password: str) -> str:
    """
    Genera un hash seguro de la contraseña usando bcrypt.
    
    Args:
        password: Contraseña en texto plano
    
    Returns:
        Hash de la contraseña (string)
    
    Ejemplo:
        hashed = hash_password("mi_contraseña")
        # Resultado: "$2b$12$..."
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        password: Contraseña en texto plano a verificar
        hashed: Hash almacenado en la BD
    
    Returns:
        True si la contraseña es correcta, False si no
    """
    if not hashed:
        return False
    if not (hashed.startswith("$2a$") or hashed.startswith("$2b$") or hashed.startswith("$2y$")):
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def get_current_user(request: Request) -> dict:
    """
    Obtiene los datos del usuario actual desde la sesión firmada.
    
    Returns:
        dict con 'email' y 'rol' del usuario, o None si no hay sesión
    """
    user_data = request.session.get("user")
    if not isinstance(user_data, dict):
        return None

    email = user_data.get("email")
    rol = user_data.get("rol")
    if not email or not rol:
        return None

    return {"email": email, "rol": rol}


def require_role(allowed_roles: list):
    """
    Dependency de FastAPI para proteger rutas por rol.
    
    Uso:
        @router.get("/admin/dashboard")
        async def dashboard(user=Depends(require_role(["admin"]))):
            ...
    
    Args:
        allowed_roles: Lista de roles permitidos (ej: ["admin"], ["admin", "medico"])
    
    Returns:
        Función dependency que verifica el rol del usuario
    
    Raises:
        HTTPException 401: Si no hay sesión activa
        HTTPException 403: Si el rol no tiene permiso
    """
    def check_role(request: Request):
        user = get_current_user(request)
        
        if not user:
            # No hay sesión → redirigir al login
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Debes iniciar sesión para acceder a esta página.",
                headers={"Location": "/auth/login"}
            )
        
        if user["rol"] not in allowed_roles:
            # Rol no autorizado
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso para acceder a esta sección. "
                       f"Se requiere rol: {', '.join(allowed_roles)}."
            )
        
        return user
    
    return check_role
