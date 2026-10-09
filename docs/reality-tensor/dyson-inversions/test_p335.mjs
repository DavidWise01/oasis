import assert from 'node:assert/strict';
import {BODY,PARAMETERS,angularVelocity,position,patricia} from './p335_galactic_motion.mjs';
const [sun,inner,outer,spiral]=BODY;
assert.ok(angularVelocity(inner)>angularVelocity(sun));assert.ok(angularVelocity(sun)>angularVelocity(outer));
assert.notEqual(angularVelocity(spiral),angularVelocity(outer));
let count=0,maxRadiusError=0;
for(const body of BODY)for(let i=0;i<10000;i++){const t=i*12345.6789,p=position(body,t),r=Math.hypot(p[0],p[1]);maxRadiusError=Math.max(maxRadiusError,Math.abs(r-body.radius));assert.ok(Math.abs(r-body.radius)<1e-8);count++;}
for(let i=0;i<1464;i++){const s=patricia(i);assert.equal(s.hop*366+s.subslot,i);assert.deepEqual(s.root,[0,0,0]);count++;}
assert.throws(()=>patricia(1464));
console.log(JSON.stringify({status:'PASS',checks:count,maxRadiusError,angularVelocities:BODY.map(b=>[b.id,angularVelocity(b)]),solarPeriodYears:PARAMETERS.solarPeriodYears,patternPeriodYears:PARAMETERS.patternPeriodYears}));
