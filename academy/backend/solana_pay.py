from urllib.parse import urlencode
from decimal import Decimal
import re
from payment_policy import quote

def payment_url(plan,reference):
    if not isinstance(reference,str) or not re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{32,44}",reference):
        raise ValueError("Invalid invoice reference")
    q=quote(plan,"USDC")
    params={"amount":str(Decimal(q["amount_atomic"])/Decimal(1000000)),"spl-token":q["mint"],"reference":reference,"label":"ZER0LIFE Academy","message":"Academy "+plan}
    return "solana:"+q["recipient"]+"?"+urlencode(params)
# Call only with a unique server-generated reference persisted in an invoice.
