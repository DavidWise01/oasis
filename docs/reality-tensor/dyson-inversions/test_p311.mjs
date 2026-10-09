import assert from 'node:assert/strict';
import {initial,forward,backward,norm,analytic,audit} from './p311_nested_scattering.mjs';
let seed=0x3112026;
function rnd(){seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return (seed>>>0)/4294967296;}
let maxError=0,maxNorm=0,maxAnalytic=0;
for(let i=0;i<25000;i++){
 const p={eta1:rnd(),eta2:rnd(),phase1:(rnd()-.5)*100,phase2:(rnd()-.5)*100};
 const s=Array.from({length:3},()=>[(rnd()-.5)*2,(rnd()-.5)*2]);
 const y=forward(s,p),z=backward(y,p);
 const e=Math.max(...s.flatMap((v,k)=>v.map((x,j)=>Math.abs(x-z[k][j]))));
 maxError=Math.max(maxError,e);maxNorm=Math.max(maxNorm,Math.abs(norm(s)-norm(y)));
 assert.ok(e<1e-12&&Math.abs(norm(s)-norm(y))<1e-11);
 const a=analytic(p),baseline=forward(initial(),p),actual=baseline.map(q=>q[0]**2+q[1]**2);
 maxAnalytic=Math.max(maxAnalytic,...actual.map((x,k)=>Math.abs(x-[a.travel,a.domain1,a.domain2][k])));
 assert.ok(Math.max(...actual.map((x,k)=>Math.abs(x-[a.travel,a.domain1,a.domain2][k])))<1e-12);
}
for(const bad of [-.01,1.01,NaN,Infinity])assert.throws(()=>forward(initial(),{eta1:bad}));
console.log(JSON.stringify({status:'PASS',cases:25000,maxError,maxNorm,maxAnalytic,default:audit()},null,2));
