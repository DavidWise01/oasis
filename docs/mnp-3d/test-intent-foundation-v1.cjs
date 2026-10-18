/* deterministic grammar tests; run: node test-intent-foundation-v1.cjs */
const assert=require('node:assert/strict');
const G=require('./intent-foundation-v1.js');
let passed=0;function test(name,fn){fn();passed++;console.log('PASS',name)}
test('52 case-sensitive foundation letters',()=>{for(const l of 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')assert.equal(G.start(l).locked,l)});
test('reject nonletters',()=>assert.throws(()=>G.start('1')));
test('foundation sets intent',()=>assert.equal(G.start('T','transport').intent,'transport'));
test('lock candidate',()=>assert.equal(G.decide(G.propose(G.start('T'),'H'),'LOCK').locked,'TH'));
test('discard candidate',()=>assert.equal(G.decide(G.propose(G.start('T'),'H'),'DISCARD').locked,'T'));
test('many sequential locks',()=>{let s=G.start('T');for(const c of 'HPPS')s=G.decide(G.propose(s,c),'LOCK');assert.equal(G.delimit(G.complete(s)).word,'THPPS')});
test('original tone retained',()=>{let s=G.start('H','harness');s=G.decide(G.propose(s,'T'),'LOCK');assert.equal(s.intent,'harness')});
test('only one provisional candidate',()=>assert.throws(()=>G.propose(G.propose(G.start('A'),'B'),'C')));
test('no completion with unresolved candidate',()=>assert.throws(()=>G.complete(G.propose(G.start('A'),'B'))));
test('check precedes X',()=>assert.throws(()=>G.delimit(G.start('A'))));
test('completed box immutable to proposals',()=>assert.throws(()=>G.propose(G.complete(G.start('A')),'B')));
test('case-sensitive sequence',()=>{let s=G.start('a');s=G.decide(G.propose(s,'Z'),'LOCK');assert.equal(s.locked,'aZ')});
test('discard logged but not appended',()=>{const s=G.decide(G.propose(G.start('A'),'x'),'DISCARD');assert.deepEqual(s.history,[{letter:'x',action:'DISCARD'}])});
test('closed output includes box/check/delimiter',()=>{const out=G.delimit(G.complete(G.start('T')));assert.equal(out.box,'||||');assert.equal(out.check,'✓');assert.equal(out.delimiter,'X')});
console.log(passed+'/14 passed');
