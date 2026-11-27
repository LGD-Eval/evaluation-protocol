# 缺席语义对照：我们的 reason_code ↔ SCITT AI-agent receipt 的四态

参照 `draft-noa-scitt-ai-agent-receipt-01` §8.3（复核见 `../../../17_现状复核_20261126.md`）。本页只做映射，不改 schema——会议前不动结构。

## 映射表

| 我们的 `reason_code` | 字段 | 最接近的四态 | 是否等价 |
|---|---|---|---|
| `not_run` | verdicts[] | NOT_CLAIMED | 等价：生产者没作任何声明 |
| `verdict_missing` | C6 | NOT_CLAIMED | 等价：必检项没有出现在判词集里 |
| `status_unavailable` | C4 | NOT_PROVIDED | 接近，不等价：他们是"未提供可接受证据"，我们是"未做评估" |
| `missing_evidence` | C5 | NOT_PROVIDED | 接近，不等价：同上 |
| `no_state_reference` | C4 | NOT_PROVIDED | 接近：没有状态参照即无法提供证据 |
| `schema_mismatch` / `digest_mismatch` / `scope_escalation` / `state_change_unrecorded` / `private_state_reference` | C1/C2/C3/C4/C7 | 无对应 | 这些是**失败**，不是缺席；四态里没有 fail 语义，由 verdict 的 BLOCKED 承载 |

## 我们缺的两态（已登记的缺口）

| 四态 | 我们的现状 | 为什么值得补 |
|---|---|---|
| INDETERMINATE | 无 | 证据给了、但不能定论——现在会被压成 `missing_evidence` 或 `status_unavailable`，语义偏粗 |
| NOT_APPLICABLE | 无 | 某项检查对该文书不适用——现在只能"不做判词"，会被 C6 记成缺失，属误报 |

补法（P1 之前，不动结论三态）：在 `reason_code` 枚举里加 `indeterminate` 与 `not_applicable`，C6 对 `not_applicable` 不计入缺失。这样仍保持"缺席不入 pass"，只是把缺席细分。

## 会议口径

被问到映射时的答法：**"按四态对齐了，两个我们还没有——INDETERMINATE 与 NOT_APPLICABLE，已作为缺口登记，不在会上临时补。"**

## v0.3 追加：`compared_state` 与 absence 的关系

- 没有 `compared_state`：不是「未评估」，是**记录不成立**（C1 拒）。这条比 absence 更硬，因为缺字段就无法谈比对。
- 有 `compared_state` 但状态已移动、且未给 C4 判决：`not_evaluated` + `status_unavailable`。
- 有 `compared_state`，而依赖方手里的状态更新：`not_evaluated` + `stale_comparison`（defer，不擅自更新）。
- 撤销与判决真伪仍无检查覆盖——它们不在 absence 表里，属「本版不覆盖」，写进文本 §6，不得靠 absence 掩盖。
