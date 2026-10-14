import assert from 'node:assert/strict';
import { TOKENS, SCALE, addressOf, tokenAt, encode, decode, tokenize, untokenize, audit } from './register.mjs';

let passed = 0;
function check(name, test) {
  try { test(); passed++; console.log(`PASS ${String(passed).padStart(3)} ${name}`); }
  catch (err) { console.error(`FAIL ${name}: ${err.message}`); throw err; }
}
check('44 total addresses', () => assert.equal(SCALE, 44));
check('44 unique tokens', () => assert.equal(new Set(TOKENS).size, 44));
check('center n is address 0', () => assert.equal(addressOf('n'), 0));
check('address 0 holds n', () => assert.equal(tokenAt(0), 'n'));
check('a-m occupy 1-13', () => assert.deepEqual(TOKENS.slice(1,14), [...'abcdefghijklm']));
check('o-x occupy 14-23', () => assert.deepEqual(TOKENS.slice(14,24), [...'opqrstuvwx']));
check('y,z,1-8 occupy 24-33', () => assert.deepEqual(TOKENS.slice(24,34), ['y','z',...'12345678']));
check('9 and symbols occupy 34-43', () => assert.deepEqual(TOKENS.slice(34), ['9','>','|',':','"','^','(','-','+','.0x']));
check('letters a-z each present once', () => assert.deepEqual([...TOKENS].filter(t => /^[a-z]$/.test(t)).sort(), [...'abcdefghijklmnopqrstuvwxyz']));
check('digits 1-9 each present once', () => assert.deepEqual([...TOKENS].filter(t => /^[1-9]$/.test(t)).sort(), [...'123456789']));
check('nine special tokens', () => assert.equal(TOKENS.filter(t => !/^[a-z1-9]$/.test(t)).length, 9));
for(let address = 0; address < 44; address++) {
  check(`address ${address} → token → address`, () => assert.equal(addressOf(tokenAt(address)), address));
  check(`token ${JSON.stringify(tokenAt(address))} → address → token`, () => assert.equal(tokenAt(addressOf(TOKENS[address])), TOKENS[address]));
}
check('full 44-token round trip', () => assert.deepEqual(decode(encode(TOKENS)), TOKENS));
check('sample string round trip', () => assert.equal(untokenize(tokenize('honey.0x+|n')), 'honey.0x+|n'));
check('.0x is ONE token', () => assert.deepEqual(tokenize('.0x'), ['.0x']));
check('n is a symbol distinct from numeric address', () => assert.deepEqual(encode(['n','a','m','o','z','9','.0x']), [0,1,13,14,25,34,43]));
check('standalone 0 is rejected', () => assert.throws(() => tokenize('0'), RangeError));
check('isolated dot is rejected', () => assert.throws(() => tokenize('.'), RangeError));
check('invalid token is rejected', () => assert.throws(() => addressOf('@'), RangeError));
check('negative address is rejected', () => assert.throws(() => tokenAt(-1), RangeError));
check('44 out-of-range address is rejected', () => assert.throws(() => tokenAt(44), RangeError));
check('fractional address is rejected', () => assert.throws(() => tokenAt(.5), RangeError));
check('wrong encode type is rejected', () => assert.throws(() => encode('abc'), TypeError));
check('wrong decode type is rejected', () => assert.throws(() => decode('123'), TypeError));
check('wrong tokenize type is rejected', () => assert.throws(() => tokenize(123), TypeError));
check('empty sequence is valid', () => assert.deepEqual(encode([]), []));
check('audit agrees', () => assert.equal(audit().indexed && audit().unique && audit().anchor === 'n', true));
console.log(`\nALL ${passed}/${passed} CHECKS PASSED`);
