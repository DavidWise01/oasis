import assert from 'node:assert/strict';
import {ADDRESS,DIMENSIONS,QUADS,TOPOLOGY,gates,forward,backward,norm,initial,conjugatePalindrome} from './p313_address_gates.mjs';
assert.equal(conjugatePalindrome(ADDRESS),true);
assert.equal(gates().length,10);assert.equal(DIMENSIONS.length,3);assert.equal(QUADS,'AaBbCcDd');assert.equal(TOPOLOGY,'{-{d}+{+{d}-}}');
let seed=0x3132026;
function rnd(){seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return(seed>>>0)/4294967296;}
let maxRecovery=0,maxNorm=0;
for(let k=0;k<25000;k++){
 const s=Array.from({length:3},()=>[(rnd()-.5)*2,(rnd()-.5)*2]),f=forward(s),b=backward(f);
 const err=Math.max(...s.flatMap((z,i)=>z.map((v,j)=>Math.abs(v-b[i][j]))));
 maxRecovery=Math.max(maxRecovery,err);maxNorm=Math.max(maxNorm,Math.abs(norm(s)-norm(f)));
 assert.ok(err<1e-11&&Math.abs(norm(s)-norm(f))<1e-11);
}
for(const bad of [[],Array(10).fill('x'),Array(10).fill('999'),Array(10).fill(1)])assert.throws(()=>gates(bad));
const result=forward(initial());
console.log(JSON.stringify({status:'PASS',cases:25000,maxRecovery,maxNorm,energy:result.map(z=>z[0]**2+z[1]**2),gates:gates()},null,2));
