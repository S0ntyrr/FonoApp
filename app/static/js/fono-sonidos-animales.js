/* FonoSonidosAnimales — sonido del animal que aparece en pantalla.
 *
 * 1) Si el animal está en /static/media/animales/lista.json, se usa su grabación
 *    real <nombre>.mp3 (el equipo puede agregarlas sin tocar código).
 * 2) Si no, el sonido se genera en el navegador (funciona sin Internet).
 * Nombres: perro, gato, vaca, rana, elefante, leon, pinguino, zorro, tortuga,
 * pato, pollito, gallo, cerdo, caballo, oveja, abeja, serpiente, pajaro, oso,
 * mono, grillo, buho, raton.
 */
(function () {
  'use strict';
  let ctx = null;
  const ctxAudio = () => { if (!ctx) { const C = window.AudioContext || window.webkitAudioContext; if (!C) return null; ctx = new C(); } if (ctx.state === 'suspended') ctx.resume(); return ctx; };
  const vol = () => { try { const v = parseFloat(localStorage.getItem('fonoapp_master_volume') || '0.7'); return Number.isNaN(v) ? 0.7 : Math.max(0, Math.min(1, v)); } catch (e) { return 0.7; } };
  const norm = s => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z]/g, '');

  function salida(c, t0, dur, pico, ataque = 0.02, caida = 0.1) {
    const g = c.createGain();
    g.gain.setValueAtTime(0.0001, t0); g.gain.exponentialRampToValueAtTime(Math.max(0.0002, pico), t0 + ataque);
    g.gain.setValueAtTime(Math.max(0.0002, pico), t0 + Math.max(ataque, dur - caida)); g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    g.connect(c.destination); return g;
  }
  function osc(c, tipo, t0, dur, frecs) {   // frecs: [[t,f], ...] relativo a t0
    const o = c.createOscillator(); o.type = tipo;
    frecs.forEach(([t, f], i) => i === 0 ? o.frequency.setValueAtTime(f, t0 + t) : o.frequency.exponentialRampToValueAtTime(f, t0 + t));
    o.start(t0); o.stop(t0 + dur + 0.05); return o;
  }
  function filtro(c, tipo, f, q = 1) { const b = c.createBiquadFilter(); b.type = tipo; b.frequency.value = f; b.Q.value = q; return b; }
  function ruido(c, t0, dur) { const b = c.createBuffer(1, Math.ceil(c.sampleRate * dur), c.sampleRate), d = b.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; const s = c.createBufferSource(); s.buffer = b; s.start(t0); return s; }
  function am(c, nodo, t0, dur, hz, prof = 0.8) {   // modulación de amplitud (gruñidos, croar, zumbidos)
    const g = c.createGain(); g.gain.value = 1 - prof / 2; const l = c.createOscillator(); l.frequency.value = hz; const p = c.createGain(); p.gain.value = prof / 2;
    l.connect(p); p.connect(g.gain); l.start(t0); l.stop(t0 + dur + 0.05); nodo.connect(g); return g;
  }
  function cadena(...n) { for (let i = 0; i < n.length - 1; i++) n[i].connect(n[i + 1]); return n[n.length - 1]; }

  const S = {
    perro(c, t, v) { [0, 0.32].forEach(d => { const o = osc(c, 'sawtooth', t + d, 0.18, [[0, 520], [0.18, 260]]); cadena(o, filtro(c, 'bandpass', 900, 1.5), salida(c, t + d, 0.18, v * 2.4, 0.01, 0.08)); const n = ruido(c, t + d, 0.08); cadena(n, filtro(c, 'bandpass', 1500, 1), salida(c, t + d, 0.08, v * 0.8, 0.005, 0.05)); }); return 0.6; },
    gato(c, t, v) { const o = osc(c, 'sawtooth', t, 0.9, [[0, 480], [0.35, 720], [0.9, 420]]); const f = filtro(c, 'bandpass', 900, 3); f.frequency.setValueAtTime(2300, t); f.frequency.linearRampToValueAtTime(1100, t + 0.4); f.frequency.linearRampToValueAtTime(700, t + 0.9); cadena(o, f, salida(c, t, 0.9, v * 3, 0.06, 0.25)); return 0.95; },
    vaca(c, t, v) { const o = osc(c, 'sawtooth', t, 1.4, [[0, 130], [0.3, 140], [1.4, 105]]); cadena(o, filtro(c, 'lowpass', 500, 2), salida(c, t, 1.4, v * 3, 0.15, 0.4)); return 1.45; },
    rana(c, t, v) { [0, 0.55].forEach(d => { const o = osc(c, 'sawtooth', t + d, 0.4, [[0, 170], [0.4, 140]]); cadena(am(c, o, t + d, 0.4, 28, 1), filtro(c, 'bandpass', 600, 2), salida(c, t + d, 0.4, v * 3, 0.03, 0.1)); }); return 1; },
    elefante(c, t, v) { const o = osc(c, 'sawtooth', t, 1.3, [[0, 320], [0.5, 560], [1.3, 480]]); const l = c.createOscillator(), p = c.createGain(); l.frequency.value = 8; p.gain.value = 18; l.connect(p); p.connect(o.frequency); l.start(t); l.stop(t + 1.35); cadena(o, filtro(c, 'bandpass', 1300, 1.2), salida(c, t, 1.3, v * 2.6, 0.08, 0.3)); const n = ruido(c, t, 1.3); cadena(n, filtro(c, 'bandpass', 2500, 0.8), salida(c, t, 1.3, v * 0.35, 0.1, 0.3)); return 1.35; },
    leon(c, t, v) { const o = osc(c, 'sawtooth', t, 1.5, [[0, 95], [0.5, 120], [1.5, 70]]); cadena(am(c, o, t, 1.5, 34, 0.9), filtro(c, 'lowpass', 700, 1), salida(c, t, 1.5, v * 3.2, 0.25, 0.5)); const n = ruido(c, t, 1.5); cadena(am(c, n, t, 1.5, 34, 0.9), filtro(c, 'lowpass', 900, 0.7), salida(c, t, 1.5, v * 1.2, 0.25, 0.5)); return 1.55; },
    oso(c, t, v) { const o = osc(c, 'sawtooth', t, 1.1, [[0, 80], [1.1, 65]]); cadena(am(c, o, t, 1.1, 25, 0.9), filtro(c, 'lowpass', 500, 1), salida(c, t, 1.1, v * 3, 0.2, 0.4)); return 1.15; },
    pinguino(c, t, v) { [0, 0.22, 0.44, 0.7].forEach((d, i) => { const o = osc(c, 'sawtooth', t + d, 0.18, [[0, 520 - i * 20], [0.18, 460]]); cadena(o, filtro(c, 'bandpass', 1100, 2), salida(c, t + d, 0.18, v * 2.4, 0.01, 0.06)); }); return 0.95; },
    zorro(c, t, v) { [0, 0.3, 0.6].forEach(d => { const o = osc(c, 'sawtooth', t + d, 0.2, [[0, 900], [0.08, 1300], [0.2, 800]]); cadena(o, filtro(c, 'bandpass', 1600, 2), salida(c, t + d, 0.2, v * 2, 0.01, 0.08)); }); return 0.85; },
    tortuga(c, t, v) { const n = ruido(c, t, 0.7); cadena(n, filtro(c, 'highpass', 2500, 0.7), salida(c, t, 0.7, v * 0.9, 0.1, 0.3)); return 0.75; },   // siseo suave
    pato(c, t, v) { [0, 0.3].forEach(d => { const o = osc(c, 'sawtooth', t + d, 0.22, [[0, 420], [0.22, 380]]); cadena(o, filtro(c, 'bandpass', 1300, 4), salida(c, t + d, 0.22, v * 3, 0.01, 0.08)); }); return 0.6; },
    pollito(c, t, v) { [0, 0.25, 0.5].forEach(d => { const o = osc(c, 'sine', t + d, 0.14, [[0, 2600], [0.14, 3600]]); cadena(o, salida(c, t + d, 0.14, v * 1.2, 0.01, 0.05)); }); return 0.7; },
    pajaro(c, t, v) { [0, 0.15, 0.3, 0.55].forEach((d, i) => { const o = osc(c, 'sine', t + d, 0.1, [[0, 3000 + i * 300], [0.1, 4200]]); cadena(o, salida(c, t + d, 0.1, v * 1.1, 0.01, 0.04)); }); return 0.7; },
    gallo(c, t, v) { [[0, 0.15, 700], [0.18, 0.15, 900], [0.36, 0.15, 900], [0.54, 0.5, 1000]].forEach(([d, du, f]) => { const o = osc(c, 'sawtooth', t + d, du, [[0, f], [du, f * 0.9]]); cadena(o, filtro(c, 'bandpass', 1500, 2), salida(c, t + d, du, v * 2.2, 0.02, 0.06)); }); return 1.1; },
    cerdo(c, t, v) { [0, 0.3].forEach(d => { const o = osc(c, 'sawtooth', t + d, 0.22, [[0, 220], [0.22, 180]]); cadena(am(c, o, t + d, 0.22, 40, 0.8), filtro(c, 'bandpass', 900, 3), salida(c, t + d, 0.22, v * 3, 0.01, 0.08)); }); return 0.6; },
    caballo(c, t, v) { const o = osc(c, 'sawtooth', t, 1.2, [[0, 700], [0.25, 1000], [1.2, 450]]); const l = c.createOscillator(), p = c.createGain(); l.frequency.value = 14; p.gain.value = 60; l.connect(p); p.connect(o.frequency); l.start(t); l.stop(t + 1.25); cadena(o, filtro(c, 'bandpass', 1400, 1.5), salida(c, t, 1.2, v * 2.4, 0.05, 0.4)); return 1.25; },
    oveja(c, t, v) { const o = osc(c, 'sawtooth', t, 0.9, [[0, 380], [0.9, 360]]); cadena(am(c, o, t, 0.9, 9, 0.7), filtro(c, 'bandpass', 1100, 2), salida(c, t, 0.9, v * 2.6, 0.05, 0.3)); return 0.95; },
    abeja(c, t, v) { const o = osc(c, 'sawtooth', t, 1.2, [[0, 220], [0.6, 240], [1.2, 215]]); cadena(am(c, o, t, 1.2, 60, 0.6), filtro(c, 'bandpass', 700, 1), salida(c, t, 1.2, v * 2, 0.1, 0.3)); return 1.25; },
    serpiente(c, t, v) { const n = ruido(c, t, 1.2); cadena(n, filtro(c, 'highpass', 4500, 0.7), salida(c, t, 1.2, v * 1.4, 0.1, 0.3)); return 1.25; },
    mono(c, t, v) { [[0, 500], [0.18, 600], [0.36, 900], [0.54, 1000]].forEach(([d, f]) => { const o = osc(c, 'sawtooth', t + d, 0.16, [[0, f], [0.16, f * 1.15]]); cadena(o, filtro(c, 'bandpass', 1200, 2), salida(c, t + d, 0.16, v * 2.2, 0.01, 0.06)); }); return 0.75; },
    grillo(c, t, v) { [0, 0.4].forEach(d => { const o = osc(c, 'sine', t + d, 0.25, [[0, 4500]]); cadena(am(c, o, t + d, 0.25, 50, 1), salida(c, t + d, 0.25, v, 0.01, 0.05)); }); return 0.7; },
    buho(c, t, v) { [0, 0.5].forEach(d => { const o = osc(c, 'sine', t + d, 0.4, [[0, 420], [0.4, 380]]); cadena(o, salida(c, t + d, 0.4, v * 2.4, 0.08, 0.2)); }); return 0.95; },
    raton(c, t, v) { [0, 0.18, 0.36].forEach(d => { const o = osc(c, 'sine', t + d, 0.08, [[0, 3500], [0.08, 4200]]); cadena(o, salida(c, t + d, 0.08, v, 0.005, 0.03)); }); return 0.5; },
  };
  const ALIAS = { perrito: 'perro', gatito: 'gato', pinguino: 'pinguino', pingino: 'pinguino', leon: 'leon', pollo: 'pollito', pajarito: 'pajaro', loro: 'pajaro', toro: 'vaca' };

  let actual = null;
  function detener() { try { actual?.pause(); } catch (_) {} actual = null; }

  function sintetizar(nombre) {
    const c = ctxAudio(); const fn = S[nombre]; if (!c || !fn) return 0;
    return fn(c, c.currentTime + 0.03, 0.12 * vol() + 0.0001);
  }

  // Grabaciones reales disponibles (static/media/animales/lista.json); el resto se sintetiza.
  let reales = null;
  const cargarLista = () => reales || (reales = fetch('/static/media/animales/lista.json', { cache: 'no-cache' })
    .then(r => r.ok ? r.json() : []).then(l => new Set((Array.isArray(l) ? l : []).map(norm))).catch(() => new Set()));
  cargarLista();

  async function reproducir(nombreLibre) {
    const n = ALIAS[norm(nombreLibre)] || norm(nombreLibre);
    if (!S[n]) return false;
    detener();
    const lista = await cargarLista();
    if (lista.has(n)) {
      try { const a = new Audio(`/static/media/animales/${n}.mp3`); a.volume = vol(); actual = a; await a.play(); return true; }
      catch (_) { actual = null; }
    }
    sintetizar(n); return true;
  }
  window.FonoSonidosAnimales = { reproducir, sintetizar, disponibles: Object.keys(S), detener };
})();
