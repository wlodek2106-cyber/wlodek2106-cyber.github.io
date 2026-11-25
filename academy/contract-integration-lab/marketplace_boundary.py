"""Offline marketplace invoice-to-contract proof boundary.

Inputs model RPC result payloads, but are not independently authenticated.
Never use this lab as a production payment approval or payout route.
"""
from dataclasses import dataclass
from datetime import datetime
from contract_lab import receipt_address, verify_fixture
from marketplace_split import key, signature, split
from payment_policy import TREASURY

@dataclass(frozen=True)
class IssuedInvoice:
    payer: str
    recipient: str
    reference: str
    quote_cents: int
    issued_at: datetime

def verify_finalized_snapshot(invoice, program, sig, status_result, tx, receipt_result):
    """Return a candidate verdict only; no RPC, DB mutation, signing or release."""
    try:
        if not isinstance(invoice, IssuedInvoice):
            return False
        if invoice.issued_at.utcoffset() is None:
            return False
        split(invoice.quote_cents)
        signature(sig)
        for k in (program, invoice.payer, invoice.recipient, invoice.reference):
            key(k)
        if len({program, invoice.payer, invoice.recipient, invoice.reference, TREASURY}) != 5:
            return False
        receipt_address(program, invoice.payer, invoice.reference)
        if len(status_result["value"]) != 1:
            return False
        status = status_result["value"][0]
        slot = tx["slot"]
        status_slot = status["slot"]
        status_context = status_result["context"]["slot"]
        receipt_context = receipt_result["context"]["slot"]
        if any(type(s) is not int or s <= 0 for s in (slot, status_slot, status_context, receipt_context)):
            return False
        if status_slot != slot or min(status_context, receipt_context) < slot:
            return False
        if status["confirmationStatus"] != "finalized" or status["confirmations"] is not None or status["err"] is not None:
            return False
        return verify_fixture(tx, receipt_result["value"], program, sig, invoice.payer,
                              invoice.recipient, invoice.reference, invoice.quote_cents, invoice.issued_at)
    except (KeyError, ValueError, TypeError, IndexError, AttributeError, OverflowError):
        return False
