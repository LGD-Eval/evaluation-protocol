#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mutation test: does every covered field actually move the digest, and does
anything outside the digest stay harmless?

For each top-level field we apply one minimal change and report:
  - whether the digest changed (must be True for covered fields)
  - what the verifier says when the record still claims the original digest

    python mutate.py
"""
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ucr  # noqa: E402

BASE = json.loads(Path("out/case-01-valid.record.json").read_text(encoding="utf-8"))

MUTATIONS = {
    "schema": lambda r: r.__setitem__("schema", "ucr/record/v9.9"),
    "artefact": lambda r: r["artefact"].__setitem__("hash", "sha256:00000000"),
    "mandate": lambda r: r["mandate"].__setitem__("version", "4"),
    "delegation": lambda r: r["delegation"][0].__setitem__("sop", "QP-8.9"),
    "process_state": lambda r: r["process_state"].__setitem__("revision", "8.9"),
    "compared_state": lambda r: r["compared_state"].__setitem__("revision", "8.9"),
    "evidence": lambda r: r["evidence"][0].__setitem__("ref", "sha256:ffff0000"),
    "verdicts": lambda r: r["verdicts"][0].__setitem__("note", "edited after signing"),
    "attestation": lambda r: r["attestation"].__setitem__("issuer", "another-service"),
    "reproducibility": lambda r: r["reproducibility"].__setitem__("digest_convention", "other"),
}

base_digest = ucr.digest_of(BASE)
covered = set(ucr.DIGEST_FIELDS)
rows, bad = [], 0

for field, mutate in MUTATIONS.items():
    rec = copy.deepcopy(BASE)
    mutate(rec)
    new_digest = ucr.digest_of(rec)
    moved = new_digest != base_digest
    rep = ucr.verify(rec, {"procedure": "QP-8.2", "revision": "8.2"})
    failing = [c["check_id"] for c in rep["checks"] if c["result"] == "fail"]
    ne = [c["check_id"] for c in rep["checks"] if c["result"] == "not_evaluated"]

    expect_moved = field in covered
    if expect_moved:
        # covered: digest must move, and the record must not resolve to a positive outcome
        ok = moved and rep["outcome"]["verification"] in ("rejected", "unresolved")
        note = "OK"
    else:
        # outside the digest by design: digest must NOT move. Protection for these
        # fields comes from the envelope signature (ucr.py scitt), not the payload.
        ok = (not moved) and rep["outcome"]["verification"] == "verified"
        note = "OK (boundary)"
    bad += 0 if ok else 1
    rows.append((field, "covered" if expect_moved else "outside", "yes" if moved else "no",
                 rep["outcome"]["verification"], ",".join(failing) or "-", ",".join(ne) or "-",
                 note if ok else "UNEXPECTED"))

print(f"{'field':18} {'in digest':9} {'digest moves':12} {'outcome':11} {'fails':18} {'not_eval':16} verdict")
for r in rows:
    print(f"{r[0]:18} {r[1]:9} {r[2]:12} {r[3]:11} {r[4]:18} {r[5]:16} {r[6]}")
print(f"\nMUTATE {'OK' if bad == 0 else 'FAILED'} — {len(rows) - bad}/{len(rows)} mutations behave as designed")
sys.exit(0 if bad == 0 else 7)
