import assert from 'node:assert/strict';
import {performance} from 'node:perf_hooks';import {randomBytes} from 'node:crypto';
import {BLOCKADE,makeCalibration,verifyCalibration,evaluateCycle,boundedEstimate,QUANTA_PER_MS as Q,MAX_OFFSET_Q} from './p402_calibration.mjs';
import {offsetsAt} from './p401_drift.mjs';
const begin=performance.now(),key=randomBytes(32);let assertions=0;
const check=v=>{assert.ok(v);assertions++},eq=(a,b)=>{assert.deepEqual(a,b);assertions++};
eq(BLOCKADE,'{-{+{%}+}-}');
const origin=-(10n**120n)+71n;
const base=[-5n,3n,-7n,0n,4n,-2n,8n].map(n=>n*Q/1000n),rate=[3n,-2n,5n,-7n,11n,-13n,17n].map(n=>n*Q/10000n);
let accepted=0,quarantined=0,late=0,maxError=0n;const cycles=121;
for(let i=0;i<cycles;i++){
 const cycle=BigInt(i-60),actual=offsetsAt(cycle,base,rate);
 const errors=Array.from({length:7},(_,lane)=>BigInt((i*17+lane*19)%61-30)*Q/100n);
 const estimate=boundedEstimate(actual,errors),record=makeCalibration(key,i,cycle,estimate);
 check(verifyCalibration(key,record,record).ok);
 const missed=i%11===0?[49,50,99,100,149,150,199]:[];
 const out=evaluateCycle({originQ:origin,cycle,base,rate,calibration:record,missedLayers:missed});
 eq(out.accepted+out.quarantined+out.late,200);
 accepted+=out.accepted;quarantined+=out.quarantined;late+=out.late;
 for(const s of out.states){check(['accepted','late','quarantined'].includes(s.status));if(s.status==='accepted')check(BigInt(s.residualQ)<=MAX_OFFSET_Q&&BigInt(s.residualQ)>=-MAX_OFFSET_Q);}
 const max=BigInt(out.maxAbsoluteResidualQ);if(max>maxError)maxError=max;
}
check(quarantined>0);check(late>0);check(accepted>0);
const sample=makeCalibration(key,130,70n,Array(7).fill(0n)),later=makeCalibration(key,131,71n,Array(7).fill(0n));
eq(verifyCalibration(key,sample,later).reason,'rollback');
eq(verifyCalibration(key,sample,null).reason,'witness-unavailable');
eq(verifyCalibration(key,{...later,offsetsQ:Array(7).fill('1')},sample).reason,'invalid-tag');
eq(verifyCalibration(key,makeCalibration(key,131,71n,Array(7).fill(1n)),later).reason,'fork');
const low=makeCalibration(key,0,0n,Array(7).fill(0n)),lowOut=evaluateCycle({originQ:origin,cycle:0n,base:Array(7).fill(0n),rate:Array(7).fill(0n),calibration:low});
eq(lowOut.accepted,200);eq(lowOut.quarantined,0);
const high=makeCalibration(key,1,0n,Array(7).fill(Q)),highOut=evaluateCycle({originQ:origin,cycle:0n,base:Array(7).fill(0n),rate:Array(7).fill(0n),calibration:high});
eq(highOut.quarantined,200);
console.log(JSON.stringify({assertions,cycles,views:cycles*200,accepted,quarantined,late,maxAbsoluteResidualMs:Number(maxError)/Number(Q),durationMs:performance.now()-begin},null,2));
