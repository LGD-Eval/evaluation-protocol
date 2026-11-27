#!/usr/bin/env node
/**
 * UCR v0.1 — independent verifier, Node implementation.
 *
 * Deliberately written from the published convention only (README.md +
 * schema/ucr-v0.1.schema.json), not from ucr.py. Its purpose is to show that a
 * party with a different runtime can reach the same verdict on the same record:
 *
 *   node verify_node.js vectors/case-01-valid.json
 *
 * Output: the same report shape as `ucr.py verify`, printed as JSON.
 * Exit code: 0 verified / 2 unresolved / 3 rejected / 1 bad input.
 */
const fs = require("fs");
const crypto = require("crypto");

const SCHEMA_ID = "ucr/record/v0.3";
const SCHEMA_ID_V4 = "ucr/record/v0.4";
const DIGEST_FIELDS = ["schema", "artefact", "mandate", "delegation", "process_state", "compared_state", "evidence", "verdicts"];
const REQUIRED_CHECKS = ["C1_schema", "C2_digest", "C3_mandate_chain", "C4_state_version",
                         "C5_evidence_present", "C6_verdict_complete", "C7_no_private_state"];
const VERIFIABLE_KINDS = ["audit", "repro-test", "process", "interop", "signed-credential"];
const REQUIRED_CHECKS_V4 = REQUIRED_CHECKS.concat(["C8_revocation_checked"]);
const FORBIDDEN = ["internal_url", "file_path", "api_token", "secret", "private_key",
                   "connection_string"];

function canonical(v) {
  if (Array.isArray(v)) return "[" + v.map(canonical).join(",") + "]";
  if (v && typeof v === "object") {
    const keys = Object.keys(v).sort();
    return "{" + keys.map(k => JSON.stringify(k) + ":" + canonical(v[k])).join(",") + "}";
  }
  return JSON.stringify(v === undefined ? null : v);
}

function digestOf(rec) {
  const payload = {};
  for (const k of DIGEST_FIELDS) payload[k] = rec[k] === undefined ? null : rec[k];
  return crypto.createHash("sha256").update(canonical(payload), "utf8").digest("hex").slice(0, 16);
}

function scopeCovers(parent, child) {
  for (const key of ["workflow", "device_family"]) {
    if (parent && child && key in parent && key in child && parent[key] !== child[key]) return false;
  }
  if (parent && child && parent.artefact_types && child.artefact_types) {
    return child.artefact_types.every(t => parent.artefact_types.includes(t));
  }
  return true;
}

function placeholderPaths(obj, path) {
  const hits = [];
  const walk = (v, p) => {
    if (Array.isArray(v)) v.forEach((x, i) => walk(x, p + "/" + i));
    else if (v && typeof v === "object") {
      for (const k of Object.keys(v)) {
        if (k.startsWith("_")) continue;
        walk(v[k], p + "/" + k);
      }
    } else if (typeof v === "string") {
      const low = v.toLowerCase();
      if (["todo", "placeholder", "<fill", "changeme"].some(m => low.includes(m))) hits.push(p || "/");
    }
  };
  walk(obj, path || "");
  return hits;
}

function verify(rec, state) {
  const checks = [];
  const add = (id, result, code, note) =>
    checks.push({ check_id: id, result, reason_code: code || "none", note: note || "" });

  // C1
  const isV4 = rec.schema === SCHEMA_ID_V4;
  const need = ["schema", "artefact", "mandate", "process_state", "compared_state", "evidence", "verdicts"];
  if (isV4) need.push("evaluator");
  const missing = need.filter(k => !(k in rec));
  if (rec.schema !== SCHEMA_ID && rec.schema !== SCHEMA_ID_V4) add("C1_schema", "fail", "schema_mismatch", "schema is " + JSON.stringify(rec.schema));
  else if (missing.length) add("C1_schema", "fail", "schema_missing_field", "missing: " + missing.join(", "));
  else add("C1_schema", "pass");

  // C2
  const claimed = (rec.reproducibility || {}).payload_digest;
  const actual = digestOf(rec);
  if (claimed === actual) add("C2_digest", "pass");
  else add("C2_digest", "fail", "digest_mismatch",
           "claimed " + JSON.stringify(claimed) + ", recomputed " + actual);

  // C3
  const parent = (rec.mandate || {}).scope || {};
  const bad = [];
  for (const hop of rec.delegation || []) {
    if (!scopeCovers(parent, hop.scope || {}))
      bad.push(hop.grantee_agent || hop.grantee || "?");
  }
  if (bad.length) add("C3_mandate_chain", "fail", "scope_escalation",
                      "delegated scope exceeds the parent mandate for: " + bad.join(", "));
  else add("C3_mandate_chain", "pass");

  // C4 — decidable from the record alone: the record names what it compared against
  const ps = rec.process_state || {};
  const cs = rec.compared_state || {};
  if (!cs.procedure || !cs.revision) {
    add("C4_state_version", "not_evaluated", "no_compared_state",
        "record does not name the state the verifier compared against");
  } else if (state && (state.procedure !== cs.procedure || state.revision !== cs.revision)) {
    add("C4_state_version", "not_evaluated", "stale_comparison",
        `record compared against ${cs.procedure} rev ${cs.revision}, but the supplied state is ${state.procedure} rev ${state.revision}; the newest state is not confirmed`);
  } else if (cs.procedure !== ps.procedure || cs.revision !== ps.revision) {
    const stated = (rec.verdicts || []).filter(v => v.check_id === "C4_state_version");
    if (stated.some(v => v.result === "not_evaluated"))
      add("C4_state_version", "not_evaluated", "status_unavailable",
          `controlled state moved ${ps.procedure} rev ${ps.revision} -> ${cs.procedure} rev ${cs.revision}, and the effect on this artefact is not evaluated`);
    else add("C4_state_version", "fail", "state_change_unrecorded",
             "state moved between production and comparison and the record does not carry a not-evaluated verdict for it");
  } else {
    add("C4_state_version", "pass", "none",
        `compared state equals production state (${ps.procedure} rev ${ps.revision})`);
  }

  // C5
  const weak = [];
  for (const ev of rec.evidence || []) {
    if (!ev.ref) weak.push(`${ev.id || "?"}:no_ref`);
    else if (VERIFIABLE_KINDS.includes(ev.kind) && !(ev.reproducible && ev.timestamped))
      weak.push(`${ev.id || "?"}:not_reproducible_or_untimestamped`);
  }
  if (weak.length) add("C5_evidence_present", "not_evaluated", "missing_evidence",
                       "evidence exists but is not confirmable: " + weak.join(", "));
  else add("C5_evidence_present", "pass");

  // C6
  const declared = {};
  for (const v of rec.verdicts || []) declared[v.check_id] = v.result;
  const req = (rec.schema === SCHEMA_ID) ? REQUIRED_CHECKS : REQUIRED_CHECKS_V4;
  const blanks = req.filter(c => !(c in declared));
  if (blanks.length) add("C6_verdict_complete", "not_evaluated", "verdict_missing",
                         "no verdict stated for: " + blanks.join(", "));
  else add("C6_verdict_complete", "pass");

  // C7
  const leaks = [];
  function walk(obj, path) {
    if (Array.isArray(obj)) obj.forEach((v, i) => walk(v, path + "/" + i));
    else if (obj && typeof obj === "object")
      for (const k of Object.keys(obj)) {
        if (FORBIDDEN.some(h => k.toLowerCase().includes(h))) leaks.push(path + "/" + k);
        walk(obj[k], path + "/" + k);
      }
  }
  const scanned = {};
  for (const k of ["artefact", "mandate", "delegation", "process_state", "evidence"])
    scanned[k] = rec[k] === undefined ? null : rec[k];
  walk(scanned, "");
  if (leaks.length) add("C7_no_private_state", "fail", "private_state_reference",
                        "record points at producer-private state: " + leaks.join(", "));
  else add("C7_no_private_state", "pass");

  // C8 revocation (v0.4 only)
  if (rec.schema === SCHEMA_ID_V4) {
    const rev = ((rec.mandate || {}).revocation) || {};
    const st = String(rev.status || "").toLowerCase();
    if (!st) add("C8_revocation_checked", "not_evaluated", "revocation_unchecked",
                 "the record carries no revocation state; an unchecked revocation blocks a positive outcome");
    else if (st === "revoked" || st === "revoked_at") add("C8_revocation_checked", "fail", "mandate_revoked",
                 "mandate revoked at " + String(rev.checked_at || "unknown time"));
    else if (!rev.checked_at) add("C8_revocation_checked", "not_evaluated", "revocation_unverified",
                 "revocation stated active but neither timestamped nor sourced");
    else add("C8_revocation_checked", "pass", "none",
             "revocation checked " + String(rev.checked_at) + " by " + String(rev.source || "unspecified"));
  }

  const results = checks.map(c => c.result);
  let verification = "verified", action = "allow";
  if (results.includes("fail")) { verification = "rejected"; action = "deny"; }
  else if (results.includes("not_evaluated")) { verification = "unresolved"; action = "defer"; }

  // Unfilled placeholders: no extra check, but a verified outcome is withheld.
  const ph = placeholderPaths(rec, "");
  if (ph.length && verification === "verified") { verification = "unresolved"; action = "defer"; }
  if (ph.length) console.warn("WARNING: record carries " + ph.length + " unfilled placeholder(s): " + ph.slice(0, 12).join(", "));

  return {
    schema: "ucr/verification-report/v0.1",
    verifier: "node/" + process.versions.node,
    artefact_id: (rec.artefact || {}).id,
    outcome: { verification, policy_action: action },
    checks,
    counts: {
      pass: results.filter(r => r === "pass").length,
      fail: results.filter(r => r === "fail").length,
      not_evaluated: results.filter(r => r === "not_evaluated").length,
      total: results.length,
    },
    recomputed_digest: actual,
    claimed_digest: claimed,
    placeholder_warnings: ph,
  };
}

const file = process.argv[2];
if (!file) { console.error("usage: node verify_node.js <case.json>"); process.exit(1); }
let bundle;
try { bundle = JSON.parse(fs.readFileSync(file, "utf8")); }
catch (e) { console.error("bad json:", e.message); process.exit(1); }

const rec = bundle.record || bundle;
const state = bundle.current_state || null;
const report = verify(rec, state);
console.log(JSON.stringify(report, null, 2));
process.exit({ verified: 0, unresolved: 2, rejected: 3 }[report.outcome.verification]);
