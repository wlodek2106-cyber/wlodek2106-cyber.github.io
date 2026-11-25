"""Read-only launch snapshot. No automatic approval or setting change."""
from marketplace_release import readiness

def summarize(diagnostics, inventory):
    languages={}
    for lang in ("en","ru","uk","pl"):
        languages[lang]={kind:inventory["coverage"][lang][kind]["count"] for kind in ("lesson","exam")}
    count=sum(sum(x.values()) for x in languages.values())
    strict={kind:bool(inventory["strict"][kind]) for kind in ("lesson","exam")}
    strict_ready={kind:bool(inventory["strict_ready"][kind]) for kind in ("lesson","exam")}
    release=readiness()
    return {
        "curriculum":{"languages":languages,"slots":count,"target":360,
            "all_languages_covered":count==360,"strict":strict,"strict_ready":strict_ready},
        "database_checks_pass":diagnostics["database_checks_pass"],
        "open_payment_tickets":diagnostics["counts"]["open_payment_tickets"],
        "open_privacy_requests":diagnostics["counts"]["open_privacy_requests"],
        "unsettled_issued":diagnostics["counts"]["split_pending_issued"],
        "marketplace_payments":release,
        "manual_checks":["owner_identity","content_quality_licenses","physical_devices_mfa","production_backup_restore","commercial_legal_review","independent_security_review","authorized_payment_test"],
        "commercial_approved":False
    }
