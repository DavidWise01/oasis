import assert from 'node:assert/strict';
import {encode} from './p318_hierarchy.mjs';
import {initial,norm} from './p314_dual_branch.mjs';
import {addressPhase,execute,ingress,egress,audit} from './p320_coordinate_binding.mjs';
let seed=3202026;const rnd=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return (seed>>>0)/4294967296;};
let maxNorm=0,maxRecovery=0,wrongKeySeparations=0;
for(let i=0;i<25000;i++){
 const request={seed:Math.floor(rnd()*1e6),dimension:i%3,quad:i%4,coords:[BigInt(i-12500),BigInt(-2*i),BigInt(i*i)],state:Array.from({length:3},()=>[2*rnd()-1,2*rnd()-1])};
 const p=ingress(request),b=egress(p),a=audit(request);
 assert.equal(b.seed,request.seed);assert.deepEqual(b.coords,request.coords);
 const ne=Math.abs(p.sourceNorm-norm(p.channels)),err=a.recoveryError;
 maxNorm=Math.max(maxNorm,ne);maxRecovery=Math.max(maxRecovery,err);
 assert.ok(ne<1e-11&&err<1e-11);
 const altered=encode(request.seed,request.dimension,request.quad,[request.coords[0]+1n,...request.coords.slice(1)]);
 const wrong=execute(p.channels,altered,true);
 if(Math.max(...wrong.flatMap((z,k)=>z.map((x,j)=>Math.abs(x-request.state[k][j]))))>1e-9)wrongKeySeparations++;
}
const sample=ingress({seed:12345,state:initial()});
assert.throws(()=>egress({...sample,channels:[[1,0]]}));
assert.ok(Number.isFinite(addressPhase(sample.address)));
console.log(JSON.stringify({status:'PASS',cases:25000,maxNorm,maxRecovery,wrongKeySeparations},null,2));
