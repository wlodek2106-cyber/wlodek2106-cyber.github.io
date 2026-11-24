const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const js=fs.readFileSync(path.join(__dirname,"../backend/free-ai.js"),"utf8");
new vm.Script(js.replace('await import("https://esm.run/@mlc-ai/web-llm@0.2.89")','await Promise.resolve(null)'));
const start=js.indexOf("async function runAgentTeam("),end=js.indexOf("\nconst teamWords=",start);
assert.ok(start>=0&&end>start);
const run=vm.runInNewContext("("+js.slice(start,end)+")");
(async()=>{
 const calls=[],emits=[];
 async function* chunks(){yield {choices:[{delta:{content:"draft"}}]};}
 const result=await run("Task","Russian",async m=>{calls.push(m);return chunks()},()=>false,(...a)=>emits.push(a));
 assert.equal(result.results.length,3);
 assert.equal(calls.length,3);
 assert.ok(calls[1][1].content.includes("planner"));
 assert.ok(calls[2][1].content.includes("worker"));
 assert.ok(calls[0][0].content.includes("Russian"));
 assert.equal(emits.filter(x=>x[2]).length,3);
 let cancel=false;let count=0;
 const stopped=await run("Task","English",async()=>{count++;return chunks()},()=>cancel,(_r,_t,start)=>{if(!start)cancel=true});
 assert.equal(stopped.stopped,true);assert.equal(count,1);
 await assert.rejects(()=>run("Task","English",async function*(){},()=>false,()=>{}),/Empty response/);
 console.log("PASS: sequential agents, context, cancellation, empty output");
})().catch(e=>{console.error(e);process.exitCode=1});
