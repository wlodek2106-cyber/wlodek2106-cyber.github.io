"""ELITE production residency: five 3-day projects, separate from legacy exams."""
def student_progress(token):
    from learning import student_progress as load
    return load(token)

PROJECTS=[
("humans","AI Digital Humans",{
"en":["Design an original fictional brand ambassador. Create a character bible, 6 reference images with consistent identity, and a consent/license register.","Produce two 15-second speaking clips with different emotions. Use a local ComfyUI/Qwen workflow and compatible lip-sync/voice tools. Check mouth timing, continuity and synthetic-media labeling.","Deliver both clips, reference sheet, reproducible workflow/settings, failure notes and a client-ready usage guide."],
"ru":["Создай вымышленного амбассадора бренда. Подготовь паспорт персонажа, 6 согласованных референсов и журнал прав/согласий.","Сделай два говорящих ролика по 15 секунд с разными эмоциями. Используй локальный ComfyUI/Qwen и совместимые инструменты голоса и артикуляции. Проверь синхронизацию губ и идентичность, обозначь AI-контент.","Сдай оба ролика, референсы, воспроизводимый workflow/настройки, журнал ошибок и инструкцию для клиента."],
"uk":["Створи вигаданого амбасадора: паспорт персонажа, 6 узгоджених референсів і журнал прав.","Зроби два ролики по 15 секунд з різними емоціями через локальні моделі. Перевір артикуляцію, сталість образу й маркування ШІ.","Здай ролики, референси, налаштування, журнал помилок та інструкцію клієнту."],
"pl":["Stwórz fikcyjnego ambasadora marki: karta postaci, 6 spójnych referencji i rejestr praw.","Wykonaj dwa klipy po 15 s z różnymi emocjami lokalnymi narzędziami. Sprawdź ruch ust, spójność i oznaczenie AI.","Oddaj klipy, referencje, ustawienia, błędy i instrukcję dla klienta."]},[["Design Studio","/design-studio"],["Voice Studio","/voice-studio"]]),
("film","AI Film & 3D Production",{
"en":["Plan a 60–90-second film: script, scene timings, shot list, character continuity, sound and asset rights. Capture overlapping images of one object for OpenMVS.","Generate or shoot footage, reconstruct the object locally, edit the film and compare enhancement settings in Veyra. Use permitted local models; log GPU limits and failures.","Deliver a film or clearly labeled animatic, 3D model if reconstruction succeeded, captions, QC report, project settings and a rights ledger."],
"ru":["Спланируй фильм на 60–90 секунд: сценарий, тайминг, список кадров, согласованность героев, звук и права. Сними объект с перекрытием кадров для OpenMVS.","Сгенерируй или сними материал, реконструируй объект локально, смонтируй фильм и сравни обработку в Veyra. Запиши ограничения GPU и ошибки; используй разрешённые модели.","Сдай фильм или явно обозначенный аниматик, 3D-модель при успешной реконструкции, субтитры, QC-отчёт, настройки и журнал прав."],
"uk":["Сплануй фільм 60–90 с: сценарій, кадри, звук, права. Зніми об’єкт для OpenMVS.","Створи матеріал, реконструюй об’єкт локально, змонтуй і порівняй Veyra. Запиши обмеження GPU.","Здай фільм або позначений аніматик, модель за успіху, субтитри, QC та журнал прав."],
"pl":["Zaplanuj film 60–90 s: scenariusz, ujęcia, dźwięk i prawa. Zrób zdjęcia obiektu dla OpenMVS.","Stwórz materiał, zrekonstruuj obiekt lokalnie, zmontuj film i porównaj Veyra. Zapisz ograniczenia GPU.","Oddaj film lub oznaczony animatik, model po sukcesie, napisy, raport QC i prawa."]},[["Storyboard","/dashboard?module=storyboard"],["OpenMotion","/openmotion-lab"],["OpenMVS","/openmvs-lab"],["Veyra","/veyra-lab"]]),
("agents","AI Agent Factory · Business Automation",{
"en":["Map a fictional company's workflow with inputs, outputs, human approval gates and an explicit tool allowlist. Define planner, producer and reviewer.","Use the Local AI Engine with a downloaded Ollama model to run a bounded team. Add a test harness for malformed inputs, contradictory instructions, missing data and timeouts. No external writes or payments.","Deliver architecture, three normal and three failure tests, output logs, a human approval policy and a cost/latency report."],
"ru":["Опиши процесс вымышленной компании: входы, выходы, точки подтверждения человеком и разрешённые инструменты. Назначь планировщика, исполнителя и ревьюера.","Запусти ограниченную команду через Local AI Engine и локальный Ollama. Проверь некорректный ввод, противоречия, отсутствие данных и таймауты. Без внешних записей и платежей.","Сдай архитектуру, три обычных и три ошибочных теста, логи, правила подтверждения и отчёт о времени/затратах."],
"uk":["Опиши процес компанії, входи, виходи, дозволи й людське підтвердження.","Запусти обмежену команду через локальний Ollama. Перевір помилки вводу, суперечності та таймаути. Без зовнішніх дій.","Здай архітектуру, 3 звичайні й 3 помилкові тести, логи, правила та звіт."],
"pl":["Opisz proces firmy, wejścia, wyjścia, uprawnienia i akceptację człowieka.","Uruchom zespół lokalnym Ollama. Sprawdź błędne dane, sprzeczności i timeouty. Bez działań zewnętrznych.","Oddaj architekturę, 3 normalne i 3 błędne testy, logi, zasady oraz raport."]},[["Local AI Engine","/local-ai-engine.py"],["Automation Studio","/automation-studio"]]),
("teacher","AI Personal Teacher · Knowledge Product",{
"en":["Choose a topic you know. Write three learning objectives, a reference explanation, examples and an assessment rubric. Separate source facts from model-generated claims.","Use the local tutor to explain, diagnose misconceptions and vary difficulty. Test a correct, wrong and ambiguous answer. Check answers against your source material and record corrections.","Deliver a mini-course, tutor dialogue, evaluation rubric, evidence of corrections and a spaced review plan. Never treat AI feedback as an accredited grade."],
"ru":["Выбери знакомую тему. Определи три цели обучения, эталонное объяснение, примеры и критерии проверки. Отдели факты источника от утверждений модели.","Через локального наставника объясни тему, выяви заблуждения и измени сложность. Проверь правильный, неверный и неоднозначный ответ. Сверь выводы с источниками.","Сдай мини-курс, диалог, рубрику оценки, подтверждения исправлений и план повторений. AI-оценка не является аккредитованной."],
"uk":["Обери тему, три цілі, еталонне пояснення, приклади та критерії.","Локальним наставником перевір правильну, хибну та неоднозначну відповідь. Зістав із джерелами.","Здай мінікурс, діалог, критерії, виправлення й план повторень."],
"pl":["Wybierz temat, trzy cele, wyjaśnienie wzorcowe, przykłady i kryteria.","Lokalnym tutorem sprawdź odpowiedź poprawną, błędną i niejednoznaczną. Porównaj ze źródłami.","Oddaj minikurs, dialog, rubrykę, poprawki i plan powtórek."]},[["Local teacher","/free-ai?role=teacher"],["Knowledge Center","/dashboard?module=knowledge"]]),
("business","AI Studio & Freelance Business",{
"en":["Choose a real target market. Define three services, portfolio evidence, deliverable scope, licensing, revision limits and a price floor based on costs.","Use existing Career Center and marketplace. Draft three personalized proposals and a client onboarding checklist; use real approved listings only. Estimate platform fee, taxes separately, and delivery capacity. Never invent orders.","Deliver a studio portfolio, pricing sheet, proposals, quality checklist and a 30-day acquisition plan. Actual orders and earnings are not guaranteed."],
"ru":["Выбери реальную нишу. Определи три услуги, доказательства навыков, объём результата, лицензии, лимит правок и минимальную цену с учётом расходов.","Через Career Center и биржу подготовь три персонализированных предложения и чек-лист клиента. Используй только реальные одобренные заявки; рассчитай комиссию, отдельно налоги и загрузку. Не выдумывай заказы.","Сдай портфолио студии, прайс, предложения, критерии качества и план поиска клиентов на 30 дней. Заказы и доход не гарантируются."],
"uk":["Обери нішу, три послуги, портфоліо, права, правки та мінімальну ціну.","Через Career Center підготуй три пропозиції й чекліст клієнта. Лише реальні заявки, розрахуй комісію та окремо податки.","Здай портфоліо, прайс, пропозиції та план залучення на 30 днів. Дохід не гарантовано."],
"pl":["Wybierz niszę, trzy usługi, portfolio, prawa, poprawki i cenę minimalną.","W Career Center przygotuj trzy oferty i checklistę klienta. Tylko realne zlecenia; oszacuj prowizję i osobno podatki.","Oddaj portfolio, cennik, oferty i plan pozyskania na 30 dni. Dochód nie jest gwarantowany."]},[["Career Center","/dashboard?module=career"],["Jobs","/dashboard?module=jobs"],["Business Center","/dashboard?module=business"]])
]
def access(token):
    p=student_progress(token)
    if not p.get("access") or p.get("plan")!="elite":
        raise PermissionError("Elite access required")
    return p
def unlocked(p):
    return bool(p.get("owner_preview") or (len(p["lessons"])==45 and all(x["completed"] for x in p["lessons"])))
def catalog(token,lang):
    p=access(token)
    from accounts import authenticate
    from database import transaction
    sid=authenticate(token)
    with transaction() as cur:
        cur.execute("SELECT project,evidence,updated_at,review_status,review_score,review_feedback,revision FROM elite_projects WHERE student_id=%s",(sid,))
        saved={k:{"evidence":e,"updated_at":t.isoformat(),"status":status,"score":score,"feedback":feedback,"revision":rev} for k,e,t,status,score,feedback,rev in cur.fetchall()}
    is_open=unlocked(p)
    return {"unlocked":is_open,"projects":[{"id":k,"title":title,"days":3,**({"steps":steps.get(lang,steps["en"]),"links":links,"submission":saved.get(k)} if is_open else {})} for k,title,steps,links in PROJECTS]}
def save(token,project,evidence):
    p=access(token)
    if not unlocked(p):raise PermissionError("Complete the 45 core lessons first")
    if not isinstance(project,str) or project not in {x[0] for x in PROJECTS} or not isinstance(evidence,str) or not 30<=len(evidence.strip())<=4000:
        raise ValueError("Provide 30–4000 characters of project evidence")
    from accounts import authenticate
    from database import transaction
    sid=authenticate(token)
    with transaction() as cur:
        cur.execute("INSERT INTO elite_projects(student_id,project,evidence) VALUES (%s,%s,%s) ON CONFLICT(student_id,project) DO UPDATE SET evidence=EXCLUDED.evidence,updated_at=now(),revision=elite_projects.revision+1,review_status=\'pending\',review_score=NULL,review_feedback=NULL,reviewed_at=NULL WHERE elite_projects.review_status<>\'approved\'",(sid,project,evidence.strip()))
        if cur.rowcount!=1: raise ValueError("Approved project is locked")
    return {"saved":True,"reviewed":False}

RUBRIC={"brief":25,"quality":25,"evidence":20,"rights":20,"presentation":10}
def validate_review(project,revision,scores,feedback):
    if project not in {x[0] for x in PROJECTS} or type(revision) is not int or revision<1:
        raise ValueError("Invalid project revision")
    if not isinstance(scores,dict) or set(scores)!=set(RUBRIC) or any(type(v) is not int or not 0<=v<=RUBRIC[k] for k,v in scores.items()):
        raise ValueError("Invalid rubric scores")
    if not isinstance(feedback,str) or not 10<=len(feedback.strip())<=4000:
        raise ValueError("Provide 10–4000 characters of feedback")
    total=sum(scores.values())
    return total,"approved" if total>=80 else "revision",feedback.strip()

def review_queue(token,status="pending",offset=0):
    from partners import owner
    from database import transaction
    owner(token)
    if status not in ("pending","revision","approved") or type(offset) is not int or not 0<=offset<=100000:
        raise ValueError("Invalid review filter")
    with transaction() as cur:
        cur.execute("""SELECT p.student_id,p.project,p.evidence,p.revision,p.review_status,p.review_score,p.review_feedback,p.updated_at,s.first_name,s.last_name
            FROM elite_projects p JOIN students s ON s.id=p.student_id
            WHERE p.review_status=%s ORDER BY p.updated_at,p.student_id,p.project LIMIT 31 OFFSET %s""",(status,offset))
        rows=cur.fetchall()
    return {"items":[{"student_id":sid,"project":project,"evidence":evidence,"revision":rev,"status":state,"score":score,"feedback":feedback,"updated_at":updated.isoformat(),"name":" ".join(x for x in (first,last) if x)} for sid,project,evidence,rev,state,score,feedback,updated,first,last in rows[:30]],"next_offset":offset+30 if len(rows)>30 else None,"rubric":RUBRIC}

def review_project(token,student_id,project,revision,scores,feedback):
    from partners import owner
    from database import transaction
    reviewer=owner(token)
    if type(student_id) is not int or student_id<1 or student_id==reviewer:
        raise PermissionError("Independent review required")
    total,status,feedback=validate_review(project,revision,scores,feedback)
    with transaction() as cur:
        cur.execute("""UPDATE elite_projects SET review_status=%s,review_score=%s,review_feedback=%s,reviewed_at=now()
            WHERE student_id=%s AND project=%s AND revision=%s AND review_status='pending'""",(status,total,feedback,student_id,project,revision))
        if cur.rowcount!=1:raise ValueError("Project changed or was already reviewed; refresh the queue")
    return {"status":status,"score":total}
