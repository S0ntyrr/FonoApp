/* Grabación complementaria OPCIONAL: no sustituye las capturas ya existentes.
   Cada prueba genera su audio propio; nunca se publica ni se comparte entre pacientes.
   Para los juegos sin micrófono, el paciente puede pulsar "Grabar intento".
*/
(function () {
  'use strict';
  let recorder = null, stream = null, chunks = [], inicioPromesa = null;
  let ultimoAudioUrl = '';
  let audiosPendientes = [];
  let status = 'Sin grabar';
  const detalle = () => document.getElementById('fono-evidencia-estado');
  const pintar = (texto) => { status = texto; if (detalle()) detalle().textContent = texto; };
  function rolPaciente() { return window.FONOAPP_ES_PACIENTE === true; }
  async function iniciar() {
    if (!rolPaciente()) return false;
    if (recorder && recorder.state === 'recording') return true;
    if (inicioPromesa) return inicioPromesa;
    inicioPromesa = (async () => {
      if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
        pintar('Este navegador no permite grabar audio'); return false;
      }
      try {
        stream = await navigator.mediaDevices.getUserMedia({audio: true});
        chunks = [];
        recorder = new MediaRecorder(stream);
        recorder.ondataavailable = e => { if (e.data?.size) chunks.push(e.data); };
        recorder.start(700);
        pintar('🔴 Grabando intento...');
        return true;
      } catch (error) {
        pintar('Micrófono no disponible. Actívalo en permisos.');
        return false;
      }
    })();
    try { return await inicioPromesa; } finally { inicioPromesa = null; }
  }
  async function finalizar() {
    if (inicioPromesa) await inicioPromesa;
    if (!recorder || recorder.state !== 'recording') return '';
    const actual = recorder;
    return new Promise(resolve => {
      actual.onstop = async () => {
        let url = '';
        try {
          const blob = new Blob(chunks, {type: actual.mimeType || 'audio/webm'});
          if (blob.size && blob.size <= 4 * 1024 * 1024) {
            const fd = new FormData();
            const extension = blob.type.includes('ogg') ? 'ogg' : (blob.type.includes('mp4') ? 'm4a' : 'webm');
            fd.append('audio', blob, 'intento.' + extension);
            fd.append('categoria', location.pathname.split('/')[2] || '');
            fd.append('juego', location.pathname.split('/')[3] || '');
            const r = await fetch('/juegos/evidencia-audio', {method:'POST',body:fd});
            if (!r.ok) throw new Error('Error al subir audio: ' + r.status);
            url = (await r.json()).audio_url || '';
          } else if (blob.size) {
            pintar('Grabación mayor de 4 MB; intenta una prueba más corta.');
          }
        } catch (e) { console.warn('Audio no guardado', e); pintar('Error guardando audio'); }
        stream?.getTracks().forEach(t => t.stop());
        recorder = null; stream = null; chunks = [];
        if (url) { ultimoAudioUrl = url; if (!audiosPendientes.includes(url)) audiosPendientes.push(url); }
        pintar(url ? '✅ Audio guardado' : '⚠️ No hay audio guardado');
        resolve(url);
      };
      actual.stop();
    });
  }
  async function enriquecer(fd) {
    const tarea = new URLSearchParams(location.search).get('tarea_id') || '';
    fd.set('tarea_id', tarea);
    const audioNativo = fd.get('audio_url') || '';
    await finalizar();
    // Guardar TODOS los clips de esta prueba. Los juegos antiguos conservan
    // su audio nativo; los complementarios quedan asociados al mismo intento.
    const disponibles = [...new Set(audiosPendientes)];
    if (!audioNativo && disponibles.length) {
      fd.set('audio_url', disponibles.shift());
    }
    fd.set('audios_extra_json', JSON.stringify(disponibles.filter(u => u !== audioNativo)));
    if (audioNativo || audiosPendientes.length) fd.set('requiere_revision_audio', 'true');
  }
  function confirmado(){
    ultimoAudioUrl='';audiosPendientes=[];
    pintar('✅ Audios guardados en la prueba');
  }
  window.FonoEvidencia = { iniciar, finalizar, enriquecer, confirmado };
  document.addEventListener('DOMContentLoaded', () => {
    if (!rolPaciente()) return;
    const partes = location.pathname.split('/').filter(Boolean);
    if (partes[0] !== 'juegos' || partes.length < 3) return;
    const caja = document.createElement('aside');
    caja.className = 'fono-evidencia-widget';
    caja.innerHTML = '<button type="button" id="fono-evidencia-iniciar" aria-label="Grabar la voz de esta prueba">🎙️ Grabar voz</button>' +
      '<button type="button" id="fono-evidencia-detener" aria-label="Detener y guardar audio" hidden>⏹️ Guardar audio</button>' +
      '<small id="fono-evidencia-estado" role="status">Toca grabar para guardar tu voz</small>';
    document.body.appendChild(caja);
    const btnIniciar = caja.querySelector('#fono-evidencia-iniciar');
    const btnDetener = caja.querySelector('#fono-evidencia-detener');
    btnIniciar.addEventListener('click', async () => {
      if (await iniciar()) { btnIniciar.hidden = true; btnDetener.hidden = false; }
    });
    btnDetener.addEventListener('click', async () => {
      await finalizar(); btnIniciar.hidden = false; btnDetener.hidden = true;
    });
    pintar(status);
    window.addEventListener('pagehide', () => {
      if (recorder?.state === 'recording') {
        // Al cerrar la página no se puede garantizar subida: detener pistas de inmediato.
        try { recorder.onstop = null; recorder.stop(); } catch (_) {}
        stream?.getTracks().forEach(t => t.stop());
      }
    });
  });
})();
