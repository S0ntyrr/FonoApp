/* FonoEmoji — reemplaza en pantalla los emojis por las ilustraciones de FonoApp.
 *
 * Los emojis se ven distinto en cada celular, pierden calidad y un niño que no
 * lee no siempre los entiende. Este script recorre la página (y lo que los
 * juegos van agregando después) y cambia cada emoji conocido por su dibujo de
 * app/iconos*.py (servidos en /iconos.js).
 *
 * El emoji original queda guardado en un <desc> dentro del SVG, así que
 * element.textContent sigue devolviendo lo mismo y la lógica de los juegos no cambia.
 */
(function () {
  'use strict';
  const ICONOS = window.FonoIconos || {};
  const MAPA = window.FonoEmojis || {};
  const claves = Object.keys(MAPA).sort((a, b) => b.length - a.length);
  if (!claves.length) return;

  const escapar = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const PATRON = new RegExp('(' + claves.map(escapar).join('|') + ')', 'gu');
  const POSIBLE = /[←-⯿]|[\uD83C-\uD83E][\uDC00-\uDFFF]/;
  const OMITIR = new Set(['SCRIPT', 'STYLE', 'TEXTAREA', 'INPUT', 'OPTION', 'SELECT', 'TITLE', 'NOSCRIPT', 'CODE', 'PRE']);

  function crearSvg(emoji) {
    const nombre = MAPA[emoji];
    const cuerpo = ICONOS[nombre];
    if (!cuerpo) return null;
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 64 64');
    svg.setAttribute('class', 'fono-emoji' + (nombre.startsWith('boca_') ? ' fa-siempre' : ''));
    svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('focusable', 'false');
    svg.setAttribute('data-icono', nombre);
    svg.innerHTML = '<desc>' + emoji + '</desc>' + cuerpo;
    return svg;
  }

  function omitido(nodo) {
    for (let el = nodo.parentNode; el && el.nodeType === 1; el = el.parentNode) {
      if (OMITIR.has(el.nodeName) || el.namespaceURI === 'http://www.w3.org/2000/svg' || el.isContentEditable || el.hasAttribute('data-sin-iconos')) return true;
    }
    return false;
  }

  function reemplazarTexto(nodo) {
    const original = nodo.nodeValue;
    if (!original || !POSIBLE.test(original) || omitido(nodo)) return;
    const texto = original.replace(/️/g, '');
    PATRON.lastIndex = 0;
    if (!PATRON.test(texto)) return;
    PATRON.lastIndex = 0;
    const frag = document.createDocumentFragment();
    let ultimo = 0, m, cambios = 0;
    while ((m = PATRON.exec(texto))) {
      const svg = crearSvg(m[0]);
      if (!svg) continue;
      if (m.index > ultimo) frag.appendChild(document.createTextNode(texto.slice(ultimo, m.index)));
      frag.appendChild(svg);
      ultimo = m.index + m[0].length;
      cambios++;
    }
    if (!cambios) return;
    if (ultimo < texto.length) frag.appendChild(document.createTextNode(texto.slice(ultimo)));
    nodo.parentNode.replaceChild(frag, nodo);
  }

  function recorrer(raiz) {
    if (!raiz) return;
    if (raiz.nodeType === 3) { reemplazarTexto(raiz); return; }
    if (raiz.nodeType !== 1 && raiz.nodeType !== 9 && raiz.nodeType !== 11) return;
    const walker = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT, {
      acceptNode: n => (n.nodeValue && POSIBLE.test(n.nodeValue)) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT
    });
    const pendientes = [];
    while (walker.nextNode()) pendientes.push(walker.currentNode);
    pendientes.forEach(reemplazarTexto);
  }

  // Atributos que lee el lector de pantalla o aparecen como globo: sin emojis.
  function limpiarAtributos(raiz) {
    if (!raiz || !raiz.querySelectorAll) return;
    raiz.querySelectorAll('[title],[aria-label],[placeholder]').forEach(el => {
      ['title', 'aria-label', 'placeholder'].forEach(a => {
        const v = el.getAttribute(a);
        if (v && POSIBLE.test(v)) {
          const limpio = v.replace(/️/g, '').replace(PATRON, '').replace(/\s{2,}/g, ' ').trim();
          if (limpio !== v) el.setAttribute(a, limpio);
        }
      });
    });
  }

  let cola = new Set(), programado = false;
  function procesarCola() {
    programado = false;
    const nodos = Array.from(cola); cola = new Set();
    nodos.forEach(n => { if (n.isConnected) { recorrer(n); if (n.nodeType === 1) limpiarAtributos(n); } });
  }
  const observador = new MutationObserver(mutaciones => {
    for (const m of mutaciones) {
      if (m.type === 'characterData') cola.add(m.target);
      else m.addedNodes.forEach(n => { if (!(n.nodeType === 1 && n.classList && n.classList.contains('fono-emoji'))) cola.add(n); });
    }
    if (!programado && cola.size) { programado = true; requestAnimationFrame(procesarCola); }
  });

  function iniciar() {
    if (document.title && POSIBLE.test(document.title)) document.title = document.title.replace(/️/g, '').replace(PATRON, '').trim();
    recorrer(document.body);
    limpiarAtributos(document.body);
    observador.observe(document.body, { childList: true, subtree: true, characterData: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();

  window.FonoEmoji = { procesar: recorrer };
})();
