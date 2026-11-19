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

  /* ── Preparar el micrófono (sirve con ruido, sin pedir silencio) ───────────── */
  // Celular con el micrófono marcado abajo y el aire llegando de cerca
  const TELEFONO = `
    <svg viewBox="0 0 160 170" class="sui-telefono" aria-hidden="true">
      <rect x="62" y="8" width="66" height="128" rx="12" fill="#2f3b4c"/>
      <rect x="67" y="18" width="56" height="100" rx="5" fill="#bfe3ff"/>
      <circle cx="95" cy="68" r="16" fill="#fff" opacity=".85"/><path d="M89 60 L103 68 L89 76Z" fill="#2bb673"/>
      <g class="sui-mic"><circle cx="95" cy="127" r="11" fill="none" stroke="#ffca28" stroke-width="4"/><circle cx="95" cy="127" r="3.5" fill="#ffca28"/></g>
      <g class="sui-aire" stroke="#2e9fd6" stroke-width="5" fill="none" stroke-linecap="round">
        <path d="M10 118 Q40 112 76 124"/><path d="M14 138 Q44 140 78 131"/><path d="M22 100 Q48 98 74 116"/>
      </g>
      <text x="95" y="162" text-anchor="middle" font-size="15" font-weight="800" fill="#2e6f9e">¡aquí!</text>
    </svg>`;
  const OREJA = `
    <svg viewBox="0 0 120 120" class="sui-oreja" aria-hidden="true">
      <path d="M40 46 Q40 18 66 18 Q92 18 92 46 Q92 62 78 72 Q70 78 70 90 Q70 104 56 104 Q44 104 42 92" fill="#ffd9b8" stroke="#e8a77a" stroke-width="4" stroke-linecap="round"/>
      <path d="M56 48 Q56 34 66 34 Q78 34 78 46 Q78 56 68 60" fill="none" stroke="#e8a77a" stroke-width="4" stroke-linecap="round"/>
      <g class="sui-ondas-oir" stroke="#7a5cc7" stroke-width="4" fill="none" stroke-linecap="round"><path d="M100 40 Q108 52 100 64"/><path d="M108 32 Q120 52 108 72"/></g>
    </svg>`;
  const ANILLO = `<svg viewBox="0 0 120 120" class="sui-anillo" aria-hidden="true"><circle cx="60" cy="60" r="52" fill="none" stroke="#e3eef7" stroke-width="12"/><circle class="sui-anillo-arco" cx="60" cy="60" r="52" fill="none" stroke="#2bb673" stroke-width="12" stroke-linecap="round" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" transform="rotate(-90 60 60)"/></svg>`;

  // Ajustes del profesional para este niño (plan de terapia)
  const ajustesPromesa = fetch('/juegos/respiracion/ajustes-microfono', { credentials: 'same-origin' })
    .then(r => r.ok ? r.json() : {}).catch(() => ({}))
    .then(a => ({ ruidoso: !!a.ruidoso, ayuda: a.ayuda !== false, exigencia: +a.exigencia || 0 }));
  const LS_EXIG = 'fono_soplo_exigencia_adulto';
  const exigenciaAdulto = () => { try { const v = sessionStorage.getItem(LS_EXIG); return v == null ? null : +v; } catch (e) { return null; } };
  const hablar = t => { try { window.FonoVoz?.hablar?.(t); } catch (e) {} };
  const adulto = t => { const el = document.getElementById('soplo-estado'); if (el) el.textContent = t; };
  const espera = ms => new Promise(r => setTimeout(r, ms));

  async function aplicarAjustes(det) {
    const a = await ajustesPromesa;
    const ex = exigenciaAdulto();
    det.ajustar({ ruidoso: a.ruidoso, exigencia: ex == null ? a.exigencia : ex });
    return a;
  }

  /* Reemplaza "pantallaSilencio + calibrar". Devuelve { ok, ajustes }. */
  async function preparar(escena, det, { probarSoplo = true } = {}) {
    actual = det;
    const a = await aplicarAjustes(det);
    sincronizarPanel(a);
    if (!det.estado.listo) { ocultarOverlay(escena); return { ok: false, ajustes: a }; }
    // 1. Escuchar el lugar: no hace falta silencio
    overlay(escena, `<div class="sui-prep">${OREJA}<div class="sui-puntos-oir"><span></span><span></span><span></span></div></div>`, 'sui-calibra');
    adulto('Escuchando el lugar… no hace falta silencio.');
    const reciente = det.estado.tienePrueba;
    await det.calibrar(reciente ? 800 : 1200);
    if (reciente || !probarSoplo) { ocultarOverlay(escena); return { ok: true, ajustes: a }; }
    // 2. Soplo de prueba cerca del micrófono
    const el = overlay(escena, `
      <div class="sui-prep sui-prueba">
        <div class="sui-prueba-fig">${ANILLO}<div class="sui-prueba-tel">${TELEFONO}</div></div>
        <div class="sui-prueba-cara">${SOPLA}</div>
        <div class="sui-cerca" hidden>${CERCA}</div>
      </div>`, 'sui-calibra sui-probando');
    adulto('Que el niño sople una vez cerca del micrófono (abajo del celular). Así el juego aprende cómo sopla.');
    hablar('Sopla aquí, cerquita');
    const arco = el.querySelector('.sui-anillo-arco'), cerca = el.querySelector('.sui-cerca'), fig = el.querySelector('.sui-prueba-fig');
    let sinAire = 0, avisado = false;
    const r = await det.calibrarSoplo({
      onProgreso(p, soplando) {
        arco.style.strokeDashoffset = String(100 - p * 100);
        fig.classList.toggle('activo', soplando);
        sinAire = soplando ? 0 : sinAire + 1;
        if (!avisado && sinAire > 200) { avisado = true; cerca.hidden = false; hablar('Más cerquita'); }
      }
    });
    if (r.ok) {
      el.innerHTML = `<div class="sui-prep sui-listo">${estrellas(3, 3)}</div>`;
      sonido('meta'); hablar('¡Muy bien!');
      adulto(`Listo: el juego ya conoce su soplo (${r.sobreDb} dB sobre el ruido).`);
      await espera(1100);
    } else {
      adulto(a.ayuda ? 'No se detectó el soplo de prueba. Se usa el ajuste estándar; si cuesta, abra «Adulto» y use la mano de ayuda.' : 'No se detectó el soplo de prueba. Se usa el ajuste estándar.');
      if (a.ayuda) mostrarAyuda(true);
      await espera(400);
    }
    ocultarOverlay(escena);
    return { ok: r.ok, ajustes: a };
  }

  /* Pista para el niño durante el juego: "¡más cerquita!" cuando sopla pero no llega */
  const CERCA = `<svg viewBox="0 0 140 90" class="sui-cerca-svg" aria-hidden="true">
      <rect x="92" y="6" width="34" height="66" rx="7" fill="#2f3b4c"/><rect x="96" y="12" width="26" height="48" rx="3" fill="#bfe3ff"/><circle cx="109" cy="66" r="4" fill="#ffca28"/>
      <path d="M14 46 L70 46" stroke="#ff7043" stroke-width="9" stroke-linecap="round"/><path d="M58 30 L80 46 L58 62" fill="none" stroke="#ff7043" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;
  let actual = null;
  function vigilarPistas(escena) {
    let burbuja = escena.querySelector('.sui-pista-cerca');
    if (!burbuja) { burbuja = document.createElement('div'); burbuja.className = 'sui-pista-cerca'; burbuja.hidden = true; burbuja.innerHTML = CERCA; escena.appendChild(burbuja); }
    let casiMs = 0, visibleHasta = 0, ult = performance.now(), ultimaVez = 0;
    (function tick(t) {
      const dt = Math.min(60, t - ult); ult = t;
      const st = actual?.estado; const ov = escena.querySelector('.sui-overlay');
      const jugando = st && st.listo && (!ov || ov.hidden);
      if (jugando && st.casi && !st.soplando) casiMs += dt; else casiMs = Math.max(0, casiMs - dt * 2);
      if (casiMs > 1100 && t > visibleHasta && t - ultimaVez > 6000) { visibleHasta = t + 2400; ultimaVez = t; casiMs = 0; hablar('¡Más cerquita!'); }
      burbuja.hidden = !(jugando && t < visibleHasta);
      requestAnimationFrame(tick);
    })(ult);
  }

  /* ── Panel para el adulto y mano de ayuda ─────────────────────────────── */
  let panelListo = false, ajustesActuales = null;
  function montarPanel() {
    if (panelListo || !window.FonoSoplo) return; panelListo = true;   // solo en juegos con detector de soplo
    const barra = document.querySelector('.soplo-barra'), controles = document.querySelector('.soplo-controles');
    if (!barra || !controles) return;
    const btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'sui-adulto-btn'; btn.setAttribute('aria-label', 'Ajustes para el adulto');
    btn.innerHTML = `<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="22" fill="#fff" stroke="#cfe3f2" stroke-width="2"/><path d="M14 18h20M14 30h20" stroke="#2e6f9e" stroke-width="4" stroke-linecap="round"/><circle cx="20" cy="18" r="4.5" fill="#ffca28" stroke="#2e6f9e" stroke-width="2.5"/><circle cx="29" cy="30" r="4.5" fill="#2bb673" stroke="#2e6f9e" stroke-width="2.5"/></svg><span>Adulto</span>`;
    barra.appendChild(btn);
    const panel = document.createElement('div');
    panel.className = 'sui-panel'; panel.hidden = true; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', 'Ajustes del micrófono');
    panel.innerHTML = `
      <div class="sui-panel-cab"><strong>Micrófono</strong><button type="button" class="sui-panel-x" aria-label="Cerrar">✕</button></div>
      <div class="sui-panel-fila"><span>Ruido del lugar</span><div class="sui-ruido"><i></i></div><b class="sui-ruido-txt">—</b></div>
      <div class="sui-panel-fila"><span>Soplo ahora</span><div class="sui-ruido sui-soplo-vivo"><i></i><em class="sui-umbral-marca"></em></div><b class="sui-soplo-txt">—</b></div>
      <p class="sui-panel-sub">¿Le cuesta que detecte el soplo?</p>
      <div class="sui-seg" role="group">
        <button type="button" data-ex="-1">Más fácil</button><button type="button" data-ex="0">Normal</button><button type="button" data-ex="1">Más exigente</button>
      </div>
      <div class="sui-panel-acciones">
        <button type="button" class="sui-recalibrar">Probar su soplo otra vez</button>
        <label class="sui-ayuda-check"><input type="checkbox"> Mostrar mano de ayuda</label>
      </div>
      <p class="sui-panel-nota"></p>`;
    barra.parentElement.insertBefore(panel, barra.nextSibling);
    const ayudaBtn = document.createElement('button');
    ayudaBtn.type = 'button'; ayudaBtn.className = 'sui-ayuda-btn'; ayudaBtn.hidden = true;
    ayudaBtn.setAttribute('aria-label', 'Ayuda del adulto: mantener presionado mientras el niño sopla');
    ayudaBtn.innerHTML = `${MANO}<span>Mantén mientras sopla</span>`;
    controles.appendChild(ayudaBtn);
    const on = () => { actual?.ayuda(true); ayudaBtn.classList.add('activo'); };
    const off = () => { actual?.ayuda(false); ayudaBtn.classList.remove('activo'); };
    ayudaBtn.addEventListener('pointerdown', e => { e.preventDefault(); ayudaBtn.setPointerCapture?.(e.pointerId); on(); });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(ev => ayudaBtn.addEventListener(ev, off));
    ayudaBtn.addEventListener('contextmenu', e => e.preventDefault());

    const abrir = v => { panel.hidden = !v; btn.classList.toggle('activo', v); };
    btn.addEventListener('click', () => abrir(panel.hidden));
    panel.querySelector('.sui-panel-x').addEventListener('click', () => abrir(false));
    panel.querySelectorAll('[data-ex]').forEach(b => b.addEventListener('click', () => {
      const v = +b.dataset.ex;
      try { sessionStorage.setItem(LS_EXIG, String(v)); } catch (e) {}
      actual?.ajustar({ exigencia: v }); marcarExig(v);
    }));
    panel.querySelector('.sui-recalibrar').addEventListener('click', async () => {
      if (!actual?.estado?.listo) { panel.querySelector('.sui-panel-nota').textContent = 'Primero toque el botón verde para empezar el juego.'; return; }
      actual.olvidarPrueba(); abrir(false);
      await preparar(document.getElementById('soplo-escena'), actual);
    });
    const chk = panel.querySelector('.sui-ayuda-check input');
    chk.addEventListener('change', () => mostrarAyuda(chk.checked));
    function marcarExig(v) { panel.querySelectorAll('[data-ex]').forEach(b => b.classList.toggle('activo', +b.dataset.ex === v)); }
    montarPanel.marcarExig = marcarExig; montarPanel.chk = chk; montarPanel.panel = panel; montarPanel.ayudaBtn = ayudaBtn;

    const barraR = panel.querySelector('.sui-ruido i'), txtR = panel.querySelector('.sui-ruido-txt');
    const barraS = panel.querySelector('.sui-soplo-vivo i'), marca = panel.querySelector('.sui-umbral-marca'), txtS = panel.querySelector('.sui-soplo-txt');
    const pct = d => Math.max(0, Math.min(100, (d + 80) / 70 * 100));
    (function vivo() {
      if (!panel.hidden && actual?.estado?.listo) {
        const st = actual.estado;
        barraR.style.width = pct(st.ruidoDb) + '%'; barraR.dataset.n = st.nivelRuido;
        txtR.textContent = { bajo: 'Bajo', medio: 'Medio', alto: 'Alto' }[st.nivelRuido];
        barraS.style.width = pct(st.db) + '%'; marca.style.left = pct(st.umbralDb) + '%';
        barraS.classList.toggle('ok', st.soplando);
        txtS.textContent = st.voz ? 'Voz' : st.asistido ? 'Ayuda' : st.soplando ? 'Soplo' : st.casi ? 'Casi' : '—';
      }
      requestAnimationFrame(vivo);
    })();
  }
  function mostrarAyuda(v) {
    montarPanel();
    if (!montarPanel.ayudaBtn) return;
    const permitido = ajustesActuales ? ajustesActuales.ayuda : true;
    montarPanel.ayudaBtn.hidden = !(v && permitido);
    if (montarPanel.chk) montarPanel.chk.checked = !!(v && permitido);
  }
  function sincronizarPanel(a) {
    ajustesActuales = a; montarPanel();
    const ex = exigenciaAdulto();
    montarPanel.marcarExig?.(ex == null ? a.exigencia : ex);
    const lbl = montarPanel.panel?.querySelector('.sui-ayuda-check');
    if (lbl) lbl.hidden = !a.ayuda;
    const nota = montarPanel.panel?.querySelector('.sui-panel-nota');
    if (nota) nota.textContent = (a.ruidoso ? 'El profesional marcó este niño como «lugar con ruido». ' : '') + (a.ayuda ? 'La ayuda del adulto queda registrada para el profesional.' : 'El profesional desactivó la ayuda del adulto.');
    if (a.ruidoso && a.ayuda) mostrarAyuda(true);
  }

  function alCargar() {
    montarPanel();
    ajustesPromesa.then(sincronizarPanel);
    const escena = document.getElementById('soplo-escena'); if (escena) vigilarPistas(escena);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', alCargar); else alCargar();

  return { pantallaInicio, pantallaSilencio, pantallaFinal, ocultarOverlay, medidor, sonido, estrellas, preparar, mostrarAyuda, ajustes: () => ajustesPromesa, icons: { PLAY, STOP, REPETIR, MANO, SOPLA, INSPIRA, HABLA_NO, TELEFONO } };
})();
