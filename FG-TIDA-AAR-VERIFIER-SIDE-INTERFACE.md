# Verifier-side interface to the record requirements

**A linked contribution record to AAR-REQ (`FG-TIDA/themes#46`)**

| | |
|---|---|
| Author | Xinghua Zhao (Steven Zhao), independent expert, GitHub `@zhaoxinghua09-cell` |
| Offered in | Individual-expert capacity, as stated on `FG-TIDA/themes#46` on 29 October 2026 |
| Hosted in | `LGD-Eval/evaluation-protocol` — the public home of the evaluation material this record draws on. Hosting is a publication venue, not an authorship claim: the record is offered in individual-expert capacity, and the account relationship is disclosed below. |
| Version | 0.2 — 16 November 2026 |
| Status | Draft for attributed review before the first in-person FG-TIDA meeting (Paris, 30 November – 1 December 2026) |
| Linked work item | AAR-REQ 0.2 — https://tyche-dev.github.io/tida-aar-req/ |
| Licence | CC BY 4.0 |

---

## 0. Terms

Two terms are used throughout and are defined here so that the interface below is readable against AAR-REQ's own text.

**Relying party.** As in AAR-REQ: the party that acts on a claim about an agent after the fact.

**Verifier.** The relying party itself, or an agent acting for it, when it evaluates a record and states a result. This record does not introduce a second role: wherever AAR-REQ binds a relying party, the obligation falls on the verifier, and wherever AAR-REQ's text says "relying party" this record's clauses are satisfied by the same party under the other name. The name is used because the clauses are about the act of verifying, not about the act of relying.

**Record-side / verifier-side.** Record-side requirements constrain what a record must carry. Verifier-side requirements constrain what a party must state when it reports a result from a record. R1–R8 are record-side. The clauses below are verifier-side.

## 1. Where this record sits

AAR-REQ §1.2 puts two things in scope: requirements on the record, and **"what a relying party reports from it"**. The second is not left open in general — R1–R4 enumerate the rejection classes a relying party reports, and R1 states that a bare accept or reject is not enough.

What is left open is narrower, and it is the gap this record works in:

- **The rejection side is enumerated; the accept side is not.** R1 forbids a bare accept and R3–R4 give four tier-1 and one tier-2 rejection class with contents. No clause says what a non-bare accept must carry, or what it is allowed to assert. R1 creates the obligation without supplying its content.
- **§1.3 hands away the verdict question.** "What a conformance verdict asserts and how it is checked" is out of scope and assigned to `FG-TIDA/themes#6`, task 3.

So the position is not an empty space: it is an obligation with no content, next to a question that has been moved elsewhere. This record supplies content for the first and stays clear of the second — it says nothing about conformance verdicts on an artefact, only about the report a party makes after verifying a record of an act.

This is a refinement of AAR-REQ's existing verifier-side requirement, not an addition to the record-side set. **It adds nothing to R1–R8 and changes nothing in them.** Where a clause depends on a record-side requirement, it takes that requirement as given and names it.

## 2. Scope

- **VR1** — the grade of the evidence the verifier relied on;
- **VR2** — the moment the verifier evaluated against;
- **VR3** — whether each reported check was performed, and by whom;
- **VR4** — what a pass may claim, bounded by what was actually checked;
- **VR5** — the verifier's own report as a claim the next party has to grade.

## 3. Out of scope

Stated so that overlap is decidable rather than implicit:

- **Decision procedure, thresholds, evidence weighting.** How a verifier reaches a class is R1–R4's subject and is not prescribed here.
- **Encodings, schemas, field names, media types, test vectors.** As in AAR-REQ §1.3. VR1's four grades and VR3's three states are **descriptions of relations, not enumerations to be encoded**: a verifier may state them in its own words, and no field name is proposed.
- **Conformance verdicts on an artefact** (`FG-TIDA/themes#6`, task 3).
- **Where authority originates and what may be conferred** (`FG-TIDA/themes#5`).
- **Legal effect.** A pass is a statement about checks performed. It is not a legal opinion and confers nothing.

## 4. Conformance language

"States" in VR1–VR5 means **SHALL** for any report presented as a pass, and **SHOULD** for any report presented as an unresolved result. The consequence of not stating is stated once here and relied on below: a report that omits a required statement cannot be graded above **D** by the next party, because the next party has nothing to check it against (VR5). No other consequence is claimed.

## 5. The clauses

Attribution follows AAR-REQ Table 2.1: each clause names who proposed it and, in brackets, who refined it. Where a clause restates an argument made elsewhere, the origin is named first and the restatement is not presented as an independent proposal.

### VR1 — Evidence grade describes the verifier's relation to the evidence, not the record

*Argument from `FG-TIDA/themes#42` and `#43` (LGD-Eval, with refinements from @dakleyer); restated and applied to the AAR verification case by @zhaoxinghua09-cell.*

A record can be complete and still be unusable by a given verifier, because usability depends on what that verifier can reach and what it has actually done. A grade assigned by the producer would therefore be a claim the verifier has not checked, and AAR-REQ §1.3 already puts "how any value in a record is computed" out of scope.

The verifier states one grade for each claim it relies on. The four grades are defined by two questions — *was the check performed, and against what?* — so that each grade has a route to being reached and each reported status has a grade:

| Grade | Was it performed? | Against what? |
|---|---|---|
| **A** | Yes, by the verifier | A source the verifier can reach without trusting the producer |
| **B** | Yes, by a named party with no relationship to the producer | A source that party can reach without trusting the producer |
| **C** | Yes, by the verifier | Material independent of the producer, which the verifier can reach, but not at source |
| **D** | No | Nothing — the verifier relied on the producer's statement |

Two things follow from the table and are worth stating because they are where it is usually got wrong. First, the grade is **about the claim, not the actor**: a grade A on a claim says nothing about whether the actor's authorization was valid, and VR1 must not be read as saying so — this is the separation argued in `FG-TIDA/themes#42`. Second, the grades are **ordered but not arithmetic**: they are not averaged across a chain, because averaging would hide the weakest hop, which is the only hop that matters.

Where corroboration is claimed at grade C, this record does **not** set how much agreement counts as corroboration. That is open question 2.

### VR2 — The verifier states which moment it evaluated against

*Three moments: @OlehVasylenko2000 (12 November 2026), recorded in AAR-REQ §2.1 against open question 12, where they are proposed as a possible R7.2a and are therefore not yet text. The verifier-side obligation to name one, and to extend it beyond the standing question, is @zhaoxinghua09-cell's.*

R6 makes freshness a relation rather than a property. R4.2 already requires a relying party to record **which moment it used** — but only for the tier-2 standing question (R4.1–R4.3). A verdict on the other tier-1 classes, and a pass as a whole, carries no such requirement, and a pass whose moment is unstated is not reproducible by a later reader: they cannot tell which question was answered.

So the verifier names one of three moments for every verdict it reports:

1. **the moment of the act** — the moment the record describes;
2. **the moment the producer states for a claim** — carried under R7.2;
3. **an independently bounded moment** — which establishes only that the record existed no later than that time, and is not the freshness relation of R6.

A verdict at moment 1 and a verdict at moment 3 are not the same object, even when every field is identical, because the effective state that governed the act (R8.5) may have changed between them. The increment over R4.2 is scope, not substance: R4.2 covers standing; VR2 covers every reported verdict, and requires the moment to be named rather than inferable.

The verifier also states whether rechecking was possible, taking R6's "means, if any, of rechecking" as given. Where no means exist, the report says so: an absent rechecking means is a finding, not a blank.

### VR3 — "Checkable" is not "checked"

*Proposed by @zhaoxinghua09-cell.*

R7.3 requires tamper-evidence that a party with no relationship to the producer **can** check. That is a capability, and it is satisfied by a record no one has ever examined.

So each reported check carries its status: **performed by the verifier**, **performed by a named third party**, or **asserted**. The mapping to VR1 is deliberate and total: A and C are the verifier's own checks, B is a named third party's, D is asserted with nothing performed.

This matters because the failure it prevents is silent. A record that is checkable but unchecked produces a report that reads like a report from a check, and nothing in the record distinguishes the two. The status is what distinguishes them, and it is why a claim whose checks were asserted cannot carry a grade above D.

### VR4 — A pass claims no violation found within a stated boundary

*Proposed by @zhaoxinghua09-cell, carrying forward the question posed in `FG-TIDA/themes` PR #28.*

A pass carries four statements, and is incomplete without any of them:

1. the **checks performed**, with VR3's status for each;
2. the **checks not performed** — named, not implied;
3. the **boundary** within which the checks ran;
4. the **moment used** (VR2).

With those four, a pass means exactly: *no violation was found within this stated boundary, using these checks, at this moment.* It does not mean the act was authorized, that the record is true, or that the delegation was sound. AAR-REQ says as much one level down — "R7 does not make a claim true" — and the same restraint has to hold at the verdict.

**A pass also has a floor.** Where every reported check is C or D, the report is *unresolved within the boundary*, not a pass, whatever else it states. Without the floor, a report in which nothing was checked against source could satisfy all four statements and present itself as a pass — which is the failure VR3 exists to name.

The floor is what makes a pass **falsifiable by its own declaration**: a later party can withdraw it by showing one check inside the declared boundary that was not performed as reported, without relitigating the facts. A pass that declares no boundary cannot be withdrawn that way, and therefore cannot be relied on — only believed.

AAR-REQ enumerates rejection classes and does not enumerate accept classes; R1 requires that a bare accept is not enough without saying what is. Whether "pass" and "unresolved within boundary" should become named classes in AAR-REQ is the group's decision, not this record's — it is open question 4.

### VR5 — The verifier's report is a claim the next party has to grade

*Proposed by @zhaoxinghua09-cell. The recursion in R7 is @OlehVasylenko2000's; this applies it one level up.*

VR4 makes the verifier's report the thing a later party relies on. When it is relied on, it is a carried claim in R7's sense, and R7's three properties apply by its own terms: attribution (R7.1), a stated moment (R7.2), and tamper-evidence a party with no relationship to the producer can check (R7.3). This record does not extend R7; it notes that R7 already reaches the report whenever the report is what a later party carries.

The practical consequence is narrow. A verifier that does not disclose the basis of its own report is producing an unattributed claim, and the next party cannot read VR4's boundary off it. That does not cap the grade at D by itself — but it caps it at whatever the next party can establish without the basis, which in practice is D. This is not a demand that verifiers publish; it is a statement about what an unpublished basis costs the next party.

## 6. Interface table

What the verifier reads from each record-side clause, and what it must state in return. The left column is AAR-REQ's and is not restated; the right column is this record's.

| AAR-REQ | What the verifier reads | What the verifier must state |
|---|---|---|
| R1, R2 | the rejection class and the reported cause | VR1 grade for the claim about the cause; VR3 status per check. Where nothing was rejected, VR4 governs instead, since R1–R4 give no content to an accept |
| R3 | the four tier-1 classes are decidable from the record and the relying party's own state | which classes it actually decided, and which it could not |
| R4, R4.1–R4.3 | whether continued standing is checkable, and which moment the relying party used | VR2 moment, named rather than inherited, extended from standing to every verdict |
| R5 | negative and null assertions are claims like any other (proposed by @cgorlla; null case @OlehVasylenko2000, refined by @zhaoxinghua09-cell) | VR1 grade per assertion; a null assertion is graded, never skipped |
| R6 | the moment the assertion was true, and the means of rechecking | VR2 moment used; whether rechecking was possible, and if not, that it was not |
| R7, R7.1–R7.3 | attribution, stated moment, tamper-evidence | VR3 status per check; VR5 for its own report |
| Absence and silence | which of the three states holds | which state was established, and the scope and author of any bounded search |
| LR1–LR5 | which lineage case holds | the case reported, with its evidence grade |
| R8, R8.1–R8.5 | four things across five sub-clauses: the act, the execution that performed it, that execution's supported relation to a logical agent where one exists, and the effective state that governed the act at that time | which of the four it established, at which moment (VR2), with the grade for each |

## 7. Three boundary cases

These are the cases where a report most easily states more than was checked.

**Case A — checkable, but not checked by this verifier.** The record is complete and tamper-evident; the verifier has no relationship to the producer and no route to a source. Every check it can make is C or D, so by VR4's floor the output is **unresolved within the boundary**, not a pass. It is also not a rejection: R1–R4's classes do not apply, because nothing was found to be wrong. The report names both facts and leaves the result unclassified, which is a gap in AAR-REQ's class set rather than in this record (open question 4).

**Case B — right record, wrong moment.** Every tier-1 check passes at the moment of the act; standing was withdrawn before the verifier looked. Reporting a pass at moment 3 while presenting it as a statement about moment 1 is the error VR2 exists to prevent. The verdict is about the moment named, and the report must let a reader see which — otherwise the reader supplies the wrong one.

**Case C — absence is not silence.** No record at all, a bounded search that returned nothing, and a reference that was established are three different findings. Only the second carries a scope and an author; the third is a positive finding. A report that collapses them reads as "nothing wrong" when the correct reading differs in each case: nothing was recorded, nothing was found within a stated search, or the thing was established.

## 8. Open questions

1. **Should the grade set and the status set be one table or two?** They are defined from the same two questions here, which makes them total but couples them: a fifth status would force a fifth grade. *(@zhaoxinghua09-cell)*
2. **How much agreement counts as corroboration at grade C?** This record does not set a threshold, and §3 excludes thresholds by scope. If the group wants C to be operable across implementers, the threshold has to come from somewhere; naming that somewhere is the open part. *(@zhaoxinghua09-cell)*
3. **Does VR5 bind all verifier output, or only published verification reports?** Binding all output is stronger and harder to meet, and I would rather the group choose it knowingly than have it arrive by implication. *(@zhaoxinghua09-cell)*
4. **Should "pass" and "unresolved within boundary" become named classes in AAR-REQ?** VR4's floor produces a result that R1–R4's class set does not name. Either the class set grows, or the report leaves it unclassified as Case A does. *(@zhaoxinghua09-cell)*
5. **Where does the boundary in VR4 come from?** If a minimum boundary is named somewhere in FG-TIDA's output, this record should cite it rather than let each verifier declare its own. *(@zhaoxinghua09-cell)*

## 9. Provenance

- AAR-REQ 0.2, web — https://tyche-dev.github.io/tida-aar-req/
- AAR-REQ 0.2, PDF — https://tyche-dev.github.io/tida-aar-req/specification.pdf
- Originating thread — https://github.com/FG-TIDA/themes/issues/46
- Verifier-side charter — https://github.com/FG-TIDA/themes/pull/28
- Evidence grading, separating evidence quality from authorization validity — https://github.com/FG-TIDA/themes/issues/42
- Evidence-graded authorization verdicts — https://github.com/FG-TIDA/themes/issues/43
- Conformance verdict scope, handed off by AAR-REQ §1.3 — https://github.com/FG-TIDA/themes/issues/6
- Author identity — https://orcid.org/0009-0001-0512-1237
- Account relationship and conflict-of-interest disclosure — https://github.com/LGD-Eval/evaluation-protocol/blob/main/CONFLICT_OF_INTEREST_DISCLOSURE.md

## 10. Limitations

- **Only the clause table and the scope chapter were read.** AAR-REQ states that its clause text "stands in 2 comments posted on FG-TIDA/themes#1" and that where the table differs, those comments govern. This record was written against the table in §2 and the scope in §1, and has **not** been reconciled against those two comments. Where they differ, they win, and VR2 in particular should be re-read against them.
- **The three moments are a proposal, not text.** AAR-REQ §2.1 records them against open question 12 as a possible R7.2a — "if the proposed R7.2a becomes text". VR2 adopts them as the set to choose from; if the group settles differently, VR2's enumeration changes with it.
- **The grade set is single-author and untested.** VR1's four grades are coherent by construction, which is not the same as being right. C is the one to test: it is the only grade whose boundary is a matter of degree, and open question 2 is unresolved.
- **No consequence semantics beyond §4.** The clauses say what a report must state and what the next party can do without it. They do not say what happens to a verifier that states nothing — that is AAR-REQ's conformance question, which §1.3 moves elsewhere.
- **No implementation accompanies this version.** The reference implementation covers the evidence-gated state machine, not the report format these clauses describe. A worked example set is the obvious next increment and is not claimed here.
- **The material this record draws on has not been through peer review.** `FG-TIDA/themes#42` and `#43` are proposals under discussion, not settled positions, and VR1 is a restatement of their separation argument rather than independent evidence for it.
- **Drafted with AI assistance** under author direction, and red-teamed before posting; the author is responsible for every claim above.

## 11. Version history

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-16 | First draft |
| 0.2 | 2026-11-16 | Position restated as a refinement of R1's unstated accept side rather than an unoccupied space; VR2 premise corrected against R4.2 (scope extension, not a blank); verifier defined against relying party; VR1 attribution corrected to #42/#43; grades redefined so each has a route to being reached and each status maps to a grade; VR4 given a floor, and Case A reclassified as unresolved; R8 count corrected; conformance language added; limitations extended to the posted-comments risk and the proposal status of the three moments |

---

## 中文要点对照

> 英文为权威文本；以下为逐条中文要点，供中文读者对照，非逐句对译。

**这份记录站的位置。** AAR-REQ §1.2 把「依赖方要报什么」写进了自己的范围，R1–R4 也逐个列了**拒绝**的类别。真正空着的不是整块，而是一条：R1 说「光说接受或拒绝不够」，但**从没说一个不 bare 的「接受」要带什么**；§1.3 又把「一致性判定能主张什么」让给了 themes#6 task 3。本文补前一条，不碰后一条。**对 R1–R8 一字不加、一字不改。**

| 条款 | 中文要点 |
|---|---|
| **VR1** | 证据等级描述的是「验证方与证据的关系」，不是记录自带的字段。四档由两个问题定义——**查没查、对什么查**——所以每一档都走得通、每个状态都有对应等级：A 自己查、对能直达且无需信任产出方的源；B 与产出方无关的具名方查、对同类源；C 自己查、对独立于产出方的材料但不在源头；D 没查，只有产出方的说法。等级针对**主张**不针对**行为人**；四档有序但**不可平均**，平均会把最弱那一跳藏起来。 |
| **VR2** | R6 说时效是关系不是属性；R4.2 **已经**要求依赖方记录用了哪个时刻——但只管 tier-2 的资格问题。本条的增量是**范围**不是内容：把「点名一个时刻」从资格问题推广到每一份判定，并把三时刻（行为时／产出方声明时／独立可界定时）作为可选集合。三时刻是 @OlehVasylenko2000 的**提案**（可能成为 R7.2a），不是既成文本，这一点正文已写明。 |
| **VR3** | 「可检查」不等于「已检查」。R7.3 只保证「与产出方无关的人**能**查」，一份没人看过的记录同样满足它。所以每项检查标状态：验证方自做／具名第三方做／仅有断言。与 VR1 是全覆盖映射：A、C 是自做，B 是第三方，D 是断言。 |
| **VR4** | 通过 = 在声明边界内、用声明的检查、在声明的时刻，未发现违规。必带四样：做了什么、**没做什么**（要点名）、边界、时刻。**另有一条地板**：若全部检查都是 C 或 D，结论是「边界内未决」，不是通过——否则「什么都没对源查过」的报告也能凑齐四条伪装成通过，而这正是 VR3 要挡的失效。有了地板，通过才能**被它自己的声明推翻**。 |
| **VR5** | 验证方的报告是下一方要评的东西；一旦被依赖，它就是 R7 意义上的 carried claim，R7 的三项（归属／时刻／防篡改）按其自身条款即已适用。本条不扩张 R7，只指出它本来就够得着报告。推论很窄：不披露自身依据的验证方，产出的是一份归属不明的主张，下一方读不出 VR4 的边界。 |

**三个边界情形。** A：记录可检查但本验证方查不到——按地板判「边界内未决」，既不是通过也不是拒绝（R1–R4 没有对应类，这是 AAR-REQ 类集的缺口，列为开放问题 4）。B：记录对、时刻错——行为时全通过、验证方来看时资格已撤回；把时刻③的结论当时刻①报，正是 VR2 要挡的。C：无记录 ≠ 静默——「没有记录」「有界检索查无」「引用已确立」是三种结论，只有第二种带检索范围和作者。
