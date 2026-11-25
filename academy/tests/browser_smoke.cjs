const {chromium}=require("playwright");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const html=fs.readFileSync(path.join(__dirname,"../backend/dashboard.html"),"utf8").replace(/\r\n?/g,"\n");
const crypto=require("node:crypto");
const hashes=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>"'sha256-"+crypto.createHash("sha256").update(x[1]).digest("base64")+"'");
const csp="default-src 'none'; script-src 'self' "+hashes.join(" ")+"; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; manifest-src 'self'; worker-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'; object-src 'none'";
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
 for(const [role,width] of [["unpaid",1280],["paid",390],["paid",320],["owner",1280]]){
 const context=await browser.newContext({viewport:{width,height:844},serviceWorkers:"block"});
 const page=await context.newPage();
 const errors=[], unexpected=[];
 page.on("pageerror",e=>errors.push(e.message));
 let signedIn=false,registerCalls=0;
 const calls=[];
 await context.route("**/*",async route=>{
  const url=new URL(route.request().url());
  if(url.origin!=="http://academy.test")return route.abort();
  const p=url.pathname;
  if(p==="/dashboard")return route.fulfill({contentType:"text/html",headers:{"Content-Security-Policy":csp},body:html});
  if(p==="/academy-icon.svg"||p==="/manifest.webmanifest"||p==="/favicon.ico")return route.fulfill({status:204});
  calls.push(p);
  if(p==="/register"){registerCalls++;const b=route.request().postDataJSON();assert.equal(b.first_name,"Test");assert.equal(b.last_name,"Student");assert.equal(b.email,"test@example.invalid");if(registerCalls===1){await new Promise(r=>setTimeout(r,100));return route.fulfill({status:400,json:{error:"Registration unavailable",code:"registration_unavailable"}})}return route.fulfill({status:201,json:{id:123}})}
  if(p==="/login"){signedIn=true;return route.fulfill({json:{token:"test-only-token"}})}
  if(!signedIn)return route.fulfill({status:403,json:{error:"Access denied"}});
  const paid=role!=="unpaid",owner=role==="owner";
  const responses={
    "/progress":{paid,plan:paid?"starter":null,lessons:Array.from({length:30},(_,i)=>({day:i+1,completed:false,unlocked:paid&&i===0}))},
    "/account/me":{id:123},
    "/account/mfa":{enabled:false,recovery_remaining:0},
    "/admin/network-access":{allowed:owner},
    "/checkout/prices":{discount_percent:0,prices:{starter:199000000,pro:499000000,vip:999000000}},
    "/checkout/active":{invoice:null},
    "/business":{clients:[],orders:[],totals:{agreed_cents:"0",received_cents:"0",expense_cents:"0",outstanding_cents:"0",cash_margin_cents:"0"}},
    "/portfolio":{items:[]},
    "/lessons/1/en":{title:"Test lesson",content_language:"en",theory:"Test theory",assignment:"Test assignment",prompts:[]},
    "/lessons/1/ru":{title:"Тестовый урок",content_language:"ru",theory:"Теория",assignment:"Задание",prompts:[]},
    "/admin/statistics":{students:3,plans:{starter:1},settled_payments:[]},
    "/community/feed":{items:[],next_after:null},
    "/notifications/count":{unread:1},
    "/notifications/list":{items:[{id:1,job_id:1,title:"Synthetic project",kind:"message",target:"room",created_at:"2026-11-24T00:00:00Z",read:false}],next_before:null,unread:1},
    "/notifications/read":{unread:0},
    "/jobs/recommended":{items:[]},
    "/logout":{ok:true}
  };
  if(!(p in responses)){unexpected.push(p);return route.fulfill({status:404,json:{error:"Unexpected mock route"}})}
  return route.fulfill({json:responses[p]});
 });
 await page.goto("http://academy.test/dashboard"+(role==="paid"?"?lang=ru&module=community":role==="unpaid"?"?lang=pl&module=learning":""));
 if(role!=="owner")assert.equal(await page.locator("#lang").inputValue(),role==="paid"?"ru":"pl");
 await page.locator("#registerTab").click();await page.locator("#register").waitFor({state:"visible"});
 if(role==="paid"){
  await page.locator("#registerSubmit").click();
  await page.getByText("Введите имя.",{exact:true}).waitFor();
  assert.equal(registerCalls,0);
  for(const [key,val] of [["first_name"," Test "],["last_name","Student"],["email","test@example.invalid"],["password","Test-password-only"]])await page.locator("#register [name="+key+"]").fill(val);
  await page.locator("#registerSubmit").click();
  await page.getByText("Не удалось зарегистрироваться.",{exact:false}).waitFor();
  assert.equal(await page.locator("#registerSubmit").isEnabled(),true);
  await page.locator("#registerSubmit").click();
  await page.getByText("Аккаунт создан.",{exact:false}).waitFor();
  assert.equal(await page.locator("#login [name=email]").inputValue(),"test@example.invalid");
  assert.equal(registerCalls,2);
 }else await page.locator("#loginTab").click();
 await page.locator("#login [name=email]").fill("test@example.invalid");await page.locator("#login [name=password]").fill("Test-password-only");
 await page.locator("#login button").click();
 await page.locator("#panel").waitFor({state:"visible"});
 if(role==="paid")await page.locator("#extra").getByRole("heading",{name:"Сообщество",exact:true}).waitFor();
 if(role==="unpaid")assert.equal(await page.locator("#workspaceOverview").isVisible(),true);
 assert.equal(await page.locator("#checkout").isVisible(),role==="unpaid");
 assert.equal(await page.locator("#ownerNav").getAttribute("hidden")!==null,role!=="owner");
 assert.equal(await page.locator("#businessButton").getAttribute("hidden")!==null,! (role!=="unpaid"));
 for(const lang of ["ru","uk","pl","en"]){
  await page.locator("#lang").selectOption(lang);
  await page.waitForFunction(l=>document.documentElement.lang===l,lang);
  assert.equal(await page.locator("#homeNavText").count(),1);
  assert.equal(await page.locator("#businessButtonLabel").count(),1);
  assert.equal(await page.locator("#mfaButtonLabel").textContent(),"2FA");
  assert.equal(await page.locator("#securityButtonLabel").textContent(),{en:"Account security",ru:"Безопасность",uk:"Безпека",pl:"Bezpieczeństwo"}[lang]);
  assert.equal(await page.locator("#logoutLabel").textContent(),{en:"Sign out",ru:"Выйти",uk:"Вийти",pl:"Wyloguj"}[lang]);
 }
 if(role==="unpaid"){
  await page.locator("#securityButton").click();
  await page.getByRole("button",{name:"Manage 2FA",exact:true}).click();
  await page.getByRole("heading",{name:"Two-factor authentication",exact:true}).waitFor();
  await page.getByRole("button",{name:"Enable 2FA",exact:true}).waitFor();
 }
 if(role==="paid"){
  await page.locator("#mobileNavToggle").click();
  await page.locator("#notificationsButton").click();
  await page.locator("#extra").getByRole("heading",{name:"Notification Center",exact:true}).waitFor();
  await page.locator("#extra").getByText("Synthetic project",{exact:true}).waitFor();
  await page.locator("#mobileNavToggle").click();
  await page.locator("#businessButton").click();
  await page.locator("#extra").getByRole("heading",{name:"Student Business Center",exact:true}).waitFor();
  await page.locator("#businessWorkflow").getByRole("button",{name:"Find jobs",exact:true}).waitFor();
  await page.locator("#businessPipeline").getByRole("heading",{name:"Order pipeline",exact:true}).waitFor();
  assert.equal(await page.locator("#businessPipeline h4").count(),4);
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
