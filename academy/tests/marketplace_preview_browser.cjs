const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {chromium}=require("playwright");
const read=name=>fs.readFileSync(path.join(__dirname,"../backend",name),"utf8");
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [320,390,1280]){
   const context=await browser.newContext({viewport:{width,height:844},serviceWorkers:"block"});
   const page=await context.newPage(),unexpected=[],errors=[];
   page.on("pageerror",e=>errors.push(e.message));
   await context.route("**/*",async route=>{
    const u=new URL(route.request().url());
    if(u.origin!=="http://academy.test"){unexpected.push(u.href);return route.abort()}
    if(u.pathname==="/marketplace-preview")return route.fulfill({contentType:"text/html",body:read("marketplace-preview.html")});
    if(u.pathname==="/marketplace-preview.js")return route.fulfill({contentType:"application/javascript",body:read("marketplace-preview.js")});
    if(u.pathname==="/favicon.ico")return route.fulfill({status:204});
    unexpected.push(u.pathname);return route.abort();
   });
   await page.goto("http://academy.test/marketplace-preview?lang=ru");
   await page.locator("#blockers li").first().waitFor();
   assert.equal(await page.locator("#heading").textContent(),"Предпросмотр оплаты");
   assert.equal(await page.locator("#blockers li").count(),5);
   assert.equal(await page.locator("#fee").textContent(),"50 USDC");
   assert.equal(await page.locator("#worker").textContent(),"950 USDC");
   assert.equal(await page.locator("#pay").isDisabled(),true);
   await page.locator("#amount").fill("0,01");
   assert.equal(await page.locator("#fee").textContent(),"0.0005 USDC");
   await page.locator("#amount").fill("1e2");
   assert.equal(await page.locator("#result").isHidden(),true);
   assert.equal(await page.locator("#error").isVisible(),true);
   await page.locator("#amount").fill("1000000");
   assert.equal(await page.locator("#fee").textContent(),"50000 USDC");
   for(const lang of ["en","uk","pl","ru"]){
    await page.locator("#lang").selectOption(lang);
    assert.equal(await page.locator("html").getAttribute("lang"),lang);
    assert.equal(await page.locator("#pay").isDisabled(),true);
    assert.equal(await page.locator("#blockers li").count(),5);
   }
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
   assert.deepEqual(errors,[]);
   assert.deepEqual(unexpected,[]);
   await context.close();
  }
  console.log("Marketplace preview browser isolation passed");
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
