/* FonoApp · demostración de boca y pronunciación dentro del juego.
 *
 * 1) Siempre se muestra la BOCA ANIMADA propia de la letra (app/iconos_ui.py):
 *    funciona sin Internet y enseña con movimiento qué hacer con labios y lengua.
 * 2) El video de una persona real (EducaMadrid, YouTube, Wikimedia) es OPCIONAL:
 *    solo aparece el botón «Ver video» si el servidor externo responde. Si la red
 *    no llega a ese servidor (p. ej. «No se ha podido encontrar la dirección IP
 *    de mediateca.educa.madrid.org»), el niño no ve ninguna página de error.
 */
(function () {
  'use strict';
  const YT = 'https://www.youtube-nocookie.com/embed/';
  const EDU = 'https://mediateca.educa.madrid.org/video/';
  const SONDA = {   // dirección pequeña para comprobar si el servidor responde
    youtube: 'https://www.youtube-nocookie.com/favicon.ico',
    educamadrid: 'https://mediateca.educa.madrid.org/favicon.ico',
    commons: 'https://upload.wikimedia.org/favicon.ico',
  };
  const CLIPS = {
    s: { type: 'youtube', id: 'e-oIVSyYATo', credit: 'Video seleccionado por el equipo', portrait: true },
    m: { type: 'educamadrid', id: '9dmp5ap6qkdsivev', credit: 'EducaMadrid · CC BY-NC-SA' },
    p: { type: 'educamadrid', id: 'dkrfrens7z2z4v1y', credit: 'EducaMadrid · CC BY-NC-SA' },
    rr: { type: 'commons', url: 'https://upload.wikimedia.org/wikipedia/commons/8/8b/Alveolar-trill-slomo.webm', credit: 'xyzzyva · Wikimedia Commons · CC BY-SA 4.0', end: 10 },
    a: { type: 'educamadrid', id: '9f4kvr9s2ywnvow1', credit: 'José Gabriel Moya · EducaMadrid · CC BY-NC-SA' },
    g: { type: 'educamadrid', id: 'kbabzytqljt9dpla', credit: 'Gloria Uría · EducaMadrid · Dominio público' },
    r: { type: 'educamadrid', id: 'vu6lmnzw1xjtk6kw', credit: 'EducaMadrid · Contenido público' },
    b: { type: 'educamadrid', id: 'ymmmozp9q1hxea1f', credit: 'Raquel Anego · EducaMadrid · CC BY-NC-SA' },
    c: { type: 'educamadrid', id: '3qi3ufmtjqjzty4u', credit: 'CP Santo Domingo · EducaMadrid · CC BY-NC-ND' },
    d: { type: 'educamadrid', id: 'ymmmozp9q1hxea1f', credit: 'Raquel Anego · EducaMadrid · CC BY-NC-SA' },
  };
  // Indicación corta para el adulto (el niño se guía por la animación)
  const AYUDA = {
    m: 'Labios juntos y la voz sale por la nariz: mmm.', p: 'Labios juntos y se abren con un soplo: p.',
    b: 'Labios juntos y se abren con voz: b.', s: 'Dientes juntos y el aire sale suave: sss.',
    f: 'Dientes de arriba sobre el labio de abajo y sale aire: fff.', d: 'La punta de la lengua toca detrás de los dientes de arriba: d.',
    r: 'La punta de la lengua da un toque rápido arriba: r.', rr: 'La punta de la lengua vibra muchas veces: rrr.',
    g: 'La parte de atrás de la lengua sube: g.', c: 'La parte de atrás de la lengua sube: c (ca, co, cu).',
    a: 'Boca bien abierta y voz: aaa.',
  };

  const disponibles = {};
  function servidorDisponible(tipo) {
    if (disponibles[tipo]) return disponibles[tipo];
    let guardado = null;
    try { guardado = sessionStorage.getItem('fono_srv_' + tipo); } catch (e) {}
    if (guardado) return (disponibles[tipo] = Promise.resolve(guardado === '1'));
    const control = new AbortController();
    const espera = setTimeout(() => control.abort(), 4000);
    disponibles[tipo] = fetch(SONDA[tipo], { mode: 'no-cors', cache: 'no-store', signal: control.signal })
      .then(() => true, () => false)
      .then(ok => { clearTimeout(espera); try { sessionStorage.setItem('fono_srv_' + tipo, ok ? '1' : '0'); } catch (e) {} return ok; });
    return disponibles[tipo];
  }

  function el(tag, cl, txt) { const n = document.createElement(tag); if (cl) n.className = cl; if (txt) n.textContent = txt; return n; }
  function svg(nombre, tam, extra) {
    const cuerpo = (window.FonoIconos || {})[nombre];
    if (!cuerpo) return null;
    const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    s.setAttribute('viewBox', '0 0 64 64'); s.setAttribute('width', tam); s.setAttribute('height', tam);
    s.setAttribute('class', 'fono-ico' + (extra ? ' ' + extra : '')); s.setAttribute('aria-hidden', 'true');
    s.innerHTML = cuerpo;
    return s;
  }

  function demoAnimada(letra) {
    const nombre = (window.FonoBocaDeFonema || {})[letra.toUpperCase()];
    const caja = el('div', 'fono-boca-demo');
    caja.setAttribute('role', 'img');
    caja.setAttribute('aria-label', 'Así se pone la boca para decir ' + letra.toUpperCase() + '. ' + (AYUDA[letra] || ''));
    const boca = nombre && svg(nombre, 128, 'fa-siempre');
    if (boca) caja.appendChild(boca);
    const pasos = el('div', 'fono-boca-demo-pasos animar'); pasos.setAttribute('aria-hidden', 'true');
    const paso = (ico, txt) => { const p = el('span', 'fono-boca-demo-paso'); const i = svg(ico, 40); if (i) p.appendChild(i); p.appendChild(el('small', '', txt)); return p; };
    const letraBox = el('span', 'fono-boca-demo-paso'); letraBox.appendChild(el('span', 'fono-boca-demo-letra', letra.toUpperCase())); letraBox.appendChild(el('small', '', 'Dilo'));
    pasos.append(paso('ojos', 'Mira'), el('span', 'fono-boca-demo-flecha', '›'), paso('altavoz', 'Escucha'), el('span', 'fono-boca-demo-flecha', '›'), letraBox);
    caja.appendChild(pasos);
    return caja;
  }

  function reproductor(data, letra) {
    if (data.type === 'commons') {
      const marco = el('div', 'fono-video-contenedor');
      const video = el('video', 'fono-video-humano fono-video-rr');
      video.controls = true; video.playsInline = true; video.preload = 'metadata'; video.src = data.url + '#t=0,10';
      video.setAttribute('aria-label', 'Video de la letra ' + letra.toUpperCase());
      video.addEventListener('timeupdate', () => { if (video.currentTime >= data.end) { video.pause(); video.currentTime = 0; } });
      video.addEventListener('error', () => marco.closest('.fono-real-video')?.remove());
      marco.appendChild(video);
      return marco;
    }
    const marco = el('div', 'fono-video-contenedor' + (data.portrait ? ' fono-video-vertical' : ''));
    const frame = el('iframe', 'fono-video-humano');
    frame.title = 'Video de la letra ' + letra.toUpperCase();
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    frame.setAttribute('allow', 'autoplay; encrypted-media; picture-in-picture; fullscreen');
    frame.setAttribute('allowfullscreen', '');
    frame.src = data.type === 'youtube' ? YT + data.id + '?rel=0&playsinline=1&controls=1&hl=es&autoplay=1' : EDU + data.id + '/fs';
    marco.appendChild(frame);
    return marco;
  }

  function seccionVideo(root, letra) {
    const data = CLIPS[letra];
    if (!data) return;
    const zona = el('div', 'fono-real-video');
    zona.hidden = true;   // se muestra solo si el servidor responde
    const boton = el('button', 'fono-real-replay fono-real-ver');
    boton.type = 'button';
    const cam = svg('pelicula', 22); if (cam) boton.appendChild(cam);
    boton.appendChild(document.createTextNode(' Ver video de una persona'));
    boton.addEventListener('click', () => {
      boton.remove();
      zona.appendChild(reproductor(data, letra));
      zona.appendChild(el('small', 'fono-real-credit', data.credit || ''));
    });
    zona.appendChild(boton);
    root.appendChild(zona);
    servidorDisponible(data.type).then(ok => { if (ok && zona.isConnected) zona.hidden = false; });
  }

  function pintar(root, fonema, opciones = {}) {
    if (!root) return;
    if (!window.FonoIconos && document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => pintar(root, fonema, opciones), { once: true });
      return;
    }
    const letra = String(fonema || '').toLowerCase().trim();
    root.replaceChildren();
    root.classList.add('fono-real-modelo');
    if (!opciones.soloVideo) {
      root.appendChild(el('strong', 'fono-real-titulo', 'Letra ' + letra.toUpperCase()));
      root.appendChild(demoAnimada(letra));
      if (AYUDA[letra]) root.appendChild(el('p', 'fono-real-pista', AYUDA[letra]));
    }
    seccionVideo(root, letra);
    if (opciones.soloVideo) {
      // Sin video disponible, el recuadro no se muestra vacío.
      root.hidden = true;
      servidorDisponible((CLIPS[letra] || {}).type || 'none').then(ok => { if (ok && CLIPS[letra]) root.hidden = false; });
    }
  }

  window.FonoBocaReal = { pintar, servidorDisponible };
  document.addEventListener('DOMContentLoaded', () => {
    // En las páginas de letras la boca animada ya está en el paso 1: aquí solo el video opcional.
    const yaHayDemo = !!document.querySelector('.fono-boca-demo');
    document.querySelectorAll('[data-real-fonema]').forEach(n => pintar(n, n.getAttribute('data-real-fonema'), { soloVideo: yaHayDemo }));
  });
})();
