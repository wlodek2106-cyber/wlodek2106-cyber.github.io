"""Offline affiliate content templates and hypothetical commission calculator."""
from payment_policy import PRICES
from urllib.parse import urlencode
from referrals import normalize
BASE="https://zer0life-academy.onrender.com/dashboard"
COPY={
"en":{
"disclosure":"Advertisement / affiliate link. I may earn a commission from your purchase.",
"post":"Build practical AI skills with ZER0LIFE Academy: image creation, video workflows, prompt engineering and portfolio projects. Choose from four tiers, from 30-day Starter to Elite with 45 core days and five production projects. Check the curriculum and device requirements before enrolling.",
"short":"Want to learn AI creation? Explore ZER0LIFE Academy, its practical lessons and local AI tools.",
"video":"15-second concept: 0–4s: blank canvas becomes an AI workflow. 4–10s: show real examples of your own work. 10–15s: display the academy name and invite viewers to explore the curriculum. Add a clearly visible affiliate disclosure.",
"email":"Explore ZER0LIFE Academy if you are interested in learning AI creative workflows. Review the course content, pricing and requirements before choosing a plan. No income or job outcome is guaranteed."},
"ru":{
"disclosure":"Реклама / партнёрская ссылка. Я могу получить комиссию от вашей покупки.",
"post":"Освой практические навыки AI с ZER0LIFE Academy: изображения, видео, промпт-инжиниринг и учебные проекты для портфолио. Выбирай из четырёх уровней: от 30-дневного Starter до Elite с 45 основными уроками и пятью проектами. Перед покупкой проверь программу и требования к устройству.",
"short":"Хочешь научиться создавать AI-контент? Изучи программу ZER0LIFE Academy и локальные AI-инструменты.",
"video":"Концепция на 15 секунд: 0–4 с — пустой холст превращается в AI-процесс. 4–10 с — покажи реальные примеры своих работ. 10–15 с — название академии и приглашение изучить программу. Добавь заметную пометку о рекламе.",
"email":"Если тебе интересны творческие AI-процессы, изучи ZER0LIFE Academy. Проверь программу, цены и требования перед выбором тарифа. Доход и трудоустройство не гарантируются."},
"uk":{
"disclosure":"Реклама / партнерське посилання. Я можу отримати комісію від вашої покупки.",
"post":"Опануй практичні навички ШІ із ZER0LIFE Academy: зображення, відео, промпт-інжиніринг і навчальні проєкти для портфоліо. Обирай один із чотирьох рівнів: від Starter до Elite з 45 уроками та п’ятьма проєктами. Перед покупкою перевір програму та вимоги до пристрою.",
"short":"Хочеш створювати ШІ-контент? Ознайомся з програмою ZER0LIFE Academy та локальними інструментами.",
"video":"Концепція на 15 секунд: 0–4 с — порожнє полотно стає ШІ-процесом. 4–10 с — покажи реальні приклади власних робіт. 10–15 с — назва академії та запрошення вивчити програму. Додай помітне маркування реклами.",
"email":"Якщо тебе цікавлять творчі ШІ-процеси, ознайомся із ZER0LIFE Academy. Перевір програму, ціни та вимоги. Дохід і працевлаштування не гарантуються."},
"pl":{
"disclosure":"Reklama / link afiliacyjny. Mogę otrzymać prowizję od zakupu.",
"post":"Rozwijaj praktyczne umiejętności AI z ZER0LIFE Academy: obrazy, wideo, inżynieria promptów i projekty do portfolio. Wybierz jeden z czterech poziomów, od Starter do Elite z 45 lekcjami i pięcioma projektami. Przed zakupem sprawdź program i wymagania sprzętowe.",
"short":"Chcesz tworzyć treści AI? Poznaj program ZER0LIFE Academy i lokalne narzędzia AI.",
"video":"Koncepcja 15 s: 0–4 s — puste płótno zmienia się w proces AI. 4–10 s — pokaż prawdziwe przykłady własnych prac. 10–15 s — nazwa akademii i zaproszenie do poznania programu. Dodaj widoczne oznaczenie reklamy.",
"email":"Jeśli interesują Cię kreatywne procesy AI, poznaj ZER0LIFE Academy. Przed wyborem sprawdź program, ceny i wymagania. Dochód ani zatrudnienie nie są gwarantowane."}}
def materials(code,lang):
    if lang not in COPY or not normalize(code): raise ValueError("Invalid campaign")
    link=BASE+"?"+urlencode({"ref":code})
    t=COPY[lang]
    return {"link":link,"materials":[{"type":k,"text":t["disclosure"]+"\n\n"+t[k]+"\n\n"+link} for k in ("post","short","video","email")],"prices":PRICES,"commission_percent":30}
def projection(counts):
    if not isinstance(counts,dict) or set(counts)!=set(PRICES): raise ValueError("Invalid counts")
    if any(type(n) is not int or not 0<=n<=10000 for n in counts.values()): raise ValueError("Invalid counts")
    total=sum(PRICES[p]*counts[p]*1000000 for p in PRICES)
    return {"gross_atomic":total,"commission_atomic":total*30//100,"hypothetical":True}
def kit(token,lang):
    from partners import dashboard
    d=dashboard(token)
    if d["status"]!="approved": raise PermissionError("Approved partner required")
    return materials(d["code"],lang)
