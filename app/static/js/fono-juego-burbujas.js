/* Burbujas de aire — juego de soplo sostenido.
 * El niño sopla y la película de jabón de la varita se infla. Solo si mantiene
 * el soplo (con fuerza suficiente para su nivel) la burbuja se suelta y sale
 * volando. Mientras sopla, el viento empuja y deforma las burbujas que ya
 * están en el aire. Hablar no cuenta: la burbuja tiembla pero no crece.
 */
(function () {
  'use strict';
  const NIVELES = {
    1: { burbujas: 3, msSoplo: 1200, minimo: 0.12 },
    2: { burbujas: 5, msSoplo: 2000, minimo: 0.20 },
    3: { burbujas: 6, msSoplo: 3000, minimo: 0.30 },
  };
  const $ = s => document.querySelector(s);

  let canvas, g, W = 0, H = 0, dpr = 1, escena, medidorUI, det = null;
  let nivel = 1, cfg = NIVELES[1], fase = 'inicio';
  let progreso = 0, temblor = 0, hechas = 0, burbujas = [], chispas = [], vientos = [], nubes = [];
  let t0 = 0, metricas, ultimoSoplando = false, sostenidoDesde = 0, raf = 0, ultimo = 0;

  function iniciar() {
    escena = $('#soplo-escena');
    canvas = $('#soplo-canvas'); g = canvas.getContext('2d');
    medidorUI = FonoSoploUI.medidor($('#soplo-medidor'));
    const params = new URLSearchParams(location.search);
    nivel = Math.max(1, Math.min(3, parseInt(params.get('nivel') || '1', 10) || 1));
    document.querySelectorAll('[data-nivel]').forEach(b => b.addEventListener('click', () => { if (fase !== 'jugando' && fase !== 'calibrando') elegirNivel(+b.dataset.nivel); }));
    $('#soplo-parar').addEventListener('click', () => terminar(false));
    canvas.addEventListener('pointerdown', tocar);
    window.addEventListener('resize', ajustar);
    for (let i = 0; i < 4; i++) nubes.push({ x: Math.random(), y: 0.08 + Math.random() * 0.25, s: 0.6 + Math.random() * 0.6, v: 0.004 + Math.random() * 0.006 });
    ajustar();
    elegirNivel(nivel);
    ultimo = performance.now();
    raf = requestAnimationFrame(loop);
  }

  function elegirNivel(n) {
    nivel = n; cfg = NIVELES[n];
    document.querySelectorAll('[data-nivel]').forEach(b => b.classList.toggle('activo', +b.dataset.nivel === n));
    reiniciar();
  }

  function reiniciar() {
    det?.detener(); det = null;
    fase = 'inicio'; progreso = 0; hechas = 0; burbujas = []; chispas = [];
    metricas = { msSoplo: 0, maxSostenido: 0, sumaIntensidad: 0, cuadrosSoplo: 0, vecesVoz: 0, reventadas: 0 };
    pintarContador();
    $('#soplo-parar').hidden = true;
    estadoAdulto('Toca el botón verde para empezar.');
    FonoSoploUI.pantallaInicio(escena, { onPlay: empezar });
  }

  async function empezar() {
    fase = 'calibrando';
    estadoAdulto('Pidiendo el micrófono…');
    det = FonoSoplo.crear({ onCuadro: () => {} });
    const ok = await det.iniciar();
    if (!ok) estadoAdulto('No se pudo usar el micrófono. Revisa los permisos (para probar: mantén la barra espaciadora).');
    else estadoAdulto('Silencio un momento… midiendo el ruido del cuarto.');
    FonoSoploUI.pantallaSilencio(escena, 1300);
    await det.calibrar(1300);
    window.FonoEvidencia?.iniciar?.();
    FonoSoploUI.ocultarOverlay(escena);
    $('#soplo-parar').hidden = false;
    fase = 'jugando'; t0 = performance.now();
    estadoAdulto('Que tome aire por la nariz y sople largo y sostenido hacia la varita.');
  }

  function ajustar() {
    dpr = Math.min(2, window.devicePixelRatio || 1);
    const r = canvas.getBoundingClientRect();
    W = r.width; H = r.height;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function aro() { const R = Math.max(26, Math.min(W, H) * 0.12); return { x: W * 0.2, y: H * 0.56, R }; }

  function tocar(e) {
    const r = canvas.getBoundingClientRect(); const x = e.clientX - r.left, y = e.clientY - r.top;
    for (let i = burbujas.length - 1; i >= 0; i--) {
      const b = burbujas[i];
      if (Math.hypot(x - b.x, y - b.y) < b.r * 1.15) { reventar(i); metricas.reventadas++; return; }
    }
  }

  function reventar(i) {
    const b = burbujas[i];
    for (let k = 0; k < 14; k++) { const a = Math.random() * Math.PI * 2, v = 60 + Math.random() * 140; chispas.push({ x: b.x + Math.cos(a) * b.r, y: b.y + Math.sin(a) * b.r, vx: Math.cos(a) * v, vy: Math.sin(a) * v, vida: 1 }); }
    burbujas.splice(i, 1);
    FonoSoploUI.sonido('pop');
  }

  function soltarBurbuja() {
    const a = aro();
    const r = a.R * 1.45;
    burbujas.push({ x: a.x + a.R * 1.1, y: a.y, r, vx: 80, vy: -20, fase: Math.random() * 6, hue: Math.random() * 360, nace: performance.now() });
    hechas++; progreso = 0; pintarContador();
    FonoSoploUI.sonido('burbuja');
    if (hechas >= cfg.burbujas) setTimeout(() => terminar(true), 900);
  }

  function pintarContador() {
    const c = $('#soplo-contador'); let h = '';
    for (let i = 0; i < cfg.burbujas; i++) h += `<span class="burbuja-ficha ${i < hechas ? 'llena' : ''}"></span>`;
    c.innerHTML = h;
  }

  function loop(ahora) {
    const dt = Math.min(0.05, (ahora - ultimo) / 1000); ultimo = ahora;
    const st = det?.estado || { intensidad: 0, soplando: false, voz: false };
    const jugando = fase === 'jugando';
    const I = jugando ? st.intensidad : 0;
    const valido = jugando && st.soplando && I >= cfg.minimo;

    if (jugando) {
      medidorUI.pintar(I, cfg.minimo, st.voz);
      if (st.voz && !ultimoSoplando) { temblor = 1; }
      if (st.voz) metricas._voz = (metricas._voz || 0) + 1; else if (metricas._voz) { metricas.vecesVoz++; metricas._voz = 0; }
      if (st.soplando) { metricas.msSoplo += dt * 1000; metricas.sumaIntensidad += I; metricas.cuadrosSoplo++; }
      if (valido && hechas < cfg.burbujas) {
        if (!sostenidoDesde) sostenidoDesde = ahora;
        metricas.maxSostenido = Math.max(metricas.maxSostenido, ahora - sostenidoDesde);
        progreso += (dt * 1000) / cfg.msSoplo * (0.75 + I * 0.5);
        if (progreso >= 1) soltarBurbuja();
      } else {
        sostenidoDesde = 0;
        // si deja de soplar la película se desinfla poco a poco (no se pierde de golpe)
        progreso = Math.max(0, progreso - dt * 0.35);
        if (st.soplando && I < cfg.minimo) temblor = Math.max(temblor, 0.4);
      }
      ultimoSoplando = st.soplando;
    } else medidorUI.pintar(0, cfg.minimo, false);

    temblor = Math.max(0, temblor - dt * 1.5);
    // Viento visible
    if (I > 0.05 && Math.random() < I * 0.9) vientos.push({ x: aro().x - 40, y: aro().y + (Math.random() - 0.5) * aro().R * 3, l: 30 + Math.random() * 60, v: 300 + I * 500, vida: 1 });
    vientos.forEach(v => { v.x += v.v * dt; v.vida -= dt * 0.9; });
    vientos = vientos.filter(v => v.vida > 0 && v.x < W + 80);

    // Física de burbujas libres: flotan, el soplo las empuja y deforma
    burbujas.forEach(b => {
      b.fase += dt * 3;
      b.vx += (I * 260 - b.vx * 0.6) * dt;
      b.vy += (-18 - b.vy * 0.5 + Math.sin(b.fase) * 30) * dt;
      b.x += b.vx * dt; b.y += b.vy * dt;
      b.empuje = I;
      if (b.y < b.r) { b.y = b.r; b.vy = Math.abs(b.vy) * 0.3; }
    });
    for (let i = burbujas.length - 1; i >= 0; i--) {
      const b = burbujas[i];
      if (b.x - b.r > W || performance.now() - b.nace > 14000) burbujas.splice(i, 1);
    }
    chispas.forEach(c => { c.x += c.vx * dt; c.y += c.vy * dt; c.vy += 200 * dt; c.vida -= dt * 2; });
    chispas = chispas.filter(c => c.vida > 0);
    nubes.forEach(n => { n.x += (n.v + I * 0.05) * dt; if (n.x > 1.2) n.x = -0.2; });

    dibujar(I, valido, ahora);
    raf = requestAnimationFrame(loop);
  }

  function dibujar(I, valido, ahora) {
    // Cielo
    const cielo = g.createLinearGradient(0, 0, 0, H);
    cielo.addColorStop(0, '#8fd3ff'); cielo.addColorStop(0.7, '#dff4ff'); cielo.addColorStop(1, '#eafbe6');
    g.fillStyle = cielo; g.fillRect(0, 0, W, H);
    // Sol
    g.fillStyle = '#ffe27a'; g.beginPath(); g.arc(W * 0.86, H * 0.16, Math.min(W, H) * 0.07, 0, Math.PI * 2); g.fill();
    g.fillStyle = 'rgba(255,226,122,.35)'; g.beginPath(); g.arc(W * 0.86, H * 0.16, Math.min(W, H) * 0.11, 0, Math.PI * 2); g.fill();
    nubes.forEach(n => nube(n.x * W, n.y * H, n.s * Math.min(W, H) * 0.09));
    // Pasto
    g.fillStyle = '#9edb8a'; g.beginPath(); g.moveTo(0, H * 0.86);
    for (let x = 0; x <= W; x += 20) g.lineTo(x, H * 0.86 + Math.sin(x * 0.05) * 4);
    g.lineTo(W, H); g.lineTo(0, H); g.fill();
    g.strokeStyle = '#7cc56a'; g.lineWidth = 2;
    for (let x = 6; x < W; x += 14) { const s = Math.sin(ahora / 400 + x) * 2 + I * 8; g.beginPath(); g.moveTo(x, H * 0.9); g.quadraticCurveTo(x + s, H * 0.86, x + s * 1.5, H * 0.83); g.stroke(); }

    // Viento
    g.lineCap = 'round';
    vientos.forEach(v => { g.strokeStyle = `rgba(255,255,255,${0.7 * v.vida})`; g.lineWidth = 3; g.beginPath(); g.moveTo(v.x, v.y); g.quadraticCurveTo(v.x + v.l / 2, v.y - 6, v.x + v.l, v.y); g.stroke(); });

    // Varita
    const a = aro();
    g.strokeStyle = '#ff8a3d'; g.lineWidth = Math.max(6, a.R * 0.18);
    g.beginPath(); g.moveTo(a.x - a.R * 0.3, a.y + a.R); g.lineTo(a.x - a.R * 1.1, H * 0.98); g.stroke();
    // Burbuja que se infla dentro del aro
    const tiembla = temblor * Math.sin(ahora / 30) * 4;
    if (fase === 'jugando' || progreso > 0) {
      const p = progreso;
      const rx = a.R * (0.95 + p * 0.6), ry = a.R * (0.95 + p * 0.45);
      const cx = a.x + p * (a.R * 1.1) + tiembla, cy = a.y;
      burbujaFigura(cx, cy, rx + Math.sin(ahora / 120) * p * 3, ry, (ahora / 20) % 360, 0.35 + p * 0.4);
    }
    // Aro
    g.strokeStyle = valido ? '#ff5fa2' : '#ff7eb6'; g.lineWidth = Math.max(5, a.R * 0.14);
    g.beginPath(); g.ellipse(a.x, a.y, a.R * 0.55, a.R, 0, 0, Math.PI * 2); g.stroke();
    // Anillo de progreso alrededor del aro (sin texto)
    if (fase === 'jugando') {
      g.strokeStyle = 'rgba(255,255,255,.7)'; g.lineWidth = 8;
      g.beginPath(); g.arc(a.x, a.y, a.R * 1.35, 0, Math.PI * 2); g.stroke();
      g.strokeStyle = '#2bb673';
      g.beginPath(); g.arc(a.x, a.y, a.R * 1.35, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * Math.min(1, progreso)); g.stroke();
    }

    // Burbujas libres
    burbujas.forEach(b => {
      const squash = 1 + (b.empuje || 0) * 0.22 + Math.sin(b.fase * 2) * 0.03;
      burbujaFigura(b.x, b.y, b.r * squash, b.r / squash, (b.hue + ahora / 15) % 360, 0.8);
    });
    chispas.forEach(c => { g.fillStyle = `rgba(160,220,255,${c.vida})`; g.beginPath(); g.arc(c.x, c.y, 3 + 3 * c.vida, 0, Math.PI * 2); g.fill(); });
  }

  function burbujaFigura(x, y, rx, ry, hue, alfa) {
    g.save();
    const grad = g.createRadialGradient(x - rx * 0.35, y - ry * 0.35, rx * 0.1, x, y, Math.max(rx, ry));
    grad.addColorStop(0, `rgba(255,255,255,${0.15 * alfa})`);
    grad.addColorStop(0.75, `hsla(${hue},90%,80%,${0.18 * alfa})`);
    grad.addColorStop(0.92, `hsla(${(hue + 60) % 360},90%,70%,${0.55 * alfa})`);
    grad.addColorStop(1, `hsla(${(hue + 120) % 360},90%,65%,${0.75 * alfa})`);
    g.fillStyle = grad;
    g.beginPath(); g.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2); g.fill();
    g.strokeStyle = `rgba(255,255,255,${0.8 * alfa})`; g.lineWidth = 2; g.stroke();
    g.fillStyle = `rgba(255,255,255,${0.85 * alfa})`;
    g.beginPath(); g.ellipse(x - rx * 0.4, y - ry * 0.45, rx * 0.16, ry * 0.09, -0.6, 0, Math.PI * 2); g.fill();
    g.restore();
  }

  function nube(x, y, s) {
    g.fillStyle = 'rgba(255,255,255,.9)';
    [[0, 0, 1], [0.9, 0.1, 0.8], [-0.9, 0.15, 0.75], [0.35, -0.45, 0.8]].forEach(([dx, dy, r]) => { g.beginPath(); g.arc(x + dx * s, y + dy * s, r * s, 0, Math.PI * 2); g.fill(); });
  }

  function estadoAdulto(t) { const el = $('#soplo-estado'); if (el) el.textContent = t; }

  async function terminar(completo) {
    if (fase !== 'jugando' && fase !== 'calibrando') return;
    fase = 'fin';
    det?.detener(); det = null;
    $('#soplo-parar').hidden = true;
    const total = cfg.burbujas;
    const est = completo ? 3 : hechas === 0 ? 0 : Math.max(1, Math.round(3 * hechas / total));
    const fin = FonoSoploUI.pantallaFinal(escena, { estrellasGanadas: est, guardando: true, onRepetir: reiniciar });
    if (completo) FonoSoploUI.sonido('meta');
    const prom = metricas.cuadrosSoplo ? metricas.sumaIntensidad / metricas.cuadrosSoplo : 0;
    const notas = `Burbujas nivel ${nivel}: ${hechas}/${total} burbujas. Soplo meta por burbuja ${cfg.msSoplo} ms (intensidad mín. ${cfg.minimo}). ` +
      `Tiempo total soplando ${(metricas.msSoplo / 1000).toFixed(1)} s; soplo sostenido más largo ${(metricas.maxSostenido / 1000).toFixed(1)} s; ` +
      `intensidad media ${prom.toFixed(2)}; veces que habló en vez de soplar ${metricas.vecesVoz}; burbujas reventadas con el dedo ${metricas.reventadas}. ` +
      `Registro para revisión profesional; no es calificación clínica.`;
    try {
      if (typeof guardarResultadoJuego === 'function') {
        await guardarResultadoJuego('respiracion', 'burbujas', Math.min(hechas, total), total, hechas >= total, Math.round(100 * Math.min(hechas, total) / total), nivel, { notas, requiereRevisionAudio: true });
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
