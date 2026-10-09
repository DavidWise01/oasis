import assert from 'node:assert/strict';
import {ingress,egress,audit} from './p319_integrated.mjs';
let seed=3192026;function rnd(){seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return (seed>>>0)/4294967296;}
let maxNorm=0,maxRecovery=0;
for(let i=0;i<25000;i++){
 const request={seed:Math.floor(rnd()*1000000),dimension:i%3,quad:i%4,coords:[BigInt(i-12500),BigInt(-2*i),BigInt(i%17)],state:Array.from({length:3},()=>[2*rnd()-1,2*rnd()-1])};
 const p=ingress(request),b=egress(p),a=audit(request);
 assert.equal(b.seed,request.seed);assert.equal(b.dimension,request.dimension);assert.equal(b.quad,request.quad);assert.deepEqual(b.coords,request.coords);
 assert.equal(a.addressStable,true);assert.equal(a.coordinateStable,true);
 maxNorm=Math.max(maxNorm,a.normError);maxRecovery=Math.max(maxRecovery,a.recoveryError);
 assert.ok(a.normError<1e-11&&a.recoveryError<1e-11);
}
assert.throws(()=>egress({address:'bad',transported:[[1,0],[0,0],[0,0]]}));
assert.throws(()=>ingress({seed:1,state:[[1,0]]}));
console.log(JSON.stringify({status:'PASS',cases:25000,maxNorm,maxRecovery},null,2));
