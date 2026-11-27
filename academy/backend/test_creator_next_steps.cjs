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
