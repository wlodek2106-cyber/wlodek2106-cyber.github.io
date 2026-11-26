"""Deterministic production worksheet; no model calls or media upload."""
FORMATS={"9:16":(1080,1920),"16:9":(1920,1080),"1:1":(1080,1080)}
DURATIONS={15:(3,5,4,3),30:(5,10,9,6),60:(8,22,20,10)}
FIELDS={"product":120,"audience":120,"benefit":200,"evidence":300,"cta":100,"style":160}
LABELS={
"en":["Hook","Demonstration","Evidence","Call to action","Show the product in context; attract attention without unsupported claims.","Demonstrate the actual use case and maintain visual continuity.","Show only supplied evidence; if none, show a neutral product detail without a claim.","End with the approved call to action; do not invent prices or discounts."],
"ru":["Хук","Демонстрация","Доказательство","Призыв к действию","Покажи продукт в контексте; привлеки внимание без неподтверждённых обещаний.","Продемонстрируй реальный сценарий использования и сохрани визуальную непрерывность.","Используй только предоставленные доказательства; если их нет, покажи нейтральную деталь продукта без обещаний.","Заверши согласованным призывом; не выдумывай цены и скидки."],
"uk":["Хук","Демонстрація","Доказ","Заклик до дії","Покажи продукт у контексті без непідтверджених обіцянок.","Продемонструй реальний сценарій і збережи візуальну сталість.","Використовуй лише надані докази; якщо їх немає, покажи нейтральну деталь.","Заверши узгодженим закликом; не вигадуй ціни чи знижки."],
"pl":["Hak","Demonstracja","Dowód","Wezwanie do działania","Pokaż produkt w kontekście bez niepotwierdzonych obietnic.","Pokaż rzeczywisty sposób użycia i zachowaj spójność.","Użyj tylko dostarczonych dowodów; bez nich pokaż neutralny detal.","Zakończ uzgodnionym wezwaniem, bez wymyślonych cen i rabatów."]}
def plan(data,lang="en"):
    if not isinstance(data,dict) or set(data)!=set(FIELDS)|{"duration","format"}:
        raise ValueError("Invalid production brief")
    clean={}
    for k,limit in FIELDS.items():
        v=data[k]
        if not isinstance(v,str) or len(v)>limit or any(ord(c)<32 and c not in "\n\t" for c in v):
            raise ValueError("Invalid brief field")
        clean[k]=v.strip()
        if k!="evidence" and not clean[k]:raise ValueError("Required brief field")
    duration,fmt=data["duration"],data["format"]
    if type(duration) is not int or duration not in DURATIONS or not isinstance(fmt,str) or fmt not in FORMATS:
        raise ValueError("Invalid duration or format")
    labels=LABELS.get(lang,LABELS["en"])
    cameras=("Wide establishing shot, steady framing","Medium close-up, slow controlled movement","Close-up of genuine product detail","Clean end frame, stable composition")
    scenes=[];start=0
    for i,seconds in enumerate(DURATIONS[duration]):
        action=labels[4+i]
        # Benefits are a supplied brief, not established facts. No testimonial is synthesized.
        claim="Evidence supplied by client: "+clean["evidence"] if i==2 and clean["evidence"] else "No additional factual claims."
        voice=[clean["product"],clean["benefit"],clean["evidence"] or "",clean["cta"]][i]
        prompt="Product reference: "+clean["product"]+". Audience: "+clean["audience"]+". Visual style: "+clean["style"]+". "+cameras[i]+". "+action+" "+claim+" Keep product appearance consistent; no invented logo or endorsements. Aspect ratio "+fmt+"."
        scenes.append({"title":labels[i],"start":start,"end":start+seconds,"seconds":seconds,"action":action,"prompt":prompt,"voice_draft":voice})
        start+=seconds
    return {"brief":clean,"duration":duration,"format":fmt,"width":FORMATS[fmt][0],"height":FORMATS[fmt][1],"scenes":scenes,"draft":True}
def student_plan(token,data,lang):
    from elite_program import access,unlocked
    if not unlocked(access(token)):raise PermissionError("Complete core lessons first")
    return plan(data,lang)
