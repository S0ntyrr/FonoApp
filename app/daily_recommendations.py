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
