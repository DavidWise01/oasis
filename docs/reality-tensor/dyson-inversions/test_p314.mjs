import assert from 'node:assert/strict';
import {compile,forward,inverse,norm,audit} from './p314_dual_branch.mjs';
assert.equal(compile().length,20);
assert.equal(compile().filter(x=>x.arm==='-+-').length,10);
assert.equal(compile().filter(x=>x.arm==='+-+').length,10);
let seed=3142026;const rnd=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return(seed>>>0)/4294967296};
let maxNorm=0,maxInverse=0;
for(let i=0;i<25000;i++){const s=Array.from({length:3},()=>[2*rnd()-1,2*rnd()-1]),f=forward(s),b=inverse(f);
const ne=Math.abs(norm(f)-norm(s)),ie=Math.max(...s.flatMap((z,j)=>z.map((x,k)=>Math.abs(x-b[j][k]))));
maxNorm=Math.max(maxNorm,ne);maxInverse=Math.max(maxInverse,ie);assert.ok(ne<1e-11&&ie<1e-11);}
console.log(JSON.stringify({status:'PASS',tests:25000,maxNorm,maxInverse,baseline:audit()},null,2));