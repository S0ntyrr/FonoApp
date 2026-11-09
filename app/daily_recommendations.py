"""Selección reproducible de juegos diarios. No toca MongoDB ni el RNG global."""
from hashlib import sha256
from random import Random


def elegir_actividades(catalogo, fecha, email, cantidad=4):
    """Una actividad por categoría, idéntica durante el día para este paciente."""
    semilla = sha256(f"{fecha:%Y-%m-%d}|{email.strip().lower()}".encode("utf-8")).digest()
    aleatorio = Random(semilla)
    categorias = sorted({a["categoria"] for a in catalogo})
    resultado = []
    for categoria in aleatorio.sample(categorias, min(cantidad, len(categorias))):
        opciones = sorted((a for a in catalogo if a["categoria"] == categoria), key=lambda a: a["actividad"])
        if opciones:
            resultado.append(aleatorio.choice(opciones))
    return resultado


# ── Plan personalizado por el médico ─────────────────────────────────────────
from urllib.parse import urlencode

from .therapy_catalog import (
    AREAS_TERAPIA, COLORES_FAVORITOS, GRAVEDAD, LETRAS_PLAN, URLS_TERAPIA, catalogo_visual,
)

MODOS_JUEGO = ("auto", "siempre", "nunca")


def normalizar_plan(datos: dict | None) -> dict:
    """Devuelve un plan válido (valores fuera de rango se corrigen)."""
    datos = dict(datos or {})
    try:
        gravedad = int(datos.get("gravedad") or 2)
    except (TypeError, ValueError):
        gravedad = 2
    gravedad = max(1, min(5, gravedad))

    def entero(clave, minimo, maximo):
        try:
            valor = int(datos.get(clave) or 0)
        except (TypeError, ValueError):
            return 0
        return valor if minimo <= valor <= maximo else 0

    juegos = []
    vistos = set()
    for j in datos.get("juegos") or []:
        url = (j or {}).get("url")
        if url not in URLS_TERAPIA or url in vistos:
            continue
        vistos.add(url)
        modo = j.get("modo") if j.get("modo") in MODOS_JUEGO else "auto"
        try:
            nivel = int(j.get("nivel") or 0)
        except (TypeError, ValueError):
            nivel = 0
        if modo != "auto" or nivel in (1, 2, 3):
            juegos.append({"url": url, "modo": modo, "nivel": nivel if nivel in (1, 2, 3) else 0})
    color = datos.get("color") if datos.get("color") in COLORES_FAVORITOS else ""
    return {
        "gravedad": gravedad,
        "nivel": entero("nivel", 1, 3),                # 0 = automático según gravedad
        "juegos_por_dia": entero("juegos_por_dia", 1, 12),  # 0 = automático
        "letras": [l for l in LETRAS_PLAN if l in (datos.get("letras") or [])],
        "areas": [a for a in AREAS_TERAPIA if a in (datos.get("areas") or [])],
        "color": color,
        "juegos": juegos,
        "nota_familia": str(datos.get("nota_familia") or "")[:300].strip(),
    }


def nivel_efectivo(plan: dict) -> int:
    return plan.get("nivel") or GRAVEDAD[plan["gravedad"]]["nivel"]


def cantidad_efectiva(plan: dict) -> int:
    return plan.get("juegos_por_dia") or GRAVEDAD[plan["gravedad"]]["juegos"]


def armar_plan_del_dia(plan: dict | None, fecha, email: str) -> list[dict]:
    """Juegos del día según gravedad, letras, colores y juegos fijados por el médico.

    Determinista por paciente y fecha: el niño ve el mismo camino todo el día.
    Orden: 1) juegos marcados «siempre», 2) juegos de las letras elegidas,
    3) el resto repartido entre las áreas (colores) elegidas.
    """
    plan = normalizar_plan(plan)
    semilla = sha256(f"plan|{fecha:%Y-%m-%d}|{email.strip().lower()}".encode("utf-8")).digest()
    azar = Random(semilla)
    catalogo = {j["url"]: j for j in catalogo_visual()}
    config = {j["url"]: j for j in plan["juegos"]}
    nunca = {u for u, c in config.items() if c["modo"] == "nunca"}
    siempre = [u for u, c in config.items() if c["modo"] == "siempre"]
    letras = plan["letras"]
    areas = set(plan["areas"])
    cantidad = max(cantidad_efectiva(plan), len(siempre))

    elegidos: list[str] = [u for u in siempre if u in catalogo]
    disponibles = [u for u in catalogo if u not in nunca and u not in elegidos
                   and (not areas or catalogo[u]["area"] in areas)]

    # Prioridad a juegos que trabajan las letras elegidas (hasta la mitad del día o más).
    if letras:
        de_letras = sorted(u for u in disponibles if set(catalogo[u]["letras"]) & set(letras))
        azar.shuffle(de_letras)
        cupo = max(1, (cantidad + 1) // 2)
        for u in de_letras[:cupo]:
            if len(elegidos) < cantidad:
                elegidos.append(u)
        disponibles = [u for u in disponibles if u not in elegidos]

    # Resto: turnos entre áreas para que haya variedad de colores.
    por_area: dict[str, list[str]] = {}
    for u in sorted(disponibles):
        por_area.setdefault(catalogo[u]["area"], []).append(u)
    for lista in por_area.values():
        azar.shuffle(lista)
    orden_areas = sorted(por_area)
    azar.shuffle(orden_areas)
    while len(elegidos) < cantidad and any(por_area.values()):
        for area in orden_areas:
            if por_area[area] and len(elegidos) < cantidad:
                elegidos.append(por_area[area].pop())

    nivel_plan = nivel_efectivo(plan)
    resultado = []
    for i, url in enumerate(elegidos):
        juego = dict(catalogo[url])
        nivel = config.get(url, {}).get("nivel") or nivel_plan
        letras_juego = [l for l in letras if l in juego["letras"]] or juego["letras"][:1]
        fonema = letras_juego[(i + fecha.toordinal()) % len(letras_juego)] if letras_juego else ""
        params = {"nivel": nivel}
        if fonema:
            params["fonema"] = fonema
        juego.update({
            "nivel": nivel, "fonema": fonema, "href": f"{url}?{urlencode(params)}",
            "area_color": AREAS_TERAPIA[juego["area"]]["color"],
            "area_suave": AREAS_TERAPIA[juego["area"]]["suave"],
            "fijo": url in siempre,
        })
        resultado.append(juego)
    return resultado
