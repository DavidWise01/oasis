import assert from 'node:assert/strict';
import {ROOT,COUNT,TOTAL,stages,forward,backward,norm,audit} from './p323_full_cipher.mjs';
assert.equal(ROOT,0);assert.equal(COUNT,255);assert.equal(TOTAL,256);
const gates=stages();assert.equal(gates.length,255);
assert.deepEqual(gates.map(g=>g.index),Array.from({length:255},(_,i)=>i+1));
assert.equal(gates.filter(g=>g.port===1).length,128);assert.equal(gates.filter(g=>g.port===2).length,127);
let seed=3232026;const rnd=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return(seed>>>0)/4294967296};
let maxNorm=0,maxError=0;
for(let i=0;i<12000;i++){const s=Array.from({length:3},()=>[2*rnd()-1,2*rnd()-1]);const f=forward(s),b=backward(f);const ne=Math.abs(norm(s)-norm(f)),err=Math.max(...s.flatMap((z,j)=>z.map((v,k)=>Math.abs(v-b[j][k]))));maxNorm=Math.max(maxNorm,ne);maxError=Math.max(maxError,err);assert.ok(ne<1e-11&&err<1e-11);}
console.log(JSON.stringify({status:'PASS',cases:12000,maxNorm,maxError,baseline:audit()},null,2));
