const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const js=fs.readFileSync(path.join(__dirname,"../backend/ai-workspace.js"),"utf8");new vm.Script(js);
const {catalog,selectTools}=vm.runInNewContext(js.slice(0,js.indexOf("const $=id"))+"\n({catalog,selectTools})");
assert.equal(catalog.length,12);assert.equal(new Set(catalog.map(x=>x[0])).size,12);
assert.equal(selectTools(catalog,"музыки","all",false,new Set(),1)[0][0],"music");assert.equal(selectTools(catalog,"","business",false,new Set(),0).length,3);
assert.equal(selectTools(catalog,"","all",true,new Set(["design"]),0)[0][0],"design");assert.equal(selectTools(catalog,"not-a-tool","all",false,new Set(),0).length,0);
assert.ok(catalog.every(x=>/^\/[a-z-]+$/.test(x[3])&&x[5].length===4));
console.log("PASS: workspace catalog, category, localized search and favorites");
