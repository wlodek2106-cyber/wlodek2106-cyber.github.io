"""Bounded read-only reference reconciliation. Absence is never proof of nonpayment."""
from marketplace_split import key,signature,matches
LIMIT=4

def scan(rpc,payer,recipient,reference,cents,issued_at,recorded=None):
    key(reference)
    result=rpc("getSignaturesForAddress",[reference,{"commitment":"finalized","limit":LIMIT+1}])
    if not isinstance(result,list): raise RuntimeError("Invalid RPC result")
    checked=0; valid=[]; incomplete=len(result)>LIMIT
    seen=set()
    for item in result[:LIMIT]:
        sig=signature(item["signature"])
        if sig in seen: continue
        seen.add(sig)
        if item.get("err") is not None: continue
        if item.get("confirmationStatus")!="finalized":
            incomplete=True
            continue
        tx=rpc("getTransaction",[sig,{"encoding":"json","commitment":"finalized","maxSupportedTransactionVersion":0}])
        if tx is None:
            incomplete=True
            continue
        checked+=1
        if matches(tx,sig,payer,recipient,reference,cents,issued_at):
            valid.append(sig)
    # A recorded signature not returned by this bounded scan is not evidence of a duplicate.
    duplicate=len(valid)>1 or (recorded is not None and any(s!=recorded for s in valid))
    return {"matches":valid,"checked":checked,"incomplete":incomplete,"duplicate_detected":duplicate,
            "recorded_signature":recorded,"status":"duplicate" if duplicate else "recorded" if recorded else "candidate" if len(valid)==1 else "not_found",
            "safe_to_retry":False}
