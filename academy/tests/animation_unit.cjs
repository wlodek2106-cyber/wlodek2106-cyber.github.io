const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const js=fs.readFileSync(path.join(__dirname,"../backend/animation-studio.js"),"utf8");new vm.Script(js);
const code=js.slice(0,js.indexOf("const $=id"));
const {frameAt,cover}=vm.runInNewContext(code+"\n({frameAt,cover})");
assert.equal(frameAt(0,2,3).index,0);assert.equal(frameAt(3,2,3).index,1);assert.equal(frameAt(6,2,3).index,1);
for(const mode of ["zoom","pan","still"]){const b=cover(720,1280,1920,1080,.5,mode);assert.ok(b.w>=720&&b.h>=1280);assert.ok(b.x<=0&&b.y<=0);}
console.log("PASS: animation syntax, timing and cover geometry");
