import assert from 'node:assert/strict';
import * as D from './p37_dyson_scale.mjs';
import {Cipher208,FORWARD,BACKWARD} from '../cipher208/cipher208.mjs';
const close=(x,y,t=1e-12)=>Math.abs(x-y)<t*Math.max(1,Math.abs(x),Math.abs(y));
assert.equal(D.LITERAL,'{{-211mv}}x10^-35');
assert.equal(D.CONSTANTS.baseMillivolts,-211);
assert.equal(D.CONSTANTS.scaleExponent,-35);
assert.equal(D.scaledPotentialV(),-2.11e-36);
const rad=2.11e-36*1e-15/D.CONSTANTS.hbarEVs;
assert(close(D.totalPortPhase({chargeSign:1}),rad));
assert(close(D.totalPortPhase({chargeSign:-1}),-rad));
assert(Math.abs(D.depthRadiusM({depth:1})/D.CONSTANTS.planckM-1)<1e-12);
let maxNorm=0,maxInverse=0;
for(let j=0;j<10000;j++){
  const cfg={shells:1+j%10,capture:j%17===0?1:(j%13===0?0:((j*37)%997)/997),chargeSign:j%2?1:-1};
  const v=Array.from({length:cfg.shells+1},(_,k)=>D.amplitude(Math.sin(j+k),Math.cos(j-k)));
  const next=D.forwardAll(v,cfg),back=D.backwardAll(next,cfg);
  maxNorm=Math.max(maxNorm,Math.abs(D.norm(v)-D.norm(next)));
  for(let k=0;k<v.length;k++)for(let i=0;i<2;i++)maxInverse=Math.max(maxInverse,Math.abs(v[k][i]-back[k][i]));
}
assert(maxNorm<1e-12 && maxInverse<1e-12);
for(let n=1;n<=10;n++)for(const capture of [0,.1,.21,.5,1]){
 const cfg={shells:n,capture};const s=D.forwardAll(D.inputState(cfg),cfg),a=D.analyticPowers(cfg);
 assert(Math.abs(D.norm(s)-1)<1e-12&&Math.abs(a.sum-1)<1e-12);
}
assert.equal(FORWARD.length,208);assert.equal(BACKWARD.length,208);
const c=new Cipher208();for(let j=0;j<208;j++)c.forward();
c.beginMirroredReverse();for(let j=0;j<208;j++)c.backward();
assert(c.recovered());
console.log(JSON.stringify({status:'PASS',voltageV:D.scaledPotentialV(),signedPhasePlusRad:rad,randomTrials:10000,maxNorm,maxInverse,cipherRecovered:true}));
