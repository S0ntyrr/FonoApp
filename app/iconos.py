"""Ilustraciones propias (SVG) para FonoApp.

Se usan en lugar de emojis: se ven igual en todos los dispositivos, no pierden
calidad y están pensadas para niños que aún no leen. Todas usan viewBox 0 0 64 64.
Uso en plantillas:  {{ icono('globo', 48) }}
"""
from markupsafe import Markup

_F = 'font-family="Arial Rounded MT Bold,Arial,sans-serif" font-weight="900" text-anchor="middle"'


def _letra(letra: str, color: str) -> str:
    tam = 30 if len(letra) == 1 else 22
    return (f'<rect x="6" y="6" width="52" height="52" rx="14" fill="{color}"/>'
            f'<rect x="6" y="6" width="52" height="20" rx="14" fill="#fff" opacity=".18"/>'
            f'<text x="32" y="{32 + tam * 0.36:.0f}" font-size="{tam + 8}" fill="#fff" {_F}>{letra}</text>')


def _cara(boca: str, extra: str = "") -> str:
    return ('<circle cx="32" cy="34" r="24" fill="#ffd9b8" stroke="#e8a77a" stroke-width="2.5"/>'
            '<path d="M10 28Q14 6 32 7Q50 6 54 28Q46 16 32 16Q18 16 10 28Z" fill="#6b3f1f"/>'
            '<circle cx="23" cy="31" r="3" fill="#1f3347"/><circle cx="41" cy="31" r="3" fill="#1f3347"/>'
            '<circle cx="24" cy="30" r="1" fill="#fff"/><circle cx="42" cy="30" r="1" fill="#fff"/>'
            + boca + extra)


def _gravedad(color: str, boca: str, cejas: str = "", extra: str = "") -> str:
    return (f'<circle cx="32" cy="32" r="28" fill="{color}"/>'
            '<circle cx="32" cy="32" r="28" fill="#fff" opacity=".12"/>'
            '<circle cx="23" cy="27" r="4" fill="#1f3347"/><circle cx="41" cy="27" r="4" fill="#1f3347"/>'
            f'<path d="{boca}" fill="none" stroke="#1f3347" stroke-width="4" stroke-linecap="round"/>'
            + (f'<path d="{cejas}" fill="none" stroke="#1f3347" stroke-width="3.5" stroke-linecap="round"/>' if cejas else "")
            + extra)


_ESTRELLA = 'M32 4L40 23L60 24L44 37L50 58L32 46L14 58L20 37L4 24L24 23Z'

ICONOS = {
    # ── Juegos ──
    "globo": '<path d="M32 4c11 0 19 8 19 19 0 12-10 21-19 22-9-1-19-10-19-22 0-11 8-19 19-19z" fill="#e53935"/>'
             '<ellipse cx="24" cy="17" rx="4" ry="7" fill="#fff" opacity=".45" transform="rotate(-20 24 17)"/>'
             '<path d="M29 45h6l-3 4z" fill="#b71c1c"/><path d="M32 49c-5 3 5 6 0 11" fill="none" stroke="#8a97a6" stroke-width="2" stroke-linecap="round"/>',
    "molino": '<rect x="30" y="30" width="4" height="30" rx="2" fill="#8a5a35"/><g transform="translate(32 28)"><g class="fa-gira-rehilete">'
              '<path d="M0 0V-23q13 5 0 23z" fill="#2e9fd6"/><path d="M0 0H23q-5 13-23 0z" fill="#f2b400"/>'
              '<path d="M0 0V23q-13-5 0-23z" fill="#e0528f"/><path d="M0 0H-23q5-13 23 0z" fill="#2bb673"/>'
              '<circle r="3.5" fill="#fff" stroke="#5a6b7b" stroke-width="1.5"/></g></g>',
    "burbujas": '<circle cx="25" cy="37" r="18" fill="#e6f7ff" stroke="#6cc4ef" stroke-width="3"/>'
                '<circle cx="47" cy="17" r="10" fill="#fde8f3" stroke="#ef8cc0" stroke-width="3"/>'
                '<circle cx="50" cy="47" r="6" fill="#eef9e6" stroke="#8fd06b" stroke-width="2.5"/>'
                '<ellipse cx="18" cy="29" rx="6" ry="3.5" fill="#fff" transform="rotate(-35 18 29)"/>'
                '<ellipse cx="43" cy="13" rx="3" ry="2" fill="#fff" transform="rotate(-35 43 13)"/>',
    "algodon": '<g transform="rotate(-28 24 46)"><rect x="0" y="41" width="44" height="10" rx="5" fill="#fff" stroke="#e9a1aa" stroke-width="1.5"/>'
               '<path d="M6 51l5-10h5l-5 10zM20 51l5-10h5l-5 10zM34 51l5-10h5l-5 10z" fill="#ef4b5f"/></g>'
               '<g fill="#cfd8e2"><circle cx="46" cy="22" r="11"/><circle cx="36" cy="27" r="8"/><circle cx="56" cy="27" r="7.5"/></g>'
               '<g fill="#fff"><circle cx="46" cy="22" r="9.5"/><circle cx="36" cy="27" r="6.5"/><circle cx="56" cy="27" r="6"/></g>'
               '<circle cx="42" cy="18" r="3" fill="#fff"/>',
    "gol": '<circle cx="32" cy="32" r="25" fill="#fff" stroke="#1f3347" stroke-width="3"/>'
           '<path d="M32 21l10 7-4 11H26l-4-11z" fill="#1f3347"/>'
           '<path d="M32 21V8M42 28l12-4M38 39l8 10M26 39l-8 10M22 28l-12-4" stroke="#1f3347" stroke-width="2.5"/>',
    "escala": '<rect x="6" y="44" width="14" height="14" rx="3" fill="#2bb673"/><rect x="25" y="34" width="14" height="24" rx="3" fill="#f2b400"/>'
              '<rect x="44" y="22" width="14" height="36" rx="3" fill="#e0528f"/>'
              '<ellipse cx="11" cy="36" rx="5" ry="4" fill="#1f3347"/><path d="M15 36V20" stroke="#1f3347" stroke-width="3"/>'
              '<ellipse cx="49" cy="14" rx="5" ry="4" fill="#1f3347"/><path d="M53 14V2" stroke="#1f3347" stroke-width="3"/>',
    "escaleras": '<path d="M6 58H58V16H46V26H34V36H22V46H10V58Z" fill="#9ed6f7"/>'
                 '<path d="M10 46H22V36H34V26H46V16H58" fill="none" stroke="#2e86de" stroke-width="3" stroke-linejoin="round"/>'
                 '<circle cx="52" cy="9" r="7" fill="#ff8a3d"/><path d="M47 6q5-3 10 0" stroke="#fff" stroke-width="2" fill="none"/>',
    "piano": '<rect x="5" y="14" width="54" height="38" rx="5" fill="#fff" stroke="#1f3347" stroke-width="3"/>'
             '<path d="M18.5 14v38M32 14v38M45.5 14v38" stroke="#1f3347" stroke-width="2"/>'
             '<g fill="#1f3347"><rect x="15" y="14" width="7" height="22" rx="1.5"/><rect x="28.5" y="14" width="7" height="22" rx="1.5"/>'
             '<rect x="42" y="14" width="7" height="22" rx="1.5"/></g><rect x="5" y="14" width="54" height="6" fill="#e53935"/>',
    "lupa": '<path d="M41 41l15 15" stroke="#2e86de" stroke-width="8" stroke-linecap="round"/>'
            '<circle cx="27" cy="27" r="18" fill="#e3f4fd" stroke="#2e86de" stroke-width="5"/>'
            '<path d="M14 27q13-11 26 0q-13 11-26 0z" fill="#fff" stroke="#1f3347" stroke-width="2"/>'
            '<circle cx="27" cy="27" r="5" fill="#1f3347"/><circle cx="29" cy="25" r="1.5" fill="#fff"/>',
    "vaca": '<path d="M12 18q-8-8-10 0 2 8 12 6zM42 18q8-8 10 0-2 8-12 6z" fill="#fff" stroke="#1f3347" stroke-width="2.5"/>'
            '<path d="M16 12q-2-8 4-8M38 12q2-8-4-8" fill="none" stroke="#c9a46b" stroke-width="4" stroke-linecap="round"/>'
            '<ellipse cx="27" cy="30" rx="16" ry="18" fill="#fff" stroke="#1f3347" stroke-width="2.5"/>'
            '<path d="M32 14q8 0 9 8q-8 2-9-8z" fill="#1f3347"/>'
            '<ellipse cx="27" cy="42" rx="12" ry="8" fill="#f7b6c2"/><circle cx="22" cy="42" r="2" fill="#1f3347"/><circle cx="32" cy="42" r="2" fill="#1f3347"/>'
            '<circle cx="20" cy="28" r="2.6" fill="#1f3347"/><circle cx="34" cy="28" r="2.6" fill="#1f3347"/>'
            '<path d="M49 30q5 6 0 12M55 25q9 11 0 22" fill="none" stroke="#8e6bd6" stroke-width="3" stroke-linecap="round"/>',
    "boca": '<path d="M6 32q26-20 52 0q-26 24-52 0z" fill="#e0528f"/><path d="M13 32q19-7 38 0q-19 12-38 0z" fill="#7a1f3d"/>'
            '<path d="M15 31q17-4 34 0v3H15z" fill="#fff"/><path d="M24 39q8 5 16 0q-8-3-16 0z" fill="#ff8fab"/>'
            '<path d="M14 26q8-4 14-2" stroke="#fff" stroke-width="2" opacity=".5" fill="none" stroke-linecap="round"/>',
    "abc": '<rect x="2" y="6" width="28" height="28" rx="7" fill="#2e9fd6"/>'
           f'<text x="16" y="28" font-size="22" fill="#fff" {_F}>A</text>'
           '<rect x="34" y="6" width="28" height="28" rx="7" fill="#2bb673"/>'
           f'<text x="48" y="28" font-size="22" fill="#fff" {_F}>B</text>'
           '<rect x="18" y="32" width="28" height="28" rx="7" fill="#e0528f"/>'
           f'<text x="32" y="54" font-size="22" fill="#fff" {_F}>C</text>',
    "diana": '<circle cx="29" cy="35" r="24" fill="#e53935"/><circle cx="29" cy="35" r="17" fill="#fff"/>'
             '<circle cx="29" cy="35" r="10" fill="#e53935"/><circle cx="29" cy="35" r="4" fill="#fff"/>'
             '<path d="M29 35L54 10" stroke="#1f3347" stroke-width="3.5" stroke-linecap="round"/>'
             '<path d="M50 4l10 0-4 4 4 4-10 0z" fill="#2bb673" transform="rotate(-45 54 10) translate(2 0)"/>',
    "lapiz": '<g transform="rotate(40 32 32)"><rect x="24" y="2" width="16" height="42" rx="2" fill="#f2b400"/>'
             '<rect x="24" y="2" width="16" height="8" rx="2" fill="#ef8cc0"/><rect x="24" y="10" width="16" height="3" fill="#b0bec5"/>'
             '<path d="M24 44h16l-8 15z" fill="#f3dcb3"/><path d="M29 53.5h6l-3 5.5z" fill="#1f3347"/>'
             '<rect x="30" y="13" width="4" height="31" fill="#fff" opacity=".35"/></g>',
    "moto": '<circle cx="14" cy="45" r="10" fill="none" stroke="#1f3347" stroke-width="5"/><circle cx="50" cy="45" r="10" fill="none" stroke="#1f3347" stroke-width="5"/>'
            '<circle cx="14" cy="45" r="3" fill="#1f3347"/><circle cx="50" cy="45" r="3" fill="#1f3347"/>'
            '<path d="M14 45l13-15h14l9 15" fill="none" stroke="#e53935" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>'
            '<path d="M22 27h18l-3 9H25z" fill="#e53935"/><path d="M41 30l5-11h8" fill="none" stroke="#1f3347" stroke-width="4" stroke-linecap="round"/>'
            '<path d="M2 30h10M4 37h8" stroke="#9fb3c4" stroke-width="3" stroke-linecap="round"/>',
    "letra_b": _letra("B", "#f08a3c"), "letra_d": _letra("D", "#1fa9a4"),
    "letra_f": _letra("F", "#8e6bd6"), "letra_r": _letra("R", "#e53935"),
    "huella": '<ellipse cx="32" cy="43" rx="14" ry="12" fill="#a0673a"/><ellipse cx="14" cy="27" rx="6" ry="7" fill="#a0673a"/>'
              '<ellipse cx="25" cy="15" rx="6" ry="7" fill="#a0673a"/><ellipse cx="39" cy="15" rx="6" ry="7" fill="#a0673a"/>'
              '<ellipse cx="50" cy="27" rx="6" ry="7" fill="#a0673a"/>',
    "lengua": '<path d="M6 24q26-16 52 0q-26 26-52 0z" fill="#7a1f3d"/><path d="M6 24q26-7 52 0" fill="none" stroke="#e0528f" stroke-width="6" stroke-linecap="round"/>'
              '<path d="M20 30q12 34 24 0q-12 7-24 0z" fill="#ff7a9a"/><path d="M32 33v14" stroke="#d94f72" stroke-width="2.5" stroke-linecap="round"/>'
              '<path d="M50 44q6 2 6 8M54 38q8 2 8 10" fill="none" stroke="#e0528f" stroke-width="2.5" stroke-linecap="round"/>',
    "pregunta": '<path d="M10 8h44a5 5 0 015 5v28a5 5 0 01-5 5H30l-13 11V46h-7a5 5 0 01-5-5V13a5 5 0 015-5z" fill="#8e6bd6"/>'
                f'<text x="32" y="38" font-size="30" fill="#fff" {_F}>?</text>',
    "notas": '<path d="M24 47V15l28-7v32" fill="none" stroke="#8e6bd6" stroke-width="4" stroke-linejoin="round"/>'
             '<path d="M24 20l28-7" stroke="#8e6bd6" stroke-width="6"/>'
             '<ellipse cx="17" cy="47" rx="8" ry="6" fill="#8e6bd6" transform="rotate(-15 17 47)"/>'
             '<ellipse cx="45" cy="40" rx="8" ry="6" fill="#8e6bd6" transform="rotate(-15 45 40)"/>',
    "perro": '<path d="M12 16q-8 16 2 27l9-5V15z" fill="#8a5a35"/><path d="M52 16q8 16-2 27l-9-5V15z" fill="#8a5a35"/>'
             '<circle cx="32" cy="34" r="19" fill="#e3b07a"/><ellipse cx="32" cy="43" rx="10" ry="8" fill="#f3d3ad"/>'
             '<circle cx="25" cy="30" r="3" fill="#1f3347"/><circle cx="39" cy="30" r="3" fill="#1f3347"/>'
             '<ellipse cx="32" cy="39" rx="5" ry="3.5" fill="#1f3347"/>'
             '<path d="M32 42v4M27 47q5 3 10 0" stroke="#1f3347" stroke-width="2" fill="none" stroke-linecap="round"/>',
    "campana": '<path d="M50 12q7 7 7 16M14 12q-7 7-7 16" fill="none" stroke="#1fa9a4" stroke-width="3.5" stroke-linecap="round"/>'
               '<path d="M32 6a4 4 0 014 4v3c9 2 14 10 14 20v10l5 6H9l5-6V33c0-10 5-18 14-20v-3a4 4 0 014-4z" fill="#f2b400"/>'
               '<path d="M22 22q3-5 8-6" stroke="#fff" stroke-width="3" fill="none" opacity=".6" stroke-linecap="round"/>'
               '<circle cx="32" cy="54" r="5" fill="#c99500"/>',
    "arrastrar": '<path d="M6 14h26M24 6l8 8-8 8" fill="none" stroke="#1fa9a4" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>'
                 '<g transform="translate(16 18) scale(.62)"><path d="M30 70Q18 58 16 46Q15 40 21 41Q25 42 28 50L28 18Q28 12 33 12Q38 12 38 18L38 38L38 32Q38 27 43 27Q48 27 48 32L48 40L48 35Q48 30 53 30Q58 30 58 35L58 42Q58 38 62 38Q67 38 67 43L67 56Q67 66 60 72Z" fill="#ffd9b8" stroke="#c98a5e" stroke-width="4" stroke-linejoin="round"/></g>',
    "rompecabezas": '<path d="M8 18H21a6 6 0 1112 0H46V30a6 6 0 110 12V56H33a6 6 0 10-12 0H8V42a6 6 0 100-12Z" fill="#f08a3c"/>'
                    '<path d="M12 22h8" stroke="#fff" stroke-width="3" opacity=".5" stroke-linecap="round"/>',
    "cara": _cara('<path d="M22 42q10 9 20 0" fill="none" stroke="#b5523b" stroke-width="3.5" stroke-linecap="round"/>',
                  '<circle cx="16" cy="40" r="4" fill="#ffb3a1"/><circle cx="48" cy="40" r="4" fill="#ffb3a1"/>'),
    "asociar": '<rect x="3" y="10" width="24" height="32" rx="5" fill="#fef0e4" stroke="#f08a3c" stroke-width="3"/>'
               '<rect x="37" y="22" width="24" height="32" rx="5" fill="#e3f4fd" stroke="#2e9fd6" stroke-width="3"/>'
               '<path d="M27 26q9 0 10 12" fill="none" stroke="#1f3347" stroke-width="3" stroke-dasharray="4 4"/>'
               '<circle cx="15" cy="26" r="6" fill="#f08a3c"/><path d="M43 45l6-11 6 11z" fill="#2e9fd6"/>',
    "praxias": _cara('<ellipse cx="32" cy="45" rx="8" ry="6" fill="#7a1f3d"/><path d="M26 46q6 12 12 0z" fill="#ff7a9a"/>'),
    "microfono": '<rect x="22" y="5" width="20" height="33" rx="10" fill="#2bb673"/><path d="M26 12h12M26 18h12M26 24h12" stroke="#fff" stroke-width="2" opacity=".6"/>'
                 '<path d="M14 30a18 18 0 0036 0" fill="none" stroke="#1f3347" stroke-width="4" stroke-linecap="round"/>'
                 '<path d="M32 48v9M22 58h20" stroke="#1f3347" stroke-width="4" stroke-linecap="round"/>',
    "oreja": '<path d="M22 47c-7-6-9-15-7-23 3-13 19-17 27-8 7 7 5 17-1 22-4 3-5 6-4 10 1 6-7 9-11 4" fill="#ffd9b8" stroke="#c98a5e" stroke-width="3" stroke-linecap="round"/>'
             '<path d="M26 30c0-6 8-8 11-3 2 4-1 7-4 8" fill="none" stroke="#c98a5e" stroke-width="3" stroke-linecap="round"/>'
             '<g fill="none" stroke="#1fa9a4" stroke-width="3.5" stroke-linecap="round"><path class="fa-onda" d="M50 22q5 8 0 16"/><path class="fa-onda fa-d2" d="M56 16q9 14 0 28"/></g>',
    "inspirar": _cara('<path d="M25 46q7 4 14 0" fill="none" stroke="#b5523b" stroke-width="3" stroke-linecap="round"/>',
                      '<path d="M30 36q2 4 4 0" fill="none" stroke="#d08a5c" stroke-width="2" stroke-linecap="round"/>'
                      '<g class="fa-aire-in" stroke="#2e9fd6" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round">'
                      '<path d="M2 54q12-6 26-16"/><path d="M22 36l6 2-2 6"/><path d="M62 54q-12-6-26-16"/><path d="M42 36l-6 2 2 6"/></g>'),
    "soplar": _cara('<ellipse cx="32" cy="45" rx="5" ry="4.5" fill="#b5523b"/>',
                    '<circle cx="16" cy="41" r="5" fill="#ffb3a1"/><circle cx="48" cy="41" r="5" fill="#ffb3a1"/>'
                    '<g class="fa-aire" stroke="#2e9fd6" stroke-width="3" fill="none" stroke-linecap="round"><path d="M40 44q10-2 20 2"/><path d="M40 49q10 2 20 7"/></g>'),
    # ── Interfaz ──
    "mapa": '<path d="M5 14l17-7 20 7 17-7v43l-17 7-20-7-17 7z" fill="#fff" stroke="#2e9fd6" stroke-width="3" stroke-linejoin="round"/>'
            '<path d="M22 7v43M42 14v43" stroke="#2e9fd6" stroke-width="2"/>'
            '<path d="M11 40q9-15 19-7t21-13" fill="none" stroke="#e53935" stroke-width="3" stroke-dasharray="4 4" stroke-linecap="round"/>'
            '<path d="M48 14l5 6M53 14l-5 6" stroke="#e53935" stroke-width="3" stroke-linecap="round"/>',
    "trofeo": '<path d="M18 12H8q0 15 13 15M46 12h10q0 15-13 15" fill="none" stroke="#e9a400" stroke-width="4.5"/>'
              '<path d="M17 6h30v16a15 15 0 01-30 0z" fill="#f2b400"/><path d="M22 10v10a10 10 0 005 9" stroke="#fff" stroke-width="3" fill="none" opacity=".5" stroke-linecap="round"/>'
              '<rect x="28" y="36" width="8" height="10" fill="#c99500"/><rect x="17" y="46" width="30" height="12" rx="3" fill="#8a5a35"/>'
              '<rect x="24" y="50" width="16" height="4" rx="2" fill="#f2b400"/>',
    "doctor": '<circle cx="32" cy="32" r="28" fill="#fff" stroke="#2e86de" stroke-width="3"/>'
              '<path d="M20 14v12a9 9 0 0018 0V14" fill="none" stroke="#2e86de" stroke-width="4" stroke-linecap="round"/>'
              '<path d="M29 35v5a10 10 0 0020 0v-4" fill="none" stroke="#2e86de" stroke-width="4"/>'
              '<circle cx="49" cy="31" r="5" fill="#e53935"/><circle cx="20" cy="14" r="3" fill="#1f3347"/><circle cx="38" cy="14" r="3" fill="#1f3347"/>',
    "candado": '<path d="M20 30v-9a12 12 0 0124 0v9" fill="none" stroke="#8a97a6" stroke-width="6"/>'
               '<rect x="12" y="29" width="40" height="30" rx="7" fill="#f2b400"/><rect x="12" y="29" width="40" height="8" rx="7" fill="#fff" opacity=".25"/>'
               '<circle cx="32" cy="42" r="4.5" fill="#8a5a00"/><rect x="30" y="43" width="4" height="9" rx="2" fill="#8a5a00"/>',
    "candado_abierto": '<path d="M44 30v-9a12 12 0 00-24 0v-4" fill="none" stroke="#8a97a6" stroke-width="6"/>'
                       '<rect x="12" y="29" width="40" height="30" rx="7" fill="#2bb673"/><rect x="12" y="29" width="40" height="8" rx="7" fill="#fff" opacity=".25"/>'
                       '<circle cx="32" cy="42" r="4.5" fill="#1d6b43"/><rect x="30" y="43" width="4" height="9" rx="2" fill="#1d6b43"/>',
    "estrella": f'<path d="{_ESTRELLA}" fill="#ffc93c" stroke="#e9a400" stroke-width="3" stroke-linejoin="round"/>'
                '<path d="M24 23L29 14" stroke="#fff" stroke-width="3" opacity=".6" stroke-linecap="round"/>',
    "estrella_vacia": f'<path d="{_ESTRELLA}" fill="#e3e8ef" stroke="#c9d1dc" stroke-width="3" stroke-linejoin="round"/>',
    "control": '<path d="M15 20h34a11 11 0 0111 11l2 13a7 7 0 01-12 6l-7-8H21l-7 8a7 7 0 01-12-6l2-13a11 11 0 0111-11z" fill="#1f3347"/>'
               '<path d="M17 28v12M11 34h12" stroke="#fff" stroke-width="4" stroke-linecap="round"/>'
               '<circle cx="44" cy="30" r="3.5" fill="#f2b400"/><circle cx="51" cy="37" r="3.5" fill="#e53935"/>'
               '<circle cx="44" cy="40" r="3.5" fill="#2bb673"/><circle cx="37" cy="37" r="3.5" fill="#2e9fd6"/>',
    "reloj": '<rect x="26" y="3" width="12" height="7" rx="2" fill="#2e86de"/><circle cx="32" cy="36" r="23" fill="#fff" stroke="#2e86de" stroke-width="5"/>'
             '<path d="M32 22v14l9 6" stroke="#1f3347" stroke-width="4" stroke-linecap="round" fill="none"/><circle cx="32" cy="36" r="2.5" fill="#1f3347"/>',
    "mano_hola": '<g transform="translate(-2 -6) scale(.9)"><path d="M30 70Q18 58 16 46Q15 40 21 41Q25 42 28 50L28 18Q28 12 33 12Q38 12 38 18L38 38L38 14Q38 9 43 9Q48 9 48 14L48 40L48 18Q48 13 53 13Q58 13 58 18L58 42Q58 26 62 26Q67 26 67 31L67 56Q67 66 60 72Z" fill="#ffd9b8" stroke="#c98a5e" stroke-width="3.5" stroke-linejoin="round"/></g>'
                 '<path d="M8 14q-4 6 0 12M14 10q-6 10 0 20" fill="none" stroke="#f2b400" stroke-width="3" stroke-linecap="round"/>',
    "altavoz": '<path d="M8 24h12l16-13v42L20 40H8z" fill="#2e86de"/>'
               '<g fill="none" stroke="#2e86de" stroke-width="4.5" stroke-linecap="round"><path class="fa-onda" d="M44 22q6 10 0 20"/><path class="fa-onda fa-d2" d="M51 15q12 17 0 34"/></g>',
    "casa": '<path d="M8 30L32 9l24 21" fill="none" stroke="#e53935" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
            '<path d="M14 26v30h36V26" fill="#fff" stroke="#e53935" stroke-width="4" stroke-linejoin="round"/>'
            '<rect x="27" y="38" width="10" height="18" rx="2" fill="#f2b400"/>',
    "familia": '<circle cx="18" cy="18" r="8" fill="#ffd9b8"/><path d="M6 46q0-18 12-18t12 18z" fill="#2e86de"/>'
               '<circle cx="44" cy="18" r="8" fill="#e8b48c"/><path d="M32 46q0-18 12-18t12 18z" fill="#e0528f"/>'
               '<circle cx="31" cy="34" r="6" fill="#ffd9b8"/><path d="M22 56q0-14 9-14t9 14z" fill="#f2b400"/>',
    # ── Gravedad 1–5 ──
    "grav1": _gravedad("#2bb673", "M18 36q14 18 28 0"),
    "grav2": _gravedad("#7cc242", "M20 39q12 9 24 0"),
    "grav3": _gravedad("#f2b400", "M21 42h22"),
    "grav4": _gravedad("#f57c00", "M21 46q11-8 22 0", "M15 22l10-4M49 22l-10-4"),
    "grav5": _gravedad("#e53935", "M19 48q13-12 26 0", "M14 22l11-6M50 22l-11-6",
                       '<path d="M50 30q4 6 0 9q-4-3 0-9z" fill="#9ed6f7"/>'),
}



# ── Librerías adicionales ──
from .iconos_dibujos import PALABRAS as _PALABRAS  # noqa: E402
from .iconos_ui import UI as _UI, BOCAS as _BOCAS, BOCA_DE_FONEMA  # noqa: E402

ICONOS.update(_PALABRAS)
ICONOS.update(_UI)
ICONOS.update(_BOCAS)

# Movimiento suave en dibujos de demostración (solo dentro de .animar)
for _n, _clase in {"globo": "fa-sube", "burbujas": "fa-sube", "notas": "fa-sube", "lupa": "fa-mano",
                   "arrastrar": "fa-mano", "gol": "fa-gira", "estrella": "fa-late"}.items():
    ICONOS[_n] = f'<g class="{_clase}">{ICONOS[_n]}</g>'

# Emoji → ilustración. El script fono-emoji.js reemplaza en pantalla cada emoji
# por su dibujo (el emoji original queda guardado dentro del SVG).
EMOJIS = {
    # Interfaz
    "🔊": "altavoz", "🔇": "silencio", "🎤": "microfono", "🎙": "microfono", "👀": "ojos", "👄": "boca", "🏆": "trofeo",
    "🔴": "grabando", "🎮": "control", "🕹": "control", "📋": "portapapeles", "⚠": "alerta", "🎯": "diana", "🎉": "fiesta",
    "📅": "calendario", "📆": "calendario", "💬": "dialogo", "👅": "lengua", "🔗": "enlace", "🔄": "refrescar", "🔁": "refrescar",
    "👂": "oreja", "❌": "error", "✅": "ok", "👨‍👩‍👧": "familia", "📊": "grafica", "📈": "tendencia", "📉": "tendencia_baja",
    "🎧": "audifonos", "🗣": "hablar", "🌟": "estrella", "✨": "estrella", "💫": "estrella", "⭐": "estrella", "🩺": "doctor",
    "👥": "personas", "👤": "persona", "👆": "arrastrar", "🖱": "mouse", "🚪": "salir", "🧾": "nota", "📝": "nota", "📚": "libro",
    "✏": "lapiz", "✍": "lapiz", "🗑": "basura", "💾": "guardar", "👁": "ojo", "🙈": "ojo_tachado", "🖨": "impresora", "📥": "descargar",
    "📭": "vacio", "🔎": "lupa", "🔍": "lupa", "🛡": "escudo", "📢": "megafono", "🎞": "pelicula", "🔌": "enchufe", "💡": "bombillo",
    "😔": "triste", "❓": "pregunta", "⬇": "abajo", "⬆": "arriba", "🏁": "bandera", "🖼": "imagen", "🧭": "brujula", "🔤": "abc",
    "🅰": "abc", "🧲": "iman", "🧩": "rompecabezas", "🫧": "burbujas", "🎈": "globo", "🎹": "piano", "🎶": "notas", "🎵": "notas",
    "🥤": "vaso_pitillo", "💨": "soplar", "🐡": "inflar", "💋": "beso", "😁": "boca_sonrisa", "😮": "boca_abierta", "😬": "boca_dientes",
    "😯": "boca_redonda", "😙": "boca_beso", "🥸": "cejas", "👃": "nariz", "😊": "cara", "🙂": "cara", "🏠": "casa", "🎲": "dado",
    "🌀": "molino", "🌬": "soplar", "🥅": "gol", "🌈": "arcoiris", "🧠": "asociar", "🐾": "huella", "👋": "mano_hola", "🎨": "imagen",
    "🟢": "circulo_verde", "🟠": "circulo_naranja", "🟡": "circulo_amarillo", "🔵": "circulo_azul", "🟣": "circulo_morado",
    "💗": "circulo_rosa", "🔥": "fuego", "💥": "estallido",
    # Animales
    "🐶": "perro", "🐕": "perro", "🐱": "gato", "🐈": "gato", "🐮": "vaca", "🐷": "cerdo", "🐸": "rana", "🐘": "elefante",
    "🦁": "leon", "🐧": "pinguino", "🐢": "tortuga", "🦊": "zorro", "🐴": "caballo", "🐻": "oso", "🐦": "pajaro", "🦆": "pato",
    "🐟": "pez", "🦋": "mariposa", "🦇": "murcielago", "🦉": "buho", "🦅": "aguila", "🐝": "abeja", "🦗": "grillo",
    "🐞": "mariquita", "🐛": "gusano", "🐤": "pollito", "🐔": "gallo", "🐓": "gallo", "🐍": "serpiente", "🦍": "gorila",
    "🦜": "loro", "🐒": "mono", "🐭": "raton", "🦭": "foca", "🦒": "jirafa", "🐂": "toro", "🐉": "letra_d",
    # Comida
    "🍎": "manzana", "🍐": "pera", "🍞": "pan", "🥔": "papa", "🍲": "sopa", "🧂": "sal", "🍪": "galleta", "🍦": "helado",
    "☕": "cafe", "🍳": "estufa", "🍴": "tenedor",
    # Naturaleza
    "☀": "sol", "🌞": "sol", "🌙": "luna", "☁": "nube", "🌧": "lluvia", "⚡": "rayo", "❄": "copo", "⛅": "solnube",
    "🌪": "tornado", "🌊": "ola", "🍃": "hoja", "🌳": "arbol", "🌹": "rosa", "🌸": "flor", "🏞": "rio", "🪨": "roca", "🏖": "playa",
    # Vehículos
    "🚗": "carro", "🏍": "moto", "🛵": "moto", "🚂": "tren", "🚆": "tren", "🛤": "tren", "✈": "avion", "🚢": "barco", "⛵": "velero",
    "🚲": "bici", "🚣": "bote",
    # Objetos
    "🪑": "silla", "🖐": "mano", "✋": "mano", "🗺": "mapa", "🔔": "campana", "🥁": "tambor", "🎸": "guitarra", "🎺": "trompeta",
    "📱": "celular", "📷": "camara", "📞": "telefono", "🧢": "gorra", "👢": "bota", "👗": "vestido", "🛞": "rueda", "🫙": "tarro",
    "🪙": "moneda", "🧽": "esponja", "🤖": "robot", "⚽": "gol", "🛋": "sofa", "☝": "dedo", "🦷": "diente", "❤": "corazon",
    "🤕": "curita", "🧒": "nina", "👶": "bebe", "👛": "monedero", "🧺": "canasta", "💳": "tarjeta", "🧥": "abrigo", "👙": "banador",
    "👔": "corbata", "🧊": "nevera", "🪣": "balde", "🔑": "llave", "🛁": "banera", "🛏": "cama", "🧴": "jabon", "🕶": "gafas",
    "🎩": "sombrero",
}


def icono(nombre: str, tam: int = 48, clase: str = "", etiqueta: str = "") -> Markup:
    """SVG en línea. Sin etiqueta queda oculto para lectores de pantalla (decorativo)."""
    cuerpo = ICONOS.get(nombre) or ICONOS["estrella"]
    if nombre.startswith("boca_"):
        clase = (clase + " fa-siempre").strip()
    acc = f'role="img" aria-label="{etiqueta}"' if etiqueta else 'aria-hidden="true"'
    return Markup(f'<svg class="fono-ico {clase}" viewBox="0 0 64 64" width="{tam}" height="{tam}" {acc} focusable="false">{cuerpo}</svg>')


def registrar(templates) -> None:
    """Hace disponible {{ icono(...) }} en las plantillas de un router."""
    templates.env.globals["icono"] = icono
