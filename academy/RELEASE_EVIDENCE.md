# ZER0LIFE Academy — release evidence and independent review dossier
Status: laboratory technical candidate, NOT commercial approval. Recorded 2026-11-25. No payment enablement or deployment of the contract.

## Verified evidence
| Scope | Source revision | GitHub Actions | Result |
| --- | --- | --- | --- |
| Rust unit, native bank, SBF build, compiled SBF execution | 8ee28972c466cee33703dd6a53145bde88fc76f7 | https://github.com/wlodek2106-cyber/wlodek2106-cyber.github.io/actions/runs/45519736492 | all four jobs successful |
| Backend and disposable PostgreSQL integration | 580664bb934be4ce656b95ee11459ac79ddc0713 | https://github.com/wlodek2106-cyber/wlodek2106-cyber.github.io/actions/runs/45519895971 | smoke and database jobs successful |
| Offline SDK and cross-language PDA comparison | 009e47e868b864614c5b6930364e6e56056af822 | https://github.com/wlodek2106-cyber/wlodek2106-cyber.github.io/actions/runs/45520198791 | offline-abi successful |
| Render live | 009e47e868b864614c5b6930364e6e56056af822 | deployment dep-dc32u0smds9s73cvpa3g | live observed |
SBF execution job 138890835323 log confirms SHA-256 check of the .so, SBF loaded from the downloaded artifact, compiled execution mode, payment_runtime_replay_validation_and_atomic_rollback passed (1 test, 0 failures). SPL Token processor in this fixture is native. Artifact 14979294008 (binary plus lock and metadata); artifact 14979329721 (execution log); seven-day retention. These are historical references, not a permanent evidence archive. No independent verification of downloaded bytes outside CI. Preserve the artifacts securely before expiry; never include a keypair. No mainnet deployment or real USDC transfer occurred.

## Intended payment invariants
- Fixed Solana SPL USDC mint and existing treasury. Exactly 95% freelancer and 5% platform, integer cents and six token decimals. SOL transaction/rent cost is separate.
- One permanent receipt for the audited program ID, payer and invoice reference. All changes commit or roll back together.
- Invoice issued to one authorized payer and selected freelancer, with immutable quote. Backend must verify exact reference, payer, recipient, cents, mint, fee and receipt before crediting. No payment accepted on receipt alone.
- Course referral discount and influencer commission remain separate from the marketplace platform fee. Never interpret test fixtures or CRM amounts as received funds.

## Open independent review requests
| ID | Threat or gap | Required evidence / acceptance |
| --- | --- | --- |
| S01 | Program identity and upgrade authority | Reviewed pinned program ID, deployment bytecode/hash match, documented upgrade authority custody and change control. No production ID exists yet. |
| S02 | Dependency/toolchain reproducibility | Review Cargo.lock and transitive dependencies, licenses and vulnerabilities; reproduce build from locked audited source. Existing generated lock is only a lab artifact. |
| S03 | Invoice authorization and replay | Threat-model wrong terms consuming a payer's reference, other payer or program, direct SPL transfers, concurrent and late attempts. Establish backend binding and support handling; no duplicate credits. Prototype PDA is not global payment uniqueness. |
| S04 | Runtime limits | Independent tests for malformed instructions/accounts, duplicate keys, frozen and insufficient token accounts, insufficient SOL, prefunded PDA, compute/rent and concurrent requests; test deployed candidate in controlled noncommercial environment. |
| S05 | RPC trust and settlement | Verify network identity, finalized slot/receipt consistency, exact CPI and balance checks, PDA derivation, program ID, duplicate signature constraints, and failure behavior; actual RPC evidence is absent. |
| S06 | Wallet compatibility | Physical mobile/desktop wallets, signing UI shows true recipient and amounts, refusal/cancellation/expired blockhash/retry, insufficient SOL, transaction simulation. No key import or server signing. |
| S07 | Support and recovery | Reconcile canonical receipt PDA rather than reference account for contract path; handle missing/failing RPC, expired/ambiguous requests, mismatch, direct/late/duplicate payment. Never ask to pay again before checking history. |
| S08 | Backend security | Independent authentication/authorization, CSRF/XSS/session, SQL and race testing, rate limits, migration/rollback, backup restore, audit logs and least privilege. |
| S09 | Commercial and privacy | Qualified review of legal entity, tax, consumer disclosures, refunds, marketplace and payment obligations, privacy/retention; no legal clearance implied. |

## Release gates
Each item requires a named reviewer, date, source revision, evidence link, decision and unresolved risks. No self-approval from CI results. All five marketplace_release.BLOCKERS remain in code: wallet_compatibility, onchain_duplicate_prevention, independent_security_review, commercial_legal_review, payment_support_recovery. The existing production gateway is NOT wired to the experimental contract. Keep the release flag unset/false; even setting it true cannot override the hard guard. No automated signing, broadcast, deployment, real payment, paid API or production settings changes.

## Academy owner acceptance
Use verified owner account only; confirm owner ID and role isolation. Import original private learning banks using owner interface and validate all intended language/day slots before enabling strict flags. Test paid/unpaid access, exams, certificate downloads, referral tree, influencer applications and moderation, with synthetic disposable data. Verify physical iOS/Android/desktop login, MFA/recovery, accessibility, actual inference on supported hardware, content licenses, backup restore and support contact. Free resources may sleep or have quota limits. No guarantee of free chain fees or commercial readiness.

## Review record template
Reviewer / role:
Date:
Revision / artifact hash:
Scope and test environment:
Evidence:
Findings (severity, reproduction, mitigation):
Residual risks:
Decision (blocked / approved for next controlled stage):
Follow-up owner:
No secrets or real customer data in public repository.

## Freeze
This dossier is documentation only. Do not rerun expensive SBF jobs solely for documentation, mark unresolved blockers complete, or claim an independent audit was performed. Next code changes should be justified by reviewed findings, then tested again at their exact revision. 

## Consolidated laboratory evidence (2026-11-25)
The isolated integration workflow for V11 completed successfully at b6d9e4a5297f108870b100d73256bcd2bc6e5c26: https://github.com/wlodek2106-cyber/wlodek2106-cyber.github.io/actions/runs/45523387487. It includes 56 synthetic Python tests and Rust/Python PDA comparison. The public preview is a local calculator only; no treasury data or authorization is exposed. Production guards remain unchanged. This entry does not assert live deployment of V12 or independent audit.
