"""Offline wallet signing compatibility lab; no wallet connection or broadcast.
The expected message must be built by the trusted invoice adapter, never supplied
by a remote wallet. All fixtures use a zero blockhash and synthetic test keys.
"""
from solders.hash import Hash
from solders.signature import Signature
from solders.transaction import Transaction
from contract_lab import unsigned_preview
from marketplace_boundary import IssuedInvoice

MAX_PACKET = 1232

def verify_wallet_fixture(invoice, program, source, destination, treasury, signed_bytes):
    """Validate exact legacy message and cryptographic signer; not chain settlement."""
    try:
        if not isinstance(invoice, IssuedInvoice):
            return False
        if type(signed_bytes) is not bytes or not 1 <= len(signed_bytes) <= MAX_PACKET:
            return False
        expected = Transaction.from_bytes(unsigned_preview(
            program, invoice.payer, invoice.recipient, invoice.reference,
            invoice.quote_cents, source, destination, treasury))
        signed = Transaction.from_bytes(signed_bytes)
        if bytes(signed) != signed_bytes:
            return False
        if bytes(signed.message) != bytes(expected.message):
            return False
        if signed.message.recent_blockhash != Hash.default():
            return False
        if len(signed.signatures) != 1 or signed.signatures[0] == Signature.default():
            return False
        return signed.signatures[0].verify(signed.message.account_keys[0], bytes(signed.message))
    except Exception:
        return False
