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

## 2. Evidence Model (evidence-grader v1.2)

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

| Verdict | Meaning | Operator meaning |
|---|---|---|
| `verified` | Evidence measured and consistent with authorization | ALLOW |
| `unresolved` | Evidence absent or unmeasurable — not yet decidable | DEFER (do not default to allow) |
| `rejected` | Evidence measured and found inconsistent | DENY |
| `quarantined` | Normative semantics of the field still unsettled | EXCLUDE from formal result until spec settles |

### 2.3 Payload digest convention

Canonical digest = `SHA-256( json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8") )`.
Digests are truncated to the first 16 hex chars as vector ids in worked examples, and
quoted in full in evidence records. Re-running the same canonical input must reproduce
the same digest (determinism check, see §4).

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

- Protocol version: v1.2 (evidence-grader). This document: v0.1.
- Changes are tracked in git; worked examples updated atomically with the grader.
- Zenodo record for protocol releases: https://zenodo.org/records/23428476 (CC-BY-4.0).

## 7. Contact & Contributions

- Repo: https://github.com/LGD-Eval/evaluation-protocol
- Reports & worked examples: `reviews/`, `worked-examples/`
- Contributions welcome via issues/PRs; all published work follows this standard.
