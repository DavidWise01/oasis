import assert from 'node:assert/strict';
import {CIRCLE,RADICES,CAPACITY,TRAVERSAL,encode,decode,walk,carrier} from './p347_circle_nesting.mjs';
assert.deepEqual(CIRCLE,[11,9,7,5,4,3,2,1,1,0,0]);
assert.equal(CAPACITY,83160);assert.equal(TRAVERSAL,183);
for(let i=0;i<CAPACITY;i++)assert.equal(encode(decode(i).slice(0,RADICES.length)),i);
for(let i=0;i<TRAVERSAL*4;i++){const x=walk(i);assert.equal(x.turn*183+x.position,i);assert.equal(x.root,0);for(let p=0;p<4;p++)assert.equal(carrier(i,p).address,i%CAPACITY);}
assert.deepEqual([0,183,366,549].map(i=>walk(i).sign),[-1,1,-1,1]);
assert.throws(()=>decode(CAPACITY));assert.throws(()=>encode([11,0,0,0,0,0,0,0,0]));
console.log(JSON.stringify({status:'PASS',capacity:CAPACITY,roundTrips:CAPACITY,traversal:TRAVERSAL,carrierChecks:TRAVERSAL*4*4,zeroSentinels:2}));
