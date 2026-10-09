import assert from 'node:assert/strict';
import {TOTAL_SEQUENCE,ADDRESS_CAPACITY,digitsOf,addressOf,frame,recover} from './p351_envelope.mjs';
assert.deepEqual(TOTAL_SEQUENCE,[60,24,12,2,1,1,0,0]);assert.equal(ADDRESS_CAPACITY,34560);
for(let i=0;i<ADDRESS_CAPACITY;i++){assert.equal(addressOf(digitsOf(i)),i);}
let count=0;
for(let ch=0;ch<48;ch++)for(let k=0;k<1440;k++){const f=frame(4,(ch*1440+k)%ADDRESS_CAPACITY,ch,k);assert.deepEqual(recover(f),{structureIndex:f.structureIndex,channelIndex:ch,spinorIndex:k});assert.equal(f.root,0);count++;}
for(let n of [0,1,8,64,1024]){const f=frame(n,34559,47,1439);assert.equal(f.carrier.scale.denominator,64n**BigInt(n));}
assert.throws(()=>digitsOf(34560));assert.throws(()=>frame(0,0,48,0));assert.throws(()=>frame(0,0,0,1440));
console.log(JSON.stringify({status:'PASS',envelopeRoundTrips:ADDRESS_CAPACITY,carrierMotionChecks:count,totalSequence:TOTAL_SEQUENCE}));
