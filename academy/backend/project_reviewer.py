"""Evidence checklist and local AI review prompt; never grades unseen files."""
from practice_lab import brief

FIELDS=("goal","deliverable","process","verification","rights","revision")
LABELS={
"en":["Goal and audience","Result and evidence","Tools and workflow","Tests and limitations","Rights and consent","Revisions and next steps"],
"ru":["Цель и аудитория","Результат и доказательства","Инструменты и процесс","Тесты и ограничения","Права и согласие","Правки и дальнейшие шаги"],
"uk":["Мета й аудиторія","Результат і докази","Інструменти й процес","Тести й обмеження","Права та згода","Правки й наступні кроки"],
"pl":["Cel i odbiorcy","Rezultat i dowody","Narzędzia i proces","Testy i ograniczenia","Prawa i zgoda","Poprawki i kolejne kroki"]}
ADVICE={
"en":["Describe the intended audience and a measurable success criterion.","Provide the actual output or a description with a link you control.","Record tools, model versions, inputs and settings.","Report at least one test, its outcome and limitations.","Document permission, licenses and any synthetic-content disclosure.","Compare before and after and identify the next improvement."],
"ru":["Опиши аудиторию и измеримый критерий успеха.","Приложи описание результата и ссылку на собственный файл.","Укажи инструменты, версии моделей, входные данные и настройки.","Опиши хотя бы один тест, его результат и ограничения.","Зафиксируй разрешения, лицензии и маркировку AI-контента.","Сравни до и после и назови следующее улучшение."],
"uk":["Опиши аудиторію та вимірюваний критерій успіху.","Додай опис результату й посилання на власний файл.","Вкажи інструменти, версії моделей, вхідні дані й налаштування.","Опиши хоча б один тест, результат та обмеження.","Зафіксуй дозволи, ліцензії та маркування ШІ-контенту.","Порівняй до та після й назви наступне покращення."],
"pl":["Opisz odbiorców i mierzalne kryterium sukcesu.","Dodaj opis rezultatu i link do własnego pliku.","Zapisz narzędzia, wersje modeli, dane wejściowe i ustawienia.","Opisz co najmniej jeden test, wynik i ograniczenia.","Udokumentuj zgody, licencje i oznaczenie treści AI.","Porównaj przed i po oraz wskaż kolejne ulepszenie."]}
def review(day,fields,lang="en"):
    if lang not in LABELS: lang="en"
    b=brief(day,lang)
    if not isinstance(fields,dict) or set(fields)!=set(FIELDS) or any(not isinstance(v,str) or len(v)>1200 for v in fields.values()):
        raise ValueError("Invalid evidence fields")
    data={k:fields[k].strip() for k in FIELDS}
    checks=[{"key":k,"label":LABELS[lang][i],"provided":bool(data[k]),"suggestion":ADVICE[lang][i]} for i,k in enumerate(FIELDS)]
    case="\n\n".join(LABELS[lang][i]+":\n"+(data[k] or "—") for i,k in enumerate(FIELDS))
    return {"day":day,"language":lang,"deliverable":b["deliverable"],"checks":checks,"provided_count":sum(x["provided"] for x in checks),"total":6,"case_study":case,"engine":"presence_check_only","official_grade":False}

def student_review(token,project,fields,lang):
    from accounts import authenticate
    from database import transaction
    sid=authenticate(token)
    if sid is None: raise PermissionError("Authentication required")
    if type(project) is not int or project<1 or project>9223372036854775807: raise ValueError("Invalid project")
    with transaction() as cur:
        cur.execute("""SELECT p.lesson,p.submission FROM project_submissions p JOIN enrollments e ON e.id=p.enrollment_id
          WHERE p.id=%s AND e.student_id=%s AND e.paid_at IS NOT NULL""",(project,sid))
        row=cur.fetchone()
    if not row: raise PermissionError("Project not found")
    result=review(row[0],fields,lang)
    result["project_id"]=project
    return result


def draft_review(token,day,fields,lang):
    """Review a draft only for an entitled lesson; no writes or AI provider calls."""
    from learning import require_lesson
    if type(day) is not int or not 1<=day<=45 or not isinstance(lang,str) or lang not in LABELS:
        raise ValueError("Invalid lesson or language")
    require_lesson(token,day)
    result=review(day,fields,lang)
    result["ready_for_submission"]=result["provided_count"]==result["total"]
    return result
