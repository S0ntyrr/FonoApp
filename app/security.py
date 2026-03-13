"""
FonoApp - Utilidades de Seguridad
===================================
Módulo centralizado para manejo de seguridad:
- Hash de contraseñas con bcrypt
- Verificación de contraseñas
- Verificación de roles de usuario
- Protección de rutas por rol

Uso en routers:
    from .security import hash_password, verify_password, get_current_user_role

IMPORTANTE: Las contraseñas existentes en la BD están en texto plano.
Al hacer login, si la contraseña no está hasheada, se hashea automáticamente.
Esto permite migración gradual sin romper cuentas existentes.
"""

import bcrypt
from fastapi import Request, HTTPException, status


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
    
    También acepta contraseñas en texto plano (para compatibilidad
    con cuentas creadas antes de implementar bcrypt).
    
    Args:
        password: Contraseña en texto plano a verificar
        hashed: Hash almacenado en la BD (o contraseña en texto plano)
    
    Returns:
        True si la contraseña es correcta, False si no
    """
    # Verificar si el hash es un hash bcrypt (empieza con $2b$ o $2a$)
    if hashed.startswith('$2b$') or hashed.startswith('$2a$'):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    else:
        # Compatibilidad con contraseñas en texto plano (cuentas antiguas)
        # En producción, forzar el cambio de contraseña
        return password == hashed


def get_current_user(request: Request) -> dict:
    """
    Obtiene los datos del usuario actual desde las cookies de sesión.
    
    Returns:
        dict con 'email' y 'rol' del usuario, o None si no hay sesión
    """
    email = request.cookies.get("usuario_email")
    rol = request.cookies.get("usuario_rol")
    
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
