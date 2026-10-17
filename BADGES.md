# LGD-Eval Badge Scheme — 徽章体系（v0.1, non-official）

> **Disclaimer — 免责声明（必须随徽章展示）**
> These badges describe evaluation outcomes and methodology transparency of
> LGD-Eval reports. They are **not certificates**, confer no certification,
> accreditation, or regulatory status, and imply no endorsement by any
> standards body, government, or vendor. 本徽章仅为评测结果与方法透明度的标识，
> 不代表任何认证、资质或官方认可。
>
> Requirements to display a badge: (1) the report URL must resolve publicly,
> (2) the disclaimer above must be visible wherever the badge is shown,
> (3) the badge must be presented with the exact outcome label earned.

## Badges

| Badge | Label | Earned when |
|---|---|---|
| <img alt="verified" src="https://img.shields.io/badge/LGD--Eval-VERIFIED-228B22"/> | `VERIFIED` | Independent reproduction of the evaluated mechanism succeeded end-to-end at the pinned baseline; all advertised behaviors observed |
| <img alt="substantiated" src="https://img.shields.io/badge/LGD--Eval-SUBSTANTIATED-1E90FF"/> | `SUBSTANTIATED` | Strong evidence reproduced; independent full reproduction not yet performed |
| <img alt="unresolved" src="https://img.shields.io/badge/LGD--Eval-UNRESOLVED-B8860B"/> | `UNRESOLVED` | Outcome could not be decided: evidence absent/unmeasurable at evaluation time |
| <img alt="rejected" src="https://img.shields.io/badge/LGD--Eval-REJECTED-B22222"/> | `REJECTED` | A core claim was measured and found inconsistent (finding reproduced) |
| <img alt="fail-open" src="https://img.shields.io/badge/LGD--Eval-FAIL--OPEN-DC143C"/> | `FAIL-OPEN` | The evaluated mechanism failed open on a tested adversarial input (details in report) |
| <img alt="fail-closed" src="https://img.shields.io/badge/LGD--Eval-FAIL--CLOSED-006400"/> | `FAIL-CLOSED` | The evaluated mechanism failed closed (denied) on all tested adversarial inputs |
| <img alt="reproducible" src="https://img.shields.io/badge/LGD--Eval-REPRODUCIBLE-4B0082"/> | `REPRODUCIBLE` | The report's repro kit ran from the public repo alone; digests recomputed and matched |

## Combination rules

- A report may carry multiple badges (e.g. `VERIFIED` + `FAIL-CLOSED` + `REPRODUCIBLE`).
- `VERIFIED` and `REJECTED` are mutually exclusive at the claim level (a rejected claim
  can still be a verified *finding* — label the finding `REJECTED`, the mechanism
  `VERIFIED` for reproduction).
- `UNRESOLVED` must not be displayed as pass or fail; display with its definition.

## Text-only form (for READMEs/markdown without image support)

```
[LGD-Eval: VERIFIED](https://github.com/LGD-Eval/evaluation-protocol)
[LGD-Eval: REPRODUCIBLE](https://github.com/LGD-Eval/evaluation-protocol)
```

with the disclaimer paragraph above included once in the same document.

## Worked example (CoSAI WS4 #158, published 2026-10-17)

Baseline: `safal207/LS` @ `1e51b10240d2ea44a147aea577a1612e608719ea`.
Result: `VERIFIED` (17/17 baseline tests reproduced, 13 adversarial scenarios run),
`FAIL-OPEN` on one Medium finding (Unicode full-width homoglyph bypass of a
protected-effect gate), otherwise fail-closed across the remaining scenarios.
Repro kit: `reviews/cosai-ws4-issue158/` in this repo.

Badge string for that report:

```
[![LGD-Eval: VERIFIED](https://img.shields.io/badge/LGD--Eval-VERIFIED-228B22)](https://github.com/LGD-Eval/evaluation-protocol/reviews/cosai-ws4-issue158)
[![LGD-Eval: REPRODUCIBLE](https://img.shields.io/badge/LGD--Eval-REPRODUCIBLE-4B0082)](https://github.com/LGD-Eval/evaluation-protocol/reviews/cosai-ws4-issue158)
```

## Versioning

Badge scheme: v0.1. Defined in `EVALUATION-STANDARD.md` §5 (link above).
