/* FonoFonema — el SONIDO de cada letra, generado en el navegador (sin vocal añadida).
 *
 * La voz sintetizada del navegador no puede decir una consonante sola: lee
 * «eme» o «ma». En terapia eso confunde al niño, así que aquí se genera el
 * sonido aislado con Web Audio:
 *  - M: zumbido nasal «mmm» (voz con resonancia nasal, boca cerrada).
 *  - S: aire agudo «sss».   F: aire suave «fff».
 *  - RR: vibración rápida de la lengua (voz modulada ~26 veces por segundo).
 *  - R: un toque corto entre vocales («a-r-a» muy breve, sin vocal final larga).
 *  - P/C: golpes de aire sin voz «p p p».  B/D/G: golpes con voz «b b b».
 *  - Vocales A E I O U: con sus formantes.
 */
(function () {
  'use strict';
  let ctx = null;
  function contexto() {
    if (!ctx) { const C = window.AudioContext || window.webkitAudioContext; if (!C) return null; ctx = new C(); }
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }
  function volumen() {
    try { const v = parseFloat(localStorage.getItem('fonoapp_master_volume') || '0.7'); return Number.isNaN(v) ? 0.7 : Math.max(0, Math.min(1, v)); } catch (e) { return 0.7; }
  }
  function ruido(c, seg) {
    const b = c.createBuffer(1, Math.ceil(c.sampleRate * seg), c.sampleRate), d = b.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    const s = c.createBufferSource(); s.buffer = b; return s;
  }
  function envolvente(c, nodo, t0, dur, pico, ataque = 0.05, caida = 0.12) {
    const g = c.createGain();
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.exponentialRampToValueAtTime(pico, t0 + ataque);
    g.gain.setValueAtTime(pico, t0 + Math.max(ataque, dur - caida));
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    nodo.connect(g); g.connect(c.destination);
    return g;
  }
  // Fuente de voz (glotis) con un poco de vibrato
  function voz(c, t0, dur, f0 = 140) {
    const o = c.createOscillator(); o.type = 'sawtooth'; o.frequency.value = f0;
    const lfo = c.createOscillator(), p = c.createGain(); lfo.frequency.value = 5; p.gain.value = f0 * 0.01; lfo.connect(p); p.connect(o.frequency);
    o.start(t0); o.stop(t0 + dur + 0.05); lfo.start(t0); lfo.stop(t0 + dur + 0.05);
    return o;
  }
  function formantes(c, fuente, lista) {
    const suma = c.createGain(); suma.gain.value = 1;
    lista.forEach(([f, q, a]) => { const bp = c.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = f; bp.Q.value = q; const g = c.createGain(); g.gain.value = a; fuente.connect(bp); bp.connect(g); g.connect(suma); });
    return suma;
  }
  const VOCALES = { A: [[800, 6, 1], [1200, 8, 0.6]], E: [[450, 6, 1], [1900, 10, 0.5]], I: [[300, 6, 1], [2300, 12, 0.4]], O: [[500, 6, 1], [900, 8, 0.6]], U: [[330, 6, 1], [800, 8, 0.5]] };

  function vocal(c, t0, dur, letra, pico) {
    const f = formantes(c, voz(c, t0, dur), VOCALES[letra]);
    envolvente(c, f, t0, dur, pico * 3, 0.06, 0.15);
  }
  function golpe(c, t0, { voz: conVoz, centro, pico }) {
    if (conVoz) { const v = voz(c, t0, 0.09, 120); const lp = c.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 350; v.connect(lp); envolvente(c, lp, t0, 0.09, pico * 1.2, 0.01, 0.03); }
    const n = ruido(c, 0.08); const bp = c.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = centro; bp.Q.value = 1.2; n.connect(bp);
    envolvente(c, bp, t0 + (conVoz ? 0.08 : 0), 0.07, pico * 2.2, 0.004, 0.05); n.start(t0 + (conVoz ? 0.08 : 0));
  }

  function reproducir(letra) {
    const c = contexto(); if (!c) return false;
    const L = String(letra || '').toUpperCase().trim();
    const t0 = c.currentTime + 0.03, pico = 0.18 * volumen() + 0.0001;
    switch (L) {
      case 'M': {   // «mmm»: voz grave filtrada + resonancia nasal
        const v = voz(c, t0, 1.4, 130);
        const f = formantes(c, v, [[250, 4, 1], [1000, 10, 0.15]]);
        const lp = c.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 600; f.connect(lp);
        envolvente(c, lp, t0, 1.4, pico * 3.5, 0.08, 0.25); break;
      }
      case 'S': { const n = ruido(c, 1.3); const hp = c.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 4500; n.connect(hp); envolvente(c, hp, t0, 1.3, pico * 1.6, 0.08, 0.25); n.start(t0); break; }
      case 'F': { const n = ruido(c, 1.3); const bp = c.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 2500; bp.Q.value = 0.4; n.connect(bp); envolvente(c, bp, t0, 1.3, pico * 1.3, 0.08, 0.25); n.start(t0); break; }
      case 'RR': {  // vibración: voz con «a» modulada ~26 Hz
        const f = formantes(c, voz(c, t0, 1.3, 135), [[500, 5, 1], [1400, 8, 0.5]]);
        const trino = c.createGain(); trino.gain.value = 0.5;
        const lfo = c.createOscillator(); lfo.frequency.value = 26; const prof = c.createGain(); prof.gain.value = 0.5; lfo.connect(prof); prof.connect(trino.gain);
        lfo.start(t0); lfo.stop(t0 + 1.35); f.connect(trino);
        envolvente(c, trino, t0, 1.3, pico * 3, 0.06, 0.2); break;
      }
      case 'R': {   // «a-ɾa»: un solo toque breve
        vocal(c, t0, 0.32, 'A', pico); vocal(c, t0 + 0.36, 0.3, 'A', pico); break;
      }
      case 'P': [0, 0.45, 0.9].forEach(d => golpe(c, t0 + d, { voz: false, centro: 900, pico })); break;
      case 'C': case 'K': [0, 0.45, 0.9].forEach(d => golpe(c, t0 + d, { voz: false, centro: 1800, pico })); break;
      case 'B': [0, 0.45, 0.9].forEach(d => golpe(c, t0 + d, { voz: true, centro: 800, pico })); break;
      case 'D': [0, 0.45, 0.9].forEach(d => golpe(c, t0 + d, { voz: true, centro: 3200, pico })); break;
      case 'G': [0, 0.45, 0.9].forEach(d => golpe(c, t0 + d, { voz: true, centro: 1700, pico })); break;
      default:
        if (VOCALES[L]) { vocal(c, t0, 1.2, L, pico); break; }
        return false;
    }
    return true;
  }
  window.FonoFonema = { reproducir };
})();
