"""Fail-closed production release guard. Configuration alone cannot approve release."""
import os
# Each blocker must be resolved and reviewed in a future code release.
BLOCKERS=("wallet_compatibility","onchain_duplicate_prevention","independent_security_review","commercial_legal_review","payment_support_recovery")
def readiness():
    requested=os.getenv("ACADEMY_MARKETPLACE_PAYMENTS_ENABLED")=="true"
    return {"requested":requested,"enabled":requested and not BLOCKERS,"blockers":list(BLOCKERS),"live_payment_tested":False}
def enabled():
    return readiness()["enabled"]
