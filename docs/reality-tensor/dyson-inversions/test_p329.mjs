import assert from 'node:assert/strict';
import {state,traverse,audit,outerPoint} from './p329_mobius_seam.mjs';
assert.equal(state(182).sign,-1);assert.equal(state(183).sign,1);assert.equal(state(184).sign,1);
assert.equal(state(542).sign,1);assert.equal(state(543).sign,-1);
assert.equal(traverse(0,360).flipped,true);assert.equal(traverse(0,720).flipped,false);
assert.equal(traverse(0,720).crossings,2);
let seed=0x329;function rnd(){seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return seed>>>0;}
for(let i=0;i<100000;i++){
 const a=(rnd()%100000)-50000,s=state(a),one=state(a+360),two=state(a+720);
 assert.equal(one.sign,-s.sign);assert.equal(two.sign,s.sign);
 assert.equal(one.angleDeg,s.angleDeg);assert.equal(two.angleDeg,s.angleDeg);
 assert.equal(traverse(a+720,-720).after.sign,s.sign);
}
console.log(JSON.stringify({status:'PASS',randomAngles:100000,...audit()}));
