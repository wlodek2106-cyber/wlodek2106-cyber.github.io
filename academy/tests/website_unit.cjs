const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const js=fs.readFileSync(path.join(__dirname,"../backend/website-builder.js"),"utf8");new vm.Script(js);
const build=vm.runInNewContext(js.slice(0,js.indexOf("const $=id"))+"\nbuildSite");
const s={brand:"<script>alert(1)</script>",title:'A" & B',description:'"><img src=x>',about:"<svg onload=alert(1)>",services:"One | two\nThree | four",email:"a@example.com",accent:"#123abc",theme:"light",lang:"ru"};
const h=build(s);assert.ok(!h.includes("<script>")&&!h.includes("<img src=x>")&&!h.includes("<svg"));assert.ok(h.includes("mailto:a@example.com")&&h.includes("О нас")&&h.includes("&quot;"));assert.equal((h.match(/<article>/g)||[]).length,2);
assert.ok(!build({...s,email:"a@example.com?subject=x",accent:"red;}</style><script>"}).includes("mailto:"));assert.ok(!build({...s,accent:"red;}</style><script>"}).includes("<script>"));
assert.ok(build({...s,lang:"bad"}).includes('lang="en"'));console.log("PASS: safe HTML export, metadata, localization, contact validation");
