# Inputs-only package — cases A / B1 / B2 / C

Requested in [FG-TIDA/use-cases#27](https://github.com/FG-TIDA/use-cases/issues/27):
an inputs-only package so that an independent evaluator can implement against the
inputs **without the expected outcomes sitting beside them**, with the expected
outcomes kept in a separate evaluator-side file under the same commit.

## What is here

| File | Case | SHA-256 (LF bytes) |
|---|---|---|
| `caseA_input.json` | case A | `9151cae3ce0ec76563cbc2f6c6ae84ea89d4a4d151f65a63b207c7cdb64acaf0` |
| `caseB1_input.json` | case B1 | `7a82f14bae30591134a0cd2c2b793b7bc32696118d4918c5511faf80096b0f9a` |
| `caseB2_input.json` | case B2 | `061f0dde32e8c89ce85ee1127d42b44ca076bd4564e1b51a22da29ed62efc120` |
| `caseC_input.json` | case C | `9d59b5d528a63e3796112b1f3ba14316a76f016e2edb616d6c7847a5d0c1708d` |

Each file contains the `subject` and the evidence `domains` only. The
`authorization` block that carried the expected result in the original input
files has been removed — an implementation reading this directory learns what
happened, never what should be concluded.

## Case B2 — authority basis (in the input, not the outcome)

Per the same request, `caseB2_input.json` records explicitly what makes the
negative response authoritative: `authority_basis` states the designated
source, the scope of its authority, the time basis (frozen vector T-B2b), the
federation caveat, and the residual limit. The verdict itself stays out of
this directory.

## Where the expected outcomes are

`../EXPECTED_OUTCOMES.evaluator-side.json` — one evaluator-side file, same
commit. It carries, per case: `outcome.verification`, `reason_code`,
`policy_action` and the `payload_digest` copied from the published v1.3
conclusions. Implementations under test must not read it.

## Separation preserved

Per-link evidence, the verification result and the relying-party policy action
remain separate fields, unchanged from the v1.3 conclusion schema.

Attribution: prepared by LGD-Eval. COI disclosure:
[LGD-Eval/CONFLICT_OF_INTEREST_DISCLOSURE.md](https://github.com/LGD-Eval/LGD-Eval/blob/main/CONFLICT_OF_INTEREST_DISCLOSURE.md)
