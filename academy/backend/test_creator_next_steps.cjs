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

const deliveryEnd=source.indexOf("const productionDeliveryWords=",productionStart);
assert.ok(deliveryEnd>productionStart);
const delivery=vm.runInNewContext(source.slice(productionStart,deliveryEnd)+"\n({report:productionDeliveryReport,plans:productionPlans,keys:qualityKeys,entry:productionAssetEntry})");
for(const [kind,ids] of Object.entries(delivery.plans)){
 const review={revision:2,checks:Object.fromEntries(Array.from(delivery.keys,k=>[k,"pass"])),notes:"private internal note"};
 const final=delivery.entry("final.pdf","document",1,"owned",true),draft=delivery.entry("internal","document",1,"restricted",false),unknown=delivery.entry("image","image",1,"unknown",true);
 test("delivery ready and privacy "+kind,()=>{
  const r=delivery.report(kind,ids.filter(x=>x!==6),review,[final,draft]);
  assert.equal(r.self_recorded_ready_for_handoff,true);
  assert.equal(r.assets.length,1);assert.equal(r.assets[0].name,"final.pdf");
  assert.equal(r.revision,2);assert.equal(r.files_included,false);assert.equal(r.client_accepted,false);
  assert.equal(r.rights_verified,false);assert.equal(r.verified_by_academy,false);
  assert.equal(JSON.stringify(r).includes("private internal note"),false);
 });
 for(const [checked,items,key] of [[[],[final],"quality"],[ids,[],"no_assets"],[ids,[unknown],"rights"]]){
  test("delivery blocker "+kind+" "+key,()=>{
   const r=delivery.report(kind,checked,review,items);
   assert.equal(r.self_recorded_ready_for_handoff,false);assert.ok(r.blockers.includes(key));
  });
 }
}

const learningStart=source.indexOf("const learningOSLanguages=");
const learningEnd=source.indexOf("const learningOSWords=",learningStart);
assert.ok(learningStart>=0&&learningEnd>learningStart);
const learning=vm.runInNewContext(source.slice(learningStart,learningEnd)+"\n({week:learningOSWeek,prompt:learningOSPrompt})");
for(const minutes of [15,30,60])for(const sessions of [3,5,7])for(const level of ["foundation","reinforce","challenge"]){
 test("learning schedule "+minutes+" "+sessions+" "+level,()=>{
  const w=learning.week(minutes,sessions,level);
  assert.equal(w.total_minutes,minutes*sessions);
  assert.equal(w.items.length,sessions);
  assert.equal(w.items.at(-1).mode,"commercial");
  assert.equal(w.items.every((x,i)=>x.session===i+1&&x.minutes===minutes),true);
 });
}
for(const mode of ["explain","recall","practice","commercial"])for(const lang of ["en","ru","uk","pl"]){
 test("learning coaching "+mode+" "+lang,()=>{
  const p=learning.prompt(1,"foundation",mode,lang,"Example task","Example attempt");
  assert.ok(p.includes("Example task")&&p.includes("Example attempt"));
  assert.ok(p.includes("not an official grade"));
 });
}
test("learning rejects unsupported schedule and prompts",()=>{
 assert.throws(()=>learning.week(90,5,"foundation"));
 assert.throws(()=>learning.week(30,4,"foundation"));
 assert.throws(()=>learning.week(30,5,"unknown"));
 assert.throws(()=>learning.prompt(0,"foundation","practice","en","Task",""));
 assert.throws(()=>learning.prompt(1,"foundation","exam","en","Task",""));
 assert.throws(()=>learning.prompt(1,"foundation","practice","constructor","Task",""));
 assert.throws(()=>learning.prompt(1,"foundation","practice","en","",""));
 assert.throws(()=>learning.prompt(1,"foundation","practice","en","Task","x".repeat(1201)));
});

const reviewStart=freeSource.indexOf("const reviewIntervals=");
const reviewEnd=freeSource.indexOf("const reviewWords=",reviewStart);
assert.ok(reviewStart>=0&&reviewEnd>reviewStart);
const review=vm.runInNewContext(freeSource.slice(reviewStart,reviewEnd)+"\n({item:teacherReviewItem,rate:teacherReviewRate,snapshot:teacherReviewSnapshot,parse:parseTeacherReview,prompt:teacherReviewPrompt})");
for(const [stage,interval] of [1,3,7,14,30].entries()){
 test("review recall interval "+stage,()=>{
  const x=review.item("Concept","My attempt",stage,100);
  const r=review.rate(x,true,100);
  assert.equal(r.due,100+interval);assert.equal(r.stage,Math.min(stage+1,4));
 });
 test("review failed recall "+stage,()=>{
  const r=review.rate(review.item("Concept","Attempt",stage,100),false,100);
  assert.equal(r.due,101);assert.equal(r.stage,0);
 });
}
test("review lesson-bound export and import",()=>{
 const s=review.snapshot(4,[review.item("Concept","Attempt",0,100)]);
 assert.equal(JSON.stringify(review.parse(s,4)),JSON.stringify(s));
 assert.throws(()=>review.parse(s,5));
 assert.throws(()=>review.parse({...s,official_grade:100},4));
});
test("review rejects invalid entries and premature ratings",()=>{
 assert.throws(()=>review.item("","Attempt",0,100));
 assert.throws(()=>review.item("Concept","x".repeat(501),0,100));
 assert.throws(()=>review.item("Concept","",5,100));
 assert.throws(()=>review.rate(review.item("Concept","",0,101),true,100));
 assert.throws(()=>review.snapshot(1,Array(31).fill(review.item("Concept","",0,100))));
});
test("review prompts request feedback and withhold solutions",()=>{
 const x=review.item("Concept","Attempt",0,100);
 assert.match(review.prompt(x,"retry"),/without revealing a solution/);
 assert.match(review.prompt(x,"feedback"),/supported mistakes/);
 assert.match(review.prompt(x,"feedback"),/reference data/);
 assert.throws(()=>review.prompt(x,"exam"));
});

const mockStart=source.indexOf("const mockExamKey="),mockEnd=source.indexOf("function learningMockExamDesign(",mockStart);
assert.ok(mockStart>=0&&mockEnd>mockStart);
const mock=vm.runInNewContext(source.slice(mockStart,mockEnd)+"\n({grade:learningMockGrade,key:mockExamKey,questions:mockExamQuestions,words:mockExamWords})");
test("practice exam complete but never grants credentials",()=>{
 const x=mock.grade(mock.key);assert.equal(x.complete,true);assert.equal(x.percent,100);assert.equal(x.official_grade,false);assert.equal(x.certificate_eligible,false);
});
test("practice exam incomplete and missed topics",()=>{
 const x=mock.grade({brief:0,verify:2});assert.equal(x.answered,2);assert.equal(x.correct,1);assert.equal(x.percent,17);assert.equal(x.complete,false);assert.equal(x.review.length,5);
 assert.ok(x.review.includes("brief"));assert.equal(x.review.includes("verify"),false);
});
test("practice exam validates answer fields",()=>{
 for(const x of [null,[],{constructor:1},{brief:"1"},{brief:3},{brief:-1},{official_grade:100}])assert.throws(()=>mock.grade(x));
});
for(const lang of ["en","ru","uk","pl"])test("practice exam translations "+lang,()=>{
 assert.equal(mock.questions[lang].length,6);assert.equal(mock.words[lang].length,14);
 for(const row of mock.questions[lang]){assert.equal(row.length,5);assert.ok(row.every(x=>typeof x==="string"&&x.trim()))}
});
