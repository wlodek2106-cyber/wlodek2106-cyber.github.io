"""Generate a local, deliberately non-payable Marketplace checkout preview.
No wallet, network calls, real addresses, personal data, or transaction requests.
"""
import argparse
from io import BytesIO
from pathlib import Path
import qrcode
from qrcode.image.svg import SvgPathImage
from marketplace_split import split

def display_atomic(value):
    whole, fractional = divmod(value, 1000000)
    return f"{whole}.{fractional:06d}".rstrip("0").rstrip(".")

def checkout_preview(cents):
    amounts = split(cents)
    payload = ("ZER0LIFE-LAB-NOT-PAYABLE:v1:"
               f"{amounts['gross_atomic']}:{amounts['freelancer_atomic']}:{amounts['fee_atomic']}")
    return {**amounts, "gross":display_atomic(amounts["gross_atomic"]),
            "freelancer":display_atomic(amounts["freelancer_atomic"]),
            "fee":display_atomic(amounts["fee_atomic"]), "qr_payload":payload,
            "asset":"USDC","network_label":"Solana (planned)","payment_enabled":False}

def make_qr(cents):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=4)
    qr.add_data(checkout_preview(cents)["qr_payload"], optimize=0)
    qr.make(fit=True)
    return qr

def render_checkout(cents):
    from base64 import b64encode
    p = checkout_preview(cents)
    buffer = BytesIO()
    make_qr(cents).make_image(image_factory=SvgPathImage).save(buffer)
    encoded = b64encode(buffer.getvalue()).decode("ascii")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>ZER0LIFE | Marketplace payment lab</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#0d1020;color:#f4f5ff;font:16px/1.5 system-ui}}
main{{max-width:520px;margin:32px auto;padding:24px}}article{{background:#181d32;border:1px solid #383d58;padding:24px;border-radius:22px}}
h1{{margin:8px 0;font-size:32px}}p{{color:#cbd0e4}}img{{display:block;width:210px;max-width:100%;margin:16px auto;background:white;padding:8px}}
dl div{{display:flex;justify-content:space-between;gap:12px;border-bottom:1px solid #383d58;padding:10px 0}}dd{{margin:0;text-align:right;overflow-wrap:anywhere}}
button{{width:100%;padding:14px;border:0;border-radius:10px;background:#383d58;color:#f4f5ff;font:inherit}}
</style></head><body><main><header>ZER0LIFE / MARKETPLACE LAB</header>
<article><h1>{p['gross']} USDC</h1><p>TEST ONLY — NO REAL PAYMENTS. Do not send funds.</p>
<img src="data:image/svg+xml;base64,{encoded}" alt="Non-payable laboratory QR">
<p>The QR contains a demonstration amount breakdown, not a wallet address or payment link.</p>
<dl><div><dt>Freelancer (95%)</dt><dd>{p['freelancer']} USDC</dd></div>
<div><dt>Academy (5%)</dt><dd>{p['fee']} USDC</dd></div>
<div><dt>Network</dt><dd>{p['network_label']}</dd></div></dl>
<button type="button" disabled>Payment disabled</button></article>
<p>No wallet connection, no transfers, no payment confirmation.</p></main></body></html>"""

if __name__=="__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cents", type=int, default=100000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(render_checkout(args.cents),encoding="utf-8")
