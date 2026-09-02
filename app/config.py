"""
FonoApp - Configuracion de la app
=========================================
Usa pydantic-settings para cargar variables de entorno desde el archivo.

Variables de entorno requeridas (en .env):
  MONGODB_URI      - URI de conexión a MongoDB Atlas
                     Ejemplo: mongodb+srv://user:pass@cluster.mongodb.net/
  MONGODB_DB_NAME  - Nombre de la base de datos
                     Ejemplo: tesis
"""

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """
    Configuracion general.
    
    Los valores se cargan automáticamente desde:
    1. Variables de entorno del sistema
    2. Archivo .env en la raíz del proyecto
    
    Las credenciales de MongoDB deben declararse explícitamente. Esto evita
    que un despliegue sin variables intente conectar a localhost.
     """
    MONGODB_URI: str
    MONGODB_DB_NAME: str = "tesis"
    SESSION_SECRET_KEY: str = "change-this-in-production"
    SESSION_COOKIE_NAME: str = "fonoapp_session"
    SESSION_MAX_AGE: int = 86400
    SESSION_HTTPS_ONLY: bool = True
    APP_TIMEZONE: str = "America/Bogota"
    MAX_IMAGE_UPLOAD_BYTES: int = 5 * 1024 * 1024
    MAX_VIDEO_UPLOAD_BYTES: int = 25 * 1024 * 1024

    class Config:
        env_file = ".env"


# Instancia global de configuración
# Importar desde otros módulos: from .config import settings
settings = AppSettings()
