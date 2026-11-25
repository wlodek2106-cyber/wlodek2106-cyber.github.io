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

## Security and performance update
Dashboard response CSP hashes both inline scripts; external scripts only same origin, no inline event handlers or eval permitted. Inline CSS remains necessary for the current UI. Request handling has 16 concurrent slots, 15-second socket inactivity timeout, POST framing checks, bearer length limit and sanitized request logging. Static asset ETag revalidation avoids redundant downloads. Browser smoke exercises CSP at 320/390/1280 px; production Safari, physical devices and load tests still required. Synthetic backup test is not a production restore. No penetration test, no paid security service and no commercial readiness claim.

## Release candidate 1.0
Workspace links now open allow-listed student modules after sign-in; hidden modules remain inaccessible via these links. URL language preference is respected. CI adds a disposable PostgreSQL service, double migration, payment-policy and rollback-only account/checkout/launch integration tests; no production credentials or actual transactions. Existing browser smoke now checks authenticated deep links and denied unpaid learning links. RC is a test candidate, not commercial approval. Freeze feature changes until these checks are green, then verify actual device and operational gates above.

Private curriculum readiness now includes per-language slot counts and a guard against normalized matches to known public exam banks. Original material and owner approval still required; strict mode has not been switched on by this change.

## Marketplace release candidate 2.0 — audit freeze
The cumulative marketplace release includes free client postings, owner moderation, enrolled student applications, course-based recommendation rules, acquisition labels, moderated reputation, private project rooms, in-app notification inbox, application-cohort analytics and manual CRM import. No escrow, tax invoices, payment verification for jobs, external messaging, automated customer acquisition or proven earnings. Separate Freelance application is not synchronized. Previous CI failures included a missing notification mock and a database-driver dependency in standalone analytics tests; fixes are in main. The previous Render build failed; inspect the newest deploy and require a confirmed live commit and both CI jobs green before declaring technical readiness. Private curriculum startup tests are isolated from actual slots; owner-only read-only preflight added. No private curriculum imported and no strict-mode change made by this release. Commercial launch gates above remain open. Freeze feature work until checks pass, then conduct owner-authenticated end-to-end smoke on real devices without synthetic real orders or unapproved transfers.
