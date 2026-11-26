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
# Worked examples and self-checks for each localized residency day.
PRACTICE_GUIDES={
  "humans": {
    "en": [
      "Example: a fictional coffee brand ambassador. Write a fixed character card (hair, clothes, palette), generate one portrait, then vary angle while keeping the card and seed/settings. Compare six frames side by side; note identity drift.",
      "Storyboard two clips: cheerful product introduction and calm explanation. Record or synthesize permitted narration; align mouth movement to the audio, inspect at normal and half speed. Repeat the weakest shot.",
      "Acceptance: six references, two 15-second clips, clear synthetic-media label, rights notes and settings sufficient for another creator to repeat the workflow."
    ],
    "ru": [
      "Пример: вымышленный амбассадор кофейни. Зафиксируй причёску, одежду и палитру в паспорте; создай портрет, затем меняй ракурс, сохраняя описание и параметры. Сравни шесть кадров и отметь изменения лица.",
      "Раскадруй два ролика: радостное представление продукта и спокойное объяснение. Запиши разрешённую озвучку, синхронизируй губы, просмотри на обычной и половинной скорости. Переделай самый слабый кадр.",
      "Самопроверка: 6 референсов, 2 ролика по 15 секунд, маркировка AI, журнал прав и настройки, позволяющие другому автору повторить работу."
    ],
    "uk": [
      "Приклад: вигаданий амбасадор кав’ярні. Зафіксуй зачіску, одяг і палітру; створи портрет, змінюй ракурси зі сталим описом. Порівняй шість кадрів.",
      "Розкадруй веселе представлення й спокійне пояснення. Додай дозволений голос, перевір рух губ на звичайній і половинній швидкості. Перероби слабкий кадр.",
      "Самоперевірка: 6 референсів, 2 кліпи по 15 с, маркування ШІ, права та відтворювані налаштування."
    ],
    "pl": [
      "Przykład: fikcyjny ambasador kawiarni. Ustal fryzurę, strój i paletę; stwórz portret, zmieniaj kąty przy stałym opisie. Porównaj sześć kadrów.",
      "Rozpisz pogodną prezentację i spokojne wyjaśnienie. Dodaj dozwolony głos, sprawdź usta w normalnym i połowicznym tempie. Popraw najsłabsze ujęcie.",
      "Samokontrola: 6 referencji, 2 klipy po 15 s, oznaczenie AI, prawa i odtwarzalne ustawienia."
    ]
  },
  "film": {
    "en": [
      "Example: a 60-second café story. Make a six-shot timeline of 10 seconds each, assign a framing and sound cue to each shot. Photograph a static textured object from overlapping angles in consistent light.",
      "Import clips into your editor, assemble the timeline, balance narration and music, and export a preview. Run the local reconstruction on the photos and record settings, result and errors. Compare one enhanced shot with its original.",
      "Acceptance: 60–90 seconds, captions matching speech, no unintended gaps, documented reconstruction outcome, rights log and reproducible export settings. Review full playback before submission."
    ],
    "ru": [
      "Пример: история кофейни на 60 секунд. Разбей её на шесть сцен по 10 секунд, укажи ракурс и звук каждой. Сними неподвижный фактурный объект с разных перекрывающихся ракурсов при одинаковом свете.",
      "Импортируй кадры в редактор, собери таймлайн, выровняй громкость музыки и речи, экспортируй черновик. Запусти локальную реконструкцию фото; запиши настройки, результат и ошибки. Сравни улучшенный кадр с оригиналом.",
      "Самопроверка: 60–90 секунд, совпадение субтитров с речью, отсутствие случайных пауз, отчёт о реконструкции, права и параметры экспорта. Просмотри весь фильм перед сдачей."
    ],
    "uk": [
      "Приклад: історія кав’ярні на 60 с. Створи шість сцен по 10 с із ракурсами та звуком. Сфотографуй нерухомий фактурний об’єкт із перекриттям.",
      "Змонтуй кадри, збалансуй музику й мовлення, експортуй чернетку. Запусти локальну реконструкцію, запиши параметри та помилки. Порівняй покращений кадр з оригіналом.",
      "Самоперевірка: 60–90 с, синхронні субтитри, відсутність випадкових пауз, звіт реконструкції, права та експорт. Переглянь усе відео."
    ],
    "pl": [
      "Przykład: historia kawiarni w 60 s. Rozpisz sześć scen po 10 s z kadrami i dźwiękiem. Fotografuj nieruchomy obiekt z nakładających się ujęć.",
      "Zmontuj materiał, wyrównaj muzykę i mowę, wyeksportuj podgląd. Uruchom rekonstrukcję lokalną, zanotuj ustawienia i błędy. Porównaj ulepszone ujęcie z oryginałem.",
      "Samokontrola: 60–90 s, zsynchronizowane napisy, brak przypadkowych przerw, raport rekonstrukcji, prawa i eksport. Obejrzyj cały film."
    ]
  },
  "agents": {
    "en": [
      "Example: classify fictional customer requests into billing, support and sales. Specify JSON inputs, allowed categories and a draft-only output. Planner assigns, producer drafts, reviewer checks; a person approves any real action.",
      "Run locally with synthetic requests. Test normal requests, missing category, malicious instructions embedded in input and a timeout. Record expected vs actual and revise the prompt or validation when they differ.",
      "Acceptance: six documented cases including failures, no unauthorized external actions, explicit escalation for uncertainty, inputs/outputs and measured runtime."
    ],
    "ru": [
      "Пример: классификация вымышленных заявок клиентов на оплату, поддержку и продажи. Опиши вход JSON, разрешённые категории и выход только в виде черновика. Планировщик распределяет, исполнитель пишет, ревьюер проверяет; реальное действие подтверждает человек.",
      "Запусти локально на вымышленных заявках. Проверь обычные обращения, отсутствие категории, постороннюю команду внутри входных данных и таймаут. Запиши ожидаемый и фактический результат, исправь промпт или валидацию.",
      "Самопроверка: 6 тестов, включая ошибки, отсутствие неразрешённых действий, передача сомнений человеку, описание входов и выходов, измеренное время выполнения."
    ],
    "uk": [
      "Приклад: класифікація вигаданих звернень на оплату, підтримку й продажі. Визнач JSON, категорії та вихід лише як чернетку. Планувальник, виконавець, рев’юер; реальні дії схвалює людина.",
      "Запусти локально на синтетичних даних. Перевір звичайні звернення, відсутню категорію, сторонні команди у вході й таймаут. Порівняй очікуване з фактичним.",
      "Самоперевірка: 6 тестів, зокрема помилки, відсутність несанкціонованих дій, ескалація, входи/виходи й час виконання."
    ],
    "pl": [
      "Przykład: klasyfikacja fikcyjnych zgłoszeń na płatności, wsparcie i sprzedaż. Ustal JSON, kategorie i wynik tylko jako szkic. Planista, wykonawca, recenzent; realne działania zatwierdza człowiek.",
      "Uruchom lokalnie na danych syntetycznych. Sprawdź zwykłe zgłoszenia, brak kategorii, obce polecenia w danych i timeout. Porównaj oczekiwane wyniki z rzeczywistymi.",
      "Samokontrola: 6 testów z błędami, brak nieuprawnionych działań, eskalacja, wejścia/wyjścia i czas."
    ]
  },
  "teacher": {
    "en": [
      "Example: teach percentages. Goal: calculate 15% of 200, explain the formula, distinguish discount from final price. Reference answer: 30 discount, 170 final price. Build a rubric around the reasoning, not only the number.",
      "Ask the local tutor to review 170 (correct final price), 30 (discount only), and an unexplained answer. Require a hint first, then a worked example and a new question. Check the feedback against the reference yourself.",
      "Acceptance: three objectives, a worked example, three tested learner answers, correction evidence and review questions for days 1, 3 and 7."
    ],
    "ru": [
      "Пример: обучение процентам. Цели: вычислить 15% от 200, объяснить формулу, отличить скидку от итоговой цены. Эталон: скидка 30, цена 170. Оценивай ход рассуждений, а не только число.",
      "Попроси локального преподавателя проверить 170 (верная цена), 30 (только скидка) и ответ без объяснения. Сначала подсказка, затем разбор примера и новый вопрос. Самостоятельно сверь обратную связь с эталоном.",
      "Самопроверка: три цели, разобранный пример, три проверенных ответа ученика, журнал исправлений и вопросы для повторения через 1, 3 и 7 дней."
    ],
    "uk": [
      "Приклад: відсотки. Цілі: обчислити 15% від 200, пояснити формулу, відрізнити знижку від ціни. Еталон: знижка 30, ціна 170. Оціни також міркування.",
      "Попроси локального викладача перевірити 170, 30 і відповідь без пояснення. Спочатку підказка, потім розбір та нове питання. Звір відгук з еталоном.",
      "Самоперевірка: три цілі, розібраний приклад, три відповіді, журнал виправлень і повторення через 1, 3 та 7 днів."
    ],
    "pl": [
      "Przykład: procenty. Cele: obliczyć 15% z 200, wyjaśnić wzór i odróżnić rabat od ceny. Wzorzec: rabat 30, cena 170. Oceń także rozumowanie.",
      "Poproś lokalnego tutora o sprawdzenie 170, 30 i odpowiedzi bez wyjaśnienia. Najpierw wskazówka, następnie przykład i nowe pytanie. Porównaj z wzorcem.",
      "Samokontrola: trzy cele, rozwiązany przykład, trzy odpowiedzi, rejestr poprawek i powtórki po 1, 3 i 7 dniach."
    ]
  },
  "business": {
    "en": [
      "Example: a fictional 30-second ad package with one revision. Estimate four hours at 20 units/hour plus 10 units of expenses. With a 5% platform fee the price floor is 90/0.95 = 94.74 units before taxes; round upward.",
      "Build one sample ad using owned assets, a one-page brief and a proposal that states scope, deadline, revision cap and license. Personalize it for real listings only; do not send without approval.",
      "Acceptance: three distinct services, sample portfolio, transparent cost sheet, three proposals, client intake checklist and a weekly outreach plan. Track replies, not invented revenue."
    ],
    "ru": [
      "Пример: рекламный ролик 30 секунд с одной правкой. Четыре часа по 20 у.е. плюс 10 у.е. расходов. При комиссии 5% минимальная цена до налогов: 90/0,95 = 94,74 у.е.; округляй вверх.",
      "Сделай образец рекламы из собственных материалов, бриф на одну страницу и предложение с объёмом, сроком, лимитом правок и лицензией. Персонализируй только под реальные заявки; не отправляй без согласия.",
      "Самопроверка: три разные услуги, образец портфолио, прозрачный расчёт затрат, три предложения, анкета клиента и недельный план поиска. Учитывай реальные ответы, а не выдуманный доход."
    ],
    "uk": [
      "Приклад: реклама 30 с з однією правкою. 4 години по 20 у.о. + 10 витрат. За комісії 5% мінімум до податків: 90/0,95 = 94,74; округли вгору.",
      "Зроби зразок із власних матеріалів, короткий бриф і пропозицію зі строком, обсягом, правками й ліцензією. Лише реальні заявки; не надсилай без згоди.",
      "Самоперевірка: три послуги, портфоліо, розрахунок витрат, три пропозиції, анкета клієнта й тижневий план. Враховуй реальні відповіді."
    ],
    "pl": [
      "Przykład: reklama 30 s z jedną poprawką. 4 godziny po 20 jednostek + 10 kosztów. Przy prowizji 5% minimum przed podatkiem: 90/0,95 = 94,74; zaokrąglij w górę.",
      "Stwórz próbkę z własnych materiałów, krótki brief i ofertę z terminem, zakresem, poprawkami i licencją. Tylko realne zlecenia; nie wysyłaj bez zgody.",
      "Samokontrola: trzy usługi, portfolio, koszty, trzy oferty, ankieta klienta i tygodniowy plan. Zapisuj rzeczywiste odpowiedzi."
    ]
  }
}

def practice_steps(project,steps,lang):
    language=lang if lang in steps else "en"
    return [task+"\n\n"+guide for task,guide in zip(steps[language],PRACTICE_GUIDES[project][language])]

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
    return {"unlocked":is_open,"projects":[{"id":k,"title":title,"days":3,**({"steps":practice_steps(k,steps,lang),"links":links,"submission":saved.get(k)} if is_open else {})} for k,title,steps,links in PROJECTS]}
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
    if not isinstance(project,str) or project not in {x[0] for x in PROJECTS} or type(revision) is not int or revision<1:
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
