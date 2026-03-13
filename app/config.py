"""
FonoApp - Configuración de la aplicación
=========================================
Usa pydantic-settings para cargar variables de entorno desde el archivo .env.

Variables de entorno requeridas (en .env):
  MONGODB_URI      - URI de conexión a MongoDB Atlas
                     Ejemplo: mongodb+srv://user:pass@cluster.mongodb.net/
  MONGODB_DB_NAME  - Nombre de la base de datos
                     Ejemplo: tesis

El archivo .env debe estar en la raíz del proyecto y NO debe subirse al repositorio.
"""

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """
    Configuración general de FonoApp.
    
    Los valores se cargan automáticamente desde:
    1. Variables de entorno del sistema
    2. Archivo .env en la raíz del proyecto
    
    Los valores por defecto son para desarrollo local con MongoDB local.
    En producción, siempre usar variables de entorno reales.
    """
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "fono_app"

    class Config:
        env_file = ".env"


# Instancia global de configuración
# Importar desde otros módulos: from .config import settings
settings = AppSettings()
