import assert from 'node:assert/strict';
import * as P from './p36_planck_bubble.mjs';
const v={depth:1,wavelengthNm:600,filmTransmission:0.13805358429274417};
const p=P.planckAudit(v);
assert.equal(P.GLYPH,'{-e{gray{+e{white}}');
assert.equal(P.COMPLETED_FOR_DISPLAY,'{-e{gray{+e{white}}}}');
assert.equal(P.REGIONS.length,4);
assert(Math.abs(p.radiusM/P.CONSTANTS.planckM-1)<1e-13);
assert(p.energyAtPlanckEV>7e28&&p.energyAtPlanckEV<8e28);
assert(p.energyRatio>3e29);
assert(p.log10Twhite < -110 && p.log10Twhite > -120);
assert(p.nearPlanck&&p.regime==='INVALID_PHYSICAL_EXTRAPOLATION');
assert.equal(p.voltsToPhotonAtPlanckDerived,false);
assert(Math.abs(P.chargedPhaseRad(1)+P.chargedPhaseRad(-1))<1e-15);
assert.throws(()=>P.apertureLog10T({depth:1.01}));
assert.throws(()=>P.apertureLog10T({entranceRadiusM:1e-36}));
assert.equal(P.apertureLog10T({depth:0}),null);
let n=0,maxNorm=0,maxRoundTrip=0;
for(let k=0;k<10000;k++){
 let f=(k+1)/10001,lambda=400+600*f;
 const cfg={depth:0.4+0.6*f,wavelengthNm:lambda,filmTransmission:(k%97)/96};
 const state=Array.from({length:3},(_,i)=>[Math.sin(k+i),Math.cos(k*1.1+i)]);
 const end=P.propagate(state,cfg),back=P.unpropagate(end,cfg);
 maxNorm=Math.max(maxNorm,Math.abs(P.normSquared(state)-P.normSquared(end)));
 maxRoundTrip=Math.max(maxRoundTrip,...back.flatMap((a,i)=>a.map((z,j)=>Math.abs(z-state[i][j]))));
 n++;
}
assert(maxNorm<1e-11);assert(maxRoundTrip<1e-11);
// Decisive physical countermodel: arbitrary 'portal' transmission would be a new axiom
// and differs drastically from the ideal-aperture extrapolation at Planck radius.
const arbitraryPortalTransmission=0.1;
assert(arbitraryPortalTransmission/p.Twhite>1e100);
console.log(JSON.stringify({gate:'ROOT0-P3.6-NESTED-PLANCK-BUBBLE',status:'PASS_SYMBOLIC_WITH_PHYSICS_NO_GO',
 tests:n,maxNorm,maxRoundTrip,planckRadiusM:p.radiusM,
 planckPhotonEnergyEV:p.energyAtPlanckEV,energyRatio:p.energyRatio,
 log10ProjectedTransmission:p.log10Twhite,
 apertureLawExtrapolationInvalidBelowNm:true,
 noUniquePlanckTransmission:true,externalPhysicsProof:false},null,2));
