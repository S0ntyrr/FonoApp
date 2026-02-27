from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

mongo_client: AsyncIOMotorClient | None = None


async def connect_to_mongo() -> None:
    """
    Abre la conexión global a MongoDB usando Motor.
    Se ejecuta al iniciar la aplicación.
    """
    global mongo_client
    mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)


async def close_mongo_connection() -> None:
    """
    Cierra la conexión global a MongoDB.
    Se ejecuta al apagar la aplicación.
    """
    global mongo_client
    if mongo_client is not None:
        mongo_client.close()


def get_db():
    """
    Devuelve la referencia a la base de datos principal.
    """
    if mongo_client is None:
        raise RuntimeError("La conexión a MongoDB no está inicializada.")
    return mongo_client[settings.MONGODB_DB_NAME]