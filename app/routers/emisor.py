from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/emisor", tags=["emisor"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/home", response_class=HTMLResponse)
async def home_emisor(request: Request):
    """
    Pantalla sencilla de inicio para el emisor (MOVIL)
    """
    return templates.TemplateResponse(
        "emisor/home.html",
        {
            "request": request,
            "titulo_pagina": "Inicio - Emisor",
        },
    )