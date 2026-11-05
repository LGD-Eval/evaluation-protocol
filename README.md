# Evaluation Protocol · 评测协议

> **门户 / Portal:** [LGD Hub · 生态超市入口](https://zhaoxinghua09-cell.github.io/lgd-hub/) ｜ LGD 生态（Lifecycle Governance Doctrine）

> 隶属：凡自治之物 · LGD 治理学（Lifecycle Governance Doctrine）· 创造术家族
> 角色：LGD-Eval 评测线 · 关联关系见 [COI 披露](https://github.com/LGD-Eval/LGD-Eval/blob/main/CONFLICT_OF_INTEREST_DISCLOSURE.md)
> 官方英文：Lifecycle Governance Doctrine
> 许可证：CC BY 4.0

## Quickstart · 一条命令复现四个已发布用例结论

```bash
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