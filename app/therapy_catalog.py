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
