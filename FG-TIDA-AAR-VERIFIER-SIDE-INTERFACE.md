# Verifier-side interface to the record requirements

**A linked contribution record to AAR-REQ (`FG-TIDA/themes#46`)**

| | |
|---|---|
| Author | Xinghua Zhao (Steven Zhao), independent expert, GitHub `@zhaoxinghua09-cell` |
| Offered in | Individual-expert capacity, as stated on `FG-TIDA/themes#46` on 29 October 2026 |
| Hosted in | `LGD-Eval/evaluation-protocol` — the public home of the evaluation material this record draws on. Hosting is a publication venue, not an authorship claim: the record is offered in individual-expert capacity, and the account relationship is disclosed below. |
| Version | 0.1 — 16 November 2026 |
| Status | Draft for attributed review before the first in-person FG-TIDA meeting (Paris, 30 November – 1 December 2026) |
| Linked work item | AAR-REQ 0.2 — https://tyche-dev.github.io/tida-aar-req/ |
| Licence | CC BY 4.0 |

---

## 1. Why this record exists

AAR-REQ states requirements on the record. It also states, in Out of Scope, that **"what a conformance verdict asserts and how it is checked"** is not its subject, and hands that question to `FG-TIDA/themes#6`, task 3.

This record occupies that handed-off position from the verifier side. It asks one question in four parts: given a record that satisfies R1–R8, **what can a party who was not there establish from it, what must that party state in order to be believed, and what is a "pass" allowed to mean when it is stated?**

It adds nothing to R1–R8 and modifies nothing in them. Every clause below is a statement about the verifier's report, not about the record's content. Where a clause depends on a record-side requirement, it names that requirement and takes it as given.

## 2. Scope

Four statements a verifier makes, and one obligation it carries:

- **VR1** — the grade of the evidence it relied on;
- **VR2** — the moment it evaluated against;
- **VR3** — whether a check was performable, and whether it was performed;
- **VR4** — what a pass may claim, bounded by what was actually checked;
- **VR5** — that its own report is a claim subject to R7.

## 3. Out of scope

Stated explicitly so that overlap is decidable rather than implicit:

- **How a verifier reaches a class.** The class vocabulary is R1–R4; this record does not prescribe decision procedure, thresholds, or evidence weighting.
- **Encodings, schemas, field names, media types, test vectors.** As in AAR-REQ §1.3.
- **What a conformance verdict asserts about an artefact** (`FG-TIDA/themes#6`, task 3). This record is about the verification verdict on a *record of an act*, not on a *product*.
- **Where authority originates and what may be conferred** (`FG-TIDA/themes#5`).
- **Legal effect.** A pass is a statement about checks performed; it is not a legal opinion and confers nothing.

## 4. The clauses

Attribution convention follows AAR-REQ Table 2.1: each clause names who proposed it, and in brackets who refined it.

### VR1 — Evidence grade is a property of the verifier's relation to the evidence, not of the record

*Proposed by @zhaoxinghua09-cell.*

A record can be complete and still be unusable by a given verifier, because usability depends on what that verifier can reach. The grade therefore cannot live inside the record: AAR-REQ §1.3 puts "how any value in a record is computed" out of scope, and a grade assigned by a producer would in any case be a claim the verifier has not checked.

The verifier states one grade, from an ordered set, for the evidence it relied on:

| Grade | Meaning |
|---|---|
| **A** | Checked by the verifier against a source it can reach without trusting the producer |
| **B** | Checked by a party with no relationship to the producer, named in the report |
| **C** | Corroborated indirectly — consistent with independent material, not checked at source |
| **D** | Asserted only — the verifier relied on the producer's statement |

Two properties matter more than the number of grades. First, the grade is **about the claim, not the actor**: a strong grade on a claim does not make the actor's authorization valid, and VR1 must not be read as doing so (this keeps the separation argued in `FG-TIDA/themes#42`). Second, the set is **ordered but not arithmetic**: grades are not averaged across a chain, because a chain is only as strong as its weakest link and averaging would hide exactly that.

### VR2 — The verifier states which moment it evaluated against, chosen from three

*Proposed by @zhaoxinghua09-cell. The three moments are @OlehVasylenko2000's (12 November 2026) and are adopted here unchanged; the verifier-side obligation is this record's.*

R6 makes freshness a relation, not a property. A relation needs two terms, and the second term — the moment the verifier used — is currently unstated on the verifier side. So the verifier names which of the three moments it used:

1. **The moment of the act** — the moment the record describes.
2. **The moment the producer states for a claim** — carried under R7.2.
3. **An independently bounded moment** — which establishes only that the record existed no later than that time, and is not the freshness relation of R6.

A verdict evaluated at moment 1 and a verdict evaluated at moment 3 are **not the same object**, even when every field is identical, because the state that governs the act (R8.5) may have changed between them. A report that omits this is not reproducible by a later reader, who cannot tell which question was answered.

The verifier also states whether rechecking was possible, taking R6's "means, if any, of rechecking" as given. Where no means exist, the report says so rather than leaving the field empty — an absent rechecking means is itself a finding.

### VR3 — "Checkable" is not "checked"

*Proposed by @zhaoxinghua09-cell.*

R7.3 requires tamper-evidence that a party with no relationship to the producer **can** check. That is a statement about capability, and it is satisfied by a record no one has ever examined.

So the verifier states, for each check it reports, which of three happened:

- **performed by the verifier** — the check was run, and the means are named;
- **performed by a named third party** — the check was run by a party with no relationship to the producer, and the report names it;
- **asserted** — the check was not run by anyone the verifier can name.

This distinction is load-bearing because the failure it prevents is silent. A record that is checkable but unchecked produces a verdict that looks like a verdict from a check, and nothing in the record distinguishes the two. Where a check was asserted rather than performed, the evidence grade (VR1) cannot exceed **D** for that claim, whatever the record's properties.

### VR4 — A pass claims no violation found within a stated boundary, and nothing more

*Proposed by @zhaoxinghua09-cell, carrying forward the question posed in `FG-TIDA/themes` PR #28.*

A pass carries four things, and is incomplete without any of them:

1. the **checks performed** (with VR3's status for each);
2. the **checks not performed** — named, not implied;
3. the **boundary** within which the checks ran;
4. the **moment used** (VR2).

With those four, a pass means exactly: *no violation was found within this stated boundary, using these checks, at this moment.* It does not mean the act was authorized, that the record is true, or that the delegation was sound. R7 says as much for carried claims — that a claim meets R7 does not make it true — and the same restraint has to hold one level up, at the verdict.

The property this buys is that a pass is **falsifiable by its own declaration**. A later party can withdraw it by showing a single check inside the declared boundary that was not performed, without having to relitigate the facts. A pass that does not declare its boundary cannot be withdrawn this way, and therefore cannot be relied on — it can only be believed.

### VR5 — The verifier's own report is a claim, subject to R7

*Proposed by @zhaoxinghua09-cell. This closes the recursion @OlehVasylenko2000 raised for R7.*

If the verifier's report matters to a later decision — and VR4 makes it the thing relied on — then the report is itself a carried claim and R7 applies to it unchanged: attribution (R7.1), a stated moment (R7.2), and tamper-evidence a party with no relationship to the producer can check (R7.3).

The practical consequence is narrow but sharp. **A verifier that does not disclose its own evidence basis is producing an unattributed claim**, and VR4's boundary cannot be read off it. This is not a demand that verifiers publish; it is a statement that an unpublished basis caps the grade the next party can assign.

## 5. Interface table

What the verifier reads from each record-side clause, and what it must state in return. The right-hand column is this record's contribution; the left-hand column is AAR-REQ's and is not restated.

| AAR-REQ | What the verifier reads | What the verifier must state |
|---|---|---|
| R1, R2 | the rejection class and the reported cause | VR1 grade for the claim about the cause; VR3 status per check |
| R3 | the four tier-1 classes are decidable from the record and the verifier's own state | which classes it actually decided, and which it could not |
| R4, R4.1–R4.3 | whether continued standing is checkable, and which moment the relying party used | VR2 moment, stated explicitly rather than inherited |
| R5 | negative and null assertions are claims like any other | VR1 grade per assertion; a null assertion is graded, never skipped |
| R6 | the moment the assertion was true, and the means of rechecking | VR2 moment used; whether rechecking was possible, and if not, that it was not |
| R7, R7.1–R7.3 | attribution, stated moment, tamper-evidence | VR3 performed / by a named third party / asserted; VR5 for its own report |
| Absence and silence | which of the three states holds | which state was established, and the scope and author of any bounded search |
| LR1–LR5 | which lineage case holds | the case reported, with the evidence grade for it |
| R8, R8.1–R8.5 | act, execution, supported relation to a logical agent, effective state | which of the five it established, and at which moment (VR2) |

## 6. Three boundary cases

These are the cases where a verifier most easily states more than it checked.

**Case A — checkable, uncheckable-by-this-verifier.** The record is complete and tamper-evident; the verifier has no relationship to the producer and no route to recheck. Verdict: *no violation found within boundary, grade D, rechecking not possible.* Not a pass in the ordinary sense, and not a rejection either — R3's classes do not apply, because nothing was found to be wrong.

**Case B — right record, wrong moment.** Every tier-1 check passes at the moment of the act; standing was withdrawn before the verifier looked. Reporting a pass at moment 3 while presenting it as a statement about moment 1 is the error VR2 exists to prevent. The verifier's verdict is about the moment it names, and the report must let a reader see which.

**Case C — absence is not silence.** No record at all, a bounded search that returned nothing, and a reference that was established are three different findings. Only the second carries a scope and an author; the third is a positive finding. Collapsing them yields a verdict that reads as "nothing wrong" when the correct reading is "nothing was looked at".

## 7. Open questions

Carried openly, in the style of AAR-REQ §2.1.

1. **Is four grades the right cut?** Three would force B and C together, which hides the difference between a check performed elsewhere and a corroboration. Five invites distinctions no one can apply consistently. *(@zhaoxinghua09-cell)*
2. **Should VR2's moment be a required field in the report, or only a required statement?** A field is machine-checkable; a statement is cheaper and survives formats the group has not settled. *(@zhaoxinghua09-cell)*
3. **Does VR5 bind all verifier output, or only published verification reports?** Binding all output is the stronger position and the harder one to meet, and I would rather the group choose it knowingly than have it arrive by implication. *(@zhaoxinghua09-cell)*
4. **Where does the boundary in VR4 come from?** If the group names a minimum boundary somewhere, this record should cite it rather than let each verifier declare its own. *(@zhaoxinghua09-cell)*

## 8. Provenance

- AAR-REQ 0.2, web — https://tyche-dev.github.io/tida-aar-req/
- AAR-REQ 0.2, PDF — https://tyche-dev.github.io/tida-aar-req/specification.pdf
- Originating thread — https://github.com/FG-TIDA/themes/issues/46
- Verifier-side charter — https://github.com/FG-TIDA/themes/pull/28
- Evidence grading (separating evidence quality from authorization validity) — https://github.com/FG-TIDA/themes/issues/42
- Evidence-graded authorization verdicts — https://github.com/FG-TIDA/themes/issues/43
- Conformance verdict scope, handed off by AAR-REQ §1.3 — https://github.com/FG-TIDA/themes/issues/6
- Author identity — https://orcid.org/0009-0001-0512-1237
- Account relationship and conflict-of-interest disclosure — https://github.com/LGD-Eval/evaluation-protocol/blob/main/CONFLICT_OF_INTEREST_DISCLOSURE.md

## 9. Limitations

- **The clause set has had one author.** VR1–VR5 are coherent with each other by construction, which is not the same as being right. Two of the five (VR3, VR4) rest on a distinction that is easy to state and hard to apply; a reviewer should test them against a case they already know the answer to.
- **No implementation accompanies this version.** The reference implementation covers the evidence-gated state machine, not the verifier report format these clauses describe. A worked example set is the obvious next increment and is not claimed here.
- **The material this record draws on has not been through peer review.** `FG-TIDA/themes#42` and `#43` are proposals under discussion, not settled positions, and VR1 is a restatement of their separation argument rather than independent evidence for it.
- **Drafted with AI assistance** under author direction; the author is responsible for every claim above.

## 10. Version history

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-16 | First draft, posted for attributed review on `FG-TIDA/themes#46` |

---

## 中文要点对照

> 英文为权威文本；以下为逐条中文要点，供中文读者对照，非逐句对译。

**本记录的位置。** AAR-REQ 在 Out of Scope 里明写「一致性判定能主张什么、怎么检查」不是它的事，并转给 `themes#6` task 3。本记录就站在这个被让出来的位置上，从验证方一侧回答：一份满足 R1–R8 的记录，一个当时不在场的人能从中确立什么、必须自己声明什么、以及「通过」到底允许主张什么。**不给 R1–R8 增加任何内容。**

| 条款 | 中文要点 |
|---|---|
| **VR1** | 证据等级是验证方与证据之间关系的属性，不是记录的属性。记录再完整，对某个验证方也可能不可用。四档：A 自己直接核到源头；B 由与产出方无关的具名第三方核过；C 间接佐证；D 仅有断言。等级针对**主张**，不针对**行为人**——等级高不等于授权有效。四档有序但不可做算术平均，链的强度等于最弱一环。 |
| **VR2** | 验证方必须声明自己用的是哪个「时刻」，三选一：①行为发生时 ②产出方为某主张声明的时刻 ③独立可界定的时刻（只能证明记录不晚于某时，不是 R6 的时效关系）。同一份记录、同一个字段，用不同时刻得出的结论**不是同一个东西**，因为 R8.5 的有效状态可能已经变了。还要声明「能否复核」——没有复核手段本身就是一个结论，不能留空。 |
| **VR3** | 「可检查」不等于「已检查」。R7.3 只保证「与产出方无关的人**能**检查」，一份谁都没看过的记录同样满足它。所以每项检查都要标状态：验证方自己做的／具名第三方做的／仅有断言。这条重要，因为失效是静默的——可检查但未检查的记录，产出的结论看起来跟检查过的一样。仅有断言时，该主张的证据等级最高只能到 D。 |
| **VR4** | 通过 = 在声明边界内、用声明的检查、在声明的时刻，未发现违规。**仅此而已**，不等于行为获授权、记录为真、委托成立。必须带四样：做了什么检查、**没做什么检查**（要点名）、边界、所用时刻。这样换来的性质是：**通过可以被它自己的声明推翻**——后人只要指出边界内有一项检查没做，就能撤回它，不必重打事实。不声明边界的通过，无法被这样撤回，因此不能被依赖，只能被相信。 |
| **VR5** | 验证方自己的报告也是主张，R7 照样适用：归属、声明时刻、与产出方无关者可校验的防篡改。推论很窄但很利：**不披露自身证据基础的验证方，产出的是一份无归属主张**，VR4 的边界无从读起。这不是要求验证方必须公开，而是说未公开的基础会压低下一个当事人能给到的等级。 |

**三个边界情形。** A：记录可检查、但本验证方查不到——结论是「边界内未发现违规、等级 D、无法复核」，既不是通过也不是拒绝（R3 的四类不适用，因为没发现错）。B：记录对、时刻错——行为时全部通过，验证方来看时资格已撤回；把时刻③的结论当时刻①的结论报，正是 VR2 要挡的错。C：无记录 ≠ 静默——「根本没有记录」「有界检索查无」「引用已确立」是三种不同结论，只有第二种带检索范围和作者；混为一谈会把「什么都没查到」读成「什么都没问题」。
