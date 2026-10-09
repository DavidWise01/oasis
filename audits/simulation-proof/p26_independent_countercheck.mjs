import assert from 'node:assert/strict';
// Independent ROOT0 P2.6 check: finite eight-label versus continuum field.
// Model-local mathematical assertions only; this does not prove simulation theory.
const N=8, ORBIT=9, theta=Math.PI/4;
assert.equal(2**3,N);
const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
const norm=x=>Math.sqrt(dot(x,x));
const onehot=i=>Array.from({length:N},(_,j)=>+(j===i));
const nearly=(a,b,eps=1e-12)=>Math.abs(a-b)<eps;
const rotateE=angle=>[Math.cos(angle),Math.sin(angle),0,0,0,0,0,0];
const orbit=Array.from({length:ORBIT},(_,j)=>rotateE(2*Math.PI*j/ORBIT));
const distances=[],fidelities=[];
for(let i=0;i<ORBIT;i++)for(let j=i+1;j<ORBIT;j++){
 const d=orbit[i].map((v,k)=>v-orbit[j][k]);
 distances.push(norm(d));fidelities.push(dot(orbit[i],orbit[j])**2);
}
assert.equal(distances.length,36);
assert(Math.min(...distances)>0.68);
assert(Math.max(...fidelities)<0.99);
const ex=Math.cos(theta),byImag=-Math.sin(theta);
assert(nearly(ex**2+byImag**2,1));
const maxOnehotFidelity=Math.max(ex**2,byImag**2);
assert(nearly(maxOnehotFidelity,.5));
const pol1=Array.from({length:N},(_,j)=>j===0||j===4?1/Math.sqrt(2):0);
const pol2=Array.from({length:N},(_,j)=>j===1?1/Math.sqrt(2):j===3?-1/Math.sqrt(2):0);
assert(nearly(dot(pol1,pol1),1));assert(nearly(dot(pol2,pol2),1));
assert(nearly(dot(pol1,pol2),0));
const weights=Array.from({length:N},(_,j)=>pol1[j]**2+pol2[j]**2);
assert(weights.every((v,i)=>nearly(v,[.5,.5,0,.5,.5,0,0,0][i])));
assert(weights.every(w=>w<1));
const coherence=Array.from({length:N},()=>1/Math.sqrt(N));
assert(nearly(dot(coherence,coherence),1));
assert(onehot(0).every((v,i)=>!nearly(v,coherence[i])));
console.log(JSON.stringify({gate:'ROOT0-P2.6-independent-countercheck',status:'PASS',
 classicalLabels:N,rotatedFieldOrbit:ORBIT,distinctOrbitPairs:distances.length,
 minOrbitDistance:Math.min(...distances),
 maxDistinctRayFidelity:Math.max(...fidelities),
 piOver4BasisFidelity:maxOnehotFidelity,
 physicalProjectorRank:2,positiveFrequencyBasisWeights:weights,
 conditionalQuantumAmplitudeLift:true,leanCompiled:false,
 simulationTheoryProven:false},null,2));
