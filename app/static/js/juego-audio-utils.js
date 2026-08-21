// Utilidades de audio compartidas para páginas de juegos standalone
// (no extienden base.html), replicando las funciones equivalentes de base.html
// para que el sonido de éxito y la captura real de evidencia de audio funcionen.
(function () {
    if (window.crearContextoAudioFono) return; // Evita redefinir si ya existe (ej. base.html)

    const FONOAPP_VOLUME_KEY = 'fonoapp_master_volume';

    function obtenerVolumenFono() {
        const guardado = parseFloat(localStorage.getItem(FONOAPP_VOLUME_KEY) || '0.7');
        if (Number.isNaN(guardado)) return 0.7;
        return Math.max(0, Math.min(1, guardado));
    }

    window.crearContextoAudioFono = function crearContextoAudioFono() {
        const Ctx = window.AudioContext || window.webkitAudioContext;
        if (!Ctx) return null;
        return new Ctx();
    };

    window.crearTonoFono = function crearTonoFono(ctx, opciones) {
        if (!ctx) return null;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const inicio = opciones.startTime ?? ctx.currentTime;
        const duracion = opciones.duration ?? 0.5;
        const volumen = Math.max(0.0001, (opciones.volumeBase ?? 0.3) * obtenerVolumenFono());
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.frequency.value = opciones.frequency ?? 440;
        osc.type = opciones.type || 'sine';
        gain.gain.setValueAtTime(volumen, inicio);
        gain.gain.exponentialRampToValueAtTime(0.001, inicio + duracion);
        osc.start(inicio);
        osc.stop(inicio + duracion);
        return { osc, gain };
    };

    async function subirEvidenciaAudio(blob, categoria, juego) {
        if (!blob || !blob.size) return '';
        const formData = new FormData();
        const extension = (blob.type || '').includes('ogg') ? 'ogg' : 'webm';
        formData.append('audio', blob, `${juego || 'actividad'}.${extension}`);
        formData.append('categoria', categoria || '');
        formData.append('juego', juego || '');
        const response = await fetch('/juegos/evidencia-audio', { method: 'POST', body: formData });
        if (!response.ok) throw new Error('No se pudo subir la evidencia de audio');
        const data = await response.json();
        return data.audio_url || '';
    }

    window.crearCapturaActividad = function crearCapturaActividad(config) {
        let mediaRecorder = null;
        let stream = null;
        let chunks = [];
        let ultimoDetalle = {};

        async function iniciar() {
            if (!window.MediaRecorder || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                return false;
            }
            if (mediaRecorder && mediaRecorder.state === 'recording') return true;
            chunks = [];
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) chunks.push(event.data);
            };
            mediaRecorder.start();
            return true;
        }

        async function detener(meta) {
            const extras = meta || {};
            if (!mediaRecorder || mediaRecorder.state === 'inactive') {
                ultimoDetalle = {
                    ...ultimoDetalle,
                    audioTranscripcion: extras.transcripcion || ultimoDetalle.audioTranscripcion || '',
                    requiereRevisionAudio: !!(ultimoDetalle.audioUrl || extras.transcripcion),
                };
                return ultimoDetalle;
            }
            return await new Promise((resolve) => {
                const recorder = mediaRecorder;
                recorder.onstop = async () => {
                    let audioUrl = '';
                    try {
                        const blob = new Blob(chunks, { type: recorder.mimeType || 'audio/webm' });
                        audioUrl = await subirEvidenciaAudio(blob, config.categoria, config.juego);
                    } catch (e) {
                        console.warn('No se pudo subir la evidencia de audio:', e);
                    }
                    if (stream) {
                        stream.getTracks().forEach((track) => track.stop());
                        stream = null;
                    }
                    mediaRecorder = null;
                    chunks = [];
                    ultimoDetalle = {
                        audioUrl,
                        audioTranscripcion: extras.transcripcion || '',
                        requiereRevisionAudio: !!(audioUrl || extras.transcripcion),
                    };
                    resolve(ultimoDetalle);
                };
                recorder.stop();
            });
        }

        function obtenerDetalle(meta) {
            const extras = meta || {};
            return {
                audioUrl: ultimoDetalle.audioUrl || '',
                audioTranscripcion: extras.transcripcion || ultimoDetalle.audioTranscripcion || '',
                requiereRevisionAudio: !!(ultimoDetalle.audioUrl || ultimoDetalle.audioTranscripcion || extras.transcripcion),
            };
        }

        function limpiar() {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                try { mediaRecorder.stop(); } catch (e) {}
            }
            if (stream) {
                stream.getTracks().forEach((track) => track.stop());
                stream = null;
            }
            mediaRecorder = null;
            chunks = [];
        }

        return { iniciar, detener, obtenerDetalle, limpiar };
    };
})();
