# Independent Third-Party Review — Verified Transition Loop (VTL) v0.14

**Reviewer:** LGD-Eval (independent third-party evaluation group)
**Date:** 2026-10-17
**Baseline:** `safal207/LS` @ `9c7fc7c3c73ec0107615af3051e78639405301e7` (main, 2026-08-27)
**Scope:** `prototypes/verified-transition-loop` (v0.14), evidence/verification layer only.
**Method family:** same as our earlier review of the LS trust runtime (see
`reviews/cosai-ws4-issue158/REVIEW.md`), applied to the VTL prototype of the same author.

> This review is an independent second evaluation by the same third-party evaluation
> group, covering a different prototype (`verified-transition-loop`) from the same
> author. It follows the same methodology as our earlier review of the trust runtime
> and is published independently. It is an evaluation, not a certification; no
> accreditation or official status is claimed.

## 1. What was examined

VTL treats the **verified state transition** as the primary unit of execution and
proof, keeping eleven proof layers separate (use-time authority, dispatch integrity,
producer signature, current-signer authority, trust-root authenticity/freshness,
canonical-byte interoperability, canonical-signature interoperability, canonical
fresh-trust interoperability, witnessed non-equivocation, transparency-log inclusion,
append-only consistency). The stated invariant: *a valid higher-layer proof never
repairs an invalid lower-layer proof.*

We exercised the transparency-log layer (v0.14) and the canonicalization core
(rfc8785-safe-integer/v0.10) with the prototype's own reference implementation and
published fixtures.

## 2. Independent reproduction

Environment: Node v22.23.2, Windows; no modifications to the prototype sources.
Commands run from `D:\doubao\ls-eval\vtl\` (files fetched from GitHub `main` @ 9c7fc7c).

| Fixture | strictParse | canonical digest (SHA-256 of canonical bytes) | bytes |
|---|---|---|---|
| attested-dispatch-v0.8 | OK | `59a3c99e…10b38bf` | 11,177 |
| canonical-proof-v0.10 | OK | `5296f479…a427885` | 4,473 |
| canonical-signed-envelope-v0.11 | OK | `3fa8d9b1…0140224` | 6,799 |
| canonical-trust-root-snapshot-v0.12 | OK | `a7ac6830…5e5f67d1` | 14,652 |
| tool-dispatch-receipt-v0.7 | OK | `1dabf2e5…1c8bfa83` | 6,558 |
| transparency-log-v0.14 | OK | `58c655f1…81937952` | 26,654 |
| trust-root-snapshot-v0.9 | OK | `360b83fc…62d2ee33` | 8,613 |
| use-time-conformance-v0.4 | OK | `e646cd6e…f5008ec` | 6,173 |
| witnessed-freshness-v0.13 | OK | `2de46c72…4a0468` | 17,465 |

**Result: 9/9 fixtures parse under the strict parser (rejects duplicate keys and
escaped collisions) and reproduce deterministic canonical digests.**

Baseline verdict on the published transparency-log fixture
(`transparency-log-v0.14.json`): `valid=true`, all sub-layers valid
(entry integrity, checkpoint integrity/signature/authority/freshness, inclusion,
consistency, view consistency), `log_equivocation_detected=false`,
`accepted_tree_size=6`.

## 3. Adversarial checks

Two variants of the published transparency-log bundle were constructed from the
public fixture (inputs fully embedded in this report's repro kit) and run through
the strict verifier CLI:

| Variant | Constructed change | Verdict | reason_codes |
|---|---|---|---|
| A — evidence missing | removed `inclusion_path` (claim without proof) | `valid=false` | `TRANSPARENCY_BUNDLE_FIELDS_INVALID`, `INCLUSION_PROOF_INVALID` |
| B — evidence tampered | flipped one hex digit of `entry.snapshot_digest` | `valid=false` | `ENTRY_SNAPSHOT_DIGEST_MISMATCH`, `INCLUSION_PROOF_INVALID` |

Both fail closed; per-layer flags (`entry_integrity_valid`, `inclusion_valid`,
`consistency_valid`) allow a reader to localize which layer failed.

## 4. Findings

**F1 (Low, informational): verdict binarization erases the "cannot be measured" state.**
Evidence-missing (A: `TRANSPARENCY_BUNDLE_FIELDS_INVALID`) and evidence-wrong
(B: `ENTRY_SNAPSHOT_DIGEST_MISMATCH`) produce *different reason codes but the same
boolean verdict* (`valid=false`). A consumer therefore cannot distinguish "the claim
was measured and found inconsistent" from "the evidence could not be measured (missing,
truncated, or not yet produced)". Operationally these demand different responses —
reject/revoke versus re-request/probe — and different audit meaning. A ternary verdict
(unresolved/rejected/verified) or an explicit `unresolved` reason class would preserve
the distinction. Fail-closed direction is safe today; the gap is semantic/audit.

**F2 (Low, informational): invalid runs discard the last-accepted anchor.**
On failure, `accepted_tree_size`/`accepted_root_hash` are set to `null`, so an auditor
cannot tell *how far* verification progressed before failure. Keeping the last
accepted checkpoint anchor alongside the failure would aid post-incident analysis.

**F3 (Positive): layer separation holds.**
Sub-layer flags are independent and the strict verifier rejects checkpoint-integrity
violations even when lower layers pass — consistent with the "higher-layer never
repairs lower-layer" invariant. Equivocation detection field (`log_equivocation_detected`)
is present and wired.

## 5. Reproducibility kit

- This repo: `reviews/verified-transition-loop/` — `REVIEW.md`, `verify_vtl.mjs`,
  variant construction script `make_variants.py`, inputs `_variant_A/B.json`.
- Prototype files pinned: `safal207/LS` @ `9c7fc7c3c73ec0107615af3051e78639405301e7`,
  `prototypes/verified-transition-loop/` (canonical-runtime-v0.12.mjs,
  transparency-log-strict-v0.14.mjs, fixtures/).
- Re-run: `node reviews/verified-transition-loop/verify_vtl.mjs` then
  `node reference/transparency-log-strict-v0.14.mjs <variant>` (paths per repo layout).

## 6. COI & neutrality

- Conflict-of-interest disclosure:
  `https://github.com/LGD-Eval/evaluation-protocol/blob/main/CONFLICT_OF_INTEREST_DISCLOSURE.md`
- This evaluation is published as independent third-party work; it confers no
  certification, accreditation, or endorsement.
- AI assistance disclosure: drafting and test-harness generation assisted by an AI
  agent; all test executions and digests independently re-run by the reviewer.
