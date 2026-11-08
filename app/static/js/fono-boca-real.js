/* FonoApp · demostraciones de boca y pronunciación dentro del juego.
 * G/R/A/B/C/D: fuentes públicas de EducaMadrid, enlazadas por reproductor
 * oficial (/fs), con demostración alternativa y sin abrir nuevas pestañas.
 * S: video corto elegido por el usuario; M/P y RR se conservan.
 * Recursos de terceros: no son ficheros descargados y requieren Internet.
 */
(function(){
 'use strict';
 const YT='https://www.youtube-nocookie.com/embed/';
 const EDU='https://mediateca.educa.madrid.org/video/';
 const CLIPS={
   s:{type:'youtube',id:'e-oIVSyYATo',title:'S · Pronunciación',credit:'Video seleccionado por el equipo',portrait:true},
   m:{type:'educamadrid',id:'9dmp5ap6qkdsivev',title:'M · Pronunciación',credit:'EducaMadrid · CC BY-NC-SA'},
   p:{type:'educamadrid',id:'dkrfrens7z2z4v1y',title:'P · Pronunciación',credit:'EducaMadrid · CC BY-NC-SA'},
   rr:{type:'commons',url:'https://upload.wikimedia.org/wikipedia/commons/8/8b/Alveolar-trill-slomo.webm',title:'RR · Vibración de lengua',credit:'xyzzyva · Wikimedia Commons · CC BY-SA 4.0',start:0,end:10},
   a:{type:'educamadrid',id:'9f4kvr9s2ywnvow1',title:'A · Pronunciación',credit:'José Gabriel Moya · EducaMadrid · CC BY-NC-SA',hint:'La A aparece durante los primeros 25 segundos.',alternate:{id:'qbobpyobjnrp6h6h',credit:'CP Santo Domingo · EducaMadrid · CC BY-SA',hint:'La A aparece al comienzo del video.'}},
   g:{type:'educamadrid',id:'kbabzytqljt9dpla',title:'G · Pronunciación',credit:'Gloria Uría · EducaMadrid · Dominio público',hint:'La explicación de la G comienza hacia los 32 segundos.',alternate:{id:'qbobpyobjnrp6h6h',credit:'CP Santo Domingo · EducaMadrid · CC BY-SA',hint:'La G aparece alrededor del minuto 1:09.'}},
   r:{type:'educamadrid',id:'vu6lmnzw1xjtk6kw',title:'R · Sonidos suave y fuerte',credit:'EducaMadrid · Contenido público',hint:'Escucha los dos sonidos de R desde el segundo 16.',alternate:{id:'a2oq5uph7bcogu3h',credit:'Andrea F. · EducaMadrid · CC BY',hint:'La R suave aparece hacia 1:16 y la fuerte hacia 1:20.'}},
   b:{type:'educamadrid',id:'ymmmozp9q1hxea1f',title:'B · Gesto y sonido',credit:'Raquel Anego · EducaMadrid · CC BY-NC-SA',hint:'La B es el primer gesto.',alternate:{id:'qbobpyobjnrp6h6h',credit:'CP Santo Domingo · EducaMadrid · CC BY-SA',hint:'La B aparece hacia 1:46.'}},
   c:{type:'educamadrid',id:'3qi3ufmtjqjzty4u',title:'C · Sonidos de la letra C',credit:'CP Santo Domingo · EducaMadrid · CC BY-NC-ND',hint:'Este video explica los distintos sonidos de C.',alternate:{id:'a2oq5uph7bcogu3h',credit:'Andrea F. · EducaMadrid · CC BY',hint:'El gesto de C aparece hacia 1:28.'}},
   d:{type:'educamadrid',id:'ymmmozp9q1hxea1f',title:'D · Gesto y sonido',credit:'Raquel Anego · EducaMadrid · CC BY-NC-SA',hint:'El gesto de D aparece después de B y C.',alternate:{id:'qbobpyobjnrp6h6h',credit:'CP Santo Domingo · EducaMadrid · CC BY-SA',hint:'La D aparece hacia 2:03.'}}
 };
 const GIFS={f:'/static/img/bocas/fonema-f.gif'};
 const OTHER_FALLBACK={
   a:'/static/img/bocas/fonema-m.gif',g:'/static/img/bocas/fonema-g.gif',
   r:'/static/img/bocas/fonema-r.gif',b:'/static/img/bocas/fonema-b.gif',
   c:'/static/img/bocas/fonema-d.gif',d:'/static/img/bocas/fonema-d.gif'
 };
 const shortNotes={a:'Abre la boca y haz A.',g:'Haz GA, GO, GU.',r:'Haz R suave, no RR fuerte.',b:'Junta los labios y haz B.',c:'Escucha CA, CO, CU o CE, CI.',d:'Pon la lengua cerca de los dientes y haz D.'};
 function el(tag,cl,txt){const n=document.createElement(tag);if(cl)n.className=cl;if(txt)n.textContent=txt;return n;}
 function srcFor(x){return x.type==='youtube'
   ?YT+x.id+'?rel=0&playsinline=1&controls=1&hl=es'
   :EDU+x.id+'/fs';}
 function addFallback(root,letter){
   const img=el('img','fono-real-imagen');
   // Una alternativa ilustrada, expresamente identificada como ilustración,
   // nunca como video humano de una letra diferente.
   img.src=OTHER_FALLBACK[letter]||GIFS[letter]||'/static/img/soplo-boca.gif';
   img.alt='Ilustración de la boca para observar un gesto.';
   img.loading='lazy';img.width=180;img.height=180;
   root.appendChild(img);
   root.appendChild(el('p','fono-real-leyenda','Ilustración de apoyo. Escucha la letra y luego intenta pronunciarla.'));
 }
 function pintar(root,fonema){
   if(!root)return;
   const letter=String(fonema||'').toLowerCase().trim();
   const data=CLIPS[letter];
   root.replaceChildren();root.classList.add('fono-real-modelo');
   root.appendChild(el('strong','fono-real-titulo','👄 Letra '+letter.toUpperCase()));
   if(!data){addFallback(root,letter);return;}
   if(data.type==='commons'){
     const frame=el('div','fono-video-contenedor');
     const video=el('video','fono-video-humano fono-video-rr');
     video.controls=true;video.playsInline=true;video.preload='metadata';
     video.src=data.url+'#t=0,10';video.setAttribute('aria-label',data.title);
     video.addEventListener('timeupdate',()=>{if(video.currentTime>=data.end){video.pause();video.currentTime=0;}});
     frame.appendChild(video);root.appendChild(frame);
     root.appendChild(el('p','fono-real-leyenda','Toca ▶ y mira la lengua vibrando durante 10 segundos.'));
   } else {
     const frame=el('div','fono-video-contenedor'+(data.portrait?' fono-video-vertical':''));
     const player=el('iframe','fono-video-humano');
     player.title='Demostración de la letra '+letter.toUpperCase();
     player.loading='lazy';player.referrerPolicy='strict-origin-when-cross-origin';
     player.setAttribute('allow','autoplay; encrypted-media; picture-in-picture; fullscreen');
     player.setAttribute('allowfullscreen','');
     player.setAttribute('scrolling','no');
     let current=data;
     const tip=el('p','fono-real-leyenda',data.hint||'Toca ▶, mira la boca e imita.');
     const credit=el('small','fono-real-credit',data.credit||'');
     const render=()=>{
       player.src=srcFor(current);
       tip.textContent=current.hint||'Toca ▶, mira la boca e imita.';
       credit.textContent=current.credit||'';
     };
     render();frame.appendChild(player);root.appendChild(frame);
     root.appendChild(tip);
     if(shortNotes[letter])root.appendChild(el('p','fono-real-pista',shortNotes[letter]));
     root.appendChild(credit);
     if(data.alternate){
       const change=el('button','fono-real-replay','↻ Probar otra demostración');change.type='button';
       let other=false;
       change.addEventListener('click',()=>{
         other=!other;
         current=other?Object.assign({type:'educamadrid'},data.alternate):data;
         render();change.textContent=other?'↻ Volver a la primera demostración':'↻ Probar otra demostración';
       });
       root.appendChild(change);
     }else if(data.type==='youtube'){
       const repeat=el('button','fono-real-replay','↻ Ver otra vez');repeat.type='button';
       repeat.addEventListener('click',()=>{player.src=srcFor(data);});
       root.appendChild(repeat);
     }
   }
 }
 window.FonoBocaReal={pintar};
 document.addEventListener('DOMContentLoaded',()=>{
   document.querySelectorAll('[data-real-fonema]').forEach(n=>pintar(n,n.getAttribute('data-real-fonema')));
 });
})();
