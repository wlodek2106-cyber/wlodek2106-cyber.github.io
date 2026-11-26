"use strict";
const moduleAuth=(()=>{
 const words={
 en:["Sign in with passkey","Use a passkey previously registered in Academy settings. Enter your 2FA or recovery code first if enabled.","Passkey sign-in failed or was cancelled. Use your password or check the registered key and 2FA.","Back to Command Center"],
 ru:["Войти с Passkey / Face ID","Используйте Passkey, ранее зарегистрированный в настройках Академии. Если включена 2FA, сначала введите код или резервный код.","Вход с Passkey не выполнен или отменён. Войдите по паролю или проверьте ключ и 2FA.","В Command Center"],
 uk:["Увійти з Passkey / Face ID","Використовуйте Passkey, раніше зареєстрований у налаштуваннях Академії. Якщо ввімкнено 2FA, спочатку введіть код або резервний код.","Вхід з Passkey не виконано або скасовано. Увійдіть за паролем або перевірте ключ і 2FA.","До Command Center"],
 pl:["Zaloguj z Passkey / Face ID","Użyj klucza wcześniej zarejestrowanego w ustawieniach Akademii. Jeśli włączono 2FA, najpierw wpisz kod lub kod zapasowy.","Logowanie kluczem nie powiodło się lub anulowano. Użyj hasła albo sprawdź klucz i 2FA.","Do Command Center"]};
 const alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
 function encode(buffer){const bytes=new Uint8Array(buffer);let bits=0,v=0,out="";for(const byte of bytes){v=(v<<8)|byte;bits+=8;while(bits>=6){bits-=6;out+=alphabet[(v>>bits)&63]}}if(bits)out+=alphabet[(v<<(6-bits))&63];return out}
 function decode(s){if(typeof s!=="string"||!/^[A-Za-z0-9_-]+$/.test(s)||s.length>8192||s.length%4===1)throw Error("Invalid WebAuthn data");let bits=0,v=0;const out=[];for(const ch of s){v=(v<<6)|alphabet.indexOf(ch);bits+=6;if(bits>=8){bits-=8;out.push((v>>bits)&255)}}if(bits&&(v&((1<<bits)-1)))throw Error("Invalid padding");return Uint8Array.from(out)}
 function options(raw){if(!raw||typeof raw!=="object"||raw.rpId!==location.hostname||raw.userVerification!=="required")throw Error("Unexpected relying party");return {...raw,challenge:decode(raw.challenge),...(raw.allowCredentials?{allowCredentials:raw.allowCredentials.map(x=>({...x,id:decode(x.id)}))}:{})}}
 function serialize(c){if(!c||c.type!=="public-key"||!c.response?.userHandle)throw Error("Invalid credential");return {id:c.id,rawId:encode(c.rawId),type:c.type,response:{clientDataJSON:encode(c.response.clientDataJSON),authenticatorData:encode(c.response.authenticatorData),signature:encode(c.response.signature),userHandle:encode(c.response.userHandle)},clientExtensionResults:{}}}
 function supported(){return location.protocol==="https:"&&location.hostname==="zer0life-academy.onrender.com"&&!!window.PublicKeyCredential&&typeof navigator.credentials?.get==="function"}
 async function signIn(api,code){if(!supported())throw Error("Passkey unavailable");const start=await api("/passkeys/login/begin");const c=await navigator.credentials.get({publicKey:options(start.options)});return api("/passkeys/login/finish",{id:start.id,credential:serialize(c),code:code||null})}
 function mount(run,api,finish){const $=id=>document.getElementById(id),label=()=>words[$("lang").value]||words.en;const btn=$("passkeySignIn"),hint=$("passkeyHint");function translate(){btn.textContent=label()[0];hint.textContent=label()[1];const a=$("commandBack");if(a){a.textContent=label()[3];a.href="/command-center?lang="+encodeURIComponent($("lang").value)}}
 translate();$("lang").addEventListener("change",translate);btn.hidden=hint.hidden=!supported();
 let active=false;btn.onclick=()=>{if(active||btn.disabled)return;return run(async()=>{active=true;btn.disabled=true;$("signIn").disabled=true;try{const result=await signIn(api,$("code").value);await finish(result)}catch{$("status").textContent=label()[2]}finally{active=false;btn.disabled=false;$("signIn").disabled=false;$("password").value="";$("code").value=""}})};
 for(const id of ["login","password","code"])$(id).addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.isComposing&&!$("signIn").disabled&&!active){e.preventDefault();$("signIn").click()}});
 }
 return {mount,encode,decode,options,serialize};
})();
