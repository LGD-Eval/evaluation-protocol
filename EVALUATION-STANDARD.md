# LGD-Eval Evaluation Standard — 评测规范（v0.1)

> **Status: community evaluation protocol, not an official standard.**
> This document defines how LGD-Eval conducts and reports third-party evaluations of
> agentic-AI authorization and control mechanisms. It is published for transparency
> and re-use; it carries no regulatory or certification authority. Any claim of
> certification, accreditation, or official designation is out of scope and disclaimed.
>
> 本规范为社区性评测协议，非官方标准；不构成任何认证或监管资质。

## 1. Purpose & Boundaries

LGD-Eval is an **independent third-party evaluation group**. Evaluations we publish:

- target **agentic-AI authorization / control mechanisms** (protocols, hooks, runtimes,
  frameworks) — trust mechanics, not macro AI governance;
- are performed against a **public, pinned baseline** (repository + commit), so any
  third party can re-run the same experiment;
- report **evidence grades, verdicts, and reproducible digests**, not opinions;
- carry an explicit **conflict-of-interest disclosure** and neutrality statement.

Out of scope: certification, accreditation, conformity assessment with legal effect,
regulatory opinion, or endorsement of any product or vendor.

## 2. Evidence Model (evidence-grader v1.3)

Each evaluated claim is graded on two axes:

### 2.1 Evidence grade (per claim)

| Grade | Meaning |
|---|---|
| V — Verified | Reproduced end-to-end by an independent run; result matches the claim |
| S — Substantiated | Strong supporting evidence; one step short of independent reproduction |
| M — Merited | Reasonable evidence; plausibly correct, further verification advised |
| L — Limited | Weak or indirect evidence; conclusion not supported beyond stated scope |
| P — Partial | Only part of the claim could be checked; remainder unverified |

### 2.2 Authorization verdict (per decision)

The verification verdict has three states. This is the vocabulary used in `outcome.verification`.

| Verdict | Meaning | Operator meaning |
|---|---|---|
| `verified` | Authorization established and current | ALLOW |
| `unresolved` | Authorization cannot be established — not yet decidable | DEFER (do not default to allow) |
| `rejected` | Authorization affirmatively not valid — established by evidence | DENY |

**Operator action is a separate axis.** What a relying party does is policy-dependent, so it is recorded in its own field (`outcome.policy_action`) and never merged into the verdict. `reject` is not available as an action name: the word is reserved for the verdict, so the two levels stay distinguishable at a glance.

| Operator action | Meaning | Typical trigger |
|---|---|---|
| `allow` | Proceed under normal policy | `verified` |
| `defer` | Do not default to allow; hold for review or escalation | `unresolved` |
| `deny` | Do not accept | `rejected` |
| `exclude` | Keep out of the formal result until the normative semantics settle | Field semantics still unsettled — this is **not** a verification verdict |

`quarantined` was a fourth value of the verdict up to v1.2 and was removed in v1.3: it described a handling decision over an unsettled field, not something that had been verified. It is now `policy_action: exclude`. Evidence-level `failure_class` still reports `quarantined` for malformed input; that is the evidence axis (§2.1) and is unchanged.

### 2.3 Payload digest convention

Canonical digest = `SHA-256( json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8") )`.
Digests are truncated to the first 16 hex chars as vector ids in worked examples, and
quoted in full in evidence records. Re-running the same canonical input must reproduce
the same digest (determinism check, see §4).

The digest covers the substantive objects of a conclusion (`domains`, `authorization`,
`outcome`) and excludes `timestamp`, so reproduction is date-independent. `verdict` and
`overall_failure_class` are pure functions of `domains` and are covered transitively.

> **Correction (v1.3, 2026-10-23).** The convention above has been published in this
> section since v0.1, but the v1.2 implementation computed the digest with default JSON
> separators (`", "` / `": "`) and insertion order rather than `sort_keys=True` with
> compact separators. A third party following this section could therefore not reproduce
> any published digest. The implementation now matches the text; all four v1.2 digests
> were recomputed, with the reasons listed in `worked-examples/cases/README.md`.

### 2.4 Case outcome vs coverage verdict

A conclusion reports two summary fields that answer different questions, and reading the
wrong one reports a passing case as a failure:

| Field | Answers | Scope |
|---|---|---|
| `outcome.verification` | What is the case-level conclusion for the dimension under test? | The case |
| `verdict` | How much of the six-domain evidence grid is covered at grade V/S? | The grid |

A case set that exercises one or two of the six domains is `Insufficient evidence` under
`verdict` by construction, even when its authorization outcome is `verified`. Readers and
programs should take the case conclusion from `outcome.verification`. Each conclusion also
carries a `scopes` object stating this in machine-readable form, so the distinction
travels with the data instead of living only in documentation.

## 3. Evaluation Report Format

Every published evaluation follows the REVIEW format (see `reviews/` for samples):

1. Scope & baseline (repo, commit, profile, date)
2. Method (how claims were exercised; tooling pinned)
3. Independent reproduction (baseline test results)
4. Findings, each with: severity, evidence grade, verdict, repro steps, digest
5. Risk table & fail-closed/fail-open classification
6. COI disclosure & neutrality statement
7. Reproducibility kit (scripts, vectors, inputs) linked

## 4. Verification Gates (pre-publication)

Before any report is published, the following must pass (recorded in the report):

- [ ] Baseline reproduced (pinned commit, tests pass) — external perspective run
- [ ] Each digest recomputed from the *published* inputs (not local-only files)
- [ ] Schema/format validation where a schema exists
- [ ] Findings' evidence grades assigned against §2.1
- [ ] Neutrality & COI statement present; no claims of certification/priority
- [ ] Repro kit self-contained (a third party can run it from the public repo alone)

## 5. Badge Scheme (non-official)

See [BADGES.md](./BADGES.md). Badges describe evaluation outcomes and methodology
transparency; they are **not** certificates, do not imply endorsement, and must be
displayed with the disclaimer text defined there.

## 6. Versioning & Change

- Protocol version: v1.3 (evidence-grader). This document: v0.2.
- v1.3 (2026-10-23): case outcome separated from the coverage verdict; operator action split
  out of the verdict vocabulary; digest computation corrected to match §2.3. All worked-example
  digests recomputed.
- Changes are tracked in git; worked examples updated atomically with the grader.
- Zenodo record for protocol releases: https://zenodo.org/records/23428476 (CC-BY-4.0).

## 7. Contact & Contributions

- Repo: https://github.com/LGD-Eval/evaluation-protocol
- Reports & worked examples: `reviews/`, `worked-examples/`
- Contributions welcome via issues/PRs; all published work follows this standard.
