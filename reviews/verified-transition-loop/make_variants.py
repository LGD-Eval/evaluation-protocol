#!/usr/bin/env python
# make_variants.py — build adversarial variants of the VTL transparency-log fixture.
# Inputs: transparency-log-v0.14.json (prototype fixture). Outputs: _variant_A/B.json.
# Usage: python make_variants.py <fixture.json> <outdir>
import json, copy, sys, os

fix = json.load(open(sys.argv[1], encoding="utf-8"))
outdir = sys.argv[2] if len(sys.argv) > 2 else "."
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
