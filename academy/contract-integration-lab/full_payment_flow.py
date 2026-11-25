"""Consolidated offline payment scenario; never authorize production settlement."""
from solders.transaction import Transaction
from marketplace_split import decode58
from wallet_compatibility import verify_wallet_fixture
from payment_gateway import checkout_preview

def same_message(signed, tx):
    """Compare the full legacy message with its simulated RPC representation."""
    try:
        m=signed.message
        raw=tx["transaction"]["message"]
        h=raw["header"]
        if raw.get("addressTableLookups") or tx["transaction"]["signatures"]!=[str(signed.signatures[0])]:
            return False
        if raw["accountKeys"]!=[str(k) for k in m.account_keys] or raw["recentBlockhash"]!=str(m.recent_blockhash):
            return False
        if (h["numRequiredSignatures"],h["numReadonlySignedAccounts"],h["numReadonlyUnsignedAccounts"]) != (
            m.header.num_required_signatures,m.header.num_readonly_signed_accounts,m.header.num_readonly_unsigned_accounts):
            return False
        instructions=raw["instructions"]
        if len(instructions)!=len(m.instructions):
            return False
        return all(type(r["programIdIndex"]) is int and r["programIdIndex"]==i.program_id_index and
                   all(type(v) is int for v in r["accounts"]) and r["accounts"]==list(i.accounts)
                   and decode58(r["data"])==bytes(i.data) for r,i in zip(instructions,m.instructions))
    except Exception:
        return False

def run_fixture(ledger, invoice, program, source, destination, treasury, signed_bytes, status, tx, receipt):
    """Only record a simulation when the signed message and receipt both match.
    The zero blockhash means this scenario cannot be broadcast as a live payment.
    """
    if not verify_wallet_fixture(invoice,program,source,destination,treasury,signed_bytes):
        raise ValueError("Wallet fixture rejected")
    signed=Transaction.from_bytes(signed_bytes)
    if not same_message(signed,tx):
        raise ValueError("Signed message and RPC fixture differ")
    outcome=ledger.record_fixture(invoice,program,str(signed.signatures[0]),status,tx,receipt)
    quote=checkout_preview(invoice.quote_cents)
    return {"state":outcome,"gross_atomic":str(quote["gross_atomic"]),
            "freelancer_atomic":str(quote["freelancer_atomic"]),"fee_atomic":str(quote["fee_atomic"]),
            "simulation":True,"settlement_authorized":False,"payment_enabled":False}
