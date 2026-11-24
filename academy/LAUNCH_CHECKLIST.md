# Launch readiness / release checks

Automated: unit tests; rollback-only DB integration at Render startup; HTTP boundary and browser smoke on public GitHub Actions. Browser uses a mock API: no production accounts, real payments or credentials. Test success is not commercial readiness.

Remaining launch gates:
- Confirm owner account ID from authenticated dashboard; enable only the verified owner.
- Replace public legacy lesson/exam material with original private banks, verify coverage, then enable strict mode.
- Review actual customer terms, privacy, refunds, legal identity, applicable tax/consumer obligations before accepting commercial customers.
- Real payment and payout: manually authorized finalized USDC transaction, exact reference and amount, confirm enrollment, idempotency, wallet receipt, partner accounting; no transfer in automated tests. Multiple late-paid invoices require manual reconciliation. Never advise a customer to pay again without checking the old invoice.
- Test sign-in including 2FA and recovery codes in physical browsers, PWA and native previews; native MFA unsupported.
- Confirm model inference on supported devices, and review content quality and licenses.
- Verify backup/restore, operational support, and account recovery. No email verification/reset currently.
- Confirm actual UI PDF downloads and language variants. Native store release/signing not included.
- Free-tier resources can sleep or have quota limits; no paid services enabled.

Public dashboard has registration and checkout enabled for testing, not verified commercial launch.
