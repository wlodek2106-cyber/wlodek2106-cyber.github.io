# Contract integration lab — offline only

This experimental SDK adapter is not imported by the production server. The separate CI job uses Solders 0.29.0 (pinned direct dependency, not an audited lock). It derives the receipt address using the same seed bytes as Rust, builds an unsigned zero-blockhash legacy message with eight ordered ABI accounts, and supplies the derived PDA to the existing offline receipt matcher. Synthetic fixtures check address separation, off-curve derivation, correct account order, instruction data, absence of signatures and invalid input rejection.

No network access by the code, no signing, real payment or deployment. The SDK is installed in CI only, never in the Render requirements. There is no approved deployed program ID. The derived address is bound to program, payer and invoice reference. Before production: cross-language fixed vectors, audited dependency lock and program identity, actual SBF runtime pass, independent security review, wallet compatibility, finalized RPC evidence, support and legal review. All existing release blockers remain.

## Cross-language vectors
Fixed YAML syntax for the binary-only SDK install command. The lab workflow compares five deterministic synthetic payer/program/reference tuples using the actual Rust contract's `receipt_address` function and Python Solders SDK. Both the PDA and bump must agree byte-for-byte before the comparison passes. The separate Rust runner imports the real prototype with no-entrypoint and does not redeploy it or trigger the SBF workflow. No production dependency, keypair, real wallet or transaction is introduced. The SDK is pinned to a published release (https://pypi.org/project/solders/0.29.0/), not independently audited. All payment gates remain closed.

## Payment gateway preview
The offline checkout uses integer atomic units and a QR with a deliberately non-payable lab payload. It contains no wallet address or Solana Pay URI. Render the sample locally using the isolated lab environment:

```sh
PYTHONPATH=../backend python payment_gateway.py --cents 100000 --output checkout-preview.html
```

The HTML has no JavaScript or network access, and the payment button is disabled. No live wallet testing, program deployment, or commercial payment authorization is implied.

## Consolidated payment flow
The fixture flow connects the checkout calculation, wallet signature check, exact legacy RPC message comparison, finalized snapshot matcher and in-memory treasury. It uses a deterministic synthetic signer and zero blockhash; it cannot settle a real order. Production gates, live-wallet compatibility, deployment identity, independent review and legal/support requirements remain open.
