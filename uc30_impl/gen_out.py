#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate everything under out/ from the vectors, in one pass.

For each vector: write record.json, state.json, report.json; for the clean vector
also write the SCITT statement and the AuthZEN-derived evidence entry.

    python gen_out.py
"""
import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ucr  # noqa: E402

OUT = Path("out")


def main():
    OUT.mkdir(exist_ok=True)
    ok = True
    for case_path in sorted(glob.glob("vectors/case-*.json")):
        bundle = json.loads(Path(case_path).read_text(encoding="utf-8"))
        name = Path(case_path).stem
        rec, state = bundle["record"], bundle["current_state"]

        (OUT / f"{name}.record.json").write_text(
            json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        (OUT / f"{name}.state.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

        rep = ucr.verify(rec, state)
        (OUT / f"{name}.report.json").write_text(
            json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")

        matched = (rep["outcome"]["verification"] == bundle["expected"]["outcome"]
                   and rep["outcome"]["policy_action"] == bundle["expected"]["policy_action"])
        ok = ok and matched
        print(f"{name:28} {rep['outcome']['verification']:11} "
              f"{rep['outcome']['policy_action']:6} {rep['recomputed_digest']} "
              f"{'ok' if matched else 'EXPECTED MISMATCH'}")

    # interop artefacts on the clean vector
    clean = json.loads((OUT / "case-01-valid.record.json").read_text(encoding="utf-8"))
    state = json.loads((OUT / "case-01-valid.state.json").read_text(encoding="utf-8"))
    rep = ucr.verify(clean, state)
    (OUT / "case-01-valid.scitt-statement.json").write_text(
        json.dumps(ucr.scitt_statement(clean, rep), ensure_ascii=False, indent=2), encoding="utf-8")

    decision = json.loads((Path("demo") / "authzen-decision.json").read_text(encoding="utf-8"))
    entry = ucr.authzen_evidence(decision)
    (OUT / "case-01-valid.authzen-evidence.json").write_text(
        json.dumps({"evidence_entry": entry,
                    "how_to_use": ("append this object to the record's evidence[] array, then re-emit "
                                   "so the digest covers it; the record stays verifiable from outside")},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print("\ninterop written: scitt statement + authzen evidence")
    print("GEN_OUT", "OK" if ok else "MISMATCH")
    return 0 if ok else 6


if __name__ == "__main__":
    sys.exit(main())
