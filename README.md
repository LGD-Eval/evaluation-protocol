# Evaluation Protocol · 评测协议

> **门户 / Portal:** [LGD Hub · 生态超市入口](https://zhaoxinghua09-cell.github.io/lgd-hub/) ｜ LGD 生态（Lifecycle Governance Doctrine）

> 隶属：凡自治之物 · LGD 治理学（Lifecycle Governance Doctrine）· 创造术家族
> 角色：LGD-Eval 评测线 · 关联关系见 [COI 披露](https://github.com/LGD-Eval/LGD-Eval/blob/main/CONFLICT_OF_INTEREST_DISCLOSURE.md)
> 官方英文：Lifecycle Governance Doctrine
> 许可证：CC BY 4.0

## Quickstart · 一条命令复现四个已发布用例结论

```bash
git clone https://github.com/LGD-Eval/evaluation-protocol.git
cd evaluation-protocol
python demo/run_worked_examples.py
```

Runs the evidence grader (`tools/evidence-grader.py`, v1.3) over the four
worked examples (A / B1 / B2 / C) and checks the case outcome
(`verification` / `reason_code` / `policy_action`) and the `payload_digest`
against the published expected outcomes — bit-for-bit, zero dependencies,
Python 3.8+.

对四个已发布用例（FG-TIDA/themes#42）做一条命令回归：跑评分器、对账用例结论与
payload 摘要，逐位复现，零第三方依赖。预期输出 `4/4 PASS`。

Self-test（评分器内置自检）: `python tools/evidence-grader.py --selftest`
Interactive demo: `python tools/evidence-grader.py --demo`


## 本仓内容
- **测试专家手册.md**：评测协议正文 —— L0-L13 判据谱系、验证方法学、不自查原则
- **AGENTS.md**：AI 协作入口
- **LICENSE**：CC BY 4.0

## 评测原则
1. 不自查原则：产出者不查自己，验证由独立方执行
2. 可复放：每份结论附完整步骤与证据
3. 分级：P0-P3 判据谱系，阻断项未修复不得发布
4. 中立：评测方与被评测方无控制性利益关系；关联方的评测在报告本体标注为「关联方评测」，其独立性由证据链与复核机制保证（关联关系与隔离机制见 [COI 披露](https://github.com/LGD-Eval/LGD-Eval/blob/main/CONFLICT_OF_INTEREST_DISCLOSURE.md)）

## 评测流程
1. 培训（协议/标准/口径）
2. 独立执行（不采信自查结论）
3. 证据闭环（哈希/时间戳/复放步骤）
4. 独立验收通过方可发布


## Anchored contribution · UC30（FG-TIDA WG0 用例 30 配套）

本条目的相关制品已按冻结根 + DOI 外锚发布，任何人可免凭据取件并按原样复跑。

| 项 | 值 |
|---|---|
| 版本 DOI | https://doi.org/10.5281/zenodo.24548619 |
| 概念 DOI | https://doi.org/10.5281/zenodo.24548618 |
| 版本 | 文本 v0.3 ／ 记录契约 ucr-v0.3 ／ 整包 v16 |
| 附件 | `UC30_巴黎首会_交付包_v16_20261126.zip`，913,945 B ／ sha256 `9ad5dcc0f08bfbf4b6d891dfbf415f5df9faf1707d1e2616324f521fe4324dea` |
| 冻结根（Merkle, 30 叶） | `9959f2ab8f83bf585b7d9d77bd18bae194a378c239e6e362621ea14fc9d8481b` |

包内是记录工具链的最小实现：带逐检查结果（通过／失败／未评估）的载荷、**声明式比对对象 `compared_state`**、
十二例一致性向量，以及 Python 与 Node 两套实现（逐检查结论与摘要值一致）。

复现（**仓库内已含同源副本**，clone 后直接跑，无需先下载附件）：

```bash
cd uc30_impl
python ucr.py selftest                                      # 期望 SELFTEST OK — 12/12（2026-11-27 实测）
python crosscheck.py                                        # 期望 CROSSCHECK OK — 12/12 AGREE
node verify_node.js vectors/case-01-valid.json               # 输出比对 JSON，exit 0
```

`uc30_impl/` 是交付包内同源副本（只去 `.bak` 与 `out/`，清单见该目录 README）。CI `repro-check`
每次推送逐条跑这三条，并跑一条篡改负向探针（必须被抓，否则 CI 红）。

其中两条向量直接指向本协议关心的边界：`case-09-no-compared-state`（记录未声明比对对象 → rejected）、
`case-10-stale-comparison`（比对对象陈旧 → unresolved/defer）。

### 已发布件勘误（原包不改，以保冻结根不变）

1. 包内 `uc30_impl/README.md` 标题写 "reference implementation **v0.2**"、"**八个**一致性向量，8/8"；
   实际为 v0.3、**12 条**向量；2026-11-27 从仓库内 `uc30_impl` 实测 12/12。
2. 同文件"一分钟跑通"第二条 `python mutate.py` 需先跑 `python gen_out.py`（依赖 `out/` 下的记录）。

改动包内任一字节即更换冻结根、断掉与已上线 DOI 的对应关系，故此处只记勘误，不重发。

### 边界（不冒充）

不含撤销检查；判决正确性未证；未对真实流程做仪表化；无第三方人类复跑；
不主张符合 EU MDR / 21 CFR 820 / EU AI Act。

## 精度声明 / Precision statement (2026-11-27)

- 评测引擎与“一键复跑总闸”不在本仓：公开入口在 `LGD-Eval/lgd-gate` 的分支 `ai-index-kit`，
  命令 `python verify_all.py`（7 PASS + 1 SKIP，rc=0；内部语料不随包发布，记 SKIP 而非通过）。
- 公开包 `ai-index-gate/scanner.py` 自检为 **93 规则 / 176 模式**；本地工作分支为 **98 / 189**。
  两者是不同版本，任何把 98/189 说成“公开仓里那份”的表述都不成立。
- 本仓不作“全面超越 / 行业唯一 / 生态闭环”类主张；对外陈述以逐条可复跑、可核对为准。
- 引用与复跑均按“匿名可及”验证：API 200 + 目录树可下载；`git ls-remote` 在 20 秒内可能超时，属通道问题。
