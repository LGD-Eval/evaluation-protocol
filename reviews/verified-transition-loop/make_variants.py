#!/usr/bin/env python
# make_variants.py — build adversarial variants of the VTL transparency-log fixture.
# Inputs: transparency-log-v0.14.json (prototype fixture). Outputs: _variant_A/B.json.
# Usage: python make_variants.py <fixture.json> [outdir]
import json
import copy
import sys
import os
import argparse


def main() -> int:
    ap = argparse.ArgumentParser(
        description="构建 VTL transparency-log fixture 的对抗变体（缺 inclusion / 篡改 entry）。")
    ap.add_argument("fixture", help="transparency-log-*.json 输入路径")
    ap.add_argument("outdir", nargs="?", default=".", help="输出目录（默认当前目录）")
    args = ap.parse_args()

    try:
        with open(args.fixture, encoding="utf-8") as fh:
            fix = json.load(fh)
    except (OSError, ValueError) as e:
        print("ERROR: 无法读取 fixture %s: %s" % (args.fixture, e), file=sys.stderr)
        return 2

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    A = copy.deepcopy(fix)
    A["base_bundle"].pop("inclusion_path", None)   # evidence missing

    B = copy.deepcopy(fix)
    d = bytearray(B["base_bundle"]["entry"]["snapshot_digest"], "ascii")
    d[0] = ord("0") if d[0] != ord("0") else ord("1")   # evidence tampered
    B["base_bundle"]["entry"]["snapshot_digest"] = d.decode()

    for name, obj in [("_variant_A_missing_inclusion.json", A), ("_variant_B_tampered_entry.json", B)]:
        with open(os.path.join(outdir, name), "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
        print("wrote", name)

    print("run: node reference/transparency-log-strict-v0.14.mjs <out>/<variant> [now_ms]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
