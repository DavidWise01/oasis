import assert from 'node:assert/strict';
import {shape,stages,initial,norm,forward,backward,audit} from './p324_primitive_stargate.mjs';
let seed=3242026;function rnd(){seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return(seed>>>0)/4294967296;}
let cases=0,maxRecovery=0,maxNorm=0;
for(const [even,odd] of [[2,1],[4,3],[10,9],[128,127],[256,255],[1024,1023]]){
 for(const orientation of ['left','right']){
  const cfg=shape(even,odd,orientation),ops=stages(cfg);
  assert.equal(ops.length,even+odd);assert.equal(ops.filter(g=>g.side===0).length,cfg.left);assert.equal(ops.filter(g=>g.side===1).length,cfg.right);
  for(let i=0;i<100;i++){const s=Array.from({length:3},()=>[rnd()*2-1,rnd()*2-1]),f=forward(s,cfg),b=backward(f,cfg);
   const e=Math.max(...s.flatMap((z,j)=>z.map((v,k)=>Math.abs(v-b[j][k])));maxRecovery=Math.max(e,maxRecovery);maxNorm=Math.max(maxNorm,Math.abs(norm(s)-norm(f)));assert.ok(e<1e-10&&Math.abs(norm(s)-norm(f))<1e-10);cases++;
  }
 }
}
for(const pair of [[2,2],[3,1],[0,1],[2,0],[-2,1]])assert.throws(()=>shape(...pair));
assert.equal(shape().nonRoot,255);assert.equal(shape().total,256);
console.log(JSON.stringify({status:'PASS',cases,maxRecovery,maxNorm,default:audit()},null,2));
