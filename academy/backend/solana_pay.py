from urllib.parse import urlencode
from decimal import Decimal
import re
from payment_policy import quote,course_amount

def payment_url(plan,reference,amount_atomic=None):
    if not isinstance(reference,str) or not re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{32,44}",reference):
        raise ValueError("Invalid invoice reference")
    q=quote(plan,"USDC")
    amount=q["amount_atomic"] if amount_atomic is None else amount_atomic
    if type(amount) is not int or amount not in (course_amount(plan),course_amount(plan,True)):
        raise ValueError("Invalid invoice amount")
    params={"amount":str(Decimal(amount)/Decimal(1000000)),"spl-token":q["mint"],"reference":reference,"label":"ZER0LIFE Academy","message":"Academy "+plan}
    return "solana:"+q["recipient"]+"?"+urlencode(params)
# Call only with a unique server-generated reference persisted in an invoice.
