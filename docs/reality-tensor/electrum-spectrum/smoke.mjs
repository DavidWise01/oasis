import assert from 'node:assert/strict';
import * as M from './p35_spectrum.mjs';
import * as C from '../cipher208/cipher208.mjs';
const close=(a,b,t=1e-10)=>Math.abs(a-b)<=t*Math.max(1,Math.abs(a),Math.abs(b));
assert.equal(M.RAW.length,44);
assert.equal(M.CIPHER_SPECTRUM.dominant.mode,24);
assert(close(M.CIPHER_SPECTRUM.dominant.magnitude,0.3830068447079039));
for(const row of M.RAW)for(const el of ['Au','Ag']){
 const x=M.measuredElement(el,row.nm);assert(close(x.n,row[el].n)&&close(x.k,row[el].k));
}
let minA=Infinity, maxEnergy=0;
for(let j=0;j<1200;j++){
 const nm=400+500*(j+.5)/1200;
 const x=M.spectrumAt(nm,{thicknessNm:j%55,method:j%2?'epsilon':'nk'});
 minA=Math.min(minA,x.A);
 maxEnergy=Math.max(maxEnergy,Math.abs(x.T+x.R+x.A-1));
 assert(x.A>=-1e-10);
}
assert(maxEnergy<1e-12);
const e=M.spectrumAt(600,{method:'epsilon'}),n=M.spectrumAt(600,{method:'nk'});
assert(close(e.T,0.13805358429274417));
assert(close(n.T,0.14103983882421633));
assert(!close(e.T,n.T,1e-4));
assert.equal(M.CIPHER_SPECTRUM.DC<1e-12,true);
const nullCase=M.spectrumAt(600,{cipherRadPerVolt:0});
const conditionalCase=M.spectrumAt(600,{cipherRadPerVolt:2,pitchNm:500});
assert(close(conditionalCase.T,nullCase.T));
assert(close(conditionalCase.R,nullCase.R));
assert(!close(conditionalCase.interferometer,nullCase.interferometer));
assert(close(M.spectrumAt(600,{cipherRadPerVolt:2,voltageV:1,referenceV:.5}).extraPhaseRad,
 M.spectrumAt(600,{cipherRadPerVolt:2,voltageV:1001,referenceV:1000.5}).extraPhaseRad));
const c=new C.Cipher208();for(let j=0;j<208;j++)c.forward();
c.beginMirroredReverse();for(let j=0;j<208;j++)c.backward();
assert(c.recovered());
console.log(JSON.stringify({status:'PASS',measuredPureMetalRows:M.RAW.length,
 filmTrials:1200,maxEnergyError:maxEnergy,minAbsorption:minA,
 dominantCipherMode:M.CIPHER_SPECTRUM.dominant.mode,unidentifiedCipherCoupling:true}));
