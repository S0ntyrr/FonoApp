"""
FonoApp - Conexión a MongoDB
=============================
Maneja la conexión asíncrona a MongoDB usando Motor (driver async de PyMongo).

La conexión se abre al iniciar la aplicación (lifespan en main.py)
y se cierra al apagarla.

Uso en routers:
    from ..database import get_db
    
    @router.get("/ruta")
    async def mi_ruta(db: AsyncIOMotorDatabase = Depends(get_db)):
        resultado = await db["coleccion"].find_one({"campo": "valor"})
"""

from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

# Variable global para el cliente de MongoDB
# Se inicializa en connect_to_mongo() y se cierra en close_mongo_connection()
mongo_client: AsyncIOMotorClient | None = None


async def connect_to_mongo() -> None:
    """
    Abre la conexión global a MongoDB usando Motor (async).
    
    Se ejecuta automáticamente al iniciar la aplicación
    a través del lifespan context manager en main.py.
    
    La URI de conexión viene de settings.MONGODB_URI (archivo .env).
    """
    global mongo_client
    mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)


async def close_mongo_connection() -> None:
    """
    Cierra la conexión global a MongoDB.
    
    Se ejecuta automáticamente al apagar la aplicación
    a través del lifespan context manager en main.py.
    """
    global mongo_client
    if mongo_client is not None:
        mongo_client.close()


def get_db():
    """
    Dependency de FastAPI para obtener la base de datos.
    
    Uso en routers con Depends():
        async def mi_ruta(db: AsyncIOMotorDatabase = Depends(get_db)):
    
    Retorna la referencia a la base de datos principal (settings.MONGODB_DB_NAME).
    
    Raises:
        RuntimeError: Si la conexión no fue inicializada (no se llamó connect_to_mongo)
    """
    if mongo_client is None:
        raise RuntimeError(
            "La conexión a MongoDB no está inicializada. "
            "Asegúrate de que la aplicación se inició correctamente."
        )
    return mongo_client[settings.MONGODB_DB_NAME]
