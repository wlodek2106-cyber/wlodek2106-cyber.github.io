"""Commercial quote drafts only. No tax invoice issuance or payment execution."""
from student_business import clean,ident,identity
from datetime import date
from io import BytesIO
import base64,os
from xml.sax.saxutils import escape

WORDS={
"en":["Commercial proposal","DRAFT · Not a tax invoice or proof of payment","Provider","Client","Project","Scope and deliverables","Delivery date","Payment and revision terms","Proposed price","Recorded advances","Remaining amount","USD · Taxes not calculated","Review applicable tax, legal and invoicing requirements before sending."],
"ru":["Коммерческое предложение","ЧЕРНОВИК · Не налоговый счёт и не подтверждение оплаты","Исполнитель","Клиент","Проект","Объём работ и результат","Срок выполнения","Условия оплаты и правок","Предлагаемая стоимость","Учтённые авансы","Остаток к оплате","USD · Налоги не рассчитаны","Перед отправкой проверь применимые налоговые, правовые и платёжные требования."],
"uk":["Комерційна пропозиція","ЧЕРНЕТКА · Не податковий рахунок і не доказ оплати","Виконавець","Клієнт","Проєкт","Обсяг робіт і результат","Термін виконання","Умови оплати та правок","Запропонована вартість","Враховані аванси","Залишок до оплати","USD · Податки не розраховані","Перед надсиланням перевір застосовні податкові, правові та платіжні вимоги."],
"pl":["Oferta handlowa","SZKIC · Nie jest fakturą podatkową ani dowodem zapłaty","Wykonawca","Klient","Projekt","Zakres i rezultaty","Termin realizacji","Warunki płatności i poprawek","Proponowana cena","Zarejestrowane zaliczki","Pozostało do zapłaty","USD · Podatki nie zostały obliczone","Przed wysłaniem sprawdź odpowiednie wymogi podatkowe, prawne i dotyczące faktur."]}
def money(cents):
    return f"{cents//100:,}.{cents%100:02d} USD"
def record(cur,sid,b):
    order=ident(b["order"])
    lang=b.get("lang","en")
    if lang not in WORDS: raise ValueError("Invalid language")
    provider=clean(b["provider"],200,True)
    scope=clean(b["scope"],3000,True)
    terms=clean(b["terms"],2000,True)
    cur.execute("""SELECT o.title,o.due,o.agreed_cents,o.received_cents,c.name,o.status
        FROM business_orders o JOIN business_clients c ON c.id=o.client_id AND c.student_id=o.student_id
        WHERE o.id=%s AND o.student_id=%s""",(order,sid))
    row=cur.fetchone()
    if not row: raise PermissionError("Order unavailable")
    title,due,agreed,received,client,status=row
    if status=="cancelled": raise ValueError("Order cancelled")
    return {"order":order,"lang":lang,"provider":provider,"scope":scope,"terms":terms,"title":title,
            "due":due.isoformat() if due else "—","agreed":agreed,"received":received,"remaining":agreed-received,"client":client,"date":date.today().isoformat()}
def render(d):
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    font="AcademyQuote"
    pdfmetrics.registerFont(TTFont(font,os.getenv("ACADEMY_CERT_FONT","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")))
    w=WORDS[d["lang"]]
    buf=BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=44,rightMargin=44,topMargin=48,bottomMargin=48,title=w[0])
    base=ParagraphStyle("base",fontName=font,fontSize=10,leading=15,textColor=colors.HexColor("#202636"),splitLongWords=1)
    title=ParagraphStyle("title",parent=base,fontSize=24,leading=30,spaceAfter=12)
    label=ParagraphStyle("label",parent=base,fontSize=10,textColor=colors.HexColor("#565b78"),spaceBefore=10,spaceAfter=3)
    warning=ParagraphStyle("warning",parent=base,fontSize=9,leading=13,textColor=colors.HexColor("#8a4622"),spaceAfter=12)
    def para(v,style=base):
        return Paragraph(escape(str(v)).replace("\n","<br/>"),style)
    story=[para(w[0],title),para(w[1],warning),para("Ref. "+str(d["order"])+" · "+d["date"])]
    for i,k in ((2,"provider"),(3,"client"),(4,"title"),(5,"scope"),(6,"due"),(7,"terms")):
        story.extend([para(w[i],label),para(d[k])])
    story.append(Spacer(1,18))
    table=Table([[para(w[i]),para(money(d[k]))] for i,k in ((8,"agreed"),(9,"received"),(10,"remaining"))],colWidths=[330,170])
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f0f1f7")),("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#dce0f1")),("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10)]))
    story.extend([table,Spacer(1,12),para(w[11],label),para(w[12],warning)])
    def footer(c,doc):
        c.setFont(font,8);c.setFillColor(colors.HexColor("#565b78"));c.drawString(44,25,"ZER0LIFE Academy · Document Studio");c.drawRightString(A4[0]-44,25,str(doc.page))
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return buf.getvalue()
def generate(token,body):
    from database import transaction
    sid=identity(token)
    with transaction() as cur: d=record(cur,sid,body)
    return {"pdf_base64":base64.b64encode(render(d)).decode("ascii"),"filename":"proposal-"+str(d["order"])+".pdf","draft":True}
