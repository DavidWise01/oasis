import assert from 'node:assert/strict';
import {PATRICIA,spinor,unspinor,stateAt,reverseBody,bodies} from './p336_patricia_360.mjs';
const GREG={hops:4,stepsPerHop:366,total:1464};
assert.equal(PATRICIA.total,1440);assert.equal(GREG.total,1464);
for(let i=0;i<1440;i++){const s=spinor(i);assert.equal(unspinor(s.hop,s.step),i);assert.equal(s.orientation,Math.floor(i/360)%2?1:-1);assert.equal(s.root,0);}
assert.deepEqual([0,360,720,1080].map(i=>spinor(i).orientation),[-1,1,-1,1]);
assert.throws(()=>spinor(1440));
let maxReversalError=0,checks=0;
for(const b of bodies())for(let j=0;j<10000;j++){const t=(j-5000)*50000,p=stateAt(b,0),z=reverseBody(b,t),e=Math.hypot(z[0]-p[0],z[1]-p[1]);maxReversalError=Math.max(maxReversalError,e);assert.ok(e<1e-7);checks++;}
console.log(JSON.stringify({status:'PASS',patriciaSteps:1440,gregSteps:1464,bodyChecks:checks,maxReversalError}));
