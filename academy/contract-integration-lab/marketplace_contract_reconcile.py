"""Offline reconciliation experiment. Use only a fixture RPC callback.
No network client, transaction signing, settlement, or automatic retries.
"""
from contract_lab import receipt_address
from marketplace_boundary import verify_finalized_snapshot
from marketplace_split import signature

LIMIT = 4

def reconcile_fixture(rpc, invoice, program, recorded=None):
    """Discover candidate signatures at the canonical receipt PDA, not the reference.
    Neither a missing receipt nor an incomplete scan proves nonpayment.
    """
    valid, seen = [], set()
    checked, incomplete, conflict = 0, False, False
    pda = None
    try:
        if recorded is not None:
            signature(recorded)
        pda, _ = receipt_address(program, invoice.payer, invoice.reference)
        rows = rpc("getSignaturesForAddress", [pda, {"commitment":"finalized","limit":LIMIT+1}])
        if not isinstance(rows, list):
            raise ValueError("Invalid history")
        incomplete = len(rows)>LIMIT
        receipt = rpc("getAccountInfo", [pda, {"commitment":"finalized","encoding":"base64"}])
        if not isinstance(receipt, dict) or receipt.get("value") is None:
            incomplete = True
        for row in rows[:LIMIT]:
            try:
                sig = signature(row["signature"])
                if sig in seen:
                    continue
                seen.add(sig)
                if row["err"] is not None:
                    continue
                if row["confirmationStatus"] != "finalized":
                    incomplete = True
                    continue
                status = rpc("getSignatureStatuses", [[sig], {"searchTransactionHistory":True}])
                tx = rpc("getTransaction", [sig, {"encoding":"json","commitment":"finalized","maxSupportedTransactionVersion":0}])
                if tx is None or type(row["slot"]) is not int or row["slot"] != tx["slot"]:
                    incomplete = True
                    continue
                checked += 1
                if verify_finalized_snapshot(invoice, program, sig, status, tx, receipt):
                    valid.append(sig)
                else:
                    # Unknown or mismatched evidence is not a retry authorization.
                    incomplete = True
            except Exception:
                incomplete = True
    except Exception:
        incomplete = True
    conflict = len(valid)>1 or (recorded is not None and any(s!=recorded for s in valid))
    if conflict:
        state = "conflict"
    elif recorded is not None:
        state = "recorded" if recorded in valid and not incomplete else "recorded_unverified"
    elif incomplete:
        state = "incomplete"
    elif len(valid)==1:
        state = "candidate"
    else:
        state = "not_found"
    return {"pda":pda,"matches":valid,"checked":checked,"incomplete":incomplete,
            "conflict":conflict,"state":state,"recorded_signature":recorded,
            "safe_to_retry":False,"settlement_authorized":False}
