import assert from 'node:assert/strict';
import {
  CYCLE, SCALE, GENESIS_HASH, auditPattern, isSelfSimilar,
  createCycleEngine, verifyLedger, asciiCycle,
} from './cycle.mjs';

let assertions = 0;
const test = (check, description) => { assert.ok(check, description); assertions++; };
const exact = (got, expected, description) => { assert.deepEqual(got, expected, description); assertions++; };

exact(SCALE, 10000, 'base scale');
exact(CYCLE.map(c => c.atUnits), [673367,333367,0,-333367,333367,673367], 'literal phases');
exact(CYCLE.map(c => c.operation), ['live','write','remember','forget','read','live'], 'literal order');
const pattern = auditPattern();
for (const [name, result] of Object.entries(pattern.checks)) test(result, `pattern invariant ${name}`);
test(pattern.pass, 'all invariants');
test(isSelfSimilar(), 'backwards-compatible predicate');
test(!isSelfSimilar(CYCLE.map((x,i) => ({ ...x, atUnits: i === 3 ? -333366 : x.atUnits }))), 'broken balance fails');
test(!auditPattern(CYCLE.slice(0,5)).pass, 'short cycle rejected');
exact((CYCLE[0].atUnits + CYCLE[3].atUnits)/2, 17*SCALE, 'midpoint exactly 17');
const engine = createCycleEngine({origin:'local::0'});
const initial = engine.runCycles();
test(initial.pass, 'first complete cycle');
exact(initial.eventCount, 6, 'six receipts');
exact(initial.loop, 0, 'first cycle index');
exact(engine.receipts()[0].prevHash, GENESIS_HASH, 'genesis linkage');
test(engine.verify(initial.head).pass, 'verify independently pinned head');
const priorLiveHash = engine.receipts()[5].hash;
const second = engine.runCycles(1);
exact(second.eventCount, 11, 'no duplicate live at boundary');
exact(engine.receipts()[6].operation, 'write', 'post-boundary resumes with write');
exact(engine.receipts()[6].prevHash, priorLiveHash, 'continuous lineage');
exact(second.loop, 1, 'second cycle index');
test(engine.verify(second.head).pass, 'second complete cycle verifies');
test(!engine.verify('a'.repeat(64)).pass, 'wrong external head rejected');
const copied = engine.receipts().map(e => ({...e}));
copied[3].atUnits++;
test(!verifyLedger(copied).pass, 'event tampering caught');
test(!verifyLedger(engine.receipts().slice(0,10)).pass, 'unclosed cycle rejected');
test(!verifyLedger([]).pass, 'empty ledger rejected');
test(Object.isFrozen(CYCLE) && Object.isFrozen(CYCLE[0]), 'phase definitions frozen');
test(Object.isFrozen(engine.receipts()[0]), 'receipts frozen');
test(asciiCycle().includes('remember'), 'ASCII view generated');
assert.throws(() => createCycleEngine({origin:''}), TypeError); assertions++;
assert.throws(() => createCycleEngine().runCycles(0), RangeError); assertions++;
assert.throws(() => createCycleEngine().runCycles(10001), RangeError); assertions++;
const incomplete = createCycleEngine();
incomplete.step();
assert.throws(() => incomplete.runCycles(), /Complete the pending/); assertions++;
for (let i = 0; i < 5; i++) incomplete.step();
test(incomplete.verify().pass, 'stepping closes the cycle');
console.log(`PASS ${assertions}/${assertions} deterministic checks`);
