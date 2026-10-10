import {createHmac,timingSafeEqual} from 'node:crypto';
import {QUANTA_PER_MS,CYCLE_QUANTA} from './p399_exact_time.mjs';
import {syncView,MAX_OFFSET_Q} from './p401_drift.mjs';
export const BLOCKADE='{-{+{%}+}-}';
const payload=o=>JSON.stringify({domain:'ROOT0/P402',sequence:o.sequence,cycle:o.cycle,offsetsQ:o.offsetsQ});
export function makeCalibration(key,sequence,cycle,offsets){
 if(!Number.isSafeInteger(sequence)||sequence<0||typeof cycle!=='bigint'||!Array.isArray(offsets)||offsets.length!==7||offsets.some(v=>typeof v!=='bigint'))throw new TypeError('calibration');
 const item={sequence,cycle:String(cycle),offsetsQ:offsets.map(String)};
 return {...item,tag:createHmac('sha256',key).update(payload(item)).digest('hex')};
}
export function verifyCalibration(key,item,retained){
 if(!item||!Number.isSafeInteger(item.sequence)||item.sequence<0||!/^[-]?\d+$/.test(item.cycle??'')||!Array.isArray(item.offsetsQ)||item.offsetsQ.length!==7||item.offsetsQ.some(x=>typeof x!=='string'||!/^[-]?\d+$/.test(x))||typeof item.tag!=='string'||!/^[0-9a-f]{64}$/.test(item.tag))return {ok:false,reason:'invalid-calibration'};
 const expected=createHmac('sha256',key).update(payload(item)).digest('hex');
 if(!timingSafeEqual(Buffer.from(expected,'hex'),Buffer.from(item.tag,'hex')))return {ok:false,reason:'invalid-tag'};
 if(!retained)return {ok:false,reason:'witness-unavailable'};
 if(item.sequence<retained.sequence||BigInt(item.cycle)<BigInt(retained.cycle))return {ok:false,reason:'rollback'};
 if(item.sequence===retained.sequence && item.tag!==retained.tag)return {ok:false,reason:'fork'};
 return {ok:true};
}
export function evaluateCycle({originQ,cycle,base,rate,calibration,boundQ=MAX_OFFSET_Q,missedLayers=[]}){
 if(typeof originQ!=='bigint'||typeof cycle!=='bigint'||!calibration||BigInt(calibration.cycle)!==cycle)throw new TypeError('cycle/calibration mismatch');
 const corrections=calibration.offsetsQ.map(BigInt);const missed=new Set(missedLayers);
 if(missedLayers.some(n=>!Number.isInteger(n)||n<0||n>=200))throw new RangeError('deadline');
 const states=[];let quarantined=0,late=0,ok=0;let maxResidual=0n;
 for(let layer=0;layer<200;layer++){
  const v=syncView(originQ,cycle,layer,base,rate,{corrections,boundQ});
  const residual=BigInt(v.residualQ);if((residual<0n?-residual:residual)>maxResidual)maxResidual=residual<0n?-residual:residual;
  const status=missed.has(layer)?'late':v.ok?'accepted':'quarantined';
  if(status==='late')late++;else if(status==='accepted')ok++;else quarantined++;
  states.push({layer,osi:v.osi,status,residualQ:v.residualQ,nominalQ:v.nominalQ});
 }
 return {ok:quarantined===0&&late===0,accepted:ok,quarantined,late,maxAbsoluteResidualQ:String(maxResidual),states};
}
export function boundedEstimate(actual,estimationError){if(actual.length!==7||estimationError.length!==7)throw RangeError('seven lanes');return actual.map((x,i)=>x+estimationError[i]);}
export {QUANTA_PER_MS,CYCLE_QUANTA,MAX_OFFSET_Q};
