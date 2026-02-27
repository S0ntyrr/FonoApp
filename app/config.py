from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """
    Config general de la aplicación FonoApp.
    Usa pydantic-settings
    """
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "fono_app"

    class Config:
        env_file = ".env"


settings = AppSettings()