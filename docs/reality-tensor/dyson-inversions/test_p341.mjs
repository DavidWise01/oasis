import assert from 'node:assert/strict';
import {C,PRIMES,TOTAL,TIERS,spectral,fromWavelength,address,inverseAddress,phaseAt} from './p341_continuous_spectrum.mjs';
assert.deepEqual(PRIMES.map(x=>x.name),['jane','patricia','toph','icarium']);
assert.equal(TIERS.at(-1),'{hz...}');
const frequencies=[1,60,440,1e6,1e9,1e12,4e14,7.5e14,1e20,1e28];
for(const f of frequencies){const w=spectral({hz:f,amplitude:0.25,phase:0.3});const recovered=fromWavelength({wavelengthM:w.wavelengthM,amplitude:w.amplitude,phase:w.phaseRad});assert.ok(Math.abs(recovered.hz-f)/f<1e-12);assert.equal(w.lambdaTimesAmplitudeM,w.wavelengthM*0.25);assert.ok(Math.abs(phaseAt(w,0)-0.3)<1e-12);}
let count=0;const wave=spectral({hz:C/550e-9});
for(let i=0;i<TOTAL;i++)for(let p=0;p<4;p++){const a=address(i,p,wave);assert.equal(inverseAddress(a.hop,a.step),i);assert.equal(a.prime.name,PRIMES[p].name);assert.equal(a.root,0);assert.equal(a.sheet,Math.floor(i/360)%2===0?-1:1);count++;}
for(const bad of [0,-1,Infinity,NaN])assert.throws(()=>spectral({hz:bad}));
assert.throws(()=>spectral({hz:1,amplitude:-0.1}));assert.throws(()=>address(TOTAL,0,wave));
console.log(JSON.stringify({status:'PASS',carrierAddresses:count,spectrumCases:frequencies.length,slots:TOTAL,lambda550nmHz:wave.hz}));
