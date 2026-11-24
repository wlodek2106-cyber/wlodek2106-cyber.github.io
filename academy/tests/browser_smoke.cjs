const {chromium}=require("playwright");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const html=fs.readFileSync(path.join(__dirname,"../backend/dashboard.html"),"utf8");
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
 for(const [role,width] of [["unpaid",1280],["paid",390],["owner",1280]]){
 const context=await browser.newContext({viewport:{width,height:844},serviceWorkers:"block"});
 const page=await context.newPage();
 const errors=[], unexpected=[];
 page.on("pageerror",e=>errors.push(e.message));
 let signedIn=false;
 const calls=[];
 await context.route("**/*",async route=>{
  const url=new URL(route.request().url());
  if(url.origin!=="http://academy.test")return route.abort();
  const p=url.pathname;
  if(p==="/dashboard")return route.fulfill({contentType:"text/html",body:html});
  if(p==="/academy-icon.svg"||p==="/manifest.webmanifest"||p==="/favicon.ico")return route.fulfill({status:204});
  calls.push(p);
  if(p==="/login"){signedIn=true;return route.fulfill({json:{token:"test-only-token"}})}
  if(!signedIn)return route.fulfill({status:403,json:{error:"Access denied"}});
  const paid=role!=="unpaid",owner=role==="owner";
  const responses={
    "/progress":{paid,plan:paid?"starter":null,lessons:Array.from({length:30},(_,i)=>({day:i+1,completed:false,unlocked:paid&&i===0}))},
    "/account/me":{id:123},
    "/admin/network-access":{allowed:owner},
    "/checkout/prices":{discount_percent:0,prices:{starter:199000000,pro:499000000,vip:999000000}},
    "/checkout/active":{invoice:null},
    "/business":{clients:[],orders:[],totals:{agreed_cents:"0",received_cents:"0",expense_cents:"0",outstanding_cents:"0",cash_margin_cents:"0"}},
    "/portfolio":{items:[]},
    "/lessons/1/en":{title:"Test lesson",content_language:"en",theory:"Test theory",assignment:"Test assignment",prompts:[]},
    "/lessons/1/ru":{title:"Тестовый урок",content_language:"ru",theory:"Теория",assignment:"Задание",prompts:[]},
    "/admin/statistics":{students:3,plans:{starter:1},settled_payments:[]},
    "/logout":{ok:true}
  };
  if(!(p in responses)){unexpected.push(p);return route.fulfill({status:404,json:{error:"Unexpected mock route"}})}
  return route.fulfill({json:responses[p]});
 });
 await page.goto("http://academy.test/dashboard");
 await page.locator("#registerTab").click();await page.locator("#register").waitFor({state:"visible"});await page.locator("#loginTab").click();
 await page.locator("#login [name=email]").fill("test@example.invalid");await page.locator("#login [name=password]").fill("Test-password-only");
 await page.locator("#login button").click();
 await page.locator("#panel").waitFor({state:"visible"});
 assert.equal(await page.locator("#checkout").isVisible(),role==="unpaid");
 assert.equal(await page.locator("#ownerNav").getAttribute("hidden")!==null,role!=="owner");
 assert.equal(await page.locator("#businessButton").getAttribute("hidden")!==null,! (role!=="unpaid"));
 for(const lang of ["ru","uk","pl","en"]){
  await page.locator("#lang").selectOption(lang);
  await page.waitForFunction(l=>document.documentElement.lang===l,lang);
  assert.equal(await page.locator("#homeNavText").count(),1);
  assert.equal(await page.locator("#businessButtonLabel").count(),1);
 }
 if(role==="paid"){
  await page.locator("#mobileNavToggle").click();
  await page.locator("#businessButton").click();
  await page.locator("#extra").getByRole("heading",{name:"Student Business Center",exact:true}).waitFor();
  assert.equal(await page.locator("#workspaceOverview").isVisible(),false);
  await page.locator("#mobileNavToggle").click();
  await page.locator("#homeNav").click();
  await page.locator("#days button[data-day='1']").click();
  await page.locator("#lesson").getByText("Test lesson",{exact:false}).first().waitFor();
  assert.equal(await page.locator("#days button[data-day='2']").isDisabled(),true);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+2),"Horizontal overflow");
 }
 if(role==="owner"){await page.locator("#admin").click();await page.locator("#extra").getByRole("heading",{name:"Academy · Admin Dashboard"}).waitFor()}
 assert.deepEqual(errors,[]);assert.deepEqual(unexpected,[]);
 console.log("PASS:",role,width,"px, 4 languages, navigation and access visibility");
 await context.close();
 }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
