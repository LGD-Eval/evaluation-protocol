# UCR — Use Case 30 record toolchain (reference implementation v0.3/v0.4, record schema v0.3 and v0.4)

一条记录，把四个事实绑在一起，离线可验。这是 FG-TIDA `use-cases#30` 第 5 节 R1–R3、R5 的最小可运行实现，第 6 节的"可判定计数"是它唯一的度量口径。

**边界先写清楚**：这是供讨论的参考实现，不是产品、不是部署、不做第三方验证的主张。样例中的器械与文书是合成数据（`D-114`、`CIA-2026-014`），不对应任何真实制造商。

## 一分钟跑通

```bash
python ucr.py selftest                     # 十二个一致性向量，12/12 应通过
python mutate.py                           # 逐字段突变：覆盖字段必动摘要，边界字段必不动
python ucr.py gen-vectors --dir vectors    # 生成向量文件
python ucr.py emit manifest.json -o record.json
python ucr.py verify record.json --state current_state.json -o report.json
python crosscheck.py                       # Python 与 Node 两实现逐项对照，12/12 应一致
node verify_node.js vectors/case-01-valid.json   # 不装 Python 也能验
```

退出码：`0` verified · `2` unresolved · `3` rejected · `1` 输入错误。这样 CI 与人工评审都读得懂。

浏览器侧另有零依赖 demo，双击即开：`demo/verify-demo.html`。它在浏览器里用自带的 SHA-256 重算摘要，不联网、不引 CDN。

## 与信封、决策层对接（不是替代）

```bash
python ucr.py scitt out/case-01-valid.record.json --state out/case-01-valid.state.json
python ucr.py authzen demo/authzen-decision.json
```

- `scitt` 输出一份**登记请求**形状的 statement：`payload.record_digest_sha256` 为全长摘要，附 `check_results`。`receipt` 恒为 `null`——登记不等于检查跑过，本命令不冒充回执。
- `authzen` 把一条 AuthZEN 决策（SARC + decision）折成 `kind: interop` 的证据项，带 `policy_identity`、`decision_id`、`decided_at`；`permit` 不代表合规结论，`deny` 不得被写成 allow。
- 两处**均未与真实 TS / PDP 联调**，只对齐了形状与字段。

## 记录长什么样（节选）

```json
{
  "artefact": {"id": "CIA-2026-014", "type": "change-impact-assessment",
               "hash": "sha256:6f1c2d9a4b7e8f10", "produced_at": "2026-05-20T09:12:00Z"},
  "mandate": {"id": "M-2026-014", "version": "3",
              "grantor": {"role": "manufacturer-compliance-owner"},
              "grantee": {"agent_id": "A-LEAD-07"},
              "scope": {"workflow": "change-impact-assessment", "device_family": "IVD"}},
  "delegation": [{"grantor_agent": "A-LEAD-07", "grantee_agent": "A-T1", "sop": "QP-8.2",
                  "scope": {"artefact_types": ["change-impact-assessment"]}}],
  "process_state": {"procedure": "QP-8.2", "revision": "8.2"},
  "evidence": [{"id": "EV-1", "kind": "signed-credential", "ref": "sha256:aa01bb02",
                "reproducible": true, "timestamped": true}],
  "verdicts": [{"check_id": "C4_state_version", "result": "not_evaluated",
                "reason_code": "status_unavailable"}],
  "reproducibility": {"payload_digest": "…"}
}
```

## 七项检查

| 检查 | 判什么 | 失败/未决时的原因码 |
|---|---|---|
| C1_schema | 结构完整、版本对 | schema_mismatch / schema_missing_field |
| C2_digest | 摘要能被任何人按公开约定重算 | digest_mismatch |
| C3_mandate_chain | 每一跳委派只收窄、不放宽 | scope_escalation |
| C4_state_version | 产出后的受控状态变化有没有被评估 | status_unavailable / state_change_unrecorded |
| C5_evidence_present | 证据有引用、且该可复现的确实可复现并带时间戳 | missing_evidence |
| C6_verdict_complete | 七项检查是否都有判词，缺一项即为 not_evaluated | verdict_missing |
| C7_no_private_state | 记录里不含指向产出方私有状态的字段 | private_state_reference |

结论只有三态：`verified` / `unresolved` / `rejected`，配套处置动作 `allow` / `defer` / `deny`。"未评估"是一等公民，不会被折成通过。

## 摘要约定

与 LGD-Eval 结论文件同一约定（`EVALUATION-STANDARD.md §2.3`）：

```
sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False))[:16]
```

覆盖字段：`schema, artefact, mandate, delegation, process_state, evidence, verdicts`（v0.2 起把声明的 schema 标识也绑进来，改版本会同时破 C1 与 C2）。`attestation` 不进摘要——重签不应让 payload 失效——它的保护来自信封签名（`ucr.py scitt`），不来自 payload 摘要。

**版本演进（v0.1 → v0.2）**：v0.1 把 schema 标识放在摘要之外，改声明版本时摘要不变、只由 C1 拦。`mutate.py` 的逐字段突变测试发现了这个边界，v0.2 将其关闭。v0.1 的结构文件留档在 `schema/ucr-v0.1.schema.json`，仅备查，不再用于校验。

## 八个一致性向量

| 向量 | 期望 | 触发的检查 |
|---|---|---|
| case-01-valid | verified / allow | 全部通过 |
| case-02-scope-escalation | rejected / deny | C3 |
| case-03-state-unevaluated | unresolved / defer | C4 |
| case-04-evidence-weak | unresolved / defer | C5 |
| case-05-tampered | rejected / deny | C2 |
| case-06-schema-version | rejected / deny | C1（内部一致，仅因声明版本不被受理） |
| case-07-private-state | rejected / deny | C7 |
| case-08-verdict-missing | unresolved / defer | C6（缺一项必检判词） |

**一处需要说明的设计**：八例的 `artefact.hash` 是同一个值 `6f1c2d9a4b7e8f10`（`case-05` 除外，它故意改它）。这不是占位符，而是"**同一份报告、八种治理情形**"——同一个受审对象在不同授权链、不同程序状态、不同证据强度下应当得到不同结论，差异全部来自治理侧而不是内容侧。这样做的原因是：如果每例换一份 artefact，就无法分辨结论变化是由内容引起的还是由治理引起的。写论文或做审计时，这一点常被问到。

## 目录

```
ucr.py                 单文件 CLI（emit / verify / selftest / gen-vectors / scitt / authzen）
verify_node.js         Node 独立验证器（照公开约定另写，不读 ucr.py）
crosscheck.py          两实现逐向量对照（结论、摘要、每项检查）
mutate.py              逐字段突变：覆盖字段必动摘要，边界字段必不动
gen_out.py             从向量一键重建 out/
schema/ucr-v0.2.schema.json（v0.1 留档备查）
vectors/               八个向量，由 ucr.py gen-vectors 生成
out/                   实跑产生的记录、报告、statement、authzen 证据
demo/verify-demo.html  浏览器端离线验证器（零依赖）
demo/verify-demo.png   实截图
demo/authzen-decision.json  一条示例 PDP 决策
docs/FIELD_MAP.md      字段到 EU MDR / FDA 申报条的映射（R4，Should 级）
docs/IMPLEMENTATION_PLAN.md  落地路径、角色、退出判据
```

## 不做的事（防止越界承诺）

- 不做身份体系、不签令牌、不做运行时策略执行——那是 SCITT / AuthZEN / IAM 的地盘。
- 不做申报文书生成器；只给证据绑定与判词。
- 不对接任何真实制造商系统；接入需要对方 QA 与 IT 参与，见 `docs/IMPLEMENTATION_PLAN.md`。


## v0.4：撤回检查（C8）与评估者独立性（声明字段）

v0.4 = v0.3 + 一项必检 + 一个必填声明字段。**只在 `record.schema = ucr/record/v0.4` 时生效**，v0.3 的十例行为与字节不变，所以会前材料里"七项检查 / 十个向量"的口径不会被这条改动弄假。

- `C8_revocation_checked` — 授权在记录产出之后可能被撤回，而记录本身无法自证"当时还有效"。判定由**依赖方**给出的撤回状态决定：
  - 未带撤回状态 → `not_evaluated` / `revocation_unchecked`（挡住肯定结论）
  - `status=revoked` → `fail` / `mandate_revoked`
  - `status=active` 但无 `checked_at` → `not_evaluated` / `revocation_unverified`
  - `status=active` 且有时间与来源 → `pass`
- `evaluator` — `{id, relation ∈ INDEPENDENT | SAME_ORGANISATION | SELF}`。这是**声明**，不是证明：写 `SELF` 不会被拒，但报告里一眼能看见，评审方自己决定这份记录值多少。任何一方都能把 `relation` 写成 `INDEPENDENT`——所以它永远不能替代外部门禁里的"具名外人实测"。

两例新向量：`case-11-revoked`（拒绝）、`case-12-revocation-unchecked`（不判定）。

已知不覆盖（写在这里，不让它变成隐含主张）：撤回检查只覆盖"授权被撤"，不覆盖"器械批次被召回"；独立性只到声明层，没到利益冲突核验；820.35(a) 投诉与 820.45(b) 标签放行两条法规仍未映射。


## 占位符守卫（2026-11-26 补）

模板里如果还留着 `TODO`，`emit` 会**拒收**并列出行号：

```
python ucr.py emit lot-intake-template.json -o rec.json
refusing to emit: 16 unfilled placeholder(s): /artefact/hash, /mandate/id, ...
```

为什么必须这样：七项检查全是结构性的，`"hash": "sha256:TODO"` 形式完全合法，所以一份填满占位的记录会被算成 **7/7 pass、verified、allow**。这正是本约定要防的那种"看起来很整齐的通过"。

- `verify` 不新增检查（对外仍是七项），但如果记录里还有占位符且其余全过，**结论降为 `unresolved` / `defer`**，并在报告里给 `placeholder_warnings`。
- Python 与 Node 两实现对这类记录给同一结论（实测 python exit 2 / node exit 2）。
- 十例向量与 v0.4 两例都不受影响：12/12 仍一致。
