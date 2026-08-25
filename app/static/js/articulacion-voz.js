/*
 * FonoApp - utilidades robustas de voz para juegos de Articulación.
 * Patrón basado en el juego Letra R:
 * - reconocimiento de PALABRAS completas (no letras aisladas),
 * - idioma español explícito,
 * - hasta 5 alternativas por resultado,
 * - una única evidencia de audio por actividad,
 * - pausa de la evidencia mientras se reproduce un ejemplo TTS.
 */
(function () {
  'use strict';

  function normalizarTexto(texto) {
    return (texto || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-zñ0-9\s]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function contienePalabraExacta(transcripcion, palabraEsperada) {
    const texto = normalizarTexto(transcripcion);
    const objetivo = normalizarTexto(palabraEsperada);
    if (!texto || !objetivo) return false;
    if (texto === objetivo) return true;
    return texto.split(' ').includes(objetivo);
  }

  function obtenerAlternativasFinales(event) {
    const alternativas = [];
    if (!event || !event.results) return alternativas;

    for (let i = event.resultIndex || 0; i < event.results.length; i += 1) {
      const resultado = event.results[i];
      if (!resultado.isFinal) continue;
      for (let j = 0; j < resultado.length; j += 1) {
        alternativas.push({
          transcript: (resultado[j].transcript || '').trim(),
          confidence: Number.isFinite(resultado[j].confidence) ? resultado[j].confidence : null,
        });
      }
    }
    return alternativas;
  }

  function elegirVozEspanol() {
    if (!('speechSynthesis' in window)) return null;
    const voces = window.speechSynthesis.getVoices() || [];
    const prioridades = ['es-CO', 'es-ES', 'es-MX', 'es-US'];

    for (const codigo of prioridades) {
      const voz = voces.find((v) => (v.lang || '').toLowerCase() === codigo.toLowerCase());
      if (voz) return voz;
    }
    return voces.find((v) => (v.lang || '').toLowerCase().startsWith('es')) || null;
  }

  function hablarEspanol(texto, opciones = {}) {
    if (!texto) return false;
    if (!('speechSynthesis' in window) || !('SpeechSynthesisUtterance' in window)) return false;

    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(texto);
    const voz = elegirVozEspanol();
    if (voz) utter.voice = voz;
    utter.lang = voz ? voz.lang : (opciones.lang || 'es-CO');
    utter.rate = opciones.rate || 0.82;
    utter.pitch = opciones.pitch || 1;
    utter.volume = 1;
    window.speechSynthesis.speak(utter);
    return true;
  }

  function mensajeErrorReconocimiento(codigo) {
    switch (codigo) {
      case 'no-speech':
        return 'No se detectó una palabra. Acércate un poco al micrófono y vuelve a intentarlo.';
      case 'audio-capture':
        return 'No se encontró un micrófono disponible. Revisa el dispositivo de entrada.';
      case 'not-allowed':
      case 'service-not-allowed':
        return 'El navegador no tiene permiso para usar el micrófono. Habilítalo y vuelve a intentarlo.';
      case 'network':
        return 'El reconocimiento de voz no pudo conectarse. Revisa la conexión e inténtalo otra vez.';
      case 'aborted':
        return 'La escucha se detuvo. Pulsa el micrófono cuando quieras volver a intentarlo.';
      default:
        return 'No se pudo reconocer la voz. Inténtalo nuevamente.';
    }
  }

  async function subirAudio(blob, config) {
    if (!blob || !blob.size) return '';
    const extension = (blob.type || '').includes('ogg') ? 'ogg' : 'webm';
    const fd = new FormData();
    fd.append('audio', blob, `${config.juego || 'articulacion'}_completo.${extension}`);
    fd.append('categoria', config.categoria || 'articulacion');
    fd.append('juego', config.juego || '');

    const response = await fetch('/juegos/evidencia-audio', { method: 'POST', body: fd });
    if (response.status === 401 || response.status === 403) {
      window.location.href = '/auth/login';
      throw new Error('sesion expirada');
    }
    if (!response.ok) throw new Error(`No se pudo subir el audio (${response.status})`);
    const data = await response.json();
    return data.audio_url || '';
  }

  function crearSesionVoz(config = {}) {
    let mediaRecorder = null;
    let stream = null;
    let chunks = [];
    let recognition = null;
    let reconocimientoEnCurso = false;
    let finalizada = false;
    let detalleFinal = { audioUrl: '', audioTranscripcion: '', requiereRevisionAudio: false };
    const transcripciones = [];

    async function iniciarOReanudarGrabacion() {
      if (!window.MediaRecorder || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        return false;
      }

      if (mediaRecorder) {
        if (mediaRecorder.state === 'paused') {
          try { mediaRecorder.resume(); } catch (_) {}
        }
        return mediaRecorder.state === 'recording';
      }

      stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          channelCount: 1,
        },
      });

      chunks = [];
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) chunks.push(event.data);
      };
      mediaRecorder.start();
      return true;
    }

    function pausarGrabacion() {
      if (mediaRecorder && mediaRecorder.state === 'recording') {
        try { mediaRecorder.requestData(); } catch (_) {}
        try { mediaRecorder.pause(); } catch (_) {}
      }
    }

    function limpiarGrabacion() {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
        stream = null;
      }
      mediaRecorder = null;
      chunks = [];
    }

    function hablar(texto, opciones = {}) {
      if (reconocimientoEnCurso) return false;
      pausarGrabacion();
      return hablarEspanol(texto, opciones);
    }

    async function reconocerPalabra({ palabraEsperada, alEscuchar, alCorrecto, alIncorrecto, alFin }) {
      if (reconocimientoEnCurso) return false;

      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) {
        if (typeof alIncorrecto === 'function') {
          alIncorrecto('Este navegador no ofrece reconocimiento de voz. Prueba con una versión reciente de Chrome o Edge.');
        }
        return false;
      }

      try {
        await iniciarOReanudarGrabacion();
      } catch (error) {
        console.warn('No se pudo iniciar la evidencia de audio:', error);
        if (error && (error.name === 'NotAllowedError' || error.name === 'SecurityError')) {
          if (typeof alIncorrecto === 'function') {
            alIncorrecto('No hay permiso para usar el micrófono. Habilítalo en el navegador y vuelve a intentarlo.');
          }
          return false;
        }
      }

      reconocimientoEnCurso = true;
      const rec = new SR();
      recognition = rec;
      rec.lang = config.idiomaReconocimiento || 'es-ES';
      rec.continuous = false;
      rec.interimResults = false;
      rec.maxAlternatives = 5;

      if (typeof alEscuchar === 'function') alEscuchar();

      rec.onresult = (event) => {
        const alternativas = obtenerAlternativasFinales(event);
        const coincidencia = alternativas.find((alt) => contienePalabraExacta(alt.transcript, palabraEsperada)) || null;
        const principal = alternativas.length ? alternativas[0].transcript : '';

        if (principal) transcripciones.push(`${palabraEsperada}:${principal}`);

        if (coincidencia) {
          if (typeof alCorrecto === 'function') alCorrecto(coincidencia);
        } else if (typeof alIncorrecto === 'function') {
          alIncorrecto(
            principal
              ? `Se escuchó: “${principal}”. Intenta otra vez diciendo la palabra completa “${String(palabraEsperada).toUpperCase()}”.`
              : `No se reconoció la palabra. Intenta otra vez diciendo “${String(palabraEsperada).toUpperCase()}”.`
          );
        }
      };

      rec.onerror = (event) => {
        if (typeof alIncorrecto === 'function') {
          alIncorrecto(mensajeErrorReconocimiento(event && event.error ? event.error : 'error'));
        }
      };

      rec.onend = () => {
        pausarGrabacion();
        reconocimientoEnCurso = false;
        recognition = null;
        if (typeof alFin === 'function') alFin();
      };

      try {
        rec.start();
        return true;
      } catch (_) {
        pausarGrabacion();
        reconocimientoEnCurso = false;
        recognition = null;
        if (typeof alIncorrecto === 'function') {
          alIncorrecto('El micrófono ya estaba ocupado. Espera un momento y vuelve a intentarlo.');
        }
        if (typeof alFin === 'function') alFin();
        return false;
      }
    }

    async function finalizar() {
      const transcripcionCompleta = transcripciones.join(' | ');
      if (finalizada) {
        return {
          ...detalleFinal,
          audioTranscripcion: transcripcionCompleta || detalleFinal.audioTranscripcion || '',
        };
      }
      finalizada = true;

      if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        detalleFinal = {
          audioUrl: '',
          audioTranscripcion: transcripcionCompleta,
          requiereRevisionAudio: !!transcripcionCompleta,
        };
        limpiarGrabacion();
        return detalleFinal;
      }

      return await new Promise((resolve) => {
        const recorder = mediaRecorder;
        recorder.onstop = async () => {
          let audioUrl = '';
          try {
            const blob = new Blob(chunks, { type: recorder.mimeType || 'audio/webm' });
            audioUrl = await subirAudio(blob, config);
          } catch (error) {
            console.warn('No se pudo subir la evidencia de audio completa:', error);
          }

          detalleFinal = {
            audioUrl,
            audioTranscripcion: transcripcionCompleta,
            requiereRevisionAudio: !!(audioUrl || transcripcionCompleta),
          };
          limpiarGrabacion();
          resolve(detalleFinal);
        };

        try { recorder.stop(); }
        catch (_) {
          limpiarGrabacion();
          resolve({
            audioUrl: '',
            audioTranscripcion: transcripcionCompleta,
            requiereRevisionAudio: !!transcripcionCompleta,
          });
        }
      });
    }

    function cancelar() {
      try {
        if (recognition) recognition.abort();
      } catch (_) {}
      recognition = null;
      reconocimientoEnCurso = false;

      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        try {
          mediaRecorder.onstop = null;
          mediaRecorder.stop();
        } catch (_) {}
      }
      limpiarGrabacion();
      try { window.speechSynthesis.cancel(); } catch (_) {}
    }

    return {
      hablar,
      reconocerPalabra,
      finalizar,
      cancelar,
      estaReconociendo: () => reconocimientoEnCurso,
      obtenerTranscripcion: () => transcripciones.join(' | '),
    };
  }

  async function guardarResultado(config = {}) {
    const fd = new FormData();
    fd.append('paciente_email', sessionStorage.getItem('paciente_email') || localStorage.getItem('paciente_email_actual') || '');
    fd.append('categoria', config.categoria || 'articulacion');
    fd.append('juego', config.juego || '');
    fd.append('paso_completado', String(config.pasoCompletado ?? 1));
    fd.append('total_pasos', String(config.totalPasos ?? 1));
    fd.append('completado', config.completado === false ? 'false' : 'true');
    fd.append('puntos', String(config.puntos ?? 0));
    fd.append('nivel', String(config.nivel ?? 1));
    fd.append('ruta', window.location.pathname || '');
    fd.append('notas', config.notas || '');
    fd.append('audio_transcripcion', config.audioTranscripcion || '');
    fd.append('audio_url', config.audioUrl || '');
    fd.append('requiere_revision_audio', config.requiereRevisionAudio ? 'true' : 'false');

    const response = await fetch('/juegos/resultado', { method: 'POST', body: fd });
    if (response.status === 401 || response.status === 403) {
      window.location.href = '/auth/login';
      throw new Error('sesion expirada');
    }
    if (!response.ok) throw new Error(`No se pudo guardar el resultado (${response.status})`);
    const data = await response.json();
    if (config.completado !== false) marcarActividadCompletada();
    return data;
  }

  function marcarActividadCompletada(ruta) {
    const actual = (ruta || window.location.pathname || '').replace(/\/+$/, '');
    let completadas = [];
    try {
      const parsed = JSON.parse(sessionStorage.getItem('actividades_hoy_completadas') || '[]');
      completadas = Array.isArray(parsed) ? parsed : [];
    } catch (_) {}
    const normalizadas = completadas.map((u) => (u || '').replace(/\/+$/, ''));
    if (!normalizadas.includes(actual)) {
      completadas.push(actual);
      sessionStorage.setItem('actividades_hoy_completadas', JSON.stringify(completadas));
      localStorage.setItem('actividades_hoy_completadas', JSON.stringify(completadas));
    }
  }

  function configurarSiguienteSeguro(boton, rutaPredeterminada) {
    if (!boton) return;
    boton.href = rutaPredeterminada;

    const modo = sessionStorage.getItem('flujo_juegos_modo') || '';
    if (modo !== 'actividades_hoy') return;

    const normalizar = (u) => (u || '').split('?')[0].split('#')[0].replace(/\/+$/, '');
    const actual = normalizar(window.location.pathname);
    let lista = [];
    let completadas = [];

    try {
      const parsed = JSON.parse(sessionStorage.getItem('actividades_hoy_urls') || '[]');
      lista = Array.isArray(parsed) ? parsed.map(normalizar) : [];
    } catch (_) {}
    try {
      const parsed = JSON.parse(sessionStorage.getItem('actividades_hoy_completadas') || '[]');
      completadas = Array.isArray(parsed) ? parsed.map(normalizar) : [];
    } catch (_) {}

    // Si el juego actual no pertenece al flujo del día, no usamos datos viejos
    // de sessionStorage para enviarlo a una pantalla inesperada.
    const idxActual = lista.indexOf(actual);
    if (idxActual < 0) return;

    const completadasSet = new Set(completadas);
    const posteriores = lista.slice(idxActual + 1).filter((u) => !completadasSet.has(u));
    const anterioresPendientes = lista.slice(0, idxActual).filter((u) => !completadasSet.has(u));
    const siguiente = posteriores[0] || anterioresPendientes[0] || '';

    if (siguiente) {
      boton.href = siguiente;
      boton.textContent = 'Siguiente actividad';
    } else {
      sessionStorage.setItem('flujo_juegos_modo', 'hub');
    }
  }

  window.FonoArticulacion = {
    normalizarTexto,
    contienePalabraExacta,
    hablarEspanol,
    crearSesionVoz,
    marcarActividadCompletada,
    configurarSiguienteSeguro,
    guardarResultado,
  };
})();
