/* Ayudas visuales no invasivas: se añaden sin reemplazar la lógica existente. */
(()=>{
 'use strict';
 const juegos={
  'respiracion/globo':{e:'🎈',nombre:'Globo',demo:'/static/img/soplo-boca.gif',pasos:[['👀','Mira el globo.'],['👄','Mira cómo soplar.'],['🎈','Sopla suave: el globo crece.']]},
  'respiracion/molino':{e:'🌬️',nombre:'Molino de Pepe',demo:'/static/img/molino-demostracion.gif',pasos:[['👀','Mira el molino.'],['🌀','Mira cómo gira.'],['👄','Sopla suave para hacerlo girar.']]},
  'fonacion/gol':{e:'⚽',nombre:'¡Haz un gol!',pasos:[['⚽','Mira la pelota.'],['🎤','Di «gol» con voz suave.'],['🥅','¡Haz que llegue a la meta!']]},
  'fonacion/escala':{e:'🎶',nombre:'Escala musical',pasos:[['👂','Escucha la nota.'],['🎵','Haz el sonido de M como en mamá.'],['🌈','Sigue la música con tu voz.']]},
  'resonancia/escaleras':{e:'⚽',nombre:'Sube la pelota',pasos:[['👂','Escucha el sonido.'],['👄','Haz el sonido de M como en mamá.'],['⚽','Mira cómo sube la pelota.']]},
  'articulacion/letra-b':{e:'🐝',nombre:'Letra B',pasos:[['👄','Mira los labios.'],['👂','Escucha el sonido «b».'],['🐝','Di «b» y después «abeja».']]},
  'articulacion/letra-d':{e:'🎲',nombre:'Letra D',pasos:[['👄','Mira cómo se mueve la boca.'],['👂','Escucha el sonido «d».'],['🎲','Di «d» y después «dado».']]},
  'articulacion/letra-f':{e:'🦭',nombre:'Letra F',pasos:[['👄','Mira cómo se hace «f».'],['👂','Escucha el sonido.'],['🦭','Di «f» y después «foca».']]},
  'articulacion/letra-r':{e:'🐸',nombre:'Letra R',pasos:[['👄','Mira la lengua.'],['👂','Escucha la «r».'],['🐸','Di «rana» como puedas.']]},
  'articulacion/completa-palabra':{e:'🔤',nombre:'Completa palabras',pasos:[['👀','Mira el dibujo.'],['👂','Escucha la palabra.'],['🔤','Completa y di la palabra.']]},
  'articulacion/moto-voz':{e:'🏍️',nombre:'Acelera la moto',pasos:[['🖼️','Mira el dibujo.'],['👂','Escucha la palabra.'],['🏍️','Dila y mueve la moto.']]},
  'prosodia/adivina-animal':{e:'🐱',nombre:'Adivina el animal',pasos:[['👂','Escucha el sonido.'],['🐱','Mira los animales.'],['👆','Toca el animal que suena.']]},
  'prosodia/trabalenguas':{e:'👅',nombre:'Trabalenguas',pasos:[['👂','Escucha despacio.'],['👄','Repite a tu ritmo.'],['⭐','¡Intenta otra vez!']]},
  'prosodia/adivinanza-imagen':{e:'🧩',nombre:'Adivina con dibujos',pasos:[['👂','Escucha una pista.'],['🖼️','Mira los dibujos.'],['👆','Elige el que va con la pista.']]},
  'prosodia/completa-cancion':{e:'🎶',nombre:'Completa la canción',pasos:[['👂','Escucha la canción.'],['🎵','Sigue el ritmo.'],['🎤','Completa cantando.']]},
  'discriminacion/sonidos-animales':{e:'🐮',nombre:'Animales',pasos:[['👂','Escucha el sonido.'],['🐾','Mira los animales.'],['👆','Toca el que escuchaste.']]},
  'discriminacion/sonidos-objetos':{e:'🔔',nombre:'Objetos',pasos:[['👂','Escucha un objeto.'],['🖼️','Mira los dibujos.'],['👆','Elige el que suena.']]},
  'discriminacion/arrastra-sonido':{e:'🧲',nombre:'Une el sonido',pasos:[['👂','Escucha.'],['👀','Encuentra su dibujo.'],['👆','Une los que van juntos.']]},
  'practica/rompecabezas':{e:'🧩',nombre:'Rompecabezas',pasos:[['🖼️','Mira la imagen.'],['🧩','Mueve una pieza.'],['⭐','¡Completa la figura!']]},
  'practica/cara':{e:'😊',nombre:'Crea tu personaje',pasos:[['👀','Mira la cara.'],['👃','Elige ojos, nariz y boca.'],['😊','Arma tu personaje.']]},
  'practica/asociacion':{e:'🎯',nombre:'Asociación',pasos:[['👀','Mira los dibujos.'],['🧠','Encuentra los que van juntos.'],['👆','Únelos.']]}
 };
 const match=location.pathname.match(/^\/juegos\/([^/]+\/[^/]+)\/?$/);
 if(!match||!juegos[match[1]])return;
 const item=juegos[match[1]];
 document.addEventListener('DOMContentLoaded',()=>{
  const main=document.querySelector('.contenedor-principal > section, .contenedor-principal > main');if(!main)return;
  if(main.querySelector('.fono-guias-visuales'))return;
  const card=document.createElement('section');card.className='fono-guias-visuales';card.setAttribute('aria-label','Tutorial visual');
  const summary=document.createElement('div');summary.className='fono-guias-head';
  const t=document.createElement('div');t.innerHTML='<span class="fono-guias-chip">👀 EJEMPLO CON DIBUJOS</span><h2>¿Cómo jugamos?</h2>';
  const show=document.createElement('button');show.type='button';show.className='fono-guias-toggle';show.setAttribute('aria-expanded','false');show.textContent='▶ Ver ejemplo';summary.append(t,show);card.append(summary);
  const body=document.createElement('div');body.className='fono-guias-body';body.hidden=true;
  const visual=document.createElement('div');visual.className='fono-guias-visual';
  const demo=document.createElement('div');demo.className='fono-guias-imagen';
  if(item.demo){const img=document.createElement('img');img.loading='lazy';img.src=item.demo;img.alt='Demostración visual del movimiento';demo.append(img);}else demo.textContent=item.e;
  const label=document.createElement('strong');label.className='fono-guias-frase';visual.append(demo,label);
  const nav=document.createElement('div');nav.className='fono-guias-botones';
  const back=document.createElement('button');back.type='button';back.textContent='← Antes';
  const sound=document.createElement('button');sound.type='button';sound.textContent='🔊 Escuchar ejemplo';
  const next=document.createElement('button');next.type='button';next.textContent='Siguiente →';
  const count=document.createElement('div');count.className='fono-guias-contador';nav.append(back,sound,next);body.append(visual,count,nav);card.append(body);
  let slide=0;
  const paint=()=>{label.textContent=item.pasos[slide][0]+' '+item.pasos[slide][1];count.textContent=`Paso ${slide+1} de ${item.pasos.length}`;back.disabled=slide===0;next.textContent=slide===item.pasos.length-1?'↻ Repetir':'Siguiente →';};
  back.addEventListener('click',()=>{slide=Math.max(0,slide-1);paint()});
  next.addEventListener('click',()=>{slide=(slide+1)%item.pasos.length;paint()});
  sound.addEventListener('click',()=>{window.FonoVoz?.hablar(item.pasos[slide][1]);});
  show.addEventListener('click',()=>{body.hidden=!body.hidden;show.textContent=body.hidden?'▶ Ver ejemplo':'▲ Ocultar ejemplo';show.setAttribute('aria-expanded',String(!body.hidden));if(!body.hidden)paint();});
  main.insertBefore(card,main.firstChild);paint();
 });
})();
