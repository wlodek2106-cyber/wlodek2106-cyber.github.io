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
