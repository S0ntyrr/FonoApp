/* Piezas visuales compartidas por los juegos de soplo (burbujas y algodón).
 * Todo son ilustraciones SVG: el niño no necesita leer.
 */
window.FonoSoploUI = (function () {
  'use strict';

  const CARA = (extra = '', boca = '') => `
    <svg viewBox="0 0 120 120" class="sui-cara" aria-hidden="true">
      <circle cx="60" cy="62" r="44" fill="#ffd9b8" stroke="#e8a77a" stroke-width="3"/>
      <path d="M22 50 Q30 12 60 14 Q92 12 98 50 Q86 30 60 30 Q36 30 22 50Z" fill="#6b3f1f"/>
      <circle cx="44" cy="56" r="5" fill="#2b2b2b"/><circle cx="76" cy="56" r="5" fill="#2b2b2b"/>
      <circle cx="45.5" cy="54.5" r="1.6" fill="#fff"/><circle cx="77.5" cy="54.5" r="1.6" fill="#fff"/>
      <path d="M57 64 Q60 72 63 64" fill="none" stroke="#d08a5c" stroke-width="3" stroke-linecap="round"/>
      ${boca}${extra}
    </svg>`;

  // 1) Tomar aire por la nariz (flechas entrando) 2) soplar (mejillas infladas + aire)
  const INSPIRA = CARA(`
      <g class="sui-flechas-in" stroke="#2e9fd6" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 98 Q30 76 52 70"/><path d="M44 64 L53 70 L45 77"/>
        <path d="M102 98 Q90 76 68 70"/><path d="M76 64 L67 70 L75 77"/>
      </g>`, `<path d="M51 88 Q60 92 69 88" fill="none" stroke="#b5523b" stroke-width="3.5" stroke-linecap="round"/>`);
  const SOPLA = CARA(`
      <circle cx="34" cy="74" r="9" fill="#ffb3a1" opacity=".8"/><circle cx="86" cy="74" r="9" fill="#ffb3a1" opacity=".8"/>
      <g class="sui-aire" stroke="#2e9fd6" stroke-width="4" fill="none" stroke-linecap="round">
        <path d="M70 86 Q86 82 104 88"/><path d="M70 92 Q90 94 112 100"/><path d="M68 80 Q84 72 100 74"/>
      </g>`, `<ellipse cx="62" cy="86" rx="7" ry="6" fill="#b5523b"/>`);
  const SILENCIO = CARA(`
      <rect x="57" y="72" width="8" height="30" rx="4" fill="#ffd9b8" stroke="#e8a77a" stroke-width="2"/>`,
      `<path d="M50 86 L70 86" stroke="#b5523b" stroke-width="3.5" stroke-linecap="round"/>`);
  const HABLA_NO = `
    <svg viewBox="0 0 120 120" class="sui-icono" aria-hidden="true">
      <circle cx="60" cy="60" r="52" fill="#fff" stroke="#e53935" stroke-width="7"/>
      <ellipse cx="50" cy="62" rx="16" ry="12" fill="#b5523b"/>
      <path d="M72 46 Q82 62 72 78 M80 38 Q94 62 80 86" fill="none" stroke="#7a5cc7" stroke-width="5" stroke-linecap="round"/>
      <path d="M24 96 L96 24" stroke="#e53935" stroke-width="8" stroke-linecap="round"/>
    </svg>`;
  const PLAY = `<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="30" fill="#2bb673"/><path d="M25 18 L48 32 L25 46Z" fill="#fff"/></svg>`;
  const STOP = `<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="30" fill="#ef6c57"/><rect x="21" y="21" width="22" height="22" rx="4" fill="#fff"/></svg>`;
  const REPETIR = `<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="30" fill="#2e9fd6"/><path d="M44 26 A13 13 0 1 0 45 36" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round"/><path d="M38 18 L47 26 L37 31Z" fill="#fff"/></svg>`;
  const ESTRELLA = (on) => `<svg viewBox="0 0 64 64" class="sui-estrella ${on ? 'on' : ''}" aria-hidden="true"><path d="M32 4 L40 23 L60 24 L44 37 L50 58 L32 46 L14 58 L20 37 L4 24 L24 23Z" fill="${on ? '#ffc93c' : '#e3e8ef'}" stroke="${on ? '#e9a400' : '#c9d1dc'}" stroke-width="3" stroke-linejoin="round"/></svg>`;
  const MANO = `<svg viewBox="0 0 80 80" class="sui-mano" aria-hidden="true"><path d="M30 70 Q18 58 16 46 Q15 40 21 41 Q25 42 28 50 L28 18 Q28 12 33 12 Q38 12 38 18 L38 38 L38 32 Q38 27 43 27 Q48 27 48 32 L48 40 L48 35 Q48 30 53 30 Q58 30 58 35 L58 42 Q58 38 62 38 Q67 38 67 43 L67 56 Q67 66 60 72Z" fill="#ffd9b8" stroke="#c98a5e" stroke-width="3" stroke-linejoin="round"/></svg>`;

  function estrellas(n, total = 3) { let h = ''; for (let i = 0; i < total; i++) h += ESTRELLA(i < n); return `<div class="sui-estrellas">${h}</div>`; }

  /* Overlay dentro de la escena */
  function overlay(escena, html, clase = '') {
    let el = escena.querySelector('.sui-overlay');
    if (!el) { el = document.createElement('div'); el.className = 'sui-overlay'; escena.appendChild(el); }
    el.className = 'sui-overlay ' + clase;
    el.innerHTML = html;
    el.hidden = false;
    return el;
  }
  function ocultarOverlay(escena) { const el = escena.querySelector('.sui-overlay'); if (el) el.hidden = true; }

  function pantallaInicio(escena, { demo = '', onPlay }) {
    const el = overlay(escena, `
      <div class="sui-pasos">
        <div class="sui-paso"><div class="sui-num">1</div>${INSPIRA}</div>
        <div class="sui-flecha">&#10140;</div>
        <div class="sui-paso"><div class="sui-num">2</div>${SOPLA}</div>
        ${demo ? `<div class="sui-flecha">&#10140;</div><div class="sui-paso"><div class="sui-num">3</div>${demo}</div>` : ''}
      </div>
      <button type="button" class="sui-boton-grande" aria-label="Empezar">${PLAY}</button>`, 'sui-inicio');
    el.querySelector('button').addEventListener('click', onPlay, { once: true });
  }

  function pantallaSilencio(escena, ms) {
    overlay(escena, `<div class="sui-silencio">${SILENCIO}<svg viewBox="0 0 100 100" class="sui-reloj"><circle cx="50" cy="50" r="42" fill="none" stroke="#dbe9f4" stroke-width="10"/><circle cx="50" cy="50" r="42" fill="none" stroke="#2e9fd6" stroke-width="10" stroke-linecap="round" pathLength="100" stroke-dasharray="100" style="animation:sui-reloj ${ms}ms linear forwards"/></svg></div>`, 'sui-calibra');
  }

  function pantallaFinal(escena, { estrellasGanadas, onRepetir, guardando }) {
    const el = overlay(escena, `
      <div class="sui-final">
        ${estrellas(estrellasGanadas)}
        <div class="sui-guardado" aria-live="polite">${guardando ? '<span class="sui-spinner"></span>' : ''}</div>
        <button type="button" class="sui-boton-grande" aria-label="Jugar otra vez">${REPETIR}</button>
      </div>`, 'sui-fin');
    el.querySelector('button').addEventListener('click', onRepetir, { once: true });
    return el;
  }

  /* Medidor de aire (columna con viento) */
  function medidor(contenedor) {
    contenedor.innerHTML = `
      <div class="sui-medidor" aria-hidden="true">
        <div class="sui-medidor-icono">${SOPLA}</div>
        <div class="sui-medidor-barra"><div class="sui-medidor-relleno"></div><div class="sui-medidor-meta"></div></div>
        <div class="sui-voz" hidden>${HABLA_NO}</div>
      </div>`;
    const relleno = contenedor.querySelector('.sui-medidor-relleno');
    const meta = contenedor.querySelector('.sui-medidor-meta');
    const voz = contenedor.querySelector('.sui-voz');
    const icono = contenedor.querySelector('.sui-medidor-icono');
    return {
      pintar(intensidad, minimo, esVoz) {
        relleno.style.width = Math.round(intensidad * 100) + '%';
        relleno.classList.toggle('ok', intensidad >= minimo);
        meta.style.left = Math.round(minimo * 100) + '%';
        voz.hidden = !esVoz;
        icono.classList.toggle('activo', intensidad > 0.02);
      }
    };
  }

  /* Sonidos suaves generados (sin archivos) */
  let actx = null;
  function sonido(tipo) {
    try {
      actx = actx || new (window.AudioContext || window.webkitAudioContext)();
      const vol = Math.max(0, Math.min(1, parseFloat(localStorage.getItem('fonoapp_master_volume') || '0.7')));
      const t = actx.currentTime, o = actx.createOscillator(), g = actx.createGain();
      o.connect(g); g.connect(actx.destination);
      const cfg = { pop: [900, 1500, .12, 'sine'], golpe: [180, 90, .25, 'triangle'], agua: [500, 260, .3, 'sine'], meta: [523, 1046, .5, 'triangle'], burbuja: [400, 800, .2, 'sine'] }[tipo] || [440, 440, .2, 'sine'];
      o.type = cfg[3];
      o.frequency.setValueAtTime(cfg[0], t); o.frequency.exponentialRampToValueAtTime(cfg[1], t + cfg[2]);
      g.gain.setValueAtTime(0.25 * vol + 0.0001, t); g.gain.exponentialRampToValueAtTime(0.0001, t + cfg[2]);
      o.start(t); o.stop(t + cfg[2] + 0.02);
    } catch (e) {}
  }

  return { pantallaInicio, pantallaSilencio, pantallaFinal, ocultarOverlay, medidor, sonido, estrellas, icons: { PLAY, STOP, REPETIR, MANO, SOPLA, INSPIRA, HABLA_NO } };
})();
