/* Infla el globo — soplo sostenido y con esfuerzo.
 * - Solo cuenta el SOPLO (FonoSoplo distingue aire de voz y calibra el ruido).
 * - El globo crece solo si el soplo supera la fuerza mínima del nivel; con un
 *   soplo flojo apenas se mueve. Si el niño deja de soplar se desinfla despacio
 *   y aparece la carita «toma aire» para que respire y siga.
 * - Al llenarse explota con confeti.
 */
(function () {
  'use strict';
  // msSoplo: tiempo de soplo fuerte necesario; minimo: fuerza mínima (0..1)
  const NIVELES = {
    1: { msSoplo: 5000, minimo: 0.22 },
    2: { msSoplo: 7500, minimo: 0.30 },
    3: { msSoplo: 10000, minimo: 0.38 },
  };
  const DETECTOR = { minDbSobreRuido: 12, msActivar: 180 };   // más exigente que burbujas
  const $ = s => document.querySelector(s);
  const COLORES = ['#e53935', '#2e86de', '#8e44ad', '#2bb673', '#f57c00', '#e84393'];

  let canvas, g, W = 0, H = 0, escena, medidorUI, det = null;
  let nivel = 1, cfg = NIVELES[1], fase = 'inicio';
  let progreso = 0, quietoDesde = 0, aire = [], confeti = [], color = COLORES[0], pop = 0;
  let metricas, sostenidoDesde = 0, ultimo = 0, t0 = 0, respiraciones = 0, soplandoAntes = false;

  function iniciar() {
    escena = $('#soplo-escena');
    canvas = $('#soplo-canvas'); g = canvas.getContext('2d');
    medidorUI = FonoSoploUI.medidor($('#soplo-medidor'));
    nivel = Math.max(1, Math.min(3, parseInt(new URLSearchParams(location.search).get('nivel') || '1', 10) || 1));
    document.querySelectorAll('[data-nivel]').forEach(b => b.addEventListener('click', () => { if (fase !== 'jugando' && fase !== 'calibrando') elegirNivel(+b.dataset.nivel); }));
    $('#soplo-parar').addEventListener('click', () => terminar(false));
    window.addEventListener('resize', ajustar);
    ajustar(); elegirNivel(nivel);
    ultimo = performance.now(); requestAnimationFrame(loop);
  }

  function elegirNivel(n) {
    nivel = n; cfg = NIVELES[n];
    document.querySelectorAll('[data-nivel]').forEach(b => b.classList.toggle('activo', +b.dataset.nivel === n));
    reiniciar();
  }

  const DEMO = `<div class="demo-globo" aria-hidden="true"><svg viewBox="0 0 120 120">
      <g class="dg-globo"><path d="M80 12c16 0 26 12 26 27 0 17-14 29-26 30-12-1-26-13-26-30 0-15 10-27 26-27z" fill="#e53935"/>
      <ellipse cx="70" cy="28" rx="5" ry="9" fill="#fff" opacity=".45" transform="rotate(-20 70 28)"/></g>
      <path d="M77 69h6l-3 6z" fill="#b71c1c"/>
      <circle cx="34" cy="86" r="24" fill="#ffd9b8" stroke="#e8a77a" stroke-width="2"/>
      <path d="M12 80q4-22 22-22t22 22q-8-10-22-10t-22 10z" fill="#6b3f1f"/>
      <circle cx="27" cy="84" r="2.6" fill="#1f3347"/><circle cx="41" cy="84" r="2.6" fill="#1f3347"/>
      <circle class="dg-mej" cx="20" cy="94" r="5" fill="#ffb3a1"/><circle class="dg-mej" cx="48" cy="94" r="5" fill="#ffb3a1"/>
      <path d="M50 96L78 74" stroke="#e53935" stroke-width="5" stroke-linecap="round"/>
      <g class="dg-aire" stroke="#2e9fd6" stroke-width="3" fill="none" stroke-linecap="round"><path d="M58 84l8-6"/><path d="M62 90l9-7"/></g>
    </svg></div>`;

  function reiniciar() {
    det?.detener(); det = null;
    fase = 'inicio'; progreso = 0; aire = []; confeti = []; pop = 0; respiraciones = 0;
    color = COLORES[Math.floor(Math.random() * COLORES.length)];
    metricas = { msSoplo: 0, maxSostenido: 0, sumaI: 0, cuadros: 0, vecesVoz: 0, _voz: 0 };
    $('#soplo-parar').hidden = true;
    estadoAdulto('Toca el botón verde para empezar.');
    FonoSoploUI.pantallaInicio(escena, { demo: DEMO, onPlay: empezar });
  }

  async function empezar() {
    fase = 'calibrando';
    estadoAdulto('Pidiendo el micrófono…');
    det = FonoSoplo.crear({ config: DETECTOR });
    const ok = await det.iniciar();
    estadoAdulto(ok ? 'Silencio un momento… midiendo el ruido del cuarto.' : 'No se pudo usar el micrófono. Revisa los permisos (para probar: barra espaciadora = soplar).');
    FonoSoploUI.pantallaSilencio(escena, 1300);
    await det.calibrar(1300);
    window.FonoEvidencia?.iniciar?.();
    FonoSoploUI.ocultarOverlay(escena);
    $('#soplo-parar').hidden = false;
    fase = 'jugando'; t0 = performance.now(); quietoDesde = t0;
    estadoAdulto('Que tome aire por la nariz y sople FUERTE y largo. Si se cansa, que respire y siga: el globo baja despacio.');
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
    const fuerte = jugando && st.soplando && I >= cfg.minimo;

    if (jugando) {
      medidorUI.pintar(I, cfg.minimo, st.voz);
      if (st.voz) metricas._voz++; else if (metricas._voz) { metricas.vecesVoz++; metricas._voz = 0; }
      if (st.soplando) { metricas.msSoplo += dt * 1000; metricas.sumaI += I; metricas.cuadros++; }
      if (fuerte) {
        if (!sostenidoDesde) sostenidoDesde = ahora;
        metricas.maxSostenido = Math.max(metricas.maxSostenido, ahora - sostenidoDesde);
        // más fuerza = un poco más rápido, pero siempre exige tiempo de soplo
        const extra = 0.7 + Math.min(1, (I - cfg.minimo) / (1 - cfg.minimo)) * 0.6;
        progreso = Math.min(1, progreso + (dt * 1000 / cfg.msSoplo) * extra);
        quietoDesde = ahora;
        if (Math.random() < 0.8) aire.push({ t: 0 });
        if (progreso >= 1) estallar();
      } else {
        sostenidoDesde = 0;
        if (!st.soplando) progreso = Math.max(0, progreso - dt * 0.035);   // se desinfla despacio
      }
      if (fuerte && !soplandoAntes) respiraciones++;
      soplandoAntes = fuerte;
    } else medidorUI.pintar(0, cfg.minimo, false);

    aire.forEach(a => a.t += dt * 1.8); aire = aire.filter(a => a.t < 1);
    confeti.forEach(c => { c.x += c.vx * dt; c.y += c.vy * dt; c.vy += 300 * dt; c.r += dt * 4; c.vida -= dt * 0.6; });
    confeti = confeti.filter(c => c.vida > 0);
    pop = Math.max(0, pop - dt * 2);
    dibujar(ahora, I, fuerte, jugando && ahora - quietoDesde > 900);
    requestAnimationFrame(loop);
  }

  function estallar() {
    const b = globoPos();
    for (let i = 0; i < 70; i++) {
      const a = Math.random() * Math.PI * 2, v = 120 + Math.random() * 260;
      confeti.push({ x: b.x, y: b.y, vx: Math.cos(a) * v, vy: Math.sin(a) * v - 80, r: Math.random() * 6, vida: 1, c: COLORES[i % COLORES.length] });
    }
    pop = 1; progreso = 1;
    FonoSoploUI.sonido('pop');
    setTimeout(() => FonoSoploUI.sonido('meta'), 250);
    terminar(true);
  }

  function globoPos() {
    const base = Math.min(W, H);
    const r = base * (0.06 + progreso * 0.28);
    return { x: W * 0.58, y: H * 0.5 - progreso * H * 0.06, r };
  }

  function dibujar(ahora, I, fuerte, pedirAire) {
    const cielo = g.createLinearGradient(0, 0, 0, H);
    cielo.addColorStop(0, '#bfe6ff'); cielo.addColorStop(1, '#f2fbff');
    g.fillStyle = cielo; g.fillRect(0, 0, W, H);
    g.fillStyle = '#c9ecb9'; g.fillRect(0, H * 0.86, W, H);

    // Medidor de llenado (columna a la derecha, sin texto)
    const mx = W - 36, my = H * 0.14, mh = H * 0.66;
    g.fillStyle = '#ffffffcc'; roundRect(mx - 12, my - 6, 24, mh + 12, 12); g.fill();
    g.fillStyle = '#e6eef5'; roundRect(mx - 7, my, 14, mh, 7); g.fill();
    g.fillStyle = color; roundRect(mx - 7, my + mh * (1 - progreso), 14, mh * progreso, 7); g.fill();
    estrellita(mx, my - 18, 11, progreso >= 1);

    // Niño
    const cx = W * 0.2, cy = H * 0.68, R = Math.min(W, H) * 0.13;
    g.fillStyle = '#ffd9b8'; g.strokeStyle = '#e8a77a'; g.lineWidth = 3;
    g.beginPath(); g.arc(cx, cy, R, 0, Math.PI * 2); g.fill(); g.stroke();
    g.fillStyle = '#6b3f1f'; g.beginPath(); g.ellipse(cx, cy - R * 0.55, R * 0.95, R * 0.5, 0, Math.PI, 0); g.fill();
    g.fillStyle = '#1f3347';
    g.beginPath(); g.arc(cx - R * 0.32, cy - R * 0.08, R * 0.09, 0, Math.PI * 2); g.arc(cx + R * 0.32, cy - R * 0.08, R * 0.09, 0, Math.PI * 2); g.fill();
    const inflado = fuerte ? 1 : 0.4;
    g.fillStyle = '#ffb3a1';
    g.beginPath(); g.arc(cx - R * 0.55, cy + R * 0.3, R * (0.14 + 0.1 * inflado), 0, Math.PI * 2); g.arc(cx + R * 0.55, cy + R * 0.3, R * (0.14 + 0.1 * inflado), 0, Math.PI * 2); g.fill();
    g.fillStyle = '#b5523b'; g.beginPath(); g.ellipse(cx + R * 0.15, cy + R * 0.42, R * 0.12, R * 0.12, 0, 0, Math.PI * 2); g.fill();

    // Boquilla del globo y globo
    const b = globoPos();
    const bocaX = cx + R * 0.22, bocaY = cy + R * 0.42;
    if (progreso < 1) {
      g.strokeStyle = shade(color, -30); g.lineWidth = Math.max(4, R * 0.14); g.lineCap = 'round';
      g.beginPath(); g.moveTo(bocaX, bocaY); g.quadraticCurveTo((bocaX + b.x) / 2, bocaY, b.x - b.r * 0.15, b.y + b.r * 0.95); g.stroke();
      const tiembla = fuerte ? Math.sin(ahora / 40) * 1.5 : 0;
      g.fillStyle = color;
      g.beginPath(); g.ellipse(b.x + tiembla, b.y, b.r * 0.92, b.r, 0, 0, Math.PI * 2); g.fill();
      g.fillStyle = 'rgba(255,255,255,.4)';
      g.beginPath(); g.ellipse(b.x - b.r * 0.35, b.y - b.r * 0.4, b.r * 0.15, b.r * 0.28, -0.4, 0, Math.PI * 2); g.fill();
      // aire viajando por la boquilla
      g.fillStyle = '#ffffffcc';
      aire.forEach(a => {
        const x = bocaX + (b.x - b.r * 0.15 - bocaX) * a.t, y = bocaY + (b.y + b.r * 0.95 - bocaY) * a.t * a.t;
        g.beginPath(); g.arc(x, y, 3, 0, Math.PI * 2); g.fill();
      });
    }
    confeti.forEach(c => { g.globalAlpha = Math.max(0, c.vida); g.fillStyle = c.c; g.fillRect(c.x, c.y, 6 + c.r, 4 + c.r); });
    g.globalAlpha = 1;
    if (pop > 0) { g.strokeStyle = `rgba(255,200,0,${pop})`; g.lineWidth = 6; g.beginPath(); g.arc(b.x, b.y, b.r * (1.6 - pop * 0.5), 0, Math.PI * 2); g.stroke(); }

    // Pista visual: si deja de soplar, aparece la carita «toma aire» (HTML sobre la escena)
    mostrarRespira(pedirAire && progreso < 1, cx, cy - R * 1.2);
  }

  let respiraEl = null;
  function mostrarRespira(ver, x, y) {
    if (!respiraEl) {
      respiraEl = document.createElement('div');
      respiraEl.className = 'globo-respira';
      respiraEl.setAttribute('aria-hidden', 'true');
      respiraEl.innerHTML = FonoSoploUI.icons.INSPIRA;
      escena.appendChild(respiraEl);
    }
    respiraEl.classList.toggle('ver', !!ver);
    respiraEl.style.left = x + 'px'; respiraEl.style.top = y + 'px';
  }

  function estrellita(x, y, r, on) {
    g.fillStyle = on ? '#ffc93c' : '#e3e8ef'; g.strokeStyle = on ? '#e9a400' : '#c9d1dc'; g.lineWidth = 2;
    g.beginPath(); for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r; g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); }
    g.closePath(); g.fill(); g.stroke();
  }
  function roundRect(x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
  function shade(hex, p) { const n = parseInt(hex.slice(1), 16); const c = v => Math.max(0, Math.min(255, v + p)); return `rgb(${c(n >> 16)},${c((n >> 8) & 255)},${c(n & 255)})`; }
  function estadoAdulto(t) { const el = $('#soplo-estado'); if (el) el.textContent = t; }

  async function terminar(completo) {
    if (fase !== 'jugando' && fase !== 'calibrando') return;
    fase = 'fin';
    det?.detener(); det = null;
    $('#soplo-parar').hidden = true;
    const est = completo ? 3 : progreso > 0.66 ? 2 : progreso > 0.25 ? 1 : 0;
    setTimeout(async () => {
      const fin = FonoSoploUI.pantallaFinal(escena, { estrellasGanadas: est, guardando: true, onRepetir: reiniciar });
      const seg = ((performance.now() - t0) / 1000).toFixed(1);
      const prom = metricas.cuadros ? metricas.sumaI / metricas.cuadros : 0;
      const notas = `Infla el globo nivel ${nivel}: ${completo ? 'globo inflado' : 'detenido al ' + Math.round(progreso * 100) + '%'} en ${seg} s. ` +
        `Soplo fuerte requerido ${cfg.msSoplo / 1000} s (intensidad mín. ${cfg.minimo}); tiempo total soplando ${(metricas.msSoplo / 1000).toFixed(1)} s; ` +
        `soplo sostenido más largo ${(metricas.maxSostenido / 1000).toFixed(1)} s; intensidad media ${prom.toFixed(2)}; respiraciones usadas ${respiraciones}; ` +
        `veces que habló en vez de soplar ${metricas.vecesVoz}. Registro para revisión profesional; no es calificación clínica.`;
      try {
        if (typeof guardarResultadoJuego === 'function') {
          await guardarResultadoJuego('respiracion', 'globo', completo ? 1 : 0, 1, completo, Math.round(progreso * 100), nivel, { notas, requiereRevisionAudio: true });
        }
        fin.querySelector('.sui-guardado').innerHTML = '<span class="sui-ok">&#10003;</span>';
        estadoAdulto('Actividad guardada.');
      } catch (e) {
        fin.querySelector('.sui-guardado').innerHTML = '';
        estadoAdulto('No se pudo guardar. Revisa la conexión y vuelve a jugar.');
      }
    }, completo ? 1300 : 0);
  }

  document.addEventListener('DOMContentLoaded', iniciar);
})();
