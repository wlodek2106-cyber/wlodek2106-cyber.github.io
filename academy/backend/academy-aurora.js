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
function motion(){for(const [n,b] of scenes){n.classList.toggle("zPaused",paused||reduced.matches||document.hidden);b.hidden=reduced.matches;b.textContent=w()[paused?33:32];b.setAttribute("aria-pressed",String(paused))}}
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
 // All existing shortcuts can still call the original lesson button, including a collapsed module.
 days.addEventListener("click",e=>{const b=e.target.closest("button[data-day]");if(!b||b.disabled)return;const item=cards.find(x=>x.panel.contains(b));if(item)selectTrack(item.index)},{capture:true});
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
 function sync(){const active=!auth.hidden&&!document.body.classList.contains("signedIn");if(document.body.classList.contains("zAuthMode")!==active)document.body.classList.toggle("zAuthMode",active);if(nav.hidden===active)nav.hidden=!active;if(!active)nav.open=false;art.classList.toggle("zAuthInactive",!active)}
 new MutationObserver(sync).observe(auth,{attributes:true,attributeFilter:["hidden"]});new MutationObserver(sync).observe(document.body,{attributes:true,attributeFilter:["class"]});
 // Avoid a class mutation observer feedback loop: classList.toggle only when state differs.
 authRelabel=()=>{const a=aw();slogan.textContent=a[0];tagline.textContent=a[1];navLabel.textContent=a[2];sealText.textContent=a[3];hint.textContent=a[4];passHint.textContent=passkey&&!passkey.hidden?a[5]:a[6];if(identifier)identifier.setAttribute("aria-label",a[7]);if(password)password.setAttribute("aria-label",a[8]);if(code)code.setAttribute("aria-label",a[9]);for(const a of original){const raw=a.getAttribute("href");if(raw?.startsWith("/")&&!raw.startsWith("//"))a.href=url(raw)}};
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
function dashboard(){const overview=$("workspaceOverview");authDesign();overview.prepend(hero(true),quick(),tiles());courseCards();bottomNav();profileDesign();learningDesign();const mark=document.querySelector(".sideMark");if(mark)mark.replaceChildren(orb());for(const n of document.querySelectorAll("#academyNav .navItem")){const name=navIcons[n.id]||navMap[n.getAttribute("href")?.split("?")[0]]?.[1];if(name&&n.firstElementChild)n.firstElementChild.replaceWith(icon(name))}const eye=document.querySelector(".workspaceTop .eyebrow");if(eye)eye.textContent="ZER0LIFE / ACADEMY 2027"}
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
function update(){for(const [n,i] of localized)n.textContent=w()[i];for(const [a,p] of links)a.href=url(p);courseRelabel?.();bottomRefresh?.();authRelabel?.();profileRefresh?.();learningRefresh?.();motion()}
document.body.classList.add("zAurora");if($("workspaceOverview"))dashboard();else{moduleHeader();moduleDesign();if(location.pathname==="/free-ai"&&$("title")&&$("intro")){const h=document.querySelector("main>header"),n=hero(false);if(h)h.after(n);else document.querySelector("main")?.prepend(n)}}
lang?.addEventListener("change",update);reduced.addEventListener?.("change",motion);document.addEventListener("visibilitychange",motion);update();
})();
