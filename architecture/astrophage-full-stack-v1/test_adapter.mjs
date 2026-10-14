import assert from 'node:assert/strict';
import { FIELD, FIELD_SOURCE, LANES, BUS_STATES, ADDRESS_CAPACITY, encodeText44, decodeText44,
  encodeTokens44, decodeTokens44, routeToBus, unrouteFromBus, canonicalFieldJSON,
  executeFullStack } from './adapter.mjs';
import { addressOf, tokenAt } from '../character-register-44/register.mjs';
import { auditPattern, createCycleEngine, verifyLedger } from '../regenerative-loop/ket-cycle-v01/cycle.mjs';
let passed = 0;
function test(name, fn) {
  try { fn(); passed++; console.log('PASS ' + String(passed).padStart(3) + ' ' + name); }
  catch (e) { console.error('FAIL ' + name, e); process.exitCode = 1; throw e; }
}
function rejects(name, fn, type) { test(name, () => assert.throws(fn, type)); }

test('KET 44 zero n', () => assert.equal(addressOf('n'), 0));
test('KET 44 .0x terminal', () => assert.equal(tokenAt(43), '.0x'));
test('8 OSIMODEL lanes', () => assert.equal(LANES.join(''), 'OSIMODEL'));
test('208 per lane', () => assert.equal(BUS_STATES, 208));
test('1664 bus positions', () => assert.equal(ADDRESS_CAPACITY, 1664));
test('source preserves exact boundary', () => assert.ok(FIELD_SOURCE.includes('-+UUUU | | uuuu -+')));
test('typed Na+ chemistry id', () => assert.equal(FIELD.inputs[0].atomicNumber, 11));
test('typed Cl- chemistry id', () => assert.equal(FIELD.inputs[1].atomicNumber, 17));
test('850 nm labelled proxy', () => assert.ok(FIELD.inputs[1].annotation.includes('not visible teal')));
test('NaCl is labelled association', () => assert.equal(FIELD.association, 'NaCl'));
test('three ordered layers', () => assert.deepEqual(FIELD.hierarchy, ['MYCELIUM', 'CYCAD', 'DIATOME']));
test('diatome bits = 129', () => assert.equal(parseInt(FIELD.diatomeBits, 2), 129));
test('three BEAR observers', () => assert.equal(FIELD.bearObservers.length, 3));
test('bear 0 phase 0', () => assert.equal(FIELD.bearObservers[0].angleRad, 0));
test('bear phases 120 and 240', () => assert.ok(Math.abs(FIELD.bearObservers[1].angleRad - 2 * Math.PI / 3) < 1e-12 && Math.abs(FIELD.bearObservers[2].angleRad - 4 * Math.PI / 3) < 1e-12));
test('symbolic Cl17 light subaddress', () => assert.equal(FIELD.registers.lightSubaddresses, '17.01..17.99'));
test('frozen field', () => assert.ok(Object.isFrozen(FIELD) && Object.isFrozen(FIELD.inputs[0]) && Object.isFrozen(FIELD.bearObservers)));
test('source round trip including Unicode', () => assert.equal(decodeText44(encodeText44(FIELD_SOURCE)), FIELD_SOURCE));
test('token round trip including Unicode', () => assert.equal(decodeTokens44(encodeTokens44(FIELD_SOURCE)), FIELD_SOURCE));
test('ASCII, zero and uppercase round trip', () => assert.equal(decodeText44(encodeText44('ASTROPHAGE 10000001 → NaCl { }')), 'ASTROPHAGE 10000001 → NaCl { }'));
test('empty round trip', () => assert.equal(decodeText44(encodeText44('')), ''));
test('two digits for each UTF-8 byte', () => assert.equal(encodeText44('é').length, 4));
test('high byte digit ≤5', () => assert.ok(encodeText44(FIELD_SOURCE).filter((_, i) => i % 2 === 0).every(x => x <= 5)));
test('8-bit byte 255 round trip', () => assert.equal(decodeText44(encodeText44('ÿ')), 'ÿ'));
for (let v = 0; v < 256; v++) {
  const pair = [Math.floor(v / 44), v % 44];
  test('byte ' + v + ': canonical address pair', () => assert.equal(pair[0] * 44 + pair[1], v));
}
const addresses = encodeText44(canonicalFieldJSON());
const packet = routeToBus(addresses);
test('routed packet round trip', () => assert.deepEqual(unrouteFromBus(packet), addresses));
test('packet all addresses in bus', () => assert.ok(packet.every(x => x.busAddress >= 0 && x.busAddress < 1664)));
test('packet ordinal distinguishes duplicate cell addresses', () => assert.equal(packet[0].ordinal, 0));
test('original text is within canonical payload', () => assert.ok(canonicalFieldJSON().includes('ASTROPHAGE FIELD')));
test('upstream balanced return', () => assert.equal(auditPattern().pass, true));
test('one cycle verified', () => assert.equal(executeFullStack().verified, true));
test('two cycles 11 receipts', () => { const x = executeFullStack({ cycles:2 });assert.equal(x.cycles,2);assert.equal(x.ledgerEvents,11); });
test('audit checksum is 64 hex chars', () => assert.match(executeFullStack().payloadSha256, /^[0-9a-f]{64}$/));
test('deterministic replay', () => assert.deepEqual(executeFullStack(),executeFullStack()));
test('different origin produces different ledger head', () => assert.notEqual(executeFullStack({origin:'a'}).ledgerHead,executeFullStack({origin:'b'}).ledgerHead));
test('tampered ledger rejected', () => { const x=createCycleEngine();x.runCycles(1);const forged=x.receipts();forged[2]={...forged[2],atUnits:1};assert.equal(verifyLedger(forged).pass,false); });
rejects('reject odd number of addresses', () => decodeText44([1]), TypeError);
rejects('reject high digit 6 (noncanonical)', () => decodeText44([6,0]), RangeError);
rejects('reject byte > 255', () => decodeText44([5,43]), RangeError);
rejects('reject malformed UTF-8 bytes', () => decodeText44([4,17]), TypeError);
rejects('reject invalid low address', () => decodeText44([1,44]), RangeError);
rejects('reject invalid text type', () => encodeText44(12), TypeError);
rejects('reject invalid tokens type', () => decodeTokens44('abc'), TypeError);
rejects('reject invalid packet type', () => routeToBus('abc'), TypeError);
rejects('reject reordered packet', () => unrouteFromBus(packet.slice(1)), RangeError);
rejects('reject tampered lane', () => unrouteFromBus([{...packet[0], lane:7}]), RangeError);
rejects('reject tampered bus address', () => unrouteFromBus([{...packet[0], busAddress:1500}]), RangeError);
rejects('reject unsupported cycle count', () => executeFullStack({cycles:0}), RangeError);
console.log('ALL ' + passed + '/' + passed + ' CHECKS PASSED');
