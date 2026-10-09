import assert from 'node:assert/strict';
import {SHAPES,shape,depthScale,compose,recover,traverse,encodeDigits,decodeDigits} from './p353_lazy_nesting.mjs';
let addresses=0,cases=0;
for(const envelope of Object.keys(SHAPES)){const s=shape(envelope);for(let i=0;i<s.capacity;i++){assert.equal(encodeDigits(envelope,decodeDigits(envelope,i)),i);addresses++;}
for(const depth of [0,1,2,8,64,256,1024]){assert.equal(depthScale(depth).denominator,64n**BigInt(depth));for(let channel=0;channel<48;channel++)for(const spinor of [0,179,180,359,360,719,720,1079,1080,1439]){const structure=(channel*1440+spinor)%s.capacity;const input={envelope,structure,channel,spinor,depth};const state=compose(input);assert.deepEqual(recover(state),input);assert.equal(state.root,0);cases++;}}}
for(const x of traverse({envelope:'circle',count:1440})){assert.equal(x.root,0);cases++;}
assert.throws(()=>depthScale(-1));assert.throws(()=>compose({envelope:'total',structure:0,channel:48,spinor:0,depth:0}));
console.log(JSON.stringify({status:'PASS',addressRoundTrips:addresses,nestedRoundTrips:cases,streaming:true}));
