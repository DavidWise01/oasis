#!/usr/bin/env node
// ROOT0 P2.8: Complex[0] floor local invariants; no inference for '^10'.
// The signed coordinate pairs are tested as ordered edges.
import assert from "node:assert/strict";
const carrier=[10,10], earlierFloor=[9,1,9];
const slots=a=>a.reduce((x,y)=>x*y,1);
assert.equal(slots(carrier),100);
assert.equal(slots(earlierFloor),81);
assert.equal(slots(carrier)-slots(earlierFloor),19);
const signed=[-1,0,1];assert.equal(signed.reduce((a,b)=>a+b,0),0);
const minus={start:[0,0],end:[0,-1]};
const plus={start:[0,1],end:[0,0]};
const delta=b=>b.start.map((v,j)=>b.end[j]-v);
assert.deepEqual(delta(minus),[0,-1]);
assert.deepEqual(delta(plus),[0,-1]);
assert.deepEqual(plus.end,minus.start);
assert.deepEqual([delta(plus)[0]+delta(minus)[0],delta(plus)[1]+delta(minus)[1]],[0,-2]);
const embeddings=[];
for(const ox of [0,1])for(const oy of [0,1]){
  const inner=new Set();
  for(let x=ox;x<ox+9;x++)for(let y=oy;y<oy+9;y++)inner.add(x+','+y);
  assert.equal(inner.size,81);
  const anchor=[ox+4,oy+4];
  assert(inner.has(anchor[0]+','+(anchor[1]-1)));
  assert(inner.has(anchor[0]+','+(anchor[1]+1)));
  embeddings.push({offset:[ox,oy],reference:anchor,unused:100-inner.size});
}
assert.equal(embeddings.length,4);
for(let j=0;j<10;j++)assert.notEqual(2*j,9);
const result={gate:"ROOT0-P2.8-Complex-zero-floor",pass:true,notation:"{{10x10}}^10",
  power10_semantics:"UNSPECIFIED",zero_floor:true,plane_slots:100,
  earlier_9x1x9_slots:81,optional_embedding_remainder:19,
  optional_embeddings:embeddings,signed_label_sum:0,
  positive_edge:plus,negative_edge:minus,
  directed_path_displacement:[0,-2],
  pinned_zero_placement:"UNSPECIFIED",frozen_v92_modified:false,
  physical_simulation_proven:false};
console.log(JSON.stringify(result,null,2));
