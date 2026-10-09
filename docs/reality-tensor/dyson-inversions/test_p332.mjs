import assert from 'node:assert/strict';
import {PATRICIA,flip,state,forward,backward,roundTrip} from './p332_patricia_photon.mjs';
assert.equal(PATRICIA.literal,'{{ -+- : +-+ }}');assert.equal(PATRICIA.calendarBound,false);
assert.equal(flip(flip('-+-')),'-+-');assert.deepEqual(state(0),{tick:0,root:0,left:'-+-',right:'+-+'});
assert.deepEqual(state(1),{tick:1,root:0,left:'+-+',right:'-+-'});
let steps=100000;let s=state();for(let i=0;i<steps;i++){s=forward(s);assert.equal(s.left,flip(s.right));assert.equal(s.root,0);}
for(let i=0;i<steps;i++)s=backward(s);assert.deepEqual(s,state(0));
for(const i of [0,1,2,255,366,1464])assert.deepEqual(roundTrip(i),state(0));
assert.throws(()=>backward(state(0)));assert.throws(()=>forward({...state(0),root:1}));
console.log(JSON.stringify({status:'PASS',steps,root:0,primitive:PATRICIA.literal,calendarBound:false}));
