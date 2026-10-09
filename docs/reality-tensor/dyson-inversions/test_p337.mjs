import assert from 'node:assert/strict';
import {scale,at,reverseCoordinate,recoverIndex,SPEC} from './p337_sync.mjs';
import {bodies} from './p336_patricia_360.mjs';
let count=0,maxRadius=0,maxReverse=0;
for(const factor of [0,1,100,10000,100000]){const cfg=scale(factor);for(let i=0;i<1440;i++){const s=at(i,cfg);assert.equal(recoverIndex(s.spinor.hop,s.spinor.step),i);assert.deepEqual(s.root,[0,0,0]);assert.equal(s.elapsedYears,i*factor);
for(const b of bodies()){const p=s.bodies.find(x=>x.id===b.id).xyz;const radial=Math.abs(Math.hypot(p[0],p[1])-b.radius);maxRadius=Math.max(maxRadius,radial);const restored=reverseCoordinate(b,s.elapsedYears,0);const p0=at(0,scale()).bodies.find(x=>x.id===b.id).xyz;const err=Math.hypot(restored[0]-p0[0],restored[1]-p0[1]);maxReverse=Math.max(maxReverse,err);assert.ok(radial<1e-7&&err<1e-7);count++;}}}
for(const invalid of [-1,Infinity,NaN])assert.throws(()=>scale(invalid));assert.throws(()=>at(1440));
console.log(JSON.stringify({status:'PASS',bodyChecks:count,spinorChecks:7200,maxRadius,maxReverse,geometry:SPEC}));
