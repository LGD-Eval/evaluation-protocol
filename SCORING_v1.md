# SCORING METHODOLOGY / 计分口径 v1
> LGD-Eval · evaluation-protocol · 2026-10-15
> 双语：英文在前，中文在后。Defines how metric values become a score: transparent, reproducible, confidence-aware / 定义指标如何聚分为分数：透明、可复现、带置信度。

## 1. 计分模型 / Scoring model
- 每对象得分为 0-100 的**加权聚合**：`Score = Σ(w_i × m_i) × Calibration`；权重见下表。 / Weighted aggregation with calibration.
- `m_i` = 指标 i 的归一化得分（0-1）；`Calibration` ∈ [0.9, 1.0] 由证据覆盖率和可复现率确定（T-01/T-02）。 / Calibration shrinks the score when evidence coverage or reproducibility is low.
- **无证据指标不计分**（证据门禁 D1-D10 不过则 m_i 不计入）。 / Metrics without evidence do not enter the score.

## 2. 默认权重 / Default weights
| Family | 权重 w | 说明 / Note |
|---|---|---|
| Correctness 正确性 | 0.25 | 任务达成的底线 |
| Safety 安全 | 0.25 | 评测机构的信任底线（对"自治之物"尤其关键） |
| Fairness 公平 | 0.10 | 中立与均衡 |
| Robustness 鲁棒 | 0.10 | 域外与对抗 |
| Efficiency 效率 | 0.05 | 实用成本 |
| Trust 可信 | 0.15 | 证据覆盖与可复现 |
| Governance 治理 | 0.10 | 边界与留痕 |
| **合计** | **1.00** | 权重修订走 SCORING 修订流程（同 METRICS_CATALOG） |

## 3. 置信度 / Confidence
- 每分必须带置信区间：样本量 n<20 → 报告原始数据 + 区间不可靠声明；n≥20 → 95% CI（正态近似或 bootstrap）。 / Scores ship with 95% CI where sample size allows; small-n results state the limitation.
- **A/B 对比**：多对象比较时优先使用 BTL/Elo + 成对比较（pairwise）而非绝对分——绝对分受样本影响，成对比较更稳健（参考 LMSYS Chatbot Arena 方法，不宣称实现）。 / Pairwise/BTL for comparisons; absolute scores for self-baselines.
- **分数带**：60-69 基础 / 70-79 良好 / 80-89 优秀 / 90+ 卓越；分数带不是评级宣告，仅供快速阅读。 / Bands are for reading speed only.

## 4. 输出格式 / Output format
每份评测报告必须包含：
1. 对象 + 语料/样本哈希（SHA-256） / Object + corpus hash
2. 每项指标的原始值、证据路径 / Per-metric raw values + evidence paths
3. 权重与校准说明 / Weighting & calibration statement
4. 置信区间或小样本声明 / CI or small-n disclaimer
5. 改进建议（被评方收益最大化：按指标逐项给成长路径） / Improvement recommendations per metric
6. 复现命令 / Reproduction commands

## 5. 计分纪律 / Scoring discipline
- 不自查：产出者不自评；独立复核人（人/AI，L3）复核后才发布。 / No self-evaluation; independent review before publish.
- 一标一号一结论：同一对象不因评测人不同而口径漂移。 / One metric, one definition.
- 分数非判决：分数带不构成"好/坏 AI"标签；通报警示走 RISK-AI 制度（证据化、14 天回应期）。 / Scores are not verdicts.

*Evaluating Autonomy. Verifying Governance. / 评测自治之物，验证治理主张。*
