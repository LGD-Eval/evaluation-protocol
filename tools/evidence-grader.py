#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LGD-Eval Evidence Grader — evidence-graded assessment engine for agentic AI trust.
LGD-Eval 证据分级器 — 面向代理 AI 可信度的证据分级评估引擎。

Purpose / 用途
---------------
Runnable reference implementation for ITU-T FG-TIDA contribution C2
(Assessment Criteria and Benchmarks for Trustworthy Agentic AI Systems),
ToR 3.4 / 4.5. It turns structured evidence into domain-level,
defensible assessment conclusions — no composite scores, evidence-first,
reproducible output.

供 FG-TIDA C2 贡献稿使用的可运行参考实现（对应 ToR 3.4 / 4.5）。
将结构化证据转换为域级、可辩护的评估结论——禁止复合分、证据优先、输出可复现。

Evidence levels / 证据分级（GRADE 适配）
----------------------------------------
V = Verified / independently reproduced（已独立复现）
S = Strong / converging method-level evidence（强方法证据）
M = Moderate / partial reproduction or single method（中等）
L = Limited / observation or single source（有限）
P = Pending / not yet testable（待定）

Failure semantics / 失败语义（v1.1 新增，对应 FG-TIDA use-cases#27 建议）
------------------------------------------------------------------------
每个证据项与每个域输出 failure_class，四态：
- quarantined（隔离）: malformed input — missing claim or invalid grade（输入畸形：缺声明或非法级别）
- rejected（拒绝）   : evidence validly asserted but grade=P (pending, not yet testable)（声明合法但尚不可判定，拒绝采用）
- unresolved（未决） : evidence exists but the link is not confirmable — verifiable kinds
                       without reproducible/timestamped evidence, or an empty domain
                       （证据存在但链路未确认：可验证类证据缺少可复现/时间戳，或空域）
- none（无失败）     : evidence accepted at face value（证据正常采用）
聚合规则：overall_failure_class 取最严重类（quarantined > rejected > unresolved > none）。

Authorization validity / 授权有效性维度（v1.2 新增，对应 FG-TIDA themes#42 评审反馈）
-----------------------------------------------------------------------------
证据分级与授权有效性是两个独立维度（见 FG-TIDA/use-cases#27 讨论与 themes#42）。
输入 JSON 可选携带 case 级 authorization 对象：
- result（必填）: verified / unresolved / rejected
- reason_code（v1.3 起必填）: 机器可读原因码，见 REASON_CODES
- reason（必填）: 人读说明
- relying_party_action（可选）: 依赖方可执行动作
- policy_action（v1.3 起必填）: allow / defer / deny / exclude（取 EVALUATION-STANDARD.md §2.2）
关键语义：授权信息缺失（unresolved）绝不等于已证实越权（rejected）。

Case outcome / 用例结论（v1.3 新增，对应 FG-TIDA use-cases#27 @wolfbrother 2026-10-23 反馈）
--------------------------------------------------------------------------------------------
v1.2 的结论里只有一个 `verdict`，它是**六域证据覆盖度**判词（六个域里有几个达到 V/S），
不是用例结论。一个只覆盖 1—2 个域的用例，`verdict` 必然是 `Insufficient evidence`，
哪怕它的授权结论是 `verified`——程序若读 `verdict` 当结论，会把正例读成"证据不足"。

v1.3 起把两件事分开写：
- `outcome.verification` : 用例结论，三态 verified / unresolved / rejected，**这是要读的字段**；
- `verdict`              : 保留原义（六域覆盖度），并由 `scopes` 显式标注其口径。

同时把"策略动作"从"验证结论"里拆出来（@wolfbrother 的第三点）：
- `quarantined` 不再出现在 authorization.result 里——它是处置动作，不是验证结论；
- 处置动作统一进 `policy_action`，**直接采用 EVALUATION-STANDARD.md §2.2 已公布的四个词**：
  allow / defer / deny / exclude（原文的 ALLOW / DEFER / DENY / EXCLUDE）。
  不再另造一套（v1.3 起；此前只把动作写成自由文本 `relying_party_action`，机器不可读）。
  刻意**不用** reject 当动作名，避免与结论词 rejected 撞车。

payload_digest 采取 EVALUATION-STANDARD.md §2.3 已经写明的算法：
    SHA-256( json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) )[:16]
v1.2 的实现与 §2.3 不一致（用了默认分隔符 ", " / ": " 且未排序键），
后果是任何第三方照 §2.3 自己算一遍都得不到我们公布的摘要；v1.3 予以更正。
摘要覆盖 domains + authorization + outcome 三个实质对象；`verdict` 与
`overall_failure_class` 是 domains 的纯函数，可由摘要覆盖的内容重算；
`timestamp` 不进摘要，以保证任何一天复现都得到同一摘要。

Usage / 用法
-------------
    python evidence-grader.py --demo            # run built-in example（运行内置示例）
    python evidence-grader.py --json out.json   # read evidence JSON, write conclusion JSON
    python evidence-grader.py --demo --json     # demo, machine-readable JSON on stdout（兼容）
    python evidence-grader.py --selftest        # run assertion tests（运行自检）

Exit codes / 退出码: 0 success（成功）, 1 input/validation error（输入校验错误）

Author / 作者: LGD-Eval（Independent Evaluation）
License / 许可: Apache-2.0
Version / 版本: v1.3 — case outcome separated from domain-coverage verdict; policy actions
                 split out of the verification vocabulary（用例结论与覆盖度判词分离；策略动作
                 从验证词表中拆出；对应 use-cases#27 @wolfbrother 2026-10-23 反馈）
"""
from __future__ import annotations
import argparse, json, sys, hashlib, datetime
from collections import OrderedDict

SCHEMA = "lgd-eval/conclusion/v1.3"

# Domain definitions / 六域定义（与 C2 贡献稿一致）
DOMAINS = OrderedDict([
    ("D1", "Identity & registration / 身份与注册"),
    ("D2", "Trust lifecycle / 信任生命周期"),
    ("D3", "Security & resilience / 安全与韧性"),
    ("D4", "Privacy & data governance / 隐私与数据"),
    ("D5", "Human oversight & accountability / 人类监督与问责"),
    ("D6", "Interoperability / 互操作性"),
])

GRADE_ORDER = ["V", "S", "M", "L", "P"]

# Failure classes / 失败语义类（从最严重到无）
FAIL_CLASSES = ["quarantined", "rejected", "unresolved", "none"]
FAIL_ORDER = {c: i for i, c in enumerate(FAIL_CLASSES)}

# Verification vocabulary / 验证词表（单一词表，结论与授权共用同一套三个词）
AUTH_RESULTS = ["verified", "unresolved", "rejected"]
OUTCOMES = ["verified", "unresolved", "rejected"]
AUTH_TO_OUTCOME = {"verified": "verified", "unresolved": "unresolved", "rejected": "rejected"}

# Machine-readable reason codes / 机器可读原因码
REASON_CODES = ["none", "authorization_unresolved", "authorization_rejected", "status_unavailable"]
REASON_FOR_RESULT = {
    "verified": ["none"],
    "unresolved": ["authorization_unresolved", "status_unavailable"],
    "rejected": ["authorization_rejected"],
}

# Policy actions / 处置动作（策略相关，与验证结论分开记录）
# 取自 EVALUATION-STANDARD.md §2.2 的 operator meaning，不另造词表
POLICY_ACTIONS = ["allow", "defer", "deny", "exclude"]

# 本应可验证的证据类型（若缺少可复现/时间戳则链路未确认）
VERIFIABLE_KINDS = {"audit", "repro-test", "design+test", "process", "interop"}

# Interpretation mapping / 解读等级映射（域级）
INTERPRET = {
    "V": {"level": "Verified / 确证",
          "meaning": "Claim independently reproduced（已独立复现）",
          "evidence": "Full reproduction kit + hash/timestamp（完整复现包+哈希/时间戳）"},
    "S": {"level": "Strong / 强证据",
          "meaning": "Converging method-level evidence（多方法收敛）",
          "evidence": ">=2 independent methods agree（至少两个独立方法一致）"},
    "M": {"level": "Moderate / 中等",
          "meaning": "Plausible with partial evidence（有部分证据支持）",
          "evidence": "Partial reproduction or single method（部分复现或单一方法）"},
    "L": {"level": "Limited / 有限",
          "meaning": "Anecdotal or single source（零散/单一来源）",
          "evidence": "Observation only（仅观察）"},
    "P": {"level": "Pending / 待定",
          "meaning": "Claim not yet testable（尚不可判定）",
          "evidence": "Explicit scope statement（明确范围声明）"},
}

# Field scopes / 字段口径（防止把覆盖度判词当用例结论读）
SCOPES = OrderedDict([
    ("outcome", "Case-level verification outcome for the dimension under test — "
                "read this field for the case conclusion. / 用例结论，读这个字段。"),
    ("verdict", "Six-domain evidence coverage: how many of the six domains reach V/S. "
                "A case that exercises one or two domains is 'Insufficient evidence' here "
                "by construction — this is NOT a case outcome. / 六域覆盖度，不是用例结论。"),
    ("overall_failure_class", "Worst evidence failure class across the six domains; an "
                              "unexercised (empty) domain is 'unresolved' by v1.x design. "
                              "/ 空域按 v1.x 设计记为 unresolved。"),
    ("policy_action", "Policy-dependent action, recorded separately from the verification "
                      "outcome (allow / defer / deny / exclude), reusing the operator meanings in EVALUATION-STANDARD.md §2.2. / 策略动作，与结论分开，词表与规范一致。"),
])

BIAS_CONTROLS = [
    "multi-judge（多裁判）", "human anchoring（人类锚定）", "AB/BA ordering（顺序轮换）",
    "inter-rater agreement kappa（裁判一致性）", "no self-review（不自查原则）",
]


def validate(evidence: dict) -> list:
    """Validate input structure; return list of error strings（校验输入结构，返回错误列表）."""
    errors = []
    if not isinstance(evidence, dict) or "subject" not in evidence:
        errors.append("missing 'subject' (评估对象缺失)")
    subjects = evidence.get("domains", {})
    if not isinstance(subjects, dict):
        errors.append("'domains' must be an object (domains 必须是对象)")
    for key in subjects:
        if key not in DOMAINS:
            errors.append("unknown domain %r (未知评估域)" % key)
        items = subjects[key]
        if not isinstance(items, list):
            errors.append("domain %s: evidence must be a list" % key)
            continue
        for it in items:
            if not isinstance(it, dict):
                errors.append("domain %s: evidence item must be an object" % key)
                continue
            grade = it.get("grade")
            if grade not in GRADE_ORDER:
                errors.append("domain %s: invalid grade %r (允许 V/S/M/L/P)" % (key, grade))
            if not it.get("claim"):
                errors.append("domain %s: evidence item missing 'claim' (缺少声明)" % key)
    auth = evidence.get("authorization")
    if auth is not None:
        if not isinstance(auth, dict):
            errors.append("'authorization' must be an object (authorization 必须是对象)")
        else:
            res = auth.get("result")
            if res not in AUTH_RESULTS:
                errors.append(
                    "authorization.result must be one of verified/unresolved/rejected "
                    "(v1.3: 'quarantined' is a policy action, not a verification outcome — "
                    "record it in authorization.policy_action as 'hold')"
                    " (授权结果必须是三态之一)")
            if not auth.get("reason"):
                errors.append("authorization.reason is required (授权原因必填)")
            code = auth.get("reason_code")
            if code is None:
                errors.append("authorization.reason_code is required"
                              " (v1.3 起必填：机器可读原因码)")
            elif code not in REASON_CODES:
                errors.append("authorization.reason_code must be one of %s"
                              % "/".join(REASON_CODES))
            elif res in REASON_FOR_RESULT and code not in REASON_FOR_RESULT[res]:
                errors.append("authorization.reason_code %r inconsistent with result %r "
                              "(allowed: %s)"
                              % (code, res, "/".join(REASON_FOR_RESULT[res])))
            action = auth.get("policy_action")
            if action is None:
                errors.append("authorization.policy_action is required"
                              " (v1.3 起必填：allow/defer/deny/exclude，见 EVALUATION-STANDARD.md §2.2)")
            elif action not in POLICY_ACTIONS:
                errors.append("authorization.policy_action must be one of %s"
                              % "/".join(POLICY_ACTIONS))
    return errors


def digest_of(text: str) -> str:
    """Stable sha256 digest for reproducibility (可复现性哈希)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def digest_of_canonical(obj) -> str:
    """Canonical payload digest, exactly as written in EVALUATION-STANDARD.md §2.3
    （规范 §2.3 原文约定的算法：排序键 + 紧凑分隔符 + ensure_ascii=False，取前 16 位）.
    """
    return digest_of(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def grade_domain(items: list) -> tuple:
    """Domain-level best grade + evidence list（域级最高证据级别 + 证据清单）."""
    if not items:
        return "P", []
    grades = [it["grade"] for it in items]
    best = grades[0]
    for g in grades:
        if GRADE_ORDER.index(g) < GRADE_ORDER.index(best):
            best = g
    return best, items


def evidence_failure_class(it: dict) -> str:
    """Failure class of a single evidence item（单条证据的失败类）."""
    if not isinstance(it, dict) or not it.get("claim") or it.get("grade") not in GRADE_ORDER:
        return "quarantined"
    if it.get("grade") == "P":
        return "rejected"
    if it.get("kind") in VERIFIABLE_KINDS and not (it.get("reproducible") or it.get("timestamped")):
        return "unresolved"
    return "none"


def domain_failure_class(items: list) -> str:
    """Worst failure class across a domain's evidence（域内最严重失败类）."""
    if not items:
        return "unresolved"
    worst = "none"
    for it in items:
        fc = evidence_failure_class(it)
        if FAIL_ORDER[fc] < FAIL_ORDER[worst]:
            worst = fc
    return worst


def normalise_authorization(auth) -> "OrderedDict | None":
    """Fixed key order so that key order in the input cannot change the digest
    （固定键序，输入文件键序变化不影响摘要）."""
    if not auth:
        return None
    return OrderedDict([
        ("result", auth.get("result")),
        ("reason_code", auth.get("reason_code")),
        ("reason", auth.get("reason")),
        ("relying_party_action", auth.get("relying_party_action", "")),
        ("policy_action", auth.get("policy_action")),
    ])


def build_outcome(auth) -> "OrderedDict | None":
    """Project the case-level outcome from the authorization dimension.
    结论由授权维度投影而来，因此两者在结构上不可能互相矛盾。
    """
    if not auth:
        return None
    return OrderedDict([
        ("verification", AUTH_TO_OUTCOME.get(auth.get("result"), "unresolved")),
        ("reason_code", auth.get("reason_code")),
        ("policy_dependent", True),
        ("policy_action", auth.get("policy_action")),
        ("relying_party_action", auth.get("relying_party_action", "")),
    ])


def conclude(evidence: dict, subject: str, evaluator: str = "LGD-Eval") -> dict:
    """Produce machine-readable conclusion（生成机器可读结论）."""
    domain_results = OrderedDict()
    for key, title in DOMAINS.items():
        items = evidence.get("domains", {}).get(key, [])
        best, used = grade_domain(items)
        fc = domain_failure_class(items)
        domain_results[key] = {
            "domain": title,
            "best_grade": best,
            "interpretation": INTERPRET[best]["level"],
            "meaning": INTERPRET[best]["meaning"],
            "failure_class": fc,
            "evidence_count": len(used),
            "used_evidence": [{"claim": it["claim"], "grade": it["grade"],
                               "kind": it.get("kind", ""), "source": it.get("source", ""),
                               "reproducible": bool(it.get("reproducible", False)),
                               "timestamped": bool(it.get("timestamped", False)),
                               "failure_class": evidence_failure_class(it)} for it in used],
        }
    # Overall verdict discipline / 总体判词纪律：无复合分；仅给出证据面覆盖统计
    graded = sum(1 for r in domain_results.values() if r["best_grade"] in ("V", "S"))
    total = len(DOMAINS)
    verdict = "Evidence-backed（证据支持）" if graded == total else "Partially evidenced（部分有据）" if graded >= total // 2 else "Insufficient evidence（证据不足）"
    # Overall failure class / 总体失败类：取最严重
    overall_fc = "none"
    for r in domain_results.values():
        if FAIL_ORDER[r["failure_class"]] < FAIL_ORDER[overall_fc]:
            overall_fc = r["failure_class"]
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    auth = normalise_authorization(evidence.get("authorization"))
    outcome = build_outcome(evidence.get("authorization"))
    payload = OrderedDict([
        ("schema", SCHEMA),
        ("subject", subject),
        ("evaluator", evaluator),
        ("timestamp", now),
        ("outcome", outcome),
        ("verdict", verdict),
        ("scopes", SCOPES),
        ("overall_failure_class", overall_fc),
        ("authorization", auth),
        ("no_composite_score", True),
        ("bias_controls", BIAS_CONTROLS),
        ("domains", domain_results),
        ("reproducibility", {
            "open_rubric": True, "evidence_appendix": True, "response_window_days": 14,
            "correction_window_hours": 24, "machine_readable": True,
            "digest_covers": ["domains", "authorization", "outcome"],
            "digest_convention": "sha256(json.dumps(obj, sort_keys=True, "
                                 "separators=(\",\", \":\"), ensure_ascii=False))[:16] "
                                 "— EVALUATION-STANDARD.md §2.3",
            "payload_digest": digest_of_canonical(
                OrderedDict([("domains", domain_results), ("authorization", auth),
                             ("outcome", outcome)])),
        }),
    ])
    return payload


def to_markdown(c: dict) -> str:
    """Render conclusion as bilingual Markdown（渲染为双语 Markdown）."""
    o = c.get("outcome") or {}
    lines = [
        "# LGD-Eval Assessment Conclusion / 评估结论",
        "",
        "- **Subject / 评估对象**: %s" % c["subject"],
        "- **Evaluator / 评估方**: %s" % c["evaluator"],
        "- **Timestamp / 时间戳**: %s" % c["timestamp"],
        "- **Outcome / 用例结论**: **%s** (reason `%s`; policy action `%s`)"
        % (o.get("verification", "—"), o.get("reason_code", "—"), o.get("policy_action", "—")),
        "- **Relying-party action / 依赖方动作**: %s" % o.get("relying_party_action", "—"),
        "- **Evidence-coverage verdict / 覆盖度判词**: %s" % c["verdict"],
        "- **Overall failure class / 总体失败类**: %s" % c["overall_failure_class"],
        "- **No composite score / 无复合分**: True（域级独立评分，禁止复合）",
        "- **Bias controls / 偏倚控制**: %s" % ("; ".join(c["bias_controls"])),
        "",
        "> `verdict` 是六域覆盖度判词，不是用例结论；用例结论读 `outcome.verification`。",
        "> `verdict` is six-domain evidence coverage, not a case outcome; read `outcome.verification`.",
        "",
        "## Domain-level results / 域级结果",
        "",
        "| Domain / 域 | Best grade / 最高级别 | Failure class / 失败类 | Interpretation / 解读 | Evidence / 证据数 |",
        "|---|---|---|---|---|",
    ]
    for key, r in c["domains"].items():
        lines.append("| %s · %s | %s | %s | %s | %d |" % (key, r["domain"], r["best_grade"], r["failure_class"], r["interpretation"], r["evidence_count"]))
    lines += ["", "## Failure semantics / 失败语义",
              "- quarantined（隔离）: malformed input — missing claim or invalid grade",
              "- rejected（拒绝）: grade=P, not yet testable",
              "- unresolved（未决）: verifiable kind without reproducible/timestamped evidence, or empty domain",
              "- none（无失败）: evidence accepted",
              "", "## Reproducibility / 可复现",
              "- open rubric（公开细则）: True",
              "- evidence appendix（证据附录）: True",
              "- response window（回应期）: 14 days / 24h corrections",
              "- machine-readable（机器可读）: True",
              "- digest covers（摘要覆盖）: domains + authorization + outcome",
              "- payload digest（载荷摘要）: `%s`" % c["reproducibility"]["payload_digest"],
              "",
              "*Generated by LGD-Eval evidence-grader（由证据分级器生成）；结论受证据级别约束，欢迎独立复现。*",
              ]
    return "\n".join(lines)


# Built-in demo evidence / 内置示例证据（示例数据，明确标注）
DEMO = {
    "subject": "MedXpert-LLM-Library v1.6 (medical-device compliance assistant) / 示例：医械合规助手",
    "domains": {
        "D1": [
            {"claim": "Identity registration with immutable registry entry / 身份注册留有不可变登记", "grade": "V",
             "kind": "audit", "source": "zenodo v1.6.0 + .ots", "reproducible": True, "timestamped": True},
            {"claim": "Delegation artefacts signed / 委托工件已签名", "grade": "M",
             "kind": "claim", "source": "vendor statement", "reproducible": False, "timestamped": False},
        ],
        "D2": [
            {"claim": "Lifecycle gates: establish-evaluate-degrade-revoke with evidence thresholds / 生命周期门禁各阶段带证据阈值", "grade": "S",
             "kind": "design+test", "source": "lgd-theory + 28 consistency tests", "reproducible": True, "timestamped": False},
        ],
        "D3": [
            {"claim": "Adversarial suite 9/9 passed (prompt-injection, mojibake, unicode confusion) / 对抗测试 9/9 通过", "grade": "V",
             "kind": "repro-test", "source": "skill-audit scanner", "reproducible": True, "timestamped": True},
        ],
        "D4": [
            {"claim": "Zero-exfiltration data handling declared / 声明零外泄数据处理", "grade": "L",
             "kind": "policy", "source": "privacy notice", "reproducible": False, "timestamped": False},
        ],
        "D5": [
            {"claim": "Human sign-off required at issuance / 签发须人类签批", "grade": "S",
             "kind": "process", "source": "workflow spec + 2 audits", "reproducible": True, "timestamped": False},
        ],
        "D6": [
            {"claim": "Machine-readable trust metadata schema.jsonld / 机器可读信任元数据", "grade": "S",
             "kind": "interop", "source": "JSON-LD schema + validator", "reproducible": True, "timestamped": False},
        ],
    },
    "authorization": {
        "result": "verified",
        "reason_code": "none",
        "reason": "issuer listed in authoritative scope registry for this credential profile and claim type",
        "relying_party_action": "proceed per normal policy",
        "policy_action": "allow",
    },
}


def run_selftest() -> int:
    """Assertion tests（断言自检）: rule invariants + failure semantics.
    断言数由计数器统计，打印的数字是真实执行的断言条数，不是手写的。
    """
    errs = []
    n = [0]

    def check(cond, msg):
        n[0] += 1
        if not cond:
            errs.append(msg)

    # --- 输入校验 ---
    bad = {"subject": "x", "domains": {"D1": [{"claim": "c", "grade": "X"}]}}
    check(bool(validate(bad)), "1: bad grade not rejected")

    # --- 域级取最高 ---
    items = [{"claim": "a", "grade": "M"}, {"claim": "b", "grade": "V"}, {"claim": "c", "grade": "S"}]
    best, _ = grade_domain(items)
    check(best == "V", "2: best-grade logic failed (%s)" % best)

    # --- 空域 ---
    best2, _ = grade_domain([])
    check(best2 == "P", "3: empty domain should be P")
    check(domain_failure_class([]) == "unresolved", "4: empty domain failure class should be unresolved")

    # --- 结论结构 ---
    c = conclude(DEMO, DEMO["subject"])
    check(c["no_composite_score"] is True, "5: composite discipline broken")
    check(len(c["domains"]) == 6, "6: domain count != 6")
    check(c["schema"] == SCHEMA, "7: schema version not %s" % SCHEMA)

    # --- 摘要确定性 ---
    check(digest_of("abc") == digest_of("abc"), "8: digest not deterministic")

    # --- 失败语义四态 ---
    check(evidence_failure_class({"claim": "", "grade": "V"}) == "quarantined",
          "9: missing claim should be quarantined")
    check(evidence_failure_class({"claim": "c", "grade": "P"}) == "rejected",
          "10: grade P should be rejected")
    check(evidence_failure_class({"claim": "c", "grade": "S", "kind": "audit",
                                  "reproducible": False, "timestamped": False}) == "unresolved",
          "11: verifiable kind without repro/ts should be unresolved")
    check(evidence_failure_class({"claim": "c", "grade": "L", "kind": "policy",
                                  "reproducible": False, "timestamped": False}) == "none",
          "12: declarative kind should be none")
    check(c["overall_failure_class"] == "none", "13: overall failure class should be none for demo")
    check(c["domains"]["D4"]["failure_class"] == "none",
          "14: D4 policy evidence failure class should be none")

    # --- 授权维度透传 ---
    check(bool(c.get("authorization")) and c["authorization"]["result"] == "verified",
          "15: authorization validity not carried into conclusion")
    bad_auth = {"subject": "x", "domains": {"D1": [{"claim": "c", "grade": "V"}]},
                "authorization": {"result": "bogus", "reason": "r",
                                  "reason_code": "none", "policy_action": "allow"}}
    check(bool(validate(bad_auth)), "16: invalid authorization result not rejected")

    # --- v1.3：quarantined 不再是验证结论 ---
    q_auth = {"subject": "x", "domains": {"D1": [{"claim": "c", "grade": "V"}]},
              "authorization": {"result": "quarantined", "reason": "spec undecided",
                                "reason_code": "none", "policy_action": "exclude"}}
    check(bool(validate(q_auth)),
          "17: v1.3 must reject 'quarantined' as a verification outcome (it is a policy action)")
    check("quarantined" not in AUTH_RESULTS, "17b: AUTH_RESULTS must not contain 'quarantined'")

    # --- v1.3：reason_code 必填且必须与 result 自洽 ---
    no_code = {"subject": "x", "domains": {"D1": [{"claim": "c", "grade": "V"}]},
               "authorization": {"result": "verified", "reason": "r", "policy_action": "allow"}}
    check(bool(validate(no_code)), "18: missing reason_code not rejected")
    mismatch = {"subject": "x", "domains": {"D1": [{"claim": "c", "grade": "V"}]},
                "authorization": {"result": "rejected", "reason": "r",
                                  "reason_code": "none", "policy_action": "deny"}}
    check(bool(validate(mismatch)), "19: reason_code inconsistent with result not rejected")
    bad_action = {"subject": "x", "domains": {"D1": [{"claim": "c", "grade": "V"}]},
                  "authorization": {"result": "verified", "reason": "r",
                                    "reason_code": "none", "policy_action": "reject"}}
    check(bool(validate(bad_action)),
          "20: policy_action 'reject' not rejected (word reserved for the outcome vocabulary)")

    # --- B1 vs B2 ---
    b1 = {"subject": "B1", "domains": {"D1": [{"claim": "sig", "grade": "V", "kind": "repro-test",
                                               "reproducible": True, "timestamped": True}]},
          "authorization": {"result": "unresolved", "reason": "scope info unavailable",
                            "reason_code": "authorization_unresolved", "policy_action": "defer"}}
    b2 = {"subject": "B2", "domains": {"D1": [{"claim": "sig", "grade": "V", "kind": "repro-test",
                                               "reproducible": True, "timestamped": True}]},
          "authorization": {"result": "rejected", "reason": "scope registry confirms lack of scope",
                            "reason_code": "authorization_rejected", "policy_action": "deny"}}
    c1, c2 = conclude(b1, "B1"), conclude(b2, "B2")
    check(c1["authorization"]["result"] == "unresolved" and c2["authorization"]["result"] == "rejected",
          "21: B1/B2 authorization separation broken")
    check(c1["reproducibility"]["payload_digest"] != c2["reproducibility"]["payload_digest"],
          "22: B1/B2 digests must differ (authorization enters digest)")
    check(c1["outcome"]["verification"] == "unresolved" and c2["outcome"]["verification"] == "rejected",
          "23: B1/B2 case outcomes must differ")

    # --- 摘要确定性（含授权维度）---
    check(conclude(b1, "B1")["reproducibility"]["payload_digest"] == c1["reproducibility"]["payload_digest"],
          "24: digest not deterministic with authorization")

    # --- v1.3：结论字段存在且与覆盖度判词分离 ---
    check(c["outcome"]["verification"] == "verified", "25: demo outcome should be 'verified'")
    n_vs = sum(1 for r in c["domains"].values() if r["best_grade"] in ("V", "S"))
    check(n_vs == 5 and c["verdict"] == "Partially evidenced（部分有据）",
          "26: demo coverage should be 5/6 -> 'Partially evidenced' (got %d/6, %s)"
          % (n_vs, c["verdict"]))
    b1_v = conclude(b1, "B1")
    check(b1_v["verdict"] == "Insufficient evidence（证据不足）" and b1_v["outcome"]["verification"] == "unresolved",
          "27: coverage verdict and case outcome must be separable (B1: insufficient coverage, unresolved outcome)")

    # --- v1.3：摘要覆盖 outcome；单改 policy_action 会改变摘要 ---
    check(c["reproducibility"]["digest_covers"] == ["domains", "authorization", "outcome"],
          "28: digest_covers must list domains/authorization/outcome")
    b1b = json.loads(json.dumps(b1))
    b1b["authorization"]["policy_action"] = "deny"
    check(conclude(b1b, "B1")["reproducibility"]["payload_digest"] != c1["reproducibility"]["payload_digest"],
          "29: changing policy_action alone must change the digest")

    # --- v1.3：键序归一化（输入键序不影响摘要）---
    shuffled = OrderedDict()
    shuffled["subject"] = b1["subject"]
    shuffled["authorization"] = OrderedDict(reversed(list(b1["authorization"].items())))
    shuffled["domains"] = b1["domains"]
    check(conclude(shuffled, "B1")["reproducibility"]["payload_digest"] == c1["reproducibility"]["payload_digest"],
          "30: key order in input must not change the digest")

    # --- v1.3：scopes 口径齐全 ---
    check(all(k in c["scopes"] for k in ("outcome", "verdict", "overall_failure_class", "policy_action")),
          "31: scopes must document outcome/verdict/overall_failure_class/policy_action")

    # --- v1.3：摘要算法必须与 EVALUATION-STANDARD.md §2.3 逐字一致 ---
    independent = hashlib.sha256(json.dumps(
        OrderedDict([("domains", c["domains"]),
                     ("authorization", c["authorization"]),
                     ("outcome", c["outcome"])]),
        sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
    check(c["reproducibility"]["payload_digest"] == independent,
          "32: digest must equal the §2.3 convention computed independently")
    check("§2.3" in c["reproducibility"].get("digest_convention", ""),
          "33: reproducibility must state which digest convention is used")

    # --- v1.3：处置词表 = 规范 §2.2 的四个词，一个不多一个不少 ---
    check(POLICY_ACTIONS == ["allow", "defer", "deny", "exclude"],
          "34: policy actions must be exactly the four operator meanings in §2.2")

    if errs:
        for e in errs:
            print("FAIL: %s" % e)
        return 1
    print("SELFTEST OK — %d invariants passed（%d 项不变量全部通过）" % (n[0], n[0]))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="LGD-Eval evidence grader（证据分级器）")
    ap.add_argument("--demo", action="store_true", help="run built-in example（运行内置示例）")
    ap.add_argument("--json", nargs="?", const="", metavar="FILE",
                    help="read evidence JSON from FILE; bare --json is accepted with --demo "
                         "（读取证据 JSON；无值 --json 与 --demo 连用时不报错）")
    ap.add_argument("--out", metavar="FILE", default=None, help="write conclusion JSON（输出结论 JSON）")
    ap.add_argument("--md", metavar="FILE", default=None, help="write bilingual Markdown report（输出双语报告）")
    ap.add_argument("--selftest", action="store_true", help="run assertion tests（运行自检）")
    args = ap.parse_args()

    if args.selftest:
        return run_selftest()

    if args.demo:
        evidence = DEMO
    elif args.json:
        try:
            evidence = json.load(open(args.json, encoding="utf-8"))
        except Exception as e:
            print("ERROR reading %s: %s" % (args.json, e))
            return 1
    else:
        ap.print_help()
        return 1

    errs = validate(evidence)
    if errs:
        for e in errs:
            print("ERROR: %s" % e)
        return 1

    c = conclude(evidence, evidence["subject"])
    out_json = json.dumps(c, ensure_ascii=False, indent=2)
    print(out_json)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(out_json)
    if args.md:
        open(args.md, "w", encoding="utf-8").write(to_markdown(c))
    return 0


if __name__ == "__main__":
    sys.exit(main())
