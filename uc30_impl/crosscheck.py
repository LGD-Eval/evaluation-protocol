#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cross-implementation check: Python verifier vs Node verifier, same records.

This is the evidence for the claim "a party with a different runtime reaches
the same verdict". It runs both verifiers over every vector and asserts that
the outcome, the digest and every per-check result agree.

    python crosscheck.py
"""
import glob
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ucr  # noqa: E402


def run_node(case_path: Path):
    out = subprocess.run(
        ["node", "verify_node.js", str(case_path)],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    return json.loads(out.stdout)


def main():
    rows, bad = [], 0
    for case_path in sorted(glob.glob("vectors/case-*.json")):
        bundle = json.loads(Path(case_path).read_text(encoding="utf-8"))
        py = ucr.verify(bundle["record"], bundle.get("current_state"))
        node = run_node(Path(case_path))

        py_map = {c["check_id"]: c["result"] for c in py["checks"]}
        nd_map = {c["check_id"]: c["result"] for c in node["checks"]}
        agree = (py_map == nd_map
                 and py["outcome"]["verification"] == node["outcome"]["verification"]
                 and py["outcome"]["policy_action"] == node["outcome"]["policy_action"]
                 and py["recomputed_digest"] == node["recomputed_digest"])
        bad += 0 if agree else 1
        rows.append((Path(case_path).stem, py["outcome"]["verification"],
                     node["outcome"]["verification"], py["recomputed_digest"],
                     node["recomputed_digest"], "AGREE" if agree else "DISAGREE"))
        if not agree:
            print("differing checks:", {k: (py_map.get(k), nd_map.get(k))
                                       for k in set(py_map) | set(nd_map)
                                       if py_map.get(k) != nd_map.get(k)})

    print(f"{'vector':28} {'python':11} {'node':11} {'digest(py)':17} {'digest(node)':17} verdict")
    for r in rows:
        print(f"{r[0]:28} {r[1]:11} {r[2]:11} {r[3]:17} {r[4]:17} {r[5]}")
    print(f"\nCROSSCHECK {'OK' if bad == 0 else 'FAILED'} — {len(rows) - bad}/{len(rows)} "
          f"vectors agree across two implementations")
    return 0 if bad == 0 else 5


if __name__ == "__main__":
    sys.exit(main())
