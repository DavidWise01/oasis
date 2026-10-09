import assert from 'node:assert/strict';
import {shape,at,execute,norm} from './p326_stream.mjs';
let seed=3262026;function rnd(){seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return(seed>>>0)/4294967296;}
const pairs=[[2,1],[4,3],[128,127],[2,999997],[999998,1],[500000,499999],[1000000,1]];
let cases=0,maxNorm=0,maxRecovery=0;
for(const [even,odd] of pairs)for(const side of ['left','right']){
 const g=shape(even,odd,side),trials=g.total>100000?2:20;
 for(let j=0;j<trials;j++){const s=Array.from({length:3},()=>[2*rnd()-1,2*rnd()-1]),f=execute(s,g),b=execute(f,g,true);
  const n=Math.abs(norm(s)-norm(f)),e=Math.max(...s.flatMap((z,i)=>z.map((v,k)=>Math.abs(v-b[i][k]))));
  maxNorm=Math.max(maxNorm,n);maxRecovery=Math.max(maxRecovery,e);assert.ok(n<1e-8&&e<1e-8);cases++;
 }
 const counts=[0,0];for(let k=1;k<=g.total;k++)counts[at(g,k).side]++;assert.deepEqual(counts,[g.left,g.right]);
}
console.log(JSON.stringify({status:'PASS',cases,maxNorm,maxRecovery},null,2));
