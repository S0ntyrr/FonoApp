/* FonoSoplo — detector de SOPLO (no de voz) para los juegos de respiración.
 *
 * Problema anterior: se usaba el volumen promedio del micrófono, así que hablar,
 * reír o un ruido fuerte contaban como "soplar". Además el navegador aplicaba
 * supresión de ruido, que precisamente borra el soplido.
 *
 * Cómo distingue soplo de voz (análisis en cada cuadro, ~60 veces por segundo):
 *  1. Energía sobre el ruido del cuarto (se calibra al empezar, 1.2 s de silencio).
 *  2. Planitud espectral (spectral flatness): el soplo es un ruido "de aire"
 *     repartido en muchas frecuencias (valor alto); la voz concentra la energía
 *     en armónicos (valor bajo).
 *  3. Periodicidad (autocorrelación en el rango del tono de voz 70–450 Hz):
 *     la voz es periódica (vibran las cuerdas vocales), el soplo no.
 *  4. Persistencia: el soplo debe sostenerse ~120 ms para activarse y, si se
 *     detecta voz, se bloquea el soplo durante medio segundo.
 *
 * Nota clínica: los fricativos sordos sostenidos ("ffff", "ssss", "shhh") son
 * también salida de aire sin vibración vocal y pueden contar como soplo.
 *
 * API:
 *   const det = FonoSoplo.crear({ onCuadro(estado){...} });
 *   await det.iniciar();      // pide micrófono
 *   await det.calibrar(1200); // mide ruido ambiente
 *   det.detener();
 *   estado = { soplando, voz, intensidad (0..1), db, planitud, claridad, ms }
 *
 * Para pruebas sin micrófono: mantener pulsada la barra espaciadora simula soplo.
 * Con ?debug=1 en la URL se muestra un panel con las medidas en vivo.
 */
window.FonoSoplo = (function () {
  'use strict';

  const CFG = {
    hpHz: 400,            // se ignora el retumbe grave del viento y la red eléctrica
    minDbSobreRuido: 9,   // dB mínimos sobre el ruido calibrado
    planitudMin: 0.16,    // >: suena a aire
    claridadVoz: 0.5,     // >: suena a voz (periódico)
    msActivar: 120,
    msSoltar: 160,
    msBloqueoVoz: 520,
    rangoDb: 32,          // dB sobre el umbral para llegar a intensidad 1
  };

  function crear(opciones = {}) {
    const onCuadro = opciones.onCuadro || (() => {});
    const cfg = Object.assign({}, CFG, opciones.config || {});
    let ctx = null, stream = null, analyser = null, raf = 0;
    let tiempo = null, frec = null, sr = 48000;
    let ruidoDb = -50, calibrando = false, muestrasRuido = [];
    let candidatoDesde = 0, faltaDesde = 0, soplando = false, vozHasta = 0;
    let suave = 0, teclaSoplo = false, ultimo = performance.now();
    let debugEl = null;
    const estado = { soplando: false, voz: false, intensidad: 0, db: -100, planitud: 0, claridad: 0, ms: 16, simulado: false, listo: false };

    function onKey(e) { if (e.code === 'Space') { teclaSoplo = e.type === 'keydown'; e.preventDefault(); } }

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
        tiempo = new Float32Array(analyser.fftSize);
        frec = new Float32Array(analyser.frequencyBinCount);
        estado.listo = true;
      } catch (e) {
        console.warn('FonoSoplo: micrófono no disponible', e);
        estado.listo = false;
      }
      ultimo = performance.now();
      bucle();
      return estado.listo;
    }

    function calibrar(ms = 1200) {
      if (!estado.listo) return Promise.resolve(ruidoDb);
      calibrando = true; muestrasRuido = [];
      return new Promise(res => setTimeout(() => {
        calibrando = false;
        if (muestrasRuido.length) {
          muestrasRuido.sort((a, b) => a - b);
          // percentil 60: robusto ante un golpe o una palabra suelta durante la calibración
          ruidoDb = Math.max(-75, Math.min(-25, muestrasRuido[Math.floor(muestrasRuido.length * 0.6)]));
        }
        res(ruidoDb);
      }, ms));
    }

    function medirFrame() {
      analyser.getFloatTimeDomainData(tiempo);
      analyser.getFloatFrequencyData(frec);
      // Energía
      let s = 0;
      for (let i = 0; i < tiempo.length; i++) s += tiempo[i] * tiempo[i];
      const rms = Math.sqrt(s / tiempo.length);
      const db = 20 * Math.log10(rms + 1e-9);
      // Planitud espectral en 400–7000 Hz
      const binHz = sr / analyser.fftSize;
      const b0 = Math.max(1, Math.floor(cfg.hpHz / binHz)), b1 = Math.min(frec.length - 1, Math.floor(7000 / binHz));
      let sumLog = 0, sumLin = 0, n = 0;
      for (let i = b0; i <= b1; i++) {
        const p = Math.pow(10, frec[i] / 10) + 1e-14;
        sumLog += Math.log(p); sumLin += p; n++;
      }
      const planitud = n ? Math.exp(sumLog / n) / (sumLin / n) : 0;
      // Periodicidad (autocorrelación normalizada, ventana de 1024 diezmada x2)
      const N = 1024, paso = 2, m = N / paso;
      const srD = sr / paso;
      const lagMin = Math.floor(srD / 450), lagMax = Math.floor(srD / 70);
      let r0 = 0;
      for (let i = 0; i < m; i++) { const v = tiempo[i * paso]; r0 += v * v; }
      let mejor = 0;
      if (r0 > 1e-9) {
        for (let lag = lagMin; lag <= lagMax && lag < m - 8; lag++) {
          let r = 0, e2 = 0;
          for (let i = 0; i < m - lag; i++) { const a = tiempo[i * paso], b = tiempo[(i + lag) * paso]; r += a * b; e2 += b * b; }
          const norm = r / Math.sqrt(r0 * e2 + 1e-12);
          if (norm > mejor) mejor = norm;
        }
      }
      return { db, planitud, claridad: mejor };
    }

    function bucle() {
      const ahora = performance.now();
      estado.ms = Math.min(60, ahora - ultimo); ultimo = ahora;
      let db = -100, planitud = 0, claridad = 0;
      if (analyser) ({ db, planitud, claridad } = medirFrame());
      if (calibrando) muestrasRuido.push(db);

      const sobre = db - ruidoDb;
      const hayEnergia = sobre > cfg.minDbSobreRuido;
      const esVoz = hayEnergia && claridad > cfg.claridadVoz && planitud < 0.3;
      if (esVoz) vozHasta = ahora + cfg.msBloqueoVoz;
      const bloqueado = ahora < vozHasta;
      const pareceAire = !calibrando && hayEnergia && planitud > cfg.planitudMin && claridad < cfg.claridadVoz && !bloqueado;

      if (pareceAire) {
        faltaDesde = 0;
        if (!candidatoDesde) candidatoDesde = ahora;
        if (ahora - candidatoDesde >= cfg.msActivar) soplando = true;
      } else {
        candidatoDesde = 0;
        if (!faltaDesde) faltaDesde = ahora;
        if (ahora - faltaDesde >= cfg.msSoltar || bloqueado) soplando = false;
      }
      let objetivo = soplando ? Math.max(0.08, Math.min(1, (sobre - cfg.minDbSobreRuido) / cfg.rangoDb)) : 0;
      estado.simulado = false;
      if (teclaSoplo) { objetivo = 0.75; estado.simulado = true; }
      suave += (objetivo - suave) * (objetivo > suave ? 0.35 : 0.12);
      if (suave < 0.01) suave = 0;

      Object.assign(estado, { ruidoDb, soplando: soplando || teclaSoplo, voz: bloqueado && !teclaSoplo, intensidad: suave, db, planitud, claridad, calibrando });
      if (debugEl) debugEl.textContent = `dB ${db.toFixed(1)} | ruido ${ruidoDb.toFixed(1)} | planitud ${planitud.toFixed(2)} | voz ${claridad.toFixed(2)} | ${estado.voz ? 'VOZ' : estado.soplando ? 'SOPLO' : '-'} ${suave.toFixed(2)}`;
      try { onCuadro(estado); } catch (e) { console.error(e); }
      raf = requestAnimationFrame(bucle);
    }

    function crearDebug() {
      debugEl = document.createElement('div');
      debugEl.style.cssText = 'position:fixed;left:6px;bottom:6px;z-index:9999;background:#000c;color:#0f0;font:12px monospace;padding:6px 8px;border-radius:6px';
      document.body.appendChild(debugEl);
    }

    function detener() {
      cancelAnimationFrame(raf); raf = 0;
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('keyup', onKey);
      stream?.getTracks().forEach(t => t.stop()); stream = null;
      try { ctx?.close(); } catch (e) {}
      ctx = null; analyser = null; estado.listo = false;
      debugEl?.remove(); debugEl = null;
    }

    window.FonoSoplo.ultimo = estado; // útil para depurar desde la consola
    return { iniciar, calibrar, detener, estado };
  }

  return { crear };
})();
