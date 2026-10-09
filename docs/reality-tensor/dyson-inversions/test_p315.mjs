import assert from 'node:assert/strict';
import {MODES,run,schedule,measure,compare} from './p315_apex_schedules.mjs';
import {norm,initial} from './p314_dual_branch.mjs';
let seed=3152026;const rnd=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return(seed>>>0)/4294967296};
let maxRec=0,maxNorm=0;
for(const mode of MODES){
 assert.equal(schedule(mode).length,mode==='PAIRED'?30:20);
 for(let i=0;i<25000;i++){
  const s=Array.from({length:3},()=>[2*rnd()-1,2*rnd()-1]),f=run(s,mode),b=run(f,mode,true);
  const rec=Math.max(...s.flatMap((z,j)=>z.map((v,k)=>Math.abs(v-b[j][k]))),energy=Math.abs(norm(s)-norm(f));
  maxRec=Math.max(maxRec,rec);maxNorm=Math.max(maxNorm,energy);
  assert.ok(rec<1e-11&&energy<1e-11);
 }
}
const result=compare();assert.ok(result.orderGap>1e-6);
assert.ok(result.modes.every(x=>!x.allZero));assert.equal(result.zeroFixedPoint,true);
console.log(JSON.stringify({status:'PASS',cases:75000,maxRec,maxNorm,...result},null,2));
