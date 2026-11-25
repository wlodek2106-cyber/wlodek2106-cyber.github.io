const assert=require("node:assert/strict"),fs=require("node:fs"),vm=require("node:vm"),path=require("node:path");
const html=fs.readFileSync(path.join(__dirname,"../backend/dashboard.html"),"utf8");
const start=html.indexOf("function marketingDraft("),end=html.indexOf("function marketingExport(",start);
assert.ok(start>=0&&end>start);
const sandbox={};vm.createContext(sandbox);vm.runInContext(html.slice(start,end),sandbox);
const base={lang:"ru",platform:"instagram",format:"video",duration:30,topic:"AI video",audience:"Creators",benefit:"Demo clip",cta:"Explore"};
for(const lang of ["en","ru","uk","pl"])for(const duration of [15,30,60]){
 const d=sandbox.marketingDraft({...base,lang,duration});
 assert.ok(d.includes("0–"+Math.floor(duration*.2)+"s"));
 assert.ok(d.includes("–"+duration+"s"));
 assert.ok(d.includes("Demo clip"));
}
assert.ok(sandbox.marketingDraft({...base,format:"carousel"}).includes("4. "));
assert.ok(!sandbox.marketingDraft({...base,format:"post"}).includes("0–6s"));
for(const bad of [{topic:""},{format:"auto"},{duration:10},{lang:"xx"},{benefit:"x".repeat(501)}])assert.throws(()=>sandbox.marketingDraft({...base,...bad}));
assert.equal(sandbox.academyCampaignLink("instagram","ru"),"https://zer0life-academy.onrender.com/dashboard?register=1&lang=ru&campaign=instagram");
assert.throws(()=>sandbox.academyCampaignLink("https://evil.test","ru"));
console.log("PASS: local marketing draft templates and campaign URLs");
