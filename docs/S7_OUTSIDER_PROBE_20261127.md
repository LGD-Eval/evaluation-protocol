# 外人角度全量实测记录（S7，2026-11-27）

这份文件记录**一次真实的机器级外人视角实测**，目的不是自夸，是把"别人能不能照着跑起来"变成可核对的事实。判据取自《发布前审查标准 v5》S7 一节。

## 方法（陌生人零上下文）

- 环境：独立云主机（Linux/Debian，Python 3.12.11，Node v22.23.4），**非作者本机**。
- 取物：`codeload` zip 匿名下载 + `git ls-remote` 取链头；环境内清除 `GH_TOKEN`/`GITHUB_TOKEN`/`GIT_ASKPASS`/`SSH_AUTH_SOCK`，`GIT_TERMINAL_PROMPT=0`。
- 全量：枚举仓内全部文件并逐件记 `size` + `sha256`，不抽样。
- 命令：只执行 README 里写着的、可复制的命令块（`cd` 视为块内状态，整块顺序执行）。
- 落盘：原始日志 + `sha256`。

## 结果（链头 `6de5c69`）

| 项 | 值 |
|---|---|
| 文件总数 | 125（资产 117 件，共 785,573 B） |
| README 命令块 | 2 块，**2/2 跑通** |
| 块一 | `cd evaluation-protocol && python demo/run_worked_examples.py` → exit 0（0.39 s，4/4 PASS） |
| 块二 | `cd uc30_impl && python ucr.py selftest && python crosscheck.py && node verify_node.js vectors/case-01-valid.json` → exit 0（0.64 s，SELFTEST OK 12/12、CROSSCHECK OK 12/12、node 输出比对 JSON） |
| CI 复核 | `repro-check` success：三条命令 + `case-05-tampered` 必拒 + 现场改 `payload_digest` 必被抓 |

## 这次修掉的缺陷（诚实记录）

1. 修前 README 让人"解包后 `cd uc30_impl`"，但 `ucr.py` / `crosscheck.py` / `verify_node.js` 都在交付包 zip 里，包不在仓库、也没给获取方式 → 陌生人从仓库起手 4 条命令只通 1 条。现改为把 `uc30_impl/` 同源副本纳入仓库（去 `.bak` 与 `out/`），clone 即可跑。
2. README 原写"10/10 vectors"，实际是 12 条 → 现在是实测 12/12。
3. CI 新增 `repro-check`，把"能跑"从一次性结论变成每次推送都验的门禁。

## 口径（不可混用）

- 本次是 `MACHINE-INDEPENDENT`：**另一台机器、无凭据**，但操作者仍是同一 owner。
- **不是** `human_outsider`。要算外部人类复跑，必须由无关系第三方按本文件步骤亲跑，并出具含"读取端点 + 时间戳"的回执。
- 本记录不证明任何主张为真，只证明：上面这些命令，在一个没有我方凭据的干净环境里，能从公开地址起步跑通。

## 自己复跑

```bash
curl -L -o repo.zip https://codeload.github.com/LGD-Eval/evaluation-protocol/zip/refs/heads/main
unzip repo.zip && cd evaluation-protocol-main/uc30_impl
python ucr.py selftest
python crosscheck.py
node verify_node.js vectors/case-01-valid.json
```
