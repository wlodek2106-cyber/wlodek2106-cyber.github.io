from decimal import Decimal
import os

TREASURY="57S7TryAMhxRq5sMSyZxTkyCmzT8tPFKfXjzZwvmv5db"
USDC_MINT="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
PRICES={"starter":199,"pro":499,"vip":999}

def course_amount(plan,discount=False):
    if plan not in PRICES or type(discount) is not bool:
        raise ValueError("Invalid price parameters")
    return PRICES[plan]*1000000*(95 if discount else 100)//100

def quote(plan,asset,discount=False):
    if plan not in PRICES or asset not in ("USDC","SOL"):
        raise ValueError("Unsupported plan or asset")
    if os.getenv("ACADEMY_PAYMENTS_ENABLED")!="true":
        raise PermissionError("Payments are closed")
    if asset=="SOL":
        raise PermissionError("SOL requires a verified expiring price quote")
    return {"plan":plan,"asset":asset,"amount_atomic":course_amount(plan,discount),"mint":USDC_MINT,"recipient":TREASURY,"network":"solana-mainnet"}

def validate_amount(expected,received):
    return type(expected) is int and type(received) is int and expected>0 and received==expected
