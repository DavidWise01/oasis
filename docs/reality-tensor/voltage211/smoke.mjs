import assert from 'node:assert/strict';
import * as V from './voltage_wrapper.mjs';
import * as C from './cipher208.mjs';
assert.equal(V.MILLIVOLTS,-211);
assert.equal(C.FORWARD.length,208);
assert.equal(V.potentialEnergyEV(0),0.211);
assert.equal(V.potentialEnergyEV(1),-0.211);
assert.equal(V.zoomLengthM(1),V.PLANCK_LENGTH_M);
assert.equal(V.zoomLengthM(0),V.basePhotonEquivalentM);
let max=0;
for(let j=0;j<100;j++){
 const a=[{re:Math.sin(j),im:.2},{re:.34,im:Math.cos(j)}];
 const s=new V.WrappedCipher208({amplitudes:a,params:{depth:j/100,dtS:(j%7+1)*1e-16}});
 for(let i=0;i<208;i++)s.forward();
 s.flip();
 for(let i=0;i<208;i++)s.backward();
 assert(s.recovered());
 assert.equal(s.eventCount,417);
 max=Math.max(max,C.distance(s.field[0],a[1]),C.distance(s.field[1],a[0]));
}
console.log(JSON.stringify({status:'PASS',voltMilli:-211,fullCycles:100,maxRecoveredError:max,planckZoomOnly:true}));
