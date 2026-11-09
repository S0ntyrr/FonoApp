/* FonoNivel — niveles en TODOS los juegos, metas de las tareas del médico y
 * color favorito del niño.
 *
 * 1) Tarea del médico (?tarea_id=…): la meta es X intentos o X minutos.
 *    - Indicador abajo a la izquierda: estrellas (intentos) o reloj (tiempo).
 *    - Cada partida terminada suma un intento (lo cuenta el servidor).
 *    - El tiempo se envía cada 15 s mientras la pantalla está visible
 *      (el servidor suma máx. 30 s por pulso).
 *    - Al cumplir la meta: trofeo y botón grande para volver al camino, donde
 *      ya están desbloqueados los juegos automáticos.
 * 2) Juego automático con ?nivel=2..3 en un juego SIN dificultad propia:
 *    el nivel son rondas (nivel 2 = jugar 2 veces). Mientras falten rondas el
 *    resultado se guarda como intento (completado=false, nota «Ronda k de N»).
 * Ambos modos interceptan el POST a /juegos/resultado, venga de
 * guardarResultadoJuego() o de un fetch directo, así que sirven para cualquier juego.
 */
(function () {
  'use strict';
  const params = new URLSearchParams(location.search);
  const ruta = (location.pathname || '').replace(/\/+$/, '');
  const esJuego = /^\/juegos\/[^/]+\/[^/]+$/.test(ruta);
  const nivel = Math.max(0, Math.min(3, parseInt(params.get('nivel') || '0', 10) || 0));
  const tareaId = esJuego && /^[0-9a-f]{24}$/i.test(params.get('tarea_id') || '') ? params.get('tarea_id') : '';
  const nativos = new Set((window.FONO_JUEGOS_CON_NIVELES || []).map(u => String(u).replace(/\/+$/, '')));
  const conRondas = esJuego && !tareaId && nivel > 1 && !nativos.has(ruta);
  const totalRondas = conRondas ? nivel : 1;
  const hoy = new Date().toISOString().slice(0, 10);
  const clave = `fono_rondas|${ruta}|${nivel}|${hoy}`;
  const fetchBase = typeof window.fetch === 'function' ? window.fetch.bind(window) : null;
  let tarea = null; // {tipo, meta, intentos, segundos, fraccion, completada}

  function leer(k, almacen = sessionStorage) { try { return almacen.getItem(k); } catch (e) { return null; } }
  function escribir(k, v, almacen = sessionStorage) { try { v === null ? almacen.removeItem(k) : almacen.setItem(k, v); } catch (e) {} }
  function hechas() { return Math.max(0, parseInt(leer(clave) || '0', 10) || 0); }

  // ── Color favorito ──────────────────────────────────────────────────────────
  const colorFav = leer('fono_color_favorito', localStorage);
  if (colorFav && /^#[0-9a-f]{6}$/i.test(colorFav)) document.documentElement.style.setProperty('--fono-fav', colorFav);

  // ── Interceptar el guardado de resultados ───────────────────────────────────
  function esPostResultado(recurso, opciones) {
    const url = typeof recurso === 'string' ? recurso : (recurso && recurso.url) || '';
    const cuerpo = opciones && opciones.body;
    return /\/juegos\/resultado(\?|$)/.test(url) && (opciones?.method || 'GET').toUpperCase() === 'POST'
      && typeof FormData !== 'undefined' && cuerpo instanceof FormData
      && String(cuerpo.get('completado')) === 'true';
  }

  if (fetchBase && (conRondas || tareaId)) {
    window.fetch = async function (recurso, opciones) {
      if (!esPostResultado(recurso, opciones)) return fetchBase(recurso, opciones);
      const cuerpo = opciones.body;

      if (tareaId) {
        // El servidor decide si la partida completa la meta.
        if (!cuerpo.get('tarea_id')) cuerpo.set('tarea_id', tareaId);
        const respuesta = await fetchBase(recurso, opciones);
        if (respuesta.ok) {
          try {
            const datos = await respuesta.clone().json();
            if (datos && datos.tarea) { tarea = datos.tarea; pintarIndicador(); }
          } catch (e) {}
          if (tarea && tarea.completada) setTimeout(mostrarMetaCumplida, 900);
          else if (tarea && tarea.tipo === 'intentos') setTimeout(mostrarIntento, 900);
        }
        return respuesta;
      }

      const ronda = Math.min(totalRondas, hechas() + 1);
      const ultima = ronda >= totalRondas;
      if (!ultima) cuerpo.set('completado', 'false');
      cuerpo.set('nivel', String(nivel));
      cuerpo.set('notas', `Ronda ${ronda} de ${totalRondas} (nivel ${nivel}). ${String(cuerpo.get('notas') || '')}`.slice(0, 1000));
      const respuesta = await fetchBase(recurso, opciones);
      if (respuesta.ok) {
        escribir(clave, ultima ? null : String(ronda));
        setTimeout(() => mostrarRonda(ronda, ultima), 900);
        pintarIndicador();
      }
      return respuesta;
    };
  }

  // ── Tarea: estado inicial y pulsos de tiempo ────────────────────────────────
  async function cargarTarea() {
    if (!tareaId || !fetchBase) return;
    try {
      const r = await fetchBase(`/juegos/tarea/${tareaId}/estado`, { credentials: 'same-origin' });
      if (!r.ok) return; // p. ej. vista previa del médico
      tarea = await r.json();
      pintarIndicador();
      if (!tarea.completada) iniciarPulsos();
    } catch (e) {}
  }

  function iniciarPulsos() {
    let ultimo = performance.now();
    const intervalo = setInterval(async () => {
      const ahora = performance.now();
      const segundos = Math.round((ahora - ultimo) / 1000);
      ultimo = ahora;
      if (document.visibilityState !== 'visible' || !tarea || tarea.completada) return;
      const fd = new FormData();
      fd.append('segundos', String(Math.min(30, segundos)));
      try {
        const r = await fetchBase(`/juegos/tarea/${tareaId}/tiempo`, { method: 'POST', body: fd, credentials: 'same-origin' });
        if (!r.ok) return;
        const antes = tarea.completada;
        tarea = await r.json();
        pintarIndicador();
        if (tarea.completada && !antes) { clearInterval(intervalo); mostrarMetaCumplida(); }
      } catch (e) {}
    }, 15000);
    // Al volver a la pestaña no se cuenta el tiempo que estuvo oculta.
    document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') ultimo = performance.now(); });
  }

  // ── Interfaz visual (sin texto para el niño) ────────────────────────────────
  const ESTRELLA = on => `<svg viewBox="0 0 64 64" class="fn-estrella${on ? ' on' : ''}" aria-hidden="true"><path d="M32 4 L40 23 L60 24 L44 37 L50 58 L32 46 L14 58 L20 37 L4 24 L24 23Z" fill="${on ? '#ffc93c' : '#e3e8ef'}" stroke="${on ? '#e9a400' : '#c9d1dc'}" stroke-width="3" stroke-linejoin="round"/></svg>`;
  const RELOJ = f => {
    const p = Math.round(Math.max(0, Math.min(1, f)) * 100);
    return `<svg viewBox="0 0 40 40" class="fn-reloj" aria-hidden="true"><circle cx="20" cy="20" r="16" fill="#fff" stroke="#e3e9f0" stroke-width="6"/><circle cx="20" cy="20" r="16" fill="none" stroke="var(--fono-fav,#2e9fd6)" stroke-width="6" stroke-linecap="round" pathLength="100" stroke-dasharray="${p} 100" transform="rotate(-90 20 20)"/><path d="M20 11 V20 L26 23" stroke="#1f3347" stroke-width="2.5" fill="none" stroke-linecap="round"/></svg>`;
  };
  // Ilustraciones (las mismas de app/iconos.py)
  const ICO_DOCTOR = "<svg class=\"fn-doc\" viewBox=\"0 0 64 64\" aria-hidden=\"true\"><circle cx=\"32\" cy=\"32\" r=\"28\" fill=\"#fff\" stroke=\"#2e86de\" stroke-width=\"3\"/><path d=\"M20 14v12a9 9 0 0018 0V14\" fill=\"none\" stroke=\"#2e86de\" stroke-width=\"4\" stroke-linecap=\"round\"/><path d=\"M29 35v5a10 10 0 0020 0v-4\" fill=\"none\" stroke=\"#2e86de\" stroke-width=\"4\"/><circle cx=\"49\" cy=\"31\" r=\"5\" fill=\"#e53935\"/><circle cx=\"20\" cy=\"14\" r=\"3\" fill=\"#1f3347\"/><circle cx=\"38\" cy=\"14\" r=\"3\" fill=\"#1f3347\"/></svg>";
  const ICO_TROFEO = "<svg class=\"fn-trofeo\" viewBox=\"0 0 64 64\" aria-hidden=\"true\"><path d=\"M18 12H8q0 15 13 15M46 12h10q0 15-13 15\" fill=\"none\" stroke=\"#e9a400\" stroke-width=\"4.5\"/><path d=\"M17 6h30v16a15 15 0 01-30 0z\" fill=\"#f2b400\"/><path d=\"M22 10v10a10 10 0 005 9\" stroke=\"#fff\" stroke-width=\"3\" fill=\"none\" opacity=\".5\" stroke-linecap=\"round\"/><rect x=\"28\" y=\"36\" width=\"8\" height=\"10\" fill=\"#c99500\"/><rect x=\"17\" y=\"46\" width=\"30\" height=\"12\" rx=\"3\" fill=\"#8a5a35\"/><rect x=\"24\" y=\"50\" width=\"16\" height=\"4\" rx=\"2\" fill=\"#f2b400\"/></svg>";
  const ICO_ABIERTO = "<svg class=\"fn-candado\" viewBox=\"0 0 64 64\" aria-hidden=\"true\"><path d=\"M44 30v-9a12 12 0 00-24 0v-4\" fill=\"none\" stroke=\"#8a97a6\" stroke-width=\"6\"/><rect x=\"12\" y=\"29\" width=\"40\" height=\"30\" rx=\"7\" fill=\"#2bb673\"/><rect x=\"12\" y=\"29\" width=\"40\" height=\"8\" rx=\"7\" fill=\"#fff\" opacity=\".25\"/><circle cx=\"32\" cy=\"42\" r=\"4.5\" fill=\"#1d6b43\"/><rect x=\"30\" y=\"43\" width=\"4\" height=\"9\" rx=\"2\" fill=\"#1d6b43\"/></svg>";
  const OTRA_VEZ = `<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="30" fill="var(--fono-fav,#2bb673)"/><path d="M25 18 L48 32 L25 46Z" fill="#fff"/></svg>`;
  const CAMINO = `<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="30" fill="var(--fono-fav,#2bb673)"/><path d="M18 34 L32 20 L46 34 M23 30 V46 H41 V30" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;

  function estilos() {
    if (document.getElementById('fono-nivel-css')) return;
    const css = document.createElement('style');
    css.id = 'fono-nivel-css';
    css.textContent = `
      .fn-indicador{position:fixed;left:10px;bottom:14px;z-index:9000;display:flex;align-items:center;gap:6px;padding:6px 10px;border-radius:999px;background:#ffffffe8;box-shadow:0 3px 12px #0002;border:3px solid var(--fono-fav,#d32f2f);pointer-events:none;max-width:calc(100vw - 150px);flex-wrap:wrap}
      .fn-punto{width:12px;height:12px;border-radius:50%;background:#dfe6ee}
      .fn-punto.on{background:var(--fono-fav,#d32f2f)}
      .fn-sep{width:2px;height:16px;background:#dfe6ee;margin:0 2px}
      .fn-ronda{width:18px;height:18px}
      .fn-ronda svg{width:100%;height:100%}
      .fn-reloj{width:34px;height:34px}
      .fn-num{font-weight:900;color:#1f3347;font-size:.95rem}
      .fn-doc{width:30px;height:30px}
      .fn-overlay{position:fixed;inset:0;z-index:10050;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;background:#ffffffd9;backdrop-filter:blur(3px);animation:fn-entra .25s ease-out;padding:16px}
      .fn-estrellas{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;max-width:560px}
      .fn-estrella{width:clamp(48px,14vw,96px);height:auto}
      .fn-estrella.on.nueva{animation:fn-pop .55s cubic-bezier(.3,1.6,.5,1) both}
      .fn-trofeo{width:clamp(80px,22vw,130px);height:auto;animation:fn-pop .6s cubic-bezier(.3,1.6,.5,1) both}
      .fn-candado{width:clamp(52px,13vw,76px);height:auto;animation:fn-abre 1s .5s ease both}
      .fn-boton{border:none;background:none;padding:0;cursor:pointer;animation:fn-late 1.2s ease-in-out infinite}
      .fn-boton svg{width:clamp(96px,22vw,128px);height:auto;filter:drop-shadow(0 6px 10px #0003)}
      .fn-salir{position:absolute;top:14px;left:14px;width:48px;height:48px;border-radius:50%;border:3px solid #dfe6ee;background:#fff;font-size:22px;cursor:pointer;color:#5a6b7b}
      @keyframes fn-pop{0%{transform:scale(0) rotate(-30deg)}70%{transform:scale(1.25)}100%{transform:scale(1)}}
      @keyframes fn-late{50%{transform:scale(1.08)}}
      @keyframes fn-entra{from{opacity:0}}
      @keyframes fn-abre{0%{transform:scale(1)}40%{transform:scale(1.3) rotate(-12deg)}100%{transform:scale(1);opacity:.9}}
      @media (prefers-reduced-motion:reduce){.fn-boton,.fn-estrella.on.nueva,.fn-trofeo,.fn-candado{animation:none}}`;
    document.head.appendChild(css);
  }

  function contenedorIndicador() {
    estilos();
    let el = document.getElementById('fn-indicador');
    if (!el) {
      el = document.createElement('div');
      el.id = 'fn-indicador';
      el.className = 'fn-indicador';
      el.setAttribute('role', 'img');
      document.body.appendChild(el);
    }
    return el;
  }

  function pintarIndicador() {
    if (!esJuego || !document.body) return;
    if (tareaId) {
      if (!tarea) return;
      const el = contenedorIndicador();
      let html = ICO_DOCTOR;
      if (tarea.tipo === 'tiempo') {
        const min = Math.floor(tarea.segundos / 60);
        html += RELOJ(tarea.fraccion) + `<span class="fn-num">${Math.min(min, tarea.meta)}/${tarea.meta}</span>`;
        el.setAttribute('aria-label', `Tiempo jugado: ${min} de ${tarea.meta} minutos`);
      } else {
        if (tarea.meta <= 10) for (let i = 0; i < tarea.meta; i++) html += `<span class="fn-ronda">${ESTRELLA(i < tarea.intentos)}</span>`;
        else html += `<span class="fn-ronda">${ESTRELLA(true)}</span><span class="fn-num">${tarea.intentos}/${tarea.meta}</span>`;
        el.setAttribute('aria-label', `Intentos: ${tarea.intentos} de ${tarea.meta}`);
      }
      el.innerHTML = html;
      return;
    }
    // Los juegos con dificultad propia ya muestran su nivel en pantalla.
    if (!nivel || nativos.has(ruta)) return;
    const el = contenedorIndicador();
    let html = '';
    for (let i = 1; i <= 3; i++) html += `<span class="fn-punto${i <= nivel ? ' on' : ''}"></span>`;
    if (conRondas) {
      html += '<span class="fn-sep"></span>';
      const h = hechas();
      for (let i = 0; i < totalRondas; i++) html += `<span class="fn-ronda">${ESTRELLA(i < h)}</span>`;
    }
    el.innerHTML = html;
    el.setAttribute('aria-label', conRondas ? `Nivel ${nivel}: ronda ${Math.min(totalRondas, hechas() + 1)} de ${totalRondas}` : `Nivel ${nivel}`);
  }

  function overlay(html, etiqueta) {
    estilos();
    document.getElementById('fn-overlay')?.remove();
    const ov = document.createElement('div');
    ov.id = 'fn-overlay';
    ov.className = 'fn-overlay';
    ov.setAttribute('role', 'dialog');
    ov.setAttribute('aria-label', etiqueta);
    ov.innerHTML = html;
    document.body.appendChild(ov);
    try { window.reproducirSonidoExito?.(); } catch (e) {}
    return ov;
  }

  function filaEstrellas(total, llenas) {
    let h = '';
    for (let i = 1; i <= total; i++) h += ESTRELLA(i <= llenas).replace('fn-estrella on', i === llenas ? 'fn-estrella on nueva' : 'fn-estrella on');
    return `<div class="fn-estrellas">${h}</div>`;
  }

  function mostrarRonda(ronda, ultima) {
    if (ultima) {
      const ov = overlay(`${ICO_TROFEO}${filaEstrellas(totalRondas, ronda)}`, '¡Todas las rondas completas!');
      ov.addEventListener('click', () => ov.remove());
      setTimeout(() => ov.remove(), 2600);
      return;
    }
    const ov = overlay(`<button type="button" class="fn-salir" aria-label="Salir">✕</button>${filaEstrellas(totalRondas, ronda)}<button type="button" class="fn-boton" aria-label="Jugar la siguiente ronda">${OTRA_VEZ}</button>`, `Ronda ${ronda} de ${totalRondas}`);
    ov.querySelector('.fn-boton').addEventListener('click', () => location.reload());
    ov.querySelector('.fn-salir').addEventListener('click', () => ov.remove());
  }

  function mostrarIntento() {
    const total = Math.min(10, tarea.meta), llenas = Math.min(total, tarea.intentos);
    const ov = overlay(`<button type="button" class="fn-salir" aria-label="Seguir aquí">✕</button>${filaEstrellas(total, llenas)}<button type="button" class="fn-boton" aria-label="Jugar otra vez">${OTRA_VEZ}</button>`, `Intento ${tarea.intentos} de ${tarea.meta}`);
    ov.querySelector('.fn-boton').addEventListener('click', () => location.reload());
    ov.querySelector('.fn-salir').addEventListener('click', () => ov.remove());
  }

  function mostrarMetaCumplida() {
    if (document.querySelector('#fn-overlay.fn-meta')) return;
    const ov = overlay(`${ICO_TROFEO}${ICO_ABIERTO}<button type="button" class="fn-boton" aria-label="Volver a mis juegos">${CAMINO}</button>`, '¡Actividad del terapeuta completada! Ya puedes jugar tus otros juegos.');
    ov.classList.add('fn-meta');
    ov.querySelector('.fn-boton').addEventListener('click', () => {
      escribir('flujo_juegos_modo', 'hub');
      location.href = leer('juegos_origen') || '/paciente/perfil';
    });
  }

  function arrancar() { pintarIndicador(); cargarTarea(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', arrancar);
  else arrancar();

  window.FonoNivel = { nivel, rondas: totalRondas, conRondas, tareaId, tarea: () => tarea, ronda: () => Math.min(totalRondas, hechas() + 1) };
})();
