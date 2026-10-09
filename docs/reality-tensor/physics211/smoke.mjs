import assert from 'node:assert/strict';
import * as M from './p33_physical_boundary.mjs';
const z=M.CONSTANTS,close=(a,b,tol=1e-12)=>Math.abs(a-b)<tol*Math.max(1,Math.abs(a),Math.abs(b));
const a=M.uniformPotentialVacuum(),b=M.electroOptic();
assert.equal(a.deltaPhaseRad,0);
assert(close(b.deltaPhaseRad,0.3529152089707245));
assert(close(b.electricFieldVPerM,-21100));
assert.equal(b.frequencyShiftHz,0);
assert(close(b.normalizedIntensityContrast,-0.13825392571530054));
assert.equal(M.electroOptic({...z,electroOpticCoeffMPerV:0}).deltaPhaseRad,0);
assert(close(M.electroOptic({...z,gapM:z.gapM*2}).deltaPhaseRad,b.deltaPhaseRad/2));
assert(close(M.electroOptic({...z,interactionLengthM:z.interactionLengthM*2}).deltaPhaseRad,b.deltaPhaseRad*2));
assert(close(M.electroOptic({...z,voltageV:0.211}).deltaPhaseRad,-b.deltaPhaseRad));
let seed=20261009,max=0;
const random=()=>((seed=Math.imul(seed,1664525)+1013904223>>>0)/4294967296);
for(let i=0;i<2000;i++){
 const phiX=1e4*(random()-.5),aT=1e4*(random()-.5),u=1e6*(random()-.5);
 const base={phi0:0,phiX,phiT:0,a0:0,aT,aX:0};
 const out=M.gaugeTransform(base,{u,v:300,w:.5});
 max=Math.max(max,Math.abs(M.electricField(base)-M.electricField(out)));
}
assert(max<1e-8);
assert(Math.abs(M.zoomLength(1)/z.planckLengthM-1)<1e-12);
assert.throws(()=>M.zoomLength(1.1));
console.log(JSON.stringify({gate:'ROOT0-P3.3-GitHub-CI-smoke',status:'PASS',randomGaugeTrials:2000,maxGaugeDifference:max,phase:b.deltaPhaseRad,physicalPredictionDerivedFromROOT0:false}));
