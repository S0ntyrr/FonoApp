/* Ayudas visuales no invasivas: se añaden sin reemplazar la lógica existente.
 * Cada paso se muestra con una ilustración de app/iconos.py (window.FonoIconos,
 * servida en /juegos/iconos.js) en lugar de emojis.
 */
(()=>{
 'use strict';
 const juegos={
  'respiracion/globo':{i:'globo',nombre:'Globo',demo:'/static/img/soplo-boca.gif',pasos:[['lupa','Mira el globo.'],['soplar','Mira cómo soplar.'],['globo','Sopla suave: el globo crece.']]},
  'respiracion/molino':{i:'molino',nombre:'Molino de Pepe',demo:'/static/img/molino-demostracion.gif',pasos:[['lupa','Mira el molino.'],['molino','Mira cómo gira.'],['soplar','Sopla suave para hacerlo girar.']]},
  'fonacion/gol':{i:'gol',nombre:'¡Haz un gol!',pasos:[['gol','Mira la pelota.'],['boca_g','Di «gol» con voz suave.'],['trofeo','¡Haz que llegue a la meta!']]},
  'fonacion/escala':{i:'escala',nombre:'Escala musical',pasos:[['oreja','Escucha la nota.'],['boca_m','Haz el sonido de M como en mamá.'],['escala','Sigue la música con tu voz.']]},
  'resonancia/escaleras':{i:'escaleras',nombre:'Sube la pelota',pasos:[['oreja','Escucha el sonido.'],['boca_m','Haz el sonido de M como en mamá.'],['escaleras','Mira cómo sube la pelota.']]},
  'articulacion/letra-b':{i:'letra_b',nombre:'Letra B',pasos:[['boca_b','Mira los labios.'],['oreja','Escucha el sonido «b».'],['letra_b','Di «b» y después «abeja».']]},
  'articulacion/letra-d':{i:'letra_d',nombre:'Letra D',pasos:[['boca_d','Mira cómo se mueve la lengua.'],['oreja','Escucha el sonido «d».'],['letra_d','Di «d» y después «dado».']]},
  'articulacion/letra-f':{i:'letra_f',nombre:'Letra F',pasos:[['boca_f','Mira cómo se hace «f».'],['oreja','Escucha el sonido.'],['letra_f','Di «f» y después «foca».']]},
  'articulacion/letra-r':{i:'letra_r',nombre:'Letra R',pasos:[['boca_r','Mira la lengua.'],['oreja','Escucha la «r».'],['letra_r','Di «rana» como puedas.']]},
  'articulacion/completa-palabra':{i:'lapiz',nombre:'Completa palabras',pasos:[['lupa','Mira el dibujo.'],['oreja','Escucha la palabra.'],['lapiz','Completa y di la palabra.']]},
  'articulacion/moto-voz':{i:'moto',nombre:'Acelera la moto',pasos:[['lupa','Mira el dibujo.'],['oreja','Escucha la palabra.'],['moto','Dila y mueve la moto.']]},
  'prosodia/adivina-animal':{i:'huella',nombre:'Adivina el animal',pasos:[['oreja','Escucha el sonido.'],['huella','Mira los animales.'],['arrastrar','Toca el animal que suena.']]},
  'prosodia/trabalenguas':{i:'lengua',nombre:'Trabalenguas',pasos:[['oreja','Escucha despacio.'],['boca','Repite a tu ritmo.'],['estrella','¡Intenta otra vez!']]},
  'prosodia/adivinanza-imagen':{i:'pregunta',nombre:'Adivina con dibujos',pasos:[['oreja','Escucha una pista.'],['lupa','Mira los dibujos.'],['arrastrar','Elige el que va con la pista.']]},
  'prosodia/completa-cancion':{i:'notas',nombre:'Completa la canción',pasos:[['oreja','Escucha la canción.'],['notas','Sigue el ritmo.'],['microfono','Completa cantando.']]},
  'discriminacion/sonidos-animales':{i:'perro',nombre:'Animales',pasos:[['oreja','Escucha el sonido.'],['perro','Mira los animales.'],['arrastrar','Toca el que escuchaste.']]},
  'discriminacion/sonidos-objetos':{i:'campana',nombre:'Objetos',pasos:[['oreja','Escucha un objeto.'],['lupa','Mira los dibujos.'],['arrastrar','Elige el que suena.']]},
  'discriminacion/arrastra-sonido':{i:'arrastrar',nombre:'Une el sonido',pasos:[['oreja','Escucha.'],['lupa','Encuentra su dibujo.'],['arrastrar','Une los que van juntos.']]},
  'practica/rompecabezas':{i:'rompecabezas',nombre:'Rompecabezas',pasos:[['lupa','Mira la imagen.'],['rompecabezas','Mueve una pieza.'],['estrella','¡Completa la figura!']]},
  'practica/cara':{i:'cara',nombre:'Crea tu personaje',pasos:[['lupa','Mira la cara.'],['cara','Elige ojos, nariz y boca.'],['estrella','Arma tu personaje.']]},
  'practica/asociacion':{i:'asociar',nombre:'Asociación',pasos:[['lupa','Mira los dibujos.'],['asociar','Encuentra los que van juntos.'],['arrastrar','Únelos.']]}
 };
 const match=location.pathname.match(/^\/juegos\/([^/]+\/[^/]+)\/?$/);
 if(!match||!juegos[match[1]])return;
 const item=juegos[match[1]];
 const svg=(nombre,tam)=>{
  const cuerpo=(window.FonoIconos||{})[nombre];
  return cuerpo?`<svg class="fono-ico${nombre.startsWith('boca_')?' fa-siempre':''}" viewBox="0 0 64 64" width="${tam}" height="${tam}" aria-hidden="true" focusable="false">${cuerpo}</svg>`:'';
 };
 document.addEventListener('DOMContentLoaded',()=>{
  const main=document.querySelector('.contenedor-principal > section, .contenedor-principal > main');if(!main)return;
  if(main.querySelector('.fono-guias-visuales'))return;
  const card=document.createElement('section');card.className='fono-guias-visuales animar';card.setAttribute('aria-label','Tutorial visual');
  const summary=document.createElement('div');summary.className='fono-guias-head';
  const t=document.createElement('div');t.innerHTML='<span class="fono-guias-chip">EJEMPLO CON DIBUJOS</span><h2>¿Cómo jugamos?</h2>';
  const show=document.createElement('button');show.type='button';show.className='fono-guias-toggle';show.setAttribute('aria-expanded','false');show.textContent='▶ Ver ejemplo';summary.append(t,show);card.append(summary);
  const body=document.createElement('div');body.className='fono-guias-body';body.hidden=true;
  const visual=document.createElement('div');visual.className='fono-guias-visual';
  const demo=document.createElement('div');demo.className='fono-guias-imagen';
  if(item.demo){const img=document.createElement('img');img.loading='lazy';img.src=item.demo;img.alt='Demostración visual del movimiento';demo.append(img);}else demo.innerHTML=svg(item.i,120);
  const label=document.createElement('strong');label.className='fono-guias-frase';
  label.style.cssText='display:flex;align-items:center;justify-content:center;gap:10px';
  visual.append(demo,label);
  const nav=document.createElement('div');nav.className='fono-guias-botones';
  const back=document.createElement('button');back.type='button';back.textContent='← Antes';
  const sound=document.createElement('button');sound.type='button';sound.innerHTML=svg('altavoz',20)+' Escuchar ejemplo';
  sound.style.cssText='display:inline-flex;align-items:center;gap:6px';
  const next=document.createElement('button');next.type='button';next.textContent='Siguiente →';
  const count=document.createElement('div');count.className='fono-guias-contador';nav.append(back,sound,next);body.append(visual,count,nav);card.append(body);
  let slide=0;
  const paint=()=>{
   const [ico,txt]=item.pasos[slide];
   // Con GIF: el dibujo del paso va junto al texto. Sin GIF: la caja grande muestra el paso.
   if(item.demo){label.innerHTML=svg(ico,56);label.append(document.createTextNode(txt));}
   else{demo.innerHTML=svg(ico,120);label.textContent=txt;}
   count.textContent=`Paso ${slide+1} de ${item.pasos.length}`;back.disabled=slide===0;
   next.textContent=slide===item.pasos.length-1?'↻ Repetir':'Siguiente →';
  };
  back.addEventListener('click',()=>{slide=Math.max(0,slide-1);paint()});
  next.addEventListener('click',()=>{slide=(slide+1)%item.pasos.length;paint()});
  sound.addEventListener('click',()=>{window.FonoVoz?.hablar(item.pasos[slide][1]);});
  show.addEventListener('click',()=>{body.hidden=!body.hidden;show.textContent=body.hidden?'▶ Ver ejemplo':'▲ Ocultar ejemplo';show.setAttribute('aria-expanded',String(!body.hidden));if(!body.hidden)paint();});
  main.insertBefore(card,main.firstChild);paint();
 });
})();
