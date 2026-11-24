"""Structured practice briefs, not private examination content or official grading."""
import json
from pathlib import Path
RUBRIC={"brief_alignment":25,"technical_quality":25,"originality":20,"verification_and_rights":20,"presentation":10}
LABELS={
"en":{"brief_alignment":"Brief alignment","technical_quality":"Technical quality","originality":"Originality","verification_and_rights":"Verification and rights","presentation":"Presentation","steps":["Define measurable acceptance criteria and choose free or already available tools.","Create the deliverable and record the inputs, settings and results.","Test against the criteria; record limitations and rights or consent.","Revise once, document the changes, and submit evidence or links to your own files."],"note":"Self-assessment only. A mock, storyboard or local prototype must be clearly labeled. Do not buy tools or upload confidential data."},
"ru":{"brief_alignment":"Соответствие брифу","technical_quality":"Техническое качество","originality":"Оригинальность","verification_and_rights":"Проверка и права","presentation":"Презентация","steps":["Определи измеримые критерии приёмки и выбери бесплатные или уже доступные инструменты.","Создай результат и запиши исходные данные, параметры и итоги.","Проверь критерии, зафиксируй ограничения и права или согласие.","Внеси правки, опиши изменения и отправь подтверждения или ссылки на свои файлы."],"note":"Только самооценка. Имитацию, раскадровку или локальный прототип нужно явно обозначить. Не покупай инструменты и не загружай конфиденциальные данные."},
"uk":{"brief_alignment":"Відповідність брифу","technical_quality":"Технічна якість","originality":"Оригінальність","verification_and_rights":"Перевірка і права","presentation":"Презентація","steps":["Визнач вимірювані критерії приймання й обери безплатні або доступні інструменти.","Створи результат та запиши вхідні дані, параметри й підсумки.","Перевір критерії, зафіксуй обмеження та права чи згоду.","Внеси правки, опиши зміни й надішли підтвердження або посилання на власні файли."],"note":"Лише самооцінка. Імітацію, розкадрування чи прототип потрібно позначити. Не купуй інструменти й не завантажуй конфіденційні дані."},
"pl":{"brief_alignment":"Zgodność z briefem","technical_quality":"Jakość techniczna","originality":"Oryginalność","verification_and_rights":"Weryfikacja i prawa","presentation":"Prezentacja","steps":["Określ mierzalne kryteria akceptacji i wybierz bezpłatne lub dostępne narzędzia.","Utwórz rezultat i zapisz dane wejściowe, ustawienia oraz wyniki.","Sprawdź kryteria, ograniczenia i prawa lub zgodę.","Popraw pracę, opisz zmiany i prześlij dowody lub linki do swoich plików."],"note":"Tylko samoocena. Symulację, storyboard lub prototyp należy oznaczyć. Nie kupuj narzędzi ani nie przesyłaj poufnych danych."}}
def brief(day,lang="en"):
    if type(day) is not int or not 1<=day<=45: raise ValueError("Invalid day")
    if lang not in LABELS: lang="en"
    catalog=json.loads(Path(__file__).with_name("practice_catalog.json").read_text())
    row=catalog[day-1]
    if row["day"]!=day: raise RuntimeError("Invalid practice catalog")
    t=LABELS[lang]
    return {"day":day,"language":lang,"deliverable":row[lang],"steps":t["steps"],"rubric":[{"key":k,"label":t[k],"max":v} for k,v in RUBRIC.items()],"note":t["note"],"self_assessment":True}
def student_brief(token,day,lang):
    from learning import require_lesson
    require_lesson(token,day)
    return brief(day,lang)
