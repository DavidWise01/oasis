import assert from 'node:assert/strict';
import {PRIM,PRIMES,AXES,scale,encode,decode,cell,inverseMotion} from './p350_prim_lattice.mjs';
assert.equal(PRIM,'{{1/8 x 1/8}}^{{n}}');assert.equal(PRIMES.length,4);assert.equal(AXES.length,6);
let checks=0;
for(const n of [0,1,2,3,4,8,16,32,64,128,256,512,1024]){
 let exact=scale(n);assert.equal(exact.denominator,64n**BigInt(n));
 for(let p=0;p<4;p++)for(let a=0;a<6;a++)for(const sign of [-1,1]){
  const addr=encode(p,a,sign);assert.deepEqual(decode(addr),{prime:p,axis:a,sign});
  for(const hop of [0,1,2,3])for(const step of [0,183,359]){
   const c=cell(n,addr,hop,step);assert.equal(c.root,0);assert.equal(c.scale.denominator,exact.denominator);assert.equal(inverseMotion(c.hop,c.step),hop*360+step);assert.equal(c.mobiusSheet,hop%2?-1:1);checks++;
  }
}
}
assert.throws(()=>encode(4,0));assert.throws(()=>cell(0,48));assert.throws(()=>scale(-1));assert.throws(()=>cell(0,0,4,0));
console.log(JSON.stringify({status:'PASS',checks,primeCount:4,axes:6,directions:2,addressCount:48,maxDepth:1024,rotationSlots:1440}));