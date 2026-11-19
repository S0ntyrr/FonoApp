/* FonoSoplo — detector de SOPLO (no de voz) para los juegos de respiración.
 *
 * Pensado para jugar con celular o tablet en lugares con ruido (colegio,
 * consultorio con otros niños). La clave no es "más o menos sensible", sino
 * comparar el soplo con el ruido del lugar Y con el soplo de ESE niño:
 *
 *  1. Ruido del lugar: se mide al empezar (no hace falta silencio) y se sigue
 *     midiendo durante el juego; si el lugar se vuelve más ruidoso, el umbral
 *     sube solo, y si se calma, baja.
 *  2. Soplo de prueba: antes de jugar el niño sopla una vez cerca del
 *     micrófono. El umbral queda entre el ruido y ese soplo (personal).
 *  3. Cómo suena el soplo cercano:
 *     - planitud espectral alta (ruido "de aire", sin armónicos), y/o
 *     - "viento": el aire que pega directo en el micrófono produce un rugido
 *       grave (20–180 Hz) que las voces lejanas casi no tienen.
 *  4. Voz: periodicidad (cuerdas vocales). Solo bloquea el soplo una voz
 *     CERCANA y fuerte (la del niño), no las conversaciones de fondo.
 *  5. Ayuda del adulto: si el lugar es imposible, el adulto mantiene pulsado
 *     un botón mientras ve al niño soplar. Queda registrado como asistido.
 *
 * Nota clínica: los fricativos sordos sostenidos ("ffff", "ssss", "shhh") son
 * también salida de aire sin vibración vocal y pueden contar como soplo.
 *
 * API:
 *   const det = FonoSoplo.crear({ config, onCuadro(estado){...} });
 *   await det.iniciar();                 // pide micrófono
 *   await det.calibrar(1200);            // mide el ruido del lugar
 *   await det.calibrarSoplo({ onProgreso(p){} });   // soplo de prueba (0..1)
 *   det.ajustar({ exigencia: -1|0|1, ruidoso: bool }); det.ayuda(true|false);
 *   det.resumen()  -> texto para el profesional
 *   estado = { soplando, voz, casi, intensidad (0..1), db, ruidoDb, umbralDb,
 *              nivelRuido: 'bajo'|'medio'|'alto', asistido, ... }
 *
 * Para pruebas sin micrófono: mantener pulsada la barra espaciadora simula soplo.
 * Con ?debug=1 en la URL se muestra un panel con las medidas en vivo.
 */
window.FonoSoplo = (function () {
  'use strict';

  const CFG = {
    hpHz: 400,            // análisis de "aire" y voz por encima del retumbe grave
    minDbSobreRuido: 9,   // margen mínimo sobre el ruido (si no hay soplo de prueba)
    margenMin: 6,         // margen mínimo con soplo de prueba
    margenMax: 20,
    fraccionUmbral: 0.45, // el umbral queda al 45 % entre el ruido y el soplo de prueba
    planitudMin: 0.16,    // >: suena a aire
    claridadVoz: 0.5,     // >: suena a voz (periódico)
    vientoMin: 0.5,       // >: rugido de aire directo en el micrófono
    vozCercaDb: 3,        // la voz bloquea solo si supera el umbral en estos dB
    msActivar: 120,
    msSoltar: 160,
    msBloqueoVoz: 520,
    rangoDb: 32,          // escala de intensidad sin soplo de prueba
    subidaRuido: 0.004,   // qué tan rápido sube el ruido estimado (~4 s)
    bajadaRuido: 0.06,
  };
  const CLAVE_PERFIL = 'fono_soplo_perfil';
  const VIGENCIA_PERFIL_MS = 25 * 60 * 1000;

  const leerPerfil = () => { try { const p = JSON.parse(localStorage.getItem(CLAVE_PERFIL) || 'null'); return p && Date.now() - p.t < VIGENCIA_PERFIL_MS ? p : null; } catch (e) { return null; } };
  const guardarPerfil = p => { try { localStorage.setItem(CLAVE_PERFIL, JSON.stringify({ ...p, t: Date.now() })); } catch (e) {} };
  const percentil = (lista, q) => { if (!lista.length) return null; const a = [...lista].sort((x, y) => x - y); return a[Math.min(a.length - 1, Math.floor(a.length * q))]; };

  let ultimoResumen = '';

  function crear(opciones = {}) {
    const onCuadro = opciones.onCuadro || (() => {});
    const cfg = Object.assign({}, CFG, opciones.config || {});
    let ctx = null, stream = null, analyser = null, analyserRaw = null, raf = 0;
    let tiempo = null, frec = null, frecRaw = null, sr = 48000;
    let ruidoDb = -50, calibrando = false, muestrasRuido = [];
    let soploDb = null, ajusteDb = 0, ruidoso = false;
    let prueba = null;   // calibración del soplo en curso
    let candidatoDesde = 0, faltaDesde = 0, soplando = false, vozHasta = 0;
    let suave = 0, teclaSoplo = false, ayudaAdulto = false, ultimo = performance.now();
    let debugEl = null;
    const m = { msJuego: 0, msSoplo: 0, msAyuda: 0, sumaRuido: 0, cuadros: 0, ruidoMax: -100, vecesVoz: 0, pruebaOk: null, iniciado: 0 };
    const estado = { soplando: false, voz: false, casi: false, intensidad: 0, db: -100, ruidoDb, umbralDb: -41, planitud: 0, claridad: 0, viento: 0, ms: 16, simulado: false, asistido: false, listo: false, nivelRuido: 'bajo', tienePrueba: false };

    function onKey(e) { if (e.code === 'Space' && !/INPUT|TEXTAREA|SELECT/.test(e.target?.tagName || '')) { teclaSoplo = e.type === 'keydown'; e.preventDefault(); } }

    async function iniciar() {
      window.addEventListener('keydown', onKey);
      window.addEventListener('keyup', onKey);
      if (new URLSearchParams(location.search).get('debug') === '1') crearDebug();
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false, channelCount: 1 }
        });
        const Ctx = window.AudioContext || window.webkitAudioContext;
        ctx = new Ctx();
        if (ctx.state === 'suspended') await ctx.resume();
        sr = ctx.sampleRate;
        const src = ctx.createMediaStreamSource(stream);
        const hp = ctx.createBiquadFilter();
        hp.type = 'highpass'; hp.frequency.value = cfg.hpHz; hp.Q.value = 0.7;
        analyser = ctx.createAnalyser();
        analyser.fftSize = 2048;
        analyser.smoothingTimeConstant = 0.25;
        src.connect(hp); hp.connect(analyser);
        analyserRaw = ctx.createAnalyser();          // señal completa: rugido grave del aire
        analyserRaw.fftSize = 2048; analyserRaw.smoothingTimeConstant = 0.3;
        src.connect(analyserRaw);
        tiempo = new Float32Array(analyser.fftSize);
        frec = new Float32Array(analyser.frequencyBinCount);
        frecRaw = new Float32Array(analyserRaw.frequencyBinCount);
        estado.listo = true;
      } catch (e) {
        console.warn('FonoSoplo: micrófono no disponible', e);
        estado.listo = false;
      }
      const p = leerPerfil();
      if (p && Number.isFinite(p.sobre)) { soploDb = null; estado.tienePrueba = true; m.pruebaOk = true; m.pruebaSobre = p.sobre; perfilPrevio = p; }
      m.iniciado = performance.now();
      ultimo = performance.now();
      bucle();
      return estado.listo;
    }
    let perfilPrevio = null;   // soplo de prueba reciente (se aplica tras medir el ruido)

    function calibrar(ms = 1200) {
      if (!estado.listo) return Promise.resolve(ruidoDb);
      calibrando = true; muestrasRuido = [];
      return new Promise(res => setTimeout(() => {
        calibrando = false;
        // percentil 60: robusto ante un golpe o una palabra suelta durante la medida
        const p = percentil(muestrasRuido, 0.6);
        if (p != null) ruidoDb = Math.max(-80, Math.min(-15, p));
        if (perfilPrevio) soploDb = ruidoDb + perfilPrevio.sobre;   // el soplo del niño, relativo al lugar de hoy
        res(ruidoDb);
      }, ms));
    }

    /* Soplo de prueba: espera hasta msNecesario de soplo (o msMax) y fija el umbral personal. */
    function calibrarSoplo({ msNecesario = 900, msMax = 7000, onProgreso } = {}) {
      return new Promise(res => {
        prueba = { muestras: [], ms: 0, desde: performance.now(), msNecesario, msMax, onProgreso, fin: res };
      });
    }
    function cerrarPrueba(ok) {
      const p = prueba; prueba = null;
      if (!p) return;
      const med = percentil(p.muestras, 0.5);
      if (ok && med != null && med > ruidoDb + cfg.margenMin) {
        soploDb = med; estado.tienePrueba = true; m.pruebaOk = true; m.pruebaSobre = soploDb - ruidoDb;
        guardarPerfil({ sobre: m.pruebaSobre });
      } else if (m.pruebaOk == null) m.pruebaOk = false;
      p.fin({ ok: !!ok && soploDb != null, sobreDb: soploDb != null ? Math.round(soploDb - ruidoDb) : null });
    }

    function umbralActual() {
      let margen = cfg.minDbSobreRuido;
      if (soploDb != null) margen = Math.max(cfg.margenMin, Math.min(cfg.margenMax, (soploDb - ruidoDb) * cfg.fraccionUmbral));
      return ruidoDb + Math.max(3, margen + ajusteDb);
    }

    function ajustar({ exigencia, ruidoso: r } = {}) {
      if (Number.isFinite(+exigencia)) ajusteDb = Math.max(-2, Math.min(2, +exigencia)) * 3;
      if (typeof r === 'boolean') { ruidoso = r; cfg.msBloqueoVoz = r ? 320 : CFG.msBloqueoVoz; cfg.vozCercaDb = r ? 6 : CFG.vozCercaDb; }
    }
    function ayuda(activo) { ayudaAdulto = !!activo; }

    function dbDe(buf) { let s = 0; for (let i = 0; i < buf.length; i++) s += buf[i] * buf[i]; return 20 * Math.log10(Math.sqrt(s / buf.length) + 1e-9); }

    function medirFrame() {
      analyser.getFloatTimeDomainData(tiempo);
      analyser.getFloatFrequencyData(frec);
      analyserRaw.getFloatFrequencyData(frecRaw);
      const db = dbDe(tiempo);
      const binHz = sr / analyser.fftSize;
      // Planitud espectral en 400–7000 Hz
      const b0 = Math.max(1, Math.floor(cfg.hpHz / binHz)), b1 = Math.min(frec.length - 1, Math.floor(7000 / binHz));
      let sumLog = 0, sumLin = 0, n = 0;
      for (let i = b0; i <= b1; i++) { const p = Math.pow(10, frec[i] / 10) + 1e-14; sumLog += Math.log(p); sumLin += p; n++; }
      const planitud = n ? Math.exp(sumLog / n) / (sumLin / n) : 0;
      // "Viento": energía 20–180 Hz respecto a 20–7000 Hz en la señal completa
      let bajo = 0, total = 0;
      const k0 = Math.max(1, Math.floor(20 / binHz)), k1 = Math.floor(180 / binHz), k2 = Math.min(frecRaw.length - 1, Math.floor(7000 / binHz));
      for (let i = k0; i <= k2; i++) { const p = Math.pow(10, frecRaw[i] / 10); total += p; if (i <= k1) bajo += p; }
      const viento = total > 0 ? bajo / total : 0;
      // Periodicidad (autocorrelación normalizada, ventana de 1024 diezmada x2)
      const N = 1024, paso = 2, mm = N / paso;
      const srD = sr / paso;
      const lagMin = Math.floor(srD / 450), lagMax = Math.floor(srD / 70);
      let r0 = 0;
      for (let i = 0; i < mm; i++) { const v = tiempo[i * paso]; r0 += v * v; }
      let mejor = 0;
      if (r0 > 1e-9) {
        for (let lag = lagMin; lag <= lagMax && lag < mm - 8; lag++) {
          let r = 0, e2 = 0;
          for (let i = 0; i < mm - lag; i++) { const a = tiempo[i * paso], b = tiempo[(i + lag) * paso]; r += a * b; e2 += b * b; }
          const norm = r / Math.sqrt(r0 * e2 + 1e-12);
          if (norm > mejor) mejor = norm;
        }
      }
      return { db, planitud, claridad: mejor, viento };
    }

    function bucle() {
      const ahora = performance.now();
      const dt = Math.min(60, ahora - ultimo); estado.ms = dt; ultimo = ahora;
      let db = -100, planitud = 0, claridad = 0, viento = 0;
      if (analyser) ({ db, planitud, claridad, viento } = medirFrame());
      if (calibrando) muestrasRuido.push(db);

      const umbral = umbralActual();
      const sobre = db - ruidoDb;
      const hayEnergia = db > umbral;
      const sonidoDeAire = planitud > cfg.planitudMin || viento > cfg.vientoMin;
      const esVoz = db > umbral + cfg.vozCercaDb && claridad > cfg.claridadVoz && planitud < 0.3 && viento < cfg.vientoMin;
      if (esVoz && !(ahora < vozHasta)) m.vecesVoz++;
      if (esVoz) vozHasta = ahora + cfg.msBloqueoVoz;
      const bloqueado = ahora < vozHasta;
      const pareceAire = !calibrando && hayEnergia && sonidoDeAire && claridad < cfg.claridadVoz && !bloqueado;

      if (pareceAire) {
        faltaDesde = 0;
        if (!candidatoDesde) candidatoDesde = ahora;
        if (ahora - candidatoDesde >= cfg.msActivar) soplando = true;
      } else {
        candidatoDesde = 0;
        if (!faltaDesde) faltaDesde = ahora;
        if (ahora - faltaDesde >= cfg.msSoltar || bloqueado) soplando = false;
      }

      // El ruido del lugar se sigue midiendo cuando nadie sopla
      const intentaSoplar = sonidoDeAire && claridad < cfg.claridadVoz && db > ruidoDb + 2.5;
      if (!calibrando && !prueba && !soplando && !candidatoDesde && analyser && !(intentaSoplar && db > ruidoDb)) {
        const k = db < ruidoDb ? cfg.bajadaRuido : cfg.subidaRuido;
        ruidoDb += (db - ruidoDb) * k;
        if (soploDb != null) ruidoDb = Math.min(ruidoDb, soploDb - cfg.margenMin - 2);
        ruidoDb = Math.max(-80, Math.min(-15, ruidoDb));
      }

      // Soplo de prueba: cuenta el tiempo con aire claramente sobre el ruido
      if (prueba) {
        const aireDePrueba = (db > ruidoDb + cfg.margenMin && sonidoDeAire && claridad < 0.55) || teclaSoplo || ayudaAdulto;
        if (aireDePrueba) { prueba.ms += dt; prueba.muestras.push(teclaSoplo || ayudaAdulto ? ruidoDb + 22 : db); }
        prueba.onProgreso?.(Math.min(1, prueba.ms / prueba.msNecesario), aireDePrueba);
        if (prueba.ms >= prueba.msNecesario) cerrarPrueba(true);
        else if (ahora - prueba.desde > prueba.msMax) cerrarPrueba(prueba.ms >= prueba.msNecesario * 0.35);
      }

      const rango = soploDb != null ? Math.max(8, soploDb + 4 - umbral) : cfg.rangoDb;
      let objetivo = soplando ? Math.max(0.08, Math.min(1, (db - umbral) / rango + 0.08)) : 0;
      estado.simulado = false; estado.asistido = false;
      if (teclaSoplo) { objetivo = 0.75; estado.simulado = true; }
      else if (ayudaAdulto) { objetivo = 0.7; estado.asistido = true; }
      suave += (objetivo - suave) * (objetivo > suave ? 0.35 : 0.12);
      if (suave < 0.01) suave = 0;

      // Métricas para el profesional
      if (!calibrando && !prueba && analyser) {
        m.cuadros++; m.sumaRuido += ruidoDb; m.ruidoMax = Math.max(m.ruidoMax, ruidoDb); m.msJuego += dt;
        if (ayudaAdulto) m.msAyuda += dt; else if (soplando || teclaSoplo) m.msSoplo += dt;
      }

      const casi = !soplando && !bloqueado && intentaSoplar && db <= umbral;
      Object.assign(estado, {
        ruidoDb, umbralDb: umbral, soplando: soplando || teclaSoplo || ayudaAdulto, voz: bloqueado && !teclaSoplo && !ayudaAdulto,
        casi, intensidad: suave, db, sobre, planitud, claridad, viento, calibrando, probando: !!prueba,
        nivelRuido: nivelDe(ruidoDb),
      });
      if (debugEl) debugEl.textContent = `dB ${db.toFixed(1)} | ruido ${ruidoDb.toFixed(1)} (${estado.nivelRuido}) | umbral ${umbral.toFixed(1)} | plan ${planitud.toFixed(2)} | viento ${viento.toFixed(2)} | voz ${claridad.toFixed(2)} | ${estado.voz ? 'VOZ' : estado.asistido ? 'AYUDA' : estado.soplando ? 'SOPLO' : casi ? 'casi' : '-'} ${suave.toFixed(2)}`;
      ultimoResumen = resumen();
      try { onCuadro(estado); } catch (e) { console.error(e); }
      raf = requestAnimationFrame(bucle);
    }

    function nivelDe(d) { return d < -55 ? 'bajo' : d < -42 ? 'medio' : 'alto'; }

    function resumen() {
      if (!m.cuadros) return '';
      const prom = m.sumaRuido / m.cuadros;
      const seg = x => Math.round(x / 100) / 10;
      const partes = [`Micrófono: ruido del lugar ${nivelDe(prom)} (prom. ${prom.toFixed(0)} dB, máx. ${m.ruidoMax.toFixed(0)} dB)`];
      if (ruidoso) partes.push('modo lugar ruidoso');
      if (m.pruebaOk === true && m.pruebaSobre != null) partes.push(`soplo de prueba ${Math.round(m.pruebaSobre)} dB sobre el ruido`);
      else if (m.pruebaOk === false) partes.push('soplo de prueba no detectado (umbral estándar)');
      if (ajusteDb) partes.push(`exigencia ${ajusteDb > 0 ? 'mayor' : 'menor'} (${ajusteDb > 0 ? '+' : ''}${ajusteDb} dB)`);
      partes.push(`soplo detectado ${seg(m.msSoplo)} s`);
      if (m.msAyuda > 0) partes.push(`AYUDA DEL ADULTO ${seg(m.msAyuda)} s (${Math.round(100 * m.msAyuda / Math.max(1, m.msAyuda + m.msSoplo))} % del soplo)`);
      if (m.vecesVoz) partes.push(`habló o gritó cerca ${m.vecesVoz} ${m.vecesVoz === 1 ? 'vez' : 'veces'}`);
      return partes.join('; ') + '.';
    }

    function crearDebug() {
      debugEl = document.createElement('div');
      debugEl.style.cssText = 'position:fixed;left:6px;bottom:6px;right:6px;z-index:9999;background:#000c;color:#0f0;font:12px monospace;padding:6px 8px;border-radius:6px';
      document.body.appendChild(debugEl);
    }

    function detener() {
      cancelAnimationFrame(raf); raf = 0;
      if (prueba) cerrarPrueba(false);
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('keyup', onKey);
      stream?.getTracks().forEach(t => t.stop()); stream = null;
      try { ctx?.close(); } catch (e) {}
      ctx = null; analyser = null; analyserRaw = null; estado.listo = false;
      ayudaAdulto = false;
      debugEl?.remove(); debugEl = null;
    }

    function olvidarPrueba() { soploDb = null; perfilPrevio = null; estado.tienePrueba = false; m.pruebaOk = null; m.pruebaSobre = null; try { localStorage.removeItem(CLAVE_PERFIL); } catch (e) {} }

    const api = { iniciar, calibrar, calibrarSoplo, ajustar, ayuda, resumen, olvidarPrueba, detener, estado };
    window.FonoSoplo.ultimo = estado; // útil para depurar desde la consola
    window.FonoSoplo.actual = api;
    return api;
  }

  return { crear, resumen: () => ultimoResumen, perfilReciente: () => !!leerPerfil() };
})();
