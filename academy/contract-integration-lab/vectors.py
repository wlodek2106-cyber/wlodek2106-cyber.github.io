"""Fixed synthetic vectors shared with the actual Rust contract implementation."""
from solders.pubkey import Pubkey
from contract_lab import receipt_address

for p,a,r in [(11,12,13),(11,12,14),(11,14,13),(14,12,13),(51,61,71)]:
    address,bump=receipt_address(*(str(Pubkey.from_bytes(bytes([v])*32)) for v in (p,a,r)))
    print(f"{p},{a},{r},{address},{bump}")
