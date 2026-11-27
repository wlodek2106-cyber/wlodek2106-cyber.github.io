/* Aurora: original CSS 3D and task glyphs; reused Lucide SVGs licensed in ACADEMY_UI_SOURCES.md. */
"use strict";
(()=>{
const $=id=>document.getElementById(id),lang=$("lang"),W={"en":["Your creative future starts here.","Learn. Create. Build.","Explore AI tools, develop your skills and build real projects in one workspace.","Continue learning","Explore AI Studio","Quick actions","Academy","AI Support","Creator Suite","Video & animation","Music & sound","Website builder","Automation","AI Workspace","AI Model Hub","Jobs marketplace","Community","Settings","Design studio","Voice studio","Your tools","Open workspace","Project workflow","My progress","View learning","Free AI Studio","Navigation","Client portal","Agency builder","Creator analytics","Cost calculator","Notifications","Pause animation","Play animation"],"ru":["Твоё будущее начинается здесь.","Обучайся. Создавай. Развивайся.","Осваивай AI, развивай навыки и создавай реальные проекты в едином пространстве.","Продолжить обучение","Открыть AI Studio","Быстрые действия","Академия","AI-поддержка","Creator Suite","Видео и анимация","Музыка и звук","Конструктор сайтов","Автоматизация","AI Workspace","AI Model Hub","Биржа заказов","Сообщество","Настройки","Дизайн-студия","Голосовая студия","Твои инструменты","Открыть пространство","Рабочие процессы","Мой прогресс","К обучению","Free AI Studio","Навигация","Кабинет клиента","Агентства","Аналитика автора","Калькулятор стоимости","Уведомления","Пауза анимации","Включить анимацию"],"uk":["Твоє майбутнє починається тут.","Навчайся. Створюй. Розвивайся.","Опануй AI, розвивай навички та створюй реальні проєкти в одному просторі.","Продовжити навчання","Відкрити AI Studio","Швидкі дії","Академія","AI-підтримка","Creator Suite","Відео й анімація","Музика й звук","Конструктор сайтів","Автоматизація","AI Workspace","AI Model Hub","Біржа замовлень","Спільнота","Налаштування","Студія дизайну","Студія голосу","Твої інструменти","Відкрити простір","Робочі процеси","Мій прогрес","До навчання","Free AI Studio","Навігація","Кабінет клієнта","Агенції","Аналітика автора","Калькулятор вартості","Сповіщення","Пауза анімації","Увімкнути анімацію"],"pl":["Twoja przyszłość zaczyna się tutaj.","Ucz się. Twórz. Rozwijaj się.","Poznaj AI, rozwijaj umiejętności i twórz projekty w jednym miejscu.","Kontynuuj naukę","Otwórz AI Studio","Szybkie działania","Akademia","Pomoc AI","Creator Suite","Wideo i animacja","Muzyka i dźwięk","Kreator stron","Automatyzacja","AI Workspace","AI Model Hub","Giełda zleceń","Społeczność","Ustawienia","Studio projektowania","Studio głosu","Twoje narzędzia","Otwórz przestrzeń","Procesy pracy","Mój postęp","Do nauki","Free AI Studio","Nawigacja","Panel klienta","Agencje","Analityka twórcy","Kalkulator kosztów","Powiadomienia","Wstrzymaj animację","Włącz animację"]},ICONS={"layout-dashboard":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <rect width=\"7\" height=\"9\" x=\"3\" y=\"3\" rx=\"1\" />\n  <rect width=\"7\" height=\"5\" x=\"14\" y=\"3\" rx=\"1\" />\n  <rect width=\"7\" height=\"9\" x=\"14\" y=\"12\" rx=\"1\" />\n  <rect width=\"7\" height=\"5\" x=\"3\" y=\"16\" rx=\"1\" />\n</svg>\n","chevron-down":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"m6 9 6 6 6-6\" />\n</svg>\n","search":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"m21 21-4.34-4.34\" />\n  <circle cx=\"11\" cy=\"11\" r=\"8\" />\n</svg>\n","menu":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M4 5h16\" />\n  <path d=\"M4 12h16\" />\n  <path d=\"M4 19h16\" />\n</svg>\n","book-open":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M12 5v16\" />\n  <path d=\"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z\" />\n</svg>\n","wallet":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1\" />\n  <path d=\"M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4\" />\n</svg>\n","settings":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915\" />\n  <circle cx=\"12\" cy=\"12\" r=\"3\" />\n</svg>\n","users":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2\" />\n  <path d=\"M16 3.128a4 4 0 0 1 0 7.744\" />\n  <path d=\"M22 21v-2a4 4 0 0 0-3-3.87\" />\n  <circle cx=\"9\" cy=\"7\" r=\"4\" />\n</svg>\n","folder":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z\" />\n</svg>\n","shield-check":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z\" />\n  <path d=\"m9 12 2 2 4-4\" />\n</svg>\n","wand-sparkles":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"m21.64 3.64-1.28-1.28a1.21 1.21 0 0 0-1.72 0L2.36 18.64a1.21 1.21 0 0 0 0 1.72l1.28 1.28a1.2 1.2 0 0 0 1.72 0L21.64 5.36a1.2 1.2 0 0 0 0-1.72\" />\n  <path d=\"m14 7 3 3\" />\n  <path d=\"M5 6v4\" />\n  <path d=\"M19 14v4\" />\n  <path d=\"M10 2v2\" />\n  <path d=\"M7 8H3\" />\n  <path d=\"M21 16h-4\" />\n  <path d=\"M11 3H9\" />\n</svg>\n","briefcase":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16\" />\n  <rect width=\"20\" height=\"14\" x=\"2\" y=\"6\" rx=\"2\" />\n</svg>\n","x":"<svg\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"24\"\n  height=\"24\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"2\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M18 6 6 18\" />\n  <path d=\"m6 6 12 12\" />\n</svg>\n","video":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"3\" y=\"5\" width=\"18\" height=\"14\" rx=\"3\"/><path d=\"m10 9 5 3-5 3z\"/></svg>","music":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M3 10v4m4-8v12m5-16v20m5-16v12m4-8v4\"/></svg>","code":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"m8 6-6 6 6 6m8-12 6 6-6 6m-2-15-4 18\"/></svg>","workflow":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"9\" y=\"2\" width=\"6\" height=\"6\" rx=\"1\"/><rect x=\"2\" y=\"16\" width=\"6\" height=\"6\" rx=\"1\"/><rect x=\"16\" y=\"16\" width=\"6\" height=\"6\" rx=\"1\"/><path d=\"M12 8v4H5v4m7-4h7v4\"/></svg>","cpu":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"5\" y=\"5\" width=\"14\" height=\"14\" rx=\"3\"/><rect x=\"9\" y=\"9\" width=\"6\" height=\"6\" rx=\"1\"/><path d=\"M9 2v3m6-3v3M9 19v3m6-3v3M2 9h3m-3 6h3m14-6h3m-3 6h3\"/></svg>","graduation":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"m2 9 10-5 10 5-10 5zM6 11v6q6 5 12 0v-6m4-2v7\"/></svg>","headphones":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M3 14v-3a9 9 0 0 1 18 0v3\"/><rect x=\"3\" y=\"12\" width=\"5\" height=\"8\" rx=\"2\"/><rect x=\"16\" y=\"12\" width=\"5\" height=\"8\" rx=\"2\"/></svg>","layers":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"m12 3 10 5-10 5L2 8zm-10 9 10 5 10-5M2 16l10 5 10-5\"/></svg>","palette":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M12 3a9 9 0 1 0 0 18h2a2 2 0 0 0 1-4 2 2 0 0 1 1-4h3a2 2 0 0 0 2-2 9 9 0 0 0-9-8z\"/><circle cx=\"7\" cy=\"10\" r=\"1\"/><circle cx=\"11\" cy=\"7\" r=\"1\"/><circle cx=\"16\" cy=\"8\" r=\"1\"/></svg>","mic":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"9\" y=\"2\" width=\"6\" height=\"13\" rx=\"3\"/><path d=\"M5 11v2a7 7 0 0 0 14 0v-2m-7 9v3m-4 0h8\"/></svg>","bell":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M5 10a7 7 0 0 1 14 0v5l2 3H3l2-3zm4 11h6\"/></svg>","play":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"m8 4 12 8-12 8z\"/></svg>","chart":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M3 3v18h18M7 16l5-6 4 3 5-8\"/></svg>","box":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"m12 2 10 5v10l-10 5-10-5V7zm0 10 10-5M12 12 2 7m10 5v10\"/></svg>","image":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"3\" y=\"3\" width=\"18\" height=\"18\" rx=\"3\"/><circle cx=\"8\" cy=\"8\" r=\"2\"/><path d=\"m3 18 6-6 4 4 3-3 5 5\"/></svg>","trophy":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M7 3h10v8a5 5 0 0 1-10 0zM7 6H3v3a4 4 0 0 0 4 4m10-7h4v3a4 4 0 0 1-4 4m-5 3v5m-5 0h10\"/></svg>","lock":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"4\" y=\"10\" width=\"16\" height=\"11\" rx=\"2\"/><path d=\"M8 10V6a4 4 0 0 1 8 0v4\"/></svg>","network":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><circle cx=\"12\" cy=\"4\" r=\"2\"/><circle cx=\"4\" cy=\"19\" r=\"2\"/><circle cx=\"20\" cy=\"19\" r=\"2\"/><path d=\"m11 6-6 11M13 6l6 11M6 19h12\"/></svg>","file":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M6 2h8l5 5v15H6zM14 2v5h5M9 12h7m-7 4h7\"/></svg>","message":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M21 11a9 9 0 0 1-9 9H3l2-5A9 9 0 1 1 21 11z\"/></svg>","gift":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"3\" y=\"7\" width=\"18\" height=\"5\" rx=\"1\"/><path d=\"M5 12v9h14v-9M12 7v14M12 7C3 7 5 0 9 3l3 4c9 0 7-7 3-4z\"/></svg>","exit":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M10 4H3v16h7m6-12 4 4-4 4m4-4H9\"/></svg>","checklist":"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.8\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><rect x=\"5\" y=\"3\" width=\"14\" height=\"19\" rx=\"2\"/><path d=\"m8 9 2 2 4-4m-6 9h8\"/></svg>"};
const locale=()=>Object.hasOwn(W,lang?.value)?lang.value:"en",w=()=>W[locale()];
function el(tag,cls="",text=""){const n=document.createElement(tag);if(cls)n.className=cls;if(text)n.textContent=text;return n}
function icon(name){const n=document.importNode(new DOMParser().parseFromString(ICONS[name]||ICONS["layout-dashboard"],"image/svg+xml").documentElement,true);n.setAttribute("aria-hidden","true");n.setAttribute("focusable","false");return n}
function orb(){const n=el("span","zOrb");n.setAttribute("aria-hidden","true");return n}
const localized=[],links=[],scenes=[];
function label(n,i){localized.push([n,i]);n.textContent=w()[i];return n}
function url(path){const u=new URL(path,location.origin);u.searchParams.set("lang",locale());return u.pathname+u.search+u.hash}
function route(path,i,ico,cls="zAction"){const a=el("a",cls);a.href=url(path);a.append(icon(ico),label(el("span"),i));links.push([a,path]);return a}
function action(i,ico,fn,cls="zAction"){const a=el("button",cls);a.type="button";a.append(icon(ico),label(el("span"),i));a.onclick=fn;return a}
function tile(path,i,ico){const a=el("a","zTile"),b=el("span","zTileIcon");a.href=url(path);b.append(icon(ico));a.append(b,label(el("span"),i));links.push([a,path]);return a}
function go(id,fallback){const n=$(id);if(n&&!n.hidden&&!n.closest("[hidden]")&&!n.disabled)n.click();else if(fallback)location.href=url(fallback)}
function study(){const n=$("widgetContinue");if(n&&!n.hidden&&!n.closest("[hidden]")&&!n.disabled){n.click();return}const b=Array.from(document.querySelectorAll("#days button[data-day]")).find(n=>!n.disabled&&n.dataset.state==="open");if(b){b.click();$("lesson")?.scrollIntoView({block:"start",behavior:"auto"})}else $("learningHeading")?.scrollIntoView({block:"start",behavior:"auto"})}
const tools=[["/free-ai",25,"cpu"],["/creator-suite",8,"layers"],["/animation-studio",9,"video"],["/music-studio",10,"music"],["/website-builder",11,"code"],["/automation-studio",12,"workflow"],["/design-studio",18,"palette"],["/voice-studio",19,"mic"],["/ai-workspace",13,"wand-sparkles"],["/free-ai#model-hub",14,"box"],["/hire",15,"briefcase"],["/support",7,"headphones"]];
const navMap=Object.fromEntries([...tools,["/dashboard",6,"graduation"],["/marketplace",15,"briefcase"],["/client-portal",27,"users"],["/agency",28,"network"],["/creator-analytics",29,"chart"],["/production-cost",30,"wallet"],["/command-center",21,"layout-dashboard"],["#model-hub",14,"box"]].map(([p,i,n])=>[p,[i,n]]));
const navIcons={homeNav:"layout-dashboard",adaptiveButton:"graduation",achievementButton:"trophy",proLibrary:"book-open",playgroundButton:"cpu",historyButton:"file",certificate:"graduation",reviewButton:"message",portfolioButton:"image",careerButton:"briefcase",businessButton:"chart",productivityButton:"checklist",referralButton:"gift",partnerButton:"users",paymentHistory:"wallet",admin:"shield-check",directoryAdmin:"users",networkAdmin:"network",founderAdmin:"layout-dashboard",contentAdmin:"file",partnerAdmin:"users",marketplaceAdmin:"briefcase",treasuryAdmin:"wallet",acquisitionAdmin:"chart",jobsAdmin:"checklist",communityAdmin:"message",securityButton:"lock",mfaButton:"shield-check",passkeySettings:"lock",logout:"exit",marketingButton:"chart",designStudioLink:"palette",voiceStudioLink:"mic",mediaStudioLink:"music",storyboardButton:"video",workflowButton:"workflow",marketplaceButton:"briefcase",notificationsButton:"bell",jobsButton:"briefcase",communityButton:"users",promptStudioButton:"code",knowledgeButton:"book-open",creatorSuiteLink:"layers"};
function stage(){const n=el("div","zStage");n.setAttribute("aria-hidden","true");n.append(el("div","zOrbit"),el("div","zOrbit second"),el("div","zPedestal"));const cube=el("div","zCube");for(let i=0;i<6;i++){const f=el("div","zFace");if(i===0||i===2)f.append(orb());cube.append(f)}n.append(cube);const sat=el("div","zSatellites");for(const key of ["graduation","video","music","code"]){const x=el("span","zSatellite");x.append(icon(key));sat.append(x)}n.append(sat);return n}
let paused=false;const reduced=matchMedia("(prefers-reduced-motion: reduce)");
function motion(){for(const [n,b] of scenes){n.classList.toggle("zPaused",paused||reduced.matches||document.hidden);b.hidden=reduced.matches;const title=w()[paused?33:32];b.textContent=paused?"▶":"Ⅱ";b.setAttribute("aria-label",title);b.title=title;b.setAttribute("aria-pressed",String(paused))}}
function hero(dash){const n=el("section","zAuroraHero");n.id=dash?"zAcademyHero":"zStudioHero";const copy=el("div","zHeroCopy");copy.append(el("div","zHeroEyebrow","ZER0LIFE / ACADEMY 2027"));if(dash)copy.append(label(el("h2"),0),label(el("p"),2));else{const title=$("title"),intro=$("intro"),tag=document.querySelector("main>.tag");if(tag)copy.append(tag);if(title)copy.append(title);if(intro)copy.append(intro)}const actions=el("div","zActions");if(dash)actions.append(action(3,"play",study,"zAction primary"),route("/ai-workspace",4,"wand-sparkles"));else actions.append(action(4,"cpu",()=>{$("discover")?.scrollIntoView({block:"center",behavior:"auto"});$("discover")?.focus()},"zAction primary"),route("/dashboard",6,"graduation"));copy.append(actions);n.append(copy,stage());const pause=el("button","zPause");pause.type="button";pause.onclick=()=>{paused=!paused;motion()};n.append(pause);scenes.push([n,pause]);return n}
function tiles(){const n=el("div","zTools");n.id="zAcademyTools";n.append(label(el("h2"),20));const grid=el("div","zToolGrid");for(const [path,i,ico] of tools)grid.append(tile(path,i,ico));n.append(grid);return n}
function quick(){const n=el("div","zTools");n.id="zQuickActions";n.style.order="-7";n.append(label(el("h2"),5));const g=el("div","zToolGrid");for(const [i,ico,fn] of [[3,"play",study],[22,"workflow",()=>go("workflowButton","/creator-suite")],[31,"bell",()=>go("notificationsButton","/command-center")],[17,"settings",()=>go("securityButton","/support")]]){const b=action(i,ico,fn,"zTile"),wrap=el("span","zTileIcon");wrap.append(b.firstChild);b.prepend(wrap);g.append(b)}n.append(g);return n}
const courseWords={"en":["AI foundations & prompts","Image & photography","Video, characters & sound","Content, marketing & AI agents","Portfolio & creator business","Web & mobile development","AI agent development","Home","Learn","AI Studio","Jobs","Menu","Lessons completed","Available","Locked","Your course modules","Choose a module","Lessons","No lessons available"],"ru":["Основы AI и промпты","Изображения и фотография","Видео, персонажи и звук","Контент, маркетинг и AI-агенты","Портфолио и бизнес","Сайты и мобильные приложения","Разработка AI-агентов","Главная","Учёба","AI Studio","Заказы","Меню","Уроков пройдено","Доступно","Закрыто","Твои учебные модули","Выбрать модуль","Уроки","Нет доступных уроков"],"uk":["Основи AI та промпти","Зображення й фотографія","Відео, персонажі та звук","Контент, маркетинг та AI-агенти","Портфоліо й бізнес","Сайти та мобільні застосунки","Розробка AI-агентів","Головна","Навчання","AI Studio","Замовлення","Меню","Уроків пройдено","Доступно","Закрито","Твої навчальні модулі","Обрати модуль","Уроки","Немає доступних уроків"],"pl":["Podstawy AI i prompty","Obrazy i fotografia","Wideo, postacie i dźwięk","Treści, marketing i agenci AI","Portfolio i biznes","Strony i aplikacje mobilne","Tworzenie agentów AI","Start","Nauka","AI Studio","Zlecenia","Menu","Ukończone lekcje","Dostępne","Zablokowane","Twoje moduły kursu","Wybierz moduł","Lekcje","Brak dostępnych lekcji"]},cw=()=>courseWords[locale()];
const tracks=[[1,6,"cpu"],[7,9,"image"],[10,17,"video"],[18,24,"workflow"],[25,30,"briefcase"],[31,40,"code"],[41,45,"network"]];
let courseRefresh=null,courseRelabel=null,bottomRefresh=null;
function courseCards(){
 const days=$("days"),heading=$("learningHeading");if(!days||!heading)return;
 const host=el("div","zCourseCards");host.id="zCourseCards";
 heading.before(host);
 const title=el("h2");const grid=el("div","zCourseGrid");host.append(title,grid);
 let selected=null,lastNodes=[],cards=[];
 function selectTrack(index,scroll=false){
   selected=index;
   for(const item of cards){item.button.setAttribute("aria-pressed",String(item.index===index));item.panel.hidden=item.index!==index}
   if(scroll)days.scrollIntoView({block:"start",behavior:"auto"});
 }
 function relabel(){
   title.textContent=cw()[15];heading.textContent=cw()[17];
   for(const item of cards){
    item.name.textContent=cw()[item.index];item.meta.textContent=item.done+" / "+item.total+" · "+cw()[12];
    item.info.textContent=cw()[13]+": "+item.available+" · "+cw()[14]+": "+item.locked;
    item.button.setAttribute("aria-label",cw()[16]+": "+cw()[item.index]+". "+item.meta.textContent);
    item.bar.setAttribute("aria-label",cw()[item.index]+": "+item.meta.textContent);
    item.panel.setAttribute("aria-label",cw()[item.index]);
   }
 }
 const observer=new MutationObserver(()=>refresh());
 function observe(){observer.observe(days,{childList:true})}
 function refresh(){
   const buttons=Array.from(days.querySelectorAll("button[data-day]"));
   if(buttons.length===lastNodes.length&&buttons.every((n,i)=>n===lastNodes[i]))return;
   lastNodes=buttons;observer.disconnect();
   grid.replaceChildren();cards=[];
   // Move original lesson controls only; keep their server-derived state, events and disabled flags.
   const fragments=[];
   for(const [index,[from,to,ico]] of tracks.entries()){
     const items=buttons.filter(b=>Number(b.dataset.day)>=from&&Number(b.dataset.day)<=to);
     if(!items.length)continue;
     const done=items.filter(b=>b.dataset.state==="completed").length,available=items.filter(b=>b.dataset.state==="open").length,locked=items.filter(b=>b.dataset.state==="locked").length;
     const button=el("button","zCourseCard");button.type="button";button.dataset.track=String(index);
     const art=el("span","zCourseArt");art.append(icon(ico));const name=el("strong","zCourseName"),meta=el("span","zCourseMeta"),info=el("span","zCourseInfo"),bar=el("progress","zCourseProgress");bar.max=items.length;bar.value=done;
     button.append(art,name,meta,bar,info);grid.append(button);
     const panel=el("div","zCourseDays");panel.dataset.track=String(index);panel.append(...items);fragments.push(panel);
     cards.push({index,button,name,meta,info,bar,panel,done,total:items.length,available,locked});
     button.onclick=()=>selectTrack(index,true);
   }
   if(buttons.length){days.replaceChildren(...fragments);days.classList.add("zGroupedDays")}
   else days.classList.remove("zGroupedDays");
   host.hidden=!cards.length;
   const preferred=cards.find(x=>x.index===selected)||cards.find(x=>x.available>0)||cards.find(x=>x.locked>0)||cards[0];
   if(preferred)selectTrack(preferred.index);
   relabel();observe();
 }
 // All existing shortcuts retain the original lesson handler. Scroll after its async render.
 const lesson=$("lesson"),overview=$("workspaceOverview"),panel=$("panel");let requestedLesson=false;
 if(lesson&&overview&&panel){
   new MutationObserver(records=>{
     if(!requestedLesson||panel.hidden||overview.hidden||lesson.hidden||!records.some(r=>r.type==="childList")||!lesson.firstElementChild)return;
     requestedLesson=false;lesson.scrollIntoView({block:"start",behavior:"auto"});
   }).observe(lesson,{childList:true});
   const cancel=()=>{if(panel.hidden||overview.hidden)requestedLesson=false};
   new MutationObserver(cancel).observe(overview,{attributes:true,attributeFilter:["hidden"]});
   new MutationObserver(cancel).observe(panel,{attributes:true,attributeFilter:["hidden"]});
 }
 days.addEventListener("click",e=>{const b=e.target.closest("button[data-day]");if(!b||b.disabled)return;const item=cards.find(x=>x.panel.contains(b));if(item)selectTrack(item.index);requestedLesson=true},{capture:true});
 courseRefresh=refresh;courseRelabel=relabel;observe();refresh();
}
function bottomNav(){
 const panel=$("panel"),nav=$("academyNav"),toggle=$("mobileNavToggle"),side=$("academySidebar");if(!panel||!nav||!toggle||!side)return;
 const bar=el("nav","zBottomNav");bar.id="zBottomNav";
 const entries=[];
 const home=()=>{$("homeNav")?.click();$("academyWorkspace")?.scrollIntoView({block:"start",behavior:"auto"})};
 const learn=()=>{$("homeNav")?.click();$("zCourseCards")?.scrollIntoView({block:"start",behavior:"auto"})};
 const jobs=()=>go("jobsButton","/hire");
 for(const [idx,ico,fn] of [[7,"layout-dashboard",home],[8,"graduation",learn],[9,"wand-sparkles",()=>{location.href=url("/ai-workspace")}],[10,"briefcase",jobs],[11,"menu",()=>toggle.click()]]){
   const b=el("button","zBottomItem");b.type="button";const text=el("span");b.append(icon(ico),text);b.onclick=fn;bar.append(b);entries.push([b,text,idx]);
 }
 function sync(){
   bar.hidden=panel.hidden||side.classList.contains("expanded");
   for(const [b,text,idx] of entries){
     text.textContent=cw()[idx];
     const current=idx===7&&$("homeNav")?.getAttribute("aria-current")==="page"||idx===10&&$("jobsButton")?.getAttribute("aria-current")==="page";
     if(current)b.setAttribute("aria-current","page");else b.removeAttribute("aria-current");
   }
   bar.setAttribute("aria-label",cw()[11]);
 }
 bottomRefresh=sync;panel.append(bar);
 new MutationObserver(sync).observe(panel,{attributes:true,attributeFilter:["hidden"]});
 new MutationObserver(sync).observe(side,{attributes:true,attributeFilter:["class"]});
 new MutationObserver(sync).observe(nav,{subtree:true,attributes:true,attributeFilter:["aria-current"]});sync();
}
const authWords={"en":["Start creating. Start from zero.","AI tools · Practical learning · Creator community","Navigation","Secure account access","Use your authenticator or recovery code only if 2FA is enabled.","Passkey uses your device authentication when supported.","Open in Safari or Chrome if device authentication is unavailable here.","Email or username","Password","2FA / recovery code"],"ru":["Создавай будущее. Начни с нуля.","AI-инструменты · Практика · Сообщество авторов","Навигация","Защищённый вход","Код приложения или резервный код нужен только при включённой 2FA.","Passkey использует защиту твоего устройства, если она поддерживается.","Если биометрия здесь недоступна, открой сайт в Safari или Chrome.","Email или логин","Пароль","Код 2FA / резервный код"],"uk":["Створюй майбутнє. Почни з нуля.","AI-інструменти · Практика · Спільнота авторів","Навігація","Захищений вхід","Код застосунку або резервний код потрібен лише при увімкненій 2FA.","Passkey використовує захист пристрою, якщо підтримується.","Якщо біометрія недоступна, відкрий сайт у Safari або Chrome.","Email або логін","Пароль","Код 2FA / резервний код"],"pl":["Twórz przyszłość. Zacznij od zera.","Narzędzia AI · Praktyka · Społeczność twórców","Nawigacja","Bezpieczne logowanie","Kod aplikacji lub zapasowy jest potrzebny tylko przy aktywnym 2FA.","Passkey używa zabezpieczeń urządzenia, jeśli jest obsługiwany.","Jeśli biometria jest niedostępna, otwórz stronę w Safari lub Chrome.","Email lub login","Hasło","Kod 2FA / kod zapasowy"]};
let authRelabel=null;
function authDesign(){
 const auth=$("auth"),login=$("login"),heroBox=document.querySelector("body>.hero"),header=document.querySelector("body>header");if(!auth||!login||!heroBox||!header)return;
 const aw=()=>authWords[locale()];
 heroBox.classList.add("zAuthHero");auth.classList.add("zAuthCard");
 const art=el("div","zAuthArt");art.append(stage());const pause=el("button","zPause");pause.type="button";pause.onclick=()=>{paused=!paused;motion()};art.append(pause);scenes.push([art,pause]);
 const eyebrow=heroBox.querySelector(".eyebrow");if(eyebrow)eyebrow.after(art);else heroBox.prepend(art);
 const slogan=el("p","zAuthSlogan"),tagline=el("p","zAuthTagline");heroBox.append(slogan,tagline);
 const seal=el("div","zAuthSeal"),sealText=el("span");seal.append(icon("shield-check"),sealText);auth.prepend(seal);
 const hint=el("p","zAuthHint"),passHint=el("p","zAuthHint");const code=login.querySelector('input[name="code"]'),identifier=$("loginIdentifier"),password=login.querySelector('input[name="password"]'),passkey=$("passkeyLogin");
 // Do not add buttons before the original submit button: the existing login handler uses the first button.
 if(code){code.after(hint);code.setAttribute("aria-describedby","zAuthMfaHint");hint.id="zAuthMfaHint";code.autocapitalize="none";code.spellcheck=false}
 if(identifier){identifier.autocapitalize="none";identifier.spellcheck=false}
 if(password)password.autocomplete="current-password";
 if(passkey){passkey.after(passHint);passHint.id="zAuthPassHint";passkey.setAttribute("aria-describedby",passHint.id)}
 const brandNode=header.querySelector(".brand"),oldMark=brandNode?.querySelector(".mark");if(oldMark)oldMark.replaceWith(orb());
 const nav=el("details","zAuthMenu"),summary=el("summary"),navLabel=el("span"),box=el("div","zModuleLinks");summary.append(icon("menu"),navLabel);
 const original=Array.from(header.children).filter(n=>n.tagName==="A");
 for(const a of original){const key=a.getAttribute("href")?.split("?")[0],data=navMap[key];const wrap=el("div","zAuthLink");wrap.append(icon(data?.[1]||"folder"),a);box.append(wrap)}
 nav.append(summary,box);header.insertBefore(nav,lang?.parentElement===header?lang:null);
 nav.addEventListener("click",e=>{if(e.target.closest("a"))nav.open=false});document.addEventListener("click",e=>{if(!nav.contains(e.target))nav.open=false});document.addEventListener("keydown",e=>{if(e.key==="Escape"&&nav.open){nav.open=false;summary.focus()}});
 function sync(){const active=!auth.hidden&&!document.body.classList.contains("signedIn");if(document.body.classList.contains("zAuthMode")!==active)document.body.classList.toggle("zAuthMode",active);if(nav.hidden===active)nav.hidden=!active;if(!active)nav.open=false;const recovery=$("zRecoveryLink");if(recovery)recovery.hidden=!active;art.classList.toggle("zAuthInactive",!active)}
 new MutationObserver(sync).observe(auth,{attributes:true,attributeFilter:["hidden"]});new MutationObserver(sync).observe(document.body,{attributes:true,attributeFilter:["class"]});
 // Avoid a class mutation observer feedback loop: classList.toggle only when state differs.
 authRelabel=()=>{const a=aw();const recovery=$("zRecoveryLink")?.querySelector("a");if(recovery)recovery.textContent=({en:"Display options",ru:"Настройки отображения",uk:"Налаштування відображення",pl:"Ustawienia wyglądu"})[locale()]||"Display options";slogan.textContent=a[0];tagline.textContent=a[1];navLabel.textContent=a[2];sealText.textContent=a[3];hint.textContent=a[4];passHint.textContent=passkey&&!passkey.hidden?a[5]:a[6];if(identifier)identifier.setAttribute("aria-label",a[7]);if(password)password.setAttribute("aria-label",a[8]);if(code)code.setAttribute("aria-label",a[9]);for(const a of original){const raw=a.getAttribute("href");if(raw?.startsWith("/")&&!raw.startsWith("//"))a.href=url(raw)}};
 if(passkey)new MutationObserver(()=>authRelabel()).observe(passkey,{attributes:true,attributeFilter:["hidden"]});
 authRelabel();sync();
}
const profileWords={"en":["My profile","Account & security","Your Academy plan","Owner control center","Manage Academy","Operations","Finance & partners","Content & community","System monitor & support","Back to overview","Students","Paid enrollments","Completed lessons","Exam attempts","Certificates","Public reviews","Submitted projects","Referral registrations","Paid referrals","Average rating","Account settings","Your account"],"ru":["Мой профиль","Аккаунт и безопасность","Твой пакет обучения","Центр управления владельца","Управление академией","Пользователи и управление","Финансы и партнёры","Контент и сообщество","Мониторинг и поддержка","Вернуться на главную","Студенты","Оплаченные пакеты","Завершённые уроки","Попытки экзаменов","Сертификаты","Публичные отзывы","Отправленные проекты","Реферальные регистрации","Оплаченные рефералы","Средняя оценка","Настройки аккаунта","Твой аккаунт"],"uk":["Мій профіль","Акаунт і безпека","Твій пакет навчання","Центр керування власника","Керування академією","Користувачі й керування","Фінанси й партнери","Контент і спільнота","Моніторинг і підтримка","На головну","Студенти","Оплачені пакети","Завершені уроки","Спроби іспитів","Сертифікати","Публічні відгуки","Надіслані проєкти","Реферальні реєстрації","Оплачені реферали","Середня оцінка","Налаштування акаунта","Твій акаунт"],"pl":["Mój profil","Konto i bezpieczeństwo","Twój pakiet nauki","Centrum właściciela","Zarządzanie akademią","Użytkownicy i zarządzanie","Finanse i partnerzy","Treści i społeczność","Monitoring i pomoc","Wróć do startu","Studenci","Opłacone pakiety","Ukończone lekcje","Próby egzaminów","Certyfikaty","Opinie publiczne","Przesłane projekty","Rejestracje poleconych","Opłacone polecenia","Średnia ocena","Ustawienia konta","Twoje konto"]},pw=()=>profileWords[locale()];
let profileRefresh=null;
function profileDesign(){
 const overview=$("workspaceOverview"),owner=$("ownerNav"),extra=$("extra"),nav=$("academyNav"),panel=$("panel"),identity=$("accountName"),accountId=$("accountId"),badge=$("accountBadge"),plan=$("workspacePlan");
 if(!overview||!owner||!extra||!nav||!panel||!identity||!accountId||!badge||!plan)return;
 const allowed=id=>{const n=$(id);return !!n&&!n.hidden&&!n.disabled&&!n.closest("[hidden]")};
 const profile=el("section","zProfileCard");profile.id="zProfileCard";
 const head=el("div","zProfileHead"),avatar=el("div","zProfileAvatar"),copy=el("div","zProfileIdentity"),eyebrow=el("small"),name=el("h2"),handle=el("p"),role=el("span","zProfileBadge");
 copy.append(eyebrow,name,handle,role);head.append(avatar,copy);
 const planRow=el("div","zProfilePlan"),planLabel=el("span"),planValue=el("strong");planRow.append(planLabel,planValue);
 const actions=el("div","zProfileActions");
 const accountControls=[["securityButton","lock"],["mfaButton","shield-check"],["passkeySettings","lock"]];
 const controlButtons=[];
 function navButton(id,ico){const btn=el("button","zProfileButton");btn.type="button";const label=el("span");btn.append(icon(ico),label);btn.onclick=()=>{if(allowed(id))$(id).click()};controlButtons.push({id,btn,label});return btn}
 for(const [id,ico] of accountControls)actions.append(navButton(id,ico));
 profile.append(head,planRow,actions);overview.prepend(profile);
 const hub=el("section","zOwnerHub");hub.id="zOwnerHub";hub.hidden=true;
 const title=el("h2"),intro=el("p","zOwnerIntro"),groups=el("div","zOwnerGroups");hub.append(title,intro,groups);
 const blocks=[];
 const sections=[[5,["admin","directoryAdmin","networkAdmin","founderAdmin"]],[6,["treasuryAdmin","partnerAdmin","acquisitionAdmin"]],[7,["contentAdmin","marketplaceAdmin","jobsAdmin","communityAdmin"]]];
 for(const [i,ids] of sections){const section=el("div","zOwnerGroup"),heading=el("h3"),grid=el("div","zOwnerGrid");for(const id of ids)grid.append(navButton(id,navIcons[id]||"shield-check"));section.append(heading,grid);groups.append(section);blocks.push({i,ids,section,heading})}
 const support=el("a","zProfileButton zOwnerSupport");support.append(icon("headphones"),el("span"));hub.append(support);
 // This is a shortcut panel, not an additional source of account or administrator privileges.
 overview.prepend(hub);
 const ownerRail=el("div","zOwnerRail");ownerRail.id="zOwnerRail";ownerRail.hidden=true;const back=el("button","zProfileButton");back.type="button";back.append(icon("layout-dashboard"),el("span"));back.onclick=()=>{if(allowed("homeNav"))$("homeNav").click()};const railTitle=el("strong");ownerRail.append(railTitle,back);extra.before(ownerRail);
 const metrics=["Students","Paid enrollments","Completed lessons","Exam attempts","Certificates","Public reviews","Submitted projects","Referral registrations","Paid referrals","Average rating"];
 const metricIcons=["users","wallet","book-open","checklist","graduation","message","image","network","gift","trophy"];
 function polishAdmin(){
   if(!allowed("admin")||$("admin").getAttribute("aria-current")!=="page"||extra.hidden)return;
   for(const card of extra.querySelectorAll("article")){
     const small=card.querySelector(":scope > small"),value=card.querySelector(":scope > h2");if(!small||!value)continue;
     let index=Number(card.dataset.zMetric);if(!card.hasAttribute("data-z-metric")){index=metrics.indexOf(small.textContent.trim());if(index<0)continue;card.dataset.zMetric=String(index);card.classList.add("zAdminMetric");const art=el("span","zMetricIcon");art.append(icon(metricIcons[index]));card.prepend(art);card.parentElement.classList.add("zAdminMetrics")}
     const translated=pw()[10+index];if(translated&&small.textContent!==translated)small.textContent=translated;
   }
 }
 function sync(){
   const signed=!panel.hidden;
   const own=signed&&!owner.hidden&&sections.some(([,ids])=>ids.some(allowed));
   profile.hidden=!signed;hub.hidden=!own;
   const n=identity.textContent.trim(),h=accountId.textContent.trim();
   name.textContent=n||pw()[21];handle.textContent=h;handle.hidden=!h;
   avatar.textContent=Array.from(n||"Z").slice(0,2).join("").toLocaleUpperCase();
   role.textContent=badge.hidden?"":badge.textContent;role.hidden=badge.hidden||!role.textContent;
   planValue.textContent=plan.textContent;eyebrow.textContent=pw()[0];planLabel.textContent=pw()[2];
   title.textContent=pw()[3];intro.textContent=pw()[4];
   for(const {id,btn,label} of controlButtons){btn.hidden=!signed||!allowed(id);label.textContent=$(id+"Label")?.textContent||$(id)?.textContent||""}
   for(const block of blocks){block.heading.textContent=pw()[block.i];block.section.hidden=!block.ids.some(allowed)}
   support.hidden=!own;support.href=url("/support");support.lastElementChild.textContent=pw()[8];
   const ownerActive=own&&sections.some(([,ids])=>ids.some(id=>allowed(id)&&$(id).getAttribute("aria-current")==="page"));
   ownerRail.hidden=!ownerActive||extra.hidden;railTitle.textContent=pw()[3];back.lastElementChild.textContent=pw()[9];
   polishAdmin();
 }
 let scheduled=false;const schedule=()=>{if(scheduled)return;scheduled=true;queueMicrotask(()=>{scheduled=false;sync()})};
 // Only observe original state nodes; never observe generated profile/owner contents.
 const obs=new MutationObserver(schedule);
 for(const node of [identity,accountId,badge,plan])obs.observe(node,{childList:true,characterData:true,subtree:true,attributes:true,attributeFilter:["hidden"]});
 obs.observe(nav,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:["hidden","disabled","aria-current"]});
 obs.observe(panel,{attributes:true,attributeFilter:["hidden"]});obs.observe(extra,{attributes:true,attributeFilter:["hidden"],childList:true});
 profileRefresh=sync;sync();
}
const learningWords={
 en:["Official exam","Answered","Next unanswered question","All questions answered. Review your choices before submitting.","Lesson steps","Practice Lab"],
 ru:["Официальный экзамен","Отвечено","Следующий вопрос без ответа","Все вопросы заполнены. Проверь ответы перед отправкой.","Этапы урока","Практическая лаборатория"],
 uk:["Офіційний іспит","Відповіді","Наступне запитання без відповіді","На всі запитання є відповіді. Перевір їх перед надсиланням.","Етапи уроку","Практична лабораторія"],
 pl:["Oficjalny egzamin","Odpowiedziano","Następne pytanie bez odpowiedzi","Wszystkie pytania mają odpowiedzi. Sprawdź je przed wysłaniem.","Etapy lekcji","Laboratorium praktyczne"]};
let learningRefresh=null;
function learningDesign(){
 const lesson=$("lesson"),extra=$("extra"),panel=$("panel");if(!lesson||!extra||!panel)return;
 const words=()=>learningWords[locale()]||learningWords.en,examViews=new WeakMap(),guidedViews=new WeakMap();
 let lastRoot=null,lastExtraKind="",lastExtraRoot=null,scheduled=false;
 const setText=(n,value)=>{if(n.textContent!==value)n.textContent=value};
 function exam(form){
   const fields=Array.from(form.querySelectorAll(":scope > fieldset")).filter(f=>f.querySelector('input[type="radio"]'));if(!fields.length)return;
   let v=examViews.get(form);
   if(!v){
     form.classList.add("zExamForm");
     const box=el("div","zExamHeader"),title=el("h2"),copy=el("span"),status=el("p"),bar=el("progress","zExamMeter"),jump=el("button","zAction");
     jump.type="button";title.append(icon("checklist"),copy);status.setAttribute("aria-live","polite");box.append(title,status,bar,jump);form.prepend(box);
     v={copy,status,bar,jump};examViews.set(form,v);
     jump.addEventListener("click",()=>{const target=fields.find(f=>!f.querySelector('input[type="radio"]:checked'));if(!target)return;target.scrollIntoView({block:"start",behavior:"auto"});target.querySelector('input[type="radio"]')?.focus({preventScroll:true})});
     form.addEventListener("change",()=>exam(form));form.addEventListener("reset",()=>queueMicrotask(()=>exam(form)));
   }
   let count=0;for(const field of fields){const checked=!!field.querySelector('input[type="radio"]:checked');field.classList.toggle("zAnswered",checked);if(checked)count++}
   setText(v.copy,words()[0]);setText(v.jump,words()[2]);setText(v.status,words()[1]+": "+count+" / "+fields.length+(count===fields.length?" · "+words()[3]:""));
   v.bar.max=fields.length;v.bar.value=count;v.bar.setAttribute("aria-label",words()[1]);const allAnswered=count===fields.length;if(v.jump.hidden!==allAnswered)v.jump.hidden=allAnswered;
 }
 function guided(root){
   const heading=root.querySelector(":scope > h2"),counter=root.querySelector(":scope > p"),parts=Array.from(root.querySelectorAll(":scope > div"));
   if(!heading||!counter||parts.length!==2||!/^\s*[1-4]\s*\/\s*4\b/.test(counter.textContent))return;
   root.classList.add("zLearningGuide");counter.classList.add("zLearningStepLabel");parts[0].classList.add("zLearningStep");parts[1].classList.add("zLearningNav");
   let bar=guidedViews.get(root);
   if(!bar){bar=el("progress","zLearningMeter");bar.max=4;counter.after(bar);guidedViews.set(root,bar)}
   bar.value=Number(counter.textContent.trim()[0]);bar.setAttribute("aria-label",words()[4]);
   const teacher=root.querySelector(":scope > article");
   if(teacher&&!teacher.classList.contains("zTeacherCard")){teacher.classList.add("zTeacherCard");teacher.querySelector("h3")?.prepend(icon("graduation"))}
 }
 function sync(){
   scheduled=false;
   if(panel.hidden){lastRoot=null;lastExtraRoot=null;lastExtraKind="";extra.classList.remove("zPracticePanel","zTutorPanel");return}
   if(!lesson.hidden&&!lesson.closest("[hidden]")){
     const root=lesson.firstElementChild;
     if(root?.tagName==="FORM")exam(root);else if(root?.tagName==="SECTION")guided(root);
     if(root&&root!==lastRoot){lastRoot=root;lesson.scrollIntoView({block:"start",behavior:"auto"})}
   }else lastRoot=null;
   const h=extra.querySelector(":scope > h2"),heading=h?.textContent.trim()||"";
   const practice=Object.values(learningWords).some(w=>heading.startsWith(w[5]+" ·"))&&!!extra.querySelector('input[type="number"]')&&!!extra.querySelector(":scope > textarea");
   const role=Array.from(extra.querySelectorAll(":scope > select")).find(n=>["teacher","coach","code","exam","project"].every(v=>Array.from(n.options).some(o=>o.value===v)));
   const tutor=!!role&&!!extra.querySelector(":scope > textarea")&&!!extra.querySelector(":scope > pre");
   extra.classList.toggle("zPracticePanel",!extra.hidden&&practice);extra.classList.toggle("zTutorPanel",!extra.hidden&&tutor);
   const kind=extra.hidden?"":practice?"practice":tutor?"tutor":"",first=extra.firstElementChild;
   if(kind&&(kind!==lastExtraKind||first!==lastExtraRoot))extra.scrollIntoView({block:"start",behavior:"auto"});
   lastExtraKind=kind;lastExtraRoot=first;
 }
 const schedule=()=>{if(!scheduled){scheduled=true;queueMicrotask(sync)}};
 const observer=new MutationObserver(schedule);
 observer.observe(lesson,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:["hidden"]});
 observer.observe(extra,{childList:true,attributes:true,attributeFilter:["hidden"]});
 observer.observe(panel,{attributes:true,attributeFilter:["hidden"]});
 learningRefresh=schedule;schedule();
}
// Optional presentation modules cannot prevent the original authentication handlers from running.
function enhance(name,run){
 try{run()}catch(error){console.warn("Academy presentation module:",name,error?.name||"Error")}
}
function dashboard(){
 const overview=$("workspaceOverview"),panel=$("panel");
 enhance("auth",()=>{authDesign();});
 let started=false,observer=null;
 function activate(){
   if(started||panel?.hidden)return;
   started=true;observer?.disconnect();
   enhance("overview",()=>overview.prepend(hero(true),quick(),tiles()));
   enhance("courses",()=>{courseCards();});
   enhance("mobile-nav",()=>{bottomNav();});
   enhance("profile",()=>{profileDesign();});
   enhance("learning",()=>{learningDesign();});
   enhance("business",()=>{businessDesign();});
   enhance("production",()=>{productionDesign();});
   enhance("social",()=>{socialDesign();});
   enhance("administration",()=>{administrationDesign();});
   enhance("compact",()=>{compactOverview();});
   enhance("onboarding",()=>{onboardingDesign();});
   enhance("teacher-center",()=>{teacherCenterDesign();});
   enhance("project-mentor",()=>{projectMentorDesign();});
   enhance("career-center",()=>{careerCenterDesign();});
   enhance("business-studio",()=>{businessStudioDesign();});
   enhance("workforce",()=>{workforceDesign();});
   enhance("factory",()=>{factoryDesign();});
   enhance("delivery-center",installDeliveryCenter);
   enhance("creator-evidence",creatorEvidenceDesign);
   enhance("command-dock",()=>{commandDockDesign();});
   enhance("navigation-icons",()=>{
     const mark=document.querySelector(".sideMark");if(mark)mark.replaceChildren(orb());
     for(const n of document.querySelectorAll("#academyNav .navItem")){
       const name=navIcons[n.id]||navMap[n.getAttribute("href")?.split("?")[0]]?.[1];
       if(name&&n.firstElementChild)n.firstElementChild.replaceWith(icon(name))
     }
     const eye=document.querySelector(".workspaceTop .eyebrow");if(eye)eye.textContent="ZER0LIFE / ACADEMY 2027";
   });
   enhance("locale",update);
 }
 // Do not construct the signed-in dashboard while a visitor is on the login screen.
 if(panel?.hidden){
   observer=new MutationObserver(activate);
   observer.observe(panel,{attributes:true,attributeFilter:["hidden"]});
 }else activate();
}
function moduleHeader(){
 const h=document.querySelector("main>header,main>nav");if(!h)return;
 h.classList.add("zModuleHeader");let brand=h.querySelector(":scope > strong");
 if(!brand){brand=el("strong","","ZER0LIFE / ACADEMY");h.prepend(brand)}
 brand.classList.add("zModuleBrand");brand.prepend(orb());
 const original=Array.from(h.children).filter(n=>n.tagName==="A");
 const back=original.find(a=>a.getAttribute("href")?.split("?")[0]==="/dashboard");
 if(back){back.classList.add("zModuleBack")}else{const a=route("/dashboard",6,"graduation","zModuleBack");h.append(a)}
 const remaining=original.filter(a=>a!==back);if(!remaining.length)return;
 const d=el("details","zModuleNav"),summary=el("summary");summary.append(icon("menu"),label(el("span"),26));const box=el("div","zModuleLinks");
 for(const a of remaining){const p=a.getAttribute("href"),data=navMap[p?.split("?")[0]];const row=el("div","zModuleLinkRow");row.append(icon(data?.[1]||"folder"),a);box.append(row)}
 d.append(summary,box);h.insertBefore(d,lang?.parentElement===h?lang:null);
 d.addEventListener("click",e=>{if(e.target.closest("a"))d.open=false});
 document.addEventListener("click",e=>{if(!d.contains(e.target))d.open=false});
 document.addEventListener("keydown",e=>{if(e.key==="Escape"&&d.open){d.open=false;summary.focus()}});
}
function moduleDesign(){
 const main=document.querySelector("main");if(!main)return;document.body.classList.add("zModulePage");
 const heading=main.querySelector(":scope > h1,:scope > .hero > h1");
 if(!heading)return;
 const glyphs={"/creator-suite":"layers","/ai-workspace":"wand-sparkles","/support":"headphones","/command-center":"layout-dashboard","/agency":"network","/creator-analytics":"chart","/client-portal":"users","/production-cost":"wallet","/marketplace":"briefcase","/hire":"briefcase","/animation-studio":"video","/music-studio":"music","/website-builder":"code","/automation-studio":"workflow","/design-studio":"palette","/voice-studio":"mic","/local-media":"image","/graduate-showcase":"graduation"};
 const glyph=glyphs[location.pathname];if(!glyph)return;
 const art=el("span","zModuleArt");art.setAttribute("aria-hidden","true");art.append(icon(glyph));
 const oldHero=heading.closest("section.hero");
 // Preserve existing form and link elements, IDs, and localized text nodes.
 if(oldHero){oldHero.classList.add("zModuleExistingHero");const kicker=oldHero.querySelector("small");if(kicker)kicker.classList.add("zModuleKicker");return}
 const intro=heading.nextElementSibling?.tagName==="P"?heading.nextElementSibling:null;
 const tag=heading.previousElementSibling?.classList.contains("tag")?heading.previousElementSibling:null;
 const hero=el("div","zModuleHero"),copy=el("div","zModuleCopy");
 const kicker=el("div","zModuleKicker","ZER0LIFE / AURORA");hero.append(copy,art);(tag||heading).before(hero);
 if(tag){tag.classList.add("zModuleKicker");copy.append(tag)}else copy.append(kicker);
 copy.append(heading);if(intro)copy.append(intro);
}
const businessWords={
 en:["Creator Business","Find work","Services marketplace","My services","My portfolio","Client portal","Agency","Analytics","Cost calculator","New project","My projects","Project detail","My agencies","Agency details","Back to top","Business workspace"],
 ru:["Creator Business","Найти заказы","Биржа услуг","Мои услуги","Моё портфолио","Кабинет клиента","Агентство","Аналитика","Калькулятор затрат","Новый проект","Мои проекты","Детали проекта","Мои агентства","Детали агентства","Наверх","Бизнес-кабинет"],
 uk:["Creator Business","Знайти замовлення","Біржа послуг","Мої послуги","Моє портфоліо","Кабінет клієнта","Агенція","Аналітика","Калькулятор витрат","Новий проєкт","Мої проєкти","Деталі проєкту","Мої агенції","Деталі агенції","Вгору","Бізнес-кабінет"],
 pl:["Creator Business","Znajdź zlecenia","Giełda usług","Moje usługi","Moje portfolio","Panel klienta","Agencja","Analityka","Kalkulator kosztów","Nowy projekt","Moje projekty","Szczegóły projektu","Moje agencje","Szczegóły agencji","Do góry","Panel biznesowy"]};
let businessRefresh=null;
function businessDesign(){
 const main=document.querySelector("main"),dashboard=!!$("workspaceOverview"),path=location.pathname;
 const businessPages=["/marketplace","/hire","/client-portal","/agency","/creator-analytics","/production-cost","/graduate-showcase"];
 if(!dashboard&&(!main||!businessPages.includes(path)))return;
 const bw=()=>businessWords[locale()]||businessWords.en;
 const labels=[],refreshers=[];
 const text=(node,i)=>{labels.push([node,i]);node.textContent=bw()[i];return node};
 const bar=el("section","zBusinessHub"),head=el("h2"),grid=el("div","zBusinessGrid");
 head.append(icon("briefcase"),text(el("span"),0));bar.append(head,grid);
 const routes=[["/dashboard?module=jobs",1,"briefcase"],["/marketplace",2,"users"],["/dashboard?module=marketplace",3,"layers"],["/client-portal",5,"users"],["/agency",6,"network"],["/creator-analytics",7,"chart"],["/production-cost",8,"wallet"]];
 function decorate(a,i,glyph){const art=el("span","zBusinessIcon");art.append(icon(glyph));a.append(art,text(el("span"),i));grid.append(a);return a}
 for(const [p,i,glyph] of routes){const a=el("a","zBusinessLink");a.href=url(p);links.push([a,p]);if(!dashboard&&p===path)a.setAttribute("aria-current","page");decorate(a,i,glyph)}
 if(dashboard){
   const port=$("portfolioButton");if(port){const a=el("button","zBusinessLink");a.type="button";decorate(a,4,"image");a.onclick=()=>{if(!port.hidden&&!port.disabled)port.click()};refreshers.push(()=>{a.hidden=port.hidden||port.disabled||!!port.closest("[hidden]")})}
   $("workspaceOverview").append(bar);
 }else{
   document.body.classList.add("zBusinessPage");
   const anchor=main.querySelector(":scope > .zModuleHero,:scope > section.hero")||main.querySelector(":scope > nav,:scope > header");if(anchor)anchor.after(bar);else main.prepend(bar);
   const privateBox=$("private");
   if(privateBox&&(path==="/client-portal"||path==="/agency")){
     const nav=el("nav","zBusinessLocalNav");nav.setAttribute("aria-label",bw()[15]);
     const create=privateBox.querySelector(":scope > section");
     const specs=path==="/client-portal"?[[create,9],[$("jobs"),10],[$("detail"),11]]:[[create,9],[$("list"),12],[$("detail"),13]];
     for(const [target,i] of specs){if(!target)continue;const b=el("button","zAction");b.type="button";text(b,i);nav.append(b);
       b.onclick=()=>{if(privateBox.hidden||target.hidden)return;target.scrollIntoView({block:"start",behavior:"auto"});const focus=target.querySelector("h2,h3,input,button");if(focus){if(!focus.matches("input,button"))focus.tabIndex=-1;focus.focus({preventScroll:true})}};
       const sync=()=>{b.hidden=target.hidden||(i===13&&!target.childElementCount)};refreshers.push(sync);new MutationObserver(sync).observe(target,{childList:true,attributes:true,attributeFilter:["hidden"]});
     }
     privateBox.prepend(nav);refreshers.push(()=>nav.setAttribute("aria-label",bw()[15]));
   }
 }
 businessRefresh=()=>{for(const [n,i] of labels)n.textContent=bw()[i];for(const fn of refreshers)fn()};businessRefresh();
 if(dashboard&&$("portfolioButton"))new MutationObserver(()=>{for(const fn of refreshers)fn()}).observe($("portfolioButton"),{attributes:true,attributeFilter:["hidden","disabled"]});
}
const productionWords={
 en:["AI Production Center","Create with your own tools","Find a lab by name","All labs","Labs found","No matching labs","Show all","Higgsfield · graduate access","External provider credits; check prices before generating.","Local/browser tools may require downloads or compatible hardware.","Film & video","Digital characters","AI agents","3D reconstruction","Motion lab","Image & design","Music & sound","Voice","Web & apps","Local AI","Creator labs","Open lab","Animation studio"],
 ru:["AI Production Center","Создавай с помощью своих инструментов","Найти лабораторию по названию","Все лаборатории","Найдено лабораторий","Ничего не найдено","Показать все","Higgsfield · доступ выпускникам","Кредиты внешнего сервиса; проверяй цены до генерации.","Локальные инструменты могут требовать загрузки моделей и совместимого устройства.","Кино и видео","Цифровые персонажи","AI-агенты","3D-реконструкция","Motion Lab","Изображения и дизайн","Музыка и звук","Голос","Сайты и приложения","Локальный AI","Лаборатории авторов","Открыть лабораторию","Студия анимации"],
 uk:["AI Production Center","Створюй зі своїми інструментами","Знайти лабораторію за назвою","Усі лабораторії","Знайдено лабораторій","Нічого не знайдено","Показати всі","Higgsfield · доступ випускникам","Кредити зовнішнього сервісу; перевір ціни перед генерацією.","Локальні інструменти можуть потребувати завантаження моделей і сумісного пристрою.","Кіно та відео","Цифрові персонажі","AI-агенти","3D-реконструкція","Motion Lab","Зображення й дизайн","Музика та звук","Голос","Сайти й застосунки","Локальний ШІ","Лабораторії авторів","Відкрити лабораторію","Студія анімації"],
 pl:["AI Production Center","Twórz własnymi narzędziami","Znajdź laboratorium po nazwie","Wszystkie laboratoria","Znalezione laboratoria","Brak wyników","Pokaż wszystkie","Higgsfield · dostęp absolwentów","Kredyty zewnętrznego dostawcy; sprawdź ceny przed generowaniem.","Narzędzia lokalne mogą wymagać pobrania modeli i zgodnego urządzenia.","Film i wideo","Postacie cyfrowe","Agenci AI","Rekonstrukcja 3D","Motion Lab","Obrazy i projektowanie","Muzyka i dźwięk","Głos","Strony i aplikacje","Lokalne AI","Laboratoria twórców","Otwórz laboratorium","Studio animacji"]};
let productionRefresh=null;
function productionDesign(){
 const journey=$("creatorJourney"),main=document.querySelector("main"),dashboard=!!journey,path=location.pathname;
 if(!dashboard&&(!main||!["/ai-workspace","/creator-suite","/free-ai"].includes(path)))return;
 const pw=()=>productionWords[locale()]||productionWords.en;
 const labels=[];function tr(n,i){labels.push([n,i]);n.textContent=pw()[i];return n}
 const box=el("section","zProductionHub"),head=el("h2"),grid=el("div","zProductionGrid");
 head.append(icon("layers"),tr(el("span"),0));box.append(head,tr(el("p"),1),grid);
 const linksData=[["/animation-studio",22,"video"],["/openmvs-lab",13,"box"],["/openmotion-lab",14,"workflow"],["/design-studio",15,"palette"],["/music-studio",16,"music"],["/voice-studio",17,"mic"],["/website-builder",18,"code"],["/free-ai",19,"cpu"]];
 const labQueries=[[10,"video","film|кино|фильм|кіно|фільм"],[11,"users","influencer|digital human|инфлюенсер|інфлюенсер|персонаж"],[12,"network","agent|агент"],[7,"video","higgsfield"],[20,"layers",""]];
 const normalize=s=>s.normalize("NFKD").replace(/\p{M}/gu,"").toLowerCase().replace(/ł/g,"l");
 function tileNode(tag,i,glyph){const n=el(tag,"zProductionTile");const art=el("span","zProductionIcon");art.append(icon(glyph));n.append(art,tr(el("span"),i));grid.append(n);return n}
 for(const [p,i,g] of linksData){const a=tileNode("a",i,g);a.href=url(p);links.push([a,p])}
 const filters=el("div","zLabSearch"),input=el("input"),clear=tr(el("button","zAction"),6),count=el("p","zLabCount");
 input.type="search";input.maxLength=100;input.autocomplete="off";clear.type="button";count.setAttribute("role","status");filters.append(input,clear);
 let preset=null,requested=false;
 function cards(){return journey?Array.from(journey.querySelectorAll(":scope > details")).filter(n=>!n.hidden):[]}
 function apply(){
   if(!journey)return;const q=normalize(input.value.trim()),need=q.split(/\s+/).filter(Boolean),all=cards();let found=0;
   for(const card of all){const title=normalize(card.querySelector(":scope > summary")?.textContent||"");const match=preset!==null?(!preset||preset.split("|").some(x=>title.includes(normalize(x)))):need.every(x=>title.includes(x));card.classList.toggle("zLabFiltered",!match);if(match)found++}
   const message=found?pw()[4]+": "+found+" / "+all.length:pw()[5];if(count.textContent!==message)count.textContent=message;
 }
 function focusLabs(i,query){if(!journey)return;expandOverviewHub('.zProductionHub');revealCreatorLabs();preset=query;input.value=query?pw()[i]:"";apply();filters.scrollIntoView({block:"start",behavior:"auto"});input.focus({preventScroll:true})}
 for(const [i,g,q] of labQueries){
   if(dashboard){const b=tileNode("button",i,g);b.type="button";b.onclick=()=>focusLabs(i,q)}
   else{const a=tileNode("a",i,g),p="/dashboard?lab="+encodeURIComponent(i);a.href=url(p);links.push([a,p])}
 }
 const note=el("div","zProductionNote");note.append(tr(el("p"),9),tr(el("p"),8));box.append(note);
 if(dashboard){
   box.id="zProductionHub";journey.before(box);box.append(filters,count);
   input.addEventListener("input",()=>{revealCreatorLabs();preset=null;apply()});clear.onclick=()=>{revealCreatorLabs();preset=null;input.value="";apply();input.focus()};
   const refresh=()=>{
     apply();
     if(!requested&&cards().length&&!journey.hidden&&!$("panel")?.hidden){requested=true;const v=new URLSearchParams(location.search).get("lab"),spec=labQueries.find(x=>String(x[0])===v);if(spec)focusLabs(spec[0],spec[2])}
   };
   new MutationObserver(refresh).observe(journey,{childList:true,attributes:true,attributeFilter:["hidden"]});
   if($("panel"))new MutationObserver(refresh).observe($("panel"),{attributes:true,attributeFilter:["hidden"]});
   refresh();
 }else{const anchor=main.querySelector(":scope > .zModuleHero,:scope > .zAuroraHero")||main.querySelector(":scope > header,:scope > nav");if(anchor)anchor.after(box);else main.prepend(box)}
 productionRefresh=()=>{for(const [n,i] of labels)n.textContent=pw()[i];input.placeholder=pw()[2];input.setAttribute("aria-label",pw()[2]);if(preset!==null&&preset){const spec=labQueries.find(x=>x[2]===preset);if(spec)input.value=pw()[spec[0]]}apply()};productionRefresh();
}
const socialWords={
 en:["Social & Community","Portfolio & public profile","Student discussions","Share my work","Build a case study","Create service page","Find clients","Marketplace","Search loaded discussions","Matching loaded posts","Clear search","No matching loaded posts","Search covers loaded posts only. Load more to search further.","Publishing remains voluntary. Community posts require moderation; external sharing needs your confirmation."],
 ru:["Social & Community","Портфолио и публичный профиль","Сообщество студентов","Поделиться работой","Создать кейс","Страница услуг","Привлечение клиентов","Биржа услуг","Поиск по загруженным обсуждениям","Найдено среди загруженных","Очистить поиск","Нет совпадений среди загруженных","Поиск работает по загруженным темам. Загрузи ещё для расширения поиска.","Публикация добровольная. Темы проходят модерацию, а внешняя публикация требует твоего подтверждения."],
 uk:["Social & Community","Портфоліо й публічний профіль","Спільнота студентів","Поділитися роботою","Створити кейс","Сторінка послуг","Залучення клієнтів","Біржа послуг","Пошук у завантажених обговореннях","Знайдено серед завантажених","Очистити пошук","Немає збігів серед завантажених","Пошук працює із завантаженими темами. Завантаж ще для ширшого пошуку.","Публікація добровільна. Теми модеруються, а зовнішня публікація потребує підтвердження."],
 pl:["Social & Community","Portfolio i profil publiczny","Społeczność studentów","Udostępnij pracę","Utwórz studium przypadku","Strona usług","Pozyskiwanie klientów","Giełda usług","Szukaj we wczytanych dyskusjach","Znaleziono we wczytanych","Wyczyść wyszukiwanie","Brak pasujących wczytanych wpisów","Wyszukiwanie obejmuje wczytane wpisy. Wczytaj więcej, aby rozszerzyć wyniki.","Publikowanie jest dobrowolne. Dyskusje wymagają moderacji, a zewnętrzne udostępnianie — potwierdzenia."]};
let socialRefresh=null;
function socialDesign(){
 const overview=$("workspaceOverview"),journey=$("creatorJourney"),extra=$("extra"),nav=$("academyNav");if(!overview||!journey||!extra||!nav)return;
 const sw=()=>socialWords[locale()]||socialWords.en,labels=[],syncers=[];
 const tr=(node,i)=>{labels.push([node,i]);node.textContent=sw()[i];return node};
 const hub=el("section","zSocialHub"),heading=el("h2"),grid=el("div","zSocialGrid");
 heading.append(icon("users"),tr(el("span"),0));hub.append(heading,grid,tr(el("p","zSocialNotice"),13));overview.append(hub);
 const normalize=s=>s.normalize("NFKD").replace(/\p{M}/gu,"").toLowerCase().replace(/ł/g,"l");
 function tile(tag,i,g){const n=el(tag,"zSocialTile"),art=el("span","zSocialIcon");art.append(icon(g));n.append(art,tr(el("span"),i));grid.append(n);if(tag==="button")n.type="button";return n}
 for(const [i,id,g] of [[1,"portfolioButton","image"],[2,"communityButton","message"]]){
   const original=$(id);if(!original)continue;const b=tile("button",i,g);
   const sync=()=>{b.hidden=original.hidden||original.disabled};syncers.push(sync);
   b.onclick=()=>{if(!original.hidden&&!original.disabled)original.click()};
 }
 const labs=[[3,"share-2","Social Share Studio"],[4,"file","Creator Portfolio Builder"],[5,"layout-dashboard","Creator Service Page"],[6,"chart","Client Acquisition Lab"]];
 const findLab=prefix=>Array.from(journey.querySelectorAll(":scope > details")).find(n=>!n.hidden&&normalize(n.querySelector(":scope > summary")?.textContent||"").startsWith(normalize(prefix)));
 for(const [i,g,prefix] of labs){const b=tile("button",i,g);syncers.push(()=>{b.disabled=!findLab(prefix)});b.onclick=()=>{
   const target=findLab(prefix);if(!target)return;expandOverviewHub(".zProductionHub");revealCreatorLabs();
   const field=document.querySelector("#zProductionHub .zLabSearch input");
   if(field){field.value=prefix;field.dispatchEvent(new Event("input",{bubbles:true}))}
   target.open=true;target.scrollIntoView({block:"start",behavior:"auto"});target.querySelector(":scope > summary")?.focus({preventScroll:true})
 }}
 const market=tile("a",7,"briefcase");market.href=url("/marketplace");links.push([market,"/marketplace"]);
 let view=null,scheduled=false;
 function filter(){
   if(!view||!view.list.isConnected)return;
   const terms=normalize(view.input.value.trim()).split(/\s+/).filter(Boolean),items=Array.from(view.list.querySelectorAll(":scope > article"));let matches=0;
   for(const item of items){const text=normalize(item.textContent);const show=terms.every(t=>text.includes(t));item.classList.toggle("zSocialFiltered",!show);if(show)matches++}
   const text=terms.length&&!matches?sw()[11]:sw()[9]+": "+matches+" / "+items.length;if(view.count.textContent!==text)view.count.textContent=text;
 }
 function sync(){
   scheduled=false;for(const fn of syncers)fn();
   const active=$("communityButton")?.getAttribute("aria-current")==="page"&&!extra.hidden;
   const portfolio=$("portfolioButton")?.getAttribute("aria-current")==="page"&&!extra.hidden;
   extra.classList.toggle("zCommunityPanel",active);extra.classList.toggle("zPortfolioPanel",portfolio);
   if(!active){if(view?.bar.isConnected)view.bar.remove();view=null;return}
   const divs=Array.from(extra.querySelectorAll(":scope > div")).filter(n=>!n.classList.contains("zCommunitySearch"));
   if(divs.length<2)return;const list=divs[divs.length-1];
   if(!view||view.list!==list){
     if(view?.bar.isConnected)view.bar.remove();
     const bar=el("div","zCommunitySearch"),input=el("input"),clear=el("button","zAction"),count=el("p","zCommunityCount"),hint=el("small");
     input.type="search";input.maxLength=100;input.autocomplete="off";clear.type="button";count.setAttribute("role","status");bar.append(input,clear,count,hint);list.before(bar);
     view={bar,input,clear,count,hint,list};input.addEventListener("input",filter);clear.onclick=()=>{input.value="";filter();input.focus()};
   }
   view.input.placeholder=sw()[8];view.input.setAttribute("aria-label",sw()[8]);
   if(view.clear.textContent!==sw()[10])view.clear.textContent=sw()[10];
   if(view.hint.textContent!==sw()[12])view.hint.textContent=sw()[12];
   filter();
 }
 const schedule=()=>{if(!scheduled){scheduled=true;queueMicrotask(sync)}};
 const obs=new MutationObserver(schedule);obs.observe(extra,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:["hidden"]});obs.observe(nav,{subtree:true,attributes:true,attributeFilter:["aria-current","hidden","disabled"]});obs.observe(journey,{childList:true,attributes:true,attributeFilter:["hidden"]});
 socialRefresh=()=>{for(const [n,i] of labels)n.textContent=sw()[i];schedule()};socialRefresh();
}
const adminWords={
 en:["Administration & Control Center","Switch administrator module","Refresh active module","Jump to report section","Report sections","Open review queue","Sales and commission records","Administrator modules only. Actions continue to require server authorization.","Select section","Recorded payments are not wallet balance or net profit."],
 ru:["Administration & Control Center","Перейти в раздел администратора","Обновить текущий раздел","Перейти к разделу отчёта","Разделы отчёта","Открыть очередь проверки","Учтённые продажи и комиссии","Только для администратора. Действия по-прежнему проверяются сервером.","Выбери раздел","Учтённые платежи — не баланс кошелька и не чистая прибыль."],
 uk:["Administration & Control Center","Перейти до розділу адміністратора","Оновити поточний розділ","Перейти до розділу звіту","Розділи звіту","Відкрити чергу перевірки","Облік продажів і комісій","Лише для адміністратора. Дії перевіряються сервером.","Обери розділ","Облік платежів — не баланс гаманця і не чистий прибуток."],
 pl:["Administration & Control Center","Przejdź do modułu administratora","Odśwież bieżący moduł","Przejdź do sekcji raportu","Sekcje raportu","Otwórz kolejkę weryfikacji","Zarejestrowana sprzedaż i prowizje","Tylko dla administratora. Działania nadal wymagają autoryzacji serwera.","Wybierz sekcję","Zarejestrowane płatności to nie saldo portfela ani zysk netto."]};
let adminRefresh=null;
function administrationDesign(){
 const owner=$("ownerNav"),rail=$("zOwnerRail"),hub=$("zOwnerHub"),extra=$("extra"),panel=$("panel");
 if(!owner||!rail||!hub||!extra||!panel)return;
 const ids=["admin","founderAdmin","directoryAdmin","networkAdmin","treasuryAdmin","partnerAdmin","acquisitionAdmin","contentAdmin","marketplaceAdmin","jobsAdmin","communityAdmin"];
 const aw=()=>adminWords[locale()]||adminWords.en;
 const allowed=id=>{const n=$(id);return !panel.hidden&&!owner.hidden&&!!n&&!n.hidden&&!n.disabled&&!n.closest("[hidden]")};
 const active=()=>ids.find(id=>allowed(id)&&$(id).getAttribute("aria-current")==="page");
 const title=id=>$(id+"Label")?.textContent?.trim()||$(id)?.textContent?.trim()||id;
 const switcher=el("select","zAdminSwitch");switcher.id="zAdminSwitch";
 const refresh=el("button","zProfileButton zAdminRefresh"),refreshText=el("span");refresh.type="button";refresh.append(icon("refresh-cw"),refreshText);
 rail.append(switcher,refresh);
 switcher.onchange=()=>{const id=switcher.value;if(ids.includes(id)&&allowed(id))$(id).click()};
 refresh.onclick=()=>{const id=active();if(id&&confirm(aw()[2]+"?"))$(id).click()};
 const helper=el("p","zAdminNotice");hub.append(helper);
 const toc=el("div","zAdminReportNav");toc.hidden=true;const tocTitle=el("strong"),jump=el("select");toc.append(tocTitle,jump);extra.before(toc);
 let sections=[],lastOptions="",lastSections="",scheduled=false;
 const queueMap=[
 ["marketplaceAdmin",["Pending marketplace services","Услуги на модерации","Послуги на модерації","Usługi do moderacji"]],
 ["communityAdmin",["Pending community posts","Публикации на модерации","Публікації на модерації","Wpisy do moderacji"]],
 ["partnerAdmin",["Pending partners","Заявки партнёров","Заявки партнерів","Wnioski partnerów"]]];
 const scrollTo=n=>{if(n?.isConnected){n.scrollIntoView({block:"start",behavior:"auto"});n.tabIndex=-1;n.focus({preventScroll:true})}};
 jump.onchange=()=>{const n=sections[Number(jump.value)];if(active()==="founderAdmin"&&jump.value!=="")scrollTo(n)};
 function decorateFounder(){
   for(const grid of extra.querySelectorAll("div")){
     const children=Array.from(grid.children);
     if(children.length>=3&&children.every(n=>n.tagName==="ARTICLE"&&n.querySelector(":scope > small")&&n.querySelector(":scope > h3"))){
       grid.classList.add("zFounderMetrics");
       for(const card of children)card.classList.add("zFounderMetric");
     }
   }
   for(const bar of extra.querySelectorAll("progress[title]"))bar.closest("div")?.classList.add("zFounderSalesRow");
   for(const row of extra.querySelectorAll("p")){
     const value=row.firstChild?.nodeType===3?row.firstChild.textContent.trim():"";
     const spec=queueMap.find(([,names])=>names.some(n=>value.startsWith(n+":")));
     if(!spec)continue;
     row.classList.add("zModerationRow");
     let b=row.querySelector(":scope > .zModerationOpen");
     if(!b){b=el("button","zModerationOpen");b.type="button";const id=spec[0];b.onclick=()=>{if(active()==="founderAdmin"&&allowed(id))$(id).click()};row.append(b)}
     if(b.textContent!==aw()[5])b.textContent=aw()[5];const hide=!allowed(spec[0]);if(b.hidden!==hide)b.hidden=hide;
   }
 }
 function sync(){
   scheduled=false;
   const id=active(),permitted=ids.filter(allowed);
   const list=permitted.map(id=>[id,title(id)]),signature=JSON.stringify(list);
   if(signature!==lastOptions){lastOptions=signature;switcher.replaceChildren();for(const [key,name] of list){const o=el("option","",name);o.value=key;switcher.append(o)}}
   if(id)switcher.value=id;
   switcher.setAttribute("aria-label",aw()[1]);refreshText.textContent=aw()[2];helper.textContent=aw()[7];
   rail.classList.toggle("zAdminRail",!!id);extra.classList.toggle("zAdminArea",!!id&&!extra.hidden);
   if(id==="founderAdmin"&&!extra.hidden){
     decorateFounder();
     sections=Array.from(extra.querySelectorAll("h2,h3")).filter(n=>n.closest("article")===extra&&!n.closest("[hidden]")&&n.textContent.trim());
   }else sections=[];
   const sectionKey=JSON.stringify([locale(),sections.map(n=>n.textContent.trim())]);
   if(sectionKey!==lastSections){lastSections=sectionKey;jump.replaceChildren();const initial=el("option","",aw()[8]);initial.value="";jump.append(initial);sections.forEach((n,i)=>{const o=el("option","",n.textContent.trim());o.value=String(i);jump.append(o)})}
   tocTitle.textContent=aw()[4];jump.setAttribute("aria-label",aw()[3]);toc.hidden=sections.length<2;
 }
 const schedule=()=>{if(!scheduled){scheduled=true;queueMicrotask(sync)}};
 const obs=new MutationObserver(schedule);
 obs.observe(owner,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:["hidden","disabled","aria-current"]});obs.observe(panel,{attributes:true,attributeFilter:["hidden"]});
 obs.observe(extra,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:["hidden"]});
 adminRefresh=schedule;schedule();
}
const compactWords={en:["Open section","Collapse section","Show creator labs","Hide creator labs"],ru:["Открыть раздел","Свернуть раздел","Показать лаборатории","Скрыть лаборатории"],uk:["Відкрити розділ","Згорнути розділ","Показати лабораторії","Приховати лабораторії"],pl:["Otwórz sekcję","Zwiń sekcję","Pokaż laboratoria","Ukryj laboratoria"]};
let compactRefresh=null;
const compactHubs=new Map();
let labsToggle=null;
function expandOverviewHub(selector){compactHubs.get(selector)?.(true)}
function revealCreatorLabs(){labsToggle?.(true)}
function compactOverview(){
 const overview=$("workspaceOverview"),journey=$("creatorJourney");if(!overview||!journey)return;
 const words=()=>compactWords[locale()]||compactWords.en,relabellers=[];
 for(const [selector,name] of [[".zProductionHub","production"],[".zBusinessHub","business"],[".zSocialHub","social"],["#zAcademyTools","tools"]]){
   const hub=overview.querySelector(":scope > "+selector),heading=hub?.querySelector(":scope > h2");if(!hub||!heading)continue;
   // Native button toggles only generated presentation; no original access flags or form nodes change.
   const b=el("button","zCompactToggle"),text=el("span");b.type="button";b.append(text,icon("chevron-down"));
   heading.classList.add("zCompactHeading");heading.append(b);hub.classList.add("zCompactHub");
   const target=Array.from(hub.children).filter(n=>n!==heading);
   const body=el("div","zCompactBody");body.id="zCompact-"+name;hub.append(body);body.append(...target);
   b.setAttribute("aria-controls",body.id);
   let open=false;
   const sync=()=>{b.setAttribute("aria-expanded",String(open));body.hidden=!open;text.textContent=words()[open?1:0]};
   const set=value=>{open=value;sync()};compactHubs.set(selector,set);b.onclick=()=>set(!open);relabellers.push(sync);sync();
 }
 const prod=overview.querySelector(".zProductionHub .zCompactBody");
 if(prod){
   const b=el("button","zAction zLabVisibility");b.type="button";b.setAttribute("aria-controls","creatorJourney");prod.append(b);let open=false;
   const sync=()=>{journey.classList.toggle("zLabsCollapsed",!open);b.setAttribute("aria-expanded",String(open));b.textContent=words()[open?3:2]};
   labsToggle=v=>{open=v;sync()};b.onclick=()=>labsToggle(!open);relabellers.push(sync);sync();
 }
 compactRefresh=()=>{for(const fn of relabellers)fn()};
 if(new URLSearchParams(location.search).has("lab")){expandOverviewHub(".zProductionHub");revealCreatorLabs()}
}
const onboardingWords={
 en:["Your next step","Start your free lesson","Choose a learning package","Continue learning","Review your learning plan","All available course days completed","No learning data yet","Loading your progress…","Lesson progress","Day","Explore tools","My portfolio","Find projects","Get help","Access is determined by your account. Tools and projects may have separate requirements."],
 ru:["Твой следующий шаг","Начать бесплатный урок","Выбрать пакет обучения","Продолжить обучение","Посмотреть план обучения","Все дни курса в твоём плане пройдены","Данные обучения ещё не загружены","Загружаем твой прогресс…","Прогресс обучения","День","AI-инструменты","Моё портфолио","Найти проекты","Получить помощь","Доступ определяется аккаунтом. Для инструментов и проектов могут действовать отдельные условия."],
 uk:["Твій наступний крок","Почати безкоштовний урок","Обрати пакет навчання","Продовжити навчання","Переглянути план навчання","Усі дні курсу у твоєму плані пройдено","Дані навчання ще не завантажено","Завантажуємо твій прогрес…","Прогрес навчання","День","AI-інструменти","Моє портфоліо","Знайти проєкти","Отримати допомогу","Доступ визначається акаунтом. Для інструментів і проєктів можуть діяти окремі умови."],
 pl:["Twój następny krok","Rozpocznij bezpłatną lekcję","Wybierz pakiet nauki","Kontynuuj naukę","Zobacz plan nauki","Wszystkie dni kursu w Twoim planie ukończone","Dane nauki nie zostały jeszcze wczytane","Wczytujemy postęp…","Postęp nauki","Dzień","Narzędzia AI","Moje portfolio","Znajdź projekty","Uzyskaj pomoc","Dostęp zależy od konta. Narzędzia i projekty mogą mieć odrębne wymagania."]};
let onboardingRefresh=null;
function onboardingDesign(){
 const overview=$("workspaceOverview"),days=$("days"),checkout=$("checkout"),panel=$("panel"),nav=$("academyNav");if(!overview||!days||!checkout||!panel||!nav)return;
 const words=()=>onboardingWords[locale()]||onboardingWords.en;
 const hub=el("section","zOnboarding");hub.id="zOnboarding";hub.hidden=true;
 const head=el("h2"),status=el("p","zOnboardingStatus"),meter=el("progress"),primary=el("button","zAction primary"),actions=el("div","zOnboardingActions"),notice=el("p","zOnboardingNotice");
 primary.type="button";status.setAttribute("role","status");hub.append(head,status,meter,primary,actions,notice);
 const shortcuts=[];
 const visible=id=>{const n=$(id);return !!n&&!n.disabled&&!n.closest("[hidden]")};
 for(const [id,label,glyph,path] of [[null,10,"wand-sparkles","/ai-workspace"],["portfolioButton",11,"image",null],["jobsButton",12,"briefcase",null],[null,13,"headphones","/support"]]){
   const b=el(path?"a":"button","zOnboardingShortcut"),txt=el("span");b.append(icon(glyph),txt);
   if(path){b.href=url(path);links.push([b,path])}else{b.type="button";b.onclick=()=>{if(visible(id))$(id).click()}}
   shortcuts.push({b,txt,id,label});actions.append(b);
 }
 const profile=$("zProfileCard");if(profile)profile.after(hub);else overview.prepend(hub);
 const write=(n,v)=>{if(n.textContent!==v)n.textContent=v};
 const hide=(n,v)=>{if(n.hidden!==v)n.hidden=v};
 let scheduled=false;
 function sync(){
   scheduled=false;hide(hub,panel.hidden);if(panel.hidden)return;
   const w=words(),list=Array.from(days.querySelectorAll("button[data-day]")),done=list.filter(b=>b.dataset.state==="completed").length,open=list.find(b=>b.dataset.state==="open"&&!b.disabled),first=list.find(b=>b.dataset.day==="1");
   const hasCheckout=!checkout.hidden;
   write(head,w[0]);write(notice,w[14]);meter.max=Math.max(1,list.length);meter.value=done;meter.setAttribute("aria-label",w[8]);hide(meter,!list.length);
   primary.disabled=false;
   if(!list.length){write(status,w[7]);write(primary,w[6]);primary.disabled=true;primary.onclick=null}
   else{
     let label=4,action=()=>days.scrollIntoView({block:"start",behavior:"auto"}),detail=done+" / "+list.length+" · "+w[8];
     if(open&&first===open&&hasCheckout){label=1;action=()=>{if(open.isConnected&&!open.disabled)open.click()};detail+=" · "+w[9]+" 1"}
     else if(hasCheckout&&!open){label=2;action=()=>{if(!checkout.hidden)checkout.scrollIntoView({block:"start",behavior:"auto"})}}
     else if(open){label=3;action=()=>{if(open.isConnected&&!open.disabled)open.click()};detail+=" · "+w[9]+" "+open.dataset.day}
     else if(done===list.length){label=4;detail=w[5]+" · "+detail}
     write(status,detail);write(primary,w[label]);primary.onclick=action;
   }
   for(const {b,txt,id,label} of shortcuts){write(txt,w[label]);hide(b,!!id&&!visible(id))}
 }
 const schedule=()=>{if(!scheduled){scheduled=true;queueMicrotask(sync)}};
 const observer=new MutationObserver(schedule);
 observer.observe(days,{subtree:true,childList:true,attributes:true,attributeFilter:["disabled","data-state"]});
 observer.observe(checkout,{attributes:true,attributeFilter:["hidden"]});
 observer.observe(panel,{attributes:true,attributeFilter:["hidden"]});
 observer.observe(nav,{subtree:true,attributes:true,attributeFilter:["hidden","disabled"]});
 onboardingRefresh=schedule;schedule();
}
const teacherCenterWords={
 en:["Personal Teacher","Your daily study session","Session length","minutes","Build my session","Preparing your session…","Could not load your study session. Try again.","No available lesson yet.","Day","Latest quiz score","Not attempted","Foundation","Reinforce","Challenge","Review","Learn","Practice","Reflect","Suggested exercise","Open lesson","Practice brief","Rules-based recommendations from quiz summaries, not a diagnosis of individual mistakes or an official grade.","Review due","Private session · no external AI request"],
 ru:["Personal Teacher","Твоя учебная сессия","Продолжительность","мин","Составить занятие","Подбираем занятие…","Не удалось загрузить занятие. Попробуй ещё раз.","Пока нет доступного урока.","День","Последний балл экзамена","Нет попыток","Основы","Закрепление","Продвинутый уровень","Повторение","Обучение","Практика","Рефлексия","Рекомендуемое упражнение","Открыть урок","Практический бриф","Рекомендации на основе итоговых баллов, а не диагностика конкретных ошибок или официальная оценка.","Пора повторить","Приватная сессия · без внешнего AI-запроса"],
 uk:["Personal Teacher","Твоя навчальна сесія","Тривалість","хв","Скласти заняття","Підбираємо заняття…","Не вдалося завантажити заняття. Спробуй ще раз.","Поки немає доступного уроку.","День","Останній бал іспиту","Немає спроб","Основи","Закріплення","Просунутий рівень","Повторення","Навчання","Практика","Рефлексія","Рекомендована вправа","Відкрити урок","Практичний бриф","Рекомендації на основі підсумкових балів, а не діагностика окремих помилок чи офіційна оцінка.","Час повторити","Приватна сесія · без зовнішнього ШІ-запиту"],
 pl:["Personal Teacher","Twoja sesja nauki","Czas trwania","min","Ułóż sesję","Przygotowujemy sesję…","Nie udało się wczytać sesji. Spróbuj ponownie.","Brak dostępnej lekcji.","Dzień","Ostatni wynik egzaminu","Brak prób","Podstawy","Utrwalenie","Poziom zaawansowany","Powtórka","Nauka","Praktyka","Refleksja","Zalecane ćwiczenie","Otwórz lekcję","Brief praktyczny","Zalecenia oparte na wynikach, nie diagnoza poszczególnych błędów ani oficjalna ocena.","Czas na powtórkę","Prywatna sesja · bez zewnętrznego zapytania AI"]};
let teacherCenterRefresh=null;
function teacherCenterDesign(){
 const overview=$("workspaceOverview"),panel=$("panel"),days=$("days");if(!overview||!panel||!days)return;
 const w=()=>teacherCenterWords[locale()]||teacherCenterWords.en;
 const hub=el("section","zTeacherCenter"),head=el("h2"),caption=el("p"),controls=el("div","zTeacherControls"),duration=el("select"),generate=el("button","zAction primary"),status=el("p"),result=el("div","zTeacherResult"),notice=el("p","zTeacherNotice");
 hub.id="zTeacherCenter";generate.type="button";status.setAttribute("role","status");status.setAttribute("aria-live","polite");
 for(const n of [15,30,60]){const option=el("option");option.value=String(n);duration.append(option)}duration.value="30";
 controls.append(duration,generate);hub.append(head,caption,controls,status,result,notice);
 const onboarding=$("zOnboarding");if(onboarding)onboarding.after(hub);else overview.prepend(hub);
 let requestId=0,lastLanguage=locale(),last=null;
 const reset=()=>{requestId++;last=null;result.replaceChildren();status.textContent="";generate.disabled=false};
 const accessible=day=>Array.from(days.querySelectorAll("button[data-day]")).find(n=>Number(n.dataset.day)===day&&!n.disabled);
 const render=d=>{
   result.replaceChildren();if(!d?.focus){status.textContent=w()[7];return}
   const f=d.focus,level={foundation:11,reinforce:12,challenge:13}[f.level],heading=el("h3","",w()[8]+" "+f.day+" · "+w()[level]),score=el("p","",w()[9]+": "+(f.latest===null?w()[10]:String(f.latest)+"/100")+(f.due?" · "+w()[22]:""));
   result.append(heading,score);
   const list=el("div","zTeacherTimeline");
   for(const item of d.items||[]){const i={review:14,learn:15,practice:16,reflect:17}[item.kind];if(i===undefined)continue;const row=el("div","zTeacherTimeBlock");row.append(el("strong","",w()[i]),el("span","",String(item.minutes)+" "+w()[3]));list.append(row)}
   result.append(list);
   if(d.practice_focus?.task)result.append(el("h4","",w()[18]),el("p","",d.practice_focus.task));
   if(d.brief?.deliverable){result.append(el("h4","",w()[20]),el("p","",d.brief.deliverable))}
   const actions=el("div","zTeacherActions"),open=el("button","zAction",w()[19]),practice=el("button","zAction",w()[20]);
   open.type=practice.type="button";open.disabled=practice.disabled=!accessible(f.day);
   open.onclick=()=>{if(!panel.hidden)accessible(f.day)?.click()};
   practice.onclick=()=>{if(!panel.hidden&&accessible(f.day)&&typeof openPractice==="function")openPractice(f.day)};
   actions.append(open,practice);result.append(actions);status.textContent=w()[23];
 };
 generate.onclick=async()=>{
   if(panel.hidden||typeof api!=="function")return;
   const id=++requestId,language=locale();generate.disabled=true;result.replaceChildren();last=null;status.textContent=w()[5];
   try{
     const data=await api("/teacher/plan",{minutes:Number(duration.value),lang:language});
     if(id!==requestId||panel.hidden||locale()!==language||!hub.isConnected)return;
     last=data;render(data);
   }catch(error){if(id===requestId&&!panel.hidden)status.textContent=w()[6]}
   finally{if(id===requestId)generate.disabled=false}
 };
 duration.onchange=reset;
 function sync(){
   if(locale()!==lastLanguage){lastLanguage=locale();reset()}
   head.textContent=w()[0];caption.textContent=w()[1];generate.textContent=w()[4];notice.textContent=w()[21];duration.setAttribute("aria-label",w()[2]);
   for(const option of duration.options)option.textContent=option.value+" "+w()[3];
 }
 new MutationObserver(()=>{if(panel.hidden)reset()}).observe(panel,{attributes:true,attributeFilter:["hidden"]});
 // Invalidate recommendations when original lesson controls are replaced or permissions change.
 new MutationObserver(()=>{if(last?.focus&&!accessible(last.focus.day))reset()}).observe(days,{childList:true,subtree:true,attributes:true,attributeFilter:["disabled","data-state"]});
 teacherCenterRefresh=sync;sync();
}
const mentorWords={
 en:["Project Mentor","Prepare evidence for a real project or a course assignment.","Choose an available lesson","Day","Goal and audience","Result and evidence","Tools and workflow","Tests and limitations","Rights and consent","Revisions and next steps","Check evidence","Reviewing…","Evidence provided","Send to portfolio for manual review","Submitted","Check failed. Try again.","No available lessons.","All six fields must be completed. This checks presence, not quality or authenticity.","Submission may have been received. Check your portfolio before retrying.","Send this draft for review?","Use your own files and do not include client secrets.","Open portfolio","Draft changed. Check again before sending."],
 ru:["Project Mentor","Подготовь материалы реального проекта или учебного задания.","Выбери доступный урок","День","Цель и аудитория","Результат и доказательства","Инструменты и процесс","Тесты и ограничения","Права и согласие","Правки и следующие шаги","Проверить материалы","Проверяем…","Заполнено разделов","Отправить в портфолио на ручную проверку","Отправлено","Проверка не удалась. Попробуй снова.","Нет доступных уроков.","Заполни все шесть разделов. Проверяется наличие материалов, а не их качество или подлинность.","Заявка могла быть получена. Проверь портфолио перед повторной отправкой.","Отправить этот черновик на проверку?","Используй собственные файлы, не добавляй секреты клиентов.","Открыть портфолио","Черновик изменён. Проверь его повторно."],
 uk:["Project Mentor","Підготуй матеріали реального проєкту або навчального завдання.","Обери доступний урок","День","Мета й аудиторія","Результат і докази","Інструменти й процес","Тести й обмеження","Права та згода","Правки й наступні кроки","Перевірити матеріали","Перевіряємо…","Заповнено розділів","Надіслати до портфоліо на ручну перевірку","Надіслано","Перевірка не вдалася. Спробуй ще раз.","Немає доступних уроків.","Заповни всі шість розділів. Перевіряється наявність, а не якість чи справжність.","Заявку могли отримати. Перевір портфоліо перед повтором.","Надіслати чернетку на перевірку?","Використовуй власні файли й не додавай секрети клієнтів.","Відкрити портфоліо","Чернетку змінено. Перевір її повторно."],
 pl:["Project Mentor","Przygotuj materiały projektu lub zadania szkoleniowego.","Wybierz dostępną lekcję","Dzień","Cel i odbiorcy","Rezultat i dowody","Narzędzia i proces","Testy i ograniczenia","Prawa i zgoda","Poprawki i kolejne kroki","Sprawdź materiały","Sprawdzamy…","Uzupełnione sekcje","Wyślij do portfolio do ręcznej oceny","Przesłano","Nie udało się sprawdzić. Spróbuj ponownie.","Brak dostępnych lekcji.","Uzupełnij sześć sekcji. Sprawdzana jest obecność, nie jakość ani autentyczność.","Zgłoszenie mogło zostać przyjęte. Sprawdź portfolio przed ponowieniem.","Wysłać szkic do oceny?","Używaj własnych plików i nie podawaj sekretów klientów.","Otwórz portfolio","Szkic zmieniony. Sprawdź ponownie."]};
let mentorRefresh=null;
function projectMentorDesign(){
 const overview=$("workspaceOverview"),panel=$("panel"),days=$("days");if(!overview||!panel||!days)return;
 const w=()=>mentorWords[locale()]||mentorWords.en;
 const hub=el("details","zProjectMentor"),summary=el("summary"),title=el("span"),intro=el("p"),day=el("select"),fieldGrid=el("div","zMentorFields"),status=el("p"),out=el("div","zMentorChecks"),check=el("button","zAction primary"),send=el("button","zAction"),portfolio=el("button","zAction"),note=el("p");
 hub.id="zProjectMentor";summary.append(icon("briefcase"),title);hub.append(summary,intro,day,fieldGrid,note,check,status,out,send,portfolio);
 check.type=send.type=portfolio.type="button";send.disabled=true;status.setAttribute("role","status");
 const keys=["goal","deliverable","process","verification","rights","revision"],fields={};
 for(const key of keys){const label=el("label"),span=el("span"),input=el("textarea");input.rows=3;input.maxLength=1200;label.append(span,input);fieldGrid.append(label);fields[key]={span,input}}
 const anchor=$("zTeacherCenter")||$("zOnboarding");if(anchor)anchor.after(hub);else overview.append(hub);
 let revision=0,approved=null,busy=false,submitting=false,signature="";
 function invalidate(clear=false){revision++;approved=null;send.disabled=true;out.replaceChildren();status.textContent=clear?"":w()[22];if(!submitting){busy=false;check.disabled=!day.value}if(clear)for(const f of Object.values(fields))f.input.value=""}
 const accessible=n=>Array.from(days.querySelectorAll("button[data-day]")).some(b=>Number(b.dataset.day)===n&&!b.disabled);
 function refresh(){
   const available=Array.from(days.querySelectorAll("button[data-day]")).filter(b=>!b.disabled).map(b=>b.dataset.day),next=JSON.stringify([locale(),available]);if(next!==signature){signature=next;const old=day.value;day.replaceChildren();for(const n of available){const option=el("option","",w()[3]+" "+n);option.value=n;day.append(option)}if(available.includes(old))day.value=old;invalidate(false);status.textContent=available.length?"":w()[16]}
   title.textContent=w()[0];intro.textContent=w()[1];day.setAttribute("aria-label",w()[2]);keys.forEach((k,i)=>fields[k].span.textContent=w()[4+i]);check.textContent=w()[10];send.textContent=w()[13];portfolio.textContent=w()[21];note.textContent=w()[17]+" "+w()[20];check.disabled=busy||submitting||!day.value;send.disabled=submitting||!approved||!accessible(Number(day.value));portfolio.hidden=!!$("portfolioButton")?.hidden;
 }
 day.onchange=()=>invalidate();for(const f of Object.values(fields))f.input.oninput=()=>invalidate();
 check.onclick=async()=>{
   if(busy||submitting||panel.hidden||!accessible(Number(day.value))||typeof api!=="function")return;
   const id=++revision,lesson=Number(day.value),lang=locale(),payload=Object.fromEntries(keys.map(k=>[k,fields[k].input.value]));
   approved=null;busy=true;check.disabled=true;send.disabled=true;out.replaceChildren();status.textContent=w()[11];
   try{
     if(new TextEncoder().encode(JSON.stringify({day:lesson,fields:payload,lang})).length>15500)throw Error("Draft too large");
     const d=await api("/portfolio/draft-review",{day:lesson,fields:payload,lang});
     if(id!==revision||panel.hidden||lang!==locale()||!accessible(lesson))return;
     status.textContent=w()[12]+": "+d.provided_count+" / "+d.total;
     for(const item of d.checks||[]){const row=el("div","zMentorCheck");row.append(el("strong","",(item.provided?"✓ ":"○ ")+item.label),el("p","",item.suggestion));out.append(row)}
     if(d.ready_for_submission===true&&typeof d.case_study==="string")approved={lesson,caseStudy:d.case_study};
   }catch(e){if(id===revision&&!panel.hidden)status.textContent=w()[15]}
   finally{if(id===revision){busy=false;refresh()}}
 };
 send.onclick=async()=>{
   if(!approved||busy||submitting||panel.hidden||!accessible(approved.lesson)||!confirm(w()[19]))return;
   const data=approved,id=++revision;approved=null;submitting=true;refresh();
   for(const f of Object.values(fields))f.input.disabled=true;day.disabled=true;
   try{const result=await api("/portfolio",{day:data.lesson,submission:data.caseStudy});if(id===revision&&!panel.hidden)status.textContent=w()[14]+" #"+result.id}
   catch(e){if(id===revision&&!panel.hidden)status.textContent=w()[18]}
   finally{submitting=false;for(const f of Object.values(fields))f.input.disabled=false;day.disabled=false;refresh()}
 };
 portfolio.onclick=()=>{const b=$("portfolioButton");if(b&&!b.disabled&&!b.hidden&&!panel.hidden)b.click()};
 new MutationObserver(refresh).observe(days,{childList:true,subtree:true,attributes:true,attributeFilter:["disabled","data-state"]});
 new MutationObserver(()=>{if(panel.hidden){invalidate(true);hub.open=false}else refresh()}).observe(panel,{attributes:true,attributeFilter:["hidden"]});
 mentorRefresh=refresh;refresh();
}
const careerCenterWords={
 en:["Career Center","Prepare for real client work. Progress is based on your own Academy records.","Refresh career roadmap","Loading…","Could not load. Try again.","Profile","Portfolio (3 projects)","Approved service listing","First client","First delivered project","Next step","Open career profile","Open portfolio","My service listing","Find jobs","Business & proposals","Project estimate · USD","Estimated hours","Hourly rate · USD","Direct expenses · USD","Contingency %","Calculate","Labor","Expenses","Contingency","Suggested project quote","Estimates exclude taxes, marketplace fees and actual payment costs. No promise of clients or earnings.","All roadmap steps recorded","Invalid estimate or unavailable service.","Stages completed","Academy progress is not a verified professional qualification."],
 ru:["Career Center","Подготовка к реальным заказам. Прогресс основан на твоих записях в академии.","Обновить карьерный маршрут","Загрузка…","Не удалось загрузить. Попробуй снова.","Профиль","Портфолио (3 проекта)","Одобренная услуга на бирже","Первый клиент","Первый завершённый заказ","Следующий шаг","Карьерный профиль","Открыть портфолио","Моя услуга на бирже","Найти заказы","Бизнес и предложения","Расчёт проекта · USD","Количество часов","Ставка за час · USD","Прямые расходы · USD","Резерв %","Рассчитать","Работа","Расходы","Резерв","Предлагаемая стоимость проекта","Расчёт не включает налоги, комиссии биржи и реальные платёжные расходы. Заказы и доход не гарантированы.","Все этапы маршрута зафиксированы","Некорректный расчёт или сервис недоступен.","Этапов завершено","Прогресс академии не подтверждает профессиональную квалификацию."],
 uk:["Career Center","Підготовка до реальних замовлень. Прогрес ґрунтується на твоїх записах в академії.","Оновити кар'єрний маршрут","Завантаження…","Не вдалося завантажити. Спробуй знову.","Профіль","Портфоліо (3 проєкти)","Схвалена послуга на біржі","Перший клієнт","Перше завершене замовлення","Наступний крок","Кар'єрний профіль","Відкрити портфоліо","Моя послуга на біржі","Знайти замовлення","Бізнес і пропозиції","Розрахунок проєкту · USD","Кількість годин","Ставка за годину · USD","Прямі витрати · USD","Резерв %","Розрахувати","Робота","Витрати","Резерв","Запропонована вартість проєкту","Розрахунок не враховує податки, комісії біржі й платіжні витрати. Замовлення та доходи не гарантовано.","Усі етапи маршруту зафіксовані","Некоректний розрахунок або сервіс недоступний.","Етапів завершено","Прогрес академії не підтверджує професійну кваліфікацію."],
 pl:["Career Center","Przygotuj się do pracy z klientami. Postęp opiera się na Twoich danych w akademii.","Odśwież ścieżkę kariery","Wczytywanie…","Nie udało się wczytać. Spróbuj ponownie.","Profil","Portfolio (3 projekty)","Zatwierdzona usługa na giełdzie","Pierwszy klient","Pierwsze zrealizowane zlecenie","Następny krok","Profil kariery","Otwórz portfolio","Moja usługa na giełdzie","Znajdź zlecenia","Biznes i oferty","Wycena projektu · USD","Liczba godzin","Stawka godzinowa · USD","Koszty bezpośrednie · USD","Rezerwa %","Oblicz","Praca","Koszty","Rezerwa","Proponowana cena projektu","Wycena nie obejmuje podatków, prowizji giełdy i opłat płatniczych. Brak gwarancji klientów lub zarobków.","Wszystkie etapy zapisane","Nieprawidłowa wycena lub usługa niedostępna.","Ukończone etapy","Postęp akademii nie potwierdza kwalifikacji zawodowych."]};
let careerCenterRefresh=null;
function careerCenterDesign(){
 const overview=$("workspaceOverview"),panel=$("panel"),nav=$("academyNav"),career=$("careerButton");if(!overview||!panel||!nav||!career)return;
 const w=()=>careerCenterWords[locale()]||careerCenterWords.en;
 const hub=el("details","zCareerCenter"),summary=el("summary"),title=el("span"),intro=el("p"),load=el("button","zAction primary"),status=el("p"),road=el("div","zCareerRoad"),linksBox=el("div","zCareerLinks"),head=el("h3"),form=el("form","zCareerEstimate"),fields=el("div","zCareerInputs"),calc=el("button","zAction"),result=el("div","zCareerResult"),note=el("p","zCareerNote");
 hub.id="zCareerCenter";summary.append(icon("briefcase"),title);hub.append(summary,intro,load,status,road,linksBox,head,form,note);form.append(fields,calc,result);load.type="button";calc.type="submit";status.setAttribute("role","status");result.setAttribute("aria-live","polite");
 const anchor=$("zProjectMentor")||$("zTeacherCenter");if(anchor)anchor.after(hub);else overview.append(hub);
 const allowed=id=>{const b=$(id);return !panel.hidden&&!!b&&!b.disabled&&!b.closest("[hidden]")};
 const navs=[["careerButton",11,"graduation"],["portfolioButton",12,"image"],["marketplaceButton",13,"briefcase"],["jobsButton",14,"search"],["businessButton",15,"chart"]],buttons=[];
 for(const [id,i,glyph] of navs){const b=el("button","zAction"),txt=el("span");b.type="button";b.append(icon(glyph),txt);b.onclick=()=>{if(allowed(id))$(id).click()};linksBox.append(b);buttons.push({id,i,b,txt})}
 const inputs={};
 for(const [key,i,max,initial] of [["hours",17,1000,"10"],["rate",18,10000,"25"],["expenses",19,100000,"20"],["buffer",20,100,"10"]]){
   const label=el("label"),txt=el("span"),input=el("input");input.type="number";input.min="0";input.max=String(max);input.step="0.01";input.required=true;input.value=initial;label.append(txt,input);fields.append(label);inputs[key]={input,txt,i};
 }
 let roadId=0,quoteId=0,lastLang=locale(),lastAllowed=false,roadData=null,quoteData=null;
 const stages={profile:[5,"careerButton"],portfolio:[6,"portfolioButton"],listing:[7,"marketplaceButton"],clients:[8,"businessButton"],delivery:[9,"businessButton"]};
 const reset=()=>{roadId++;quoteId++;roadData=quoteData=null;road.replaceChildren();result.replaceChildren();status.textContent="";load.disabled=calc.disabled=false};
 const renderRoad=d=>{
   road.replaceChildren();const valid=Array.isArray(d?.stages)?d.stages.filter(s=>Object.hasOwn(stages,s.id)):[];
   if(!valid.length)return;const meter=el("progress");meter.max=valid.length;meter.value=valid.filter(s=>s.done===true).length;meter.setAttribute("aria-label",w()[29]);road.append(el("strong","",w()[29]+": "+meter.value+" / "+meter.max),meter);
   for(const stage of valid){const [i,id]=stages[stage.id],row=el("div","zCareerStage"),label=el("span","",(stage.done?"✓ ":"○ ")+w()[i]),count=el("strong","",String(stage.value)+" / "+String(stage.target));row.append(label,count);road.append(row)}
   const next=stages[d.next];if(next){const b=el("button","zAction",w()[10]+": "+w()[next[0]]);b.type="button";b.disabled=!allowed(next[1]);b.onclick=()=>{if(allowed(next[1]))$(next[1]).click()};road.append(b)}else if(d.next===null)road.append(el("p","",w()[27]));
 };
 const renderQuote=d=>{result.replaceChildren();for(const [key,i] of [["labor",22],["expenses",23],["contingency",24],["total",25]]){const row=el("div","zCareerStage"+(key==="total"?" zCareerTotal":""));row.append(el("span","",w()[i]),el("strong","","$"+String(d[key])));result.append(row)}};
 load.onclick=async()=>{
   if(!allowed("careerButton")||typeof api!=="function")return;const id=++roadId;load.disabled=true;status.textContent=w()[3];road.replaceChildren();roadData=null;
   try{const d=await api("/career/accelerator");if(id!==roadId||!allowed("careerButton"))return;roadData=d;renderRoad(d);status.textContent=""}
   catch(e){if(id===roadId&&allowed("careerButton"))status.textContent=w()[4]}
   finally{if(id===roadId)load.disabled=false}
 };
 form.onsubmit=async e=>{
   e.preventDefault();if(!allowed("careerButton")||typeof api!=="function"||!form.reportValidity())return;const id=++quoteId;calc.disabled=true;quoteData=null;result.textContent=w()[3];
   try{const body=Object.fromEntries(Object.entries(inputs).map(([k,f])=>[k,f.input.value]));const d=await api("/career/estimate",body);if(id!==quoteId||!allowed("careerButton"))return;quoteData=d;renderQuote(d)}
   catch(e){if(id===quoteId&&allowed("careerButton"))result.textContent=w()[28]}
   finally{if(id===quoteId)calc.disabled=false}
 };
 for(const f of Object.values(inputs))f.input.oninput=()=>{quoteId++;quoteData=null;result.replaceChildren();calc.disabled=false};
 let pending=false;
 function sync(){
   pending=false;const access=allowed("careerButton");if(!access&&lastAllowed){reset();hub.open=false;for(const [k,f] of Object.entries(inputs))f.input.value={hours:"10",rate:"25",expenses:"20",buffer:"10"}[k]}lastAllowed=access;
   if(hub.hidden===access)hub.hidden=!access;
   if(lastLang!==locale()){lastLang=locale();roadId++;quoteId++;load.disabled=calc.disabled=false;status.textContent="";if(roadData)renderRoad(roadData);else road.replaceChildren();if(quoteData)renderQuote(quoteData);else result.replaceChildren()}
   title.textContent=w()[0];intro.textContent=w()[1];load.textContent=w()[2];head.textContent=w()[16];calc.textContent=w()[21];note.textContent=w()[26]+" "+w()[30];
   for(const {id,i,b,txt} of buttons){if(txt.textContent!==w()[i])txt.textContent=w()[i];const hidden=!allowed(id);if(b.hidden!==hidden)b.hidden=hidden}
   for(const f of Object.values(inputs))f.txt.textContent=w()[f.i];
 }
 const schedule=()=>{if(!pending){pending=true;queueMicrotask(sync)}};
 new MutationObserver(schedule).observe(nav,{subtree:true,attributes:true,attributeFilter:["hidden","disabled"]});
 new MutationObserver(schedule).observe(panel,{attributes:true,attributeFilter:["hidden"]});
 careerCenterRefresh=schedule;sync();
}
const businessStudioWords={
 en:["Creator Business Studio","Your private CRM dashboard","Refresh records","Loading…","Could not load. Try again.","Clients","Orders","Recorded contract value","Received","Expenses","Outstanding","Cash difference","Leads","In progress","Delivered","Cancelled","Priority actions","Overdue","Cost overrun","Due soon","Collect payment","Set deadline","Follow up","Open CRM & PDF proposals","Find jobs","No priority actions","Manual USD records, not bank balances, verified payments or net profit. Taxes and fees are not calculated.","As of","Showing first 12 priority actions"],
 ru:["Creator Business Studio","Личная панель управления клиентами","Обновить данные","Загрузка…","Не удалось загрузить. Попробуй снова.","Клиенты","Заказы","Учтённая стоимость заказов","Получено","Расходы","Остаток к оплате","Разница поступлений и расходов","Потенциальные заказы","В работе","Выполнено","Отменено","Приоритетные задачи","Просрочено","Превышение расходов","Срок приближается","Проверить получение оплаты","Установить срок","Связаться с клиентом","CRM и PDF-предложения","Найти заказы","Нет приоритетных задач","Ручной учёт в USD, не баланс кошелька, подтверждение оплаты или чистая прибыль. Налоги и комиссии не рассчитаны.","Данные на","Первые 12 приоритетных задач"],
 uk:["Creator Business Studio","Приватна панель керування клієнтами","Оновити дані","Завантаження…","Не вдалося завантажити. Спробуй знову.","Клієнти","Замовлення","Врахована вартість замовлень","Отримано","Витрати","Залишок до оплати","Різниця надходжень і витрат","Потенційні замовлення","У роботі","Виконано","Скасовано","Пріоритетні завдання","Прострочено","Перевищення витрат","Термін наближається","Перевірити отримання оплати","Встановити термін","Зв'язатися з клієнтом","CRM і PDF-пропозиції","Знайти замовлення","Немає пріоритетних завдань","Ручний облік у USD, не баланс гаманця, підтвердження оплати або чистий прибуток. Податки й комісії не розраховано.","Дані на","Перші 12 пріоритетних завдань"],
 pl:["Creator Business Studio","Prywatny panel CRM","Odśwież dane","Wczytywanie…","Nie udało się wczytać. Spróbuj ponownie.","Klienci","Zlecenia","Zapisana wartość zleceń","Otrzymano","Koszty","Pozostało do zapłaty","Różnica wpływów i kosztów","Potencjalne zlecenia","W realizacji","Dostarczono","Anulowano","Pilne zadania","Po terminie","Przekroczenie kosztów","Zbliża się termin","Sprawdź płatność","Ustal termin","Skontaktuj się z klientem","CRM i oferty PDF","Znajdź zlecenia","Brak pilnych zadań","Ręczny zapis w USD, nie saldo portfela, potwierdzenie płatności ani zysk netto. Podatki i prowizje nie zostały obliczone.","Stan na","Pierwsze 12 pilnych zadań"]};
let businessStudioRefresh=null;
function businessStudioDesign(){
 const overview=$("workspaceOverview"),panel=$("panel"),nav=$("academyNav"),button=$("businessButton");if(!overview||!panel||!nav||!button)return;
 const w=()=>businessStudioWords[locale()]||businessStudioWords.en;
 const hub=el("details","zBusinessStudio"),summary=el("summary"),title=el("span"),intro=el("p"),load=el("button","zAction primary"),status=el("p"),report=el("div","zBusinessReport"),actions=el("div","zBusinessStudioLinks"),crm=el("button","zAction"),jobs=el("button","zAction"),note=el("p","zBusinessStudioNote");
 hub.id="zBusinessStudio";summary.append(icon("chart"),title);hub.append(summary,intro,load,status,report,actions,note);actions.append(crm,jobs);load.type=crm.type=jobs.type="button";status.setAttribute("role","status");
 const anchor=$("zCareerCenter");if(anchor)anchor.after(hub);else overview.append(hub);
 const allowed=id=>{const b=$(id);return !panel.hidden&&!!b&&!b.disabled&&!b.closest("[hidden]")};
 crm.onclick=()=>{if(allowed("businessButton"))button.click()};jobs.onclick=()=>{if(allowed("jobsButton"))$("jobsButton").click()};
 const money=c=>{try{const n=BigInt(c),a=n<0n?-n:n;return (n<0n?"-":"")+"$"+(a/100n).toString()+"."+(a%100n).toString().padStart(2,"0")}catch(e){return "—"}};
 let seq=0,data=null,lang=locale(),hadAccess=false;
 function clear(){seq++;data=null;report.replaceChildren();status.textContent="";load.disabled=false}
 function render(d){
   report.replaceChildren();const grid=el("div","zStudioMetrics");
   const values=[[5,d.clients],[6,d.orders],[7,money(d.totals.agreed_cents)],[8,money(d.totals.received_cents)],[9,money(d.totals.expense_cents)],[10,money(d.totals.outstanding_cents)],[11,money(d.totals.cash_margin_cents)]];
   for(const [i,value] of values){const card=el("div","zStudioMetric");card.append(el("small","",w()[i]),el("strong","",String(value)));grid.append(card)}report.append(grid);
   const pipeline=el("div","zStudioPipeline");
   for(const [key,i] of [["lead",12],["in_progress",13],["delivered",14],["cancelled",15]]){const row=el("div","zStudioOrder");row.append(el("span","",w()[i]),el("strong","",String(d.counts[key]||0)));pipeline.append(row)}report.append(pipeline);
   const flagWords={overdue:17,cost_overrun:18,due_soon:19,collect_payment:20,set_deadline:21,follow_up:22};
   report.append(el("h3","",w()[16]+" · "+d.action_count));
   if(!d.actions.length)report.append(el("p","",w()[25]));
   for(const action of d.actions){const row=el("div","zStudioAction");row.append(el("strong","",action.title),el("p","",action.flags.filter(f=>Object.hasOwn(flagWords,f)).map(f=>w()[flagWords[f]]).join(" · ")));report.append(row)}
   if(d.action_count>d.actions.length)report.append(el("small","",w()[28]));
   report.append(el("small","",w()[27]+": "+d.as_of+" UTC"));
 }
 load.onclick=async()=>{
   if(!allowed("businessButton")||typeof api!=="function")return;const id=++seq;load.disabled=true;data=null;report.replaceChildren();status.textContent=w()[3];
   try{const d=await api("/business/studio");if(id!==seq||!allowed("businessButton"))return;if(d.manual!==true||d.private!==true)throw Error("Invalid report");data=d;render(d);status.textContent=""}
   catch(e){if(id===seq&&allowed("businessButton"))status.textContent=w()[4]}
   finally{if(id===seq)load.disabled=false}
 };
 function sync(){
   const access=allowed("businessButton");if(!access&&hadAccess){clear();hub.open=false}hadAccess=access;if(hub.hidden===access)hub.hidden=!access;
   if(lang!==locale()){lang=locale();seq++;load.disabled=false;status.textContent="";if(data&&access)render(data)}
   title.textContent=w()[0];intro.textContent=w()[1];load.textContent=w()[2];crm.textContent=w()[23];jobs.textContent=w()[24];note.textContent=w()[26];const hideJobs=!allowed("jobsButton");if(jobs.hidden!==hideJobs)jobs.hidden=hideJobs;
 }
 let pending=false;const schedule=()=>{if(!pending){pending=true;queueMicrotask(()=>{pending=false;sync()})}};
 new MutationObserver(schedule).observe(nav,{subtree:true,attributes:true,attributeFilter:["hidden","disabled"]});
 new MutationObserver(schedule).observe(panel,{attributes:true,attributeFilter:["hidden"]});
 businessStudioRefresh=schedule;sync();
}
const commandDockWords={
 en:["Creator Command Center","Choose a workspace","Personal Teacher","Project Mentor","Career Center","Business Studio","AI Production","Portfolio","Find jobs","AI Support","Close workspace","Open full Command Center","Only one workspace is expanded at a time. Access remains account-dependent.","AI Agent Workforce","AI Agent Factory","AI Model Hub","Smart Router"],
 ru:["Creator Command Center","Выбери рабочий раздел","Персональный преподаватель","Наставник проектов","Карьера","Бизнес-студия","AI Production","Портфолио","Найти заказы","AI-поддержка","Закрыть раздел","Полный Command Center","Одновременно открыт один рабочий раздел. Доступ определяется аккаунтом.","AI Agent Workforce","AI Agent Factory","AI Model Hub","Smart Router"],
 uk:["Creator Command Center","Обери робочий розділ","Персональний викладач","Наставник проєктів","Кар'єра","Бізнес-студія","AI Production","Портфоліо","Знайти замовлення","ШІ-підтримка","Закрити розділ","Повний Command Center","Одночасно відкрито один робочий розділ. Доступ визначає акаунт.","AI Agent Workforce","AI Agent Factory","AI Model Hub","Smart Router"],
 pl:["Creator Command Center","Wybierz obszar pracy","Osobisty nauczyciel","Mentor projektów","Kariera","Studio biznesowe","AI Production","Portfolio","Znajdź zlecenia","Wsparcie AI","Zamknij obszar","Pełne Command Center","Jednocześnie otwarty jest jeden obszar. Dostęp zależy od konta.","AI Agent Workforce","AI Agent Factory","AI Model Hub","Smart Router"]};
let commandDockRefresh=null;
function commandDockDesign(){
 const overview=$("workspaceOverview"),panel=$("panel"),nav=$("academyNav");if(!overview||!panel||!nav)return;
 const words=()=>commandDockWords[locale()]||commandDockWords.en;
 const hub=el("section","zCommandDock"),head=el("h2"),intro=el("p"),grid=el("div","zCommandGrid"),body=el("div","zCommandBody"),close=el("button","zCommandClose"),note=el("p","zCommandNote");
 hub.id="zCommandDock";body.id="zCommandBody";close.type="button";close.hidden=true;body.hidden=true;hub.append(head,intro,grid,close,body,note);
 const onboarding=$("zOnboarding");if(onboarding)onboarding.after(hub);else overview.prepend(hub);
 const permitted=id=>{const n=$(id);return !panel.hidden&&!!n&&!n.disabled&&!n.closest("[hidden]")};
 const panels=[["zTeacherCenter",2,"graduation",null],["zProjectMentor",3,"clipboard-check",null],["zCareerCenter",4,"briefcase","careerButton"],["zBusinessStudio",5,"chart","businessButton"],["zWorkforce",13,"network",null],["zFactory",14,"workflow",null]];
 const entries=[];let selected=null;
 function tile(i,glyph){
   const b=el("button","zCommandTile"),art=el("span","zCommandIcon"),label=el("span");b.type="button";art.append(icon(glyph));b.append(art,label);grid.append(b);return {b,label,i};
 }
 function available(entry){return !panel.hidden&&(!entry.permission||permitted(entry.permission))}
 function choose(entry,focus=false){
   if(entry&&!available(entry))entry=null;
   selected=entry;
   for(const e of entries){if(!e.target)continue;const active=e===selected;e.target.classList.toggle("zCommandInactive",!active);e.b.setAttribute("aria-expanded",String(active));if(active&&e.target.tagName==="DETAILS")e.target.open=true}
   const open=!!selected;body.hidden=!open;close.hidden=!open;
   if(open&&focus){body.scrollIntoView({block:"start",behavior:"auto"});close.focus({preventScroll:true})}
 }
 for(const [id,i,glyph,permission] of panels){
   const target=$(id);if(!target)continue;
   // Move generated UI only; original lesson, navigation and checkout controls stay in place.
   const entry={...tile(i,glyph),target,permission};entry.b.setAttribute("aria-controls",id);entry.b.setAttribute("aria-expanded","false");entry.b.onclick=()=>choose(selected===entry?null:entry,true);entries.push(entry);body.append(target);
 }
 function shortcut(i,glyph,permission,action){
   const entry={...tile(i,glyph),permission};entry.b.onclick=()=>{if(available(entry))action()};entries.push(entry);
 }
 shortcut(6,"layers",null,()=>{const p=$("zProductionHub");if(p){expandOverviewHub(".zProductionHub");p.scrollIntoView({block:"start",behavior:"auto"})}else location.href=url("/ai-workspace")});
 shortcut(7,"image","portfolioButton",()=>$("portfolioButton").click());
 shortcut(8,"briefcase","jobsButton",()=>$("jobsButton").click());
 shortcut(9,"headphones",null,()=>{location.href=url("/support")});
 shortcut(15,"cpu",null,()=>{location.href=url("/free-ai#model-hub")});
 shortcut(16,"workflow",null,()=>{location.href=url("/free-ai#model-router")});
 const full=el("a","zCommandFull");full.href=url("/command-center");links.push([full,"/command-center"]);hub.append(full);
 close.onclick=()=>{const prior=selected;choose(null);prior?.b.focus()};
 function sync(){
   head.textContent=words()[0];intro.textContent=words()[1];close.textContent=words()[10];full.textContent=words()[11];note.textContent=words()[12];
   if(selected&&!available(selected))choose(null);
   for(const e of entries){if(e.label.textContent!==words()[e.i])e.label.textContent=words()[e.i];const hidden=!available(e);if(e.b.hidden!==hidden)e.b.hidden=hidden}
   if(panel.hidden){choose(null)}
 }
 let pending=false;const schedule=()=>{if(!pending){pending=true;queueMicrotask(()=>{pending=false;sync()})}};
 new MutationObserver(schedule).observe(panel,{attributes:true,attributeFilter:["hidden"]});
 new MutationObserver(schedule).observe(nav,{subtree:true,attributes:true,attributeFilter:["hidden","disabled"]});
 commandDockRefresh=schedule;choose(null);sync();
}
const workforceWords={
 en:["AI Agent Workforce","Free guided workflows · not running AI models","Teacher","Code assistant","Design assistant","Video producer","Marketing assistant","Project reviewer","Available lesson","Day","Build workflow","Loading…","Could not load workflow.","No available lessons.","Copy local AI prompt","Copied","Optional brief (stays on this page)","Use a local model manually. No automatic execution, model call or charge.","Do not include secrets. Verify outputs yourself; no official grade.","Copy failed; select the prompt manually.","Task","Workflow"],
 ru:["AI Agent Workforce","Бесплатные сценарии · не запущенные AI-модели","Преподаватель","Программист","Дизайнер","Видеопродюсер","Маркетолог","Ревьюер проектов","Доступный урок","День","Подготовить сценарий","Загрузка…","Не удалось загрузить сценарий.","Нет доступных уроков.","Копировать промпт для локального AI","Скопировано","Дополнительный бриф (остаётся на этой странице)","Запускай локальную модель самостоятельно. Без автоматического выполнения, вызова модели или списания средств.","Не вводи секреты. Проверяй результат самостоятельно; это не официальная оценка.","Не удалось скопировать; выдели промпт вручную.","Задание","Рабочий процесс"],
 uk:["AI Agent Workforce","Безплатні сценарії · не запущені ШІ-моделі","Викладач","Програміст","Дизайнер","Відеопродюсер","Маркетолог","Рев’юер проєктів","Доступний урок","День","Підготувати сценарій","Завантаження…","Не вдалося завантажити сценарій.","Немає доступних уроків.","Копіювати промпт для локального ШІ","Скопійовано","Додатковий бриф (лишається на сторінці)","Запускай локальну модель самостійно. Без автоматичного виконання, виклику моделі або списання коштів.","Не вводь секрети. Перевіряй результати; це не офіційна оцінка.","Не вдалося скопіювати; виділи промпт вручну.","Завдання","Робочий процес"],
 pl:["AI Agent Workforce","Bezpłatne scenariusze · nieuruchomione modele AI","Nauczyciel","Programista","Projektant","Producent wideo","Marketing","Recenzent projektów","Dostępna lekcja","Dzień","Przygotuj scenariusz","Wczytywanie…","Nie udało się wczytać scenariusza.","Brak dostępnych lekcji.","Kopiuj prompt do lokalnego AI","Skopiowano","Dodatkowy brief (pozostaje na stronie)","Uruchom lokalny model samodzielnie. Bez automatycznego wykonania, wywołania modelu lub opłat.","Nie podawaj sekretów. Sprawdź wyniki; to nie oficjalna ocena.","Nie udało się skopiować; zaznacz prompt ręcznie.","Zadanie","Przebieg pracy"]};
let workforceRefresh=null;
function workforceDesign(){
 const overview=$("workspaceOverview"),panel=$("panel"),days=$("days");if(!overview||!panel||!days)return;
 const w=()=>workforceWords[locale()]||workforceWords.en;
 const hub=el("section","zWorkforce"),head=el("h2"),intro=el("p"),roles=el("div","zWorkforceRoles"),day=el("select"),brief=el("textarea"),build=el("button","zAction primary"),status=el("p"),result=el("div","zWorkforceResult"),prompt=el("textarea"),copy=el("button","zAction"),local=el("a"),note=el("p");
 hub.id="zWorkforce";build.type=copy.type="button";brief.rows=3;brief.maxLength=1600;prompt.rows=7;prompt.readOnly=true;prompt.hidden=copy.hidden=true;status.setAttribute("role","status");
 local.href=url("/free-ai");local.textContent="Local AI / Model Hub";links.push([local,"/free-ai"]);hub.append(head,intro,roles,day,brief,build,status,result,prompt,copy,local,note);overview.append(hub);
 const specs=[["teacher","graduation"],["code","code"],["design","palette"],["video","video"],["marketing","chart"],["project","clipboard-check"]],buttons=[];let role="teacher",seq=0,signature="",data=null;
 function clear(){seq++;data=null;result.replaceChildren();prompt.value="";prompt.hidden=copy.hidden=true;status.textContent="";build.disabled=!day.value}
 for(const [i,[id,glyph]] of specs.entries()){const b=el("button","zWorkforceRole"),txt=el("span");b.type="button";b.append(icon(glyph),txt);b.onclick=()=>{role=id;clear();sync()};roles.append(b);buttons.push({b,txt,id,i})}
 function available(n){return Array.from(days.querySelectorAll("button[data-day]")).some(b=>Number(b.dataset.day)===n&&!b.disabled)}
 function sync(){
   const values=Array.from(days.querySelectorAll("button[data-day]")).filter(b=>!b.disabled).map(b=>b.dataset.day),key=JSON.stringify([locale(),values]);
   if(key!==signature){signature=key;const old=day.value;day.replaceChildren();for(const n of values){const option=el("option","",w()[9]+" "+n);option.value=n;day.append(option)}if(values.includes(old))day.value=old;clear();if(!values.length)status.textContent=w()[13]}
   head.textContent=w()[0];intro.textContent=w()[1];day.setAttribute("aria-label",w()[8]);brief.placeholder=w()[16];brief.setAttribute("aria-label",w()[16]);build.textContent=w()[10];copy.textContent=w()[14];note.textContent=w()[17]+" "+w()[18];prompt.setAttribute("aria-label",w()[14]);
   for(const {b,txt,id,i} of buttons){txt.textContent=w()[2+i];b.setAttribute("aria-pressed",String(id===role))}
 }
 day.onchange=clear;
 function updatePrompt(){
   if(!data)return;
   const roleLabel=w()[2+specs.findIndex(([id])=>id===data.role)];
   prompt.value=[roleLabel,w()[20]+": "+data.deliverable,w()[21]+":",...data.steps.map((s,i)=>(i+1)+". "+s),w()[18],brief.value.trim()].filter(Boolean).join("\n");prompt.hidden=copy.hidden=false;
 }
 brief.oninput=updatePrompt;
 build.onclick=async()=>{
   if(panel.hidden||!available(Number(day.value))||typeof api!=="function")return;
   const id=++seq,lesson=Number(day.value),language=locale(),chosen=role;data=null;build.disabled=true;result.replaceChildren();prompt.hidden=copy.hidden=true;status.textContent=w()[11];
   try{const d=await api("/agents/playbook",{day:lesson,role:chosen,lang:language});if(id!==seq||panel.hidden||!available(lesson))return;if(d.external_request!==false||d.automatic_execution!==false)throw Error("Invalid playbook");data=d;result.append(el("h3","",w()[20]),el("p","",d.deliverable));const list=el("ol");for(const step of d.steps)list.append(el("li","",step));result.append(list);updatePrompt();status.textContent=""}
   catch(e){if(id===seq&&!panel.hidden)status.textContent=w()[12]}
   finally{if(id===seq)build.disabled=!day.value}
 };
 copy.onclick=async()=>{if(panel.hidden||!data||!available(data.day))return;try{await navigator.clipboard.writeText(prompt.value);status.textContent=w()[15]}catch(e){prompt.focus();prompt.select();status.textContent=w()[19]}};
 let pending=false;const schedule=()=>{if(!pending){pending=true;queueMicrotask(()=>{pending=false;sync()})}};
 new MutationObserver(schedule).observe(days,{subtree:true,childList:true,attributes:true,attributeFilter:["disabled","data-state"]});
 new MutationObserver(()=>{if(panel.hidden){brief.value="";clear()}else sync()}).observe(panel,{attributes:true,attributeFilter:["hidden"]});
 workforceRefresh=schedule;sync();
}
const factoryWords={
en:["AI Agent Factory","Build an ordered team for an available lesson.","Lesson","Day","Add role","Remove","Move up","Move down","Teacher","Developer","Designer","Producer","Marketing","Reviewer","Optional project brief (local only)","Prepare team","Export JSON","Download local AI engine","No available lessons","Select at least one role","Preparing…","Could not prepare team","Ready to export","Open the JSON in the desktop Local AI Engine with Ollama and an installed model. No execution on the Academy server. Review all outputs.","Stage","No automatic charges or external actions."],
ru:["AI Agent Factory","Собери последовательную команду для доступного урока.","Урок","День","Добавить роль","Удалить","Выше","Ниже","Преподаватель","Разработчик","Дизайнер","Продюсер","Маркетолог","Ревьюер","Дополнительный бриф (только локально)","Подготовить команду","Экспорт JSON","Скачать Local AI Engine","Нет доступных уроков","Выбери хотя бы одну роль","Подготовка…","Не удалось подготовить команду","Готово к экспорту","Открой JSON в desktop Local AI Engine с Ollama и установленной моделью. На сервере академии запуск не выполняется. Проверяй результаты.","Этап","Без автоматических списаний и внешних действий."],
uk:["AI Agent Factory","Створи послідовну команду для доступного уроку.","Урок","День","Додати роль","Видалити","Вище","Нижче","Викладач","Розробник","Дизайнер","Продюсер","Маркетолог","Рев’юер","Додатковий бриф (лише локально)","Підготувати команду","Експорт JSON","Завантажити Local AI Engine","Немає доступних уроків","Обери хоча б одну роль","Підготовка…","Не вдалося підготувати команду","Готово до експорту","Відкрий JSON у desktop Local AI Engine з Ollama та встановленою моделлю. На сервері академії запуску немає. Перевіряй результати.","Етап","Без автоматичних списань і зовнішніх дій."],
pl:["AI Agent Factory","Zbuduj sekwencyjny zespół dla dostępnej lekcji.","Lekcja","Dzień","Dodaj rolę","Usuń","Wyżej","Niżej","Nauczyciel","Programista","Projektant","Producent","Marketing","Recenzent","Dodatkowy brief (tylko lokalnie)","Przygotuj zespół","Eksport JSON","Pobierz Local AI Engine","Brak dostępnych lekcji","Wybierz co najmniej jedną rolę","Przygotowanie…","Nie udało się przygotować zespołu","Gotowe do eksportu","Otwórz JSON w desktop Local AI Engine z Ollama i zainstalowanym modelem. Brak uruchamiania na serwerze akademii. Sprawdź wyniki.","Etap","Bez automatycznych opłat i działań zewnętrznych."]};
let factoryRefresh=null;
const factoryProjectWords={
en:["Save as private project","Project title","Project type","Image","Video","Advertising","Animation","Audio","Product","Deadline (optional)","Save project and tasks","Project saved","Could not save project. Check title, date and combined brief (max 2000 characters).","Open Project Manager","Save this project and checklist to your Academy account? No external actions.","Only task checklist and brief are saved; export JSON separately for AI execution."],
ru:["Сохранить как личный проект","Название проекта","Тип проекта","Изображение","Видео","Реклама","Анимация","Аудио","Продукт","Срок (необязательно)","Сохранить проект и задачи","Проект сохранён","Не удалось сохранить. Проверь название, дату и общий бриф (до 2000 символов).","Открыть Project Manager","Сохранить проект и список задач в аккаунте академии? Внешних действий не будет.","Сохраняются бриф и чек-лист; для запуска AI скачай JSON отдельно."],
uk:["Зберегти як особистий проєкт","Назва проєкту","Тип проєкту","Зображення","Відео","Реклама","Анімація","Аудіо","Продукт","Термін (необов’язково)","Зберегти проєкт і завдання","Проєкт збережено","Не вдалося зберегти. Перевір назву, дату й загальний бриф (до 2000 символів).","Відкрити Project Manager","Зберегти проєкт і завдання в акаунті академії? Без зовнішніх дій.","Зберігаються бриф і чекліст; для запуску ШІ експортуй JSON окремо."],
pl:["Zapisz jako prywatny projekt","Nazwa projektu","Typ projektu","Obraz","Wideo","Reklama","Animacja","Audio","Produkt","Termin (opcjonalnie)","Zapisz projekt i zadania","Projekt zapisany","Nie zapisano. Sprawdź nazwę, datę i łączny brief (maks. 2000 znaków).","Otwórz Project Manager","Zapisać projekt i listę zadań na koncie Akademii? Bez działań zewnętrznych.","Zapisywany jest brief i lista zadań; wyeksportuj JSON osobno, aby uruchomić AI."]};
function factoryDesign(){
 const overview=$("workspaceOverview"),panel=$("panel"),days=$("days");if(!overview||!panel||!days)return;
 const w=()=>factoryWords[locale()]||factoryWords.en;
 const hub=el("section","zFactory"),head=el("h2"),intro=el("p"),lesson=el("select"),role=el("select"),add=el("button","zAction"),bar=el("div","zFactoryControls"),list=el("div","zFactoryStages"),brief=el("textarea"),build=el("button","zAction primary"),save=el("button","zAction"),download=el("a"),status=el("p"),note=el("p"),result=el("div");
 hub.id="zFactory";brief.rows=3;brief.maxLength=1600;add.type=build.type=save.type="button";save.disabled=true;status.setAttribute("role","status");download.href="/local-ai-engine.py";download.download="zer0life_local_ai.py";bar.append(role,add);const browser=el("a");browser.href=url("/free-ai#academy-team-import");links.push([browser,"/free-ai#academy-team-import"]);hub.append(head,intro,lesson,bar,list,brief,build,save,status,result,download,browser,note);overview.append(hub);
 const roles=["teacher","code","design","video","marketing","project"];let team=["design","video","project"],seq=0,data=null,signature="",busy=false;
 const pw=()=>factoryProjectWords[locale()]||factoryProjectWords.en;
 const project=el("details","zFactoryProject"),projectHead=el("summary"),projectTitle=el("input"),projectKind=el("select"),projectDue=el("input"),projectSave=el("button","zAction primary"),projectOpen=el("button","zAction"),projectStatus=el("p"),projectHint=el("p");
 const kinds=["image","video","advertising","animation","audio","product"];for(const k of kinds){const o=el("option");o.value=k;projectKind.append(o)}projectKind.value="video";projectTitle.maxLength=160;projectDue.type="date";projectSave.type=projectOpen.type="button";projectStatus.setAttribute("role","status");project.append(projectHead,projectTitle,projectKind,projectDue,projectSave,projectOpen,projectHint,projectStatus);hub.append(project);project.hidden=true;let projectBusy=false,projectSaved=false;
 function projectSync(){
   projectHead.textContent=pw()[0];projectTitle.placeholder=pw()[1];projectTitle.setAttribute("aria-label",pw()[1]);projectKind.setAttribute("aria-label",pw()[2]);projectDue.setAttribute("aria-label",pw()[9]);Array.from(projectKind.options).forEach((o,i)=>o.textContent=pw()[3+i]);projectSave.textContent=pw()[10];projectOpen.textContent=pw()[13];projectHint.textContent=pw()[15];projectSave.disabled=projectBusy||projectSaved||!data;projectTitle.disabled=projectKind.disabled=projectDue.disabled=projectBusy||projectSaved;project.hidden=!data;
 }
 projectSave.onclick=async()=>{
   if(projectBusy||projectSaved||!data||panel.hidden||!allowed(data.day)||typeof api!=="function")return;
   const title=projectTitle.value.trim(),custom=brief.value.trim();
   if(!title||Array.from(data.deliverable+"\n\n"+custom).length>2000){projectStatus.textContent=pw()[12];return}
   if(!confirm(pw()[14]))return;
   const id=seq,payload={day:data.day,roles:data.stages.map(s=>s.role),lang:data.language,title,kind:projectKind.value,due:projectDue.value,custom_brief:custom};projectBusy=true;projectSync();
   try{const r=await api("/agents/project",payload);if(id!==seq||panel.hidden)return;projectSaved=true;projectStatus.textContent=pw()[11]+" · #"+r.id+" · "+r.tasks}
   catch(e){if(id===seq&&!panel.hidden)projectStatus.textContent=pw()[12]}
   finally{projectBusy=false;projectSync()}
 };
 projectOpen.onclick=()=>{const b=$("workflowButton");if(b&&!b.hidden&&!b.disabled&&!panel.hidden)b.click()};

 const allowed=n=>Array.from(days.querySelectorAll("button[data-day]")).some(b=>Number(b.dataset.day)===n&&!b.disabled);
 function invalidate(){seq++;data=null;busy=false;save.disabled=true;result.replaceChildren();status.textContent="";build.disabled=!lesson.value||!team.length;projectSaved=false;projectStatus.textContent="";projectSync()}
 function renderRoles(){
   const previous=role.value;role.replaceChildren();for(const r of roles.filter(r=>!team.includes(r))){const option=el("option","",w()[8+roles.indexOf(r)]);option.value=r;role.append(option)}if(Array.from(role.options).some(o=>o.value===previous))role.value=previous;add.disabled=team.length===roles.length;
   list.replaceChildren();
   for(const [i,r] of team.entries()){const row=el("div","zFactoryStage"),text=el("strong","",(i+1)+". "+w()[8+roles.indexOf(r)]);row.append(text);
     for(const [word,action,disabled] of [[6,()=>{[team[i-1],team[i]]=[team[i],team[i-1]]},i===0],[7,()=>{[team[i+1],team[i]]=[team[i],team[i+1]]},i===team.length-1],[5,()=>team.splice(i,1),false]]){const b=el("button","zAction",w()[word]);b.type="button";b.disabled=disabled;b.onclick=()=>{action();invalidate();renderRoles()};row.append(b)}list.append(row)}
 }
 function sync(){
   const vals=Array.from(days.querySelectorAll("button[data-day]")).filter(b=>!b.disabled).map(b=>b.dataset.day),key=JSON.stringify([locale(),vals]);
   if(key!==signature){signature=key;const old=lesson.value;lesson.replaceChildren();for(const n of vals){const o=el("option","",w()[3]+" "+n);o.value=n;lesson.append(o)}if(vals.includes(old))lesson.value=old;invalidate();if(!vals.length)status.textContent=w()[18]}
   head.textContent=w()[0];intro.textContent=w()[1];lesson.setAttribute("aria-label",w()[2]);role.setAttribute("aria-label",w()[4]);add.textContent=w()[4];brief.placeholder=w()[14];brief.setAttribute("aria-label",w()[14]);build.textContent=w()[15];save.textContent=w()[16];download.textContent=w()[17];browser.textContent=({en:"Open browser AI Studio",ru:"Открыть браузерную AI Studio",uk:"Відкрити браузерну AI Studio",pl:"Otwórz AI Studio w przeglądarce"})[locale()];note.textContent=w()[23]+" "+w()[25];renderRoles();projectSync();
 }
 add.onclick=()=>{if(roles.includes(role.value)&&!team.includes(role.value)){team.push(role.value);invalidate();renderRoles()}};
 lesson.onchange=invalidate;
 build.onclick=async()=>{
   if(busy||panel.hidden||!allowed(Number(lesson.value))||!team.length||typeof api!=="function")return;
   const id=++seq,n=Number(lesson.value);busy=true;build.disabled=true;data=null;save.disabled=true;projectSaved=false;projectStatus.textContent="";projectSync();result.replaceChildren();status.textContent=w()[20];
   try{const d=await api("/agents/team",{day:n,roles:team.slice(),lang:locale()});if(id!==seq||panel.hidden||!allowed(n))return;if(d.schema!=="zer0life-agent-team-v1"||d.external_request!==false||d.automatic_execution!==false)throw Error("Invalid team");data=d;result.append(el("p","",d.deliverable));for(const s of d.stages){const card=el("div","zFactoryStage");card.append(el("strong","",w()[24]+" "+s.stage+" · "+w()[8+roles.indexOf(s.role)]),el("p","",s.steps.join(" · ")));result.append(card)}save.disabled=false;status.textContent=w()[22];projectSync()}
   catch(e){if(id===seq&&!panel.hidden)status.textContent=w()[21]}
   finally{if(id===seq){busy=false;build.disabled=false}}
 };
 save.onclick=()=>{if(!data||panel.hidden||!allowed(data.day))return;const blob=new Blob([JSON.stringify({...data,custom_brief:brief.value.trim()},null,2)],{type:"application/json"}),address=URL.createObjectURL(blob),a=el("a");a.href=address;a.download="zer0life-agent-team.json";a.click();setTimeout(()=>URL.revokeObjectURL(address),1500)};
 let pending=false;const schedule=()=>{if(!pending){pending=true;queueMicrotask(()=>{pending=false;sync()})}};
 new MutationObserver(schedule).observe(days,{subtree:true,childList:true,attributes:true,attributeFilter:["disabled","data-state"]});
 new MutationObserver(()=>{if(panel.hidden){brief.value="";projectTitle.value="";projectDue.value="";team=["design","video","project"];invalidate()}else sync()}).observe(panel,{attributes:true,attributeFilter:["hidden"]});
 factoryRefresh=schedule;sync();
}
const deliveryCenterWords={
 en:["Client Delivery Center","Deliveries","Revision requests","Milestones","Open milestones","Recent handoffs (latest 10)","Delivery","Revision","Download handoff report","No handoffs yet","Private record; does not certify quality or payment. Review before sharing.","Status"],
 ru:["Client Delivery Center","Сдано версий","Запросы правок","Этапы проекта","Незакрытые этапы","История сдачи (последние 10)","Сдача","Правки","Скачать отчёт о сдаче","Пока нет сдач","Личная запись; не подтверждает качество или оплату. Проверь перед передачей.","Статус"],
 uk:["Client Delivery Center","Здано версій","Запити правок","Етапи проєкту","Незакриті етапи","Історія здачі (останні 10)","Здача","Правки","Завантажити звіт","Здач ще немає","Приватний запис; не підтверджує якість чи оплату. Перевір перед передаванням.","Статус"],
 pl:["Client Delivery Center","Oddane wersje","Prośby o poprawki","Etapy projektu","Otwarte etapy","Historia oddań (ostatnie 10)","Oddanie","Poprawki","Pobierz raport","Brak oddań","Prywatny zapis; nie potwierdza jakości ani płatności. Sprawdź przed udostępnieniem.","Status"]};
function renderDeliveryCenter(host,d,lang){
 const x=d.delivery;if(!x||x.advisory_only!==true)return;
 const w=deliveryCenterWords[lang]||deliveryCenterWords.en,root=document.createElement("details");root.className="zDeliveryCenter";host.append(root);root.open=true;
 const make=(p,tag,t="")=>{const n=document.createElement(tag);n.textContent=t;p.append(n);return n};
 make(root,"summary",w[0]);const lines=[w[0],w[11]+": "+x.status,w[1]+": "+x.deliveries,w[2]+": "+x.revisions,w[3]+": "+x.milestones_done+"/"+x.milestones_total,w[4]+": "+x.open_milestones];
 for(const line of lines.slice(1))make(root,"p",line);
 make(root,"h3",w[5]);const events=Array.isArray(x.recent_events)?x.recent_events.slice(0,10):[];
 if(!events.length)make(root,"p",w[9]);
 for(const e of events){const label=w[e.kind==="deliver"?6:7]+" · "+e.created_at;const row=make(root,"article");make(row,"strong",label);make(row,"p",e.body);lines.push(label,e.body)}
 make(root,"p",w[10]);lines.push(w[10]);const b=make(root,"button",w[8]);b.type="button";b.onclick=()=>{if(!root.isConnected)return;const address=URL.createObjectURL(new Blob([lines.join("\n\n")],{type:"text/plain;charset=utf-8"})),a=document.createElement("a");a.href=address;a.download="zer0life-delivery-report.txt";a.click();setTimeout(()=>URL.revokeObjectURL(address),1000)};
}
function installDeliveryCenter(){
 // Keep the original schedule renderer and return contract. Only add presentation.
 if(typeof renderProjectSchedule!=="function")return;
 const original=renderProjectSchedule;
 renderProjectSchedule=function(host,d,lang){const w=original(host,d,lang);try{renderDeliveryCenter(host,d,lang)}catch(e){console.warn("Delivery presentation",e.name)}return w};
}
const creatorEvidenceWords={
 en:["Portfolio & Reputation","Refresh private evidence","Submissions","Reviewed submissions","Lessons with projects","Completed client orders","Approved client reviews","Rating","Academy lessons passed (paid enrollment)","Certificate issued","Service listing","Graduate showcase","Download summary","Yes","No","No rating","Loading…","Could not load evidence","Not a professional credential or payment confirmation. Sharing is optional; check before sending.","Not listed","Pending","Approved","Rejected","Blocked","Withdrawn"],
 ru:["Портфолио и репутация","Обновить личные достижения","Отправленные работы","Проверенные работы","Уроки с проектами","Завершённые клиентские заказы","Одобренные отзывы клиентов","Рейтинг","Пройденные уроки (платный курс)","Сертификат выдан","Услуга на бирже","Портфолио выпускника","Скачать сводку","Да","Нет","Нет рейтинга","Загрузка…","Не удалось загрузить данные","Не является профессиональной квалификацией или подтверждением оплаты. Передавай только после проверки.","Не размещена","На модерации","Одобрена","Отклонена","Заблокирована","Снята"],
 uk:["Портфоліо та репутація","Оновити особисті досягнення","Надіслані роботи","Перевірені роботи","Уроки з проєктами","Завершені замовлення","Схвалені відгуки клієнтів","Рейтинг","Пройдені уроки (платний курс)","Сертифікат видано","Послуга на біржі","Портфоліо випускника","Завантажити звіт","Так","Ні","Немає рейтингу","Завантаження…","Не вдалося завантажити дані","Не є професійною кваліфікацією чи підтвердженням оплати. Перевір перед поширенням.","Не розміщена","На модерації","Схвалена","Відхилена","Заблокована","Знята"],
 pl:["Portfolio i reputacja","Odśwież prywatne osiągnięcia","Przesłane prace","Sprawdzone prace","Lekcje z projektami","Zakończone zlecenia","Zatwierdzone opinie klientów","Ocena","Ukończone lekcje (płatny kurs)","Wydany certyfikat","Usługa na giełdzie","Portfolio absolwenta","Pobierz podsumowanie","Tak","Nie","Brak oceny","Ładowanie…","Nie udało się wczytać danych","Nie jest kwalifikacją zawodową ani potwierdzeniem płatności. Sprawdź przed udostępnieniem.","Brak oferty","Moderacja","Zatwierdzona","Odrzucona","Zablokowana","Wycofana"]};
const creatorNextWords={
 en:["Your next steps","Complete a practical project and submit it for review.","Check feedback when your submitted work is reviewed.","Prepare a service listing with clear scope and pricing.","Find suitable client briefs and agree on deliverables before accepting work.","After a completed order, invite honest client feedback through the platform.","Complete your course and required assessments for the Academy certificate.","If you wish, publish a graduate showcase using only work you have permission to share.","Keep your portfolio current and improve it using client feedback."],
 ru:["Следующие шаги","Выполни практический проект и отправь его на проверку.","Изучи обратную связь, когда твои работы будут проверены.","Подготовь предложение услуги с чётким объёмом работ и ценой.","Найди подходящие заказы и согласуй результат до начала работы.","После завершения заказа предложи клиенту оставить честный отзыв через платформу.","Заверши курс и необходимые проверки для получения сертификата Academy.","При желании опубликуй портфолио выпускника только с разрешёнными к публикации работами.","Обновляй портфолио и улучшай его с учётом отзывов клиентов."],
 uk:["Наступні кроки","Виконай практичний проєкт і надішли його на перевірку.","Ознайомся з відгуками, коли твої роботи перевірять.","Підготуй пропозицію послуги з чітким обсягом робіт і ціною.","Знайди відповідні замовлення та узгодь результат до початку роботи.","Після завершення замовлення запропонуй клієнту залишити чесний відгук через платформу.","Заверши курс і необхідні перевірки для отримання сертифіката Academy.","За бажанням опублікуй портфоліо випускника лише з дозволеними до публікації роботами.","Оновлюй портфоліо та вдосконалюй його з урахуванням відгуків клієнтів."],
 pl:["Następne kroki","Wykonaj projekt praktyczny i prześlij go do oceny.","Zapoznaj się z opiniami po sprawdzeniu swoich prac.","Przygotuj ofertę usługi z jasnym zakresem i ceną.","Znajdź odpowiednie zlecenia i uzgodnij rezultat przed rozpoczęciem pracy.","Po ukończeniu zlecenia poproś klienta o szczerą opinię za pośrednictwem platformy.","Ukończ kurs i wymagane oceny, aby otrzymać certyfikat Academy.","Jeśli chcesz, opublikuj portfolio absolwenta wyłącznie z pracami, które wolno udostępniać.","Aktualizuj portfolio i ulepszaj je na podstawie opinii klientów."]};
function creatorNextSteps(x){
 const steps=[];
 if(x.submitted===0)steps.push(1);
 else if(x.reviewed<x.submitted)steps.push(2);
 if(["none","withdrawn","rejected"].includes(x.listing_status))steps.push(3);
 if(x.completed_orders===0&&x.listing_status==="approved")steps.push(4);
 if(x.completed_orders>0&&x.approved_reviews===0)steps.push(5);
 if(x.certificate_issued===false)steps.push(6);
 else if(x.showcase_published===false)steps.push(7);
 return (steps.length?steps:[8]).slice(0,3);
}
let creatorEvidenceRefresh=null;
function creatorEvidenceDesign(){
 const hub=$("zCareerCenter"),panel=$("panel"),nav=$("academyNav"),career=$("careerButton");if(!hub||!panel||!nav||!career)return;
 const w=()=>creatorEvidenceWords[locale()]||creatorEvidenceWords.en;
 const section=el("details","zCreatorEvidence"),head=el("summary"),load=el("button","zAction"),exportBtn=el("button","zAction"),status=el("p"),rows=el("div","zEvidenceRows"),note=el("p");
 const nextTitle=el("h3"),nextList=el("ol","zEvidenceNext");nextTitle.hidden=nextList.hidden=true;
 section.id="zCreatorEvidence";load.type=exportBtn.type="button";status.setAttribute("role","status");section.append(head,load,status,rows,nextTitle,nextList,exportBtn,note);hub.append(section);
 let data=null,request=0,busy=false,lastAccess=false;
 const allowed=()=>!panel.hidden&&!career.disabled&&!career.closest("[hidden]");
 function entries(){if(!data)return [];const x=data,t=w(),yes=v=>t[v===true?13:14],states={none:19,pending:20,approved:21,rejected:22,blocked:23,withdrawn:24};return [[2,x.submitted],[3,x.reviewed],[4,x.project_lessons],[5,x.completed_orders],[6,x.approved_reviews],[7,x.rating===null?t[15]:x.rating+" / 5"],[8,x.completed_lessons],[9,yes(x.certificate_issued)],[10,t[states[x.listing_status]??19]],[11,yes(x.showcase_published)]]}
 function draw(){rows.replaceChildren();for(const [i,v] of entries()){const row=el("div","zCareerStage");row.append(el("span","",w()[i]),el("strong","",String(v)));rows.append(row)}const visible=Boolean(data)&&!busy&&allowed();nextTitle.hidden=nextList.hidden=!visible;nextList.replaceChildren();if(visible){const t=creatorNextWords[locale()]||creatorNextWords.en;nextTitle.textContent=t[0];for(const i of creatorNextSteps(data))nextList.append(el("li","",t[i]))}exportBtn.disabled=!visible}
 function reset(){request++;data=null;busy=false;status.textContent="";section.open=false;draw()}
 function sync(){const access=allowed();if(lastAccess&&!access)reset();lastAccess=access;section.hidden=!access;head.textContent=w()[0];load.textContent=w()[1];exportBtn.textContent=w()[12];note.textContent=w()[18];load.disabled=busy||!access;draw()}
 load.onclick=async()=>{if(!allowed()||busy||typeof api!=="function")return;const id=++request;busy=true;data=null;status.textContent=w()[16];sync();try{const d=await api("/career/evidence");if(id!==request||!allowed())return;if(d.private!==true||d.official_credential!==false)throw Error("Invalid evidence");data=d;status.textContent=""}catch(e){if(id===request&&allowed())status.textContent=w()[17]}finally{if(id===request){busy=false;sync()}}};
 exportBtn.onclick=()=>{if(!data||busy||!allowed())return;const text=[w()[0],...entries().map(([i,v])=>w()[i]+": "+v),w()[18]].join("\n");const address=URL.createObjectURL(new Blob([text],{type:"text/plain;charset=utf-8"})),a=el("a");a.href=address;a.download="zer0life-creator-evidence.txt";a.click();setTimeout(()=>URL.revokeObjectURL(address),1000)};
 let pending=false;const schedule=()=>{if(!pending){pending=true;queueMicrotask(()=>{pending=false;sync()})}};
 new MutationObserver(schedule).observe(panel,{attributes:true,attributeFilter:["hidden"]});new MutationObserver(schedule).observe(nav,{subtree:true,attributes:true,attributeFilter:["disabled","hidden"]});window.addEventListener("pagehide",reset);window.addEventListener("pageshow",schedule);creatorEvidenceRefresh=schedule;sync();
}
function update(){for(const [n,i] of localized)n.textContent=w()[i];for(const [a,p] of links)a.href=url(p);courseRelabel?.();bottomRefresh?.();authRelabel?.();profileRefresh?.();learningRefresh?.();businessRefresh?.();productionRefresh?.();socialRefresh?.();adminRefresh?.();compactRefresh?.();onboardingRefresh?.();teacherCenterRefresh?.();mentorRefresh?.();careerCenterRefresh?.();creatorEvidenceRefresh?.();businessStudioRefresh?.();commandDockRefresh?.();workforceRefresh?.();factoryRefresh?.();motion()}
document.body.classList.add("zAurora");if($("workspaceOverview"))dashboard();else{moduleHeader();moduleDesign();businessDesign();if(location.pathname==="/free-ai"&&$("title")&&$("intro")){const h=document.querySelector("main>header"),n=hero(false);if(h)h.after(n);else document.querySelector("main")?.prepend(n)}productionDesign()}
lang?.addEventListener("change",update);reduced.addEventListener?.("change",motion);document.addEventListener("visibilitychange",motion);update();
})();
