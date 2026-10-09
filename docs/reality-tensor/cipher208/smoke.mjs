import assert from 'node:assert/strict';
import * as C from './cipher208.mjs';
import * as T from '../wave/tensor_kernel.mjs';
assert.equal(C.MOTIF,'..||..|....|||');
assert.equal(C.FORWARD.length,208);assert.equal(C.BACKWARD.length,208);
assert.equal(C.SEAMS.length,16);
assert.deepEqual(C.COUNT,{dot:104,bar:104});
assert.equal(C.reverseInvert(C.BACKWARD),C.FORWARD);
for(let i=0;i<10000;i++)assert.equal(C.reflectZ(C.reflectZ(i)),i);
assert.equal(C.mirrorUpsideDown(0),0);
const origin=T.encodeTensor({outer:2301,inner:9237});
assert.equal(C.mirrorUpsideDown(C.mirrorUpsideDown(origin)),origin);
let maxError=0;
for(let k=0;k<150;k++){
 const seed=[{re:Math.sin(k+1),im:Math.cos(k/3)},{re:Math.cos(k/7),im:Math.sin(k/11)}];
 const s=new C.Cipher208({amplitudes:seed,
   params:{wavelength:1+(k%32),theta:(k%17-8)/11,barKick:(k%23)/7}});
 const before=s.initialNorm;
 for(let i=0;i<208;i++)s.forward();
 s.beginMirroredReverse();
 for(let i=207;i>=0;i--){const e=s.backward();assert.equal(e.sourceTick,i);}
 assert(s.recovered(1e-10));
 assert.equal(s.totalEvents,417);
 maxError=Math.max(maxError,Math.abs(s.energyProxy-before),
   C.distance(s.amplitudes[0],seed[1]),C.distance(s.amplitudes[1],seed[0]));
}
assert(maxError<1e-10);
console.log(JSON.stringify({gate:'P3.1',status:'PASS',frameCount:16,forward:208,backward:208,
  cyclesChecked:150,pairedAddressInvolution:true,zeroPinned:true,maxError},null,2));
