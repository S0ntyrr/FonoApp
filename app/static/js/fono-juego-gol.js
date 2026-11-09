/* ¡Haz un gol! — penal en vista 3D, apuntar con el dedo y patear con la voz.
 * - Apuntar: arrastrar el dedo (o ratón / flechas) a izquierda o derecha.
 * - Fuerza: mientras el niño dice «GOOOOOL» se llena la barra; la fuerza decide
 *   la ALTURA del tiro (poco = rasante, más = alto, demasiado = por encima).
 * - Solo vale la palabra «gol»: si el navegador reconoce voz se exige que diga
 *   «gol»; si no (sin Internet o navegador sin soporte), se exige voz sostenida
 *   con sonido de O (análisis acústico).
 */
(function () {
  'use strict';
  const NIVELES = {
    1: { tiros: 5, adivina: 0.25, alcance: 0.30, velArquero: 0.5 },
    2: { tiros: 5, adivina: 0.4, alcance: 0.32, velArquero: 0.8 },
    3: { tiros: 5, adivina: 0.55, alcance: 0.34, velArquero: 1.1 },
  };
  const $ = s => document.querySelector(s);

  let canvas, g, W = 0, H = 0, escena, nivel = 1, cfg = NIVELES[1], fase = 'inicio';
  let mira = 0, teclas = { izq: false, der: false }, arrastrando = false;
  let potencia = 0, vozDesde = 0, ultimaVoz = 0, framesVoz = 0, framesO = 0, picoVoz = 0;
  let tiro = null, arquero = { x: 0, objetivo: 0, salto: 0 }, goles = 0, tiros = 0, resultado = null, celebracion = 0, confeti = [];
  let audio = null, rec = null, recOk = false, recErr = '', escuchoGol = 0, transcripciones = [];
  let historial = [], ultimo = 0;

  // ── Audio: voz, fuerza y «o» ──
  async function iniciarAudio() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: false, autoGainControl: false } });
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      if (ctx.state === 'suspended') await ctx.resume();
      const src = ctx.createMediaStreamSource(stream);
      const an = ctx.createAnalyser(); an.fftSize = 2048; an.smoothingTimeConstant = 0.3;
      src.connect(an);
      audio = { ctx, stream, an, t: new Float32Array(2048), f: new Float32Array(1024), ruido: -60, muestras: [], calibrando: true };
      setTimeout(() => {
        const m = audio.muestras.sort((a, b) => a - b);
        if (m.length) audio.ruido = Math.max(-75, Math.min(-25, m[Math.floor(m.length * 0.6)]));
        audio.calibrando = false;
      }, 1200);
      return true;
    } catch (e) { return false; }
  }
  function leerAudio() {
    if (!audio) return { voz: false, nivel: 0, o: false };
    const { an, t, f, ctx } = audio;
    an.getFloatTimeDomainData(t); an.getFloatFrequencyData(f);
    let s = 0; for (let i = 0; i < t.length; i++) s += t[i] * t[i];
    const db = 20 * Math.log10(Math.sqrt(s / t.length) + 1e-9);
    if (audio.calibrando) { audio.muestras.push(db); return { voz: false, nivel: 0, o: false }; }
    // periodicidad (la voz vibra; el soplo/ruido no)
    const N = 1024, paso = 2, m = N / paso, sr = ctx.sampleRate / paso;
    let r0 = 0; for (let i = 0; i < m; i++) r0 += t[i * paso] ** 2;
    let mejor = 0;
    for (let lag = Math.floor(sr / 450); lag <= Math.floor(sr / 70); lag++) {
      let r = 0, e = 0; for (let i = 0; i < m - lag; i++) { const a = t[i * paso], b = t[(i + lag) * paso]; r += a * b; e += b * b; }
      mejor = Math.max(mejor, r / Math.sqrt(r0 * e + 1e-12));
    }
    const sobre = db - audio.ruido;
    const voz = sobre > 10 && mejor > 0.55;
    // «o»: energía grave (250–1100 Hz) domina sobre la aguda (1100–3500 Hz)
    const hz = ctx.sampleRate / an.fftSize;
    let baja = 0, alta = 0;
    for (let i = Math.floor(250 / hz); i < Math.floor(1100 / hz); i++) baja += Math.pow(10, f[i] / 10);
    for (let i = Math.floor(1100 / hz); i < Math.floor(3500 / hz); i++) alta += Math.pow(10, f[i] / 10);
    const o = voz && baja / (alta + 1e-12) > 3;
    return { voz, nivel: Math.max(0, Math.min(1, (sobre - 10) / 28)), o };
  }

  // ── Reconocimiento de la palabra «gol» ──
  function iniciarReconocimiento() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { recErr = 'sin-soporte'; return; }
    rec = new SR();
    rec.lang = 'es-ES'; rec.continuous = true; rec.interimResults = true; rec.maxAlternatives = 3;
    rec.onresult = ev => {
      for (let i = ev.resultIndex; i < ev.results.length; i++) {
        for (let j = 0; j < ev.results[i].length; j++) {
          const txt = (ev.results[i][j].transcript || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
          if (/\bgo+l+\b|\bgo+o+l|\bgool|\bgoo+/.test(txt)) { escuchoGol = performance.now(); }
          if (ev.results[i].isFinal && j === 0 && txt.trim()) transcripciones.push(txt.trim());
        }
      }
      recOk = true;
    };
    rec.onerror = e => { if (['network', 'not-allowed', 'service-not-allowed', 'audio-capture'].includes(e.error)) recErr = e.error; };
    rec.onend = () => { if (fase !== 'fin' && fase !== 'inicio' && !recErr) { try { rec.start(); } catch (_) {} } };
    try { rec.start(); } catch (_) { recErr = 'no-inicia'; }
  }
  function detenerReconocimiento() { try { rec && rec.abort(); } catch (_) {} rec = null; }
  const usaPalabra = () => !!rec && !recErr;

  // ── Juego ──
  function iniciar() {
    escena = $('#gol-escena'); canvas = $('#gol-canvas'); g = canvas.getContext('2d');
    nivel = Math.max(1, Math.min(3, parseInt(new URLSearchParams(location.search).get('nivel') || '1', 10) || 1));
    document.querySelectorAll('[data-nivel]').forEach(b => b.addEventListener('click', () => { if (fase === 'inicio') elegirNivel(+b.dataset.nivel); }));
    $('#gol-parar').addEventListener('click', () => terminar());
    canvas.addEventListener('pointerdown', e => { arrastrando = true; canvas.setPointerCapture?.(e.pointerId); apuntar(e); });
    canvas.addEventListener('pointermove', e => { if (arrastrando) apuntar(e); });
    ['pointerup', 'pointercancel'].forEach(t => canvas.addEventListener(t, () => arrastrando = false));
    window.addEventListener('keydown', e => { if (e.code === 'ArrowLeft') teclas.izq = true; if (e.code === 'ArrowRight') teclas.der = true; if (e.code === 'Space') { simVoz = true; e.preventDefault(); } });
    window.addEventListener('keyup', e => { if (e.code === 'ArrowLeft') teclas.izq = false; if (e.code === 'ArrowRight') teclas.der = false; if (e.code === 'Space') simVoz = false; });
    window.addEventListener('resize', ajustar);
    ajustar(); elegirNivel(nivel);
    ultimo = performance.now(); requestAnimationFrame(loop);
  }
  let simVoz = false;   // para probar sin micrófono: mantener la barra espaciadora = «goooool»

  function elegirNivel(n) {
    nivel = n; cfg = NIVELES[n];
    document.querySelectorAll('[data-nivel]').forEach(b => b.classList.toggle('activo', +b.dataset.nivel === n));
    reiniciar();
  }

  function pantallaInicio() {
    const I = window.FonoIconos || {};
    const ico = (n, cls = '') => `<svg class="${cls}" viewBox="0 0 64 64">${I[n] || ''}</svg>`;
    const el = document.createElement('div');
    el.className = 'sui-overlay';
    el.innerHTML = `
      <div class="sui-pasos gol-pasos">
        <div class="sui-paso"><div class="sui-num">1</div><div class="gol-paso-ico animar">${ico('arrastrar')}</div><b>Apunta</b></div>
        <div class="sui-flecha">&#10140;</div>
        <div class="sui-paso"><div class="sui-num">2</div><div class="gol-paso-ico">${ico('boca_o', 'fa-siempre')}</div><b class="gol-grito">GOOOOL</b></div>
        <div class="sui-flecha">&#10140;</div>
        <div class="sui-paso"><div class="sui-num">3</div><div class="gol-paso-ico animar">${ico('gol')}</div><b>¡Tiro!</b></div>
      </div>
      <button type="button" class="sui-boton-grande" aria-label="Empezar">${FonoSoploUI.icons.PLAY}</button>`;
    escena.querySelector('.sui-overlay')?.remove();
    escena.appendChild(el);
    el.querySelector('button').addEventListener('click', empezar, { once: true });
  }

  function reiniciar() {
    detenerReconocimiento(); cerrarAudio();
    fase = 'inicio'; goles = 0; tiros = 0; tiro = null; resultado = null; confeti = []; historial = []; transcripciones = [];
    potencia = 0; mira = 0; recErr = ''; recOk = false;
    $('#gol-parar').hidden = true; pintarMarcador();
    estadoAdulto('Toca el botón verde para empezar.');
    pantallaInicio();
  }

  async function empezar() {
    fase = 'preparando';
    escena.querySelector('.sui-overlay')?.remove();
    estadoAdulto('Pidiendo el micrófono… silencio un momento.');
    const ok = await iniciarAudio();
    iniciarReconocimiento();
    window.FonoEvidencia?.iniciar?.();
    estadoAdulto(ok ? 'Mueve el dedo para apuntar y di «GOOOOOOL» largo: mientras más largo y fuerte, más alto sale el tiro.' : 'No se pudo usar el micrófono (para probar: mantener la barra espaciadora).');
    setTimeout(() => { fase = 'apuntando'; $('#gol-parar').hidden = false; }, 1300);
  }

  function apuntar(e) {
    const r = canvas.getBoundingClientRect();
    mira = Math.max(-1, Math.min(1, ((e.clientX - r.left) / r.width - 0.5) * 2.2));
  }

  function ajustar() {
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const r = canvas.getBoundingClientRect(); W = r.width; H = r.height;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function loop(ahora) {
    const dt = Math.min(0.05, (ahora - ultimo) / 1000); ultimo = ahora;
    if (teclas.izq) mira = Math.max(-1, mira - dt * 1.6);
    if (teclas.der) mira = Math.min(1, mira + dt * 1.6);
    // arquero se mueve de lado a lado mientras espera
    if (!tiro) { arquero.objetivo = Math.sin(ahora / 1000 * cfg.velArquero) * 0.45; arquero.x += (arquero.objetivo - arquero.x) * Math.min(1, dt * 3); arquero.salto = 0; }

    if (fase === 'apuntando' || fase === 'cargando') {
      const a = simVoz ? { voz: true, nivel: 0.6, o: true } : leerAudio();
      if (a.voz) {
        if (fase === 'apuntando') { fase = 'cargando'; vozDesde = ahora; framesVoz = 0; framesO = 0; picoVoz = 0; potencia = 0; }
        ultimaVoz = ahora; framesVoz++; if (a.o) framesO++; picoVoz = Math.max(picoVoz, a.nivel);
        potencia = Math.min(1.05, potencia + dt / 2.2 * (0.6 + a.nivel * 0.8));
      }
      if (fase === 'cargando' && ahora - ultimaVoz > 320) { fase = 'validando'; validar(ahora); }
      if (fase === 'cargando' && ahora - vozDesde > 4000) { fase = 'validando'; validar(ahora); }
    }
    if (tiro) avanzarTiro(dt, ahora);
    confeti.forEach(c => { c.x += c.vx * dt; c.y += c.vy * dt; c.vy += 260 * dt; c.vida -= dt * 0.5; }); confeti = confeti.filter(c => c.vida > 0);
    celebracion = Math.max(0, celebracion - dt * 0.5);
    dibujar(ahora);
    requestAnimationFrame(loop);
  }

  function validar(ahora) {
    const durVoz = (ultimaVoz - vozDesde) / 1000;
    const fraccionO = framesVoz ? framesO / framesVoz : 0;
    const finVoz = ultimaVoz;
    const decidir = () => {
      let valido, motivo;
      if (escuchoGol >= vozDesde - 500) {
        valido = true; motivo = 'palabra «gol» reconocida';
      } else if (usaPalabra() && recOk) {
        valido = false; motivo = 'no se reconoció «gol»';
      } else {
        valido = durVoz >= 0.5 && fraccionO >= 0.45;
        motivo = valido ? 'voz sostenida con O (sin reconocimiento de palabras)' : 'voz corta o sin sonido de O';
      }
      if (simVoz || (!audio && !rec)) { valido = true; motivo = 'simulado'; }
      if (potencia < 0.12) { valido = false; motivo = 'muy corto'; }
      historial.push({ potencia: +potencia.toFixed(2), duracion: +durVoz.toFixed(1), o: +fraccionO.toFixed(2), pico: +picoVoz.toFixed(2), valido, motivo });
      if (!valido) { avisoDiGol(); fase = 'apuntando'; potencia = 0; return; }
      patear();
    };
    // Esperar un momento el resultado del reconocedor
    if (usaPalabra() && escuchoGol < vozDesde - 500) {
      const espera = setInterval(() => {
        if (escuchoGol >= vozDesde - 500 || performance.now() - finVoz > 1400 || recErr) { clearInterval(espera); decidir(); }
      }, 100);
    } else decidir();
  }

  let avisoHasta = 0;
  function avisoDiGol() { avisoHasta = performance.now() + 2200; FonoSoploUI.sonido('golpe'); }

  function patear() {
    tiros++;
    const altura = Math.min(1.15, potencia);          // 0 = rasante, 1 = travesaño, >1 = por encima
    const x = mira;
    // el arquero adivina el lado con cierta probabilidad
    // Adivina el lado según el nivel; si no adivina, se lanza al lado contrario.
    const adivina = Math.random() < cfg.adivina;
    const ladoBalon = Math.abs(x) < 0.15 ? 0 : Math.sign(x);
    if (adivina) arquero.objetivo = Math.max(-0.8, Math.min(0.8, x + (Math.random() - 0.5) * 0.2));
    else arquero.objetivo = ladoBalon === 0 ? (Math.random() < 0.5 ? -0.6 : 0.6) : -ladoBalon * 0.55;
    tiro = { t: 0, x, altura, salio: altura > 1.0 || Math.abs(x) > 0.98 };
    fase = 'tiro';
    FonoSoploUI.sonido('golpe');
  }

  function avanzarTiro(dt, ahora) {
    tiro.t = Math.min(1, tiro.t + dt * 1.6);
    arquero.x += (arquero.objetivo - arquero.x) * Math.min(1, dt * 6);
    arquero.salto = Math.min(1, arquero.salto + dt * 3);
    if (tiro.t >= 1 && !tiro.fin) {
      tiro.fin = true;
      const cerca = Math.abs(arquero.x - tiro.x) < cfg.alcance && tiro.altura < 0.92;
      if (tiro.salio) resultado = 'fuera';
      else if (cerca) resultado = 'atajada';
      else { resultado = 'gol'; goles++; celebrar(); }
      historial[historial.length - 1].resultado = resultado;
      pintarMarcador();
      setTimeout(() => {
        tiro = null; resultado = null; potencia = 0;
        if (tiros >= cfg.tiros) terminar(); else fase = 'apuntando';
      }, resultado === 'gol' ? 2400 : 1600);
    }
  }

  function celebrar() {
    celebracion = 1;
    for (let i = 0; i < 80; i++) confeti.push({ x: W / 2, y: H * 0.3, vx: (Math.random() - 0.5) * 520, vy: -Math.random() * 380, vida: 1, c: ['#e53935', '#2bb673', '#f2b400', '#2e86de', '#8e6bd6'][i % 5] });
    FonoSoploUI.sonido('meta');
  }

  function pintarMarcador() {
    const el = $('#gol-marcador'); if (!el) return;
    let h = '';
    for (let i = 0; i < cfg.tiros; i++) {
      const r = historial.filter(x => x.resultado)[i]?.resultado;
      h += `<span class="gol-ficha ${r || ''}"></span>`;
    }
    el.innerHTML = h;
  }

  // ── Dibujo pseudo-3D ──
  function dibujar(ahora) {
    const hz = H * 0.34;
    // tribuna y cielo
    const cielo = g.createLinearGradient(0, 0, 0, hz); cielo.addColorStop(0, '#7fc4ff'); cielo.addColorStop(1, '#cfe9ff');
    g.fillStyle = cielo; g.fillRect(0, 0, W, hz);
    g.fillStyle = '#5a6b8c'; g.fillRect(0, hz * 0.45, W, hz * 0.55);
    for (let y = hz * 0.5; y < hz; y += 8) for (let x = (y / 8 % 2) * 5; x < W; x += 10) {
      g.fillStyle = ['#ffd54a', '#e53935', '#fff', '#2e86de', '#2bb673'][Math.floor((x * 7 + y * 3) % 5)];
      g.fillRect(x + Math.sin(ahora / 300 + x) * (celebracion * 2), y - (celebracion ? Math.abs(Math.sin(ahora / 120 + x)) * 3 : 0), 4, 4);
    }
    // césped con franjas en perspectiva
    for (let i = 0; i < 14; i++) {
      const y0 = hz + (H - hz) * Math.pow(i / 14, 1.6), y1 = hz + (H - hz) * Math.pow((i + 1) / 14, 1.6);
      g.fillStyle = i % 2 ? '#4caf50' : '#43a047'; g.fillRect(0, y0, W, y1 - y0 + 1);
    }
    // líneas del área
    g.strokeStyle = 'rgba(255,255,255,.85)'; g.lineWidth = 3;
    g.beginPath(); g.moveTo(W * 0.08, H); g.lineTo(W * 0.2, hz + 4); g.lineTo(W * 0.8, hz + 4); g.lineTo(W * 0.92, H); g.stroke();
    g.beginPath(); g.ellipse(W / 2, H * 0.86, 4, 2, 0, 0, Math.PI * 2); g.fillStyle = '#fff'; g.fill();

    // arco
    const ax0 = W * 0.2, ax1 = W * 0.8, ay1 = hz + 4, ay0 = hz - H * 0.17;
    g.fillStyle = 'rgba(255,255,255,.18)'; g.fillRect(ax0, ay0, ax1 - ax0, ay1 - ay0);
    g.strokeStyle = 'rgba(255,255,255,.5)'; g.lineWidth = 1;
    const sacude = resultado === 'gol' ? Math.sin(ahora / 40) * 3 : 0;
    for (let x = ax0; x <= ax1; x += 12) { g.beginPath(); g.moveTo(x + sacude, ay0); g.lineTo(x, ay1); g.stroke(); }
    for (let y = ay0; y <= ay1; y += 10) { g.beginPath(); g.moveTo(ax0, y); g.lineTo(ax1, y + sacude * 0.3); g.stroke(); }
    g.strokeStyle = '#fff'; g.lineWidth = 6; g.lineCap = 'round';
    g.beginPath(); g.moveTo(ax0, ay1); g.lineTo(ax0, ay0); g.lineTo(ax1, ay0); g.lineTo(ax1, ay1); g.stroke();

    const gx = v => W / 2 + v * (ax1 - ax0) / 2;      // -1..1 -> x en el arco
    const gy = h => ay1 - Math.min(1.2, h) * (ay1 - ay0);  // 0..1 -> y en el arco

    // arquero
    const kx = gx(arquero.x), ky = ay1, kh = (ay1 - ay0) * 0.8;
    const inclina = tiro ? Math.sign(arquero.objetivo - 0) * arquero.salto * 0.6 : 0;
    g.save(); g.translate(kx, ky); g.rotate(inclina);
    g.fillStyle = '#f2b400'; g.fillRect(-kh * 0.18, -kh * 0.75, kh * 0.36, kh * 0.45);
    g.fillStyle = '#1f3347'; g.fillRect(-kh * 0.16, -kh * 0.3, kh * 0.12, kh * 0.3); g.fillRect(kh * 0.04, -kh * 0.3, kh * 0.12, kh * 0.3);
    g.strokeStyle = '#f2b400'; g.lineWidth = kh * 0.1;
    const brazo = tiro ? -kh * 0.35 : -kh * 0.15;
    g.beginPath(); g.moveTo(-kh * 0.15, -kh * 0.68); g.lineTo(-kh * 0.42, -kh * 0.68 + brazo); g.moveTo(kh * 0.15, -kh * 0.68); g.lineTo(kh * 0.42, -kh * 0.68 + brazo); g.stroke();
    g.fillStyle = '#2bb673'; [-1, 1].forEach(s => { g.beginPath(); g.arc(s * kh * 0.44, -kh * 0.7 + brazo, kh * 0.08, 0, Math.PI * 2); g.fill(); });
    g.fillStyle = '#ffd9b8'; g.beginPath(); g.arc(0, -kh * 0.88, kh * 0.14, 0, Math.PI * 2); g.fill();
    g.restore();

    // mira (dónde va el tiro: x con el dedo, altura con la fuerza de la voz)
    if (fase === 'apuntando' || fase === 'cargando' || fase === 'validando') {
      const mx = gx(mira), my = gy(Math.max(0.05, potencia));
      g.strokeStyle = potencia > 1 ? '#e53935' : '#fff'; g.lineWidth = 4;
      g.beginPath(); g.arc(mx, my, 14, 0, Math.PI * 2); g.moveTo(mx - 22, my); g.lineTo(mx + 22, my); g.moveTo(mx, my - 22); g.lineTo(mx, my + 22); g.stroke();
      // flecha desde el balón
      g.setLineDash([8, 8]); g.strokeStyle = 'rgba(255,255,255,.7)'; g.lineWidth = 3;
      g.beginPath(); g.moveTo(W / 2, H * 0.8); g.quadraticCurveTo((W / 2 + mx) / 2, my - 30, mx, my); g.stroke(); g.setLineDash([]);
    }

    // balón
    let bx = W / 2, by = H * 0.84, br = Math.min(W, H) * 0.065;
    if (tiro) {
      const t = tiro.t, tx = gx(tiro.x), ty = gy(tiro.altura);
      bx = W / 2 + (tx - W / 2) * t; by = H * 0.84 + (ty - H * 0.84) * t - Math.sin(t * Math.PI) * H * 0.08;
      br *= 1 - t * 0.7;
      if (resultado === 'atajada') { bx = gx(arquero.x); by = ay1 - kh * 0.6; }
    }
    g.fillStyle = 'rgba(0,0,0,.2)'; g.beginPath(); g.ellipse(bx, tiro ? H * 0.84 + (ay1 - H * 0.84) * tiro.t : by + br * 0.9, br, br * 0.3, 0, 0, Math.PI * 2); g.fill();
    g.save(); g.translate(bx, by); g.rotate(tiro ? tiro.t * 12 : 0);
    g.fillStyle = '#fff'; g.strokeStyle = '#1f3347'; g.lineWidth = 2;
    g.beginPath(); g.arc(0, 0, br, 0, Math.PI * 2); g.fill(); g.stroke();
    g.fillStyle = '#1f3347'; g.beginPath();
    for (let i = 0; i < 5; i++) { const a = -Math.PI / 2 + i * 2 * Math.PI / 5; g.lineTo(Math.cos(a) * br * 0.38, Math.sin(a) * br * 0.38); } g.fill();
    g.restore();

    // barra de fuerza (vertical, sin texto)
    const fx = W - 30, fy = H * 0.42, fh = H * 0.4;
    g.fillStyle = '#ffffffcc'; rr(fx - 13, fy - 8, 26, fh + 16, 13); g.fill();
    const grad = g.createLinearGradient(0, fy + fh, 0, fy); grad.addColorStop(0, '#2bb673'); grad.addColorStop(0.8, '#f2b400'); grad.addColorStop(1, '#e53935');
    g.fillStyle = '#e6eef5'; rr(fx - 7, fy, 14, fh, 7); g.fill();
    g.fillStyle = grad; const p = Math.min(1.05, potencia); rr(fx - 7, fy + fh * (1 - p / 1.05), 14, fh * p / 1.05, 7); g.fill();
    g.strokeStyle = '#e53935'; g.lineWidth = 2; g.beginPath(); g.moveTo(fx - 12, fy + fh * (1 - 1 / 1.05)); g.lineTo(fx + 12, fy + fh * (1 - 1 / 1.05)); g.stroke();

    // confeti y textos grandes
    confeti.forEach(c => { g.globalAlpha = Math.max(0, c.vida); g.fillStyle = c.c; g.fillRect(c.x, c.y, 7, 5); }); g.globalAlpha = 1;
    if (resultado === 'gol') grande('GOOOOOL', '#ffd54a', ahora);
    if (resultado === 'atajada') grande('¡Atajada!', '#fff', ahora, 0.6);
    if (resultado === 'fuera') grande('¡Muy alto!', '#fff', ahora, 0.6);
    if (performance.now() < avisoHasta) {
      const I = window.FonoIconos || {};
      g.fillStyle = '#ffffffee'; rr(W / 2 - 120, H * 0.5 - 34, 240, 68, 18); g.fill();
      g.fillStyle = '#e53935'; g.font = '900 30px Inter, system-ui, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
      g.fillText('Di: GOOOOL', W / 2, H * 0.5);
    }
    if (fase === 'cargando') {
      g.fillStyle = '#fff'; g.font = '900 ' + Math.round(26 + potencia * 14) + 'px Inter, system-ui, sans-serif'; g.textAlign = 'center';
      g.fillText('G' + 'O'.repeat(1 + Math.floor(potencia * 7)) + 'L', W / 2, H * 0.62);
    }
  }
  function grande(txt, color, ahora, esc = 1) {
    const s = 1 + Math.sin(ahora / 120) * 0.05;
    g.save(); g.translate(W / 2, H * 0.55); g.scale(s * esc, s * esc);
    g.font = '900 ' + Math.round(Math.min(W, H) * 0.16) + 'px Inter, system-ui, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.lineWidth = 8; g.strokeStyle = '#1f3347'; g.strokeText(txt, 0, 0); g.fillStyle = color; g.fillText(txt, 0, 0);
    g.restore();
  }
  function rr(x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
  function estadoAdulto(t) { const el = $('#gol-estado'); if (el) el.textContent = t; }
  function cerrarAudio() { if (audio) { audio.stream.getTracks().forEach(t => t.stop()); try { audio.ctx.close(); } catch (_) {} audio = null; } }

  async function terminar() {
    if (fase === 'fin' || fase === 'inicio') return;
    fase = 'fin'; detenerReconocimiento(); cerrarAudio();
    $('#gol-parar').hidden = true;
    const est = goles >= 4 ? 3 : goles >= 2 ? 2 : goles >= 1 ? 1 : 0;
    const fin = FonoSoploUI.pantallaFinal(escena, { estrellasGanadas: est, guardando: true, onRepetir: reiniciar });
    const validos = historial.filter(h => h.valido);
    const notas = `¡Haz un gol! nivel ${nivel}: ${goles} goles de ${tiros} tiros. Detección: ${usaPalabra() ? 'reconocimiento de la palabra «gol»' : 'acústica (voz sostenida con O)'}${recErr ? ' (reconocimiento no disponible: ' + recErr + ')' : ''}. ` +
      `Intentos de voz ${historial.length} (válidos ${validos.length}). ` + historial.map((h, i) => `#${i + 1} ${h.valido ? (h.resultado || '') : 'no válido: ' + h.motivo}, voz ${h.duracion}s, fuerza ${h.potencia}`).join('; ') +
      (transcripciones.length ? `. Se escuchó: ${transcripciones.slice(-8).join(' | ')}` : '') + '. Registro para revisión profesional.';
    try {
      if (typeof guardarResultadoJuego === 'function') {
        await guardarResultadoJuego('fonacion', 'gol', goles, cfg.tiros, tiros >= cfg.tiros, Math.round(100 * goles / cfg.tiros), nivel, { notas, requiereRevisionAudio: true, audioTranscripcion: transcripciones.join(' | ') });
      }
      fin.querySelector('.sui-guardado').innerHTML = '<span class="sui-ok">&#10003;</span>';
      estadoAdulto('Actividad guardada.');
    } catch (e) { fin.querySelector('.sui-guardado').innerHTML = ''; estadoAdulto('No se pudo guardar. Revisa la conexión.'); }
  }

  document.addEventListener('DOMContentLoaded', iniciar);
})();
