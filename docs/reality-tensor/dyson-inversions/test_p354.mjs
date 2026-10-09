import assert from 'node:assert/strict';
import {SHAPES,shape,depthScale,compose,recover,traverse,encodeDigits,decodeDigits} from './p354_hardened.mjs';
let tests=0;
for(const e of Object.keys(SHAPES)){const cap=shape(e).capacity;for(let i=0;i<cap;i++){assert.equal(encodeDigits(e,decodeDigits(e,i)),i);tests++;}}
for(const n of [0,1,64,1024,4096,9999,10000]){assert.equal(depthScale(n).denominator.toString(2).length,6*n+1);tests++;}
for(const n of [-1,10001,1.1,NaN,Infinity]){assert.throws(()=>depthScale(n));tests++;}
for(const e of Object.keys(SHAPES)){const cap=shape(e).capacity;for(let channel=0;channel<48;channel++)for(let spinor=0;spinor<1440;spinor++){const x={envelope:e,structure:(channel*1440+spinor)%cap,channel,spinor,depth:64};assert.deepEqual(recover(compose(x)),x);tests++;}}
for(const e of Object.keys(SHAPES)){const serialize=s=>s.hop+':'+s.step+':'+s.digits.join(',');const full=[...traverse({envelope:e,structure:42,depth:5,channel:47,count:1440})].map(serialize);const split=[];const cuts=[0,1,17,183,359,360,361,720,1080,1439,1440];for(let j=0;j<cuts.length-1;j++)split.push(...[...traverse({envelope:e,structure:42,depth:5,channel:47,start:cuts[j],count:cuts[j+1]-cuts[j]})].map(serialize));assert.deepEqual(split,full);tests++;}
const forged={...compose({envelope:'total',structure:0,channel:1,spinor:0,depth:0}),hop:99};assert.throws(()=>recover(forged));tests++;
assert.throws(()=>traverse({envelope:'total',channel:99,count:0}).next());tests++;
console.log(JSON.stringify({status:'PASS',tests}));
