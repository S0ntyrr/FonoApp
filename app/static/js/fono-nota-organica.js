/* Notas musicales con timbre orgánico (voz/flauta suave) para los juegos de fonación. */
(function () {
    'use strict';
    function volumen() {
        try { const v = parseFloat(localStorage.getItem('fonoapp_master_volume') || '0.7'); return Number.isNaN(v) ? 0.7 : Math.max(0, Math.min(1, v)); }
        catch (e) { return 0.7; }
    }
    /* Nota con timbre más orgánico (parecido a una voz/flauta suave):
     * fundamental + armónicos que se apagan, ataque suave, vibrato natural
     * que aparece después del ataque, filtro que redondea el sonido y un
     * final suave (sin cortes). Devuelve el tiempo en que termina. */
    window.tocarNotaOrganica = function tocarNotaOrganica(ctx, frecuencia, duracion = 1, inicio) {
        if (!ctx) return 0;
        const t0 = inicio ?? ctx.currentTime + 0.02;
        const vol = Math.max(0.0001, 0.22 * volumen());
        const salida = ctx.createGain();
        const filtro = ctx.createBiquadFilter();
        filtro.type = 'lowpass'; filtro.frequency.value = Math.min(4000, frecuencia * 6); filtro.Q.value = 0.6;
        salida.connect(filtro); filtro.connect(ctx.destination);
        // Envolvente: ataque 0.08 s, sostén con leve respiración, final 0.35 s
        salida.gain.setValueAtTime(0.0001, t0);
        salida.gain.exponentialRampToValueAtTime(vol, t0 + 0.08);
        salida.gain.setValueAtTime(vol, t0 + Math.max(0.1, duracion - 0.35));
        salida.gain.exponentialRampToValueAtTime(0.0001, t0 + duracion);
        // Vibrato suave (5 Hz) que entra poco a poco
        const lfo = ctx.createOscillator(), prof = ctx.createGain();
        lfo.frequency.value = 5; prof.gain.setValueAtTime(0, t0);
        prof.gain.linearRampToValueAtTime(frecuencia * 0.006, t0 + Math.min(0.6, duracion * 0.4));
        lfo.connect(prof);
        [[1, 1], [2, 0.32], [3, 0.14], [4, 0.06]].forEach(([mult, amp]) => {
            const osc = ctx.createOscillator(), g = ctx.createGain();
            osc.type = mult === 1 ? 'triangle' : 'sine';
            osc.frequency.value = frecuencia * mult;
            prof.connect(osc.frequency);
            g.gain.value = amp;
            osc.connect(g); g.connect(salida);
            osc.start(t0); osc.stop(t0 + duracion + 0.05);
        });
        lfo.start(t0); lfo.stop(t0 + duracion + 0.05);
        return t0 + duracion;
    };

})();
