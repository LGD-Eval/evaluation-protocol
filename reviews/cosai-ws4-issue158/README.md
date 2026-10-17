# Independent Third-Party Review — CoSAI WS4 issue #158 target

This directory archives the independent adversarial review performed by
**LGD-Eval** (independent third-party evaluation) of the review target named in
[CoSAI WS4 issue #158](https://github.com/cosai-oasis/ws4-secure-design-agentic-systems/issues/158)
(`safal207/LS` — `prototypes/openai-agent-trust-runtime`, baseline
`1e51b10240d2ea44a147aea577a1612e608719ea`).

## Contents

| File | Purpose |
|---|---|
| `REVIEW.md` | Full review: findings, fail-closed matrix, remediation (English) |
| `attack_vectors.py` | Deterministic offline harness — all 12 review-packet attack scenarios + Unicode/ledger probes. JSON output. |

## Reproduce

```bash
git clone https://github.com/safal207/LS.git
cd LS && git checkout 1e51b10240d2ea44a147aea577a1612e608719ea
cd prototypes/openai-agent-trust-runtime
python3.11 -m venv .venv && . .venv/bin/activate
python -m pip install -e '.[dev]'
pytest -q                     # shipped suite: 17 passed
python /path/to/attack_vectors.py   # independent vectors: JSON result
```

## Key result

- 8 of 12 review-packet attack scenarios fail closed as designed.
- **Finding 1 (Medium)**: protected-effect gate bypass via Unicode confusable
  (full-width/homoglyph) identifiers — invariant 7 normalization gap;
  one-line NFKC fix.
- Findings 2–4: declared non-claims confirmed by measurement, with v0.2
  hardening suggestions (SDK trace binding, structured task contracts,
  external ledger checkpoint).

*Independent assessment — not an endorsement, certification, or security
guarantee.*
