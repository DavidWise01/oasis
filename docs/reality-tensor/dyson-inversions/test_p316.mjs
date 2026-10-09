import assert from 'node:assert/strict';
import {SPEC,encode11,decode11,translate,cross,indexedCross} from './p316_seeded_cross.mjs';
assert.equal(SPEC.seedCount,1000000);assert.equal(SPEC.base,11);
assert.equal(Number(SPEC.scaleNumerator)/Number(SPEC.scaleDenominator),5032.84375);
assert.deepEqual(SPEC.walk,[[-2,3],[2,-3]]);
assert.deepEqual(cross().closure,[0,0]);
let maxError=0;for(let i=0;i<SPEC.seedCount;i++){
 const v=indexedCross(i);assert.equal(decode11(v.radix),i);
 assert.equal(v.antipodal,true);assert.deepEqual(v.closure,[0,0]);
}
let state=0x316;const rnd=()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return state>>>0;};
for(let i=0;i<100000;i++){
 const origin=[(rnd()%20001)-10000,(rnd()%20001)-10000];
 const c=cross(origin);assert.deepEqual(c.closure,origin);assert.equal(c.antipodal,true);
 const a=translate(translate(origin,SPEC.walk[1]),SPEC.walk[0]);assert.deepEqual(a,origin);
}
for(const bad of [-1,1000000,1.5,NaN])assert.throws(()=>indexedCross(bad));
console.log(JSON.stringify({status:'PASS',seeds:SPEC.seedCount,randomOrigins:100000,scale:Number(SPEC.scaleNumerator)/Number(SPEC.scaleDenominator),root:SPEC.origin,branchVectors:SPEC.walk,apex:SPEC.apex,base:SPEC.base,maxError},null,2));
