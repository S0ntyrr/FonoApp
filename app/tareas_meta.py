"""Metas de las tareas asignadas por el médico: X intentos o X minutos.

Mientras un paciente tenga tareas pendientes, sus juegos automáticos del día
quedan bloqueados; al cumplir la meta la tarea se completa y se desbloquean.
Las tareas antiguas (sin meta) equivalen a «1 intento».
"""
from datetime import datetime

TIPOS_META = ("intentos", "tiempo")
LIMITES_META = {"intentos": (1, 20), "tiempo": (1, 60)}  # intentos / minutos
MAX_SEGUNDOS_POR_PULSO = 30


def validar_meta(tipo: str, valor) -> tuple[str, int] | None:
    """Devuelve (tipo, valor) válidos o None si están fuera de rango."""
    if tipo not in TIPOS_META:
        return None
    try:
        valor = int(valor)
    except (TypeError, ValueError):
        return None
    minimo, maximo = LIMITES_META[tipo]
    return (tipo, valor) if minimo <= valor <= maximo else None


def meta_de(tarea: dict) -> tuple[str, int]:
    tipo = tarea.get("meta_tipo") if tarea.get("meta_tipo") in TIPOS_META else "intentos"
    try:
        valor = int(tarea.get("meta_valor") or 1)
    except (TypeError, ValueError):
        valor = 1
    minimo, maximo = LIMITES_META[tipo]
    return tipo, max(minimo, min(maximo, valor))


def progreso_de(tarea: dict) -> dict:
    """Avance legible para plantillas y para el juego (0..1 en «fraccion»)."""
    tipo, meta = meta_de(tarea)
    intentos = int(tarea.get("progreso_intentos") or 0)
    segundos = int(tarea.get("progreso_segundos") or 0)
    if tipo == "tiempo":
        hecho, total = segundos, meta * 60
        texto = f"{segundos // 60}/{meta} min"
    else:
        hecho, total = intentos, meta
        texto = f"{intentos}/{meta} intentos"
    completada = tarea.get("estado") == "completada"
    return {
        "tipo": tipo, "meta": meta, "intentos": intentos, "segundos": segundos,
        "fraccion": 1.0 if completada else min(1.0, hecho / max(1, total)),
        "texto": texto, "completada": completada,
    }


def cambios_por_intento(tarea: dict, ahora: datetime, intento_id: str) -> dict:
    """$set a aplicar cuando el niño completa una partida de la tarea."""
    tipo, meta = meta_de(tarea)
    intentos = int(tarea.get("progreso_intentos") or 0) + 1
    cambios = {"progreso_intentos": intentos, "ultimo_intento_id": intento_id}
    if tipo == "intentos" and intentos >= meta:
        cambios.update({"estado": "completada", "completada_en": ahora, "intento_id": intento_id})
    return cambios


def cambios_por_tiempo(tarea: dict, ahora: datetime, segundos_cliente) -> dict:
    """$set para un pulso de tiempo jugado.

    El servidor no confía en el cliente: suma como máximo 30 s por pulso y
    nunca más que el tiempo real transcurrido desde el pulso anterior.
    """
    try:
        segundos = int(segundos_cliente)
    except (TypeError, ValueError):
        segundos = 0
    segundos = max(0, min(MAX_SEGUNDOS_POR_PULSO, segundos))
    ultimo = tarea.get("ultimo_pulso")
    if isinstance(ultimo, datetime):
        transcurrido = (ahora - ultimo).total_seconds()
        segundos = int(max(0, min(segundos, transcurrido + 2)))
    total = int(tarea.get("progreso_segundos") or 0) + segundos
    cambios = {"progreso_segundos": total, "ultimo_pulso": ahora}
    tipo, meta = meta_de(tarea)
    if tipo == "tiempo" and total >= meta * 60:
        cambios.update({"estado": "completada", "completada_en": ahora})
    return cambios
