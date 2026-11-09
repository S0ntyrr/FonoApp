/* El molino de Pepe — soplo con tres modos.
 * - MISIONES: hacer X vueltas antes de que se acabe el tiempo (3 misiones por nivel).
 * - LIBRE: soplar y ver cuántas vueltas se logran, sin tiempo.
 * - MEDIR: 3 intentos guiados «Respira → Sopla todo el aire»; mide la fuerza
 *   máxima del soplo y cuántos segundos dura (capacidad). Guarda el mejor.
 * Siempre se ve la tira RESPIRA → SOPLA → RESPIRA con la fase actual iluminada.
 */
(function () {
  'use strict';
  const MISIONES = {
    1: [{ vueltas: 4, seg: 25 }, { vueltas: 6, seg: 25 }, { vueltas: 8, seg: 30 }],
    2: [{ vueltas: 6, seg: 20 }, { vueltas: 9, seg: 25 }, { vueltas: 12, seg: 30 }],
    3: [{ vueltas: 8, seg: 18 }, { vueltas: 12, seg: 22 }, { vueltas: 16, seg: 26 }],
  };
  const MINIMO = { 1: 0.14, 2: 0.2, 3: 0.26 };
  const INTENTOS_MEDIR = 3;
  const $ = s => document.querySelector(s);

  let canvas, g, W = 0, H = 0, escena, medidorUI, det = null, hud = null;
  let nivel = 1, modo = '', fase = 'inicio';
  let angulo = 0, omega = 0, vueltas = 0, misionIdx = 0, misionInicio = 0, misionesOk = 0;
  let medir = null, metricas, ultimo = 0, t0 = 0, viento = [];

  function iniciar() {
    escena = $('#soplo-escena');
    canvas = $('#soplo-canvas'); g = canvas.getContext('2d');
    medidorUI = FonoSoploUI.medidor($('#soplo-medidor'));
    nivel = Math.max(1, Math.min(3, parseInt(new URLSearchParams(location.search).get('nivel') || '1', 10) || 1));
    document.querySelectorAll('[data-nivel]').forEach(b => b.addEventListener('click', () => { if (fase === 'inicio') elegirNivel(+b.dataset.nivel); }));
    $('#soplo-parar').addEventListener('click', () => terminar());
    window.addEventListener('resize', ajustar);
    crearHud(); ajustar(); elegirNivel(nivel);
    ultimo = performance.now(); requestAnimationFrame(loop);
  }

  function elegirNivel(n) {
    nivel = n;
    document.querySelectorAll('[data-nivel]').forEach(b => b.classList.toggle('activo', +b.dataset.nivel === n));
    elegirModo();
  }

  // ── HUD (DOM): tira de respiración, tiempo y vueltas ──
  function crearHud() {
    hud = document.createElement('div');
    hud.className = 'mol-hud';
    const ICO = FonoSoploUI.icons;
    hud.innerHTML = `
      <div class="mol-ciclo" aria-label="Respira, sopla, respira">
        <span class="mol-fase" data-f="in1">${ICO.INSPIRA}<b>Respira</b></span><i>›</i>
        <span class="mol-fase" data-f="out">${ICO.SOPLA}<b>Sopla</b></span><i>›</i>
        <span class="mol-fase" data-f="in2">${ICO.INSPIRA}<b>Respira</b></span>
      </div>
      <div class="mol-marcador">
        <div class="mol-vueltas" aria-live="polite"><svg viewBox="0 0 64 64" aria-hidden="true">${(window.FonoIconos || {}).molino || ''}</svg><strong id="mol-v">0</strong><small id="mol-meta"></small></div>
        <div class="mol-reloj" id="mol-reloj" hidden><svg viewBox="0 0 40 40"><circle cx="20" cy="20" r="16" fill="#fff" stroke="#e3e9f0" stroke-width="6"/><circle id="mol-reloj-arco" cx="20" cy="20" r="16" fill="none" stroke="#2e9fd6" stroke-width="6" stroke-linecap="round" pathLength="100" stroke-dasharray="100 100" transform="rotate(-90 20 20)"/></svg><strong id="mol-s">0</strong></div>
        <div class="mol-estrellas" id="mol-estrellas"></div>
      </div>`;
    escena.appendChild(hud);
  }
  function faseCiclo(f) { hud.querySelectorAll('.mol-fase').forEach(e => e.classList.toggle('activa', e.dataset.f === f || (f === 'in' && e.dataset.f === 'in1'))); }

  // ── Elegir modo (pantalla sin texto obligatorio: dibujos grandes) ──
  function elegirModo() {
    det?.detener(); det = null; fase = 'inicio'; modo = '';
    $('#soplo-parar').hidden = true; hud.hidden = true;
    const I = window.FonoIconos || {};
    const ov = overlay(`
      <div class="mol-modos">
        <button type="button" data-modo="misiones"><svg viewBox="0 0 64 64">${I.diana || ''}</svg><b>Misiones</b><small>Vueltas antes del tiempo</small></button>
        <button type="button" data-modo="libre"><svg viewBox="0 0 64 64">${I.molino || ''}</svg><b>Libre</b><small>Sopla sin prisa</small></button>
        <button type="button" data-modo="medir"><svg viewBox="0 0 64 64">${I.grafica || ''}</svg><b>Medir</b><small>Fuerza y aire</small></button>
      </div>`);
    ov.querySelectorAll('[data-modo]').forEach(b => b.addEventListener('click', () => empezar(b.dataset.modo), { once: true }));
    estadoAdulto('Elige un modo. Misiones: retos de vueltas con tiempo. Libre: practicar. Medir: 3 soplos largos para ver la fuerza y cuánto aire tiene.');
  }

  function overlay(html) {
    let el = escena.querySelector('.sui-overlay');
    if (!el) { el = document.createElement('div'); escena.appendChild(el); }
    el.className = 'sui-overlay'; el.innerHTML = html; el.hidden = false;
    return el;
  }

  async function empezar(m) {
    modo = m; fase = 'calibrando';
    metricas = { msSoplo: 0, maxSostenido: 0, picoI: 0, sumaI: 0, cuadros: 0, vecesVoz: 0, _voz: 0, sostDesde: 0 };
    vueltas = 0; angulo = 0; omega = 0; misionIdx = 0; misionesOk = 0;
    det = FonoSoplo.crear({ config: { minDbSobreRuido: 10 } });
    const ok = await det.iniciar();
    estadoAdulto(ok ? 'Silencio un momento… midiendo el ruido del cuarto.' : 'No se pudo usar el micrófono (para probar: barra espaciadora = soplar).');
    FonoSoploUI.pantallaSilencio(escena, 1300);
    await det.calibrar(1300);
    window.FonoEvidencia?.iniciar?.();
    FonoSoploUI.ocultarOverlay(escena);
    hud.hidden = false; $('#soplo-parar').hidden = false;
    fase = 'jugando'; t0 = performance.now();
    $('#mol-reloj').hidden = modo !== 'misiones';
    pintarEstrellas();
    if (modo === 'misiones') iniciarMision();
    if (modo === 'libre') { $('#mol-meta').textContent = ''; estadoAdulto('Modo libre: respirar por la nariz y soplar al molino. Mientras más fuerte y largo, más vueltas.'); }
    if (modo === 'medir') iniciarMedicion();
  }

  // ── Misiones ──
  function iniciarMision() {
    const m = MISIONES[nivel][misionIdx];
    vueltas = 0; misionInicio = performance.now();
    $('#mol-meta').textContent = '/' + m.vueltas;
    estadoAdulto(`Misión ${misionIdx + 1} de 3: ${m.vueltas} vueltas en ${m.seg} segundos. Puede respirar las veces que necesite.`);
  }
  function revisarMision(ahora) {
    const m = MISIONES[nivel][misionIdx];
    const resta = Math.max(0, m.seg - (ahora - misionInicio) / 1000);
    $('#mol-s').textContent = Math.ceil(resta);
    $('#mol-reloj-arco').setAttribute('stroke-dasharray', `${(resta / m.seg) * 100} 100`);
    if (vueltas >= m.vueltas) { misionesOk++; FonoSoploUI.sonido('meta'); siguienteMision(true); }
    else if (resta <= 0) { FonoSoploUI.sonido('golpe'); siguienteMision(false); }
  }
  function siguienteMision(ok) {
    pintarEstrellas(ok);
    misionIdx++;
    if (misionIdx >= MISIONES[nivel].length) return terminar();
    fase = 'pausa';
    const ov = overlay(`<div class="mol-mensaje">${FonoSoploUI.estrellas(misionesOk, MISIONES[nivel].length)}<button type="button" class="sui-boton-grande" aria-label="Siguiente misión">${FonoSoploUI.icons.PLAY}</button></div>`);
    ov.querySelector('button').addEventListener('click', () => { FonoSoploUI.ocultarOverlay(escena); fase = 'jugando'; iniciarMision(); }, { once: true });
  }
  function pintarEstrellas() {
    const el = $('#mol-estrellas');
    if (modo !== 'misiones') { el.innerHTML = ''; return; }
    el.innerHTML = FonoSoploUI.estrellas(misionesOk, MISIONES[nivel].length);
  }

  // ── Medir fuerza y capacidad ──
  function iniciarMedicion() {
    medir = { intento: 0, etapa: 'respira', desde: performance.now(), resultados: [], pico: 0, inicioSoplo: 0, finSoplo: 0, vueltasIni: 0 };
    $('#mol-meta').textContent = '';
    estadoAdulto('Medir: 3 intentos. Primero respirar por la nariz (3 s), luego soplar TODO el aire de una vez, lo más largo posible.');
  }
  function revisarMedicion(ahora, st, I) {
    const m = medir;
    if (m.etapa === 'respira') {
      const resta = 3 - (ahora - m.desde) / 1000;
      faseCiclo('in1');
      $('#mol-reloj').hidden = false;
      $('#mol-s').textContent = Math.max(1, Math.ceil(resta));
      $('#mol-reloj-arco').setAttribute('stroke-dasharray', `${Math.max(0, resta / 3) * 100} 100`);
      $('#mol-meta').textContent = ' · ' + (m.intento + 1) + '/' + INTENTOS_MEDIR;
      if (resta <= 0) { m.etapa = 'sopla'; m.desde = ahora; m.pico = 0; m.inicioSoplo = 0; m.finSoplo = 0; m.vueltasIni = vueltas; FonoSoploUI.sonido('burbuja'); }
      return;
    }
    if (m.etapa === 'sopla') {
      faseCiclo('out');
      const sopla = m.inicioSoplo ? ((m.finSoplo || ahora) - m.inicioSoplo) / 1000 : 0;
      $('#mol-s').textContent = sopla.toFixed(1);
      $('#mol-reloj-arco').setAttribute('stroke-dasharray', `${Math.min(100, sopla / 12 * 100)} 100`);
      if (st.soplando) {
        if (!m.inicioSoplo) m.inicioSoplo = ahora;
        m.finSoplo = ahora; m.pico = Math.max(m.pico, I);
      }
      const silencio = m.inicioSoplo && !st.soplando && ahora - m.finSoplo > 700;
      const sinEmpezar = !m.inicioSoplo && ahora - m.desde > 6000;
      if (silencio || sinEmpezar || ahora - m.desde > 25000) {
        const seg = m.inicioSoplo ? (m.finSoplo - m.inicioSoplo) / 1000 : 0;
        m.resultados.push({ fuerza: Math.round(m.pico * 100), segundos: +seg.toFixed(1), vueltas: +(vueltas - m.vueltasIni).toFixed(1) });
        m.intento++;
        if (m.intento >= INTENTOS_MEDIR) return mostrarMedicion();
        m.etapa = 'respira'; m.desde = ahora;
      }
    }
  }
  function mostrarMedicion() {
    const r = medir.resultados;
    const mejorF = Math.max(...r.map(x => x.fuerza)), mejorS = Math.max(...r.map(x => x.segundos));
    medir.mejor = { fuerza: mejorF, segundos: mejorS };
    fase = 'fin';
    det?.detener(); det = null; $('#soplo-parar').hidden = true;
    const barra = (v, max, color) => `<div class="mol-barra"><i style="width:${Math.min(100, (v / max) * 100)}%;background:${color}"></i></div>`;
    const I = window.FonoIconos || {};
    const fin = overlay(`
      <div class="mol-medida">
        <div class="mol-medida-fila"><svg viewBox="0 0 64 64">${I.soplar || ''}</svg><div><b>Fuerza</b>${barra(mejorF, 100, '#f57c00')}</div><strong>${mejorF}</strong></div>
        <div class="mol-medida-fila"><svg viewBox="0 0 64 64">${I.reloj || ''}</svg><div><b>Aire (segundos)</b>${barra(mejorS, 12, '#2e9fd6')}</div><strong>${mejorS}s</strong></div>
        <div class="sui-guardado" aria-live="polite"><span class="sui-spinner"></span></div>
        <button type="button" class="sui-boton-grande" aria-label="Volver a elegir modo">${FonoSoploUI.icons.REPETIR}</button>
      </div>`);
    fin.querySelector('button').addEventListener('click', elegirModo, { once: true });
    guardar(fin, true);
  }

  function ajustar() {
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const r = canvas.getBoundingClientRect(); W = r.width; H = r.height;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function loop(ahora) {
    const dt = Math.min(0.05, (ahora - ultimo) / 1000); ultimo = ahora;
    const st = det?.estado || { intensidad: 0, soplando: false, voz: false };
    const jugando = fase === 'jugando';
    const I = jugando ? st.intensidad : 0;
    const empuja = jugando && st.soplando && I >= MINIMO[nivel];
    if (jugando) {
      medidorUI.pintar(I, MINIMO[nivel], st.voz);
      if (st.voz) metricas._voz++; else if (metricas._voz) { metricas.vecesVoz++; metricas._voz = 0; }
      if (st.soplando) { metricas.msSoplo += dt * 1000; metricas.sumaI += I; metricas.cuadros++; metricas.picoI = Math.max(metricas.picoI, I); }
      if (empuja) { if (!metricas.sostDesde) metricas.sostDesde = ahora; metricas.maxSostenido = Math.max(metricas.maxSostenido, ahora - metricas.sostDesde); } else metricas.sostDesde = 0;
      if (modo !== 'medir') faseCiclo(empuja ? 'out' : 'in');
    } else medidorUI.pintar(0, MINIMO[nivel], false);

    // Física: el soplo acelera; el roce frena
    const objetivo = empuja ? (2 + I * 10) : 0;      // rad/s
    omega += (objetivo - omega) * Math.min(1, dt * (empuja ? 2.5 : 0.8));
    angulo += omega * dt;
    if (jugando) vueltas += omega * dt / (Math.PI * 2);
    if (jugando) $('#mol-v').textContent = Math.floor(vueltas);
    if (jugando && modo === 'misiones') revisarMision(ahora);
    if (jugando && modo === 'medir') revisarMedicion(ahora, st, I);

    if (empuja && Math.random() < I) viento.push({ x: W * 0.12, y: H * (0.25 + Math.random() * 0.3), v: 250 + I * 400, l: 30 + Math.random() * 40, vida: 1 });
    viento.forEach(v => { v.x += v.v * dt; v.vida -= dt * 1.2; }); viento = viento.filter(v => v.vida > 0);
    dibujar(ahora);
    requestAnimationFrame(loop);
  }

  function dibujar(ahora) {
    const cielo = g.createLinearGradient(0, 0, 0, H);
    cielo.addColorStop(0, '#9fd8ff'); cielo.addColorStop(1, '#e6f7ff');
    g.fillStyle = cielo; g.fillRect(0, 0, W, H);
    // colinas
    g.fillStyle = '#a8dca0'; g.beginPath(); g.moveTo(0, H * 0.78); g.quadraticCurveTo(W * 0.3, H * 0.66, W * 0.6, H * 0.76); g.quadraticCurveTo(W * 0.85, H * 0.82, W, H * 0.72); g.lineTo(W, H); g.lineTo(0, H); g.fill();
    g.fillStyle = '#8fcf86'; g.fillRect(0, H * 0.86, W, H * 0.14);
    // viento
    g.strokeStyle = 'rgba(255,255,255,.85)'; g.lineWidth = 3; g.lineCap = 'round';
    viento.forEach(v => { g.globalAlpha = v.vida; g.beginPath(); g.moveTo(v.x, v.y); g.quadraticCurveTo(v.x + v.l / 2, v.y - 5, v.x + v.l, v.y); g.stroke(); });
    g.globalAlpha = 1;
    // molino
    const mx = W * 0.6, base = H * 0.86, alto = H * 0.42, cy = base - alto;
    g.fillStyle = '#e8d3b0'; g.beginPath(); g.moveTo(mx - W * 0.09, base); g.lineTo(mx - W * 0.05, cy); g.lineTo(mx + W * 0.05, cy); g.lineTo(mx + W * 0.09, base); g.closePath(); g.fill();
    g.fillStyle = '#c0392b'; g.beginPath(); g.moveTo(mx - W * 0.07, cy + 4); g.lineTo(mx, cy - H * 0.07); g.lineTo(mx + W * 0.07, cy + 4); g.closePath(); g.fill();
    g.fillStyle = '#8a5a35'; g.fillRect(mx - 10, base - H * 0.09, 20, H * 0.09);
    const L = Math.min(W, H) * 0.3;
    g.save(); g.translate(mx, cy); g.rotate(angulo);
    for (let i = 0; i < 4; i++) {
      g.rotate(Math.PI / 2);
      g.fillStyle = '#fff8e8'; g.strokeStyle = '#a5621c'; g.lineWidth = 2;
      g.fillRect(-3, 0, 6, L);
      g.beginPath(); g.rect(3, L * 0.25, L * 0.24, L * 0.72); g.fill(); g.stroke();
      g.strokeStyle = '#d9b98a'; g.beginPath(); for (let k = 1; k < 4; k++) { g.moveTo(3, L * (0.25 + k * 0.18)); g.lineTo(3 + L * 0.24, L * (0.25 + k * 0.18)); } g.stroke();
    }
    g.restore();
    g.fillStyle = '#6d4c2e'; g.beginPath(); g.arc(mx, cy, 8, 0, Math.PI * 2); g.fill();
    // Pepe soplando a la izquierda
    const px = W * 0.15, py = H * 0.62, R = Math.min(W, H) * 0.09;
    g.fillStyle = '#ffd9b8'; g.strokeStyle = '#e8a77a'; g.lineWidth = 3;
    g.beginPath(); g.arc(px, py, R, 0, Math.PI * 2); g.fill(); g.stroke();
    g.fillStyle = '#f2b400'; g.beginPath(); g.ellipse(px, py - R * 0.7, R * 1.1, R * 0.35, 0, 0, Math.PI * 2); g.fill();
    g.fillRect(px - R * 0.6, py - R * 1.35, R * 1.2, R * 0.65);
    g.fillStyle = '#1f3347'; g.beginPath(); g.arc(px - R * 0.3, py - R * 0.05, R * 0.1, 0, Math.PI * 2); g.arc(px + R * 0.3, py - R * 0.05, R * 0.1, 0, Math.PI * 2); g.fill();
    g.fillStyle = '#b5523b'; g.beginPath(); g.ellipse(px + R * 0.45, py + R * 0.4, R * 0.13, R * 0.13, 0, 0, Math.PI * 2); g.fill();
    g.fillStyle = '#2e86de'; g.fillRect(px - R * 0.7, py + R * 0.95, R * 1.4, R * 1.3);
  }

  function estadoAdulto(t) { const el = $('#soplo-estado'); if (el) el.textContent = t; }

  function terminar() {
    if (fase === 'fin' || fase === 'inicio') return;
    if (modo === 'medir' && medir && medir.resultados.length) return mostrarMedicion();
    fase = 'fin';
    det?.detener(); det = null; $('#soplo-parar').hidden = true;
    const total = MISIONES[nivel].length;
    const est = modo === 'misiones' ? misionesOk : Math.min(3, Math.floor(vueltas / 5));
    const fin = FonoSoploUI.pantallaFinal(escena, { estrellasGanadas: est, guardando: true, onRepetir: elegirModo });
    if (est >= 3) FonoSoploUI.sonido('meta');
    guardar(fin, modo === 'misiones' ? misionesOk === total : vueltas >= 5);
  }

  async function guardar(fin, completo) {
    const seg = ((performance.now() - t0) / 1000).toFixed(1);
    const prom = metricas.cuadros ? metricas.sumaI / metricas.cuadros : 0;
    let det_modo = '';
    if (modo === 'misiones') det_modo = `Misiones nivel ${nivel}: ${misionesOk}/${MISIONES[nivel].length} cumplidas (${MISIONES[nivel].map(m => m.vueltas + ' vueltas/' + m.seg + 's').join(', ')}).`;
    if (modo === 'libre') det_modo = `Modo libre: ${Math.floor(vueltas)} vueltas en ${seg} s.`;
    if (modo === 'medir') det_modo = `Medición de soplo (${INTENTOS_MEDIR} intentos): ` + medir.resultados.map((r, i) => `#${i + 1} fuerza ${r.fuerza}/100, duración ${r.segundos} s`).join('; ') + `. Mejor fuerza ${medir.mejor.fuerza}/100; mejor duración ${medir.mejor.segundos} s.`;
    const notas = `Molino de Pepe. ${det_modo} Tiempo total soplando ${(metricas.msSoplo / 1000).toFixed(1)} s; soplo sostenido más largo ${(metricas.maxSostenido / 1000).toFixed(1)} s; ` +
      `intensidad media ${prom.toFixed(2)}, pico ${metricas.picoI.toFixed(2)}; veces que habló en vez de soplar ${metricas.vecesVoz}. Registro para revisión profesional; no es calificación clínica.`;
    const pasos = modo === 'misiones' ? misionesOk : modo === 'medir' ? medir.resultados.length : Math.min(10, Math.floor(vueltas));
    const total = modo === 'misiones' ? MISIONES[nivel].length : modo === 'medir' ? INTENTOS_MEDIR : 10;
    try {
      if (typeof guardarResultadoJuego === 'function') {
        await guardarResultadoJuego('respiracion', 'molino', pasos, total, !!completo, Math.round(100 * pasos / total), nivel, { notas, requiereRevisionAudio: true });
      }
      fin.querySelector('.sui-guardado').innerHTML = '<span class="sui-ok">&#10003;</span>';
      estadoAdulto('Actividad guardada.');
    } catch (e) {
      fin.querySelector('.sui-guardado').innerHTML = '';
      estadoAdulto('No se pudo guardar. Revisa la conexión y vuelve a jugar.');
    }
  }

  document.addEventListener('DOMContentLoaded', iniciar);
})();
