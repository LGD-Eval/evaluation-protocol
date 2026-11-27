# 字段映射：UCR 记录 → EU MDR / FDA 申报（R4，Should 级）

> R4 在 UC30 里是 **Should 不是 Must**：记录格式"应当"能映射到申报要求，但不得假装替代法规。本页只做映射说明，不做合规判定。

## EU MDR 2017/745 技术文档（Annex II / Annex IX 审计）

| UCR 字段 | 对应处 | 说明 |
|---|---|---|
| `artefact.id` + `type` | Annex II 1.1 器械描述与文档清单 | 文书标识与类别 |
| `artefact.device.id` / `family` | Annex II 1.1、UDI-DI 关联 | 器械标识，家族用于范围收窄 |
| `artefact.produced_at` | Annex II 1.2 变更历史（日期） | 产出时点 |
| `mandate.id` + `version` | Annex IX 第 2 章 质量管理体系 | 授权身份与版本，对应文件控制中的受控版本 |
| `mandate.grantor.role` | Annex IX 2.2 管理职责 | 授权人角色 |
| `delegation[].sop` | Annex IX 2.1 质量体系程序 | 每跳委派依据的 SOP 编号 |
| `process_state.procedure` + `revision` | Annex IX 2.2 文件控制 | 产出时生效的程序与修订 |
| `evidence[].ref` + `timestamped` | Annex II 6 验证与确认证据 | 证据引用与时间戳；只放哈希不放原件路径 |
| `verdicts[].result` + `reason_code` | Annex IX 2.3 审核记录 | 检查判词与未评估原因，供审核员直接读 |

**缺口要说清**：MDR 没有规定"机器可判定的未评估语义"。本记录是把 Annex IX 的审核实践显式化，不是新增强制项。

## FDA（21 CFR 820 QMSR / 510(k) / PMA 证据索引）

| UCR 字段 | 对应处 | 说明 |
|---|---|---|
| `artefact.hash` | 510(k) 提交件中的文档标识 | 摘要用于确认提交件与受控版本同一 |
| `mandate.scope.artefact_types` | 820.40 文件控制（批准范围） | 授权覆盖的文书类别 |
| `delegation[]` | 820.40 / 820.75 过程确认中的职责链 | 谁在什么范围内做了什么 |
| `process_state.revision` | 820.40(b) 文件变更 | 产出时生效的版本 |
| `evidence[].kind=process` | 820.70 生产与过程控制记录 | 过程证据 |
| `verdicts` 全表 | 820.180 记录保存 / 820.198 投诉与纠正措施档案 | 判词与原因码可直接作为审核索引 |

**注意**：QMSR 已把 820 与 ISO 13485 的术语对齐，但"智能体授权记录"仍不在条文里；本映射是**可消费性**论证，不是合规结论。

## 交叉映射（同一份记录，两套消费）

| 消费方 | 读哪些字段 | 读到什么 |
|---|---|---|
| EU 公告机构审核员 | `mandate`、`process_state`、`verdicts` | 这份文书在产出时的授权与受控状态，以及哪些没评估 |
| FDA 检查员 | `artefact.hash`、`evidence`、`verdicts` | 提交件与受控版本是否同一，检查跑没跑 |
| 内部 QA | `delegation`、`verdicts.reason_code` | 哪一跳范围出问题、哪一项待补评估 |
| 第二方复跑 | 整个 `reproducibility` | 能否在不接触私有状态的情况下得到同一摘要与同一结论 |

一句话：**同一份记录，两个法域各取所需，不需要各写一套。** 这正是 UC30 §3 Cross-border 那条主张的可操作含义。
