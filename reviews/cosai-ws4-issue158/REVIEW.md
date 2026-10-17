# Independent Third-Party Review — LS Agent Trust Runtime v0.1

**Reviewer**: LGD-Eval (independent third-party evaluation; evidence-based verification of governance claims)
**Target**: `safal207/LS` — `prototypes/openai-agent-trust-runtime`
**Baseline commit**: `1e51b10240d2ea44a147aea577a1612e608719ea`
**Date**: 2026-10-17
**Method**: full local reproduction + adversarial vector testing (all 12 review-packet attack scenarios probed; 17 shipped tests re-run; dry-run reproduced)

---

## 1. Reproduction summary (verified)

| Step | Result |
|---|---|
| `pytest -q` (shipped suite) | **17/17 passed** (Python 3.13.13, pytest 9.1.1) |
| `ls-agent-trust-demo --dry-run` | Runs offline; ledger emitted and `verify_ledger()=true` |
| Independent adversarial vectors | 13 scenarios executed; see §3 |

The ten-minute reproduction in the review packet works as documented.

## 2. Executive summary

The prototype's fail-closed core is real and mostly well-built: child-agent binding, single-terminal enforcement, supersession freshness, recovery non-escalation, parent allowlist ceiling, approval-after-result binding, and approval/request digest binding all held under direct probing. Eight of the twelve requested attack scenarios were rejected by design controls.

**One high-value bypass was reproduced** (Finding 1): the policy-identifier normalization claimed by invariant 7 ("Protected-effect normalization") uses case-folding only and does not apply Unicode NFKC folding. Visually-confusable (full-width / homoglyph) effect identifiers can therefore authorize a protected effect — e.g. `deploy` — **without human approval**. This is a genuine gap in the trust boundary, and the fix is one line.

The remaining three items (Findings 2–4) are declared non-claims confirmed by measurement; they are listed with concrete v0.2 hardening suggestions rather than as defects.

## 3. Findings

### Finding 1 — [Medium] Protected-effect gate bypass via Unicode confusable identifiers (violates invariant 7)

**Severity**: Medium (P2). Requires an effect string supplied by a model/tool/integration layer to contain a full-width or homoglyph form *and* a scope/grant recorded in the matching non-canonical form; does not require host compromise or credential theft. Exploit surface is configuration/input-layer ambiguity.

**Violated invariant**: 7 — "Protected-effect normalization — effect identifiers are normalized before scope and approval checks." Normalization is incomplete: `str.casefold()` is applied, but Unicode NFKC folding is not.

**Minimal reproduction** (deterministic, offline):

```python
rt = TrustRuntime()                      # default protected effects include "deploy"
d = rt.issue_dispatch(parent_agent="Coordinator", child_agent="Deploy Agent",
                      task="Deploy the artifact",
                      authority_scope=("ｄｅｐｌｏｙ",))   # full-width in scope
r = rt.submit_result(dispatch_id=d.receipt_id, agent="Deploy Agent",
                     status="COMPLETED", summary="done", evidence=("fixture:build",))
dec = rt.authorize_effect(dispatch_id=d.receipt_id, result_receipt_id=r.receipt_id,
                          effect="ＤＥＰＬＯＹ")            # full-width effect
assert dec.allowed is True      # BYPASS: protected effect, no human approval
assert dec.reason == "allowed"
```

Measured: `"ＤＥＰＬＯＹ".casefold()` → `"ｄｅｐｌｏｙ"` ≠ `"deploy"` (normalization gap confirmed); the effect was authorized with no approval receipt.

**Expected vs actual**: expected — a protected effect (`deploy`, `payment`, `delete`, `merge`, …) always requires human approval and membership in the authority scope after canonical normalization; actual — a full-width confusable spelling of `deploy` is treated as a *different, unprotected* identifier while still matching a visually-identical scope grant, so it is authorized without approval.

**OWASP mapping**: ASI02 (Tool Misuse & Exploitation) — the protected-effect gate is the primary control against undelegated effects; this bypass narrows it. ASI09 (Human-Agent Trust Exploitation) — the human-approval requirement is circumvented.

**Smallest safe remediation**: normalize every policy identifier with Unicode NFKC + case-fold + strip before *both* storage and comparison, e.g. `unicodedata.normalize("NFKC", s).strip().casefold()` in `_clean_identifier` / `_clean_text` (or a dedicated `_clean_policy_identifier`). Optionally reject or flag identifiers containing confusable characters at configuration time. Re-running this vector after the fix must yield `allowed=False`.

**Does it block a public demonstration?**: No — the prototype's core invariants (1–6, 8–10) hold. It should be fixed before v0.2 conformance claims are made.

### Finding 2 — [Informational / boundary confirmed] "Incomplete or interrupted run" cannot be distinguished from a completed run (review-packet scenario 9)

**Measured**: any non-empty SDK `final_output` maps to `COMPLETED` with evidence `openai-agents-sdk:final-output-sha256:<digest>`; `BLOCKED` only for `None`/empty output. No tool-call count, no guardrail/interrupt signal, no agent-chain length is captured into evidence.

**Expected vs actual**: a run that returned text but was interrupted, tool-misused, or partially executed is recorded as `COMPLETED`. This is inside the declared non-claims ("not proof that a live OpenAI API run completed safely", "evidence truth… not verified") but it is the single most consequential integration seam.

**Smallest safe remediation (v0.2)**: include SDK trace/span correlation IDs and a tool-call ledger (count + names) in the evidence tuple; treat "no tool calls recorded but side-effect claimed" as `BLOCKED` unless policy allows no-tool completions. Bind receipts to trace/span IDs as review-packet question 4 asks.

### Finding 3 — [Informational / boundary confirmed] Handoff metadata is model-authored free text (scenario 11)

**Measured**: `DispatchInput.task` and `constraints` are model-generated strings; `bounded_authority` constrains only the authority field. A receipt therefore binds the *claimed* task string, not observed behaviour.

**Expected vs actual**: invariant 1 states a result is "bound to the exact task"; in practice the task is the model's own free-text claim, so a misleading receipt is constructible whenever a model output misdescribes its work.

**Smallest safe remediation (v0.2)**: enforce a structured task contract (finite field set, e.g. goal/scope/exclusions), and bind receipts to SDK trace/span IDs rather than labels only.

### Finding 4 — [Informational / boundary confirmed] Ledger suffix truncation is undetectable without an external checkpoint (scenario 10)

**Measured**: mutation, reordering, and insertion in the supplied ledger are all detected by `verify_records`; truncation to a valid prefix still verifies (`verify_records(truncated) == True`).

**Expected vs actual**: consistent with the declared non-claim ("suffix-truncation detection without an external checkpoint").

**Smallest safe remediation (v0.2)**: anchor the ledger with an external checkpoint (signed hash published to an append-only transparency service, or a periodic externally-pinned summary record) so a valid prefix is distinguishable from the latest state.

## 4. Fail-closed matrix (all 12 review-packet attack scenarios)

| # | Scenario | Result | Control / decision |
|---|---|---|---|
| 1 | Submit as a different agent | **PASS** | `only the dispatched child agent may submit the result` |
| 2 | Reuse a result receipt across dispatches | **PASS** | `result is not bound to this dispatch` |
| 3 | Late work after supersession | **PASS** | superseded dispatch rejected |
| 4 | Recover while relaxing constraints/authority | **PASS** | recovery must preserve task/constraints/scope |
| 5 | Request authority outside parent allowlist | **PASS** | `handoff requested authority outside parent grant` |
| 6 | Protected-effect bypass (Unicode) | **BYPASS → Finding 1** | authorized without approval |
| 7 | Approval before completed result | **PASS** | `human approval requires a completed result` |
| 8 | Approval reuse for different effect/request | **PASS** | digest-bound approval |
| 9 | Incomplete run as COMPLETED | **INFO → Finding 2** | declared boundary; v0.2 recommendation |
| 10 | Ledger tamper/reorder/insert/truncate | **INFO → Finding 4** | tamper/reorder detected; truncation open |
| 11 | Misleading receipt via handoff metadata | **INFO → Finding 3** | declared boundary; v0.2 recommendation |
| 12 | ALLOW → unintended real effect | **INFO** | no transactional effect adapter (declared) |

## 5. Positive observations

- Approval–request digest binding is sound: a mutated payment request (`$10→$10000`, recipient change) was denied with a different digest.
- Recovery re-validation against a live `authority_resolver` is correctly enforced (parent revocation blocks a recovered worker).
- Hash-chained ledger with canonical JSON digests detects in-chain mutation and reordering.
- Packaging, review packet, and reproduction instructions are genuinely runnable — rare and appreciated.

## 6. Artifacts

- Adversarial vector harness (deterministic, offline): `attack_vectors.py` — 13 scenarios, JSON output.
- Shipped test suite: `tests/` — 17 tests, all passing.
- This report.

---
*This review is an independent third-party assessment. It is not an endorsement, certification, or security guarantee. Verified against baseline commit `1e51b10240d2ea44a147aea577a1612e608719ea` on 2026-10-17.*
