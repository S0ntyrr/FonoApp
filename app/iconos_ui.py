"""Dibujos de interfaz y bocas animadas por fonema (viewBox 0 0 64 64).

Las clases fa-* se animan con static/css/fono-anim.css:
- Las bocas de fonemas (boca_m, boca_p, …) se animan siempre: son demostraciones.
- El resto solo dentro de un contenedor .animar (p. ej. la guía «Ver ejemplo»).
"""

O = "#1f3347"

UI = {
    "ojos": '<ellipse cx="20" cy="32" rx="14" ry="17" fill="#fff" stroke="' + O + '" stroke-width="3"/><ellipse cx="44" cy="32" rx="14" ry="17" fill="#fff" stroke="' + O + '" stroke-width="3"/>'
            '<g class="fa-mira"><circle cx="22" cy="34" r="7" fill="' + O + '"/><circle cx="46" cy="34" r="7" fill="' + O + '"/><circle cx="24" cy="31" r="2.4" fill="#fff"/><circle cx="48" cy="31" r="2.4" fill="#fff"/></g>',
    "fiesta": '<path d="M8 58l12-36 22 22z" fill="#f2b400"/><path d="M14 40l14 14M17 31l17 17" stroke="#e53935" stroke-width="3"/>'
              '<g class="fa-sube"><circle cx="40" cy="14" r="3" fill="#e0528f"/><circle cx="52" cy="24" r="3" fill="#2e86de"/><circle cx="48" cy="8" r="2.5" fill="#2bb673"/><circle cx="56" cy="40" r="2.5" fill="#f57c00"/>'
              '<path d="M32 10q4 6 0 10M44 30q6-2 8 4" stroke="#8e6bd6" stroke-width="3" fill="none" stroke-linecap="round"/></g>',
    "calendario": '<rect x="6" y="10" width="52" height="48" rx="7" fill="#fff" stroke="#9fb3c4" stroke-width="2.5"/><path d="M6 17q0-7 7-7h38q7 0 7 7v7H6z" fill="#e53935"/>'
                  '<path d="M18 4v12M46 4v12" stroke="' + O + '" stroke-width="4" stroke-linecap="round"/>'
                  '<g fill="#cfd8e2"><rect x="13" y="30" width="8" height="7" rx="1.5"/><rect x="28" y="30" width="8" height="7" rx="1.5"/><rect x="43" y="30" width="8" height="7" rx="1.5"/><rect x="13" y="43" width="8" height="7" rx="1.5"/><rect x="43" y="43" width="8" height="7" rx="1.5"/></g>'
                  '<rect x="28" y="43" width="8" height="7" rx="1.5" fill="#2bb673"/>',
    "dialogo": '<path d="M8 8h48a6 6 0 016 6v26a6 6 0 01-6 6H26L14 58V46H8a6 6 0 01-6-6V14a6 6 0 016-6z" fill="#2e86de"/>'
               '<g fill="#fff"><circle cx="18" cy="27" r="4"/><circle cx="32" cy="27" r="4"/><circle cx="46" cy="27" r="4"/></g>',
    "enlace": '<g fill="none" stroke="#2e86de" stroke-width="6" stroke-linecap="round"><path d="M28 36l-8 8a8 8 0 01-12-12l8-8"/><path d="M36 28l8-8a8 8 0 0112 12l-8 8"/><path d="M24 40l16-16"/></g>',
    "refrescar": '<g class="fa-gira"><path d="M50 26A20 20 0 1 0 52 40" fill="none" stroke="#2e86de" stroke-width="6" stroke-linecap="round"/><path d="M42 16l12 10-14 5z" fill="#2e86de"/></g>',
    "error": '<circle cx="32" cy="32" r="27" fill="#e53935"/><path d="M21 21l22 22M43 21L21 43" stroke="#fff" stroke-width="7" stroke-linecap="round"/>',
    "ok": '<circle cx="32" cy="32" r="27" fill="#2bb673"/><path d="M18 33l9 9 19-19" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>',
    "grafica": '<path d="M6 58h52" stroke="' + O + '" stroke-width="3" stroke-linecap="round"/><rect x="10" y="34" width="10" height="22" rx="2" fill="#2e86de"/>'
               '<rect x="27" y="20" width="10" height="36" rx="2" fill="#2bb673"/><rect x="44" y="8" width="10" height="48" rx="2" fill="#f2b400"/>',
    "tendencia": '<path d="M6 50l16-16 10 10 22-24" fill="none" stroke="#2bb673" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/><path d="M40 14h16v16z" fill="#2bb673"/><path d="M6 58h52" stroke="#9fb3c4" stroke-width="3"/>',
    "tendencia_baja": '<path d="M6 14l16 16 10-10 22 24" fill="none" stroke="#e53935" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/><path d="M40 50h16V34z" fill="#e53935"/><path d="M6 58h52" stroke="#9fb3c4" stroke-width="3"/>',
    "audifonos": '<path d="M10 40V32a22 22 0 0144 0v8" fill="none" stroke="' + O + '" stroke-width="5"/><rect x="6" y="36" width="14" height="22" rx="6" fill="#2e86de"/><rect x="44" y="36" width="14" height="22" rx="6" fill="#2e86de"/>',
    "hablar": '<path d="M10 58V44q-6-4-6-14Q4 8 24 8q16 0 18 14l4 10-4 2v8q0 4-4 4h-6v12z" fill="#9fb3c4"/>'
              '<g fill="none" stroke="#2e86de" stroke-width="3.5" stroke-linecap="round"><path class="fa-onda" d="M50 26q4 6 0 12"/><path class="fa-onda fa-d2" d="M56 20q8 12 0 24"/></g>',
    "persona": '<circle cx="32" cy="20" r="12" fill="#2e86de"/><path d="M10 58q0-24 22-24t22 24z" fill="#2e86de"/>',
    "personas": '<circle cx="22" cy="20" r="10" fill="#2e86de"/><path d="M4 56q0-20 18-20t18 20z" fill="#2e86de"/>'
                '<circle cx="44" cy="22" r="9" fill="#4aa3f0"/><path d="M30 56q0-18 14-18t16 18z" fill="#4aa3f0"/>',
    "salir": '<rect x="8" y="6" width="30" height="52" rx="3" fill="#a0673a"/><circle cx="31" cy="34" r="2.5" fill="#f2b400"/>'
             '<path d="M34 32h24M48 22l10 10-10 10" fill="none" stroke="#e53935" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>',
    "portapapeles": '<rect x="10" y="8" width="44" height="52" rx="5" fill="#d9a066"/><rect x="16" y="14" width="32" height="40" rx="2" fill="#fff"/>'
                    '<rect x="22" y="4" width="20" height="10" rx="3" fill="#607d8b"/><path d="M21 26h22M21 34h22M21 42h14" stroke="#9fb3c4" stroke-width="3" stroke-linecap="round"/>',
    "nota": '<path d="M12 4h30l12 12v44H12z" fill="#fff" stroke="#9fb3c4" stroke-width="2.5"/><path d="M42 4v12h12" fill="#e3eef6"/>'
            '<path d="M19 26h26M19 34h26M19 42h18" stroke="#9fb3c4" stroke-width="3" stroke-linecap="round"/>',
    "alerta": '<path d="M32 4L2 58h60z" fill="#f2b400" stroke="#e9a400" stroke-width="2" stroke-linejoin="round"/><path d="M32 22v18" stroke="' + O + '" stroke-width="6" stroke-linecap="round"/><circle cx="32" cy="49" r="3.5" fill="' + O + '"/>',
    "basura": '<rect x="8" y="12" width="48" height="7" rx="3" fill="#607d8b"/><rect x="24" y="5" width="16" height="8" rx="2" fill="#607d8b"/>'
              '<path d="M12 20h40l-4 38H16z" fill="#90a4ae"/><path d="M24 28v22M32 28v22M40 28v22" stroke="#607d8b" stroke-width="3" stroke-linecap="round"/>',
    "guardar": '<path d="M8 8h40l8 8v40H8z" fill="#2e86de"/><rect x="18" y="8" width="24" height="16" fill="#e3f4fd"/><rect x="34" y="11" width="5" height="10" fill="#2e86de"/><rect x="16" y="34" width="32" height="22" rx="2" fill="#fff"/>',
    "ojo": '<path d="M2 32q30-34 60 0-30 34-60 0z" fill="#fff" stroke="' + O + '" stroke-width="3"/><circle cx="32" cy="32" r="11" fill="#2e86de"/><circle cx="32" cy="32" r="5" fill="' + O + '"/><circle cx="35" cy="29" r="2" fill="#fff"/>',
    "ojo_tachado": '<path d="M2 32q30-34 60 0-30 34-60 0z" fill="#fff" stroke="' + O + '" stroke-width="3"/><circle cx="32" cy="32" r="11" fill="#9fb3c4"/><path d="M8 56L56 8" stroke="#e53935" stroke-width="5" stroke-linecap="round"/>',
    "impresora": '<rect x="16" y="4" width="32" height="18" fill="#fff" stroke="#9fb3c4" stroke-width="2.5"/><rect x="4" y="20" width="56" height="26" rx="5" fill="#607d8b"/>'
                 '<rect x="16" y="38" width="32" height="22" fill="#fff" stroke="#9fb3c4" stroke-width="2.5"/><circle cx="50" cy="28" r="2.5" fill="#2bb673"/><path d="M22 46h20M22 52h14" stroke="#9fb3c4" stroke-width="2.5"/>',
    "descargar": '<path d="M32 4v30M20 22l12 12 12-12" fill="none" stroke="#2bb673" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 38v14q0 6 6 6h40q6 0 6-6V38" fill="none" stroke="#2e86de" stroke-width="5" stroke-linecap="round"/>',
    "vacio": '<path d="M6 30l8-20h36l8 20v24H6z" fill="#e3eef6" stroke="#9fb3c4" stroke-width="2.5"/><path d="M6 30h16q0 8 10 8t10-8h16" fill="none" stroke="#9fb3c4" stroke-width="2.5"/>',
    "escudo": '<path d="M32 4l24 8v16q0 20-24 32Q8 48 8 28V12z" fill="#2e86de"/><path d="M20 32l9 9 16-18" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>',
    "megafono": '<path d="M8 26h12l26-16v44L20 38H8z" fill="#e53935"/><rect x="12" y="38" width="8" height="16" rx="3" fill="#b71c1c"/>'
                '<g fill="none" stroke="#f2b400" stroke-width="3.5" stroke-linecap="round"><path class="fa-onda" d="M52 24q4 8 0 16"/><path class="fa-onda fa-d2" d="M57 18q8 14 0 28"/></g>',
    "pelicula": '<rect x="6" y="8" width="52" height="48" rx="4" fill="' + O + '"/><rect x="16" y="14" width="32" height="16" fill="#4aa3f0"/><rect x="16" y="34" width="32" height="16" fill="#f2b400"/>'
                '<g fill="#fff"><rect x="9" y="12" width="4" height="5"/><rect x="9" y="24" width="4" height="5"/><rect x="9" y="36" width="4" height="5"/><rect x="9" y="48" width="4" height="5"/>'
                '<rect x="51" y="12" width="4" height="5"/><rect x="51" y="24" width="4" height="5"/><rect x="51" y="36" width="4" height="5"/><rect x="51" y="48" width="4" height="5"/></g>',
    "enchufe": '<path d="M22 4v14M42 4v14" stroke="#9fb3c4" stroke-width="5" stroke-linecap="round"/><path d="M14 18h36v14q0 12-14 14h-8Q14 44 14 32z" fill="#607d8b"/><path d="M32 46v14" stroke="' + O + '" stroke-width="5"/>',
    "bombillo": '<path d="M32 4a18 18 0 00-10 33v7h20v-7A18 18 0 0032 4z" fill="#ffd54a"/><rect x="22" y="44" width="20" height="10" rx="2" fill="#9fb3c4"/><path d="M26 58h12" stroke="#607d8b" stroke-width="4" stroke-linecap="round"/>'
                '<path d="M27 30l5-8 5 8" stroke="#f2a900" stroke-width="2.5" fill="none"/>',
    "triste": '<circle cx="32" cy="32" r="27" fill="#ffd54a"/><circle cx="23" cy="27" r="3.5" fill="' + O + '"/><circle cx="41" cy="27" r="3.5" fill="' + O + '"/>'
              '<path d="M21 46q11-10 22 0" fill="none" stroke="' + O + '" stroke-width="4" stroke-linecap="round"/>',
    "abajo": '<path d="M32 6v44M16 36l16 16 16-16" fill="none" stroke="#2e86de" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>',
    "arriba": '<path d="M32 58V14M16 28l16-16 16 16" fill="none" stroke="#2e86de" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>',
    "bandera": '<path d="M12 4v56" stroke="#8a5a35" stroke-width="4" stroke-linecap="round"/><path d="M14 6h40v28H14z" fill="#fff" stroke="' + O + '" stroke-width="1.5"/>'
               '<g fill="' + O + '"><rect x="14" y="6" width="10" height="7"/><rect x="34" y="6" width="10" height="7"/><rect x="24" y="13" width="10" height="7"/><rect x="44" y="13" width="10" height="7"/><rect x="14" y="20" width="10" height="7"/><rect x="34" y="20" width="10" height="7"/><rect x="24" y="27" width="10" height="7"/><rect x="44" y="27" width="10" height="7"/></g>',
    "imagen": '<rect x="4" y="8" width="56" height="48" rx="6" fill="#e3f4fd" stroke="#2e86de" stroke-width="3"/><circle cx="44" cy="22" r="6" fill="#ffd54a"/>'
              '<path d="M6 52l16-20 12 14 8-8 16 14z" fill="#43a047"/>',
    "brujula": '<circle cx="32" cy="32" r="27" fill="#fff" stroke="#2e86de" stroke-width="4"/><path d="M32 10l7 22-7 22-7-22z" fill="#e53935"/><path d="M32 32l7 0-7 22-7-22z" fill="#9fb3c4"/><circle cx="32" cy="32" r="3" fill="' + O + '"/>',
    "iman": '<path d="M12 8h12v24a8 8 0 0016 0V8h12v24a20 20 0 01-40 0z" fill="#e53935"/><rect x="12" y="8" width="12" height="8" fill="#cfd8e2"/><rect x="40" y="8" width="12" height="8" fill="#cfd8e2"/>'
            '<path d="M6 54l6-4M32 60v-6M58 54l-6-4" stroke="#2e86de" stroke-width="3" stroke-linecap="round"/>',
    "grabando": '<circle cx="32" cy="32" r="22" fill="#e53935" class="fa-late"/><circle cx="32" cy="32" r="28" fill="none" stroke="#e53935" stroke-width="3" opacity=".4"/>',
    "silencio": '<path d="M6 24h12l16-13v42L18 40H6z" fill="#9fb3c4"/><path d="M42 24l16 16M58 24L42 40" stroke="#e53935" stroke-width="5" stroke-linecap="round"/>',
    "mouse": '<rect x="16" y="6" width="32" height="52" rx="16" fill="#fff" stroke="' + O + '" stroke-width="3"/><path d="M32 6v18M16 24h32" stroke="' + O + '" stroke-width="3"/><rect x="29" y="12" width="6" height="8" rx="3" fill="#2e86de"/>',
    "beso": '<path d="M10 32q10-16 22-8 12-8 22 8-10 8-22 6-12 2-22-6z" fill="#e53935"/><path d="M10 32q22 22 44 0-10 6-22 6t-22-6z" fill="#c62828"/>'
            '<path d="M44 14q6-6 10 0-2 6-10 10-8-4-10-10 4-6 10 0z" fill="#e0528f" class="fa-sube"/>',
}

# Círculos de color (teclas del piano)
for _n, _c in {"verde": "#2bb673", "naranja": "#f57c00", "amarillo": "#f2b400", "azul": "#2e86de",
               "morado": "#8e6bd6", "rosa": "#e0528f", "rojo": "#e53935"}.items():
    UI[f"circulo_{_n}"] = f'<circle cx="32" cy="32" r="26" fill="{_c}"/><circle cx="24" cy="24" r="8" fill="#fff" opacity=".3"/>'


# ── Bocas animadas (vista de frente, primer plano) ───────────────────────────
_PIEL = ('<rect x="2" y="2" width="60" height="60" rx="16" fill="#ffe3cc"/>'
         '<path d="M24 6q8 8 16 0" fill="none" stroke="#e8a77a" stroke-width="2.5" stroke-linecap="round"/>'
         '<ellipse cx="27" cy="10" rx="2.6" ry="1.8" fill="#d08a5c"/><ellipse cx="37" cy="10" rx="2.6" ry="1.8" fill="#d08a5c"/>')
_LABIO_SUP = "#e0528f"
_LABIO_INF = "#d4457f"

# Fotogramas reutilizables (centro de la boca: 32,36)
CERRADA = ('<path d="M12 36q10-8 20-4 10-4 20 4-10 2-20 1-10 1-20-1z" fill="' + _LABIO_SUP + '"/>'
           '<path d="M12 36q20 16 40 0-10 3-20 2-10 1-20-2z" fill="' + _LABIO_INF + '"/>'
           '<path d="M12 36q20 3 40 0" stroke="#a8325f" stroke-width="2" fill="none"/>')
ABIERTA = ('<path d="M12 34q10-10 20-6 10-4 20 6-6 22-20 22T12 34z" fill="' + _LABIO_SUP + '"/>'
           '<path d="M16 35q8-6 16-3 8-3 16 3-4 15-16 15T16 35z" fill="#7a1f3d"/>'
           '<path d="M19 34q13-5 26 0v3H19z" fill="#fff"/>'
           '<path d="M22 46q10-6 20 0-4 4-10 4t-10-4z" fill="#ff8fab"/>')
SONRISA_DIENTES = ('<path d="M10 32q22-6 44 0-6 16-22 16T10 32z" fill="' + _LABIO_SUP + '"/>'
                   '<path d="M14 33q18-4 36 0-4 11-18 11T14 33z" fill="#fff"/>'
                   '<path d="M14 38.5q18 2 36 0" stroke="#cfd8e2" stroke-width="1.6"/><path d="M23 33v10M32 32v12M41 33v10" stroke="#e3e9ef" stroke-width="1.2"/>')
REDONDA = ('<ellipse cx="32" cy="38" rx="12" ry="13" fill="' + _LABIO_SUP + '"/><ellipse cx="32" cy="38" rx="7" ry="8" fill="#7a1f3d"/>'
           '<ellipse cx="32" cy="43" rx="4" ry="2.4" fill="#ff8fab"/>')
BESO = ('<path d="M24 38q2-8 8-6 6-2 8 6-2 8-8 7-6 1-8-7z" fill="' + _LABIO_SUP + '"/><path d="M24 38q8 2 16 0" stroke="#a8325f" stroke-width="1.6" fill="none"/>')


def _boca(*capas):
    return _PIEL + "".join(capas)


def _aire(clase="fa-aire"):
    return ('<g class="' + clase + '" fill="none" stroke="#2e9fd6" stroke-width="2.6" stroke-linecap="round">'
            '<path d="M40 54q8 2 16 6"/><path d="M32 56v6"/><path d="M24 54q-8 2-16 6"/></g>')


def _voz():
    return ('<g fill="none" stroke="#8e6bd6" stroke-width="2.6" stroke-linecap="round">'
            '<path class="fa-onda" d="M54 26q4 8 0 16"/><path class="fa-onda fa-d2" d="M58 20q7 14 0 28"/>'
            '<path class="fa-onda" d="M10 26q-4 8 0 16"/><path class="fa-onda fa-d2" d="M6 20q-7 14 0 28"/></g>')


def _alterna(a, b):
    """Dos fotogramas que se alternan (fa-a visible primero, luego fa-b)."""
    return f'<g class="fa-a">{a}</g><g class="fa-b">{b}</g>'


def _lengua_arriba(clase):
    # boca abierta mostrando la punta de la lengua que sube a los dientes de arriba
    return ('<path d="M12 34q10-10 20-6 10-4 20 6-6 22-20 22T12 34z" fill="' + _LABIO_SUP + '"/>'
            '<path d="M16 35q8-6 16-3 8-3 16 3-4 15-16 15T16 35z" fill="#7a1f3d"/>'
            '<path d="M19 34q13-5 26 0v3H19z" fill="#fff"/>'
            f'<g class="{clase}"><path d="M20 50q2-12 12-12t12 12q-6 3-12 3t-12-3z" fill="#ff7a9a"/><path d="M32 42v8" stroke="#e05578" stroke-width="1.6"/></g>')


BOCAS = {
    # M: labios juntos y vibran (sonido por la nariz)
    "boca_m": _boca('<g class="fa-vibra">' + CERRADA + '</g>', _voz(),
                    '<g class="fa-aire-in" fill="none" stroke="#2e9fd6" stroke-width="2.4" stroke-linecap="round"><path d="M27 13v-9M37 13v-9"/></g>'),
    # P: labios juntos y se abren con un soplo
    "boca_p": _boca(_alterna(CERRADA, ABIERTA + _aire("fa-aire fa-b-solo"))),
    # B: como P pero con voz
    "boca_b": _boca(_alterna(CERRADA, ABIERTA), _voz()),
    # S: dientes juntos, el aire sale por el centro
    "boca_s": _boca(SONRISA_DIENTES, '<g class="fa-aire" fill="none" stroke="#2e9fd6" stroke-width="2.6" stroke-linecap="round"><path d="M32 46v14"/><path d="M28 46q-6 6-10 14"/><path d="M36 46q6 6 10 14"/></g>'),
    # F: dientes de arriba sobre el labio de abajo, sale aire
    "boca_f": _boca('<path d="M12 40q20 14 40 0-10-2-20-2t-20 2z" fill="' + _LABIO_INF + '"/>'
                    '<path d="M18 31h28v7q-14 3-28 0z" fill="#fff" stroke="#e3e9ef" stroke-width="1.2"/>'
                    '<path d="M12 31q10-8 20-4 10-4 20 4z" fill="' + _LABIO_SUP + '"/>', _aire()),
    # D: la punta de la lengua toca detrás de los dientes de arriba
    "boca_d": _boca(_lengua_arriba("fa-toque"), _voz()),
    # R: un toque rápido de la lengua
    "boca_r": _boca(_lengua_arriba("fa-toque-rapido")),
    # RR: la lengua vibra muchas veces
    "boca_rr": _boca(_lengua_arriba("fa-vibra-lengua"), _voz()),
    # G / C: boca abierta, la parte de atrás de la lengua sube
    "boca_g": _boca('<path d="M12 34q10-10 20-6 10-4 20 6-6 22-20 22T12 34z" fill="' + _LABIO_SUP + '"/>'
                    '<path d="M16 35q8-6 16-3 8-3 16 3-4 15-16 15T16 35z" fill="#7a1f3d"/>'
                    '<path d="M19 34q13-5 26 0v3H19z" fill="#fff"/>'
                    '<g class="fa-sube"><path d="M18 50q4-14 14-14t14 14q-6 2-14 2t-14-2z" fill="#ff7a9a"/></g>', _voz()),
    # A: boca muy abierta y voz
    "boca_a": _boca('<g class="fa-abre">' + ABIERTA + '</g>', _voz()),
    # O / U: labios redondos
    "boca_o": _boca(REDONDA, _voz()),
    # Movimientos de boca (para praxias y la letra R)
    "boca_sonrisa": _boca(SONRISA_DIENTES),
    "boca_abierta": _boca(ABIERTA),
    "boca_redonda": _boca(REDONDA),
    "boca_beso": _boca(BESO),
    "boca_dientes": _boca('<path d="M14 32h36v10H14z" fill="#fff" stroke="#cfd8e2" stroke-width="1.5"/><path d="M14 37h36M23 32v10M32 32v10M41 32v10" stroke="#e3e9ef" stroke-width="1.2"/>'
                          '<path d="M10 32q22-8 44 0" fill="none" stroke="' + _LABIO_SUP + '" stroke-width="4"/><path d="M10 42q22 8 44 0" fill="none" stroke="' + _LABIO_INF + '" stroke-width="4"/>'),
}
BOCAS["boca_c"] = BOCAS["boca_g"]
BOCAS["boca_k"] = BOCAS["boca_g"]

# Qué boca usar para cada fonema
BOCA_DE_FONEMA = {"M": "boca_m", "P": "boca_p", "B": "boca_b", "S": "boca_s", "F": "boca_f", "D": "boca_d",
                  "R": "boca_r", "RR": "boca_rr", "G": "boca_g", "C": "boca_c", "A": "boca_a", "O": "boca_o", "U": "boca_o"}
