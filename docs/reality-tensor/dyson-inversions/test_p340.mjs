import assert from 'node:assert/strict';
import {C,PRIME,TIERS,TOTAL,address,spectralTail,sample,invertFrequency} from './p340_spectral_tail.mjs';
let addresses=0;for(let n=0;n<TOTAL;n++)for(let p=0;p<4;p++)for(let t=0;t<4;t++){
 const a=address(n,p,t);assert.equal(a.hop*360+a.step,n);assert.equal(a.root,0);assert.equal(a.prime,PRIME[p][0]);assert.equal(a.tier,TIERS[t]);addresses++;
}
const waves=[400e-9,450e-9,530e-9,650e-9,700e-9,1e-3].map(wavelengthM=>spectralTail({wavelengthM,amplitude:0.5}));
for(const w of waves){assert.ok(Math.abs(invertFrequency(w.hz)-w.wavelengthM)/w.wavelengthM<1e-12);assert.equal(w.wavelengthTimesAmplitude,w.wavelengthM*0.5);assert.ok(Math.abs(sample(w,0))<1e-12);}
assert.equal(spectralTail({wavelengthM:500e-9,amplitude:0}).hz,C/500e-9);
assert.throws(()=>spectralTail({wavelengthM:0,amplitude:1}));assert.throws(()=>spectralTail({wavelengthM:500e-9,amplitude:-1}));assert.throws(()=>address(1440,0,0));
console.log(JSON.stringify({status:'PASS',addresses,waveCases:waves.length,totalSymbolicSlots:TOTAL,primes:PRIME.map(p=>p[0]),tierCount:TIERS.length,frequencyExampleHz:waves[0].hz}));
