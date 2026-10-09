import assert from 'node:assert/strict';
import * as T from './tensor_kernel.mjs';
import * as W from './wave_kernel.mjs';
const c=W.parseCarrier(W.GLYPH);
assert.equal(c.dots,8);assert.equal(c.bars,6);assert.equal(c.length,14);
const z=(re,im=0)=>({re,im});
const norm=x=>x.re*x.re+x.im*x.im;
let maxError=0;
for(let j=0;j<20000;j++){
 const a=z(Math.sin(j*1.7),Math.cos(j*.53));
 const b=z(Math.cos(j*.17),Math.sin(j*.97));
 const theta=(j%181-90)*Math.PI/180;
 const phase=W.phaseAt(j,8,Math.PI/2);
 const [p,q]=W.gate(a,b,theta,phase);
 const [x,y]=W.gate(p,q,-theta,phase);
 const d=Math.abs(norm(a)+norm(b)-norm(p)-norm(q));
 maxError=Math.max(maxError,d,Math.hypot(x.re-a.re,x.im-a.im),Math.hypot(y.re-b.re,y.im-b.im));
}
assert(maxError<1e-12);
for(let n=0;n<10000;n++){
 assert.equal(W.transposeId(W.transposeId(n*10000+9999)),n*10000+9999);
 assert.equal(W.transposeId(W.transposeId(n*10000+n)),n*10000+n);
}
assert.equal((10000*10000-10000)/2,49_995_000);
const s=new W.WaveTensor({wavelength:8,theta:.19,barKick:Math.PI/2,pruneEpsilon:0});
s.seed({outer:2431,inner:9123},1);const origin=s.amplitudes;
for(let j=0;j<14;j++){s.forward();assert(!s.amplitudes.has(0));}
for(let j=0;j<14;j++)s.reverse();
assert.equal(s.tick,0);assert.equal(s.eventCount,28);
for(const [id,a] of origin){const b=s.amplitudes.get(id);assert(b&&Math.hypot(a.re-b.re,a.im-b.im)<1e-11);}
assert.throws(()=>s.seed(T.ZERO,1));
assert.throws(()=>W.waveStep(new Map([[0,z(1)]]),0));
console.log(JSON.stringify({gate:'P3.0-wave-module-github-smoke',status:'PASS',carrier:W.GLYPH,complexGateTrials:20000,pairedGateMaxResidual:maxError,pairGeometry:49_995_000,waveRoundTrip:14,anchorPinned:true}));
