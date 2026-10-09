import assert from 'node:assert/strict';
import {SHAPES,spec,encode,decode,channel,unchannel,traversal,recover} from './p352_reconcile.mjs';
let addressChecks=0,traversalChecks=0;
for(const name of Object.keys(SHAPES)){
 const s=spec(name);for(let i=0;i<s.capacity;i++){assert.equal(encode(name,decode(name,i)),i);addressChecks++;}
 for(let c=0;c<48;c++){const d=unchannel(c);assert.equal(channel(d.prime,d.axis,d.sign),c);
  for(let tick=0;tick<1440;tick++){const address=(tick*47+c*19)%s.capacity;const t=traversal(name,address,c,tick);
   assert.deepEqual(recover(t),{shape:name,address,channel:c,index:tick});assert.equal(t.root,0);
   assert.equal(t.sheet,Math.floor(tick/360)%2===0?-1:1);traversalChecks++;}}
}
assert.deepEqual(SHAPES.total,[60,24,12,2,1,1,0,0]);
assert.deepEqual(SHAPES.boxy,[10,6,8,4,2,1,1,0,0]);
assert.deepEqual(SHAPES.circle,[11,9,7,5,4,3,2,1,1,0,0]);
assert.throws(()=>decode('total',34560));assert.throws(()=>traversal('circle',0,48,0));
console.log(JSON.stringify({status:'PASS',capacities:Object.fromEntries(Object.keys(SHAPES).map(n=>[n,spec(n).capacity])),addressChecks,traversalChecks,total:addressChecks+traversalChecks}));
