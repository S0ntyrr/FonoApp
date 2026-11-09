"""Dibujos de palabras (animales, comida, naturaleza, objetos) para los juegos.

Todos usan viewBox 0 0 64 64 y el mismo estilo plano de app/iconos.py.
Pensados para que un niño que aún no lee reconozca la palabra por el dibujo.
"""

O = "#1f3347"  # contorno / ojos


def _ojos(x1, x2, y, r=3):
    return (f'<circle cx="{x1}" cy="{y}" r="{r}" fill="{O}"/><circle cx="{x2}" cy="{y}" r="{r}" fill="{O}"/>'
            f'<circle cx="{x1 + 1}" cy="{y - 1}" r="{r * .35:.1f}" fill="#fff"/><circle cx="{x2 + 1}" cy="{y - 1}" r="{r * .35:.1f}" fill="#fff"/>')


ANIMALES = {
    "gato": '<path d="M12 30L10 8l14 10zM52 30l2-22-14 10z" fill="#f0a24a"/><path d="M14 26l-1-12 8 6zM50 26l1-12-8 6z" fill="#ffc9a1"/>'
            '<ellipse cx="32" cy="36" rx="22" ry="20" fill="#f0a24a"/><ellipse cx="32" cy="44" rx="11" ry="8" fill="#ffe2c4"/>'
            + _ojos(23, 41, 33) + '<path d="M29 40h6l-3 3z" fill="#e0528f"/><path d="M32 43q-3 4-6 2M32 43q3 4 6 2" fill="none" stroke="' + O + '" stroke-width="1.8" stroke-linecap="round"/>'
            '<path d="M8 40h12M8 46l12-3M56 40H44M56 46l-12-3" stroke="' + O + '" stroke-width="1.5" stroke-linecap="round"/>',
    "cerdo": '<path d="M14 18l4 12-12-2zM50 18l-4 12 12-2z" fill="#f48fb1"/><circle cx="32" cy="34" r="22" fill="#f8bbd0"/>'
             '<ellipse cx="32" cy="41" rx="10" ry="7" fill="#f48fb1"/><ellipse cx="28" cy="41" rx="2" ry="3" fill="#c2185b"/><ellipse cx="36" cy="41" rx="2" ry="3" fill="#c2185b"/>'
             + _ojos(23, 41, 29),
    "rana": '<circle cx="20" cy="18" r="9" fill="#5cbf5c"/><circle cx="44" cy="18" r="9" fill="#5cbf5c"/>'
            '<ellipse cx="32" cy="38" rx="26" ry="18" fill="#5cbf5c"/>' + _ojos(20, 44, 18, 4) +
            '<path d="M14 40q18 14 36 0" fill="none" stroke="#2e7d32" stroke-width="3" stroke-linecap="round"/>'
            '<circle cx="16" cy="34" r="3" fill="#f48fb1" opacity=".7"/><circle cx="48" cy="34" r="3" fill="#f48fb1" opacity=".7"/>',
    "elefante": '<ellipse cx="12" cy="30" rx="10" ry="14" fill="#9fb3c4"/><ellipse cx="52" cy="30" rx="10" ry="14" fill="#9fb3c4"/>'
                '<circle cx="32" cy="28" r="18" fill="#b8c7d6"/><path d="M27 36q0 22 10 22q4 0 4-4q-5 0-6-6l-1-12z" fill="#b8c7d6"/>'
                + _ojos(25, 39, 26) + '<path d="M22 40q-4 4 0 8M42 40q4 4 0 8" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round"/>',
    "leon": '<circle cx="32" cy="32" r="28" fill="#c77d2b"/><g fill="#a5621c"><circle cx="10" cy="22" r="7"/><circle cx="54" cy="22" r="7"/><circle cx="8" cy="40" r="7"/><circle cx="56" cy="40" r="7"/><circle cx="32" cy="6" r="7"/><circle cx="18" cy="9" r="7"/><circle cx="46" cy="9" r="7"/></g>'
            '<circle cx="32" cy="34" r="18" fill="#f2b84b"/><ellipse cx="32" cy="42" rx="9" ry="6" fill="#ffe2a8"/>' + _ojos(25, 39, 31) +
            '<path d="M29 38h6l-3 3z" fill="' + O + '"/><path d="M32 41q-3 3-5 1M32 41q3 3 5 1" fill="none" stroke="' + O + '" stroke-width="1.6"/>',
    "pinguino": '<ellipse cx="32" cy="36" rx="20" ry="24" fill="#263544"/><ellipse cx="32" cy="40" rx="13" ry="18" fill="#fff"/>'
                '<ellipse cx="32" cy="22" rx="11" ry="9" fill="#fff"/>' + _ojos(28, 36, 22, 2.5) +
                '<path d="M28 27h8l-4 5z" fill="#f2a900"/><path d="M22 58h8l-4-3zM34 58h8l-4-3z" fill="#f2a900"/>',
    "tortuga": '<ellipse cx="54" cy="38" rx="7" ry="6" fill="#8bc34a"/><circle cx="56" cy="36" r="1.6" fill="' + O + '"/>'
               '<rect x="14" y="40" width="7" height="10" rx="3" fill="#8bc34a"/><rect x="38" y="40" width="7" height="10" rx="3" fill="#8bc34a"/>'
               '<path d="M8 42q0-26 24-26t24 26z" fill="#5d8f3c"/><path d="M18 42l6-12h16l6 12M24 30l8-8 8 8" fill="none" stroke="#3e6b28" stroke-width="2.5"/>',
    "zorro": '<path d="M8 10l16 12-10 10zM56 10L40 22l10 10z" fill="#e8742a"/><path d="M8 22q24 46 48 0q-10 6-24 6t-24-6z" fill="#e8742a"/>'
             '<path d="M20 34q12 22 24 0q-12 6-24 0z" fill="#fff"/>' + _ojos(24, 40, 30) + '<circle cx="32" cy="45" r="3" fill="' + O + '"/>',
    "caballo": '<path d="M20 58V36q-8-4-8-14Q12 6 30 6q20 0 22 16l2 14q0 8-8 8h-8v14z" fill="#a0673a"/>'
               '<path d="M30 6q-10 4-12 20l8-2q0-10 4-18z" fill="#5d3a1a"/><ellipse cx="46" cy="40" rx="7" ry="5" fill="#c99067"/>'
               '<circle cx="44" cy="40" r="1.4" fill="' + O + '"/><circle cx="49" cy="40" r="1.4" fill="' + O + '"/><circle cx="38" cy="20" r="3" fill="' + O + '"/>'
               '<path d="M32 6l4-4 2 6z" fill="#a0673a"/>',
    "oso": '<circle cx="14" cy="16" r="9" fill="#8a5a35"/><circle cx="50" cy="16" r="9" fill="#8a5a35"/><circle cx="14" cy="16" r="4.5" fill="#c99067"/><circle cx="50" cy="16" r="4.5" fill="#c99067"/>'
           '<circle cx="32" cy="34" r="22" fill="#8a5a35"/><ellipse cx="32" cy="42" rx="11" ry="8" fill="#c99067"/>' + _ojos(24, 40, 30) +
           '<ellipse cx="32" cy="39" rx="4" ry="3" fill="' + O + '"/><path d="M32 42q-3 3-5 1M32 42q3 3 5 1" fill="none" stroke="' + O + '" stroke-width="1.6"/>',
    "pajaro": '<path d="M8 34q8-4 14 2l-6 6z" fill="#2e86de"/><ellipse cx="32" cy="36" rx="20" ry="16" fill="#4aa3f0"/><circle cx="42" cy="24" r="11" fill="#4aa3f0"/>'
              '<ellipse cx="30" cy="40" rx="11" ry="7" fill="#2e86de"/><circle cx="45" cy="22" r="2.6" fill="' + O + '"/><path d="M52 24l9 2-9 3z" fill="#f2a900"/>'
              '<path d="M26 52l-2 6M34 52l2 6" stroke="#f2a900" stroke-width="2.5" stroke-linecap="round"/>',
    "pato": '<ellipse cx="30" cy="42" rx="24" ry="14" fill="#ffd54a"/><circle cx="42" cy="22" r="12" fill="#ffd54a"/>'
            '<path d="M52 22q10 0 10 4t-10 2z" fill="#f57c00"/><circle cx="44" cy="19" r="2.6" fill="' + O + '"/>'
            '<path d="M14 38q10 10 22 2" fill="none" stroke="#e9b400" stroke-width="3" stroke-linecap="round"/><path d="M6 36l-4-4 8 1z" fill="#ffd54a"/>',
    "pez": '<path d="M44 32L60 18v28z" fill="#ff8a3d"/><ellipse cx="28" cy="32" rx="22" ry="15" fill="#ffab40"/>'
           '<path d="M20 20q4 12 0 24M30 18q4 14 0 28" fill="none" stroke="#ff8a3d" stroke-width="2.5"/>'
           '<circle cx="14" cy="28" r="3.2" fill="' + O + '"/><circle cx="15" cy="27" r="1.1" fill="#fff"/><path d="M8 36q3 2 6 0" stroke="' + O + '" stroke-width="2" fill="none" stroke-linecap="round"/>',
    "mariposa": '<path d="M32 30Q20 2 8 12Q2 26 30 32z" fill="#8e6bd6"/><path d="M32 30Q44 2 56 12Q62 26 34 32z" fill="#8e6bd6"/>'
                '<path d="M30 34Q10 36 12 50q8 8 18-12zM34 34q20 2 18 16-8 8-18-12z" fill="#e0528f"/>'
                '<circle cx="18" cy="18" r="4" fill="#fff" opacity=".6"/><circle cx="46" cy="18" r="4" fill="#fff" opacity=".6"/>'
                '<rect x="30" y="20" width="4" height="28" rx="2" fill="' + O + '"/><path d="M31 21q-4-10-8-12M33 21q4-10 8-12" stroke="' + O + '" stroke-width="2" fill="none" stroke-linecap="round"/>',
    "murcielago": '<path d="M32 26Q20 10 2 18q8 4 6 12 6-4 10 2 4-6 8 0 4-4 6-6zM32 26q12-16 30-8-8 4-6 12-6-4-10 2-4-6-8 0-4-4-6-6z" fill="#5a4a7a"/>'
                  '<ellipse cx="32" cy="32" rx="9" ry="12" fill="#5a4a7a"/><path d="M25 22l2-8 4 6zM39 22l-2-8-4 6z" fill="#5a4a7a"/>'
                  '<circle cx="29" cy="28" r="2" fill="#ffd54a"/><circle cx="35" cy="28" r="2" fill="#ffd54a"/><path d="M30 35l1 3 1-3M32 35l1 3 1-3" fill="#fff"/>',
    "buho": '<path d="M12 12l10 8M52 12l-10 8" stroke="#8a5a35" stroke-width="5" stroke-linecap="round"/><ellipse cx="32" cy="36" rx="22" ry="24" fill="#a0673a"/>'
            '<ellipse cx="32" cy="44" rx="13" ry="13" fill="#e8c9a0"/><circle cx="23" cy="26" r="9" fill="#fff"/><circle cx="41" cy="26" r="9" fill="#fff"/>'
            '<circle cx="23" cy="26" r="4.5" fill="' + O + '"/><circle cx="41" cy="26" r="4.5" fill="' + O + '"/><path d="M29 33h6l-3 5z" fill="#f2a900"/>'
            '<path d="M24 46l3 3 3-3 2 3 2-3 3 3 3-3" fill="none" stroke="#a0673a" stroke-width="1.6"/>',
    "aguila": '<path d="M4 30q14-10 28-4 14-6 28 4-10 0-14 6-6-4-14-2-8-2-14 2-4-6-14-6z" fill="#6d4c2e"/>'
              '<circle cx="32" cy="22" r="12" fill="#fff"/><circle cx="36" cy="20" r="2.6" fill="' + O + '"/><path d="M40 22q10 0 6 8l-6-4z" fill="#f2a900"/>'
              '<path d="M24 34h16l-4 22h-8z" fill="#6d4c2e"/>',
    "abeja": '<ellipse cx="22" cy="18" rx="10" ry="8" fill="#e3f4fd" stroke="#9ed6f7" stroke-width="2"/><ellipse cx="40" cy="16" rx="10" ry="8" fill="#e3f4fd" stroke="#9ed6f7" stroke-width="2"/>'
             '<ellipse cx="32" cy="38" rx="22" ry="16" fill="#ffd54a"/><path d="M24 23v30M34 22v32M44 25v26" stroke="' + O + '" stroke-width="5"/>'
             '<circle cx="14" cy="34" r="2.6" fill="' + O + '"/><path d="M54 38l8 2-8 3z" fill="' + O + '"/>',
    "grillo": '<ellipse cx="30" cy="34" rx="20" ry="11" fill="#7cb342"/><circle cx="50" cy="30" r="8" fill="#7cb342"/><circle cx="53" cy="28" r="2" fill="' + O + '"/>'
              '<path d="M54 22q4-14 8-16M50 22q-2-14 2-18" stroke="#558b2f" stroke-width="2" fill="none" stroke-linecap="round"/>'
              '<path d="M22 40l-8 16M30 44l-2 12M38 42l6 14M18 30q-6-10 8-14" stroke="#558b2f" stroke-width="3" fill="none" stroke-linecap="round"/>',
    "mariquita": '<circle cx="32" cy="14" r="9" fill="' + O + '"/><circle cx="32" cy="36" r="22" fill="#e53935"/><path d="M32 14v44" stroke="' + O + '" stroke-width="3"/>'
                 '<g fill="' + O + '"><circle cx="22" cy="28" r="4"/><circle cx="42" cy="28" r="4"/><circle cx="20" cy="44" r="4"/><circle cx="44" cy="44" r="4"/></g>'
                 '<circle cx="28" cy="12" r="2" fill="#fff"/><circle cx="36" cy="12" r="2" fill="#fff"/>',
    "gusano": '<g fill="#8bc34a"><circle cx="10" cy="44" r="8"/><circle cx="20" cy="38" r="8"/><circle cx="30" cy="42" r="8"/><circle cx="40" cy="36" r="8"/></g>'
              '<circle cx="50" cy="28" r="10" fill="#9ccc65"/>' + _ojos(47, 54, 26, 2) + '<path d="M47 32q3 3 6 0" stroke="' + O + '" stroke-width="2" fill="none" stroke-linecap="round"/>'
              '<path d="M46 19l-2-6M54 19l2-6" stroke="#558b2f" stroke-width="2" stroke-linecap="round"/>',
    "pollito": '<circle cx="32" cy="38" r="20" fill="#ffd54a"/><circle cx="32" cy="20" r="12" fill="#ffd54a"/>'
               + _ojos(27, 37, 18, 2.4) + '<path d="M29 23h6l-3 4z" fill="#f57c00"/><path d="M30 8q2-6 4 0" fill="#ffd54a"/>'
               '<path d="M14 36q-6 4 2 8M50 36q6 4-2 8" fill="#ffca28"/><path d="M26 58l-2 4M38 58l2 4" stroke="#f57c00" stroke-width="2.5" stroke-linecap="round"/>',
    "gallo": '<path d="M24 10q2-8 6-2 2-8 6 0 4-6 5 4z" fill="#e53935"/><ellipse cx="34" cy="40" rx="20" ry="16" fill="#fff" stroke="#e0e6ec" stroke-width="2"/>'
             '<circle cx="34" cy="20" r="10" fill="#fff" stroke="#e0e6ec" stroke-width="2"/><circle cx="37" cy="18" r="2.4" fill="' + O + '"/>'
             '<path d="M43 20l8 3-8 3z" fill="#f2a900"/><path d="M38 27q2 6-2 6-2-4 2-6z" fill="#e53935"/>'
             '<path d="M14 36q-12-12 2-22-2 10 6 14M14 40q-14-2-10-14 4 8 12 8" fill="#2bb673"/><path d="M30 56v6M38 56v6" stroke="#f2a900" stroke-width="3"/>',
    "serpiente": '<path d="M8 50q10 8 18 0t16 0 14-10q4-10-6-12H30q-8 0-8-8t8-8h14" fill="none" stroke="#5cbf5c" stroke-width="9" stroke-linecap="round"/>'
                 '<circle cx="48" cy="12" r="8" fill="#5cbf5c"/><circle cx="50" cy="10" r="2" fill="' + O + '"/><path d="M56 13l6 1-4 2 4 2-6-1" stroke="#e53935" stroke-width="1.6" fill="none"/>',
    "gorila": '<circle cx="12" cy="30" r="6" fill="#3b3b3b"/><circle cx="52" cy="30" r="6" fill="#3b3b3b"/><circle cx="32" cy="30" r="22" fill="#3b3b3b"/>'
              '<path d="M18 30q0-12 14-12t14 12q4 18-14 22-18-4-14-22z" fill="#8d7b6a"/>' + _ojos(26, 38, 28) +
              '<path d="M28 36q4-2 8 0" stroke="' + O + '" stroke-width="3" fill="none"/><path d="M26 44q6 4 12 0" stroke="' + O + '" stroke-width="2.5" fill="none" stroke-linecap="round"/>',
    "loro": '<path d="M30 58q-4-10 2-16l6 16z" fill="#2e86de"/><ellipse cx="32" cy="34" rx="14" ry="18" fill="#2bb673"/><circle cx="34" cy="18" r="12" fill="#e53935"/>'
            '<circle cx="38" cy="16" r="3" fill="#fff"/><circle cx="38" cy="16" r="1.6" fill="' + O + '"/><path d="M44 16q8 2 4 12-2-6-6-6z" fill="#f2a900"/>'
            '<path d="M22 30q-6 10 4 18" fill="#f2b400"/>',
    "mono": '<circle cx="12" cy="30" r="8" fill="#8a5a35"/><circle cx="52" cy="30" r="8" fill="#8a5a35"/><circle cx="12" cy="30" r="4" fill="#e8c9a0"/><circle cx="52" cy="30" r="4" fill="#e8c9a0"/>'
            '<circle cx="32" cy="30" r="20" fill="#8a5a35"/><path d="M20 28q0-8 6-8 6 0 6 6 0-6 6-6 6 0 6 8 4 16-12 20-16-4-12-20z" fill="#e8c9a0"/>'
            + _ojos(26, 38, 28) + '<path d="M26 40q6 5 12 0" stroke="' + O + '" stroke-width="2.5" fill="none" stroke-linecap="round"/>',
    "raton": '<circle cx="16" cy="18" r="11" fill="#b8c7d6"/><circle cx="48" cy="18" r="11" fill="#b8c7d6"/><circle cx="16" cy="18" r="6" fill="#f8bbd0"/><circle cx="48" cy="18" r="6" fill="#f8bbd0"/>'
             '<path d="M32 58q-20-6-18-26 2-12 18-12t18 12q2 20-18 26z" fill="#cfd8e2"/>' + _ojos(25, 39, 34) +
             '<circle cx="32" cy="48" r="3.5" fill="#e0528f"/><path d="M18 46h8M18 51l8-2M46 46h-8M46 51l-8-2" stroke="' + O + '" stroke-width="1.4" stroke-linecap="round"/>',
    "foca": '<path d="M8 50q4-30 30-34 18 0 20 14 0 8-8 10-10 10-26 12q-8 4-16-2z" fill="#90a4ae"/>'
            '<circle cx="46" cy="26" r="2.6" fill="' + O + '"/><ellipse cx="54" cy="32" rx="3" ry="2" fill="' + O + '"/>'
            '<path d="M50 36l8 2M50 38l7 4" stroke="' + O + '" stroke-width="1.3"/><path d="M4 52q6-10 10-2zM22 52q4 8-8 6z" fill="#78909c"/>'
            '<circle cx="54" cy="10" r="6" fill="#e53935"/>',
    "jirafa": '<path d="M30 60V24h10v36z" fill="#f2b84b"/><path d="M26 14q0-8 10-8h4q8 0 8 8v6q0 6-8 6h-6q-8 0-8-6z" fill="#f2b84b"/>'
              '<path d="M30 6V0M40 6V0" stroke="#a0673a" stroke-width="3" stroke-linecap="round"/><circle cx="34" cy="13" r="2.4" fill="' + O + '"/>'
              '<ellipse cx="44" cy="20" rx="5" ry="4" fill="#e8c9a0"/><g fill="#a0673a"><circle cx="33" cy="32" r="3"/><circle cx="37" cy="42" r="3"/><circle cx="32" cy="50" r="3"/><circle cx="37" cy="56" r="2.5"/></g>',
    "toro": '<path d="M14 20Q2 18 4 6q6 8 16 8zM50 20q12-2 10-14-6 8-16 8z" fill="#f3e5c0"/><path d="M14 22q0-10 18-10t18 10q4 24-18 32-22-8-18-32z" fill="#6d4c2e"/>'
            '<ellipse cx="32" cy="44" rx="12" ry="9" fill="#c99067"/><circle cx="27" cy="44" r="2" fill="' + O + '"/><circle cx="37" cy="44" r="2" fill="' + O + '"/>'
            + _ojos(24, 40, 28) + '<path d="M28 52q4 4 8 0" fill="none" stroke="#f2b400" stroke-width="3"/>',
    "inflar": '<circle cx="32" cy="34" r="24" fill="#ffd9b8" stroke="#e8a77a" stroke-width="2.5"/><path d="M10 28Q14 6 32 7Q50 6 54 28Q46 16 32 16Q18 16 10 28Z" fill="#6b3f1f"/>'
              + _ojos(23, 41, 30) + '<circle cx="14" cy="42" r="8" fill="#ffb3a1"/><circle cx="50" cy="42" r="8" fill="#ffb3a1"/>'
              '<path d="M27 45q5-3 10 0q-5 3-10 0z" fill="#b5523b"/>',
}

COMIDA = {
    "manzana": '<path d="M32 18q-14-8-22 4-8 16 6 32 8 8 16 4 8 4 16-4 14-16 6-32-8-12-22-4z" fill="#e53935"/>'
               '<path d="M32 18q0-8 4-12" stroke="#6d4c2e" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M36 12q10-6 14 2-8 4-14-2z" fill="#5cbf5c"/>'
               '<ellipse cx="20" cy="28" rx="4" ry="7" fill="#fff" opacity=".35"/>',
    "pera": '<path d="M32 12q-6 0-6 12-14 8-12 22 2 14 18 14t18-14q2-14-12-22 0-12-6-12z" fill="#c0ca33"/>'
            '<path d="M32 12q0-6 2-8" stroke="#6d4c2e" stroke-width="3" stroke-linecap="round"/><path d="M34 8q8-4 12 2-6 4-12-2z" fill="#5cbf5c"/>'
            '<ellipse cx="22" cy="40" rx="3" ry="6" fill="#fff" opacity=".35"/>',
    "pan": '<path d="M8 30q0-16 24-16t24 16q0 4-4 4v16q0 6-6 6H18q-6 0-6-6V34q-4 0-4-4z" fill="#e0a458"/>'
           '<path d="M14 34v16q0 2 2 2h32q2 0 2-2V34" fill="#f5d7a1"/><path d="M22 22l4 4M32 20l4 4M42 22l4 4" stroke="#b77b35" stroke-width="2.5" stroke-linecap="round"/>',
    "papa": '<path d="M10 34q-2-18 18-22 24-4 28 14 4 18-16 26-26 6-30-18z" fill="#c9a26b"/>'
            '<g fill="#a07c46"><circle cx="22" cy="26" r="2"/><circle cx="40" cy="22" r="2"/><circle cx="44" cy="38" r="2"/><circle cx="26" cy="42" r="2"/></g>',
    "sopa": '<path d="M24 14q-4-6 0-10M32 14q-4-6 0-10M40 14q-4-6 0-10" stroke="#b0bec5" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
            '<ellipse cx="32" cy="28" rx="26" ry="6" fill="#ff9e3d"/><path d="M6 28q2 28 26 28t26-28" fill="#e53935"/>'
            '<path d="M46 26L60 6" stroke="#9fb3c4" stroke-width="4" stroke-linecap="round"/><circle cx="22" cy="27" r="2" fill="#5cbf5c"/><circle cx="34" cy="29" r="2" fill="#f2b400"/>',
    "sal": '<path d="M20 22h24l-2 34q0 4-4 4H26q-4 0-4-4z" fill="#eef3f8" stroke="#b0bec5" stroke-width="2"/>'
           '<path d="M20 22q0-14 12-14t12 14z" fill="#9fb3c4"/><g fill="#5a6b7b"><circle cx="28" cy="15" r="1.5"/><circle cx="32" cy="12" r="1.5"/><circle cx="36" cy="15" r="1.5"/></g>'
           '<text x="32" y="46" font-size="14" font-weight="900" text-anchor="middle" fill="#9fb3c4" font-family="Arial,sans-serif">S</text>',
    "galleta": '<circle cx="32" cy="32" r="26" fill="#d9a066"/><circle cx="32" cy="32" r="26" fill="none" stroke="#b77b35" stroke-width="2"/>'
               '<g fill="#5d3a1a"><circle cx="22" cy="22" r="4"/><circle cx="40" cy="20" r="3.5"/><circle cx="44" cy="38" r="4"/><circle cx="26" cy="42" r="3.5"/><circle cx="34" cy="31" r="3"/></g>',
    "helado": '<path d="M20 30l12 30 12-30z" fill="#e0a458"/><path d="M24 34l14 10M22 40l10-4M34 40l8 4" stroke="#b77b35" stroke-width="1.6"/>'
              '<circle cx="32" cy="22" r="13" fill="#f8bbd0"/><circle cx="24" cy="28" r="7" fill="#f8bbd0"/><circle cx="40" cy="28" r="7" fill="#f8bbd0"/>'
              '<circle cx="32" cy="8" r="4" fill="#e53935"/>',
    "cafe": '<path d="M24 14q-4-6 0-10M34 14q-4-6 0-10" stroke="#b0bec5" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
            '<path d="M10 20h36v20q0 14-18 14T10 40z" fill="#fff" stroke="#9fb3c4" stroke-width="2.5"/><ellipse cx="28" cy="21" rx="17" ry="3" fill="#6d4c2e"/>'
            '<path d="M46 26h4q8 0 8 7t-8 7h-4" fill="none" stroke="#9fb3c4" stroke-width="4"/><ellipse cx="28" cy="58" rx="22" ry="3" fill="#dfe6ee"/>',
    "estufa": '<ellipse cx="28" cy="34" rx="22" ry="20" fill="#455a64"/><ellipse cx="28" cy="34" rx="16" ry="14" fill="#607d8b"/>'
              '<path d="M48 34h14" stroke="#455a64" stroke-width="7" stroke-linecap="round"/>'
              '<ellipse cx="26" cy="34" rx="8" ry="7" fill="#fff"/><circle cx="26" cy="34" r="4" fill="#ffc107"/>',
    "tenedor": '<path d="M22 4v16q0 8 6 8v32" stroke="#9fb3c4" stroke-width="5" stroke-linecap="round" fill="none"/><path d="M16 4v14M28 4v14" stroke="#9fb3c4" stroke-width="3.5" stroke-linecap="round"/>'
               '<path d="M42 4q8 6 8 20 0 6-6 6v30" stroke="#9fb3c4" stroke-width="5" fill="none" stroke-linecap="round"/>',
}


NATURALEZA = {
    "sol": '<g stroke="#f2b400" stroke-width="4" stroke-linecap="round"><path d="M32 2v8M32 54v8M2 32h8M54 32h8M10 10l6 6M48 48l6 6M54 10l-6 6M16 48l-6 6"/></g>'
           '<circle cx="32" cy="32" r="16" fill="#ffd54a"/>' + _ojos(26, 38, 30, 2) + '<path d="M26 37q6 5 12 0" stroke="' + O + '" stroke-width="2" fill="none" stroke-linecap="round"/>',
    "luna": '<path d="M42 6a26 26 0 1 0 16 40A22 22 0 0 1 42 6z" fill="#ffd54a"/><circle cx="28" cy="28" r="2.4" fill="' + O + '"/>'
            '<path d="M24 38q5 4 10 0" stroke="' + O + '" stroke-width="2" fill="none" stroke-linecap="round"/><circle cx="18" cy="44" r="3" fill="#f2b400"/>',
    "arcoiris": '<g fill="none" stroke-width="5"><path d="M6 50a26 26 0 0152 0" stroke="#e53935"/><path d="M11 50a21 21 0 0142 0" stroke="#f57c00"/>'
                '<path d="M16 50a16 16 0 0132 0" stroke="#f2b400"/><path d="M21 50a11 11 0 0122 0" stroke="#2bb673"/><path d="M26 50a6 6 0 0112 0" stroke="#2e86de"/></g>'
                '<g fill="#fff"><circle cx="8" cy="52" r="6"/><circle cx="14" cy="54" r="5"/><circle cx="56" cy="52" r="6"/><circle cx="50" cy="54" r="5"/></g>',
    "nube": '<g fill="#e3f0fa"><circle cx="22" cy="36" r="12"/><circle cx="36" cy="28" r="15"/><circle cx="48" cy="38" r="10"/><rect x="12" y="36" width="44" height="12" rx="6"/></g>'
            '<path d="M14 46h40" stroke="#cfe3f2" stroke-width="2"/>',
    "lluvia": '<g fill="#b0c4d8"><circle cx="22" cy="24" r="11"/><circle cx="36" cy="18" r="13"/><circle cx="47" cy="27" r="9"/><rect x="12" y="24" width="44" height="11" rx="5.5"/></g>'
              '<g stroke="#2e86de" stroke-width="3.5" stroke-linecap="round"><path d="M20 42l-3 8M32 42l-3 8M44 42l-3 8M26 52l-2 6M38 52l-2 6"/></g>',
    "rayo": '<path d="M36 2L12 36h16l-6 26 26-36H32z" fill="#ffd54a" stroke="#f2a900" stroke-width="2" stroke-linejoin="round"/>',
    "copo": '<g stroke="#4aa3f0" stroke-width="4" stroke-linecap="round"><path d="M32 4v56M8 18l48 28M8 46l48-28"/>'
            '<path d="M26 8l6 6 6-6M26 56l6-6 6 6M8 26l8-2-2-8M56 38l-8 2 2 8M8 38l8 2-2 8M56 26l-8-2 2-8"/></g>',
    "solnube": '<g stroke="#f2b400" stroke-width="3.5" stroke-linecap="round"><path d="M24 2v6M6 20h6M10 6l4 4M38 6l-4 4"/></g><circle cx="24" cy="22" r="12" fill="#ffd54a"/>'
               '<g fill="#e3f0fa"><circle cx="30" cy="40" r="11"/><circle cx="44" cy="34" r="13"/><circle cx="54" cy="44" r="8"/><rect x="20" y="40" width="40" height="12" rx="6"/></g>',
    "tornado": '<g stroke="#90a4ae" stroke-width="5" stroke-linecap="round" fill="none"><path d="M6 10h52"/><path d="M12 20h40"/><path d="M18 30h28"/><path d="M24 40h18"/><path d="M28 50h10"/><path d="M30 58h4"/></g>',
    "ola": '<path d="M2 40q8-10 16 0t16 0 16 0 14 0v22H2z" fill="#2e86de"/><path d="M2 48q8-8 16 0t16 0 16 0 14 0" stroke="#9ed6f7" stroke-width="3" fill="none"/>'
           '<path d="M10 34q6-22 26-20 10 2 8 10-6-6-12 0 4 8-8 10" fill="#4aa3f0"/>',
    "hoja": '<path d="M10 54Q8 14 54 8q4 42-44 46z" fill="#5cbf5c"/><path d="M10 54L44 18M24 40l-2-12M32 32l10 2M20 46l12 2" stroke="#2e7d32" stroke-width="2.5" stroke-linecap="round"/>',
    "fuego": '<path d="M32 4q6 14 16 22 8 8 8 18 0 16-24 18Q8 60 8 44q0-12 10-18 0 10 6 12-2-20 8-34z" fill="#f57c00"/>'
             '<path d="M32 30q4 8 10 14 4 6-2 12-4 4-8 4-10 0-12-8 0-6 6-10 0 6 4 6-2-10 2-18z" fill="#ffd54a"/>',
    "arbol": '<rect x="28" y="38" width="8" height="22" rx="2" fill="#8a5a35"/><circle cx="32" cy="24" r="18" fill="#43a047"/>'
             '<circle cx="20" cy="32" r="11" fill="#43a047"/><circle cx="44" cy="32" r="11" fill="#43a047"/><circle cx="26" cy="18" r="6" fill="#66bb6a"/>',
    "rosa": '<path d="M32 34v26" stroke="#2e7d32" stroke-width="4"/><path d="M32 48q-12-8-16 0 8 6 16 0zM32 44q10-8 14 0-8 6-14 0z" fill="#43a047"/>'
            '<circle cx="32" cy="22" r="15" fill="#e53935"/><path d="M32 12q-10 4-6 12 4 6 10 2 6-6-2-12M26 20q8 0 10 8" fill="none" stroke="#b71c1c" stroke-width="2.5" stroke-linecap="round"/>',
    "flor": '<path d="M32 36v24" stroke="#2e7d32" stroke-width="4"/><path d="M32 50q-12-8-16 0 8 6 16 0z" fill="#43a047"/>'
            '<g fill="#f48fb1"><circle cx="32" cy="12" r="9"/><circle cx="20" cy="22" r="9"/><circle cx="44" cy="22" r="9"/><circle cx="24" cy="34" r="9"/><circle cx="40" cy="34" r="9"/></g>'
            '<circle cx="32" cy="24" r="7" fill="#ffd54a"/>',
    "rio": '<path d="M2 26l14-14 10 8 12-14 24 20v6H2z" fill="#81c784"/><path d="M0 30h64v34H0z" fill="#a5d6a7"/>'
           '<path d="M24 30q-10 10 4 16t-6 18h22q16-10 2-18t6-16z" fill="#4aa3f0"/><path d="M30 40q4 2 8 0M28 52q4 2 8 0" stroke="#e3f4fd" stroke-width="2" fill="none"/>',
    "roca": '<path d="M6 52l8-24 14-12 18 4 12 18 2 14z" fill="#9e9e9e"/><path d="M14 28l14-12 6 14-10 8z" fill="#bdbdbd"/>'
            '<path d="M34 30l12-10 12 18" fill="none" stroke="#757575" stroke-width="2"/><path d="M4 54h58" stroke="#757575" stroke-width="3" stroke-linecap="round"/>',
    "playa": '<path d="M0 44q32-10 64 0v20H0z" fill="#f3dcb3"/><path d="M0 40q16-6 32 0t32 0v6q-16-4-32 0T0 46z" fill="#4aa3f0"/>'
             '<circle cx="50" cy="14" r="8" fill="#ffd54a"/><path d="M18 46V18" stroke="#8a5a35" stroke-width="3"/><path d="M18 18q-12 0-14 8 8-6 14-4 6-2 14 4-2-8-14-8z" fill="#43a047"/>',
}

VEHICULOS = {
    "carro": '<path d="M6 40v-8q0-4 4-5l8-2 6-10q2-3 6-3h12q4 0 6 3l6 10 4 2q4 1 4 5v8z" fill="#e53935"/>'
             '<path d="M24 25l4-8h6v8zM38 25v-8h4l4 8z" fill="#b3e5fc"/><circle cx="18" cy="42" r="7" fill="' + O + '"/><circle cx="46" cy="42" r="7" fill="' + O + '"/>'
             '<circle cx="18" cy="42" r="2.5" fill="#9fb3c4"/><circle cx="46" cy="42" r="2.5" fill="#9fb3c4"/><rect x="52" y="30" width="4" height="4" rx="1" fill="#ffd54a"/>',
    "tren": '<rect x="10" y="10" width="34" height="34" rx="6" fill="#2e86de"/><rect x="15" y="15" width="11" height="10" rx="2" fill="#b3e5fc"/><rect x="29" y="15" width="11" height="10" rx="2" fill="#b3e5fc"/>'
            '<rect x="44" y="24" width="12" height="20" rx="3" fill="#e53935"/><rect x="48" y="12" width="6" height="12" fill="' + O + '"/>'
            '<circle cx="20" cy="48" r="6" fill="' + O + '"/><circle cx="38" cy="48" r="6" fill="' + O + '"/><circle cx="52" cy="48" r="5" fill="' + O + '"/>'
            '<path d="M4 58h56" stroke="#8a5a35" stroke-width="3"/><circle cx="52" cy="6" r="4" fill="#cfd8e2"/>',
    "avion": '<path d="M4 34l52-18q6-2 6 4t-6 6L30 36l-8 18h-6l2-16-10 2-4 6H2l2-10z" fill="#4aa3f0"/>'
             '<path d="M26 26l-10-12h6l16 8z" fill="#2e86de"/><circle cx="48" cy="24" r="2" fill="#fff"/><circle cx="42" cy="26" r="2" fill="#fff"/>',
    "barco": '<path d="M4 38h56l-8 16H12z" fill="#e53935"/><rect x="16" y="24" width="28" height="14" rx="2" fill="#fff" stroke="#cfd8e2" stroke-width="2"/>'
             '<rect x="26" y="12" width="8" height="12" fill="#f2b400"/><g fill="#4aa3f0"><circle cx="22" cy="31" r="2.5"/><circle cx="32" cy="31" r="2.5"/><circle cx="42" cy="31" r="2.5"/></g>'
             '<path d="M2 58q8-4 15 0t15 0 15 0 15 0" stroke="#4aa3f0" stroke-width="3" fill="none"/>',
    "velero": '<path d="M30 6v40" stroke="#8a5a35" stroke-width="3"/><path d="M33 8l20 34H33z" fill="#fff" stroke="#cfd8e2" stroke-width="2"/><path d="M27 14L10 42h17z" fill="#e53935"/>'
              '<path d="M6 46h52l-8 10H14z" fill="#8a5a35"/><path d="M2 60q8-4 15 0t15 0 15 0 15 0" stroke="#4aa3f0" stroke-width="3" fill="none"/>',
    "bici": '<circle cx="14" cy="42" r="11" fill="none" stroke="' + O + '" stroke-width="4"/><circle cx="50" cy="42" r="11" fill="none" stroke="' + O + '" stroke-width="4"/>'
            '<path d="M14 42l12-18h16l8 18M26 24l8 18 8-18M24 18h8M42 24l-2-8h6" fill="none" stroke="#2bb673" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>',
    "bote": '<path d="M4 38h56q-4 14-14 14H18Q8 52 4 38z" fill="#a0673a"/><circle cx="32" cy="22" r="6" fill="#ffd9b8"/><path d="M26 38q0-10 6-10t6 10z" fill="#e53935"/>'
            '<path d="M14 26l36 22" stroke="#6d4c2e" stroke-width="3" stroke-linecap="round"/><path d="M2 58q8-4 15 0t15 0 15 0 15 0" stroke="#4aa3f0" stroke-width="3" fill="none"/>',
}

OBJETOS = {
    "silla": '<rect x="18" y="6" width="28" height="26" rx="4" fill="#c77d2b"/><rect x="14" y="30" width="36" height="8" rx="3" fill="#a5621c"/>'
             '<path d="M18 38v20M46 38v20" stroke="#a5621c" stroke-width="5" stroke-linecap="round"/><path d="M24 12v14M32 12v14M40 12v14" stroke="#a5621c" stroke-width="2"/>',
    "mano": '<g transform="translate(-4 -6) scale(.95)"><path d="M30 70Q18 58 16 46Q15 40 21 41Q25 42 28 50L28 18Q28 12 33 12Q38 12 38 18L38 38L38 14Q38 9 43 9Q48 9 48 14L48 40L48 18Q48 13 53 13Q58 13 58 18L58 42Q58 26 62 26Q67 26 67 31L67 56Q67 66 60 72Z" fill="#ffd9b8" stroke="#c98a5e" stroke-width="3.5" stroke-linejoin="round"/></g>',
    "tambor": '<ellipse cx="32" cy="22" rx="24" ry="8" fill="#f3e5c0" stroke="#a5621c" stroke-width="2"/><path d="M8 22v24q0 8 24 8t24-8V22q0 8-24 8T8 22z" fill="#e53935"/>'
              '<path d="M8 26l12 24M20 30l12 24M32 30l12 24M44 30l12 18" stroke="#ffd54a" stroke-width="2"/><path d="M40 4l-8 14M54 6L38 18" stroke="#8a5a35" stroke-width="3" stroke-linecap="round"/>',
    "guitarra": '<path d="M44 6l6 6-14 14" stroke="#6d4c2e" stroke-width="5" stroke-linecap="round"/><path d="M48 4l6 6" stroke="' + O + '" stroke-width="4" stroke-linecap="round"/>'
                '<path d="M30 22q-8-4-14 2-6 6-2 12-10 4-10 12 0 12 14 12 8 0 12-10 6 4 12-2 6-6 2-14t-14-12z" fill="#e0a458"/>'
                '<circle cx="28" cy="38" r="5" fill="#6d4c2e"/><path d="M20 46l20-20" stroke="#fff" stroke-width="1.5"/>',
    "trompeta": '<path d="M6 30h30l16-12v28L36 34H6z" fill="#f2b400"/><path d="M52 16q8 0 8 16t-8 16z" fill="#ffd54a"/>'
                '<path d="M16 30v-6M22 30v-6M28 30v-6" stroke="#c99500" stroke-width="3" stroke-linecap="round"/><rect x="2" y="28" width="6" height="8" rx="2" fill="#c99500"/>',
    "celular": '<rect x="16" y="4" width="32" height="56" rx="6" fill="' + O + '"/><rect x="19" y="10" width="26" height="40" rx="2" fill="#4aa3f0"/>'
               '<circle cx="32" cy="55" r="2.5" fill="#9fb3c4"/><rect x="24" y="16" width="16" height="4" rx="2" fill="#fff" opacity=".6"/>',
    "libro": '<path d="M32 14Q20 6 6 10v40q14-4 26 4z" fill="#2e86de"/><path d="M32 14q12-8 26-4v40q-14-4-26 4z" fill="#4aa3f0"/>'
             '<path d="M32 14v40" stroke="#1d5fa8" stroke-width="2"/><path d="M12 20q8-2 14 1M12 28q8-2 14 1M38 21q6-3 14-1M38 29q6-3 14-1" stroke="#fff" stroke-width="2" fill="none" opacity=".7"/>',
    "camara": '<rect x="4" y="18" width="56" height="36" rx="6" fill="#455a64"/><path d="M20 18l4-8h16l4 8z" fill="#37474f"/>'
              '<circle cx="32" cy="36" r="12" fill="#cfd8e2"/><circle cx="32" cy="36" r="7" fill="' + O + '"/><circle cx="29" cy="33" r="2" fill="#fff"/><rect x="48" y="22" width="7" height="4" rx="1" fill="#ffd54a"/>',
    "telefono": '<path d="M14 6l10 2 4 12-6 4q4 12 16 18l4-6 12 4 2 10q-2 8-10 8Q8 54 6 16q0-8 8-10z" fill="#e53935"/>',
    "gorra": '<path d="M8 36q0-24 24-24t24 24z" fill="#2e86de"/><path d="M30 36h32q0 6-8 6H30z" fill="#1d5fa8"/><circle cx="32" cy="12" r="3" fill="#1d5fa8"/>'
             '<path d="M20 20q4-4 10-4" stroke="#fff" stroke-width="2.5" fill="none" opacity=".5" stroke-linecap="round"/>',
    "bota": '<path d="M16 4h20v34l18 6q6 2 6 8v6H10V4z" fill="#a0673a"/><rect x="10" y="54" width="50" height="6" rx="2" fill="#6d4c2e"/><rect x="14" y="4" width="24" height="6" rx="2" fill="#6d4c2e"/>',
    "vestido": '<path d="M24 4h16l-2 10 6 6-4 6 14 34H10l14-34-4-6 6-6z" fill="#e0528f"/><path d="M20 26h24" stroke="#fff" stroke-width="3"/>'
               '<g fill="#fff" opacity=".6"><circle cx="24" cy="42" r="2"/><circle cx="34" cy="50" r="2"/><circle cx="42" cy="40" r="2"/></g>',
    "rueda": '<circle cx="32" cy="32" r="28" fill="' + O + '"/><circle cx="32" cy="32" r="16" fill="#cfd8e2"/><circle cx="32" cy="32" r="5" fill="#607d8b"/>'
             '<path d="M32 16v32M16 32h32M21 21l22 22M43 21L21 43" stroke="#607d8b" stroke-width="3"/>',
    "tarro": '<rect x="18" y="4" width="28" height="8" rx="2" fill="#e53935"/><path d="M16 14h32v40q0 6-6 6H22q-6 0-6-6z" fill="#e3f4fd" stroke="#9fb3c4" stroke-width="2.5"/>'
             '<path d="M18 30h28v24q0 4-4 4H22q-4 0-4-4z" fill="#ff9e3d"/><path d="M22 18v30" stroke="#fff" stroke-width="3" opacity=".7"/>',
    "moneda": '<circle cx="32" cy="32" r="26" fill="#f2b400"/><circle cx="32" cy="32" r="20" fill="#ffd54a" stroke="#c99500" stroke-width="2"/>'
              '<text x="32" y="41" font-size="24" font-weight="900" text-anchor="middle" fill="#c99500" font-family="Arial,sans-serif">$</text>',
    "esponja": '<rect x="8" y="16" width="48" height="32" rx="6" fill="#ffd54a"/><rect x="8" y="16" width="48" height="10" rx="5" fill="#5cbf5c"/>'
               '<g fill="#e9b400"><circle cx="18" cy="34" r="3"/><circle cx="30" cy="40" r="2.5"/><circle cx="42" cy="33" r="3"/><circle cx="48" cy="42" r="2"/></g>',
    "robot": '<path d="M32 4v8" stroke="#607d8b" stroke-width="3"/><circle cx="32" cy="4" r="3" fill="#e53935"/><rect x="12" y="12" width="40" height="30" rx="8" fill="#90a4ae"/>'
             '<circle cx="23" cy="25" r="5" fill="#fff"/><circle cx="41" cy="25" r="5" fill="#fff"/><circle cx="23" cy="25" r="2.5" fill="#2e86de"/><circle cx="41" cy="25" r="2.5" fill="#2e86de"/>'
             '<rect x="22" y="33" width="20" height="4" rx="2" fill="' + O + '"/><rect x="18" y="44" width="28" height="16" rx="4" fill="#78909c"/><circle cx="32" cy="52" r="3" fill="#ffd54a"/>'
             '<rect x="6" y="22" width="6" height="10" rx="2" fill="#78909c"/><rect x="52" y="22" width="6" height="10" rx="2" fill="#78909c"/>',
    "dado": '<rect x="8" y="8" width="48" height="48" rx="10" fill="#fff" stroke="' + O + '" stroke-width="3"/>'
            '<g fill="#e53935"><circle cx="20" cy="20" r="5"/><circle cx="44" cy="20" r="5"/><circle cx="32" cy="32" r="5"/><circle cx="20" cy="44" r="5"/><circle cx="44" cy="44" r="5"/></g>',
    "sofa": '<rect x="10" y="14" width="44" height="22" rx="6" fill="#8e6bd6"/><rect x="4" y="26" width="12" height="24" rx="5" fill="#7a59c4"/><rect x="48" y="26" width="12" height="24" rx="5" fill="#7a59c4"/>'
            '<rect x="14" y="34" width="36" height="12" rx="4" fill="#a68be0"/><path d="M10 50v6M54 50v6" stroke="#5a4a7a" stroke-width="4" stroke-linecap="round"/>',
    "dedo": '<g transform="rotate(-20 32 32)"><rect x="22" y="4" width="20" height="54" rx="10" fill="#ffd9b8" stroke="#c98a5e" stroke-width="3"/>'
            '<rect x="26" y="8" width="12" height="13" rx="6" fill="#fff3ea" stroke="#e8b48c" stroke-width="2"/>'
            '<path d="M26 32q6 2 12 0M26 44q6 2 12 0" stroke="#e8a77a" stroke-width="2" fill="none" stroke-linecap="round"/></g>',
    "diente": '<path d="M14 14q0-10 10-10 4 0 8 3 4-3 8-3 10 0 10 10 0 10-4 18-2 6-3 18-1 8-5 8-4 0-4-12 0-6-2-6t-2 6q0 12-4 12-4 0-5-8-1-12-3-18-4-8-4-18z" fill="#fff" stroke="#9fb3c4" stroke-width="2.5"/>'
              '<path d="M20 12q4-4 8 0" stroke="#e3f4fd" stroke-width="3" fill="none" stroke-linecap="round"/>',
    "corazon": '<path d="M32 56Q4 36 6 20 8 6 20 6q8 0 12 8 4-8 12-8 12 0 14 14 2 16-26 36z" fill="#e53935"/><ellipse cx="18" cy="18" rx="4" ry="6" fill="#fff" opacity=".4" transform="rotate(-30 18 18)"/>',
    "curita": '<g transform="rotate(-35 32 32)"><rect x="4" y="22" width="56" height="20" rx="10" fill="#f3c69b"/><rect x="22" y="22" width="20" height="20" fill="#e8b48c"/>'
              '<g fill="#c98a5e"><circle cx="28" cy="28" r="1.4"/><circle cx="36" cy="28" r="1.4"/><circle cx="28" cy="36" r="1.4"/><circle cx="36" cy="36" r="1.4"/></g></g>',
    "nina": '<path d="M12 30q0-24 20-24t20 24v24H12z" fill="#e53935"/><circle cx="32" cy="32" r="14" fill="#ffd9b8"/>'
            + _ojos(27, 37, 31, 2) + '<path d="M27 37q5 4 10 0" stroke="#b5523b" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M18 26q14-12 28 0" fill="#e53935"/>'
            '<path d="M20 60l12-14 12 14z" fill="#e53935"/>',
    "bebe": '<circle cx="32" cy="32" r="24" fill="#ffd9b8"/><path d="M28 8q4 6 0 8" stroke="#a0673a" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
            + _ojos(24, 40, 30) + '<circle cx="16" cy="38" r="4" fill="#ffb3a1"/><circle cx="48" cy="38" r="4" fill="#ffb3a1"/>'
            '<circle cx="32" cy="44" r="6" fill="#4aa3f0"/><rect x="30" y="47" width="4" height="6" rx="2" fill="#4aa3f0"/>',
    "monedero": '<path d="M8 26q0-8 8-8h32q8 0 8 8v24q0 8-8 8H16q-8 0-8-8z" fill="#e0528f"/><path d="M22 18q0-12 10-12t10 12" fill="none" stroke="#f2b400" stroke-width="4"/>'
                '<circle cx="28" cy="18" r="3" fill="#f2b400"/><circle cx="36" cy="18" r="3" fill="#f2b400"/><path d="M8 32h48" stroke="#c2185b" stroke-width="2"/>',
    "canasta": '<path d="M14 26q0-20 18-20t18 20" fill="none" stroke="#a5621c" stroke-width="4"/><path d="M6 26h52l-6 30H12z" fill="#d9a066"/>'
               '<path d="M10 34h44M12 42h40M14 50h36M22 26l2 30M32 26v30M42 26l-2 30" stroke="#a5621c" stroke-width="2"/>',
    "tarjeta": '<rect x="4" y="14" width="56" height="36" rx="6" fill="#2e86de"/><rect x="4" y="22" width="56" height="7" fill="' + O + '"/>'
               '<rect x="10" y="36" width="12" height="8" rx="2" fill="#ffd54a"/><path d="M30 40h22" stroke="#fff" stroke-width="3" stroke-linecap="round"/>',
    "abrigo": '<path d="M22 6l10 8 10-8 14 8v44H40V30h-2v28H26V30h-2v28H8V14z" fill="#8a5a35"/><path d="M32 14v44" stroke="#6d4c2e" stroke-width="2"/>'
              '<g fill="#f2b400"><circle cx="36" cy="24" r="2"/><circle cx="36" cy="34" r="2"/><circle cx="36" cy="44" r="2"/></g><path d="M22 6l10 14 10-14" fill="none" stroke="#6d4c2e" stroke-width="2"/>',
    "banador": '<path d="M12 18h40l-4 18q-6 16-16 16T16 36z" fill="#2e86de"/><path d="M12 18q20 8 40 0" fill="none" stroke="#1d5fa8" stroke-width="3"/>'
               '<g fill="#fff"><circle cx="22" cy="28" r="2.5"/><circle cx="34" cy="34" r="2.5"/><circle cx="42" cy="26" r="2.5"/></g>',
    "corbata": '<path d="M24 4h16l-4 8h-8z" fill="#c62828"/><path d="M28 12h8l8 36-12 12-12-12z" fill="#e53935"/><path d="M26 24l14 8M24 36l18 8" stroke="#ffcdd2" stroke-width="2.5"/>',
    "nevera": '<rect x="14" y="4" width="36" height="56" rx="6" fill="#e3f0fa" stroke="#9fb3c4" stroke-width="2.5"/><path d="M14 24h36" stroke="#9fb3c4" stroke-width="2.5"/>'
              '<path d="M20 12v6M20 30v12" stroke="#607d8b" stroke-width="3" stroke-linecap="round"/><path d="M34 40l4-4 4 4-4 4zM40 46l3-3 3 3-3 3" fill="#9ed6f7"/>',
    "balde": '<path d="M14 18q0-14 18-14t18 14" fill="none" stroke="#607d8b" stroke-width="3"/><path d="M10 18h44l-6 40H16z" fill="#4aa3f0"/>'
             '<ellipse cx="32" cy="18" rx="22" ry="4" fill="#2e86de"/><path d="M16 30h32" stroke="#e3f4fd" stroke-width="2.5"/>',
    "llave": '<circle cx="20" cy="22" r="14" fill="#f2b400"/><circle cx="20" cy="22" r="6" fill="#fff"/><path d="M30 32l22 22M44 46l6-6M50 52l6-6" stroke="#f2b400" stroke-width="7" stroke-linecap="round"/>',
    "banera": '<path d="M4 30h56v8q0 14-14 14H18Q4 52 4 38z" fill="#fff" stroke="#9fb3c4" stroke-width="2.5"/><path d="M14 52l-2 6M50 52l2 6" stroke="#9fb3c4" stroke-width="3" stroke-linecap="round"/>'
             '<path d="M10 30V12q0-6 6-6t6 6" fill="none" stroke="#9fb3c4" stroke-width="3"/><g fill="#9ed6f7"><circle cx="26" cy="26" r="5"/><circle cx="36" cy="22" r="6"/><circle cx="46" cy="26" r="5"/></g>',
    "cama": '<rect x="4" y="30" width="56" height="16" rx="3" fill="#2e86de"/><rect x="4" y="16" width="8" height="40" rx="2" fill="#8a5a35"/><rect x="52" y="24" width="8" height="32" rx="2" fill="#8a5a35"/>'
            '<rect x="14" y="22" width="16" height="10" rx="4" fill="#fff"/><path d="M30 30h22v-4H30z" fill="#4aa3f0"/>',
    "jabon": '<rect x="18" y="20" width="28" height="38" rx="8" fill="#81d4fa"/><rect x="26" y="8" width="12" height="12" fill="#29b6f6"/><path d="M38 10h12" stroke="#29b6f6" stroke-width="4" stroke-linecap="round"/>'
             '<g fill="#e3f4fd"><circle cx="10" cy="12" r="5" stroke="#9ed6f7" stroke-width="1.5"/><circle cx="54" cy="30" r="4" stroke="#9ed6f7" stroke-width="1.5"/></g><rect x="24" y="30" width="16" height="14" rx="3" fill="#fff" opacity=".7"/>',
    "gafas": '<circle cx="18" cy="34" r="12" fill="' + O + '"/><circle cx="46" cy="34" r="12" fill="' + O + '"/><path d="M30 32q2-3 4 0" stroke="' + O + '" stroke-width="3" fill="none"/>'
             '<path d="M6 30L2 22M58 30l4-8" stroke="' + O + '" stroke-width="3" stroke-linecap="round"/><path d="M12 28l6 0M40 28l6 0" stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity=".6"/>',
    "sombrero": '<ellipse cx="32" cy="48" rx="28" ry="8" fill="' + O + '"/><rect x="16" y="10" width="32" height="38" rx="4" fill="' + O + '"/><rect x="16" y="36" width="32" height="6" fill="#e53935"/>',
    "cejas": '<path d="M6 30q10-12 22-6M58 30q-10-12-22-6" stroke="#6b3f1f" stroke-width="7" fill="none" stroke-linecap="round"/>' + _ojos(18, 46, 42, 4),
    "nariz": '<path d="M32 8q-4 20-14 30-4 6 2 10 6 2 10-2 2 2 4 2t4-2q4 4 10 2 6-4 2-10-10-10-14-30" fill="#ffd9b8" stroke="#c98a5e" stroke-width="3" stroke-linejoin="round"/>'
             '<ellipse cx="25" cy="44" rx="3" ry="2" fill="#c98a5e"/><ellipse cx="39" cy="44" rx="3" ry="2" fill="#c98a5e"/>',
    "estallido": '<path d="M32 2l6 16 16-8-6 16 16 6-16 6 8 16-16-6-6 16-6-16-16 6 8-16-16-6 16-6-6-16 16 8z" fill="#ffd54a" stroke="#f57c00" stroke-width="2.5" stroke-linejoin="round"/>'
                 '<path d="M32 20l3 8 8-3-4 8 8 3-8 3 3 8-8-4-3 8-3-8-8 4 3-8-8-3 8-3-4-8 8 3z" fill="#f57c00"/>',
    "vaso_pitillo": '<path d="M38 2l-6 26" stroke="#ef4b5f" stroke-width="4" stroke-linecap="round"/><path d="M16 20h32l-4 38H20z" fill="#e3f4fd" stroke="#9fb3c4" stroke-width="2.5"/>'
                    '<path d="M18 34h28l-3 24H21z" fill="#ff9e3d"/>',
}

PALABRAS = {**ANIMALES, **COMIDA, **NATURALEZA, **VEHICULOS, **OBJETOS}
