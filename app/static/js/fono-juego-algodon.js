/* Sopla el algodón — carrera en primera persona (vista desde el pitillo).
 * - El algodón SOLO avanza mientras el niño sopla (más fuerte = más rápido).
 * - Con el dedo (o el ratón / flechas) se mueve el pitillo de lado a lado
 *   para esquivar piedras y charcos y recoger estrellas.
 * - Piedra: el algodón rebota hacia atrás. Charco: se moja y pesa más un rato.
 * Estilo de carretera pseudo-3D de los juegos clásicos 2D.
 */
(function () {
  'use strict';
  const NIVELES = {
    1: { largo: 3600, sep: [750, 1050], tipos: ['piedra', 'estrella', 'estrella'], dobles: 0, minimo: 0.12 },
    2: { largo: 6000, sep: [520, 820], tipos: ['piedra', 'charco', 'estrella', 'estrella'], dobles: 0.15, minimo: 0.18 },
    3: { largo: 8600, sep: [400, 640], tipos: ['piedra', 'charco', 'piedra', 'estrella'], dobles: 0.35, minimo: 0.24 },
  };
  const D = 300;            // distancia focal (unidades de mundo)
  const DIST_ALGODON = D * 1.9;
  const VISTA = 3600;       // distancia máxima dibujada (camino)
  const VISTA_OBJ = 2600;   // objetos: aparecen desde lejos, no desde el inicio
  const SEG = 100;          // largo de franja del camino
  const ANCHOS = { piedra: 0.42, charco: 0.62, estrella: 0.3 };
  const $ = s => document.querySelector(s);

  let canvas, g, W = 0, H = 0, dpr = 1, escena, medidorUI, det = null;
  let nivel = 1, cfg = NIVELES[1], fase = 'inicio';
  let pos = 0, vel = 0, jugX = 0, objX = 0, objetos = [], particulas = [], soplos = [];
  let mojadoHasta = 0, golpe = 0, estrellas = 0, arrastrando = false, teclas = { izq: false, der: false };
  let metricas, sostenidoDesde = 0, ultimo = 0, inicioJuego = 0, pistaMano = 0, decor = [];

  const curva = z => 0.9 * Math.sin(z / 1100) + 0.45 * Math.sin(z / 430 + 1.3);

  function iniciar() {
    escena = $('#soplo-escena');
    canvas = $('#soplo-canvas'); g = canvas.getContext('2d');
    medidorUI = FonoSoploUI.medidor($('#soplo-medidor'));
    nivel = Math.max(1, Math.min(3, parseInt(new URLSearchParams(location.search).get('nivel') || '1', 10) || 1));
    document.querySelectorAll('[data-nivel]').forEach(b => b.addEventListener('click', () => { if (fase !== 'jugando' && fase !== 'calibrando') elegirNivel(+b.dataset.nivel); }));
    $('#soplo-parar').addEventListener('click', () => terminar(false));
    canvas.addEventListener('pointerdown', e => { arrastrando = true; canvas.setPointerCapture?.(e.pointerId); apuntar(e); });
    canvas.addEventListener('pointermove', e => { if (arrastrando) apuntar(e); });
    ['pointerup', 'pointercancel'].forEach(t => canvas.addEventListener(t, () => { arrastrando = false; }));
    window.addEventListener('keydown', e => { if (e.code === 'ArrowLeft') teclas.izq = true; if (e.code === 'ArrowRight') teclas.der = true; });
    window.addEventListener('keyup', e => { if (e.code === 'ArrowLeft') teclas.izq = false; if (e.code === 'ArrowRight') teclas.der = false; });
    window.addEventListener('resize', ajustar);
    ajustar();
    elegirNivel(nivel);
    ultimo = performance.now();
    requestAnimationFrame(loop);
  }

  function apuntar(e) {
    const r = canvas.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width;
    objX = Math.max(-0.85, Math.min(0.85, (px - 0.5) * 2.1));
    pistaMano = 0;
  }

  function elegirNivel(n) {
    nivel = n; cfg = NIVELES[n];
    document.querySelectorAll('[data-nivel]').forEach(b => b.classList.toggle('activo', +b.dataset.nivel === n));
    reiniciar();
  }

  function generarPista() {
    objetos = []; decor = [];
    let z = 700;
    const carriles = [-0.58, 0, 0.58];
    while (z < cfg.largo - 300) {
      const tipo = cfg.tipos[Math.floor(Math.random() * cfg.tipos.length)];
      const c = Math.floor(Math.random() * 3);
      objetos.push({ tipo, x: carriles[c] + (Math.random() - 0.5) * 0.12, z, activo: true });
      if (tipo !== 'estrella' && Math.random() < cfg.dobles) {
        const otro = (c + 1 + Math.floor(Math.random() * 2)) % 3;
        objetos.push({ tipo: Math.random() < 0.5 ? 'piedra' : 'charco', x: carriles[otro], z: z + 20, activo: true });
      }
      z += cfg.sep[0] + Math.random() * (cfg.sep[1] - cfg.sep[0]);
    }
    for (let dz = 0; dz < cfg.largo + VISTA; dz += 160) {
      const lado = Math.random() < 0.5 ? -1 : 1;
      decor.push({ tipo: Math.random() < 0.55 ? 'arbol' : 'flor', x: lado * (1.5 + Math.random() * 1.6), z: dz + Math.random() * 120, h: Math.random() * 360 });
    }
  }

  function reiniciar() {
    det?.detener(); det = null;
    fase = 'inicio'; pos = 0; vel = 0; jugX = 0; objX = 0; estrellas = 0; golpe = 0; mojadoHasta = 0; particulas = []; soplos = [];
    metricas = { msSoplo: 0, maxSostenido: 0, sumaI: 0, cuadros: 0, piedras: 0, charcos: 0, vecesVoz: 0, _voz: 0 };
    generarPista();
    $('#soplo-parar').hidden = true;
    estadoAdulto('Toca el botón verde para empezar.');
    FonoSoploUI.pantallaInicio(escena, { demo: `<div class="sui-demo-mano">${FonoSoploUI.icons.MANO}</div>`, onPlay: empezar });
  }

  async function empezar() {
    fase = 'calibrando';
    estadoAdulto('Pidiendo el micrófono…');
    det = FonoSoplo.crear({});
    const ok = await det.iniciar();
    estadoAdulto(ok ? 'Silencio un momento… midiendo el ruido del cuarto.' : 'No se pudo usar el micrófono. Revisa los permisos (para probar: barra espaciadora = soplar).');
    FonoSoploUI.pantallaSilencio(escena, 1300);
    await det.calibrar(1300);
    window.FonoEvidencia?.iniciar?.();
    FonoSoploUI.ocultarOverlay(escena);
    $('#soplo-parar').hidden = false;
    fase = 'jugando'; inicioJuego = performance.now(); pistaMano = 1;
    estadoAdulto('Soplar hace avanzar el algodón. Con el dedo se mueve el pitillo para esquivar.');
  }

  function ajustar() {
    dpr = Math.min(2, window.devicePixelRatio || 1);
    const r = canvas.getBoundingClientRect(); W = r.width; H = r.height;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  // Proyección: mundo (x en semianchos de camino, z) -> pantalla
  function horizonte() { return H * 0.36; }
  function camX() { return curva(pos + DIST_ALGODON) + jugX * 0.55; }
  function proyectar(x, z) {
    const dz = z - pos; if (dz < 40) return null;
    const s = D / dz;
    const hz = horizonte();
    return { x: W / 2 + (curva(z) + x - camX()) * s * W * 0.46, y: hz + s * (H * 1.02 - hz), s };
  }

  function loop(ahora) {
    const dt = Math.min(0.05, (ahora - ultimo) / 1000); ultimo = ahora;
    const st = det?.estado || { intensidad: 0, soplando: false, voz: false };
    const jugando = fase === 'jugando';
    const I = jugando ? st.intensidad : 0;
    const empuja = jugando && st.soplando && I >= cfg.minimo;

    if (jugando) {
      medidorUI.pintar(I, cfg.minimo, st.voz);
      if (st.voz) metricas._voz++; else if (metricas._voz) { metricas.vecesVoz++; metricas._voz = 0; }
      if (st.soplando) { metricas.msSoplo += dt * 1000; metricas.sumaI += I; metricas.cuadros++; }
      if (empuja) { if (!sostenidoDesde) sostenidoDesde = ahora; metricas.maxSostenido = Math.max(metricas.maxSostenido, ahora - sostenidoDesde); }
      else sostenidoDesde = 0;

      // Dirección: dedo o flechas
      if (teclas.izq) objX = Math.max(-0.85, objX - dt * 1.8);
      if (teclas.der) objX = Math.min(0.85, objX + dt * 1.8);
      jugX += (objX - jugX) * Math.min(1, dt * 9);

      // Movimiento: solo avanza soplando
      const mojado = ahora < mojadoHasta;
      const acel = empuja ? 420 * (0.4 + I) * (mojado ? 0.45 : 1) : 0;
      const roce = mojado ? 2.6 : 1.5;
      vel += (acel - vel * roce) * dt;
      if (!empuja && vel > 0) vel = Math.max(0, vel - 120 * dt);
      const antes = pos + DIST_ALGODON;
      pos = Math.max(0, pos + vel * dt);
      const ahoraZ = pos + DIST_ALGODON;
      colisiones(antes, ahoraZ, ahora);
      if (empuja && Math.random() < 0.6) soplos.push({ x: 0, y: 0, vida: 1, dx: (Math.random() - 0.5) * 0.4 });
      if (ahoraZ >= cfg.largo) { terminar(true); }
    } else medidorUI.pintar(0, cfg.minimo, false);

    golpe = Math.max(0, golpe - dt * 2.5);
    soplos.forEach(p => p.vida -= dt * 2.2); soplos = soplos.filter(p => p.vida > 0);
    particulas.forEach(p => { p.x += p.vx * dt; p.y += p.vy * dt; p.vy += 500 * dt; p.vida -= dt * 1.6; });
    particulas = particulas.filter(p => p.vida > 0);
    pistaMano = Math.max(0, pistaMano - dt * 0.18);

    dibujar(I, ahora);
    requestAnimationFrame(loop);
  }

  function colisiones(z0, z1, ahora) {
    const radio = 0.2;
    for (const o of objetos) {
      if (!o.activo || o.z < z0 - 5 || o.z > z1 + 5) continue;
      if (Math.abs(o.x - jugX) > ANCHOS[o.tipo] / 2 + radio) continue;
      const p = { x: W / 2 + (jugX * 0.45) * W * 0.46 * (D / DIST_ALGODON), y: yAlgodon() };
      if (o.tipo === 'piedra') {
        o.activo = false; vel = -180; golpe = 1; metricas.piedras++;
        FonoSoploUI.sonido('golpe'); navigator.vibrate?.(120);
        chispa(p, '#b9a68f', 12);
      } else if (o.tipo === 'charco') {
        o.activo = false; mojadoHasta = ahora + 2600; metricas.charcos++;
        FonoSoploUI.sonido('agua'); chispa(p, '#62b6ef', 18);
      } else {
        o.activo = false; estrellas++; FonoSoploUI.sonido('pop'); chispa(p, '#ffc93c', 14);
      }
    }
  }
  function chispa(p, color, n) { for (let i = 0; i < n; i++) particulas.push({ x: p.x, y: p.y, vx: (Math.random() - 0.5) * 380, vy: -120 - Math.random() * 260, vida: 1, color }); }
  function yAlgodon() { const hz = horizonte(); return hz + (D / DIST_ALGODON) * (H * 1.02 - hz); }

  /* ---------- Dibujo ---------- */
  function dibujar(I, ahora) {
    const hz = horizonte();
    const sacudida = golpe * Math.sin(ahora / 22) * 8;
    g.save(); g.translate(sacudida, 0);
    // Cielo y colinas
    const cielo = g.createLinearGradient(0, 0, 0, hz);
    cielo.addColorStop(0, '#7fcbff'); cielo.addColorStop(1, '#d9f2ff');
    g.fillStyle = cielo; g.fillRect(-20, 0, W + 40, hz + 2);
    const des = (curva(pos + DIST_ALGODON) * 60) % W;
    colinas(hz, '#a8dca0', 0.22, des * 0.3, 1);
    colinas(hz, '#8fcf86', 0.13, des * 0.6, 2.1);
    g.fillStyle = '#7ccc6c'; g.fillRect(-20, hz, W + 40, H - hz);

    // Camino por franjas, de lejos a cerca
    const base = Math.floor(pos / SEG) * SEG;
    const tiras = [];
    let ant = null;
    for (let z = base + VISTA; z >= base; z -= SEG / 2) {
      const p = proyectar(0, z);
      if (!p) continue;
      if (ant) tiras.push([ant, p, Math.floor(z / SEG) % 2 === 0]);
      ant = p;
    }
    tiras.forEach(([a, p, par]) => trapecio(a, p, 1.35, par ? '#6fc25e' : '#79cb68', true)); // pasto alterno
    tiras.forEach(([a, p, par]) => trapecio(a, p, 1.12, par ? '#e6c79a' : '#d7b689'));       // borde
    tiras.forEach(([a, p, par]) => trapecio(a, p, 1.0, par ? '#f3dcb3' : '#ead0a3'));        // tierra
    tiras.forEach(([a, p, par]) => { if (par) trapecio(a, p, 0.05, '#ffffffaa'); });         // línea central
    // Meta
    const pm = proyectar(0, cfg.largo);
    // Objetos y decoración (de lejos a cerca)
    const visibles = [];
    decor.forEach(d => { if (d.z > pos + 40 && d.z < pos + VISTA_OBJ) visibles.push(d); });
    objetos.forEach(o => { if (o.activo && o.z > pos + 40 && o.z < pos + VISTA_OBJ) visibles.push(o); });
    if (pm && cfg.largo - pos < VISTA_OBJ) visibles.push({ tipo: 'meta', z: cfg.largo, x: 0 });
    visibles.sort((a, b) => b.z - a.z);
    const zAlg = pos + DIST_ALGODON;
    let algodonDibujado = false;
    for (const o of visibles) {
      if (!algodonDibujado && o.z < zAlg) { escenaJugador(I, ahora); algodonDibujado = true; }
      const p = proyectar(o.x, o.z); if (!p) continue;
      sprite(o, p, ahora);
    }
    if (!algodonDibujado) escenaJugador(I, ahora);

    particulas.forEach(q => { g.globalAlpha = Math.max(0, q.vida); g.fillStyle = q.color; g.beginPath(); g.arc(q.x, q.y, 4, 0, Math.PI * 2); g.fill(); });
    g.globalAlpha = 1;
    g.restore();
    hud();
    if (fase === 'jugando' && pistaMano > 0) manoPista(ahora);
  }

  function trapecio(a, b, ancho, color, todo) {
    const wa = a.s * W * 0.46 * ancho, wb = b.s * W * 0.46 * ancho;
    g.fillStyle = color; g.beginPath();
    if (todo) { g.rect(-20, a.y - 1, W + 40, b.y - a.y + 2); g.fill(); return; }
    g.moveTo(a.x - wa, a.y - 1); g.lineTo(a.x + wa, a.y - 1); g.lineTo(b.x + wb, b.y + 1); g.lineTo(b.x - wb, b.y + 1); g.closePath(); g.fill();
  }

  function colinas(hz, color, alto, desp, frec) {
    g.fillStyle = color; g.beginPath(); g.moveTo(-20, hz);
    for (let x = -20; x <= W + 20; x += 10) g.lineTo(x, hz - (Math.sin((x + desp) / W * Math.PI * frec) * 0.5 + 0.5) * H * alto);
    g.lineTo(W + 20, hz); g.fill();
  }

  function sprite(o, p, ahora) {
    const u = p.s * W * 0.46; // píxeles por unidad de mundo
    if (o.tipo === 'piedra') {
      const w = u * ANCHOS.piedra, h = w * 0.7;
      g.fillStyle = 'rgba(0,0,0,.18)'; g.beginPath(); g.ellipse(p.x, p.y, w * 0.6, h * 0.18, 0, 0, Math.PI * 2); g.fill();
      const gr = g.createLinearGradient(p.x - w / 2, p.y - h, p.x + w / 2, p.y);
      gr.addColorStop(0, '#b8b1a8'); gr.addColorStop(1, '#6f6860');
      g.fillStyle = gr; g.beginPath();
      g.moveTo(p.x - w * 0.5, p.y); g.quadraticCurveTo(p.x - w * 0.55, p.y - h * 0.7, p.x - w * 0.15, p.y - h);
      g.quadraticCurveTo(p.x + w * 0.3, p.y - h * 1.1, p.x + w * 0.5, p.y - h * 0.45); g.lineTo(p.x + w * 0.48, p.y); g.closePath(); g.fill();
      g.fillStyle = 'rgba(255,255,255,.35)'; g.beginPath(); g.ellipse(p.x - w * 0.15, p.y - h * 0.7, w * 0.14, h * 0.1, -0.5, 0, Math.PI * 2); g.fill();
    } else if (o.tipo === 'charco') {
      const w = u * ANCHOS.charco, h = w * 0.22;
      const gr = g.createRadialGradient(p.x, p.y - h * 0.5, 2, p.x, p.y - h * 0.5, w * 0.55);
      gr.addColorStop(0, '#9fd8ff'); gr.addColorStop(1, '#3d93d6');
      g.fillStyle = gr; g.beginPath(); g.ellipse(p.x, p.y - h * 0.5, w * 0.5, h * 0.5, 0, 0, Math.PI * 2); g.fill();
      g.strokeStyle = 'rgba(255,255,255,.7)'; g.lineWidth = Math.max(1, u * 0.012);
      const o2 = (ahora / 600) % 1;
      g.beginPath(); g.ellipse(p.x, p.y - h * 0.5, w * 0.3 * (0.4 + o2 * 0.6), h * 0.3 * (0.4 + o2 * 0.6), 0, 0, Math.PI * 2); g.stroke();
    } else if (o.tipo === 'estrella') {
      const r = u * ANCHOS.estrella * 0.5, y = p.y - r * 1.6 - Math.sin(ahora / 250 + o.z) * r * 0.3;
      estrella(p.x, y, r, '#ffc93c', '#e9a400');
    } else if (o.tipo === 'arbol') {
      const w = u * 0.55;
      g.fillStyle = '#8a5a35'; g.fillRect(p.x - w * 0.08, p.y - w * 0.9, w * 0.16, w * 0.9);
      g.fillStyle = `hsl(${110 + (o.h % 30)},45%,42%)`; g.beginPath(); g.arc(p.x, p.y - w * 1.1, w * 0.48, 0, Math.PI * 2); g.fill();
      g.fillStyle = 'rgba(255,255,255,.15)'; g.beginPath(); g.arc(p.x - w * 0.15, p.y - w * 1.25, w * 0.2, 0, Math.PI * 2); g.fill();
    } else if (o.tipo === 'flor') {
      const r = Math.max(1.5, u * 0.05);
      g.strokeStyle = '#3f8f3a'; g.lineWidth = Math.max(1, r * 0.4); g.beginPath(); g.moveTo(p.x, p.y); g.lineTo(p.x, p.y - r * 3); g.stroke();
      g.fillStyle = `hsl(${o.h},80%,65%)`; for (let k = 0; k < 5; k++) { const a = k * 1.256; g.beginPath(); g.arc(p.x + Math.cos(a) * r, p.y - r * 3 + Math.sin(a) * r, r * 0.8, 0, Math.PI * 2); g.fill(); }
      g.fillStyle = '#ffd54a'; g.beginPath(); g.arc(p.x, p.y - r * 3, r * 0.6, 0, Math.PI * 2); g.fill();
    } else if (o.tipo === 'meta') {
      const w = u * 1.25, alto = u * 1.4, x0 = p.x - w, x1 = p.x + w;
      g.fillStyle = '#e53935'; g.fillRect(x0 - u * 0.04, p.y - alto, u * 0.08, alto); g.fillRect(x1 - u * 0.04, p.y - alto, u * 0.08, alto);
      const filas = 2, cols = 12, cw = (x1 - x0) / cols, ch = u * 0.12;
      for (let f = 0; f < filas; f++) for (let c = 0; c < cols; c++) { g.fillStyle = (f + c) % 2 ? '#222' : '#fff'; g.fillRect(x0 + c * cw, p.y - alto + f * ch, cw + 0.5, ch + 0.5); }
      for (let c = 0; c < cols; c++) { g.fillStyle = c % 2 ? '#222' : '#fff'; g.fillRect(x0 + c * cw, p.y - u * 0.04, cw + 0.5, u * 0.05); }
    }
  }

  function estrella(x, y, r, c1, c2) {
    g.fillStyle = c1; g.strokeStyle = c2; g.lineWidth = Math.max(1, r * 0.15); g.beginPath();
    for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r; g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); }
    g.closePath(); g.fill(); g.stroke();
  }

  // Algodón + pitillo (vista POV)
  function escenaJugador(I, ahora) {
    const s = D / DIST_ALGODON;
    const cx = W / 2 + jugX * 0.45 * W * 0.46 * s;
    const cy = yAlgodon();
    const R = Math.min(W, H) * 0.075;
    const bote = Math.abs(Math.sin(pos / 60)) * Math.min(8, vel / 40);
    const mojado = performance.now() < mojadoHasta;
    // Sombra
    g.fillStyle = 'rgba(0,0,0,.18)'; g.beginPath(); g.ellipse(cx, cy + R * 0.15, R * 1.05, R * 0.25, 0, 0, Math.PI * 2); g.fill();
    // Algodón: varias bolas suaves
    const y = cy - R * 0.75 - bote;
    const gira = pos / 90;
    const bolas = [[0, 0, 1], [-0.55, 0.2, 0.62], [0.55, 0.18, 0.66], [-0.25, -0.45, 0.6], [0.3, -0.42, 0.58], [0, 0.4, 0.6]];
    bolas.forEach(([dx, dy, r]) => {
      const a = gira * 0.2;
      const x = cx + (dx * Math.cos(a) - dy * Math.sin(a) * 0.3) * R, yy = y + dy * R;
      const gr = g.createRadialGradient(x - r * R * 0.3, yy - r * R * 0.35, r * R * 0.1, x, yy, r * R);
      gr.addColorStop(0, '#ffffff'); gr.addColorStop(1, mojado ? '#a9cfee' : '#dfe6ee');
      g.fillStyle = gr; g.beginPath(); g.arc(x, yy, r * R, 0, Math.PI * 2); g.fill();
    });
    if (mojado) { g.fillStyle = '#3d93d6'; for (let k = 0; k < 3; k++) { const dx = (k - 1) * R * 0.5, dy = ((ahora / 4 + k * 40) % 40) / 40 * R; g.beginPath(); g.ellipse(cx + dx, y + R * 0.7 + dy, 3, 5, 0, 0, Math.PI * 2); g.fill(); } }
    // Aire saliendo del pitillo
    const tipX = cx + (W / 2 - cx) * 0.1 + R * 0.15, tipY = cy + R * 0.55;
    soplos.forEach(p => {
      const t = 1 - p.vida;
      g.strokeStyle = `rgba(255,255,255,${p.vida * 0.9})`; g.lineWidth = 3; g.beginPath();
      const ax = tipX + p.dx * R, ay = tipY - t * R * 1.3;
      g.moveTo(ax, ay); g.lineTo(ax + p.dx * R * 0.6, ay - R * 0.35); g.stroke();
    });
    // Pitillo (desde abajo de la pantalla hacia el algodón)
    pitillo(tipX, tipY, W * 0.56 + jugX * W * 0.16, H + 40, Math.max(18, Math.min(W, H) * 0.05), Math.max(46, Math.min(W, H) * 0.16), ahora, I);
  }

  function pitillo(x1, y1, x0, y0, wTip, wBase, ahora, I) {
    const ang = Math.atan2(y1 - y0, x1 - x0), nx = -Math.sin(ang), ny = Math.cos(ang);
    const quad = [[x0 + nx * wBase / 2, y0 + ny * wBase / 2], [x1 + nx * wTip / 2, y1 + ny * wTip / 2], [x1 - nx * wTip / 2, y1 - ny * wTip / 2], [x0 - nx * wBase / 2, y0 - ny * wBase / 2]];
    g.save(); g.beginPath(); quad.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath();
    g.fillStyle = '#ffffff'; g.fill(); g.clip();
    // Franjas diagonales rojas
    const len = Math.hypot(x1 - x0, y1 - y0), n = 9;
    for (let i = -1; i < n + 1; i++) {
      const t0 = i / n, t1 = (i + 0.45) / n;
      const ax = x0 + (x1 - x0) * t0, ay = y0 + (y1 - y0) * t0, bx = x0 + (x1 - x0) * t1, by = y0 + (y1 - y0) * t1;
      g.fillStyle = '#ef4b5f'; g.beginPath();
      g.moveTo(ax + nx * wBase, ay + ny * wBase); g.lineTo(bx + nx * wBase + (bx - ax) * 0.6, by + ny * wBase + (by - ay) * 0.6);
      g.lineTo(bx - nx * wBase, by - ny * wBase); g.lineTo(ax - nx * wBase - (bx - ax) * 0.6, ay - ny * wBase - (by - ay) * 0.6); g.fill();
    }
    // Brillo
    const gr = g.createLinearGradient(x0 + nx * wBase / 2, y0 + ny * wBase / 2, x0 - nx * wBase / 2, y0 - ny * wBase / 2);
    gr.addColorStop(0, 'rgba(0,0,0,.18)'); gr.addColorStop(0.35, 'rgba(255,255,255,.45)'); gr.addColorStop(1, 'rgba(0,0,0,.25)');
    g.fillStyle = gr; g.fillRect(Math.min(x0, x1) - wBase, Math.min(y0, y1) - wBase, Math.abs(x1 - x0) + wBase * 2, len + wBase * 2);
    g.restore();
    // Boca del pitillo
    g.fillStyle = '#c23245'; g.beginPath(); g.ellipse(x1, y1, wTip / 2, wTip / 4, ang + Math.PI / 2, 0, Math.PI * 2); g.fill();
    if (I > 0.05) { g.strokeStyle = `rgba(255,255,255,${0.4 + I * 0.5})`; g.lineWidth = 2; g.beginPath(); g.ellipse(x1, y1, wTip / 2 + 3, wTip / 4 + 2, ang + Math.PI / 2, 0, Math.PI * 2); g.stroke(); }
  }

  function hud() {
    // Barra de recorrido: algodón -> bandera (gráfico, sin texto)
    const x0 = W * 0.12, x1 = W * 0.82, y = 22;
    g.fillStyle = 'rgba(255,255,255,.75)'; g.beginPath(); g.roundRect?.(x0 - 8, y - 10, x1 - x0 + 16, 20, 10); g.fill();
    const t = Math.min(1, pos / (cfg.largo - DIST_ALGODON));
    g.fillStyle = '#2bb673'; g.beginPath(); g.roundRect?.(x0 - 4, y - 6, (x1 - x0 + 8) * t, 12, 6); g.fill();
    // bandera
    g.fillStyle = '#e53935'; g.fillRect(x1 + 12, y - 14, 3, 28);
    for (let f = 0; f < 3; f++) for (let c = 0; c < 4; c++) { g.fillStyle = (f + c) % 2 ? '#222' : '#fff'; g.fillRect(x1 + 15 + c * 5, y - 14 + f * 5, 5, 5); }
    // algodón en la barra
    const ax = x0 + (x1 - x0) * t;
    g.fillStyle = '#fff'; g.strokeStyle = '#9bb'; g.lineWidth = 1.5;
    [[0, 0, 9], [-6, 3, 6], [6, 3, 6]].forEach(([dx, dy, r]) => { g.beginPath(); g.arc(ax + dx, y + dy - 2, r, 0, Math.PI * 2); g.fill(); g.stroke(); });
    // estrellas recogidas
    estrella(W - 46, 58, 13, '#ffc93c', '#e9a400');
    g.fillStyle = '#1d3b53'; g.font = '800 20px Inter, system-ui, sans-serif'; g.textAlign = 'left'; g.textBaseline = 'middle';
    g.fillText(String(estrellas), W - 28, 59);
  }

  function manoPista(ahora) {
    const s = D / DIST_ALGODON, cy = yAlgodon();
    const x = W / 2 + Math.sin(ahora / 380) * W * 0.18, y = cy + (H - cy) * 0.55;
    g.globalAlpha = Math.min(1, pistaMano * 2);
    g.strokeStyle = 'rgba(255,255,255,.9)'; g.lineWidth = 4; g.setLineDash([8, 8]);
    g.beginPath(); g.moveTo(W / 2 - W * 0.2, y + 26); g.lineTo(W / 2 + W * 0.2, y + 26); g.stroke(); g.setLineDash([]);
    // mano dibujada
    g.save(); g.translate(x, y); const k = Math.min(W, H) / 600; g.scale(k * 1.1, k * 1.1);
    g.fillStyle = '#ffd9b8'; g.strokeStyle = '#c98a5e'; g.lineWidth = 3;
    const p = new Path2D('M-10 58 Q-22 46 -24 34 Q-25 28 -19 29 Q-15 30 -12 38 L-12 6 Q-12 0 -7 0 Q-2 0 -2 6 L-2 26 L-2 20 Q-2 15 3 15 Q8 15 8 20 L8 28 L8 23 Q8 18 13 18 Q18 18 18 23 L18 30 Q18 26 22 26 Q27 26 27 31 L27 44 Q27 54 20 60Z');
    g.fill(p); g.stroke(p); g.restore(); g.globalAlpha = 1;
  }

  function estadoAdulto(t) { const el = $('#soplo-estado'); if (el) el.textContent = t; }

  async function terminar(completo) {
    if (fase !== 'jugando' && fase !== 'calibrando') return;
    fase = 'fin'; vel = 0;
    det?.detener(); det = null;
    $('#soplo-parar').hidden = true;
    const avance = completo ? 1 : Math.min(1, pos / (cfg.largo - DIST_ALGODON));
    let est = completo ? 3 - (metricas.piedras >= 4 ? 1 : 0) : avance > 0.66 ? 2 : avance > 0.2 ? 1 : 0;
    const fin = FonoSoploUI.pantallaFinal(escena, { estrellasGanadas: Math.max(completo ? 1 : 0, est), guardando: true, onRepetir: reiniciar });
    if (completo) FonoSoploUI.sonido('meta');
    const seg = ((performance.now() - inicioJuego) / 1000).toFixed(1);
    const prom = metricas.cuadros ? metricas.sumaI / metricas.cuadros : 0;
    const notas = `Algodón con pitillo nivel ${nivel}: recorrido ${Math.round(avance * 100)}% ${completo ? '(llegó a la meta)' : '(detenido)'} en ${seg} s. ` +
      `Tiempo total soplando ${(metricas.msSoplo / 1000).toFixed(1)} s; soplo sostenido más largo ${(metricas.maxSostenido / 1000).toFixed(1)} s; intensidad media ${prom.toFixed(2)}. ` +
      `Choques con piedras ${metricas.piedras}; charcos ${metricas.charcos}; estrellas ${estrellas}; veces que habló en vez de soplar ${metricas.vecesVoz}. ` +
      `Registro para revisión profesional; no es calificación clínica.`;
    const pasos = Math.round(avance * 10);
    try {
      if (typeof guardarResultadoJuego === 'function') {
        await guardarResultadoJuego('respiracion', 'pitillos', pasos, 10, completo, Math.round(avance * 100), nivel, { notas, requiereRevisionAudio: true });
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
