import assert from 'node:assert/strict';
import {RADICES,BOXY,CIRCLE,CAPACITY,nest,unnest,geometric,normalizeScale,signed,carrier} from './p346_nesting.mjs';
assert.deepEqual(RADICES,[7,5,3,1,1]);assert.equal(CAPACITY,105);
assert.deepEqual(BOXY,[10,6,8,4,2,1,1,0,0]);assert.deepEqual(CIRCLE,[11,9,7,5,3,2,1,1,0,0]);
for(let i=0;i<CAPACITY;i++)assert.equal(nest(unnest(i)),i);
for(let dim=3;dim<=5;dim++){const expected={3:'vxw',4:'vxwy',5:'vxwyz'}[dim];assert.equal(signed(dim,Array(dim).fill(0)).axes.join(''),expected);}
for(let x=0;x<=11;x++)assert.equal(normalizeScale(x).scaled,false);
assert.deepEqual(normalizeScale(22),{structural:11,scale:2,scaled:true});
let n=0;for(let i=0;i<1440;i++){for(let p=0;p<4;p++){for(let d=0;d<6;d++){let a=carrier(i,p,d,i%2?'circle':'boxy',5,[0,0,0,0,0]);assert.equal(a.state.root,0);assert.equal(a.hop*360+a.step,i);assert.equal(nest(a.nest),i%CAPACITY);assert.equal(a.sign,Math.floor(i/360)%2?-1:1);n++;}}}
assert.throws(()=>nest([7,0,0,0,0]));assert.throws(()=>normalizeScale(-1));assert.throws(()=>carrier(1440,0,0,'boxy',3,[0,0,0]));
console.log(JSON.stringify({status:'PASS',nestedCapacity:CAPACITY,nestedRoundTrips:CAPACITY,carrierChecks:n,shapeNames:['boxy','circle'],scaleThreshold:11}));
