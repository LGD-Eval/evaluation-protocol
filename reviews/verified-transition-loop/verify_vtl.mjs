// verify_vtl.mjs — independent reproduction of VTL canonical digests
// Runs the prototype's own canonicalizer against its published fixtures.
import fs from 'node:fs';
import path from 'node:path';
import { strictParse, canonicalSha256, canonicalBytes } from './canonical-runtime-v0.12.mjs';

const dir = '.';
const fixtures = [
  'attested-dispatch-v0.8', 'canonical-proof-v0.10', 'canonical-signed-envelope-v0.11',
  'canonical-trust-root-snapshot-v0.12', 'tool-dispatch-receipt-v0.7', 'transparency-log-v0.14',
  'trust-root-snapshot-v0.9', 'use-time-conformance-v0.4', 'witnessed-freshness-v0.13'
];
let pass = 0;
for (const f of fixtures) {
  const raw = fs.readFileSync(path.join(dir, `${f}.json`), 'utf8');
  let parsed;
  try { parsed = strictParse(raw); pass++; } catch (e) { console.log(`${f}: strictParse FAIL ${e.code}`); continue; }
  const digest = canonicalSha256(parsed);
  const bytes = canonicalBytes(parsed).length;
  console.log(`${f}: digest=${digest} canonicalBytes=${bytes} parse=OK`);
}
console.log(`\nstrictParse passed: ${pass}/${fixtures.length}`);
