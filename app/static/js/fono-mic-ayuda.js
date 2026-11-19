/* FonoMic — ayudas de micrófono para TODOS los juegos con voz (no los de soplo,
 * que tienen su propio detector y panel en fono-soplo-ui.js).
 *
 * Problema: en un salón con ruido el reconocimiento de voz del navegador falla
 * y los juegos de cantar avanzan solos con el ruido. Aquí:
 *  - Para el niño: pista con dibujo «¡acércate y habla fuerte!» cuando no se
 *    le escucha (sin leer).
 *  - Para el adulto: botón «Adulto» con el ruido del lugar y consejos, y el botón
 *    verde «Lo dijo bien» para validar una palabra que el niño dijo bien pero
 *    el celular no entendió por el ruido. Queda registrado para el profesional.
 *  - FonoVozNivel: detector de VOZ (no ruido) para juegos de cantar/gritar:
 *    ruido del lugar adaptable + periodicidad (cuerdas vocales) + tono.
 *  - El profesional decide en el plan: lugar ruidoso, exigencia y si se permite
 *    la ayuda del adulto.
 *
 * API para los juegos:
 *   FonoMic.montar();                                // muestra el botón Adulto
 *   const i = FonoMic.vigilarIntento({ palabra, alValidar(){...} });  i.terminar(ok)
 *   FonoMic.fallo('no-speech' | 'no-coincide');      // pista para el niño si toca
 *   FonoMic.observarStream(stream);                  // mide el ruido con un stream ya abierto
 *   FonoMic.resumen()                                // texto para las notas del profesional
 *   const v = FonoVozNivel.crear(); await v.iniciar(); v.estado -> { voz, casi, intensidad, pitchHz, nivelRuido }
 */
(function () {
  'use strict';
  if (window.FonoMic) return;

  const ajustesPromesa = fetch('/juegos/ajustes-microfono', { credentials: 'same-origin' })
    .then(r => r.ok ? r.json() : {}).catch(() => ({}))
    .then(a => ({ ruidoso: !!a.ruidoso, ayuda: a.ayuda !== false, exigencia: +a.exigencia || 0 }));
  let ajustes = { ruidoso: false, ayuda: true, exigencia: 0 };
  ajustesPromesa.then(a => { ajustes = a; sincronizar(); });

  const est = { ruidoDb: null, nivelRuido: null, validaciones: [], pistas: 0, fallos: 0 };
  const nivelDe = d => d == null ? null : d < -55 ? 'bajo' : d < -42 ? 'medio' : 'alto';
  const hablar = t => { try { (window.FonoVoz?.hablar || window.FonoArticulacion?.hablarEspanol)?.(t); } catch (e) {} };

  /* ── Dibujos ── */
  const PISTA = `<svg viewBox="0 0 200 120" aria-hidden="true">
      <circle cx="52" cy="62" r="36" fill="#ffd9b8" stroke="#e8a77a" stroke-width="3"/>
      <path d="M20 52 Q24 22 52 22 Q82 22 86 52 Q76 36 52 36 Q30 36 20 52Z" fill="#6b3f1f"/>
      <circle cx="42" cy="58" r="4" fill="#2b2b2b"/><circle cx="64" cy="58" r="4" fill="#2b2b2b"/>
      <ellipse cx="56" cy="78" rx="8" ry="7" fill="#b5523b"/>
      <g class="fm-ondas" stroke="#7a5cc7" stroke-width="5" fill="none" stroke-linecap="round"><path d="M96 58 Q104 68 96 78"/><path d="M106 50 Q118 68 106 86"/></g>
      <path class="fm-flecha" d="M118 98 L150 98" stroke="#ff7043" stroke-width="8" stroke-linecap="round"/><path class="fm-flecha" d="M140 88 L154 98 L140 108" fill="none" stroke="#ff7043" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
      <rect x="160" y="30" width="32" height="64" rx="7" fill="#2f3b4c"/><rect x="164" y="36" width="24" height="46" rx="3" fill="#bfe3ff"/><circle cx="176" cy="88" r="3.5" fill="#ffca28"/>
    </svg>`;
  const CHECK = `<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="22" fill="#2bb673"/><path d="M13 25 L21 33 L36 16" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  const AJUSTES = `<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="22" fill="#fff" stroke="#cfe3f2" stroke-width="2"/><path d="M14 18h20M14 30h20" stroke="#2e6f9e" stroke-width="4" stroke-linecap="round"/><circle cx="20" cy="18" r="4.5" fill="#ffca28" stroke="#2e6f9e" stroke-width="2.5"/><circle cx="29" cy="30" r="4.5" fill="#2bb673" stroke="#2e6f9e" stroke-width="2.5"/></svg>`;

  function css() {
    if (document.getElementById('fm-css')) return;
    const s = document.createElement('style'); s.id = 'fm-css';
    s.textContent = `
.fm-adulto{position:fixed;top:10px;right:10px;z-index:9000;display:flex;align-items:center;gap:4px;border:none;background:#ffffffe6;border-radius:999px;padding:3px 10px 3px 3px;box-shadow:0 3px 12px #0002;cursor:pointer;font:700 .78rem system-ui,sans-serif;color:#2e6f9e}
.fm-adulto svg{width:34px;height:34px}
.fm-adulto.fm-en-barra{position:static;box-shadow:none;background:none;padding:0;flex:0 0 auto}
.soplo-barra:has(.fm-en-barra) .soplo-titulo{min-width:0;overflow:hidden}
.soplo-barra:has(.fm-en-barra){min-width:0}
@media (max-width:560px){.fm-adulto.fm-en-barra span{display:none}.fm-adulto.fm-en-barra svg{width:32px;height:32px}.soplo-barra:has(.fm-en-barra){gap:6px}.soplo-barra:has(.fm-en-barra) .soplo-niveles button{min-width:36px;padding:0 5px}.soplo-barra:has(.fm-en-barra) .soplo-titulo > svg:first-child{display:none}}
.fm-panel{position:fixed;top:56px;right:10px;left:auto;width:min(340px,calc(100vw - 20px));z-index:9001;background:#fff;border:2px solid #cfe3f2;border-radius:18px;padding:12px 14px;box-shadow:0 12px 30px #2e6f9e33;font:400 .86rem system-ui,sans-serif;color:#1d3b53;animation:fm-baja .25s ease both}
.fm-panel[hidden],.fm-ok[hidden],.fm-pista[hidden],.fm-toast[hidden]{display:none}
@keyframes fm-baja{from{transform:translateY(-8px);opacity:0}to{transform:none;opacity:1}}
.fm-cab{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.fm-x{border:none;background:#eef4f9;border-radius:50%;width:30px;height:30px;cursor:pointer;color:#2e6f9e}
.fm-fila{display:grid;grid-template-columns:96px 1fr 56px;gap:8px;align-items:center;margin:6px 0}
.fm-barra{height:14px;border-radius:8px;background:#eef4f9;overflow:hidden}.fm-barra i{display:block;height:100%;width:0;background:#7fd1a0;border-radius:8px;transition:width .2s}
.fm-barra i[data-n=medio]{background:#ffca28}.fm-barra i[data-n=alto]{background:#ef6c57}
.fm-fila b{text-align:right;color:#2e6f9e}
.fm-medir,.fm-boton{border:none;background:#2e9fd6;color:#fff;border-radius:12px;padding:8px 12px;font-weight:700;cursor:pointer;box-shadow:0 3px 0 #1f78a6}
.fm-consejo{background:#f3f9ff;border-radius:12px;padding:8px 10px;margin:8px 0;font-size:.82rem;line-height:1.35}
.fm-check{display:flex;gap:6px;align-items:center;margin-top:8px;cursor:pointer}
.fm-nota{margin:8px 0 0;font-size:.76rem;color:#58738a}
.fm-ok{position:fixed;left:12px;bottom:84px;z-index:9000;display:flex;flex-direction:column;align-items:center;gap:2px;border:3px solid #2bb673;background:#fff;border-radius:20px;padding:6px 8px;cursor:pointer;box-shadow:0 6px 18px #0002;font:800 .68rem system-ui,sans-serif;color:#1b7a4a;max-width:86px;text-align:center;line-height:1.1}
.fm-ok svg{width:42px;height:42px}
.fm-ok.pendiente{animation:fm-pulso 1.1s ease-in-out infinite}
@keyframes fm-pulso{0%,100%{box-shadow:0 6px 18px #0002,0 0 0 0 #2bb67366}50%{box-shadow:0 6px 18px #0002,0 0 0 12px #2bb67300}}
.fm-pista{position:fixed;left:50%;top:38%;transform:translate(-50%,-50%);z-index:9002;background:#fff3e0;border:4px solid #ffb74d;border-radius:26px;padding:10px 16px;box-shadow:0 14px 34px #0003;pointer-events:none;animation:fm-entra .45s cubic-bezier(.3,1.6,.5,1) both}
.fm-pista svg{width:min(250px,70vw);height:auto;display:block}
.fm-ondas path{animation:fm-oir .9s ease-in-out infinite}.fm-ondas path:nth-child(2){animation-delay:.2s}
.fm-flecha{animation:fm-empuja .8s ease-in-out infinite}
@keyframes fm-oir{0%,100%{opacity:.25}50%{opacity:1}}
@keyframes fm-empuja{0%,100%{transform:translateX(0)}50%{transform:translateX(8px)}}
@keyframes fm-entra{from{transform:translate(-50%,-50%) scale(.3);opacity:0}to{transform:translate(-50%,-50%) scale(1);opacity:1}}
.fm-toast{position:fixed;left:50%;bottom:150px;transform:translateX(-50%);z-index:9003;background:#1d3b53;color:#fff;border-radius:14px;padding:8px 14px;font:700 .85rem system-ui,sans-serif;box-shadow:0 6px 18px #0003}
@media (prefers-reduced-motion:reduce){.fm-ondas path,.fm-flecha,.fm-ok.pendiente{animation:none}}`;
    document.head.appendChild(s);
  }

  /* ── Interfaz ── */
  let ui = null;
  function montar() {
    if (ui || window.FonoSoplo) return;   // los juegos de soplo tienen su propio panel (fono-soplo-ui.js)
    if (!document.body) { document.addEventListener('DOMContentLoaded', montar, { once: true }); return; }
    css();
    const btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'fm-adulto'; btn.setAttribute('aria-label', 'Ajustes del micrófono para el adulto');
    btn.innerHTML = `${AJUSTES}<span>Adulto</span>`;
    const panel = document.createElement('div');
    panel.className = 'fm-panel'; panel.hidden = true; panel.setAttribute('role', 'dialog');
    panel.innerHTML = `
      <div class="fm-cab"><strong>Micrófono</strong><button type="button" class="fm-x" aria-label="Cerrar">✕</button></div>
      <div class="fm-fila"><span>Ruido del lugar</span><div class="fm-barra"><i></i></div><b class="fm-nivel">—</b></div>
      <button type="button" class="fm-medir">Medir el ruido ahora</button>
      <div class="fm-consejo">Si hay ruido: que el niño hable <b>cerca del celular</b> (a un palmo) y fuerte, y aleje el celular de otros niños o parlantes.</div>
      <label class="fm-check"><input type="checkbox"> Mostrar botón verde «Lo dijo bien»</label>
      <p class="fm-nota"></p>`;
    const ok = document.createElement('button');
    ok.type = 'button'; ok.className = 'fm-ok'; ok.hidden = true;
    ok.setAttribute('aria-label', 'El adulto confirma que el niño lo dijo bien');
    ok.innerHTML = `${CHECK}<span>Lo dijo bien</span>`;
    const pista = document.createElement('div'); pista.className = 'fm-pista'; pista.hidden = true; pista.innerHTML = PISTA;
    const toast = document.createElement('div'); toast.className = 'fm-toast'; toast.hidden = true; toast.setAttribute('role', 'status');
    const barra = document.querySelector('.soplo-barra');
    if (barra) { btn.classList.add('fm-en-barra'); barra.appendChild(btn); document.body.append(panel, ok, pista, toast); }
    else document.body.append(btn, panel, ok, pista, toast);
    ui = { btn, panel, ok, pista, toast, chk: panel.querySelector('.fm-check input'), barra: panel.querySelector('.fm-barra i'), nivel: panel.querySelector('.fm-nivel'), nota: panel.querySelector('.fm-nota') };
    btn.addEventListener('click', () => { panel.hidden = !panel.hidden; pintarRuido(); });
    panel.querySelector('.fm-x').addEventListener('click', () => panel.hidden = true);
    panel.querySelector('.fm-medir').addEventListener('click', async e => {
      const b = e.currentTarget; b.disabled = true; b.textContent = 'Escuchando…';
      await medirRuido(1500); b.disabled = false; b.textContent = 'Medir el ruido otra vez'; pintarRuido();
    });
    ui.chk.addEventListener('change', () => mostrarOk(ui.chk.checked));
    ok.addEventListener('click', validar);
    sincronizar();
  }
  function mostrarOk(v) { if (!ui) return; const permitido = ajustes.ayuda; ui.ok.hidden = !(v && permitido); ui.chk.checked = !!(v && permitido); }
  function sincronizar() {
    if (!ui) return;
    ui.chk.parentElement.hidden = !ajustes.ayuda;
    ui.nota.textContent = (ajustes.ruidoso ? 'El profesional marcó «lugar con ruido». ' : '') + (ajustes.ayuda ? 'Lo validado por el adulto queda registrado para el profesional.' : 'El profesional desactivó la validación del adulto.');
    if (ajustes.ruidoso && ajustes.ayuda) mostrarOk(true);
  }
  function pintarRuido() {
    if (!ui || est.ruidoDb == null) return;
    ui.barra.style.width = Math.max(4, Math.min(100, (est.ruidoDb + 80) / 70 * 100)) + '%';
    ui.barra.dataset.n = est.nivelRuido; ui.nivel.textContent = { bajo: 'Bajo', medio: 'Medio', alto: 'Alto' }[est.nivelRuido];
  }
  let toastT = 0;
  function aviso(t) { if (!ui) return; ui.toast.textContent = t; ui.toast.hidden = false; clearTimeout(toastT); toastT = setTimeout(() => ui.toast.hidden = true, 1800); }

  /* ── Validación del adulto ── */
  let pendiente = null;
  function vigilarIntento({ palabra = '', alValidar } = {}) {
    montar();
    const yo = { palabra, fn: alValidar, hasta: Infinity };
    pendiente = yo; ui?.ok.classList.add('pendiente');
    return {
      terminar(acerto) {
        if (pendiente !== yo) return;
        if (acerto) { pendiente = null; ui?.ok.classList.remove('pendiente'); }
        else { yo.hasta = performance.now() + 9000; setTimeout(() => { if (pendiente === yo && performance.now() >= yo.hasta) { pendiente = null; ui?.ok.classList.remove('pendiente'); } }, 9100); }
      },
      cancelar() { if (pendiente === yo) { pendiente = null; ui?.ok.classList.remove('pendiente'); } },
    };
  }
  function validar() {
    const p = pendiente;
    if (!p || performance.now() > p.hasta || typeof p.fn !== 'function') { aviso('Primero que el niño intente decirlo'); return; }
    pendiente = null; ui?.ok.classList.remove('pendiente');
    est.validaciones.push(p.palabra || '(sin palabra)');
    aviso('✓ Validado por el adulto');
    try { p.fn({ transcript: p.palabra, validadoAdulto: true }); } catch (e) { console.error(e); }
  }

  /* ── Pista para el niño ── */
  let ultimaPista = -1e9;
  function pistaCerca(forzar = false) {
    montar(); if (!ui) return;
    const t = performance.now();
    if (!forzar && t - ultimaPista < 8000) return;
    ultimaPista = t; est.pistas++;
    ui.pista.hidden = false; hablar('¡Acércate y habla fuerte!');
    setTimeout(() => { if (ui) ui.pista.hidden = true; }, 2600);
  }
  function fallo(tipo) {
    est.fallos++;
    const ruido = ajustes.ruidoso || est.nivelRuido === 'medio' || est.nivelRuido === 'alto';
    if (tipo === 'no-speech' || ruido || est.fallos % 2 === 0) pistaCerca();
    if (ajustes.ayuda && est.fallos >= 2 && ui && ui.ok.hidden && ui.chk.parentElement && !ui.chk.parentElement.hidden && ruido) mostrarOk(true);
  }

  /* ── Ruido del lugar ── */
  function registrarRuido(db) { est.ruidoDb = db; est.nivelRuido = nivelDe(db); pintarRuido(); }
  async function medirRuido(ms = 1500) {
    let stream = null, ctx = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false } });
      ctx = new (window.AudioContext || window.webkitAudioContext)(); if (ctx.state === 'suspended') await ctx.resume();
      const an = ctx.createAnalyser(); an.fftSize = 2048; ctx.createMediaStreamSource(stream).connect(an);
      const buf = new Float32Array(2048), m = [];
      const fin = performance.now() + ms;
      while (performance.now() < fin) { an.getFloatTimeDomainData(buf); m.push(dbDe(buf)); await new Promise(r => setTimeout(r, 40)); }
      m.sort((a, b) => a - b); registrarRuido(m[Math.floor(m.length * 0.5)]);
    } catch (e) { aviso('No se pudo usar el micrófono'); }
    finally { stream?.getTracks().forEach(t => t.stop()); try { ctx?.close(); } catch (e) {} }
    return est.nivelRuido;
  }
  function dbDe(buf) { let s = 0; for (let i = 0; i < buf.length; i++) s += buf[i] * buf[i]; return 20 * Math.log10(Math.sqrt(s / buf.length) + 1e-9); }
  // Con un stream ya abierto por el juego (p. ej. la grabación de evidencia): piso de ruido = envolvente baja
  function observarStream(stream) {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const an = ctx.createAnalyser(); an.fftSize = 2048; ctx.createMediaStreamSource(stream).connect(an);
      const buf = new Float32Array(2048); let piso = null;
      const iv = setInterval(() => {
        if (!stream.active) { clearInterval(iv); try { ctx.close(); } catch (e) {} return; }
        an.getFloatTimeDomainData(buf); const d = dbDe(buf);
        piso = piso == null ? d : piso + (d - piso) * (d < piso ? 0.3 : 0.02);
        registrarRuido(piso);
      }, 100);
    } catch (e) {}
  }

  function resumen() {
    const partes = [];
    if (est.nivelRuido) partes.push(`ruido del lugar ${est.nivelRuido} (${Math.round(est.ruidoDb)} dB)`);
    if (ajustes.ruidoso) partes.push('modo lugar ruidoso');
    if (est.validaciones.length) partes.push(`VALIDADO POR EL ADULTO ${est.validaciones.length} ${est.validaciones.length === 1 ? 'vez' : 'veces'} (${est.validaciones.join(', ')})`);
    if (est.pistas) partes.push(`pista «acércate y habla fuerte» ${est.pistas} ${est.pistas === 1 ? 'vez' : 'veces'}`);
    return partes.length ? `Micrófono: ${partes.join('; ')}.` : '';
  }

  if (document.readyState !== 'loading') setTimeout(autoMontar, 0); else document.addEventListener('DOMContentLoaded', autoMontar);
  function autoMontar() { if (document.querySelector('[data-fono-mic]') || window.FONO_USA_MICROFONO) montar(); }
  window.FonoMic = { montar, vigilarIntento, validar, fallo, pistaCerca, medirRuido, observarStream, resumen, ajustes: () => ajustesPromesa, estado: est, mostrarOk };

  /* ── Detector de VOZ para juegos de cantar / gritar ─────────────────────── */
  const CFG_VOZ = { margenDb: 9, claridadVoz: 0.55, msActivar: 90, msSoltar: 220, rangoDb: 26, subida: 0.004, bajada: 0.06 };
  function crearVoz(opciones = {}) {
    const cfg = Object.assign({}, CFG_VOZ, opciones.config || {});
    let ctx = null, stream = null, an = null, raf = 0, t = null, f = null, sr = 48000;
    let ruidoDb = -50, calibrando = false, muestras = [], ajusteDb = 0;
    let desde = 0, falta = 0, voz = false, suave = 0, tecla = false, ult = performance.now();
    const estado = { listo: false, voz: false, casi: false, intensidad: 0, db: -100, ruidoDb, umbralDb: -41, claridad: 0, pitchHz: 0, nivelRuido: 'bajo', simulado: false };
    const onKey = e => { if (e.code === 'Space' && !/INPUT|TEXTAREA/.test(e.target?.tagName || '')) { tecla = e.type === 'keydown'; } };
    async function iniciar({ calibrarMs = 900 } = {}) {
      window.addEventListener('keydown', onKey); window.addEventListener('keyup', onKey);
      const a = await ajustesPromesa;
      ajusteDb = (a.exigencia || 0) * 3 + (opciones.ajusteDb || 0);
      try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false, channelCount: 1 } });
        ctx = new (window.AudioContext || window.webkitAudioContext)(); if (ctx.state === 'suspended') await ctx.resume();
        sr = ctx.sampleRate;
        const src = ctx.createMediaStreamSource(stream);
        const hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 70;
        an = ctx.createAnalyser(); an.fftSize = 2048; an.smoothingTimeConstant = 0.3;
        src.connect(hp); hp.connect(an);
        t = new Float32Array(2048); f = new Float32Array(1024);
        estado.listo = true; estado.stream = stream;
        calibrando = true; muestras = [];
        setTimeout(() => { calibrando = false; if (muestras.length) { muestras.sort((x, y) => x - y); ruidoDb = Math.max(-80, Math.min(-15, muestras[Math.floor(muestras.length * 0.6)])); } }, calibrarMs);
      } catch (e) { console.warn('FonoVozNivel: sin micrófono', e); }
      ult = performance.now(); bucle();
      return estado.listo;
    }
    function analizar() {
      an.getFloatTimeDomainData(t); an.getFloatFrequencyData(f);
      const db = dbDe(t);
      const paso = 2, mm = 512, srD = sr / paso;
      let r0 = 0; for (let i = 0; i < mm; i++) r0 += t[i * paso] ** 2;
      let mejor = 0, lagMejor = 0;
      if (r0 > 1e-9) for (let lag = Math.floor(srD / 900); lag <= Math.floor(srD / 70); lag++) {
        let r = 0, e = 0; for (let i = 0; i < mm - lag; i++) { const a = t[i * paso], b = t[(i + lag) * paso]; r += a * b; e += b * b; }
        const n = r / Math.sqrt(r0 * e + 1e-12); if (n > mejor) { mejor = n; lagMejor = lag; }
      }
      return { db, claridad: mejor, pitchHz: lagMejor ? srD / lagMejor : 0 };
    }
    function bucle() {
      const ahora = performance.now(); const dt = Math.min(60, ahora - ult); ult = ahora;
      let db = -100, claridad = 0, pitchHz = 0;
      if (an) ({ db, claridad, pitchHz } = analizar());
      if (calibrando) muestras.push(db);
      const umbral = ruidoDb + Math.max(4, cfg.margenDb + ajusteDb);
      const periodico = claridad > cfg.claridadVoz;
      const candidato = !calibrando && db > umbral && periodico;
      if (candidato) { falta = 0; if (!desde) desde = ahora; if (ahora - desde >= cfg.msActivar) voz = true; }
      else { desde = 0; if (!falta) falta = ahora; if (ahora - falta >= cfg.msSoltar) voz = false; }
      const casi = !voz && periodico && db > ruidoDb + 2.5 && db <= umbral;
      if (!calibrando && !voz && !desde && !casi && an) {
        ruidoDb += (db - ruidoDb) * (db < ruidoDb ? cfg.bajada : cfg.subida);
        ruidoDb = Math.max(-80, Math.min(-15, ruidoDb));
      }
      let obj = voz ? Math.max(0.08, Math.min(1, (db - umbral) / cfg.rangoDb + 0.1)) : 0;
      estado.simulado = tecla; if (tecla) { obj = 0.7; pitchHz = pitchHz || 260; }
      suave += (obj - suave) * (obj > suave ? 0.35 : 0.15); if (suave < 0.01) suave = 0;
      Object.assign(estado, { voz: voz || tecla, casi, intensidad: suave, db, ruidoDb, umbralDb: umbral, claridad, pitchHz: (voz || tecla) ? pitchHz : 0, nivelRuido: nivelDe(ruidoDb), calibrando });
      if (!calibrando && an) registrarRuido(ruidoDb);
      // pista para el niño: intenta pero no llega
      if (casi) { casiMs += dt; if (casiMs > 1400) { casiMs = 0; pistaCerca(); } } else casiMs = Math.max(0, casiMs - dt);
      raf = requestAnimationFrame(bucle);
    }
    let casiMs = 0;
    function detener() {
      cancelAnimationFrame(raf); raf = 0;
      window.removeEventListener('keydown', onKey); window.removeEventListener('keyup', onKey);
      stream?.getTracks().forEach(x => x.stop()); stream = null;
      try { ctx?.close(); } catch (e) {} ctx = null; an = null; estado.listo = false;
    }
    montar();
    return { iniciar, detener, estado };
  }
  window.FonoVozNivel = { crear: crearVoz };
})();
