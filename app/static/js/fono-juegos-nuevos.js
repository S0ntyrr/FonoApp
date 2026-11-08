/* Mini-juegos visuales con instrucciones simples para niños. */
window.FonoJuegosNuevos = (function(){
 'use strict';
 const DATA = {
   M:[['🍎','manzana'],['🦋','mariposa'],['🖐️','mano'],['🏍️','moto'],['🗺️','mapa']],
   P:[['🍐','pera'],['🦆','pato'],['🍞','pan'],['🥔','papa'],['🐟','pez']],
   S:[['☀️','sol'],['🐸','sapo'],['🍲','sopa'],['🪑','silla'],['🧂','sal']],
   G:[['🐈','gato'],['🎈','globo'],['🦍','gorila'],['🐔','gallo'],['🍪','galleta']],
   R:[['🐭','ratón'],['🌹','rosa'],['🤖','robot'],['🍐','pera'],['🦜','loro']],
   RR:[['🐕','perro'],['🚗','carro'],['🛤️','ferrocarril'],['🫙','tarro'],['🧢','gorra']]
 };
 const ABC=[['✈️','avión','A'],['⚽','balón','B'],['🏠','casa','C'],['🎲','dado','D']];
 const IMITAR=[['🐮','vaca','muuu'],['🐈','gato','miau'],['🐕','perro','guau'],['⏰','reloj','tic tac'],['🚂','tren','chu chu']];
 const PRAXIAS=[
   {kind:'move',shape:'sonrisa',emoji:'😁',child:'Sonríe como yo.',adult:'Sonríe suavemente y muestra cómo estirar los labios hacia ambos lados.'},
   {kind:'move',shape:'lengua',emoji:'👅',child:'Saca la lengua.',adult:'Saca un poquito la lengua y vuelve a guardarla, con calma.'},
   {kind:'move',shape:'pico',emoji:'💋',child:'Haz una boquita de beso.',adult:'Junta y redondea los labios sin esfuerzo.'},
   {kind:'move',shape:'inflar',emoji:'🐡',child:'Infla los cachetes.',adult:'Infla las mejillas un momento y suelta el aire con calma.'},
   {kind:'move',shape:'soplar',emoji:'💨',child:'Sopla como el viento.',adult:'Sopla suavemente, sin hacerlo hasta marearse.'},
   {kind:'move',shape:'abrir',emoji:'😮',child:'Abre la boca grande.',adult:'Abre y cierra la boca lentamente, sin forzar la mandíbula.'},
   {kind:'letter',letter:'M',voice:'ma',child:'Di M.',adult:'Imita el sonido M con labios juntos.'},
   {kind:'letter',letter:'P',voice:'pa',child:'Di P.',adult:'Cierra y abre los labios con un soplo corto.'},
   {kind:'letter',letter:'S',voice:'sa',child:'Di S.',adult:'Deja salir el aire suavemente.'},
   {kind:'letter',letter:'G',voice:'ga',child:'Di G.',adult:'Haz el sonido en la parte de atrás de la boca.'},
   {kind:'letter',letter:'R',voice:'ra',child:'Di R.',adult:'Toque corto de la lengua.'},
   {kind:'letter',letter:'RR',voice:'carro',child:'Di RR.',adult:'Sonido vibrante de lengua.'},
   {kind:'letter',letter:'A',voice:'a',child:'Di A.',adult:'Abre la boca para decir A.'},
   {kind:'letter',letter:'B',voice:'ba',child:'Di B.',adult:'Cierra y abre los labios.'},
   {kind:'letter',letter:'C',voice:'ca',child:'Di CA.',adult:'El sonido C es distinto en casa y cielo.'},
   {kind:'letter',letter:'D',voice:'da',child:'Di D.',adult:'Apoya la lengua detrás de los dientes superiores.'}
 ];
 const PUNTOS_MODO = {M:'👄 Junta los labios y suelta el sonido.',P:'👄 Cierra y abre los labios.',S:'🦷 Saca aire suave.',G:'👅 El sonido sale atrás de la boca.',R:'👅 Toque corto con la lengua.',RR:'👅 Haz vibrar la lengua.'};
 const TITULOS={burbujas:'🫧 Burbujas de aire',pitillos:'☁️ Sopla el algodón',fonemas:'👄 Sonidos por imágenes',pronunciacion5:'🎯 5 palabras, un sonido',praxias:'👄 Juego de boca y sonidos',imitacion:'🐮 ¿Cómo suena?',abc:'🔤 Letras A B C D'};
 const NOMBRES={burbujas:'burbujas',pitillos:'pitillos',fonemas:'fonemas',pronunciacion5:'pronunciacion_5',praxias:'praxias',imitacion:'imitacion',abc:'abc'};
 const CATEGORIAS={burbujas:'respiracion',pitillos:'respiracion',fonemas:'articulacion',pronunciacion5:'articulacion',praxias:'practica_conmigo',imitacion:'resonancia',abc:'articulacion'};
 let modo,nivel,fonema,indice,avance,activo,ctx,stream,analyser,raf,ultimoUmbral,completado;
 let praxiasTipo='movimientos',praxiasLetra='',grabacionEnCurso=false;
 const $=id=>document.getElementById(id);
 function texto(t){$('fono-status').textContent=t;}
 function dibuja(html){$('fono-visual').innerHTML=html;}
 function progreso(p,total){$('fono-progreso-barra').style.width=Math.min(100,Math.round((p/Math.max(1,total))*100))+'%';$('fono-contador').textContent=`${p} de ${total}`;}
 function botones(items,onClick){$('fono-acciones').innerHTML='';items.forEach(([label,accion,extra=''])=>{const b=document.createElement('button');b.className='fono-gran-boton'+(extra?(' '+extra):'');b.textContent=label;b.type='button';b.addEventListener('click',()=>onClick(label,accion));$('fono-acciones').appendChild(b);});}
 function hablar(t){if(window.FonoVoz?.hablar(t))return;texto('Pide ayuda a un adulto para escuchar.');}
 function boca(tipo='pico'){return `<div class="fono-boca ${tipo}"><div class="fono-labios"></div></div>`;}
 function cambiarNivel(n){nivel=n;document.querySelectorAll('#fono-niveles button').forEach(b=>b.classList.toggle('activo',+b.dataset.nivel===nivel));reiniciar();}
 function cambiarFonema(f){if(!DATA[f])return;fonema=f;document.querySelectorAll('#fono-fonemas button').forEach(b=>b.classList.toggle('activo',b.textContent===f));reiniciar();}
 async function grabar(){return window.FonoEvidencia?.iniciar() || false;}
 function lista(){return modo==='abc'?ABC:modo==='imitacion'?IMITAR:modo==='praxias'?(praxiasTipo==='movimientos'?PRAXIAS.filter(x=>x.kind==='move'):PRAXIAS.filter(x=>x.kind==='letter'&&x.letter===praxiasLetra)):DATA[fonema];}
 function objetivo(){return [0,5,9,13][nivel];}
 function limpiarAudio(){activo=false;if(raf)cancelAnimationFrame(raf);raf=0;stream?.getTracks().forEach(t=>t.stop());stream=null;ctx?.close();ctx=null;}
 async function iniciarMic(){
   try{
    stream=await navigator.mediaDevices.getUserMedia({audio:true});
    const Ctx=window.AudioContext||window.webkitAudioContext;if(!Ctx)throw new Error('sin contexto');
    ctx=new Ctx();analyser=ctx.createAnalyser();analyser.fftSize=512;ctx.createMediaStreamSource(stream).connect(analyser);
    activo=true;await grabar();texto('🔴 Sopla suave al micrófono.');ultimoUmbral=0;medir();
   }catch(e){texto('No pude usar el micrófono. Puedes volver a intentarlo.');limpiarAudio();}
 }
 function medir(){if(!activo||!analyser)return;const a=new Uint8Array(analyser.frequencyBinCount);analyser.getByteFrequencyData(a);const rms=a.reduce((s,x)=>s+x,0)/a.length;const ahora=performance.now();
    if(rms>(nivel===1?16:nivel===2?22:27)&&ahora-ultimoUmbral>300){ultimoUmbral=ahora;avance++;if(modo==='burbujas'){const d=document.createElement('button');d.type='button';d.className='fono-burbuja';const size=26+Math.random()*55;d.style.width=size+'px';d.style.height=size+'px';d.style.left=10+Math.random()*80+'%';d.title='Toca para reventar';d.addEventListener('click',()=>d.remove());$('fono-visual').appendChild(d);setTimeout(()=>d.remove(),4000);}else{$('fono-copito').style.left=Math.min(80,5+avance*75/objetivo())+'%';}
      progreso(avance,objetivo());if(avance>=objetivo()){limpiarAudio();terminar();return;}}
    raf=requestAnimationFrame(medir);
 }
 function iniciarSoplo(){if(activo)return; if(modo==='burbujas')dibuja('<div class="fono-ilustracion">🫧</div>'); else dibuja('<div class="fono-pitillo" aria-hidden="true">🥤</div><div id="fono-copito" class="fono-copito">☁️</div><div class="fono-meta">🏁</div>'); botones([['⏹️ Terminar intento','stop','secundario']],(_,a)=>{if(a==='stop'){limpiarAudio();terminar();}}); iniciarMic();}
 function mostrarReto(){
   const items=lista(), item=items[indice];
   if(!item){if(modo==='praxias'&&praxiasTipo==='letras'&&!praxiasLetra){mostrarElegirLetra();return;}return terminar();}
   progreso(indice, items.length);
   if(modo==='praxias') return mostrarPraxia(item, items.length);
   if(modo==='imitacion') return mostrarImitacion(item, items.length);
   return mostrarPronunciacion(item, items.length);
 }
 function seleccionarPraxias(tipo, letra=''){
   if(grabacionEnCurso){texto('Primero guarda el audio del sonido actual.');return;}
   praxiasTipo=tipo;praxiasLetra=letra;indice=0;completado=false;
   document.querySelectorAll('#fono-fonemas button[data-tipo]').forEach(b=>b.classList.toggle('activo',b.dataset.tipo===tipo));
   document.querySelectorAll('#fono-fonemas button[data-letra]').forEach(b=>b.classList.toggle('activo',b.dataset.letra===letra));
   if(tipo==='letras'&&!letra)mostrarElegirLetra();else mostrarReto();
 }
 function mostrarElegirLetra(){
   progreso(0,1);$('fono-palabra').textContent='';
   dibuja('<div class="fono-pronuncia-card"><div class="fono-letra-grande">A a RR</div><p class="fono-mini-ayuda">Elige una letra arriba para ver a una persona que la pronuncia.</p></div>');
   texto('👆 Elige una letra.');botones([]);
 }
 function iniciarSelectorPraxias(){
   const caja=$('fono-fonemas');caja.classList.add('fono-selector-praxias');
   caja.replaceChildren();
   const tabs=document.createElement('div');tabs.className='fono-praxias-tabs';
   [['movimientos','👄 Mover la boca'],['letras','🔤 Decir letras']].forEach(([tipo,label])=>{
     const b=document.createElement('button');b.type='button';b.dataset.tipo=tipo;b.textContent=label;
     b.addEventListener('click',()=>seleccionarPraxias(tipo));tabs.appendChild(b);
   });
   const letras=document.createElement('div');letras.className='fono-praxias-letras';letras.id='fono-praxias-letras';
   ['M','P','S','G','R','RR','A','B','C','D'].forEach(letra=>{
     const b=document.createElement('button');b.type='button';b.dataset.letra=letra;b.textContent=letra;
     b.addEventListener('click',()=>seleccionarPraxias('letras',letra));letras.appendChild(b);
   });
   caja.append(tabs,letras);
   function actualizar(){
     letras.hidden=praxiasTipo!=='letras';
     tabs.querySelectorAll('button').forEach(b=>b.classList.toggle('activo',b.dataset.tipo===praxiasTipo));
     letras.querySelectorAll('button').forEach(b=>b.classList.toggle('activo',b.dataset.letra===praxiasLetra));
   }
   const _anterior=seleccionarPraxias;
   seleccionarPraxias=(tipo,letra='')=>{
     _anterior(tipo,letra); actualizar();
   };
   actualizar();
 }
 async function terminarPraxia(){
   if(completado)return;
   if(grabacionEnCurso){texto('Primero toca «⏹ Guardar audio».');return;}
   completado=true;botones([]);texto('Guardando este intento...');
   const total=lista().length,hechos=Math.min(total,indice);
   const notas=praxiasTipo==='letras'?'Práctica del sonido '+praxiasLetra+' con modelo humano en vídeo; grabación para revisión médica.':'Movimientos de boca realizados por imitación, sin exigir grabación.';
   try{
     await guardarResultadoJuego('practica_conmigo','praxias',hechos,total,hechos>=total,Math.round(100*hechos/Math.max(1,total)),1,{notas,requiereRevisionAudio:praxiasTipo==='letras'});
     texto('✅ ¡Muy bien! Intento guardado.');
     botones([['🔁 Hacer otra actividad','otra']],()=>{completado=false;praxiasLetra='';seleccionarPraxias(praxiasTipo);});
   }catch(e){completado=false;texto('No se guardó. Vuelve a intentarlo.');botones([['💾 Guardar','otra']],()=>terminarPraxia());}
 }
 function mostrarPraxia(item,total){
   $('fono-palabra').textContent='';
   const ayuda=document.querySelector('.fono-guia-nueva p');if(ayuda)ayuda.textContent=item.adult;
   if(item.kind==='move'){
      dibuja(`<div class="fono-pronuncia-card fono-movimiento"><div class="fono-boca-animada gesto-${item.shape}" role="img" aria-label="Demostración de ${item.child}"><span class="fono-ojos"><i></i><i></i></span><span class="fono-mejilla izq"></span><span class="fono-mejilla der"></span><span class="fono-labio"><i></i></span><span class="fono-aire">〰</span></div><div class="fono-movimiento-leyenda"><span>${item.emoji}</span><strong>${item.child}</strong></div><p class="fono-mini-ayuda">Mira la boca. ¡Tú también puedes!</p></div>`);
      texto(`👀 Movimiento ${indice+1} de ${total}.`);
      botones([['✅ Ya lo hice →','hecho']],()=>siguiente());
   }else{
     dibuja(`<div class="fono-pronuncia-card fono-humano"><div class="fono-letra-grande">${item.letter}</div><div id="fono-modelo-humano"></div><p class="fono-mini-ayuda">1. Mira el video · 2. Escucha · 3. Di la letra</p></div>`);
     window.FonoBocaReal?.pintar($('fono-modelo-humano'),item.letter);
     $('fono-palabra').textContent='Sonido '+item.letter;
     texto('🔊 Escucha, di el sonido y graba un intento.');
     function botonesLetra(){botones([['🔊 1. Escuchar','escucha'],['🎙️ 2. Grabar','grabar'],['✅ 3. Guardar intento','hecho']],async (_,a)=>{
       if(a==='escucha'){if(window.FonoVoz)FonoVoz.fonema(item.letter);else hablar(item.voice);return;}
       if(a==='grabar'){
         if(!window.FonoEvidencia){texto('Grabación no disponible. Puedes practicar igualmente.');return;}
         const ok=await window.FonoEvidencia.iniciar();
         if(!ok){texto('No fue posible abrir el micrófono.');return;}
         grabacionEnCurso=true;texto('🔴 Di el sonido '+item.letter+'. Después toca Guardar audio.');
         botones([['⏹️ Guardar audio','stop']],async()=>{
           const url=await window.FonoEvidencia.finalizar();grabacionEnCurso=false;
           texto(url?'✅ Audio guardado. Ahora finaliza el intento.':'No se pudo guardar el audio. Puedes intentarlo otra vez.');
           botonesLetra();
         });
         return;
       }
       indice=1;await terminarPraxia();
     });}
     botonesLetra();
   }
 }
 function mostrarImitacion(item,total){
   $('fono-palabra').textContent='';
   dibuja(`<div class="fono-imitar-card"><span class="fono-ilustracion">${item[0]}</span><div class="fono-pista-demo"><strong>Mira el dibujo</strong><p>Escucha y después haz el sonido tú.</p></div></div>`);
   texto(`Sonido ${indice+1} de ${total}: toca escuchar.`);
   function acciones(){botones([['🔊 1. Escuchar','escucha'],['🎙️ 2. Grabar','grabar'],['✅ 3. Siguiente','sig']],async(_,a)=>{
     if(a==='escucha'){
       if(window.FonoVoz) await FonoVoz.sonido(item[1],{fallback:item[2]});else hablar(item[1]);
       texto('Ahora haz el sonido como el ejemplo.');return;
     }
     if(a==='grabar'){
       if(!window.FonoEvidencia){texto('No se puede grabar en este navegador.');return;}
       const ok=await window.FonoEvidencia.iniciar();if(!ok){texto('No se pudo activar el micrófono.');return;}
       grabacionEnCurso=true;texto('🔴 Haz el sonido. Después toca Guardar audio.');
       botones([['⏹️ Guardar audio','stop']],async()=>{
         await window.FonoEvidencia.finalizar();grabacionEnCurso=false;
         texto('✅ Grabación terminada.');acciones();
       });return;
     }
     if(grabacionEnCurso){texto('Primero guarda la grabación.');return;}
     siguiente();
   });}
   acciones();
 }
 function mostrarPronunciacion(item,total){
    const visualFonema = ['fonemas','pronunciacion5'].includes(modo) ? '<div id="fono-modelo-humano"></div>' : '';
    dibuja(`<div class="fono-pronuncia-card"><span class="fono-ilustracion">${item[0]}</span>${visualFonema}<p class="fono-mini-ayuda">Primero mira. Después escucha. Luego di la palabra.</p></div>`);
    if(visualFonema) window.FonoBocaReal?.pintar($('fono-modelo-humano'),fonema);
    $('fono-palabra').textContent=(modo==='fonemas'||modo==='pronunciacion5') ? ('Letra ' + fonema) : '?';
    if(['fonemas','pronunciacion5'].includes(modo))texto(`Paso ${indice+1} de ${total}: ${PUNTOS_MODO[fonema]}`);
    let fase=0;
    function avanzarFase(){
      if(fase===0){texto(`Paso ${indice+1} de ${total}: mira el dibujo y toca escuchar.`);botones([['1. Escuchar la palabra','siguiente']],()=>{hablar(item[1]);fase=1;avanzarFase();});}
      else if(fase===1){texto('Ahora elige la letra correcta.'); const correcta=(modo==='abc'?item[2]:fonema); const alternativas=modo==='abc'?['A','B','C','D']:['M','P','S','G','R','RR'];
        if (nivel===3 && modo!=='abc') {const c=$('fono-acciones');c.innerHTML='';const inp=document.createElement('input');inp.className='fono-letra-input';inp.type='text';inp.maxLength=2;inp.placeholder='Escribe la letra';inp.setAttribute('aria-label','Escribe la letra');const ok=document.createElement('button');ok.className='fono-gran-boton';ok.textContent='2. Revisar';ok.addEventListener('click',()=>{if(inp.value.trim().toUpperCase()===correcta){fase=2;avanzarFase();}else{texto('Intenta otra vez.');}});c.append(inp,ok);} else {botones(alternativas.map(a=>[a,a]),(_,a)=>{if(a===correcta){fase=2;avanzarFase();}else{texto('Esa no es. Intenta otra vez.');}});}
      } else {
        $('fono-palabra').textContent=item[1].toUpperCase();
        texto('Ahora di la palabra.');
        botones([
          ['2. Escuchar otra vez','escucha'],
          ['3. Grabar mi voz','grabar'],
          ['4. Ya la dije','hecho']
        ],async(_,a)=>{if(a==='escucha'){hablar(item[1]);return;}if(a==='grabar'){await grabar();texto(`Di la palabra ${item[1]} y luego toca “Ya la dije”.`);return;}siguiente();});
      }
    }
    avanzarFase();
 }
 function siguiente(){indice++;if(indice>=lista().length){if(modo==='praxias')terminarPraxia();else terminar();return;}mostrarReto();}
 async function terminar(){if(completado)return;completado=true;limpiarAudio();texto('✅ ¡Muy bien! Guardando tu actividad...');botones([]);const total=(modo==='burbujas'||modo==='pitillos')?objetivo():lista().length;const pasos=(modo==='burbujas'||modo==='pitillos')?Math.min(avance,total):Math.min(indice,total);const notas=`Actividad ${modo}. Fonema ${fonema}. Nivel ${nivel}. Registro para revisión profesional; no es calificación clínica.`;try{const _=await guardarResultadoJuego(CATEGORIAS[modo],NOMBRES[modo],pasos,total,pasos>=total,Math.min(100,Math.round((pasos/Math.max(1,total))*100)),nivel,{notas,requiereRevisionAudio:true});texto('⭐ Actividad guardada.');}catch(e){completado=false;texto('No pude guardar. Inténtalo otra vez.');console.warn(e);botones([['💾 Guardar otra vez','save'],['🔁 Repetir','retry']],(_,a)=>a==='save'?terminar():reiniciar());return;} botones([['🔁 Volver a jugar','retry']],()=>reiniciar());}
 function reiniciar(){completado=false;avance=0;indice=0;limpiarAudio();const ayuda = document.querySelector('.fono-guia-nueva p');if(ayuda) ayuda.textContent='Muestra el dibujo y ayuda a escuchar. El niño puede señalar si todavía no lee. No fuerces la respiración ni la voz. La evaluación corresponde al profesional.';$('fono-palabra').textContent='';if(modo==='burbujas'||modo==='pitillos'){$('fono-consigna').textContent='👃 Toma aire y luego sopla suave.';dibuja(modo==='burbujas'?'<span class="fono-ilustracion">🫧</span>':'<div class="fono-pitillo" aria-hidden="true">🥤</div><div id="fono-copito" class="fono-copito">☁️</div><div class="fono-meta">🏁</div>');progreso(0,objetivo());botones([['▶️ Empezar','empezar']],()=>iniciarSoplo());texto('Toca empezar para jugar.');}else{$('fono-consigna').textContent=modo==='praxias'?'👄 Elige: mover la boca o practicar una letra':'👀 Mira · 👂 Escucha · 👄 Di';if(modo==='praxias'&&praxiasTipo==='letras'&&!praxiasLetra){mostrarElegirLetra();}else{mostrarReto();}}}
 function iniciar(m){modo=m;nivel=Math.max(1,Math.min(3,parseInt(new URLSearchParams(location.search).get('nivel')||'1',10)||1));fonema=(new URLSearchParams(location.search).get('fonema')||'M').toUpperCase();if(!DATA[fonema])fonema='M';$('fono-titulo').textContent=TITULOS[m];document.querySelectorAll('#fono-niveles button').forEach(b=>b.addEventListener('click',()=>cambiarNivel(+b.dataset.nivel)));if(['fonemas','pronunciacion5'].includes(m)){for(const f of Object.keys(DATA)){const b=document.createElement('button');b.type='button';b.textContent=f;b.addEventListener('click',()=>cambiarFonema(f));$('fono-fonemas').appendChild(b);}document.querySelectorAll('#fono-fonemas button').forEach(b=>b.classList.toggle('activo',b.textContent===fonema));}if($('fono-niveles')){$('fono-niveles').hidden=!['burbujas','pitillos'].includes(m);}if(m==='praxias'){const params=new URLSearchParams(location.search);if(params.has('fonema')&&['M','P','S','G','R','RR','A','B','C','D'].includes(fonema)){praxiasTipo='letras';praxiasLetra=fonema;}iniciarSelectorPraxias();}cambiarNivel(nivel);}
 return {iniciar};
})();
