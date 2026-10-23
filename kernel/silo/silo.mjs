#!/usr/bin/env node
/**
 * OASIS / KET Kernel Silo — acceptance prove.
 * Does not import frozen ket.mjs / kernel0.mjs.
 */
import { createSilo, SPEC, LAYER_META, layerShape, boxBulge, parseWavePayload, proveSilo } from './silo-kernel.mjs';

const failures = [];
function assert(cond, id, msg) {
  if (!cond) failures.push({ id, msg });
}

const fresh = createSilo();
assert(fresh.state.boxFlexFraction === 0.02875, 'D0', `default flex ${fresh.state.boxFlexFraction}`);
assert(Math.abs(boxBulge(2, SPEC.boxFlexFraction) - 2 * 0.02875) < 1e-12, 'D1', 'bulge = halfSide × 0.02875');
assert(LAYER_META.length === 10, 'D2', 'LAYER_META length');
for (let n = 1; n <= 10; n++) {
  const expect = n % 2 === 1 ? 'toroid' : 'box';
  assert(layerShape(n) === expect, 'D3', `layerShape(${n})`);
  assert(LAYER_META[n - 1].shape === expect, 'D4', `LAYER_META[${n}]`);
}
assert(SPEC.notationTenBang === '10!', 'D5', 'preserve 10! notation');
assert(SPEC.factorialTen !== SPEC.layerCount, 'D6', 'factorial is not layer count');
assert(SPEC.workspaceCount === 6, 'D7', 'six workspace addresses');
assert(SPEC.lanes.length === 5, 'D8', 'five VAINL lanes');

const wave = parseWavePayload();
assert(wave.bitCount === 49, 'D9', '49 explicit bits');
assert(wave.controlBitsAsserted === false, 'D10', 'no silent control bits');

let threw = false;
try {
  layerShape(0);
} catch {
  threw = true;
}
assert(threw, 'D11', 'level 0 (scalar) is not a geometry level');

const report = proveSilo(fresh);
assert(report.ok, 'P0', report.issues.map((i) => i.id + ':' + i.msg).join('; ') || 'proveSilo');

const seq = createSilo();
const h1 = seq.transition('YES');
const h2 = seq.transition('NO');
assert(seq.state.history.length === 2, 'H0', 'two transitions → two records');
assert(h1.seq === 1 && h2.seq === 2, 'H1', 'sequence numbers');
assert(seq.state.simulatedSeconds === 4, 'H2', '+2s per commit');
seq.resetDemo();
assert(seq.state.history.length === 0 && seq.state.step === 0, 'H3', 'reset clears demo history only');
assert(seq.state.layerCount === 10, 'H4', 'reset preserves kernel geometry');

if (failures.length || !report.ok) {
  console.error('SILO PROVE FAIL');
  for (const f of failures) console.error('  ' + f.id + '  ' + f.msg);
  for (const i of report.issues) console.error('  ' + i.id + '  ' + i.msg);
  process.exit(1);
}

console.log('SILO PROVE PASS');
console.log(`  layers     ${SPEC.layerCount}  odd=toroid even=box  scalar=0 (referent)`);
console.log(`  flex       ${SPEC.boxFlexFraction}  (${SPEC.boxFlexPercent}%)  bulge=halfSide×flex`);
console.log(`  workspaces ${SPEC.workspaceCount}  ${SPEC.workspaceNotation}`);
console.log(`  lanes      ${SPEC.lanes.join(' ')}  grouping configurable (proposal not law)`);
console.log(`  authority  ${SPEC.authority.join(' → ')} → SCALAR 0`);
console.log(`  time       +${SPEC.futureWindowSeconds}s / commit · append-only demo journal`);
console.log(`  wave       ${wave.groups.length}×${SPEC.waveBitsPerGroup} = ${wave.bitCount} bits · 3-1-3 · control bits NOT asserted`);
console.log(`  notation   ${SPEC.notationTenBang} preserved; ${SPEC.factorialTen} is factorial, not layer count`);
console.log(`  mnemonic   ${SPEC.connectivityMnemonic.join(', ')}  (connectivity, not chemical valence)`);
console.log('  frozen KET not imported');
