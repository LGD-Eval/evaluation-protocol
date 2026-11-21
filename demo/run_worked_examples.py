#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-command worked-examples regression demo.

Reproduces the four published case conclusions (A / B1 / B2 / C) from the
original full inputs (worked-examples/cases/*_input.json, which include the
authorization dimension) and checks the produced outcome fields and payload
digest against worked-examples/cases/EXPECTED_OUTCOMES.evaluator-side.json.

Note: worked-examples/cases/inputs-package/ is the inputs-only variant for
independent evaluators (the authorization block is intentionally stripped
there); this demo runs against the original inputs so the published
conclusions — including payload_digest — can be reproduced bit-for-bit.

Usage / 用法
------------
    python demo/run_worked_examples.py            # run all cases
    python demo/run_worked_examples.py --quiet    # only print the summary

Exit code 0 = all cases match; 1 = any mismatch or error.

Zero third-party dependencies. Python 3.8+.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRADER = ROOT / "tools" / "evidence-grader.py"
CASES = ROOT / "worked-examples" / "cases"
EXPECTED = CASES / "EXPECTED_OUTCOMES.evaluator-side.json"

CASE_FILES = {
    "caseA": "caseA_valid_registered_credential_input.json",
    "caseB1": "caseB1_unverifiable_issuer_scope_input.json",
    "caseB2": "caseB2_confirmed_out_of_scope_issuer_input.json",
    "caseC": "caseC_unavailable_status_source_input.json",
}


def run_case(case_name: str, input_file: Path) -> tuple:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    proc = subprocess.run(
        [sys.executable, str(GRADER), "--json", str(input_file)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
        timeout=90)
    if proc.returncode != 0:
        return False, f"grader exited {proc.returncode}: {proc.stderr.strip()[:200]}"
    # robust JSON extraction: take the outermost {...} of stdout
    text = proc.stdout
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return False, "no JSON object found in grader output"
    try:
        conclusion = json.loads(text[start:end + 1])
    except json.JSONDecodeError as e:
        return False, f"conclusion is not valid JSON: {e}"

    outcome = conclusion.get("outcome") or {}
    if not outcome:
        return False, "conclusion has no outcome object (input missing authorization?)"
    got = {
        "outcome_verification": outcome.get("verification"),
        "reason_code": outcome.get("reason_code"),
        "policy_action": outcome.get("policy_action"),
        "payload_digest": (conclusion.get("reproducibility") or {}).get("payload_digest"),
    }
    return True, got


def main() -> int:
    ap = argparse.ArgumentParser(description="Run worked examples against expected outcomes")
    ap.add_argument("--quiet", action="store_true", help="only print the summary table")
    args = ap.parse_args()

    if not GRADER.exists() or not CASES.exists() or not EXPECTED.exists():
        print("ABORT: repo layout not found (run from inside the repository)")
        return 1

    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))["cases"]
    rows, failures = [], 0

    for case_name in sorted(expected):
        input_file = CASES / CASE_FILES[case_name]
        if not input_file.exists():
            rows.append((case_name, "FAIL", "input file missing"))
            failures += 1
            continue
        ok, got = run_case(case_name, input_file)
        if not ok:
            rows.append((case_name, "FAIL", got))
            failures += 1
            continue
        exp = expected[case_name]
        mismatch = [k for k in got if got[k] != exp.get(k)]
        if mismatch:
            detail = "; ".join(f"{k}: got {got[k]!r}, expected {exp.get(k)!r}" for k in mismatch)
            rows.append((case_name, "FAIL", detail))
            failures += 1
        else:
            rows.append((case_name, "PASS",
                         f"{got['outcome_verification']}/{got['policy_action']} + digest match"))

    print()
    print("LGD-Eval evaluation-protocol — worked examples regression")
    print("=" * 64)
    for case_name, status, detail in rows:
        print(f"  {case_name:8s} {status:5s} {detail}")
    print("=" * 64)
    total = len(rows)
    print(f"  {total - failures}/{total} PASS")
    if failures == 0:
        print("  All cases match the published expected outcomes.")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
