"use strict";
function frameAt(seconds,count,duration){const t=Math.max(0,Math.min(seconds,count*duration-0.000001));return {index:Math.floor(t/duration),progress:(t%duration)/duration};}
function cover(w,h,iw,ih,progress,motion){const scale=Math.max(w/iw,h/ih)*(motion==="zoom"?1+0.12*progress:motion==="pan"?1.12:1),dw=iw*scale,dh=ih*scale;return {x:(w-dw)*(motion==="pan"?progress:0.5),y:(h-dh)/2,w:dw,h:dh};}
const $=id=>document.getElementById(id);
const labels={
en:["Animate your own images locally: up to 6 scenes, no uploads or paid APIs. This is a motion slideshow, not generative AI video.","Images in scene order (PNG/JPEG/WebP, up to 6 × 5 MB)","Captions — one line per scene","Format","Seconds per scene","Motion","Slow zoom","Pan","Still","Preview","Record video","Stop","Download video","Silent video. Keep this tab visible; export depends on browser codecs. Files stay in memory until you close the page.","Ready","Invalid image or unsupported browser","Recording / playing","Stopped","Video ready"],
ru:["Анимируй свои изображения локально: до 6 сцен, без загрузки на сервер и платных API. Это слайд-шоу с движением, а не генеративное AI-видео.","Изображения по порядку сцен (PNG/JPEG/WebP, до 6 × 5 МБ)","Титры — одна строка на сцену","Формат","Секунд на сцену","Движение","Плавный зум","Панорама","Статика","Предпросмотр","Записать видео","Стоп","Скачать видео","Видео без звука. Не закрывай вкладку; экспорт зависит от кодеков браузера. Файлы в памяти до закрытия страницы.","Готово","Ошибка изображения или браузер не поддерживается","Запись / воспроизведение","Остановлено","Видео готово"],
uk:["Анімуй власні зображення локально: до 6 сцен, без завантаження на сервер і платних API. Це рухоме слайд-шоу, не генеративне ШІ-відео.","Зображення за порядком сцен (PNG/JPEG/WebP, до 6 × 5 МБ)","Титри — один рядок на сцену","Формат","Секунд на сцену","Рух","Плавне наближення","Панорама","Статика","Перегляд","Записати відео","Стоп","Завантажити відео","Відео без звуку. Тримай вкладку відкритою; експорт залежить від кодеків браузера. Файли лише в пам’яті.","Готово","Помилка зображення або браузер не підтримується","Запис / відтворення","Зупинено","Відео готове"],
pl:["Animuj własne obrazy lokalnie: do 6 scen, bez wysyłania i płatnych API. To animowany pokaz slajdów, nie generatywne wideo AI.","Obrazy w kolejności scen (PNG/JPEG/WebP, do 6 × 5 MB)","Napisy — jeden wiersz na scenę","Format","Sekundy na scenę","Ruch","Powolne zbliżenie","Panorama","Statyczny","Podgląd","Nagraj wideo","Stop","Pobierz wideo","Wideo bez dźwięku. Nie zamykaj karty; eksport zależy od kodeków przeglądarki. Pliki tylko w pamięci.","Gotowe","Błędny obraz lub brak obsługi przeglądarki","Nagrywanie / odtwarzanie","Zatrzymano","Wideo gotowe"]};
const lang=new URLSearchParams(location.search).get("lang");$("lang").value=Object.hasOwn(labels,lang)?lang:"en";
const t=i=>labels[$("lang").value][i], status=i=>$("status").textContent=t(i);
function translate(){document.documentElement.lang=$("lang").value;document.querySelectorAll("[data-t]").forEach(e=>e.textContent=t(Number(e.dataset.t)));} $("lang").onchange=translate;translate();
const sizes={landscape:[1280,720],portrait:[720,1280],square:[720,720]},canvas=$("canvas"),ctx=canvas.getContext("2d");
let images=[],loading=false,busy=false,raf=0,rec=null,stream=null,output=null,blob=null;
function controls(){for(const id of ["images","captions","size","duration","motion"])$(id).disabled=busy||loading;$("play").disabled=busy||loading||!images.length;$("record").disabled=busy||loading||!images.length||!canvas.captureStream||typeof MediaRecorder==="undefined";$("stop").disabled=!busy;$("download").disabled=busy||!blob;}
function clearOutput(){if(output)URL.revokeObjectURL(output);output=null;blob=null;$("video").removeAttribute("src");$("video").hidden=true;}
function draw(s=0){const [w,h]=sizes[$("size").value];if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}ctx.fillStyle="#101025";ctx.fillRect(0,0,w,h);if(!images.length)return;const f=frameAt(s,images.length,Number($("duration").value)),im=images[f.index],b=cover(w,h,im.width,im.height,f.progress,$("motion").value);ctx.drawImage(im,b.x,b.y,b.w,b.h);const caption=($("captions").value.split(/\r?\n/)[f.index]||"").slice(0,180);if(caption){const fs=Math.round(w*.045);ctx.fillStyle="#000b";ctx.fillRect(0,h*.78,w,h*.22);ctx.font="bold "+fs+"px system-ui";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillStyle="#fff";ctx.fillText(caption,w/2,h*.88,w*.88);}}
$("images").onchange=async()=>{if(busy||loading)return;loading=true;controls();const next=[];try{const files=[...$("images").files];if(files.length>6)throw Error();for(const f of files){if(!["image/png","image/jpeg","image/webp"].includes(f.type)||f.size>5*1024*1024)throw Error();const original=await createImageBitmap(f);let im=original;if(Math.max(original.width,original.height)>1280){const ratio=1280/Math.max(original.width,original.height);try{im=await createImageBitmap(original,{resizeWidth:Math.max(1,Math.round(original.width*ratio)),resizeHeight:Math.max(1,Math.round(original.height*ratio)),resizeQuality:"high"});}finally{original.close();}}if(!im.width||!im.height){im.close();throw Error();}next.push(im);}images.forEach(i=>i.close());images=next;clearOutput();$("files").textContent=files.map(f=>f.name).join(" · ");draw();status(14);}catch{next.forEach(i=>i.close());$("images").value="";status(15);}finally{loading=false;controls();}};
for(const id of ["captions","size","duration","motion"])$(id).oninput=()=>{clearOutput();draw();controls();};
function finish(){cancelAnimationFrame(raf);if(rec&&rec.state!=="inactive"){rec.stop();return;}if(!rec){busy=false;status(17);controls();}}
function start(record){if(busy||loading||!images.length)return;clearOutput();draw();busy=true;controls();let chunks=[];try{if(record){stream=canvas.captureStream(24);const mime=["video/webm;codecs=vp8","video/webm","video/mp4"].find(m=>MediaRecorder.isTypeSupported(m));rec=mime?new MediaRecorder(stream,{mimeType:mime,videoBitsPerSecond:2500000}):new MediaRecorder(stream);let failed=false;rec.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};rec.onerror=()=>{failed=true;finish();};rec.onstop=()=>{stream?.getTracks().forEach(t=>t.stop());stream=null;const type=rec.mimeType||chunks[0]?.type||"video/webm";rec=null;busy=false;if(!failed&&chunks.length){blob=new Blob(chunks,{type});output=URL.createObjectURL(blob);$("video").src=output;$("video").hidden=false;status(18);}else status(15);controls();};rec.start(500);}const begun=performance.now(),total=images.length*Number($("duration").value);status(16);function tick(now){if(!busy)return;const elapsed=(now-begun)/1000;draw(Math.min(elapsed,total));if(elapsed>=total){finish();return;}raf=requestAnimationFrame(tick);}raf=requestAnimationFrame(tick);}catch{stream?.getTracks().forEach(t=>t.stop());stream=null;rec=null;busy=false;status(15);controls();}}
$("play").onclick=()=>start(false);$("record").onclick=()=>start(true);$("stop").onclick=finish;
$("download").onclick=()=>{if(!blob||!output)return;const a=document.createElement("a");a.href=output;a.download="zer0life-animation."+(blob.type.includes("mp4")?"mp4":"webm");a.click();};
document.addEventListener("visibilitychange",()=>{if(document.hidden&&busy)finish();});draw();status(14);controls();

/* Digital Human Lab: local PCM preparation and original, procedural 2D teaching preview. */
function humanReadPCM(buffer){
 if(!(buffer instanceof ArrayBuffer)||buffer.byteLength<44||buffer.byteLength>24*1024*1024)throw Error("Invalid WAV size");
 const v=new DataView(buffer),tag=p=>String.fromCharCode(v.getUint8(p),v.getUint8(p+1),v.getUint8(p+2),v.getUint8(p+3));
 if(tag(0)!=="RIFF"||tag(8)!=="WAVE"||v.getUint32(4,true)+8!==v.byteLength)throw Error("Invalid WAV header");
 let format=null,offset=-1,length=0;
 for(let p=12;p+8<=v.byteLength;){
  const n=v.getUint32(p+4,true),end=p+8+n;if(end>v.byteLength)throw Error("Invalid chunk");
  if(tag(p)==="fmt "){if(n<16||format)throw Error("Invalid format");format=[v.getUint16(p+8,true),v.getUint16(p+10,true),v.getUint32(p+12,true),v.getUint16(p+20,true),v.getUint16(p+22,true)];}
  if(tag(p)==="data"){if(offset>=0)throw Error("Duplicate data");offset=p+8;length=n;}
  p=end+(n%2);
 }
 if(!format||offset<0)throw Error("Missing WAV data");
 const [encoding,channels,rate,align,bits]=format;
 if(encoding!==1||![1,2].includes(channels)||bits!==16||align!==channels*2||rate<8000||rate>96000||length%align)throw Error("PCM16 mono/stereo required");
 const count=length/align;if(!count||count/rate>60)throw Error("Max 60 seconds");
 const mono=new Float32Array(count);
 for(let i=0;i<count;i++){let sum=0;for(let ch=0;ch<channels;ch++)sum+=v.getInt16(offset+i*align+2*ch,true)/32768;mono[i]=sum/channels;}
 return {mono,rate};
}
function humanWriteWAV(samples){
 if(!(samples instanceof Float32Array)||!samples.length||samples.length>960000)throw Error("Invalid samples");
 const b=new ArrayBuffer(44+samples.length*2),v=new DataView(b),tag=(p,t)=>{for(let i=0;i<t.length;i++)v.setUint8(p+i,t.charCodeAt(i))};
 tag(0,"RIFF");v.setUint32(4,b.byteLength-8,true);tag(8,"WAVE");tag(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,16000,true);v.setUint32(28,32000,true);v.setUint16(32,2,true);v.setUint16(34,16,true);tag(36,"data");v.setUint32(40,samples.length*2,true);
 for(let i=0;i<samples.length;i++){const x=Math.max(-1,Math.min(1,samples[i]));v.setInt16(44+i*2,Math.round(x<0?x*32768:x*32767),true);}
 return b;
}
async function humanResample(data){
 if(data.rate===16000)return data.mono;
 const Offline=window.OfflineAudioContext||window.webkitOfflineAudioContext;if(!Offline)throw Error("Offline audio unsupported");
 const context=new Offline(1,Math.max(1,Math.round(data.mono.length*16000/data.rate)),16000);
 const original=context.createBuffer(1,data.mono.length,data.rate);original.copyToChannel(data.mono,0);
 const source=context.createBufferSource();source.buffer=original;source.connect(context.destination);source.start(0);
 const result=await context.startRendering();return new Float32Array(result.getChannelData(0));
}
function humanMouth(samples,time){
 if(!samples||!Number.isFinite(time)||time<0)return 0;
 const start=Math.floor(time*16000),end=Math.min(start+480,samples.length);if(start>=end)return 0;
 let sum=0;for(let i=start;i<end;i++)sum+=samples[i]*samples[i];return Math.min(1,Math.sqrt(sum/(end-start))*5);
}
const humanFactoryWords={"en":["Digital Human Factory 28.0","Appearance and expression","Skin color","Hair color","Clothing color","Background color","Expression","Neutral","Happy","Serious","Blinking","Export motion track JSON","Local procedural character, not photorealistic AI or voice cloning. Motion track records amplitude and blink values, not phonemes or a native rig. Export requires authorized prepared audio.","Run character tests","Tests passed","Tests failed","Frames at 20 fps"],"ru":["Digital Human Factory 28.0","Внешность и выражение лица","Цвет кожи","Цвет волос","Цвет одежды","Цвет фона","Выражение лица","Нейтральное","Радостное","Серьёзное","Моргание","Скачать трек движений JSON","Локальный процедурный персонаж, не фотореалистичный AI и не клонирование голоса. Трек содержит громкость и моргание, а не фонемы или нативный риг. Экспорт требует подготовленного разрешённого аудио.","Запустить тесты персонажа","Тесты пройдены","Ошибка тестов","Кадры с частотой 20 fps"],"uk":["Digital Human Factory 28.0","Зовнішність і вираз обличчя","Колір шкіри","Колір волосся","Колір одягу","Колір фону","Вираз обличчя","Нейтральний","Радісний","Серйозний","Моргання","Завантажити трек рухів JSON","Локальний процедурний персонаж, не фотореалістичний ШІ й не клонування голосу. Трек містить гучність і моргання, а не фонеми чи нативний риг. Експорт потребує підготовленого дозволеного аудіо.","Запустити тести персонажа","Тести пройдено","Помилка тестів","Кадри з частотою 20 fps"],"pl":["Digital Human Factory 28.0","Wygląd i mimika","Kolor skóry","Kolor włosów","Kolor ubrania","Kolor tła","Wyraz twarzy","Neutralny","Radosny","Poważny","Mruganie","Pobierz ścieżkę ruchu JSON","Lokalna postać proceduralna, nie fotorealistyczne AI ani klonowanie głosu. Ścieżka zawiera amplitudę i mruganie, nie fonemy ani natywny rig. Eksport wymaga przygotowanego nagrania za zgodą.","Uruchom testy postaci","Testy zaliczone","Błąd testów","Klatki przy 20 fps"]};
function humanAppearance(skin,hair,clothing,background,expression,blink){
 const colors=[skin,hair,clothing,background];if(colors.some(c=>typeof c!=="string"||!/^#[0-9a-f]{6}$/i.test(c))||!["neutral","happy","serious"].includes(expression)||typeof blink!=="boolean")throw Error("Invalid appearance");
 return {skin,hair,clothing,background,expression,blink};
}
function humanBlink(time,enabled){if(!enabled||!Number.isFinite(time)||time<0)return 0;const t=time%4;return t>=3.75?Math.max(0,1-Math.abs(t-3.875)/.125):0}
function humanMotionTrack(samples,appearance){
 if(!(samples instanceof Float32Array)||!samples.length||samples.length>960000||samples.some(x=>!Number.isFinite(x)))throw Error("Invalid audio");
 const style=humanAppearance(appearance.skin,appearance.hair,appearance.clothing,appearance.background,appearance.expression,appearance.blink);
 const frames=Array.from({length:Math.ceil(samples.length/800)},(_,i)=>({time_ms:i*50,mouth:Math.round(humanMouth(samples,i/20)*1000)/1000,blink:Math.round(humanBlink(i/20,style.blink)*1000)/1000}));
 return {version:1,format:"zer0life_procedural_motion",fps:20,duration_ms:samples.length/16,appearance:style,frames,phonemes:false,native_rig:false};
}
function humanFactoryTests(){
 const style=humanAppearance("#abcdef","#123456","#445566","#000000","happy",true),a=new Float32Array(1600),b=new Float32Array(1600).fill(.2);const silent=humanMotionTrack(a,style),loud=humanMotionTrack(b,style);
 const rejects=fn=>{try{fn();return false}catch{return true}};
 return [silent.frames.length===2,silent.frames.every(f=>f.mouth===0),loud.frames[0].mouth===1,loud.frames[1].time_ms===50,loud.duration_ms===100,humanBlink(3.875,true)===1,humanBlink(3.875,false)===0,humanBlink(0,true)===0,rejects(()=>humanAppearance("bad","#123456","#445566","#000000","happy",true)),rejects(()=>humanMotionTrack(new Float32Array([NaN]),style))];
}

function initDigitalHuman(){
 const words={"en":["Digital Human Lab","Create a fictional avatar and preview audio-driven mouth motion. This is a volume-based 2D preview, not AI lip-sync or NVIDIA inference. Files remain on this device.","Use only your own or authorized audio.","Choose PCM WAV (16-bit, mono/stereo, max 60 seconds / 24 MB)","Prepare audio","Play avatar","Pause","Download 16 kHz mono WAV","Download character brief","Character name","Character description","Audio ready","Invalid WAV or unsupported browser","Preparing locally…","NVIDIA Audio2Face SDK — advanced local installation; compatible GPU and models required.","Audio2Face official SDK","Permission to use the recording is required.","Audio duration","seconds","Character details are optional and exported only by you."],"ru":["Digital Human Lab","Создай вымышленного персонажа и посмотри движение рта под звук. Это 2D-предпросмотр по громкости, не AI-синхронизация губ и не NVIDIA inference. Файлы остаются на устройстве.","Используй только свою запись или аудио с разрешением.","Выбери PCM WAV (16 бит, моно/стерео, до 60 секунд / 24 МБ)","Подготовить аудио","Воспроизвести аватар","Пауза","Скачать WAV 16 кГц моно","Скачать бриф персонажа","Имя персонажа","Описание персонажа","Аудио готово","Неверный WAV или браузер не поддерживается","Локальная обработка…","NVIDIA Audio2Face SDK — продвинутая локальная установка; нужны совместимые GPU и модели.","Официальный Audio2Face SDK","Нужно разрешение на использование записи.","Длительность аудио","сек.","Описание персонажа необязательно и экспортируется только тобой."],"uk":["Digital Human Lab","Створи вигаданого персонажа й переглянь рух рота під звук. Це 2D-перегляд за гучністю, не ШІ-синхронізація губ і не NVIDIA inference. Файли залишаються на пристрої.","Використовуй власний або дозволений запис.","Обери PCM WAV (16 біт, моно/стерео, до 60 секунд / 24 МБ)","Підготувати аудіо","Відтворити аватар","Пауза","Завантажити WAV 16 кГц моно","Завантажити бриф персонажа","Ім’я персонажа","Опис персонажа","Аудіо готове","Невірний WAV або браузер не підтримується","Локальна обробка…","NVIDIA Audio2Face SDK — розширене локальне встановлення; потрібні сумісні GPU та моделі.","Офіційний Audio2Face SDK","Потрібен дозвіл на використання запису.","Тривалість аудіо","сек.","Опис необов’язковий; експортуєш лише ти."],"pl":["Digital Human Lab","Stwórz fikcyjną postać i podgląd ruchu ust według głośności. To podgląd 2D, nie synchronizacja AI ani inferencja NVIDIA. Pliki pozostają na urządzeniu.","Używaj własnych lub dozwolonych nagrań.","Wybierz PCM WAV (16 bitów, mono/stereo, do 60 s / 24 MB)","Przygotuj audio","Odtwórz awatar","Pauza","Pobierz WAV 16 kHz mono","Pobierz brief postaci","Imię postaci","Opis postaci","Audio gotowe","Nieprawidłowy WAV lub brak obsługi przeglądarki","Przetwarzanie lokalne…","NVIDIA Audio2Face SDK — zaawansowana instalacja lokalna; wymaga zgodnego GPU i modeli.","Oficjalny Audio2Face SDK","Wymagana zgoda na użycie nagrania.","Czas audio","s","Opis jest opcjonalny; eksportujesz go samodzielnie."]},w=()=>words[$("lang").value]||words.en;
 const add=(p,t,idx)=>{const e=document.createElement(t);if(idx!==undefined)e.textContent=w()[idx];p.append(e);return e};
 const root=add(document.querySelector("main"),"section"),localized=[];root.id="digital-human";
 const label=(p,t,i)=>{const e=add(p,t,i);localized.push([e,i]);return e};
 label(root,"h2",0);label(root,"p",1);
 const name=add(label(root,"label",9),"input");name.maxLength=80;
 const desc=add(label(root,"label",10),"textarea");desc.rows=3;desc.maxLength=1000;
 label(root,"p",20);
 const hw=()=>humanFactoryWords[$("lang").value]||humanFactoryWords.en,factoryLabels=[];
 const fl=(p,t,i)=>{const e=add(p,t);e.textContent=hw()[i];factoryLabels.push([e,i]);return e};
 fl(root,"h3",0);fl(root,"h4",1);
 const palette=["#e9b99a","#29213d","#7460ba","#15152a"].map((c,i)=>{const l=add(root,"label");fl(l,"span",i+2);const e=add(l,"input");e.type="color";e.value=c;return e});
 const expressionLabel=add(root,"label");fl(expressionLabel,"span",6);const expression=add(expressionLabel,"select");["neutral","happy","serious"].forEach((v,i)=>{const e=fl(expression,"option",7+i);e.value=v});expression.value="neutral";
 const blinkLabel=add(root,"label"),blink=add(blinkLabel,"input");blink.type="checkbox";blink.checked=true;blink.style.width="auto";fl(blinkLabel,"span",10);
 const appearance=()=>humanAppearance(...palette.map(e=>e.value),expression.value,blink.checked);
 const track=fl(root,"button",11);track.type="button";fl(root,"p",12);const test=fl(root,"button",13);test.type="button";const testResult=add(root,"p");testResult.setAttribute("role","status");
 test.onclick=()=>{const checks=humanFactoryTests();testResult.textContent=hw()[checks.every(Boolean)?14:15]+" · "+checks.filter(Boolean).length+"/"+checks.length};
 const consentLabel=add(root,"label"),consent=add(consentLabel,"input");consent.type="checkbox";consent.style.width="auto";consent.style.display="inline";label(consentLabel,"span",2);
 const file=add(label(root,"label",3),"input");file.type="file";file.accept=".wav,audio/wav,audio/x-wav";
 const prep=label(root,"button",4),play=label(root,"button",5),pause=label(root,"button",6),download=label(root,"button",7),brief=label(root,"button",8);
 const status=add(root,"p");status.setAttribute("role","status");
 const avatar=add(root,"canvas");avatar.width=480;avatar.height=360;avatar.setAttribute("aria-label","Procedural 2D avatar");const paint=avatar.getContext("2d");
 const audio=add(root,"audio");audio.controls=true;audio.preload="metadata";
 label(root,"p",15);const sdk=label(root,"a",16);sdk.href="https://github.com/NVIDIA/Audio2Face-3D-SDK";sdk.target="_blank";sdk.rel="noopener noreferrer";
 let data=null,url=null,busy=false,frame=0,state=0;
 function draw(m=0,time=0){if(!paint)return;const st=appearance(),closed=humanBlink(time,st.blink);
 const ellipse=(x,y,rx,ry,color)=>{paint.fillStyle=color;paint.beginPath();paint.ellipse(x,y,rx,ry,0,0,Math.PI*2);paint.fill()};
 paint.fillStyle=st.background;paint.fillRect(0,0,480,360);ellipse(240,335,116,75,st.clothing);ellipse(240,155,88,117,st.hair);ellipse(240,173,79,105,st.skin);ellipse(240,82,80,29,st.hair);
 for(const x of [211,269]){ellipse(x,142,8,Math.max(1,11*(1-closed)),st.hair);paint.strokeStyle=st.hair;paint.lineWidth=3;paint.beginPath();const tilt=st.expression==="serious"?(x<240?6:-6):0;paint.moveTo(x-12,121-tilt);paint.lineTo(x+12,121+tilt);paint.stroke()}
 if(m>.03)ellipse(240,213,st.expression==="happy"?30:25,3+19*m,"#874354");else{paint.strokeStyle="#874354";paint.lineWidth=3;paint.beginPath();paint.moveTo(216,213);paint.quadraticCurveTo(240,st.expression==="happy"?232:st.expression==="serious"?205:215,264,213);paint.stroke()}
 }
 function controls(){prep.disabled=busy||!consent.checked||!file.files.length;file.disabled=consent.disabled=busy;play.disabled=busy||!data;pause.disabled=!data||audio.paused;download.disabled=busy||!data;track.disabled=busy||!data||!consent.checked;status.textContent=state?w()[state]+(state===11&&data?" · "+w()[18]+": "+(data.length/16000).toFixed(2)+" "+w()[19]:""):"";}
 function clear(){audio.pause();audio.removeAttribute("src");audio.load();if(url)URL.revokeObjectURL(url);url=null;data=null;cancelAnimationFrame(frame);draw();}
 function saveBlob(blob,filename){const u=URL.createObjectURL(blob),a=document.createElement("a");a.href=u;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(u),1500);}
 file.onchange=consent.onchange=()=>{clear();state=0;controls()};
 prep.onclick=async()=>{if(busy||!consent.checked||!file.files.length)return;clear();busy=true;state=13;controls();try{const f=file.files[0];if(f.size>24*1024*1024)throw Error();data=await humanResample(humanReadPCM(await f.arrayBuffer()));const wav=humanWriteWAV(data);url=URL.createObjectURL(new Blob([wav],{type:"audio/wav"}));audio.src=url;state=11}catch(e){clear();state=12}finally{busy=false;controls()}};
 play.onclick=()=>audio.play().catch(()=>{state=12;controls()});pause.onclick=()=>audio.pause();
 function tick(){draw(humanMouth(data,audio.currentTime),audio.currentTime);if(!audio.paused&&!audio.ended)frame=requestAnimationFrame(tick)}
 audio.onplay=()=>{cancelAnimationFrame(frame);tick();controls()};audio.onpause=audio.onended=()=>{cancelAnimationFrame(frame);draw();controls()};
 download.onclick=()=>{if(data&&consent.checked)saveBlob(new Blob([humanWriteWAV(data)],{type:"audio/wav"}),"zer0life-audio2face-16k.wav")};
 for(const e of [...palette,expression,blink]){e.addEventListener("input",()=>draw(humanMouth(data,audio.currentTime),audio.currentTime));e.addEventListener("change",()=>draw(humanMouth(data,audio.currentTime),audio.currentTime))}
 track.onclick=()=>{if(!data||!consent.checked||busy)return;try{const motion=humanMotionTrack(data,appearance());saveBlob(new Blob([JSON.stringify(motion,null,2)],{type:"application/json"}),"zer0life-character-motion.json")}catch{state=12;controls()}};
 brief.onclick=()=>saveBlob(new Blob([JSON.stringify({version:2,character:name.value.trim(),description:desc.value.trim(),appearance:appearance(),audio_prepared:!!data,format:"PCM16 mono 16000 Hz",preview:"procedural_2d_volume_only",motion_format:"zer0life_procedural_motion"},null,2)],{type:"application/json"}),"zer0life-character-brief.json");
 $("lang").addEventListener("change",()=>{for(const [e,i] of localized){if(e.tagName==="LABEL"){const text=e.firstChild;if(text&&text.nodeType===3)text.nodeValue=w()[i]}else e.textContent=w()[i]}for(const [e,i] of factoryLabels)e.textContent=hw()[i];testResult.textContent="";controls()});
 window.addEventListener("pagehide",clear);draw();controls();
}
initDigitalHuman();
