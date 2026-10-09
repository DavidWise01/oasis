import assert from 'node:assert/strict';
import * as P from './p36_planck_bubble.mjs';
import * as C from './upstream/cipher208.mjs';
assert.equal(P.GLYPH,'{-e{gray{+e{white}}');
assert.equal(P.COMPLETED_FOR_DISPLAY,P.GLYPH+'}}');
assert.equal(C.FORWARD.length,208);assert.equal(C.BACKWARD.length,208);
const p=P.planckAudit({depth:1});
assert(p.energyAtPlanckEV>7e28&&p.energyRatio>3e29);
assert(p.log10Twhite<-110);
assert.equal(p.regime,'INVALID_PHYSICAL_EXTRAPOLATION');
let maxError=0;
for(let j=0;j<5000;j++){
 const params={depth:.5+.5*((j+1)/5001),filmTransmission:(j%101)/100,
  wavelengthNm:400+j%501};
 const input=Array.from({length:3},(_,k)=>[Math.sin(j+k),Math.cos(j*.77+k)]);
 const forward=P.propagate(input,params),backward=P.unpropagate(forward,params);
 maxError=Math.max(maxError,Math.abs(P.normSquared(forward)-P.normSquared(input)));
 for(let k=0;k<3;k++)for(let v=0;v<2;v++)maxError=Math.max(maxError,Math.abs(backward[k][v]-input[k][v]));
}
assert(maxError<1e-11);
let c=new C.Cipher208();for(let j=0;j<208;j++)c.forward();
c.beginMirroredReverse();for(let j=0;j<208;j++)c.backward();
assert(c.recovered());
console.log(JSON.stringify({status:'PASS',threeModeTrials:5000,maxResidual:maxError,PlanckLengthM:p.radiusM,formalLog10T:p.log10Twhite,cipherRecovered:true,nonPhysicalExtrapolationFlagged:true}));
