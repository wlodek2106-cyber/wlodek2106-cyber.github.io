const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const js=fs.readFileSync(path.join(__dirname,"../backend/music-studio.js"),"utf8");new vm.Script(js);
const {synth,wav}=vm.runInNewContext(js.slice(0,js.indexOf("const $=id"))+"\n({synth,wav})");
const p=Array.from({length:5},()=>Array(16).fill(true));
for(const effect of ["music","rise","impact","click"]){const {samples,rate}=synth(p,120,4,36,effect);assert.equal(samples.length,effect==="music"?176400:44100);assert.ok(samples.some(x=>x!==0));assert.ok(samples.every(x=>Number.isFinite(x)&&Math.abs(x)<=1));const b=wav(samples,rate),v=new DataView(b);assert.equal(v.getUint32(24,true),22050);assert.equal(v.getUint32(40,true),samples.length*2);assert.equal(b.byteLength,44+samples.length*2);}
const empty=synth(Array.from({length:5},()=>Array(16).fill(false)),120,1,36);assert.ok(empty.samples.every(x=>x===0));console.log("PASS: synthesizer and PCM WAV");
