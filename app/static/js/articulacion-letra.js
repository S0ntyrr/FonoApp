/* Motor de los juegos Letra B/D/F. La configuración se define en cada plantilla. */
(function () {
  'use strict';

  function iniciar(config) {
    if (!config || !window.FonoArticulacion) {
      console.error('Falta configuración o FonoArticulacion.');
      return;
    }

    const sesion = FonoArticulacion.crearSesionVoz({
      categoria: 'articulacion',
      juego: config.juego,
      idiomaReconocimiento: config.idiomaReconocimiento || 'es-ES',
    });

    let retoActual = 0;
    const hechas = new Set();
    let resultadoGuardado = false;

    function el(id) { return document.getElementById(id); }

    function feedback(elemento, tipo, texto) {
      elemento.className = `art-feedback ${tipo}`;
      elemento.textContent = texto;
    }

    function goStep(n) {
      document.querySelectorAll('.art-step').forEach((s) => s.classList.remove('active'));
      const destino = el(`s${n}`);
      if (destino) destino.classList.add('active');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function hablar(texto) {
      sesion.hablar(texto, { rate: 0.8 });
    }

    function construirSilabas() {
      const cont = el('silabas');
      config.silabas.forEach((silaba, index) => {
        const fila = document.createElement('div');
        fila.className = 'art-silaba-row';
        fila.innerHTML = `
          <span class="art-silaba">${silaba.toUpperCase()}</span>
          <span class="art-mouth">${['😮','😬','😁','😯','😙'][index] || '🗣️'}</span>
          <button type="button" class="art-audio">🔊 Escuchar</button>
        `;
        fila.querySelector('button').addEventListener('click', () => {
  const textoVoz = (config.silabasVoz && config.silabasVoz[index])
    ? config.silabasVoz[index]
    : silaba;

  hablar(textoVoz);
});
        cont.appendChild(fila);
      });
    }

    function actualizarMoto() {
      const reto = config.retosMoto[retoActual];
      if (!reto) {
        el('moto-objetivo').textContent = '¡META!';
        el('moto-contador').textContent = `${config.retosMoto.length} de ${config.retosMoto.length} palabras reconocidas`;
        el('btn-ir-palabras').disabled = false;
        feedback(el('fb-moto'), 'ok', '✅ Llegaste a la meta. Continúa con las palabras finales.');
        return;
      }
      el('moto-objetivo').textContent = reto.palabra.toUpperCase();
      el('moto-contador').textContent = `Palabra ${retoActual + 1} de ${config.retosMoto.length}`;
    }

    function grabarMoto() {
      const reto = config.retosMoto[retoActual];
      if (!reto) return;
      const btn = el('mic-moto');
      const fb = el('fb-moto');

      sesion.reconocerPalabra({
        palabraEsperada: reto.palabra,
        alEscuchar: () => {
          btn.classList.add('escuchando');
          btn.textContent = '⏹️';
          feedback(fb, 'info', `Escuchando… di “${reto.palabra.toUpperCase()}”.`);
        },
        alCorrecto: (coincidencia) => {
          retoActual += 1;
          const pct = Math.min(86, 6 + (retoActual / config.retosMoto.length) * 80);
          el('moto').style.left = `${pct}%`;
          feedback(fb, 'ok', `✅ Palabra reconocida: “${coincidencia.transcript}”.`);
          setTimeout(actualizarMoto, 450);
          actualizarFinalizable();
        },
        alIncorrecto: (mensaje) => feedback(fb, 'error', mensaje),
        alFin: () => {
          btn.classList.remove('escuchando');
          btn.textContent = '🎤';
        },
      });
    }

    function construirPalabras() {
      const grid = el('palabras-grid');
      config.palabras.forEach((item, indice) => {
        const card = document.createElement('div');
        card.className = 'art-item';
        card.innerHTML = `
          <div class="emoji">${item.emoji}</div>
          <div class="word">${item.incompleta}</div>
          <div class="objetivo">Di la palabra completa</div>
          <div class="acciones">
            <button type="button" class="audio-sm" aria-label="Escuchar ${item.palabra}">🔊</button>
            <button type="button" class="mic-sm" aria-label="Pronunciar ${item.palabra}">🎤</button>
          </div>
          <p class="art-estado">Escucha el ejemplo si lo necesitas.</p>
        `;
        const btnAudio = card.querySelector('.audio-sm');
        const btnMic = card.querySelector('.mic-sm');
        const estado = card.querySelector('.art-estado');
        btnAudio.addEventListener('click', () => hablar(item.palabra));
        btnMic.addEventListener('click', () => grabarPalabra(item, indice, card, btnMic, estado));
        grid.appendChild(card);
      });
    }

    function grabarPalabra(item, indice, card, btn, estado) {
      if (hechas.has(indice) || sesion.estaReconociendo()) return;

      sesion.reconocerPalabra({
        palabraEsperada: item.palabra,
        alEscuchar: () => {
          btn.textContent = '⏹️';
          btn.style.background = '#2e7d32';
          estado.textContent = `Escuchando… di “${item.palabra.toUpperCase()}”.`;
          estado.style.color = '#333';
        },
        alCorrecto: (coincidencia) => {
          hechas.add(indice);
          card.classList.add('done');
          btn.textContent = '✓';
          btn.style.background = '#2e7d32';
          estado.textContent = `✅ Reconocida: “${coincidencia.transcript}”`;
          estado.style.color = '#2e7d32';
          actualizarProgreso();
          actualizarFinalizable();
        },
        alIncorrecto: (mensaje) => {
          btn.textContent = '🎤';
          btn.style.background = '#e63946';
          estado.textContent = mensaje;
          estado.style.color = '#b71c1c';
        },
        alFin: () => {
          if (!hechas.has(indice)) {
            btn.textContent = '🎤';
            btn.style.background = '#e63946';
          }
        },
      });
    }

    function actualizarProgreso() {
      const total = config.palabras.length;
      const pct = Math.round((hechas.size / total) * 100);
      el('palabras-progreso').textContent = `${hechas.size} / ${total} palabras reconocidas`;
      el('palabras-fill').style.width = `${pct}%`;
    }

    function actualizarFinalizable() {
      const listo = retoActual >= config.retosMoto.length && hechas.size >= config.palabras.length;
      el('btn-finalizar').disabled = !listo;
    }

    async function guardarResultado() {
      if (resultadoGuardado) return;
      if (retoActual < config.retosMoto.length) {
        goStep(3);
        feedback(el('fb-moto'), 'error', `Completa primero las ${config.retosMoto.length} palabras de la moto.`);
        return;
      }
      if (hechas.size < config.palabras.length) {
        el('palabras-progreso').textContent = `Faltan ${config.palabras.length - hechas.size} palabra(s) por reconocer.`;
        return;
      }

      const btn = el('btn-finalizar');
      btn.disabled = true;
      btn.textContent = 'Guardando…';

      let detalle = { audioUrl: '', audioTranscripcion: sesion.obtenerTranscripcion(), requiereRevisionAudio: true };
      try { detalle = await sesion.finalizar(); }
      catch (e) { console.warn('No se pudo finalizar el audio:', e); }

      const fd = new FormData();
      fd.append('paciente_email', sessionStorage.getItem('paciente_email') || localStorage.getItem('paciente_email_actual') || '');
      fd.append('categoria', 'articulacion');
      fd.append('juego', config.juego);
      fd.append('paso_completado', '5');
      fd.append('total_pasos', '5');
      fd.append('completado', 'true');
      fd.append('puntos', String(config.puntos || 60));
      fd.append('nivel', '1');
      fd.append('ruta', window.location.pathname || '');
      fd.append('audio_transcripcion', detalle.audioTranscripcion || '');
      fd.append('audio_url', detalle.audioUrl || '');
      fd.append('requiere_revision_audio', 'true');
      fd.append('notas', `Palabras completas reconocidas por Web Speech API. La calidad fonética de la ${config.letra} requiere revisión profesional del audio.`);

      try {
        const response = await fetch('/juegos/resultado', { method: 'POST', body: fd });
        if (response.status === 401 || response.status === 403) {
          window.location.href = '/auth/login';
          return;
        }
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        resultadoGuardado = true;
        FonoArticulacion.marcarActividadCompletada();
        btn.textContent = '✓ Actividad guardada';
        reproducirExito();
        goStep(5);
      } catch (e) {
        console.error(`No se pudo guardar ${config.juego}:`, e);
        btn.disabled = false;
        btn.textContent = 'Reintentar guardado';
        el('palabras-progreso').textContent = 'No se pudo guardar el resultado. Intenta nuevamente.';
      }
    }

    function reproducirExito() {
      try {
        if (typeof crearContextoAudioFono !== 'function' || typeof crearTonoFono !== 'function') return;
        const ctx = crearContextoAudioFono();
        if (!ctx) return;
        [523, 659, 784, 1047].forEach((freq, i) => {
          crearTonoFono(ctx, { frequency: freq, startTime: ctx.currentTime + i * 0.15, duration: 0.26, volumeBase: 0.22, type: 'sine' });
        });
      } catch (_) {}
    }

    // Exponer solo las acciones usadas por botones inline de la plantilla.
    window.artGoStep = goStep;
    window.artHablar = hablar;
    window.artGrabarMoto = grabarMoto;
    window.artFinalizar = guardarResultado;

    construirSilabas();
    construirPalabras();
    actualizarMoto();
    actualizarProgreso();
    actualizarFinalizable();
    FonoArticulacion.configurarSiguienteSeguro(el('btn-siguiente-final'), config.siguiente);

    window.addEventListener('beforeunload', () => sesion.cancelar());
  }

  window.iniciarJuegoLetraArticulacion = iniciar;
})();
