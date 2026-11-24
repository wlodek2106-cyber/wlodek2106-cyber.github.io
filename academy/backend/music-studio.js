"use strict";
function synth(pattern,bpm,bars,root,effect="music"){
 const rate=22050, step=60/bpm/4, count=effect==="music"?Math.ceil(rate*step*16*bars):rate*2;
 const out=new Float32Array(count);let seed=13579;
 const noise=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/2147483648-1;};
 const tau=2*Math.PI, scale=[0,3,7,10,12,7,5,3];
 for(let i=0;i<count;i++){
  const t=i/rate,s=Math.floor(t/step)%16,u=t%step;let y=0;
  if(effect==="rise"){y=(Math.sin(tau*(100*t+180*t*t))+noise()*.4)*Math.sin(Math.PI*t/2)*.45;}
  else if(effect==="impact"){y=(Math.sin(tau*(55*t+5*(1-Math.exp(-15*t))))*.7+noise()*.3)*Math.exp(-5*t);}
  else if(effect==="click"){y=Math.sin(tau*880*t)*Math.exp(-35*t)*.6;}
  else {
   const kick=pattern[0][s],snare=pattern[1][s],hat=pattern[2][s],bass=pattern[3][s],lead=pattern[4][s];
   const hz=440*2**((root-69)/12),env=Math.min(1,u/.008)*Math.max(0,1-u/step);
   if(kick)y+=.52*Math.sin(tau*(45*u+3*(1-Math.exp(-42*u))))*Math.exp(-13*u)*Math.min(1,u/.003);
   if(snare)y+=.25*noise()*Math.exp(-22*u)*Math.min(1,u/.002);
   if(hat)y+=.13*noise()*Math.exp(-65*u)*Math.min(1,u/.002);
   if(bass)y+=.22*(Math.sin(tau*hz*u)+.22*Math.sin(tau*hz*2*u))*env;
   if(lead)y+=.14*Math.sin(tau*hz*4*2**(scale[s%8]/12)*u)*env;
  }
  out[i]=Math.max(-.95,Math.min(.95,y))*Math.min(1,i/110,(count-1-i)/220);
 }
 return {samples:out,rate};
}
function wav(samples,rate){
 const b=new ArrayBuffer(44+samples.length*2),v=new DataView(b);
 const tag=(p,s)=>{for(let i=0;i<s.length;i++)v.setUint8(p+i,s.charCodeAt(i));};
 tag(0,"RIFF");v.setUint32(4,b.byteLength-8,true);tag(8,"WAVE");tag(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,rate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);tag(36,"data");v.setUint32(40,samples.length*2,true);
 for(let i=0;i<samples.length;i++)v.setInt16(44+2*i,Math.round(Math.max(-1,Math.min(1,samples[i]))*32767),true);
 return b;
}
const $=id=>document.getElementById(id);
const words={en:["Create original instrumental loops and effects using local synthesis. No AI model, samples, upload or paid API.","Tempo (BPM)","Bars","Root note","Pattern preset","Apply preset","Clear pattern","Render music","Sound effects","Rise","Impact","Click","Download WAV","Mono PCM, 22.05 kHz. Preview is manual. No cloud storage or vocals.","Ready","Invalid tempo","Audio rendered"],ru:["Создавай оригинальные инструментальные лупы и эффекты локальным синтезом. Без AI-модели, семплов, загрузки на сервер и платных API.","Темп (BPM)","Такты","Основная нота","Шаблон ритма","Применить шаблон","Очистить ритм","Создать музыку","Звуковые эффекты","Нарастание","Удар","Щелчок","Скачать WAV","Моно PCM, 22,05 кГц. Прослушивание вручную. Без облачного хранения и вокала.","Готово","Неверный темп","Аудио создано"],uk:["Створюй оригінальні інструментальні лупи та ефекти локальним синтезом. Без ШІ-моделі, семплів, завантаження на сервер і платних API.","Темп (BPM)","Такти","Основна нота","Шаблон ритму","Застосувати шаблон","Очистити ритм","Створити музику","Звукові ефекти","Наростання","Удар","Клацання","Завантажити WAV","Моно PCM, 22,05 кГц. Ручне прослуховування. Без хмарного сховища та вокалу.","Готово","Невірний темп","Аудіо створено"],pl:["Twórz oryginalne pętle instrumentalne i efekty za pomocą lokalnej syntezy. Bez modelu AI, sampli, wysyłania i płatnych API.","Tempo (BPM)","Takty","Nuta podstawowa","Wzorzec rytmu","Zastosuj wzorzec","Wyczyść rytm","Utwórz muzykę","Efekty dźwiękowe","Narastanie","Uderzenie","Klik","Pobierz WAV","Mono PCM, 22,05 kHz. Odsłuch ręczny. Bez chmury i wokalu.","Gotowe","Błędne tempo","Dźwięk utworzony"]};
const names=["Kick","Snare","Hi-hat","Bass","Lead"],preset={pulse:[[0,4,8,12],[4,12],[2,6,10,14],[0,6,8,14],[2,7,10,15]],ambient:[[0,8],[],[6,14],[0,8],[0,4,9,13]],beat:[[0,3,8,11],[4,12],[0,2,4,6,8,10,12,14],[0,3,8,11],[5,7,13,15]]};
let pattern=[],url=null,filename="";const lang=new URLSearchParams(location.search).get("lang");$("lang").value=Object.hasOwn(words,lang)?lang:"en";
const w=()=>words[$("lang").value],status=i=>$("status").textContent=w()[i];
function translate(){document.documentElement.lang=$("lang").value;document.querySelectorAll("[data-t]").forEach(e=>e.textContent=w()[Number(e.dataset.t)]);}
function invalidate(){if(url){$("audio").pause();$("audio").removeAttribute("src");$("audio").load();URL.revokeObjectURL(url);}url=null;$("audio").hidden=true;$("download").disabled=true;}
function grid(){const table=$("steps");table.replaceChildren();const head=table.insertRow();head.append(document.createElement("th"));for(let i=0;i<16;i++){const th=document.createElement("th");th.textContent=i+1;head.append(th);}pattern.forEach((row,r)=>{const tr=table.insertRow(),th=document.createElement("th");th.scope="row";th.textContent=names[r];tr.append(th);row.forEach((active,c)=>{const b=document.createElement("button");b.type="button";b.textContent=active?"●":"·";b.setAttribute("aria-label",names[r]+" "+(c+1));b.setAttribute("aria-pressed",String(active));b.onclick=()=>{pattern[r][c]=!pattern[r][c];b.textContent=pattern[r][c]?"●":"·";b.setAttribute("aria-pressed",String(pattern[r][c]));invalidate();};tr.insertCell().append(b);});});}
function apply(){pattern=preset[$("preset").value].map(row=>Array.from({length:16},(_,i)=>row.includes(i)));grid();invalidate();}
$("apply").onclick=apply;$("clear").onclick=()=>{pattern=Array.from({length:5},()=>Array(16).fill(false));grid();invalidate();};$("lang").onchange=translate;
for(const id of ["bpm","bars","root"])$(id).onchange=invalidate;
function render(effect){const bpm=Number($("bpm").value);if(!Number.isInteger(bpm)||bpm<60||bpm>180){status(15);return;}invalidate();const {samples,rate}=synth(pattern,bpm,Number($("bars").value),Number($("root").value),effect);url=URL.createObjectURL(new Blob([wav(samples,rate)],{type:"audio/wav"}));filename="zer0life-"+effect+".wav";$("audio").src=url;$("audio").hidden=false;$("download").disabled=false;status(16);}
$("make").onclick=()=>render("music");document.querySelectorAll("[data-effect]").forEach(b=>b.onclick=()=>render(b.dataset.effect));$("download").onclick=()=>{if(url){const a=document.createElement("a");a.href=url;a.download=filename;a.click();}};translate();apply();status(14);
