/* Vendored Lucide SVG icons: https://github.com/lucide-icons/lucide
ISC License

Copyright (c) 2026 Lucide Icons and Contributors

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

---

The following Lucide icons are derived from the Feather project:

airplay, alert-circle, alert-octagon, alert-triangle, aperture, arrow-down-circle, arrow-down-left, arrow-down-right, arrow-down, arrow-left-circle, arrow-left, arrow-right-circle, arrow-right, arrow-up-circle, arrow-up-left, arrow-up-right, arrow-up, at-sign, calendar, cast, check, chevron-down, chevron-left, chevron-right, chevron-up, chevrons-down, chevrons-left, chevrons-right, chevrons-up, circle, clipboard, clock, code, columns, command, compass, corner-down-left, corner-down-right, corner-left-down, corner-left-up, corner-right-down, corner-right-up, corner-up-left, corner-up-right, crosshair, database, divide-circle, divide-square, dollar-sign, download, external-link, feather, frown, hash, headphones, help-circle, info, italic, key, layout, life-buoy, link-2, link, loader, lock, log-in, log-out, maximize, meh, minimize, minimize-2, minus-circle, minus-square, minus, monitor, moon, more-horizontal, more-vertical, move, music, navigation-2, navigation, octagon, pause-circle, percent, plus-circle, plus-square, plus, power, radio, rss, search, server, share, shopping-bag, sidebar, smartphone, smile, square, table-2, tablet, target, terminal, trash-2, trash, triangle, tv, type, upload, x-circle, x-octagon, x-square, x, zoom-in, zoom-out

The MIT License (MIT) (for the icons listed above)

Copyright (c) 2013-present Cole Bemis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

*/
"use strict";
(()=>{
 const $=id=>document.getElementById(id),nav=$("academyNav"),sidebar=$("academySidebar"),toggle=$("mobileNavToggle"),panel=$("panel"),lang=$("lang");
 if(!nav||!sidebar||!toggle||!panel||!lang)return;
 const ICONS={"layout-dashboard":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <rect width=\"7\" height=\"9\" x=\"3\" y=\"3\" rx=\"1\" />\n  <rect width=\"7\" height=\"5\" x=\"14\" y=\"3\" rx=\"1\" />\n  <rect width=\"7\" height=\"9\" x=\"14\" y=\"12\" rx=\"1\" />\n  <rect width=\"7\" height=\"5\" x=\"3\" y=\"16\" rx=\"1\" />\n</svg>\n","chevron-down":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"m6 9 6 6 6-6\" />\n</svg>\n","search":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"m21 21-4.34-4.34\" />\n  <circle cx=\"11\" cy=\"11\" r=\"8\" />\n</svg>\n","menu":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M4 5h16\" />\n  <path d=\"M4 12h16\" />\n  <path d=\"M4 19h16\" />\n</svg>\n","book-open":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M12 5v16\" />\n  <path d=\"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z\" />\n</svg>\n","wallet":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1\" />\n  <path d=\"M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4\" />\n</svg>\n","settings":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915\" />\n  <circle cx=\"12\" cy=\"12\" r=\"3\" />\n</svg>\n","users":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2\" />\n  <path d=\"M16 3.128a4 4 0 0 1 0 7.744\" />\n  <path d=\"M22 21v-2a4 4 0 0 0-3-3.87\" />\n  <circle cx=\"9\" cy=\"7\" r=\"4\" />\n</svg>\n","folder":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z\" />\n</svg>\n","shield-check":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z\" />\n  <path d=\"m9 12 2 2 4-4\" />\n</svg>\n","wand-sparkles":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"m21.64 3.64-1.28-1.28a1.21 1.21 0 0 0-1.72 0L2.36 18.64a1.21 1.21 0 0 0 0 1.72l1.28 1.28a1.2 1.2 0 0 0 1.72 0L21.64 5.36a1.2 1.2 0 0 0 0-1.72\" />\n  <path d=\"m14 7 3 3\" />\n  <path d=\"M5 6v4\" />\n  <path d=\"M19 14v4\" />\n  <path d=\"M10 2v2\" />\n  <path d=\"M7 8H3\" />\n  <path d=\"M21 16h-4\" />\n  <path d=\"M11 3H9\" />\n</svg>\n","briefcase":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16\" />\n  <rect width=\"20\" height=\"14\" x=\"2\" y=\"6\" rx=\"2\" />\n</svg>\n","x":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M18 6 6 18\" />\n  <path d=\"m6 6 12 12\" />\n</svg>\n"};
 function icon(name,cls=""){const el=new DOMParser().parseFromString(ICONS[name]||ICONS["layout-dashboard"],"image/svg+xml").documentElement;const out=document.importNode(el,true);out.setAttribute("aria-hidden","true");out.setAttribute("focusable","false");if(cls)out.setAttribute("class",cls);return out}
 const W={
 en:["Menu","Find a module","Close menu","Learning","AI Studio","Creator business","Jobs & clients","Partners & payments","Administration","Account & security","Help & resources","AI Command Center","Support center","AI Workspace","No available modules found","Marketplace","Agency Builder","Creator Analytics","Client Portal","Reviews","Members & operations","Finance & partners","Moderation & content","Community"],
 ru:["Меню","Найти раздел","Закрыть меню","Обучение","AI Studio","Работа и бизнес","Заказы и клиенты","Партнёры и платежи","Администрирование","Аккаунт и безопасность","Помощь и ресурсы","AI Command Center","Техподдержка","AI Workspace","Доступные разделы не найдены","Биржа услуг","Агентства","Аналитика автора","Кабинет клиента","Отзывы","Пользователи и управление","Финансы и партнёры","Модерация и контент","Сообщество"],
 uk:["Меню","Знайти розділ","Закрити меню","Навчання","AI Studio","Робота й бізнес","Замовлення та клієнти","Партнери й платежі","Адміністрування","Акаунт і безпека","Допомога й ресурси","AI Command Center","Техпідтримка","AI Workspace","Доступних розділів не знайдено","Біржа послуг","Агенції","Аналітика автора","Кабінет клієнта","Відгуки","Користувачі й управління","Фінанси й партнери","Модерація й контент","Спільнота"],
 pl:["Menu","Znajdź moduł","Zamknij menu","Nauka","AI Studio","Praca i biznes","Zlecenia i klienci","Partnerzy i płatności","Administracja","Konto i bezpieczeństwo","Pomoc i zasoby","AI Command Center","Pomoc techniczna","AI Workspace","Nie znaleziono dostępnych modułów","Giełda usług","Agencje","Analityka twórcy","Panel klienta","Opinie","Użytkownicy i zarządzanie","Finanse i partnerzy","Moderacja i treści","Społeczność"]
 };
 const w=()=>W[lang.value]||W.en,home=$("homeNav"),study=$("studyNav"),work=$("workNav"),partners=$("communityNav"),owner=$("ownerNav"),account=$("accountNav"),resources=$("resourcesLabel")?.parentElement;
 if([home,study,work,partners,owner,account,resources].some(x=>!x))return;
 function link(path,index,name){const a=document.createElement("a");a.className="navItem";a.href=path;a.target="_blank";a.rel="noopener noreferrer";a.append(icon(name),document.createElement("span"));a.dataset.zLabel=index;return a}
 function group(id){const el=document.createElement("div");el.id=id;el.className="navGroup";el.append(document.createElement("h3"));return el}
 const ai=group("zAiNav"),jobs=group("zJobsNav"),community=group("zCommunityNav");
 function move(host,ids){for(const id of ids){const n=$(id);if(n)host.append(n)}}
 ai.append(link("/ai-workspace",13,"wand-sparkles"));
 move(ai,["promptStudioButton","storyboardButton","workflowButton","designStudioLink","voiceStudioLink","mediaStudioLink","creatorSuiteLink","marketingButton","knowledgeButton"]);
 const studio=$("studioNavText")?.closest("a");if(studio)ai.append(studio);
 move(jobs,["jobsButton","marketplaceButton","notificationsButton"]);
 jobs.append(link("/marketplace",15,"briefcase"),link("/client-portal",18,"briefcase"),link("/agency",16,"users"),link("/creator-analytics",17,"briefcase"));
 move(community,["communityButton"]);
 resources.append(link("/command-center",11,"layout-dashboard"),link("/support",12,"circle-help"),link("/reviews",19,"users"));
 const order=[[study,3,"book-open"],[ai,4,"wand-sparkles"],[work,5,"briefcase"],[jobs,6,"briefcase"],[partners,7,"wallet"],[community,23,"users"],[owner,8,"shield-check"],[account,9,"settings"],[resources,10,"circle-help"]];
 for(const [g] of order)nav.append(g);
 if(home.firstElementChild)home.firstElementChild.replaceWith(icon("layout-dashboard"));
 const groups=[];
 for(const [g,index,name] of order){
   const heading=g.querySelector(":scope > h3");if(!heading)continue;
   const details=document.createElement("details"),summary=document.createElement("summary"),children=document.createElement("div");
   children.className="zChildren";summary.append(icon(name),heading,icon("chevron-down","zChevron"));
   children.append(...Array.from(g.children));details.append(summary,children);g.append(details);groups.push({g,details,children,heading,index});
 }
 const own=groups.find(x=>x.g===owner);
 if(own)for(const [i,ids] of [[20,["admin","directoryAdmin","networkAdmin","founderAdmin"]],[21,["treasuryAdmin","partnerAdmin","acquisitionAdmin"]],[22,["contentAdmin","marketplaceAdmin","jobsAdmin","communityAdmin"]]]){const h=document.createElement("div");h.className="zSubheading";h.dataset.zLabel=i;own.children.append(h);move(own.children,ids)}
 const top=document.createElement("div");top.className="zDrawerTop";const brand=document.createElement("strong");brand.textContent="ZER0LIFE / ACADEMY";const close=document.createElement("button");close.type="button";if(ICONS.x)close.append(icon("x"));else close.textContent="×";top.append(brand,close);
 const searchWrap=document.createElement("div");searchWrap.className="zSearch";const search=document.createElement("input");search.type="search";search.maxLength=100;search.autocomplete="off";searchWrap.append(icon("search"),search);
 const empty=document.createElement("p");empty.hidden=true;empty.setAttribute("role","status");empty.style.fontSize="13px";nav.prepend(top,searchWrap,empty);
 const backdrop=document.createElement("button");backdrop.type="button";backdrop.className="zBackdrop";backdrop.tabIndex=-1;sidebar.append(backdrop);
 const mq=matchMedia("(max-width:900px)");let searching=false,saved=new Map(),wasOpen=false,focusSearch=false;
 const searchWords={en:["Search Academy","Find modules by name (Ctrl/⌘ + K)","Clear search"],ru:["Поиск по академии","Найти раздел (Ctrl/⌘ + K)","Очистить поиск"],uk:["Пошук в академії","Знайти розділ (Ctrl/⌘ + K)","Очистити пошук"],pl:["Szukaj w akademii","Znajdź moduł (Ctrl/⌘ + K)","Wyczyść wyszukiwanie"]};
 const sw=()=>searchWords[lang.value]||searchWords.en;
 const normalize=s=>s.normalize("NFKD").replace(/\p{M}/gu,"").toLocaleLowerCase().replace(/ł/g,"l").replace(/ё/g,"е");
 const permitted=n=>!n.hidden&&!n.closest("[hidden]")&&!n.disabled&&n.getAttribute("aria-disabled")!=="true";
 const results=()=>Array.from(nav.querySelectorAll(".navItem")).filter(n=>permitted(n)&&!n.closest(".zFiltered")&&n.getClientRects().length>0);
 const jump=document.createElement("button"),jumpText=document.createElement("span");
 jump.type="button";jump.className="zProfileButton";jump.id="zAcademySearchShortcut";jump.append(icon("search"),jumpText);
 jump.setAttribute("aria-keyshortcuts","Control+k Meta+k");
 document.querySelector(".workspaceTop")?.append(jump);
 function openSearch(){
   if(panel.hidden)return;
   if(mq.matches&&!sidebar.classList.contains("expanded")){
     focusSearch=true;toggle.click();
     if(!sidebar.classList.contains("expanded")){focusSearch=false;return}
   }
   search.focus();search.select();
 }
 jump.addEventListener("click",openSearch);
 const clear=document.createElement("button");clear.type="button";clear.className="zProfileButton";clear.hidden=true;clear.append(icon("x"));searchWrap.append(clear);
 clear.addEventListener("click",()=>{search.value="";filter();search.focus()});
 function filter(){
   const q=normalize(search.value.trim());const tokens=q.split(/\s+/).filter(Boolean);clear.hidden=!q;
   if(q&&!searching){saved=new Map(groups.map(g=>[g.details,g.details.open]));searching=true}
   if(!q&&searching){for(const [d,open] of saved)d.open=open;searching=false;saved.clear()}
   let total=0;
   for(const {g,details,children,heading} of groups){
     let matches=0;
     for(const n of children.querySelectorAll(".navItem")){
       const hay=normalize(n.textContent+" "+heading.textContent);const match=tokens.every(t=>hay.includes(t));
       n.classList.toggle("zFiltered",!match);
       if(permitted(n)&&match)matches++;
     }
     g.classList.toggle("zFiltered",!!q&&matches===0);
     if(q&&matches)details.open=true;
     if(!g.hidden)total+=matches;
   }
   const hm=tokens.every(t=>normalize(home.textContent).includes(t));
   home.classList.toggle("zFiltered",!hm);if(hm&&permitted(home))total++;
   const hide=!q||total>0;if(empty.hidden!==hide)empty.hidden=hide;
 }
 function labels(){
   for(const x of groups)if(x.heading.textContent!==w()[x.index])x.heading.textContent=w()[x.index];
   for(const n of nav.querySelectorAll("[data-z-label]")){const text=w()[Number(n.dataset.zLabel)];if(n.tagName==="A"){n.lastElementChild.textContent=text;const url=new URL(n.href,location.origin);url.searchParams.set("lang",lang.value);n.href=url.pathname+url.search}else n.textContent=text}
   jumpText.textContent=sw()[0];jump.title=sw()[1];clear.setAttribute("aria-label",sw()[2]);clear.title=sw()[2];search.placeholder=w()[1];search.setAttribute("aria-label",w()[1]);close.setAttribute("aria-label",w()[2]);backdrop.setAttribute("aria-label",w()[2]);empty.textContent=w()[14];toggle.setAttribute("aria-label",w()[0]);toggle.replaceChildren(icon("menu"),document.createTextNode(w()[0]));filter();
 }
 function closeDrawer(focus=true){sidebar.classList.remove("expanded");toggle.setAttribute("aria-expanded","false");document.body.classList.remove("zDrawerOpen");if(focus&&mq.matches)toggle.focus()}
 function sync(){
   const open=mq.matches&&!panel.hidden&&sidebar.classList.contains("expanded");
   document.body.classList.toggle("zDrawerOpen",open);
   if(open&&!wasOpen){if(focusSearch){focusSearch=false;search.focus();search.select()}else close.focus({preventScroll:true})}
   wasOpen=open;
   if(!panel.hidden&&!mq.matches&&!searching)for(const {g,details} of groups)if(!g.hidden&&g.querySelector(".navItem[aria-current=page]:not([hidden])"))details.open=true;
   filter();
 }
 search.addEventListener("input",filter);
 search.addEventListener("keydown",e=>{
   if(e.isComposing)return;
   if(e.key==="Escape"&&search.value){e.preventDefault();e.stopPropagation();search.value="";filter();return}
   if(!search.value.trim())return;
   const found=results();
   if(e.key==="ArrowDown"&&found.length){e.preventDefault();found[0].focus()}
   if(e.key==="Enter"&&found.length===1){e.preventDefault();found[0].click()}
 });
 document.addEventListener("keydown",e=>{
   if(!panel.hidden&&!e.isComposing&&(e.ctrlKey||e.metaKey)&&!e.altKey&&e.key.toLowerCase()==="k"){e.preventDefault();openSearch()}
 });
 close.onclick=()=>closeDrawer();backdrop.onclick=()=>closeDrawer();
 nav.addEventListener("click",e=>{if(e.target.closest("a.navItem"))closeDrawer(false)});
 document.addEventListener("keydown",e=>{
   if(!mq.matches||panel.hidden||!sidebar.classList.contains("expanded"))return;
   if(e.key==="Escape"){e.preventDefault();closeDrawer();return}
   if(e.key==="Tab"){
     const focusable=Array.from(nav.querySelectorAll("button:not([disabled]),a[href],input:not([disabled]),summary")).filter(n=>!n.hidden&&!n.closest("[hidden]")&&n.getClientRects().length>0);
     if(!focusable.length)return;
     const first=focusable[0],last=focusable[focusable.length-1],active=document.activeElement;
     if(!nav.contains(active)||(e.shiftKey&&active===first)||(!e.shiftKey&&active===last)){e.preventDefault();(e.shiftKey?last:first).focus()}
   }
 });
 mq.addEventListener?.("change",()=>{if(!mq.matches)closeDrawer(false);sync()});
 new MutationObserver(sync).observe(sidebar,{attributes:true,subtree:true,attributeFilter:["hidden","aria-current"]});
 new MutationObserver(sync).observe(sidebar,{attributes:true,attributeFilter:["class"]});
 new MutationObserver(()=>{if(panel.hidden){focusSearch=false;search.value="";filter();for(const g of groups)g.details.open=false;closeDrawer(false)}sync()}).observe(panel,{attributes:true,attributeFilter:["hidden"]});
 let pending=false;new MutationObserver(()=>{if(pending)return;pending=true;queueMicrotask(()=>{pending=false;for(const x of groups)if(x.heading.textContent!==w()[x.index])x.heading.textContent=w()[x.index];filter()})}).observe(nav,{subtree:true,childList:true,characterData:true});
 new MutationObserver(()=>{if(!toggle.querySelector("svg"))toggle.replaceChildren(icon("menu"),document.createTextNode(w()[0]))}).observe(toggle,{childList:true});
 lang.addEventListener("change",labels);document.body.classList.add("z2027");labels();sync();
})();
