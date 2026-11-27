"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const source=fs.readFileSync(path.join(__dirname,"academy-aurora.js"),"utf8");
new vm.Script(source); // Parse the entire dashboard, without executing DOM code.
const start=source.indexOf("function creatorNextSteps(x){");
const end=source.indexOf("const creatorNextActions=",start);
assert.ok(start>=0&&end>start);
const {next,valid}=vm.runInNewContext(source.slice(start,end)+"\n({next:creatorNextSteps,valid:validCreatorEvidence})");
const fixture={private:true,official_credential:false,payment_verified:false,submitted:0,reviewed:0,project_lessons:0,completed_orders:0,approved_reviews:0,completed_lessons:0,listing_status:"none",certificate_issued:false,showcase_published:false,rating:null};
const cases=[
 [{},[1,3,6]],
 [{submitted:1,reviewed:0,listing_status:"pending"},[2,9,6]],
 [{submitted:1,reviewed:1,listing_status:"blocked"},[10,6]],
 [{submitted:1,reviewed:1,listing_status:"approved"},[4,6]],
 [{submitted:1,reviewed:1,listing_status:"approved",completed_orders:1,certificate_issued:true},[5,7]],
 [{submitted:1,reviewed:1,listing_status:"approved",completed_orders:1,approved_reviews:1,certificate_issued:true,showcase_published:true,rating:5},[8]]
];
for(const [patch,expected] of cases)test("career steps "+expected.join(","),()=>{
 const x={...fixture,...patch};
 assert.equal(valid(x),true);
 assert.deepEqual(Array.from(next(x)),expected);
});
for(const patch of [null,{private:false},{payment_verified:true},{submitted:-1},{reviewed:1},{listing_status:"unknown"},{rating:6},{showcase_published:true},{completed_lessons:"1"}])test("invalid evidence "+JSON.stringify(patch),()=>{
 assert.equal(valid(patch===null?null:{...fixture,...patch}),false);
});

const mentorStart=source.indexOf("const mentorTasks=");
const mentorEnd=source.indexOf("const careerMentorWords=",mentorStart);
assert.ok(mentorStart>=0&&mentorEnd>mentorStart);
const mentor=vm.runInNewContext(source.slice(mentorStart,mentorEnd)+"\n({build:buildCareerMentorPrompt,tasks:mentorTasks,languages:mentorLanguages})");
for(const task of Object.keys(mentor.tasks))for(const language of Object.keys(mentor.languages)){
 test("mentor "+task+" "+language,()=>{
   const p=mentor.build(task,language,"Example brief");
   assert.ok(p.includes(mentor.tasks[task]));
   assert.ok(p.includes(mentor.languages[language]));
   assert.ok(p.includes("Example brief"));
   assert.ok(p.includes("do not fabricate credentials"));
 });
}
for(const args of [["constructor","en",""],["portfolio","bad",""],["portfolio","en","a".repeat(1201)],["portfolio","en",null]]){
 test("mentor rejects invalid "+String(args[0])+" "+String(args[1])+" "+String(args[2]).length,()=>{
   assert.throws(()=>mentor.build(...args));
 });
}

test("acquisition task coverage and translations",()=>{
 const start=source.indexOf("const careerMentorTaskLabels=");
 const end=source.indexOf("function careerMentorDesign(",start);
 assert.ok(start>=0&&end>start);
 const localized=vm.runInNewContext(source.slice(start,end)+"\n({labels:careerMentorTaskLabels,links:careerMentorLinkWords})");
 for(const lang of Object.keys(mentor.languages)){
   assert.deepEqual(Object.keys(localized.labels[lang]).sort(),Object.keys(mentor.tasks).sort());
   assert.equal(localized.links[lang].length,5);
   for(const label of Object.values(localized.labels[lang]))assert.ok(typeof label==="string"&&label.trim());
 }
 for(const k of ["audience","offer","promotion","outreach","pipeline"])assert.ok(Object.hasOwn(mentor.tasks,k));
 assert.match(mentor.tasks.outreach,/Do not scrape/);
 assert.match(mentor.tasks.audience,/Do not claim to have searched/);
});

const agencySource=fs.readFileSync(path.join(__dirname,"agency.js"),"utf8");
new vm.Script(agencySource);
const agencyStart=agencySource.indexOf("function agencyTaskFlags("),agencyEnd=agencySource.indexOf("const agencyOpsWords=",agencyStart);
assert.ok(agencyStart>=0&&agencyEnd>agencyStart);
const taskView=vm.runInNewContext(agencySource.slice(agencyStart,agencyEnd)+"\nagencyTaskView");
const agencyTasks=[{id:1,status:"done",project:7,assignee:1,due:"2026-11-25"},{id:2,status:"todo",project:7,depends_on:1,assignee:null,due:"2026-11-26"},{id:3,status:"doing",project:7,depends_on:2,assignee:1,due:"2026-11-27"},{id:4,status:"todo",project:null,depends_on:99,assignee:null,due:null}];
const today="2026-11-27";
test("agency aggregate counts",()=>assert.deepEqual({...taskView(agencyTasks,"all","all",today).counts},{all:4,todo:2,doing:1,done:1,overdue:1,blocked:2,unassigned:2}));
for(const [project,filter,date,expected] of [["7","blocked",today,[3]],["none","all",today,[4]],["7","overdue",today,[2]],["all","unassigned",today,[2,4]],["all","done",today,[1]],["all","overdue",null,[]],["7","unknown",today,[]]]){
 test("agency filter "+project+" "+filter+" "+date,()=>assert.deepEqual(Array.from(taskView(agencyTasks,project,filter,date).visible),expected));
}
test("agency empty workspace",()=>assert.deepEqual({...taskView([],"all","all",today).counts},{all:0,todo:0,doing:0,done:0,overdue:0,blocked:0,unassigned:0}));

const productionStart=source.indexOf("const productionPlans=");
const productionEnd=source.indexOf("function productionOSDesign(",productionStart);
assert.ok(productionStart>=0&&productionEnd>productionStart);
const production=vm.runInNewContext(source.slice(productionStart,productionEnd)+"\n({plans:productionPlans,state:productionPlanState,routes:productionStageRoutes,words:productionOSWords})");
for(const [kind,stages] of Object.entries(production.plans)){
 test("production empty "+kind,()=>{const p=production.state(kind,[]);assert.equal(p.completed,0);assert.equal(p.total,stages.length);assert.equal(p.next,stages[0])});
 test("production partial "+kind,()=>{const p=production.state(kind,[stages[0]]);assert.equal(p.completed,1);assert.equal(p.next,stages[1])});
 test("production complete "+kind,()=>{const p=production.state(kind,[...stages,...stages,999,"0"]);assert.equal(p.completed,stages.length);assert.equal(p.next,null)});
}
test("production rejects invalid inputs",()=>{assert.throws(()=>production.state("constructor",[]));assert.throws(()=>production.state("film",null))});
test("production translations and stage routes",()=>{
 assert.equal(Object.keys(production.plans).length,6);
 for(const lang of ["en","ru","uk","pl"]){assert.equal(production.words[lang].length,31);for(const label of production.words[lang])assert.ok(label.trim())}
 for(const stages of Object.values(production.plans)){assert.equal(new Set(stages).size,stages.length);for(const id of stages)assert.ok(production.routes[id].startsWith("/"))}
});

const pipeline=vm.runInNewContext(source.slice(productionStart,productionEnd)+"\n({handoff:productionHandoff,snapshot:productionSnapshot,parse:parseProductionSnapshot})");
const freeSource=fs.readFileSync(path.join(__dirname,"free-ai.js"),"utf8");
const handStart=freeSource.indexOf("function handoff(team,title)"),handEnd=freeSource.indexOf("const factoryWords=",handStart);
assert.ok(handStart>=0&&handEnd>handStart);
const parseHandoff=vm.runInNewContext(freeSource.slice(handStart,handEnd)+"\nparseHandoff");
for(const [kind,stages] of Object.entries(production.plans)){
 for(const id of stages)test("production handoff "+kind+" "+id,()=>{
   const payload=pipeline.handoff(kind,id,"Example stage");
   assert.equal(parseHandoff(payload).task,"Example stage");
   assert.equal(parseHandoff(payload).team,payload.team);
 });
 test("production project snapshot roundtrip "+kind,()=>{
   const p=pipeline.snapshot(kind,[stages[0]]);
   assert.equal(JSON.stringify(pipeline.parse(p)),JSON.stringify(p));
 });
}
for(const value of [null,{}, {version:1,kind:"zer0life_production_plan",project:"film",checked:[99]},{version:1,kind:"zer0life_production_plan",project:"film",checked:[0,0]},{version:1,kind:"zer0life_production_plan",project:"constructor",checked:[]}]){
 test("production rejects snapshot "+JSON.stringify(value),()=>assert.throws(()=>pipeline.parse(value)));
}
test("production rejects wrong stage and unsafe title",()=>{
 assert.throws(()=>pipeline.handoff("film",13,"Example"));
 assert.throws(()=>pipeline.handoff("film",0,""));
 assert.throws(()=>pipeline.handoff("film",0,"x".repeat(161)));
 assert.throws(()=>pipeline.handoff("film",0,"a\n b"));
});

const qualityEnd=source.indexOf("const productionQualityWords=",productionStart);
assert.ok(qualityEnd>productionStart);
const quality=vm.runInNewContext(source.slice(productionStart,qualityEnd)+"\n({report:productionQualityReport,keys:qualityKeys,plans:productionPlans})");
const allPass=Object.fromEntries(Array.from(quality.keys,k=>[k,"pass"]));
for(const [kind,ids] of Object.entries(quality.plans)){
 test("production quality ready "+kind,()=>{
  const r=quality.report(kind,ids.filter(x=>x!==6),1,allPass,"review");
  assert.equal(r.self_recorded_ready_for_handoff,true);
  assert.equal(r.client_accepted,false);
  assert.equal(r.verified_by_academy,false);
 });
 test("production quality incomplete "+kind,()=>assert.equal(quality.report(kind,[],1,allPass,"").self_recorded_ready_for_handoff,false));
 test("production quality failed "+kind,()=>assert.equal(quality.report(kind,ids,1,{...allPass,rights:"fail"},"").self_recorded_ready_for_handoff,false));
}
test("quality rejects invalid version, checks, notes and stage IDs",()=>{
 assert.throws(()=>quality.report("film",[],0,allPass,""));
 assert.throws(()=>quality.report("film",[],10000,allPass,""));
 assert.throws(()=>quality.report("film",[],1,{...allPass,unknown:"pass"},""));
 assert.throws(()=>quality.report("film",[],1,{...allPass,scope:"approved"},""));
 assert.throws(()=>quality.report("film",[],1,allPass,"a".repeat(1201)));
 assert.throws(()=>quality.report("film",[99],1,allPass,""));
});

const assetEnd=source.indexOf("const productionAssetWords=",productionStart);
assert.ok(assetEnd>productionStart);
const asset=vm.runInNewContext(source.slice(productionStart,assetEnd)+"\n({entry:productionAssetEntry,manifest:productionAssetManifest,plans:productionPlans})");
for(const kind of Object.keys(asset.plans)){
 test("asset register "+kind,()=>{
 const a=asset.entry("video.mp4","video",1,"licensed",true);
 const b=asset.entry("image.png","image",2,"unknown",true);
 const c=asset.entry("draft.txt","document",1,"restricted",false);
 const report=asset.manifest(kind,[a,b,c]);
 assert.equal(report.selected_count,2);
 assert.equal(report.selected_needing_rights_review,1);
 assert.equal(report.files_included,false);
 assert.equal(report.rights_verified,false);
 assert.equal(asset.manifest(kind,[a]).selected_rights_self_recorded,true);
 });
}
test("asset rejects invalid paths and values",()=>{
 assert.throws(()=>asset.entry("../secret.txt","document",1,"owned",true));
 assert.throws(()=>asset.entry("a","unknown",1,"owned",true));
 assert.throws(()=>asset.entry("a","image",0,"owned",true));
 assert.throws(()=>asset.entry("a","image",1,"verified",true));
 assert.throws(()=>asset.entry("a","image",1,"owned","true"));
});
test("asset rejects duplicates and over-limit manifest",()=>{
 const a=asset.entry("a","image",1,"owned",true);
 assert.throws(()=>asset.manifest("film",[a,a]));
 assert.throws(()=>asset.manifest("film",Array(101).fill(a)));
 assert.throws(()=>asset.manifest("constructor",[a]));
 assert.throws(()=>asset.manifest("film",[{...a,path:"private"}]));
});
