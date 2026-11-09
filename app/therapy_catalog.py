"""Catálogo ampliado y controlado de actividades terapéuticas.
No modifica rutas ni datos anteriores; el doctor decide el ejercicio indicado.
"""
JUEGOS_TERAPIA = [
    ("Respiración", "Infla el globo", "/juegos/respiracion/globo"),
    ("Respiración", "El molino de Pepe", "/juegos/respiracion/molino"),
    ("Respiración", "Burbujas de aire", "/juegos/respiracion/burbujas"),
    ("Respiración", "Sopla el algodón", "/juegos/respiracion/pitillos"),
    ("Fonación", "¡Haz un gol!", "/juegos/fonacion/gol"),
    ("Fonación", "Escala musical", "/juegos/fonacion/escala"),
    ("Fonación", "Escaleras de tono", "/juegos/resonancia/escaleras"),
    ("Resonancia", "Piano interactivo", "/juegos/resonancia/piano"),
    ("Resonancia", "Veo, veo", "/juegos/resonancia/veoveo"),
    ("Resonancia", "Imita al animal", "/juegos/resonancia/imitacion"),
    ("Articulación", "Pronuncia un fonema", "/juegos/articulacion/fonemas"),
    ("Articulación", "Letras A B C D", "/juegos/articulacion/abcd"),
    ("Articulación", "5 retos de pronunciación", "/juegos/articulacion/pronunciacion-5"),
    ("Articulación", "Completa la palabra", "/juegos/articulacion/completa-palabra"),
    ("Articulación", "Acelera la moto", "/juegos/articulacion/moto-voz"),
    ("Articulación", "Letra B", "/juegos/articulacion/letra-b"),
    ("Articulación", "Letra D", "/juegos/articulacion/letra-d"),
    ("Articulación", "Letra F", "/juegos/articulacion/letra-f"),
    ("Articulación", "Letra R", "/juegos/articulacion/letra-r"),
    ("Prosodia", "Adivina el animal", "/juegos/prosodia/adivina-animal"),
    ("Prosodia", "Trabalenguas", "/juegos/prosodia/trabalenguas"),
    ("Prosodia", "Relaciona la adivinanza", "/juegos/prosodia/adivinanza-imagen"),
    ("Prosodia", "Completa la canción", "/juegos/prosodia/completa-cancion"),
    ("Discriminación", "Sonidos de animales", "/juegos/discriminacion/sonidos-animales"),
    ("Discriminación", "Sonidos de objetos", "/juegos/discriminacion/sonidos-objetos"),
    ("Discriminación", "Arrastra al sonido", "/juegos/discriminacion/arrastra-sonido"),
    ("Práctica", "Rompecabezas", "/juegos/practica/rompecabezas"),
    ("Práctica", "Crea tu personaje", "/juegos/practica/cara"),
    ("Práctica", "Asociación de imágenes", "/juegos/practica/asociacion"),
    ("Praxias", "Movimientos de la boca", "/juegos/practica/praxias"),
]
URLS_TERAPIA = {url for _, _, url in JUEGOS_TERAPIA}
FONEMAS_TERAPIA = ("M", "P", "S", "G", "R", "RR")

# Solo actividades en las que el nivel altera realmente los objetivos o el recorrido.
# Otros juegos pueden tener etapas internas (no es una dificultad a elegir).
JUEGOS_CON_NIVELES = frozenset({
    "/juegos/respiracion/globo",      # 40, 70, 100 %
    "/juegos/respiracion/burbujas",   # 5, 9, 13 soplos
    "/juegos/respiracion/pitillos",   # 5, 9, 13 avances
    "/juegos/resonancia/piano",       # 14, 28, 42 notas
    "/juegos/resonancia/veoveo",      # 3, 4, 5 retos y más distractores
    "/juegos/practica/rompecabezas",  # 3x3, 4x4, 5x5 piezas
    "/juegos/fonacion/escala",        # arranca en secuencias de ritmo diferentes
})


# ── Personalización del plan de terapia ──────────────────────────────────────
# Áreas por color: el médico puede asignar un "color" completo de juegos y el
# niño reconoce cada área por su color e icono (no necesita leer).
AREAS_TERAPIA = {
    "respiracion":    {"nombre": "Respiración",    "color": "#2e9fd6", "suave": "#e3f4fd", "icono": "globo"},
    "fonacion":       {"nombre": "Fonación",       "color": "#2bb673", "suave": "#e4f7ec", "icono": "microfono"},
    "resonancia":     {"nombre": "Resonancia",     "color": "#e9a520", "suave": "#fff4d9", "icono": "piano"},
    "articulacion":   {"nombre": "Articulación",   "color": "#e0528f", "suave": "#fde7f0", "icono": "boca"},
    "praxias":        {"nombre": "Praxias",        "color": "#e5533d", "suave": "#fde9e5", "icono": "praxias"},
    "prosodia":       {"nombre": "Prosodia",       "color": "#8e6bd6", "suave": "#f0eafc", "icono": "notas"},
    "discriminacion": {"nombre": "Discriminación", "color": "#1fa9a4", "suave": "#e1f6f5", "icono": "oreja"},
    "practica":       {"nombre": "Práctica",       "color": "#f08a3c", "suave": "#fef0e4", "icono": "rompecabezas"},
}
_AREA_POR_CATEGORIA = {
    "Respiración": "respiracion", "Fonación": "fonacion", "Resonancia": "resonancia",
    "Articulación": "articulacion", "Praxias": "praxias", "Prosodia": "prosodia",
    "Discriminación": "discriminacion", "Práctica": "practica",
}

# Dibujo que ve el niño en su camino de juegos.
# Nombre de la ilustración (app/iconos.py) que ve el niño en su camino de juegos.
ICONOS_JUEGOS = {
    "/juegos/respiracion/globo": "globo",
    "/juegos/respiracion/molino": "molino",
    "/juegos/respiracion/burbujas": "burbujas",
    "/juegos/respiracion/pitillos": "algodon",
    "/juegos/fonacion/gol": "gol",
    "/juegos/fonacion/escala": "escala",
    "/juegos/resonancia/escaleras": "escaleras",
    "/juegos/resonancia/piano": "piano",
    "/juegos/resonancia/veoveo": "lupa",
    "/juegos/resonancia/imitacion": "vaca",
    "/juegos/articulacion/fonemas": "boca",
    "/juegos/articulacion/abcd": "abc",
    "/juegos/articulacion/pronunciacion-5": "diana",
    "/juegos/articulacion/completa-palabra": "lapiz",
    "/juegos/articulacion/moto-voz": "moto",
    "/juegos/articulacion/letra-b": "letra_b",
    "/juegos/articulacion/letra-d": "letra_d",
    "/juegos/articulacion/letra-f": "letra_f",
    "/juegos/articulacion/letra-r": "letra_r",
    "/juegos/prosodia/adivina-animal": "huella",
    "/juegos/prosodia/trabalenguas": "lengua",
    "/juegos/prosodia/adivinanza-imagen": "pregunta",
    "/juegos/prosodia/completa-cancion": "notas",
    "/juegos/discriminacion/sonidos-animales": "perro",
    "/juegos/discriminacion/sonidos-objetos": "campana",
    "/juegos/discriminacion/arrastra-sonido": "arrastrar",
    "/juegos/practica/rompecabezas": "rompecabezas",
    "/juegos/practica/cara": "cara",
    "/juegos/practica/asociacion": "asociar",
    "/juegos/practica/praxias": "praxias",
}

# Letras que el médico puede priorizar y juegos que trabajan cada letra.
LETRAS_PLAN = ("M", "P", "S", "G", "R", "RR", "B", "D", "F")
_SEIS = ("M", "P", "S", "G", "R", "RR")
LETRAS_POR_JUEGO = {
    "/juegos/articulacion/fonemas": _SEIS,
    "/juegos/articulacion/pronunciacion-5": _SEIS,
    "/juegos/articulacion/moto-voz": _SEIS,
    "/juegos/practica/praxias": _SEIS + ("B", "D"),
    "/juegos/articulacion/letra-b": ("B",),
    "/juegos/articulacion/letra-d": ("D",),
    "/juegos/articulacion/letra-f": ("F",),
    "/juegos/articulacion/letra-r": ("R", "RR"),
}

# Colores favoritos para pintar el camino del niño.
COLORES_FAVORITOS = {
    "rojo": "#e53935", "naranja": "#f57c00", "amarillo": "#f2b400", "verde": "#2bb673",
    "azul": "#2e86de", "morado": "#8e44ad", "rosa": "#e84393", "turquesa": "#16a6a0",
}

# Gravedad 1–5: a mayor gravedad, más juegos al día y nivel inicial más fácil
# (más práctica con menos exigencia). El médico puede cambiar ambos valores.
GRAVEDAD = {
    1: {"nombre": "Muy leve",  "juegos": 3, "nivel": 3, "cara": "grav1"},
    2: {"nombre": "Leve",      "juegos": 4, "nivel": 2, "cara": "grav2"},
    3: {"nombre": "Moderado",  "juegos": 5, "nivel": 2, "cara": "grav3"},
    4: {"nombre": "Grave",     "juegos": 6, "nivel": 1, "cara": "grav4"},
    5: {"nombre": "Muy grave", "juegos": 8, "nivel": 1, "cara": "grav5"},
}

# Todos los juegos aceptan nivel 1–3. Los de JUEGOS_CON_NIVELES cambian su
# dificultad interna; en los demás el nivel indica cuántas veces se repite el
# juego (rondas) antes de contar como completado.
NIVELES_NOMBRE = {1: "Fácil", 2: "Medio", 3: "Reto"}


def area_de(url_o_categoria: str) -> str:
    """Clave de área para una URL del catálogo o un nombre de categoría."""
    if url_o_categoria in _AREA_POR_CATEGORIA:
        return _AREA_POR_CATEGORIA[url_o_categoria]
    for cat, _nombre, url in JUEGOS_TERAPIA:
        if url == url_o_categoria:
            return _AREA_POR_CATEGORIA.get(cat, "practica")
    return "practica"


def catalogo_visual():
    """Catálogo enriquecido para plantillas del médico y del niño."""
    return [{
        "categoria": cat, "actividad": nombre, "url": url, "area": area_de(cat),
        "icono": ICONOS_JUEGOS.get(url, "control"), "letras": list(LETRAS_POR_JUEGO.get(url, ())),
        "nivel_nativo": url in JUEGOS_CON_NIVELES,
    } for cat, nombre, url in JUEGOS_TERAPIA]
