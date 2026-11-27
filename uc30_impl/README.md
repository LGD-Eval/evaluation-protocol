# uc30_impl — 记录工具链的最小实现（仓库内可复跑副本）

本目录是 UC30 交付包 `UC30_巴黎首会_交付包_v16_20261126.zip`（sha256 `9ad5dcc0…4dea`，冻结根 30 叶 `9959f2ab…481b`）中 `uc30_impl/` 的**同源副本**，只去掉了 `.bak` 备份与 `out/` 生成物，其余未改一字节。

放这里的唯一理由：让外人**从仓库 clone 就能跑**，不必先去找附件下载链接。
交付包本身仍是冻结件的真源；本目录不构成新的"版本"。

## 三条命令（复制粘贴即可，2026-11-27 实测）

```bash
python ucr.py selftest                                    # SELFTEST OK — 12/12 vectors as expected
python crosscheck.py                                      # CROSSCHECK OK — 12/12 vectors agree across two implementations
node verify_node.js vectors/case-01-valid.json             # 输出比对 JSON，exit 0
```

实测环境：Linux Debian，Python 3.12.11，Node v22.23.4；零第三方依赖，纯标准库。

## 生成其余路径（可选）

```bash
python gen_out.py        # 由 vectors 生成 out/ 下记录与报告
python mutate.py         # 需先跑 gen_out.py（依赖 out/ 下的记录）
```

## 已知过时文本（不改，保留原文）

`README_package_v16_original.md` 是包内原文，标题自称 "v0.2"、"八个一致性向量，8/8" —— **已过时**：现为 ucr-v0.3、12 条向量，实测 12/12。原文保留是为了对齐冻结根，不做美化。

## 边界

不含撤销检查；判决正确性未证；未对真实流程做仪表化；无第三方人类复跑；
不主张符合 EU MDR / 21 CFR 820 / EU AI Act。
