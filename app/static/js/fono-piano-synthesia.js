/* Piano Synthesia original de FonoApp: melodía tradicional de dominio público.
   La detección de notas es visual/interactiva, no evaluación clínica de afinación. */
(()=>{
 'use strict';
 const SONG=[0,0,4,4,5,5,4,3,3,2,2,1,1,0,
  4,4,3,3,2,2,1,4,4,3,3,2,2,1,
  0,0,4,4,5,5,4,3,3,2,2,1,1,0];
 const NOTES=[
  ['DO',261.63,'#ff766e','🔴'],['RE',293.66,'#ffb45c','🟠'],['MI',329.63,'#ffda57','🟡'],
  ['FA',349.23,'#6fda92','🟢'],['SOL',392,'#48cabb','🟢'],['LA',440,'#73b5ff','🔵'],
  ['SI',493.88,'#ab91f6','🟣'],['DO+',523.25,'#fa93db','💗']
 ];
 const $=id=>document.getElementById(id);
 if(!$('notas-canvas'))return;
 const canvas=$('notas-canvas'),pen=canvas.getContext('2d'),keys=[];
 let audioContext=null,recording=null,recordUrl='',recordingActive=false;
 let mode='guided',speed=1,level=1,sequence=SONG.slice(0,14),current=0,score=0;
 let state='idle',running=false,lastTime=0,stepTime=0,demoTime=0,demoPlayed=0,raf=0,saving=false,saved=false;
 const LEAD=1850,BEAT=680;
 const view=()=>({w:canvas.clientWidth||600,h:canvas.clientHeight||300});
 const reqRedraw=()=>{const{w,h}=view();const dpr=Math.min(2,window.devicePixelRatio||1);if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr)}pen.setTransform(dpr,0,0,dpr,0,0);return {w,h};};
 function setStatus(text){$('nota-piano-actual').textContent=text}
 function update(){
   $('piano-avance').textContent=current;$('piano-total').textContent=sequence.length;$('puntos-piano').textContent=score;
   const progress=Math.round(current/sequence.length*100);$('piano-progreso').style.width=progress+'%';$('piano-progreso').setAttribute('aria-valuenow',progress);
   $('piano-iniciar').disabled=running||state==='done';$('piano-pausar').disabled=!running&&state!=='paused';
   $('piano-pausar').textContent=running?'⏸ Pausar':'▶ Continuar';
   $('piano-modo-estado').textContent=mode==='guided'?'🎯 Toca la nota iluminada':'👀 Mira cómo cae cada nota';
   $('piano-demo').classList.toggle('activo',mode==='demo');$('piano-guiado').classList.toggle('activo',mode==='guided');
 }
 function render(){
   const {w,h}=reqRedraw(),lane=w/NOTES.length,hit=h-28,fall=hit/(LEAD/speed);
   pen.clearRect(0,0,w,h);
   pen.fillStyle='#162348';pen.fillRect(0,0,w,h);
   for(let i=0;i<NOTES.length;i++){
     pen.fillStyle=i%2?'#ffffff06':'#ffffff0e';pen.fillRect(i*lane,0,lane,h);
     pen.strokeStyle='#ffffff25';pen.beginPath();pen.moveTo(i*lane,0);pen.lineTo(i*lane,h);pen.stroke();
   }
   if(state==='idle'){pen.textAlign='center';pen.fillStyle='#dcecff';pen.font=`800 ${Math.max(15,Math.min(23,w/26))}px sans-serif`;pen.fillText('🌟 ¡Cada color es una nota!',w/2,h/2);return;}
   const start=mode==='guided'?current:0;
   for(let i=start;i<Math.min(sequence.length,start+9);i++){
     let offset;
     if(mode==='guided'){offset=(i-current)*BEAT/speed+LEAD/speed-stepTime;}
     else {offset=LEAD/speed+i*(BEAT/speed)-demoTime;}
     const y=hit-offset*fall;
     if(y<-55||y>h+50)continue;
     const idx=sequence[i],x=idx*lane+lane*.08,width=lane*.84;
     pen.fillStyle=NOTES[idx][2];pen.shadowColor=NOTES[idx][2];pen.shadowBlur=13;
     pen.beginPath();pen.roundRect(x,y-33,width,30,Math.min(9,width/5));pen.fill();pen.shadowBlur=0;
     pen.fillStyle='#0b2037';pen.font=`900 ${Math.min(13,Math.max(9,lane*.22))}px sans-serif`;
     pen.textAlign='center';pen.fillText(NOTES[idx][0],x+width/2,y-12);
   }
   pen.fillStyle='#ffe8a2';pen.fillRect(0,hit-1,w,3);
   if(mode==='guided'&&state==='playing'&&stepTime>=LEAD/speed){
     const idx=sequence[current];if(idx!==undefined){pen.strokeStyle='#fffbe6';pen.lineWidth=4;pen.strokeRect(idx*lane+3,hit-34,lane-6,35);pen.lineWidth=1;}
   }
 }
 async function ensureAudio(){try{if(!audioContext){audioContext=typeof crearContextoAudioFono==='function'?crearContextoAudioFono():new (window.AudioContext||window.webkitAudioContext)()}if(audioContext?.state==='suspended')await audioContext.resume();}catch(e){console.warn('Audio no disponible',e);}}
 function play(idx){if(!audioContext||audioContext.state==='closed')return;try{
   if(typeof crearTonoFono==='function'){crearTonoFono(audioContext,{frequency:NOTES[idx][1],duration:.34,volumeBase:.2,type:'sine'});}
   else{const o=audioContext.createOscillator(),g=audioContext.createGain();o.frequency.value=NOTES[idx][1];o.connect(g);g.connect(audioContext.destination);g.gain.setValueAtTime(.12,audioContext.currentTime);g.gain.exponentialRampToValueAtTime(.001,audioContext.currentTime+.34);o.start();o.stop(audioContext.currentTime+.35)}
 }catch(e){console.warn(e)}}
 function highlight(idx,correct){keys.forEach((key,k)=>{key.classList.toggle('synth-destino',mode==='guided'&&state==='playing'&&k===sequence[current]);if(k===idx&&correct){key.classList.add('synth-tocada');setTimeout(()=>key.classList.remove('synth-tocada'),270)}})}
 function done(){running=false;state='done';cancelAnimationFrame(raf);current=sequence.length;highlight(-1,false);update();render();
   $('fase-cantar').hidden=false;setStatus('🎉 ¡Lo lograste! Ahora puedes cantar y grabar tu voz.');}
 function tick(time){
   if(!running)return;
   const delta=Math.min(90,time-(lastTime||time));lastTime=time;
   if(mode==='guided')stepTime=Math.min(LEAD/speed,stepTime+delta);
   else{
     demoTime+=delta;
     while(demoPlayed<sequence.length&&demoTime>=LEAD/speed+demoPlayed*(BEAT/speed)){
       const idx=sequence[demoPlayed];play(idx);demoPlayed++;current=demoPlayed;update();highlight(idx,true);
     }
     if(demoPlayed===sequence.length&&demoTime>=LEAD/speed+sequence.length*(BEAT/speed)){done();return;}
   }
   render();if(mode==='guided')highlight(-1,false);
   raf=requestAnimationFrame(tick);
 }
 async function start(){if(state==='done')reset();await ensureAudio();if(!audioContext){setStatus('Este navegador no admite sonido; puedes tocar las teclas.');}
   if(state==='idle'){stepTime=0;demoTime=0;demoPlayed=0;current=0;}
   state='playing';running=true;lastTime=0;update();if(mode==='guided')setStatus('👀 Mira el color. 👆 Toca '+NOTES[sequence[current]][0]);else setStatus('👂 Escucha y mira las teclas que se encienden.');highlight(-1,false);
   cancelAnimationFrame(raf);raf=requestAnimationFrame(tick);
 }
 function pause(){if(state==='playing'){running=false;state='paused';cancelAnimationFrame(raf);setStatus('⏸ Pausa: continúa cuando quieras.');}
   else if(state==='paused'){start();return;}update();render();}
 function reset(){running=false;cancelAnimationFrame(raf);state='idle';current=0;score=0;stepTime=0;demoTime=0;demoPlayed=0;lastTime=0;saved=false;recordUrl='';$('fase-cantar').hidden=true;setStatus('Toca «Empezar» para seguir las estrellas.');update();highlight(-1,false);render();}
 function switchMode(m){if(mode===m)return;mode=m;reset();}
 async function keyTouch(idx){await ensureAudio();play(idx);if(state!=='playing'||mode!=='guided')return;
   if(sequence[current]===idx){score+=10;highlight(idx,true);current++;stepTime=0;lastTime=0;update();
     if(current>=sequence.length){done();return;}
     setStatus('✅ ¡Bien! Ahora toca '+NOTES[sequence[current]][0]);
   }else{setStatus('👀 Busca la tecla '+NOTES[sequence[current]][0]+' de color '+(NOTES[sequence[current]][3]||'')+'.');}
 }
 function buildKeys(){const container=$('piano-container');container.replaceChildren();NOTES.forEach((n,i)=>{
   const b=document.createElement('button');b.type='button';b.dataset.note=n[0];b.setAttribute('aria-label','Tocar nota '+n[0]);
   const icon=document.createElement('span');icon.className='synth-tecla-icono';icon.textContent=n[3];const name=document.createElement('span');name.textContent=n[0];b.append(icon,name);
   b.addEventListener('click',()=>keyTouch(i));container.appendChild(b);keys.push(b);
 });}
 async function micStart(){if(recordingActive)return;try{
   recording=typeof crearCapturaActividad==='function'?crearCapturaActividad({categoria:'resonancia',juego:'piano'}):null;
   if(!recording)throw new Error('Grabación no disponible');const ok=await recording.iniciar();if(ok===false)throw new Error('Permiso no concedido');
   recordingActive=true;$('btn-mic-piano').hidden=true;$('piano-terminar-mic').hidden=false;$('mic-estado-piano').textContent='🔴 Cantando... toca Guardar mi voz cuando termines.';
 }catch(e){$('mic-estado-piano').textContent='No se pudo activar el micrófono. Revisa sus permisos.';recording=null;}}
 async function micStop(){if(!recordingActive)return;recordingActive=false;$('piano-terminar-mic').disabled=true;$('mic-estado-piano').textContent='Guardando grabación...';
  try{const detail=await recording.detener({transcripcion:''});recordUrl=detail?.audioUrl||'';$('mic-estado-piano').textContent=recordUrl?'✅ Voz guardada. Pulsa Finalizar actividad.':'No se guardó la voz. Puedes intentarlo otra vez.';}
  catch(e){$('mic-estado-piano').textContent='No fue posible guardar el audio. Puedes reintentarlo.';}
  $('btn-mic-piano').hidden=false;$('piano-terminar-mic').hidden=true;$('piano-terminar-mic').disabled=false;
 }
 async function finish(){if(saving||saved)return;if(recordingActive)await micStop();saving=true;$('piano-finalizar').disabled=true;$('mic-estado-piano').textContent='Guardando tu actividad...';
  try{if(typeof guardarResultadoJuego!=='function')throw new Error('Sin almacenamiento');
   await guardarResultadoJuego('resonancia','piano',current,sequence.length,current===sequence.length,score,level,{audioUrl:recordUrl,requiereRevisionAudio:!!recordUrl,notas:'Piano con notas descendentes. Modo: '+mode+'. Velocidad: '+speed+'x. La puntuación indica interacción, no calidad de afinación.'});
   saved=true;$('mic-estado-piano').textContent='✅ Actividad registrada para el profesional.';
  }catch(e){$('mic-estado-piano').textContent='No se pudo registrar la actividad. Revisa la conexión e intenta otra vez.';}
  finally{saving=false;$('piano-finalizar').disabled=saved;}}
 function init(){buildKeys();$('piano-demo').addEventListener('click',()=>switchMode('demo'));
  $('piano-guiado').addEventListener('click',()=>switchMode('guided'));
  $('piano-nivel').addEventListener('change',e=>{level=Number(e.target.value);sequence=SONG.slice(0,level===1?14:level===2?28:42);reset();});
  $('piano-velocidad').addEventListener('input',e=>{const old=speed;speed=Number(e.target.value);$('piano-velocidad-valor').textContent=speed.toFixed(2).replace(/0$/,'')+'×';if(mode==='guided'&&stepTime>0)stepTime=stepTime*old/speed;update();render();});
  $('piano-iniciar').addEventListener('click',start);$('piano-pausar').addEventListener('click',pause);$('piano-repetir').addEventListener('click',reset);
  $('btn-mic-piano').addEventListener('click',micStart);$('piano-terminar-mic').addEventListener('click',micStop);$('piano-finalizar').addEventListener('click',finish);
  window.addEventListener('resize',render);window.addEventListener('pagehide',()=>{running=false;cancelAnimationFrame(raf);});
  const params=new URLSearchParams(location.search),n=Number(params.get('nivel'));if([1,2,3].includes(n)){$('piano-nivel').value=String(n);level=n;sequence=SONG.slice(0,n===1?14:n===2?28:42)}reset();}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
