"""Entitlement-aware, zero-cost agent playbooks. No autonomous execution or provider calls."""
ROLES=["teacher","code","design","video","marketing","project"]
STEPS={
  "en": [
    [
      "Explain the lesson concept using an original example.",
      "Ask one formative question and wait for the learner's reasoning.",
      "Give feedback and propose a short exercise."
    ],
    [
      "Define inputs, outputs and acceptance tests.",
      "Write a minimal implementation or identify defects in pasted code.",
      "Suggest reproducible tests; distinguish proposed from executed tests."
    ],
    [
      "Define audience, visual hierarchy and style.",
      "Draft two original concepts and select measurable criteria.",
      "Review accessibility, rights and export requirements."
    ],
    [
      "Draft a storyboard with shot durations and continuity.",
      "Choose sound, motion and production requirements.",
      "Review pacing, permissions and delivery format."
    ],
    [
      "Define audience, offer and measurable campaign goal.",
      "Draft truthful copy and two test variants.",
      "Plan measurement without inventing performance or customer claims."
    ],
    [
      "Compare the actual evidence with the assignment.",
      "Identify evidence gaps, limitations and rights concerns.",
      "Prioritize three revisions; do not assign an official grade."
    ]
  ],
  "ru": [
    [
      "Объясни понятие урока на оригинальном примере.",
      "Задай один учебный вопрос и дождись рассуждения студента.",
      "Дай обратную связь и предложи короткое упражнение."
    ],
    [
      "Определи входные данные, результат и тесты приёмки.",
      "Напиши минимальную реализацию или найди ошибки в предоставленном коде.",
      "Предложи воспроизводимые тесты; не выдавай предложенные тесты за выполненные."
    ],
    [
      "Определи аудиторию, визуальную иерархию и стиль.",
      "Предложи две оригинальные концепции и критерии выбора.",
      "Проверь доступность, права и требования к экспорту."
    ],
    [
      "Составь раскадровку с длительностью кадров и последовательностью.",
      "Определи звук, движение и требования к производству.",
      "Проверь темп, разрешения и формат сдачи."
    ],
    [
      "Определи аудиторию, предложение и измеримую цель кампании.",
      "Подготовь правдивый текст и два варианта для тестирования.",
      "Предложи измерение результатов без выдуманных показателей или отзывов."
    ],
    [
      "Сопоставь реальные материалы с заданием.",
      "Найди недостающие доказательства, ограничения и вопросы прав.",
      "Назови три приоритетные правки; не выставляй официальную оценку."
    ]
  ],
  "uk": [
    [
      "Поясни поняття уроку на оригінальному прикладі.",
      "Постав одне навчальне запитання й дочекайся міркувань студента.",
      "Дай відгук і запропонуй коротку вправу."
    ],
    [
      "Визнач вхідні дані, результат і тести приймання.",
      "Напиши мінімальну реалізацію або знайди дефекти в наданому коді.",
      "Запропонуй відтворювані тести; не стверджуй, що виконав їх."
    ],
    [
      "Визнач аудиторію, візуальну ієрархію та стиль.",
      "Запропонуй дві оригінальні концепції й критерії вибору.",
      "Перевір доступність, права та вимоги експорту."
    ],
    [
      "Склади розкадрування з тривалістю кадрів і послідовністю.",
      "Визнач звук, рух і виробничі вимоги.",
      "Перевір темп, дозволи й формат здачі."
    ],
    [
      "Визнач аудиторію, пропозицію та вимірювану мету.",
      "Підготуй правдивий текст і два варіанти для тестування.",
      "Запропонуй вимірювання без вигаданих результатів або відгуків."
    ],
    [
      "Зістав фактичні матеріали із завданням.",
      "Визнач прогалини в доказах, обмеження та питання прав.",
      "Назви три пріоритетні правки; не виставляй офіційну оцінку."
    ]
  ],
  "pl": [
    [
      "Wyjaśnij pojęcie z lekcji na oryginalnym przykładzie.",
      "Zadaj pytanie i zaczekaj na rozumowanie ucznia.",
      "Przekaż informację zwrotną i zaproponuj krótkie ćwiczenie."
    ],
    [
      "Określ dane wejściowe, wynik i testy akceptacji.",
      "Napisz minimalną implementację lub znajdź błędy w podanym kodzie.",
      "Zaproponuj odtwarzalne testy; nie twierdź, że je wykonałeś."
    ],
    [
      "Określ odbiorców, hierarchię wizualną i styl.",
      "Zaproponuj dwie oryginalne koncepcje i kryteria wyboru.",
      "Sprawdź dostępność, prawa i wymagania eksportu."
    ],
    [
      "Przygotuj storyboard z czasami ujęć i ciągłością.",
      "Określ dźwięk, ruch i wymagania produkcji.",
      "Sprawdź tempo, zgody i format dostawy."
    ],
    [
      "Określ odbiorców, ofertę i mierzalny cel.",
      "Przygotuj rzetelny tekst i dwa warianty testowe.",
      "Zaplanuj pomiary bez wymyślania wyników i opinii."
    ],
    [
      "Porównaj faktyczne materiały z zadaniem.",
      "Wskaż braki dowodów, ograniczenia i kwestie praw.",
      "Wskaż trzy najważniejsze poprawki; bez oficjalnej oceny."
    ]
  ]
}
def playbook(day,role,lang,brief):
    if not isinstance(role,str) or role not in ROLES or not isinstance(lang,str) or lang not in STEPS:
        raise ValueError("Invalid agent or language")
    return {"day":day,"role":role,"language":lang,"deliverable":brief["deliverable"],
            "steps":STEPS[lang][ROLES.index(role)],"engine":"guided_rules",
            "automatic_execution":False,"official_grade":False,"external_request":False}

def student_playbook(token,day,role,lang):
    if type(day) is not int or not 1<=day<=45 or not isinstance(role,str) or role not in ROLES or not isinstance(lang,str) or lang not in STEPS:
        raise ValueError("Invalid lesson, agent or language")
    from practice_lab import student_brief
    return playbook(day,role,lang,student_brief(token,day,lang))

def team_plan(token,day,roles,lang):
    """Export a bounded sequential team, with no model invocation."""
    if type(day) is not int or not 1<=day<=45 or not isinstance(lang,str) or lang not in STEPS:
        raise ValueError("Invalid lesson or language")
    if not isinstance(roles,list) or not 1<=len(roles)<=6 or any(not isinstance(r,str) or r not in ROLES for r in roles) or len(set(roles))!=len(roles):
        raise ValueError("Select one to six distinct roles")
    from practice_lab import student_brief
    brief=student_brief(token,day,lang)
    return {"schema":"zer0life-agent-team-v1","day":day,"language":lang,"deliverable":brief["deliverable"],
            "stages":[{"role":r,"steps":STEPS[lang][ROLES.index(r)],"depends_on":i if i else None,"stage":i+1} for i,r in enumerate(roles)],
            "automatic_execution":False,"external_request":False,"human_review_required":True}

PROJECT_LABELS={
 "en":["Teacher","Developer","Designer","Producer","Marketing","Reviewer","Human review and approval"],
 "ru":["Преподаватель","Разработчик","Дизайнер","Продюсер","Маркетолог","Ревьюер","Проверка и утверждение человеком"],
 "uk":["Викладач","Розробник","Дизайнер","Продюсер","Маркетолог","Рев’юер","Перевірка та затвердження людиною"],
 "pl":["Nauczyciel","Programista","Projektant","Producent","Marketing","Recenzent","Weryfikacja i zatwierdzenie przez człowieka"]
}

def project_payload(plan,title,kind,custom_brief="",due=""):
    """Build a private checklist from a server-authorized team plan."""
    from student_business import clean
    title=clean(title,160,True)
    if not isinstance(kind,str) or kind not in ("image","video","advertising","animation","audio","product"):
        raise ValueError("Invalid project type")
    custom=clean(custom_brief,1600)
    brief=clean(plan["deliverable"]+("\n\n"+custom if custom else ""),2000,True)
    tasks=[]
    labels=PROJECT_LABELS[plan["language"]]
    for stage in plan["stages"]:
        label=labels[ROLES.index(stage["role"])]
        for i,step in enumerate(stage["steps"],1):
            task=clean(f'{stage["stage"]}.{i} {label}: {step}',120,True)
            tasks.append({"title":task,"done":False})
    tasks.append({"title":labels[6],"done":False})
    return {"title":title,"kind":kind,"brief":brief,"due":due,"tasks":tasks,"completed":[],"notes":"","materials":""}

def create_team_project(token,body):
    # Recompute authorized lesson and steps; never trust client-provided instructions or IDs.
    plan=team_plan(token,body.get("day"),body.get("roles"),body.get("lang","en"))
    payload=project_payload(plan,body.get("title"),body.get("kind"),body.get("custom_brief",""),body.get("due",""))
    from creative_workflow import dispatch
    result=dispatch(token,"save",payload)
    return {"id":result["id"],"tasks":len(payload["tasks"]),"automatic_execution":False}
