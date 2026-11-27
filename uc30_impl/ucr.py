#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UCR — Use Case 30 record toolchain (reference implementation, v0.3).

Commands
--------
  python ucr.py gen-vectors         build the conformance vectors under vectors/
  python ucr.py selftest            run every vector and assert the expected outcome
  python ucr.py emit manifest.json -o record.json
                                    build a record from a manifest, naming every check
                                    that has no verdict as not_evaluated (R5)
  python ucr.py verify record.json [--state current_state.json] -o report.json
                                    offline verification; exit 0 = verified,
                                    2 = unresolved, 3 = rejected, 1 = input error

Scope note: this implements the record semantics and the check outcomes of
FG-TIDA use-cases#30 section 5 (R1-R3, R5) and section 6 (decidable count).
It is a reference implementation for discussion, not a product, and it makes
no claim of independent validation.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

SCHEMA_ID = "ucr/record/v0.3"
SCHEMA_ID_V4 = "ucr/record/v0.4"  # v0.4: + C8 revocation, + evaluator declaration

# Digest convention, identical to the LGD-Eval conclusion convention:
#   sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False))[:16]
DIGEST_CONVENTION = ('sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), '
                     'ensure_ascii=False))[:16]')
# v0.2 binds the record's own schema id into the digest. In v0.1 the schema id sat
# outside the digest, so swapping the declared version changed no digest and was
# caught only structurally (C1). v0.2 closes that gap: a version swap now also
# breaks C2. `attestation` stays outside the digest so re-signing does not
# invalidate the payload.
# v0.3 adds `compared_state` to the payload: the record names the state the
# verifier compared the production state against, so C4 is decidable from the
# record alone. A comparison against a later state is a new sealed revision of
# the record (append-only), never an edit of the earlier one.
DIGEST_FIELDS = ("schema", "artefact", "mandate", "delegation", "process_state",
                 "compared_state", "evidence", "verdicts")

# Checks the verifier always evaluates. Any check without a verdict in the
# record is reported as not_evaluated, never as a pass.
REQUIRED_CHECKS = [
    "C1_schema",
    "C2_digest",
    "C3_mandate_chain",
    "C4_state_version",
    "C5_evidence_present",
    "C6_verdict_complete",
    "C7_no_private_state",
]

# v0.4 adds one check: an authority can be revoked after the record was produced.
REQUIRED_CHECKS_V4 = REQUIRED_CHECKS + ["C8_revocation_checked"]

VERIFIABLE_KINDS = {"audit", "repro-test", "process", "interop", "signed-credential"}
FORBIDDEN_KEY_HINTS = ("internal_url", "file_path", "api_token", "secret", "private_key",
                       "connection_string")


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_of(record: dict) -> str:
    payload = {k: record.get(k) for k in DIGEST_FIELDS}
    return hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()[:16]


def sha256_filelike(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


# --------------------------------------------------------- placeholder lint

_PLACEHOLDER_MARKERS = ("todo", "placeholder", "<fill", "changeme")


def _placeholder_paths(obj, path=""):
    """Paths whose value still looks like a template slot.

    Every check here is structural: a manifest with "hash": "sha256:TODO" is
    well formed, so it passes C1/C2 and the record reads "verified". That is
    the overclaim this convention exists to prevent, so placeholders are
    caught before sealing and re-reported at verification.
    """
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).startswith("_"):
                continue
            hits += _placeholder_paths(v, path + "/" + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += _placeholder_paths(v, path + "/" + str(i))
    elif isinstance(obj, str):
        low = obj.lower()
        if any(m in low for m in _PLACEHOLDER_MARKERS):
            hits.append(path or "/")
    return hits


# --------------------------------------------------------------------------- emit

def emit(manifest: dict) -> dict:
    """Turn a manifest into a record. Missing verdicts become not_evaluated."""
    # Refuse to seal a manifest that still carries placeholders. Without this,
    # a template full of TODO emits a record that verify() calls "verified",
    # because the checks are structural and cannot tell a filled field from a
    # well-formed placeholder. Lint at the door, not at the reader.
    if not manifest.get("_allow_placeholders"):
        hits = _placeholder_paths(manifest)
        if hits:
            raise SystemExit(
                "refusing to emit: %d unfilled placeholder(s): %s\n"
                "replace them, or pass \"_allow_placeholders\": true if this is a dry run"
                % (len(hits), ", ".join(hits[:12])))
    rec = {
        "schema": SCHEMA_ID,
        "artefact": manifest["artefact"],
        "mandate": manifest["mandate"],
        "delegation": manifest.get("delegation", []),
        "process_state": manifest["process_state"],
        "evidence": manifest.get("evidence", []),
        "verdicts": manifest.get("verdicts", []),
        "attestation": manifest.get("attestation", {
            "issuer": "unspecified", "issued_at": manifest["artefact"].get("produced_at"),
            "key_id": "unspecified",
        }),
    }
    if manifest.get("compared_state"):
        rec["compared_state"] = manifest["compared_state"]
    present = {v.get("check_id") for v in rec["verdicts"]}
    for cid in REQUIRED_CHECKS:
        if cid not in present:
            rec["verdicts"].append({
                "check_id": cid,
                "result": "not_evaluated",
                "reason_code": "not_run",
                "note": "no verdict supplied by the producer; named here rather than assumed",
            })
    rec["reproducibility"] = {"digest_convention": DIGEST_CONVENTION,
                              "payload_digest": digest_of(rec)}
    return rec


# ------------------------------------------------------------------------- verify

def _scope_covers(parent: dict, child: dict) -> bool:
    """Child scope must not exceed parent scope on any dimension."""
    for key in ("workflow", "device_family"):
        if key in parent and key in child and parent[key] != child[key]:
            return False
    if "artefact_types" in parent and "artefact_types" in child:
        if not set(child["artefact_types"]) <= set(parent["artefact_types"]):
            return False
    return True


def verify(record: dict, current_state: dict | None = None) -> dict:
    checks = []

    def add(cid, result, code="none", note=""):
        checks.append({"check_id": cid, "result": result, "reason_code": code, "note": note})

    # C1 schema
    req_keys = ["schema", "artefact", "mandate", "process_state",
                "compared_state", "evidence", "verdicts"]
    if record.get("schema") == SCHEMA_ID_V4:
        req_keys.append("evaluator")
    missing = [k for k in req_keys if k not in record]
    if record.get("schema") not in (SCHEMA_ID, SCHEMA_ID_V4):
        add("C1_schema", "fail", "schema_mismatch", f"schema is {record.get('schema')!r}")
    elif missing:
        add("C1_schema", "fail", "schema_missing_field", "missing: " + ", ".join(missing))
    else:
        add("C1_schema", "pass")

    # C2 digest
    claimed = record.get("reproducibility", {}).get("payload_digest")
    actual = digest_of(record)
    if claimed == actual:
        add("C2_digest", "pass")
    else:
        add("C2_digest", "fail", "digest_mismatch",
            f"claimed {claimed!r}, recomputed {actual}")

    # C3 mandate chain: every hop narrows, never widens
    parent_scope = record.get("mandate", {}).get("scope", {})
    bad = []
    for hop in record.get("delegation", []):
        if not _scope_covers(parent_scope, hop.get("scope", {})):
            bad.append(hop.get("grantee_agent") or hop.get("grantee") or "?")
    if bad:
        add("C3_mandate_chain", "fail", "scope_escalation",
            "delegated scope exceeds the parent mandate for: " + ", ".join(bad))
    else:
        add("C3_mandate_chain", "pass")

    # C4 state version: the record names the state it compared production
    # against, so the verdict is decidable from the record alone.
    ps = record.get("process_state", {}) or {}
    cs = record.get("compared_state", {}) or {}
    if not cs.get("procedure") or not cs.get("revision"):
        add("C4_state_version", "not_evaluated", "no_compared_state",
            "record does not name the state the verifier compared against")
    elif current_state and (current_state.get("procedure") != cs.get("procedure") or
                            current_state.get("revision") != cs.get("revision")):
        add("C4_state_version", "not_evaluated", "stale_comparison",
            f"record compared against {cs.get('procedure')} rev {cs.get('revision')}, "
            f"but the supplied state is {current_state.get('procedure')} rev "
            f"{current_state.get('revision')}; the newest state is not confirmed")
    elif (cs.get("procedure") != ps.get("procedure") or
          cs.get("revision") != ps.get("revision")):
        stated = [v for v in record.get("verdicts", [])
                  if v.get("check_id") == "C4_state_version"]
        if any(v.get("result") == "not_evaluated" for v in stated):
            add("C4_state_version", "not_evaluated", "status_unavailable",
                f"controlled state moved {ps.get('procedure')} rev {ps.get('revision')} -> "
                f"{cs.get('procedure')} rev {cs.get('revision')}, and the effect on this "
                "artefact is not evaluated")
        else:
            add("C4_state_version", "fail", "state_change_unrecorded",
                "state moved between production and comparison and the record does not "
                "carry a not-evaluated verdict for it")
    else:
        add("C4_state_version", "pass", "none",
            f"compared state equals production state "
            f"({ps.get('procedure')} rev {ps.get('revision')})")

    # C5 evidence present and strong enough to be checked
    weak = []
    for ev in record.get("evidence", []):
        kind = ev.get("kind")
        if not ev.get("ref"):
            weak.append(f"{ev.get('id', '?')}:no_ref")
        elif kind in VERIFIABLE_KINDS and not (ev.get("reproducible") and ev.get("timestamped")):
            weak.append(f"{ev.get('id', '?')}:not_reproducible_or_untimestamped")
    if weak:
        add("C5_evidence_present", "not_evaluated", "missing_evidence",
            "evidence exists but is not confirmable: " + ", ".join(weak))
    else:
        add("C5_evidence_present", "pass")

    # C6 verdict completeness — the record must state every required check
    req_checks = REQUIRED_CHECKS if record.get("schema") == SCHEMA_ID else REQUIRED_CHECKS_V4
    declared = {v.get("check_id"): v.get("result") for v in record.get("verdicts", [])}
    blanks = [c for c in req_checks if c not in declared]
    if blanks:
        add("C6_verdict_complete", "not_evaluated", "verdict_missing",
            "no verdict stated for: " + ", ".join(blanks))
    else:
        add("C6_verdict_complete", "pass")

    # C7 no private state — verifiable from outside means hashes and ids only
    leaks = []
    def walk(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if any(h in str(k).lower() for h in FORBIDDEN_KEY_HINTS):
                    leaks.append(path + "/" + str(k))
                walk(v, path + "/" + str(k))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, path + f"/{i}")
    walk({k: record.get(k) for k in ("artefact", "mandate", "delegation", "process_state", "evidence")})
    if leaks:
        add("C7_no_private_state", "fail", "private_state_reference",
            "record points at producer-private state: " + ", ".join(leaks))
    else:
        add("C7_no_private_state", "pass")

    # C8 revocation (v0.4 only): the relying party supplies the revocation state;
    # the producer's own assertion is not accepted as a check.
    if record.get("schema") == SCHEMA_ID_V4:
        rev = (record.get("mandate") or {}).get("revocation") or {}
        st = str(rev.get("status") or "").lower()
        if not st:
            add("C8_revocation_checked", "not_evaluated", "revocation_unchecked",
                "the record carries no revocation state; an unchecked revocation blocks a positive outcome")
        elif st in ("revoked", "revoked_at"):
            add("C8_revocation_checked", "fail", "mandate_revoked",
                "mandate revoked at " + str(rev.get("checked_at") or "unknown time"))
        elif not rev.get("checked_at"):
            add("C8_revocation_checked", "not_evaluated", "revocation_unverified",
                "revocation stated active but neither timestamped nor sourced")
        else:
            add("C8_revocation_checked", "pass", "none",
                "revocation checked " + str(rev.get("checked_at")) + " by " + str(rev.get("source") or "unspecified"))

    results = [c["result"] for c in checks]
    if "fail" in results:
        outcome, action = "rejected", "deny"
    elif "not_evaluated" in results:
        outcome, action = "unresolved", "defer"
    else:
        outcome, action = "verified", "allow"

    # A failure stated inside the record is still information; report it.
    stated = [v for v in record.get("verdicts", []) if v.get("result") == "fail"]
    # Unfilled placeholders are a warning, not a verdict: the checks are
    # structural, so a well-formed "TODO" passes them. Say so instead of
    # letting it read as verified.
    ph = _placeholder_paths(record)
    if ph and outcome == "verified":
        # A structurally valid record with unfilled fields is not verified.
        # No extra check is added (the seven-check surface stays as filed);
        # the outcome itself is withheld, which is the same rule the checks use.
        outcome, action = "unresolved", "defer"
    report = {
        "schema": "ucr/verification-report/v0.1",
        "artefact_id": record.get("artefact", {}).get("id"),
        "outcome": {"verification": outcome, "policy_action": action},
        "checks": checks,
        "stated_failures": stated,
        "counts": {
            "pass": results.count("pass"),
            "fail": results.count("fail"),
            "not_evaluated": results.count("not_evaluated"),
            "total": len(results),
        },
        "recomputed_digest": actual,
        "claimed_digest": claimed,
        "verifier_note": ("Decidable count only: no composite score. Anything not evaluated is "
                          "reported as not_evaluated and counted against the record, never as a pass."),
        "placeholder_warnings": ph,
    }
    if ph:
        print("WARNING: record carries %d unfilled placeholder(s): %s"
              % (len(ph), ", ".join(ph[:12])))
    return report


# ------------------------------------------------------------------------- interop

def record_digest_full(record: dict) -> str:
    """Full-length digest over the same payload the short digest covers."""
    payload = {k: record.get(k) for k in DIGEST_FIELDS}
    return hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()


def scitt_statement(record: dict, report: dict | None = None) -> dict:
    """Shape the record for registration by a Transparency Service (RFC 9943).

    This is a registration request, not a receipt: registering a statement
    proves it existed at a point in time, not that any check ran.
    """
    att = record.get("attestation", {}) or {}
    art = record.get("artefact", {}) or {}
    payload = {
        "subject": f"urn:ucr:artefact:{art.get('id')}",
        "record_schema": SCHEMA_ID,
        "record_digest_sha256": record_digest_full(record),
        "payload_digest": (record.get("reproducibility") or {}).get("payload_digest"),
        "digest_convention": DIGEST_CONVENTION,
    }
    if report:
        payload["verification"] = report["outcome"]
        payload["counts"] = report["counts"]
        payload["check_results"] = {c["check_id"]: c["result"] for c in report["checks"]}
    return {
        "schema": "ucr/scitt-statement/v0.1",
        "profile_note": ("Statement shaped for a SCITT Transparency Service. Registration proves "
                         "the statement existed and was logged; it does not prove any check ran or "
                         "that the artefact may be relied on. This object asserts no receipt."),
        "protected": {
            "content_type": "application/json",
            "issuer": att.get("issuer"),
            "issued_at": att.get("issued_at"),
            "key_id": att.get("key_id"),
        },
        "payload": payload,
        "receipt": None,
    }


def authzen_evidence(decision: dict, index: int = 1) -> dict:
    """Turn an AuthZEN decision (SARC + decision) into a record evidence entry.

    The decision is referenced by hash so it stays checkable, and the verdict
    label keeps runtime permission distinct from a compliance conclusion.
    """
    ref = "sha256:" + hashlib.sha256(canonical(decision).encode("utf-8")).hexdigest()
    raw = decision.get("decision")
    label = {True: "permit", False: "deny"}.get(raw, str(raw))
    if label not in ("permit", "deny"):
        label = "defer"
    note = ("runtime authorization decision captured as evidence; a permit here is not a "
            "compliance verdict, and a deny here must not be reported as allow")
    return {
        "id": f"EV-AUTHZEN-{index}",
        "kind": "interop",
        "ref": ref,
        "reproducible": True,
        "timestamped": bool(decision.get("decided_at")),
        "policy_identity": decision.get("pdp") or decision.get("policy_id") or "unspecified",
        "decision": label,
        "decision_id": decision.get("decision_id"),
        "decided_at": decision.get("decided_at"),
        "subject": (decision.get("subject") or {}).get("id"),
        "note": note,
    }


def cmd_scitt(args):
    rec = json.loads(Path(args.record).read_text(encoding="utf-8"))
    rep = None
    if args.state:
        state = json.loads(Path(args.state).read_text(encoding="utf-8"))
        rep = verify(rec, state)
    stmt = scitt_statement(rec, rep)
    text = json.dumps(stmt, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print("wrote", args.out, "record_digest", stmt["payload"]["record_digest_sha256"][:16])
    else:
        print(text)
    return 0


def cmd_authzen(args):
    decision = json.loads(Path(args.decision).read_text(encoding="utf-8"))
    entry = authzen_evidence(decision, args.index)
    out = {"evidence_entry": entry,
           "how_to_use": ("append this object to the record's evidence[] array, then re-emit "
                          "so the digest covers it; the record stays verifiable from outside")}
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print("wrote", args.out, "decision", entry["decision"], "ref", entry["ref"][:25])
    else:
        print(text)
    return 0


# ------------------------------------------------------------------------ vectors

BASE = {
    "artefact": {
        "id": "CIA-2026-014",
        "type": "change-impact-assessment",
        "device": {"id": "D-114", "family": "IVD"},
        "hash": "sha256:6f1c2d9a4b7e8f10",
        "produced_at": "2026-05-20T09:12:00Z",
    },
    "mandate": {
        "id": "M-2026-014", "version": "3",
        "grantor": {"role": "manufacturer-compliance-owner", "id": "OWNER-01"},
        "grantee": {"agent_id": "A-LEAD-07"},
        "scope": {"workflow": "change-impact-assessment", "device_family": "IVD",
                  "artefact_types": ["change-impact-assessment", "evidence-index"]},
        "regime": ["EU MDR 2017/745", "FDA 21 CFR 820"],
        "valid_from": "2026-03-01", "valid_to": "2026-09-30",
    },
    "delegation": [
        {"grantor_agent": "A-LEAD-07", "grantee_agent": "A-T1", "sop": "QP-8.2",
         "scope": {"workflow": "change-impact-assessment", "device_family": "IVD",
                   "artefact_types": ["change-impact-assessment"]}},
        {"grantor_agent": "A-LEAD-07", "grantee_agent": "A-T2", "sop": "QP-8.2",
         "scope": {"workflow": "change-impact-assessment", "device_family": "IVD",
                   "artefact_types": ["evidence-index"]}},
    ],
    "process_state": {"procedure": "QP-8.2", "revision": "8.2", "captured_at": "2026-05-20T09:05:00Z"},
    "compared_state": {"procedure": "QP-8.2", "revision": "8.2", "captured_at": "2026-05-20T09:12:00Z",
                       "asserted_by": "A-LEAD-07@emission"},
    "evidence": [
        {"id": "EV-1", "kind": "signed-credential", "ref": "sha256:aa01bb02", "reproducible": True,
         "timestamped": True},
        {"id": "EV-2", "kind": "process", "ref": "sha256:cc03dd04", "reproducible": True,
         "timestamped": True},
        {"id": "EV-3", "kind": "audit", "ref": "sha256:ee05ff06", "reproducible": True,
         "timestamped": True},
    ],
    "attestation": {"issuer": "attestation-service", "issued_at": "2026-05-20T09:13:00Z",
                    "key_id": "as-key-2026"},
}

STATE_SAME = {"procedure": "QP-8.2", "revision": "8.2"}
STATE_MOVED = {"procedure": "QP-8.3", "revision": "8.3"}


def build_vectors() -> dict:
    """Five conformance vectors, each with an expected outcome."""
    cases = []

    # 01 clean: everything stated, state unchanged
    v1 = emit(copy.deepcopy(BASE))
    cases.append(("case-01-valid", v1, STATE_SAME, "verified", "allow"))

    # 02 scope escalation: a task agent claims more than its lead held
    m2 = copy.deepcopy(BASE)
    m2["delegation"][1]["scope"]["artefact_types"] = ["change-impact-assessment", "evidence-index",
                                                     "submission-dossier"]
    m2["delegation"][1]["scope"]["device_family"] = "IVD+"
    cases.append(("case-02-scope-escalation", emit(m2), STATE_SAME, "rejected", "deny"))

    # 03 state moved and nobody evaluated it -> the record carries the comparison,
    #    so the verifier decides without asking the producer for current state
    m3 = copy.deepcopy(BASE)
    m3["compared_state"] = {"procedure": "QP-8.3", "revision": "8.3",
                            "captured_at": "2026-06-14T10:00:00Z",
                            "asserted_by": "auditor review 2026-06-14"}
    m3["verdicts"] = [{"check_id": "C4_state_version", "result": "not_evaluated",
                       "reason_code": "status_unavailable",
                       "note": "QP-8.2 superseded by QP-8.3 on 2026-06-14; effect on this artefact not assessed"}]
    cases.append(("case-03-state-unevaluated", emit(m3), None, "unresolved", "defer"))

    # 04 evidence present but not confirmable (no hash, untimestamped)
    m4 = copy.deepcopy(BASE)
    m4["evidence"][1]["reproducible"] = False
    m4["evidence"][1]["timestamped"] = False
    cases.append(("case-04-evidence-weak", emit(m4), STATE_SAME, "unresolved", "defer"))

    # 05 tampered artefact hash after signing -> digest mismatch
    v5 = emit(copy.deepcopy(BASE))
    v5["artefact"]["hash"] = "sha256:deadbeef0000"
    cases.append(("case-05-tampered", v5, STATE_SAME, "rejected", "deny"))

    # 06 wrong schema version -> C1 fail. The digest is recomputed after the swap,
    #     so this vector shows that version admission is independent of integrity:
    #     an internally consistent record is still refused if its declared version
    #     is not the one the verifier accepts.
    m6 = copy.deepcopy(BASE)
    v6 = emit(m6)
    v6["schema"] = "ucr/record/v0.5"  # unknown version: v0.4 is now accepted
    v6["reproducibility"]["payload_digest"] = digest_of(v6)
    cases.append(("case-06-schema-version", v6, STATE_SAME, "rejected", "deny"))

    # 07 private state reference -> C7 fail (record points at a producer path)
    m7 = copy.deepcopy(BASE)
    m7["evidence"].append({"id": "EV-4", "kind": "process", "ref": "sha256:11223344",
                           "reproducible": True, "timestamped": True,
                           "file_path": "/opt/qms/records/QP-8.2/batch-114.pdf"})
    v7 = emit(m7)
    cases.append(("case-07-private-state", v7, STATE_SAME, "rejected", "deny"))

    # 08 a required verdict was dropped after emitting -> C6 not_evaluated
    v8 = emit(copy.deepcopy(BASE))
    v8["verdicts"] = [x for x in v8["verdicts"] if x["check_id"] != "C7_no_private_state"]
    v8["reproducibility"]["payload_digest"] = digest_of(v8)  # keep the record self-consistent
    cases.append(("case-08-verdict-missing", v8, STATE_SAME, "unresolved", "defer"))

    # 09 no compared_state at all -> the record cannot say what it was compared
    #    against, so it is structurally refused (C1), not silently passed
    m9 = copy.deepcopy(BASE)
    del m9["compared_state"]
    v9 = emit(m9)
    cases.append(("case-09-no-compared-state", v9, None, "rejected", "deny"))

    # 10 a newer state is supplied than the one the record compared against ->
    #    freshness gap is named, defer. The record is not rewritten; a later
    #    comparison is a new sealed revision.
    v10 = emit(copy.deepcopy(BASE))
    cases.append(("case-10-stale-comparison", v10, STATE_MOVED, "unresolved", "defer"))

    # 11 v0.4: the authority was revoked after production -> C8 fail, deny
    v11 = emit(copy.deepcopy(BASE))
    v11["schema"] = SCHEMA_ID_V4
    v11["evaluator"] = {"id": "EV-2026-014", "relation": "INDEPENDENT", "declared_by": "relying_party"}
    v11["mandate"] = dict(v11["mandate"])
    v11["mandate"]["revocation"] = {"status": "revoked", "checked_at": "2026-11-26T09:00:00Z",
                                    "source": "authority register rev-check"}
    v11["verdicts"] = list(v11["verdicts"]) + [{"check_id": "C8_revocation_checked", "result": "fail"}]
    v11["reproducibility"]["payload_digest"] = digest_of(v11)
    cases.append(("case-11-revoked", v11, STATE_SAME, "rejected", "deny"))

    # 12 v0.4: no revocation state at all -> C8 not_evaluated, defer (blocked, not passed)
    v12 = emit(copy.deepcopy(BASE))
    v12["schema"] = SCHEMA_ID_V4
    v12["evaluator"] = {"id": "EV-2026-014", "relation": "SELF", "declared_by": "producer"}
    v12["mandate"] = dict(v12["mandate"])
    v12["mandate"].pop("revocation", None)
    v12["verdicts"] = list(v12["verdicts"]) + [{"check_id": "C8_revocation_checked", "result": "not_evaluated"}]
    v12["reproducibility"]["payload_digest"] = digest_of(v12)
    cases.append(("case-12-revocation-unchecked", v12, STATE_SAME, "unresolved", "defer"))

    out = {"schema": "ucr/vectors/v0.4", "cases": []}
    for name, rec, state, exp_outcome, exp_action in cases:
        out["cases"].append({
            "name": name, "record": rec, "current_state": state,
            "expected": {"outcome": exp_outcome, "policy_action": exp_action},
        })
    return out


def cmd_gen_vectors(args):
    vectors = build_vectors()
    d = Path(args.dir)
    d.mkdir(parents=True, exist_ok=True)
    for c in vectors["cases"]:
        p = d / f"{c['name']}.json"
        p.write_text(json.dumps(
            {"record": c["record"], "current_state": c["current_state"], "expected": c["expected"]},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print("wrote", p.name)
    (d / "_index.json").write_text(json.dumps(
        {c["name"]: c["expected"] for c in vectors["cases"]}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"{len(vectors['cases'])} vectors written")


def cmd_selftest(args):
    vectors = build_vectors()
    failures = 0
    for c in vectors["cases"]:
        rep = verify(copy.deepcopy(c["record"]), c["current_state"])
        ok = (rep["outcome"]["verification"] == c["expected"]["outcome"] and
              rep["outcome"]["policy_action"] == c["expected"]["policy_action"])
        dig_ok = rep["claimed_digest"] == rep["recomputed_digest"]
        # a tampered record must NOT be digest-consistent
        dig_ok = dig_ok if c["name"] != "case-05-tampered" else (not dig_ok)
        print(f"{c['name']:26} outcome={rep['outcome']['verification']:11} "
              f"policy={rep['outcome']['policy_action']:6} digest={'ok' if dig_ok else 'MISMATCH'} "
              f"-> {'PASS' if ok and dig_ok else 'FAIL'}")
        failures += 0 if (ok and dig_ok) else 1
    print(f"\nSELFTEST {'OK' if failures == 0 else 'FAILED'} — {len(vectors['cases']) - failures}"
          f"/{len(vectors['cases'])} vectors as expected")
    return 0 if failures == 0 else 4


def cmd_emit(args):
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    rec = emit(manifest)
    out = Path(args.out) if args.out else Path("record.json")
    out.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", out, "digest", rec["reproducibility"]["payload_digest"])


def cmd_verify(args):
    rec = json.loads(Path(args.record).read_text(encoding="utf-8"))
    state = None
    if args.state:
        state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    rep = verify(rec, state)
    text = json.dumps(rep, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print("wrote", args.out)
    else:
        print(text)
    return {"verified": 0, "unresolved": 2, "rejected": 3}[rep["outcome"]["verification"]]


def main(argv=None):
    ap = argparse.ArgumentParser(description="UCR — Use Case 30 record toolchain")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gen-vectors")
    g.add_argument("--dir", default="vectors")
    g.set_defaults(func=cmd_gen_vectors)

    s = sub.add_parser("selftest")
    s.set_defaults(func=cmd_selftest)

    e = sub.add_parser("emit")
    e.add_argument("manifest")
    e.add_argument("-o", "--out")
    e.set_defaults(func=cmd_emit)

    v = sub.add_parser("verify")
    v.add_argument("record")
    v.add_argument("--state")
    v.add_argument("-o", "--out")
    v.set_defaults(func=cmd_verify)

    sc = sub.add_parser("scitt", help="shape a record as a SCITT registration statement")
    sc.add_argument("record")
    sc.add_argument("--state", help="optional current state, adds the verification outcome")
    sc.add_argument("-o", "--out")
    sc.set_defaults(func=cmd_scitt)

    az = sub.add_parser("authzen", help="turn an AuthZEN decision into an evidence entry")
    az.add_argument("decision")
    az.add_argument("--index", type=int, default=1)
    az.add_argument("-o", "--out")
    az.set_defaults(func=cmd_authzen)

    args = ap.parse_args(argv)
    rc = args.func(args)
    return rc if isinstance(rc, int) else 0


if __name__ == "__main__":
    sys.exit(main())
