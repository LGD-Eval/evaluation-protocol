# Verifier-side interface to the record requirements

**A linked contribution record to AAR-REQ (`FG-TIDA/themes#46`)**

| | |
|---|---|
| Author | Xinghua Zhao (Steven Zhao), independent expert, GitHub `@zhaoxinghua09-cell` |
| Offered in | Individual-expert capacity, as stated on `FG-TIDA/themes#46` on 29 October 2026 |
| Hosted in | `LGD-Eval/evaluation-protocol` — the public home of the evaluation material this record draws on. Hosting is a publication venue, not an authorship claim; the account relationship is linked in §9. |
| Version | 0.4 — 16 November 2026 |
| Status | Draft for attributed review before the first in-person FG-TIDA meeting (Paris, 30 November – 1 December 2026) |
| Linked work item | AAR-REQ 0.2 — https://tyche-dev.github.io/tida-aar-req/ |
| Licence | CC BY 4.0 |

---

## 0. Terms

**Relying party.** As in AAR-REQ: the party that acts on a claim about an agent after the fact.

**Verifier.** The relying party itself, or an agent acting for it, when it evaluates a record and states a result. This record introduces no second role: wherever AAR-REQ binds a relying party, the obligation falls on the verifier, and the name is used because these clauses are about the act of verifying rather than the act of relying.

**Record-side, rejection-side, accept-side.** R3–R8 constrain what a record must carry. R1–R4 constrain what a relying party reports **when it rejects**. Neither constrains what it reports when it accepts — that is the subject of the clauses below.

**Source.** A party, register or artefact against which a check can be run **without taking the producer's word for the result**. The record is the object checked, not a source: reading it establishes what it says, not whether what it says is true. This definition matters because it is the only thing standing between a verification and a recital.

## 1. Where this record sits

AAR-REQ §1.2 puts two things in scope: requirements on the record, and what a relying party reports from it. R1 requires that a bare accept or reject is not enough. R1–R4 then give the rejection classes content; **the accept side is required to be non-bare but is nowhere given content** — no clause states which checks a report of acceptance covers, or what bounds them.

Two neighbouring clauses come close and stop short, and it is worth being exact about how:

- **R4.4** makes a carried standing answer a claim, subject to R7. So a carried answer already owes attribution, a stated moment and tamper-evidence.
- **R7** governs the properties of any carried claim.

Neither says **what was checked** or **within what boundary** — R7 regulates how a claim is carried, not what an acceptance asserts. That distinction is the whole subject of this record, and it is narrower than "a gap in AAR-REQ": the properties are supplied, the content is not.

§1.3 separately puts "what a conformance verdict asserts and how it is checked" out of scope and assigns it to `FG-TIDA/themes#6`, task 3. This record does not enter that question: it is about a verdict on a **record of an act**, not on an artefact.

**Nothing here adds to or alters R1–R8.** Every clause constrains the verifier's report.

## 2. Scope

- **VR1** — what the verifier reports about each check: who performed it, and against what;
- **VR2** — the moment the verifier evaluated against;
- **VR3** — what a pass may claim, bounded by the checks reported;
- **VR4** — the verifier's report as a claim the next party has to assess.

## 3. Out of scope

- **Decision procedure, thresholds, evidence weighting.** AAR-REQ §1.3 puts how a relying party reaches a class out of scope, and this record does not bring it back in.
- **Encodings, schemas, field names, media types, test vectors.** As in §1.3. The two components in VR1 are **descriptions of what happened, not fields to be implemented**, and no encoding is proposed.
- **Conformance verdicts on an artefact** (`FG-TIDA/themes#6`, task 3).
- **Where authority originates and what may be conferred** (`FG-TIDA/themes#5`).
- **Legal effect.** A pass is a statement about checks performed. It is not a legal opinion and confers nothing.

## 4. Conformance language

Every clause statement about what the verifier does — **states**, **reports**, **names**, **carries**, **says** — is **SHALL** for any report presented as a pass, and **SHOULD** for one presented as unresolved. Where a required statement is omitted, the next party cannot assess the report above the pair "not performed, against none", which is the lowest pair under the within-component order in VR1. Two further consequences follow from the clauses themselves rather than from this section: an asserted check cannot support a pass (VR3), and a pass whose boundary is undeclared cannot be withdrawn and therefore cannot be relied on (VR3).

## 5. The clauses

Attribution follows AAR-REQ Table 2.1: each clause names who proposed it and, in brackets, who refined it. Where a clause restates an argument made elsewhere, the origin is named first and the restatement is not presented as an independent proposal.

### VR1 — Each check is reported by who performed it and against what

*Proposed by @zhaoxinghua09-cell. The separation of evidence quality from authorization validity is `FG-TIDA/themes#42`'s argument, restated in `#43`, published under the LGD-Eval account, with @dakleyer's refinements; this clause applies it to the AAR case and does not claim the argument.*

A record can be complete and still support nothing, because what a report supports depends on what the verifier did and what it did it against. Both parts are reported, as a pair — not as a single rank:

| Component | Values |
|---|---|
| **Performed by** | the verifier / a named party / not performed (asserted) |
| **Against** | source (per §0) / corroborated material, not at source / none |

The values do not combine freely: where nothing was performed there is nothing to check against, so "not performed" pairs only with "none". The pairs that can occur are five:

- performed by the verifier, against source;
- performed by the verifier, against corroborated material;
- performed by a named party, against source;
- performed by a named party, against corroborated material;
- not performed, against none.

**No order is claimed between the pairs.** The values within each component are ordered — performed before not performed, source before corroborated before none — and that within-component order is the only one used below. Ordering the pairs against each other would have to decide, for instance, whether a named party's check against source outranks the verifier's own check against corroborating material, and any answer to that is a policy choice the group has not made (open question 1).

Two points about what the pair does **not** say:

- **It does not grade the actor.** A report about a claim says nothing about whether the actor's authorization was valid. Keeping the two apart is `#42`'s argument, and VR1 reports only the first.
- **It does not grade the record.** The values describe the verifier's relation to the evidence, not a property the record carries. A grade assigned by a producer would describe how the producer evaluated the record, which is a different object and is not what a later party needs.

Corroboration is deliberately weaker than a check at source: corroborating material cannot distinguish an independent source from a shared upstream one, which is the case `FG-TIDA/themes#60` raises. Where a report rests on corroboration, it says so, and the next party can see that the independence question is open.

### VR2 — The verifier states which moment it evaluated against

*Three moments: @OlehVasylenko2000 (12 November 2026), recorded in AAR-REQ §2.1 against open question 12 as a **possible** R7.2a and therefore not yet text. The obligation to name one for every verdict, rather than for the standing question alone, is @zhaoxinghua09-cell's.*

R6 makes freshness a relation, not a property. R4.2 already requires a relying party to record which moment it used — for the tier-2 standing question (R4.1–R4.3). Outside that question the requirement does not run, and a verdict whose moment is unstated cannot be reproduced by a later reader: they cannot tell which question was answered.

So the verifier names one of three:

1. **the moment of the act** — the moment the record describes;
2. **the moment the producer states for a claim** — carried under R7.2;
3. **an independently bounded moment** — which establishes only that the record existed no later than that time, and is not the freshness relation of R6.

The increment over R4.2 is scope, not substance: R4.2 covers standing, VR2 covers every reported verdict. A verdict at moment 1 and one at moment 3 are not the same object even when every field is identical, because the effective state that governed the act (R8.5) may have changed between them.

The verifier also reports whether rechecking was possible, taking R6's "means, if any, of rechecking" as given. Where no means exist, the report says so: an absent means of rechecking is a finding, not a blank.

### VR3 — A pass claims no violation found within a stated boundary

*Proposed by @zhaoxinghua09-cell, carrying forward the question posed in `FG-TIDA/themes` PR #28.*

A pass carries four statements, and is incomplete without any of them:

1. the **checks performed**, with VR1's pair for each;
2. the **checks not performed** — named, not implied;
3. the **boundary** within which the checks ran;
4. the **moment used** (VR2).

A pass then means no more than this: *no violation was found within this stated boundary, using these checks, at this moment.* It does not mean the act was authorized, that the record is true, or that the delegation was sound. AAR-REQ says as much one level down — "R7 does not make a claim true" — and the same restraint holds at the verdict.

**A pass also has a floor.** At least one reported check must be performed, against source. Without the floor, a report in which every check was corroborated or asserted could state all four things and present itself as a pass — and nothing in the report would distinguish it from a report in which something was actually checked. The same property that makes corroboration weaker than source in VR1 is what keeps it from carrying a pass: corroboration cannot establish that the evidence is independent of the producer.

The floor is what makes a pass **withdrawable by its own declaration**: a later party can withdraw it by showing one check inside the declared boundary that was not performed as reported, without relitigating the facts. A pass that declares no boundary cannot be withdrawn that way, and therefore cannot be relied on — only believed.

AAR-REQ names rejection classes and not accept classes. Whether "pass" and "unresolved within boundary" should become named classes is the group's decision (open question 3).

### VR4 — The verifier's report is a claim the next party has to assess

*Proposed by @zhaoxinghua09-cell. The recursion in R7 is @OlehVasylenko2000's; this applies it one level up.*

VR3 makes the verifier's report the thing a later party relies on. Once it is relied on, it is carried, and R7 reaches it by its own terms — attribution (R7.1), a stated moment (R7.2), tamper-evidence a party with no relationship to the producer can check (R7.3). This record does not extend R7. It notes that R7 already covers the case, and that a verifier which has not disclosed the basis of its report has produced a claim the next party cannot assess above the lowest VR1 pair.

This is not a demand that verifiers publish. It is a statement about what an undisclosed basis costs the next party.

## 6. Interface table

What the verifier reads from each record-side clause, and what it reports in return. The left column is AAR-REQ's; the right column is this record's.

| AAR-REQ | What the verifier reads | What the verifier reports |
|---|---|---|
| R1, R2 | the rejection class and the reported cause | VR1 pair for the claim about the cause. Where nothing was rejected, VR3 governs, since R1–R4 give no content to an accept |
| R3 | the four tier-1 classes are decidable from the record and the relying party's own state | which classes it decided, and which it could not |
| R4, R4.1–R4.3 | whether continued standing is checkable, and which moment the relying party used | VR2 moment, named rather than inherited, extended from standing to every verdict |
| R4.4, R7 | the properties a carried answer owes | satisfied by VR4's application of R7 to the report itself |
| R5 | negative and null assertions are claims like any other (proposed by @cgorlla; null case @OlehVasylenko2000, refined by @zhaoxinghua09-cell) | VR1 pair per assertion; a null assertion is reported, never skipped |
| R6 | the moment the assertion was true, and the means of rechecking | VR2 moment used, and whether rechecking was possible |
| Absence and silence | which of the three states holds | which state was established, and the scope and author of any bounded search |
| LR1–LR5 | which lineage case holds | the case reported, with its VR1 pair |
| R8, R8.1–R8.5 | four things across five sub-clauses: the act, the execution that performed it, that execution's supported relation to a logical agent where one exists, and the effective state that governed the act at that time | which of the four it established, at which moment (VR2), with a VR1 pair for each |

## 7. Three boundary cases

**Case A — the record is readable but nothing can be checked against source.** The verifier can read the record and can reach no source. Every check it reports is corroborated or asserted, so by VR3's floor the result is **unresolved within the boundary**, not a pass. It is also not a rejection: R1–R4's classes do not apply, because nothing was found to be wrong. The report states both facts and leaves the result unclassified — a gap in the class set, not in this record (open question 3).

**Case B — right record, wrong moment.** Every tier-1 check passes at the moment of the act; standing was withdrawn before the verifier looked. Reporting a pass at moment 3 while presenting it as a statement about moment 1 is the error VR2 exists to prevent. The verdict is about the moment named, and the report must let a reader see which — otherwise the reader supplies the wrong one.

**Case C — absence is not silence.** No record at all, a bounded search that returned nothing, and a reference that was established are three different findings. Only the second carries a scope and an author. A report that collapses them reads as "nothing wrong", and the correct reading differs in each case: nothing was recorded; nothing was found within a stated search; the thing was established.

## 8. Open questions

1. **Is there an order between the nine pairs?** This record deliberately claims none, and VR3's floor uses only "performed, against source". If the group needs a single rank for comparison, the ordering is a policy decision and should be taken as one. *(@zhaoxinghua09-cell)*
2. **Does the floor belong at "performed, against source", or lower?** A named party's check against source is admitted by the floor; a verifier's own corroboration is not. That asymmetry follows from independence, not from the verifier's effort, and it is worth testing against a case where the verifier is the only party with access. *(@zhaoxinghua09-cell)*
3. **Should "pass" and "unresolved within boundary" become named classes in AAR-REQ?** VR3's floor produces a result R1–R4 do not name. Either the class set grows, or the report leaves it unclassified as Case A does. *(@zhaoxinghua09-cell)*
4. **Does VR4 bind all verifier output, or only published reports?** Binding all output is stronger and harder to meet, and I would rather the group choose it knowingly. *(@zhaoxinghua09-cell)*
5. **Where does the boundary in VR3 come from?** If a minimum boundary is named in FG-TIDA's output, this record should cite it rather than let each verifier declare its own. *(@zhaoxinghua09-cell)*

## 9. Provenance

- AAR-REQ 0.2, web — https://tyche-dev.github.io/tida-aar-req/
- AAR-REQ 0.2, PDF — https://tyche-dev.github.io/tida-aar-req/specification.pdf
- Originating thread — https://github.com/FG-TIDA/themes/issues/46
- Verifier-side charter, for the theme from #27 — https://github.com/FG-TIDA/themes/pull/28
- Evidence grading, separating evidence quality from authorization validity — https://github.com/FG-TIDA/themes/issues/42
- Evidence-graded authorization verdicts — https://github.com/FG-TIDA/themes/issues/43
- Independence between references — https://github.com/FG-TIDA/themes/issues/60
- Conformance verdict scope, handed off by AAR-REQ §1.3 — https://github.com/FG-TIDA/themes/issues/6
- Author identity — https://orcid.org/0009-0001-0512-1237
- Account relationship and conflict-of-interest disclosure — https://github.com/LGD-Eval/evaluation-protocol/blob/main/CONFLICT_OF_INTEREST_DISCLOSURE.md

## 10. Limitations

- **Only the clause table and the scope chapter were read.** AAR-REQ states that its clause text stands in two comments on `FG-TIDA/themes#1` and that where the table differs, those comments govern. This record was written against the table in §2 and the scope in §1, and has **not** been reconciled against those comments. Where they differ, they win; VR2 should be re-read against them first.
- **The three moments are a proposal, not text.** AAR-REQ §2.1 records them against open question 12 as a possible R7.2a. If the group settles differently, VR2's enumeration changes with it.
- **The two components are a design that has not been tested.** Nine pairs can be named, but whether two readers assign the same pair to the same facts is untested. The likely disagreements are whether a given artefact counts as source under §0, and whether a check was performed by the verifier or by a party acting for it — a distinction §0 does not draw and probably needs to.
- **The floor is a judgement, not a derivation.** "At least one check performed against source" is where I would put it; a group that wants lower can lower it, and the case for doing so is open question 2.
- **No consequence semantics beyond §4.** The clauses say what a report must state and what the next party can do without it. They do not say what happens to a verifier that states nothing; that is AAR-REQ's conformance question, which §1.3 moves elsewhere.
- **No implementation accompanies this version.** The reference implementation covers the evidence-gated state machine, not the report format these clauses describe.
- **The material this record draws on has not been through peer review.** `FG-TIDA/themes#42` and `#43` are proposals under discussion, and VR1 restates their separation argument rather than providing independent evidence for it.
- **Drafted with AI assistance** under author direction, and red-teamed in three independent passes before posting; the author is responsible for every claim above.

## 11. Version history

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-16 | First draft |
| 0.2 | 2026-11-16 | Position restated as a refinement of R1's unstated accept side; VR2 premise corrected against R4.2; verifier defined; VR1 attribution moved to #42/#43; VR4 given a floor; conformance language added |
| 0.3 | 2026-11-16 | Grade lattice replaced by a two-component report, removing an unclaimed ordering and two nameless combinations; VR1 and the former VR3 merged, so each reported value has one home; "no clause says" corrected — R4.4 and R7 supply properties, not content; **source** defined in §0; VR3's floor reason aligned with the rule; conformance language extended to every obligation verb |

---

## 中文要点对照

> 英文为权威文本；以下为逐条中文要点，供中文读者对照，非逐句对译。

**这份记录的位置。** R1 要求「只说接受或拒绝不够」，R1–R4 又把**拒绝**的类别逐条给了内容；**接受这一侧被要求「不 bare」，却始终没被给内容**——没有条款说一份接受报告覆盖了哪些检查、边界在哪。R4.4 和 R7 在附近，但只到一半：R4.4 让「被携带的资格答复」受 R7 约束，R7 管的是**怎么携带**（归属、时刻、防篡改），不是**查了什么、边界在哪**。这就是本文的全部题目，比「AAR-REQ 有个洞」要窄：属性已给，内容未给。§1.3 另把「一致性判定能主张什么」让给 themes#6 task 3，本文不进去。

| 条款 | 中文要点 |
|---|---|
| **VR1** | 每项检查报**两个分量**，不是打一个分：**谁查的**（验证方／具名第三方／没查即断言）× **对什么查的**（源头／佐证材料（不在源头）／无）。九个组合，个个有名，**不主张彼此排序**——排序等于替组里做政策决定（开放问题 1）。两条边界：「source」§0 定义为「无需采信产出方的说法即可运行的对照物」，**记录本身不是 source**（读记录只能知道它说了什么，不能知道它说的是不是真的）；佐证**刻意弱于源头**，因为佐证分不开「独立来源」和「共上游」——正是 #60 那个问题。 |
| **VR2** | R6 说时效是关系；R4.2 **已经**要求记录用了哪个时刻，但**只管 tier-2 资格问题**。本文的增量是**范围**：推广到每一份判定。三时刻（行为时／产出方声明时／独立可界定时）是 @OlehVasylenko2000 的**提案**（可能的 R7.2a），不是既成文本，正文写明。还要报「能否复核」——没有复核手段本身是结论，不是空白。 |
| **VR3** | 通过必带四样：做了什么检查（含 VR1 两分量）、**没做什么**（点名）、边界、时刻。通过的含义**不多于**：在该边界内、用这些检查、在该时刻，未发现违规。**另设地板**：至少一项检查是「做了、且对源头」——否则一份全部靠佐证或断言、却凑齐四样的报告，也能自称通过，而且看不出区别。有了地板，通过才能**被它自己的声明推翻**。 |
| **VR4** | 验证方的报告一旦被下一方依赖，就是被携带的主张，R7 按其自身条款即已适用（归属／时刻／防篡改）。本文**不扩张** R7，只指出它本来就够得着；不披露自身依据的验证方，产出的是一份下一方无法评到最低一档以上的主张。这不是要求公开，是说未公开的代价由下一方承担。 |

**三个边界情形。** A：记录可读但无可对源——按地板判「边界内未决」，既不是通过也不是拒绝（R1–R4 无对应类，属类集缺口，开放问题 3）。B：记录对、时刻错——把时刻③的结论当时刻①报，正是 VR2 要挡的。C：无记录 ≠ 静默——「没有记录」「有界检索查无」「引用已确立」三种结论，只有第二种带检索范围和作者。
| 0.4 | 2026-11-16 | R1–R8 split into rejection-side (R1–R4) and record-side (R3–R8) so the accept side is defined negatively and accurately; the five occurrable VR1 pairs enumerated, with a within-component order stated and no order between pairs; §4 conformance language extended to every obligation verb and its "stated once" claim removed |
