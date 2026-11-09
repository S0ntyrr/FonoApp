/* FonoApp | motor compartido de voz y ejemplos sonoros.
   Audio original de Wikimedia Commons, reproducido en el juego sin salir de la app.
   Vaca: Secretlondon, Mudchute cow 1.ogg (CC BY-SA 3.0).
   Gato: Dcrosby, Meow.ogg (CC BY-SA 3.0).
   Perro: Amada44, Barking of a dog.ogg (CC BY-SA 3.0).
   Reloj: natalie, Clock ticking.ogg (dominio público).
   Las voces sintetizadas dependen de la voz española instalada en el navegador.
*/
(function(){
 'use strict';
 const FILES={
   vaca:'Mudchute_cow_1.ogg',
   gato:'Meow.ogg',
   perro:'Barking_of_a_dog.ogg',
   reloj:'Clock_ticking.ogg'
 };
 const FALLBACK={
   vaca:'La vaca hace mu.',gato:'El gato hace miau.',perro:'El perro hace guau.',
   reloj:'El reloj hace tic tac.',tren:'El tren hace chu chu.',
   pato:'El pato hace cua cua.',pollito:'El pollito hace pío pío.',
   rana:'La rana hace croac.',serpiente:'La serpiente hace sss.',
   moto:'La moto hace brrr.',abeja:'La abeja hace bzz.',
   campana:'La campana hace din don.',leon:'El león ruge.',tambor:'El tambor suena pom pom.'
 };
 const RUIDO=['muuu','muuuu','muuuú','miauuu','ssssss','ssss','brrrr','grrrr'];
 const NORMALIZAR={muuu:'mu',muuuu:'mu',miauuu:'miau',brrrr:'brr',grrrr:'grr'};
 let actual=null;
 let voices=[];
 function cargarVoces(){
   if(!('speechSynthesis' in window))return;
   voices=window.speechSynthesis.getVoices()||[];
 }
 if('speechSynthesis' in window){cargarVoces();window.speechSynthesis.addEventListener?.('voiceschanged',cargarVoces);}
 function elegirVoz(){
   if(!voices.length)cargarVoces();
   return voices.find(v=>(v.lang||'').toLowerCase()==='es-co')
       || voices.find(v=>(v.lang||'').toLowerCase()==='es-mx')
       || voices.find(v=>(v.lang||'').toLowerCase()==='es-es')
       || voices.find(v=>(v.lang||'').toLowerCase().startsWith('es'))||null;
 }
 function detener(){
   try{actual?.pause();if(actual)actual.currentTime=0;}catch(_){}actual=null;
   try{window.speechSynthesis?.cancel();}catch(_){}
 }
 function hablar(texto,opts={}){
   if(!('speechSynthesis' in window)||!('SpeechSynthesisUtterance' in window))return false;
   let limpio=String(texto||'').replace(/\s+/g,' ').trim();
   if(!limpio)return false;
   const l=limpio.toLowerCase();
   if(RUIDO.includes(l))limpio=NORMALIZAR[l] || limpio;
   detener();
   const u=new SpeechSynthesisUtterance(limpio);
   const v=elegirVoz();if(v)u.voice=v;
   u.lang=v?.lang||'es-CO';
   // 0.95 es una guía más natural que 0.78 para muchas voces; no cambia el idioma.
   u.rate=Math.max(.86,Math.min(1.07,opts.rate??.96));
   u.pitch=Math.max(.9,Math.min(1.1,opts.pitch??1));
   u.volume=typeof obtenerVolumenFono==='function'?obtenerVolumenFono():.8;
   window.speechSynthesis.speak(u);
   return true;
 }
 function sonido(nombre,opts={}){
   const clave=String(nombre||'').trim().toLowerCase();
   detener();
   if(!FILES[clave]){
     // No inventar audio real donde todavía no hay grabación autorizada.
     return Promise.resolve(hablar(FALLBACK[clave]||opts.fallback||'Escucha e imita el sonido.'));
   }
   // Wikimedia Special:Redirect permite reproducir el archivo original sin abrir página externa.
   const url='https://commons.wikimedia.org/wiki/Special:Redirect/file/'+encodeURIComponent(FILES[clave]);
   const a=typeof crearAudioFono==='function'?crearAudioFono(url):new Audio(url);
   actual=a;a.preload='auto';
   return a.play().then(()=>true).catch(()=>{
      if(actual===a)actual=null;
      return hablar(FALLBACK[clave]||opts.fallback||'Escucha e imita el sonido.');
   });
 }
 // Sonido de la letra SIN vocal añadida (M = «mmm», no «ma»). Lo genera fono-fonemas-audio.js.
 function fonema(letra){
   detener();
   if(window.FonoFonema && window.FonoFonema.reproducir(letra))return true;
   const ejemplos={A:'a',E:'e',I:'i',O:'o',U:'u'};
   return hablar(ejemplos[String(letra||'').toUpperCase()]||String(letra||''));
 }
 window.FonoVoz={hablar,sonido,fonema,detener,fuentes:FILES};
 window.addEventListener('pagehide',detener);
})();
