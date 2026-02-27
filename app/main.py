from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import connect_to_mongo, close_mongo_connection
from .routers import auth, emisor, paciente
from .web import routes_admin, routes_doctor, routes_juegos


@asynccontextmanager
async def lifespan(app):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="FonoApp",
    description="Backend de FonoApp (web y móvil).",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False)
async def raiz():
    """Redirige la raíz al login."""
    return RedirectResponse(url="/auth/login")


app.include_router(auth.router)
app.include_router(emisor.router)
app.include_router(paciente.router)
app.include_router(routes_admin.router)
app.include_router(routes_doctor.router)
app.include_router(routes_juegos.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
