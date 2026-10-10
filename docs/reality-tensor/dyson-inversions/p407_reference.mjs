import {generateKeyPairSync,sign,verify} from 'node:crypto';
import {DiverseQuorum} from './p406_diverse_quorum.mjs';
import {Q} from './p405_sensor_quorum.mjs';
const abs=x=>x<0n?-x:x;
const canonical=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P407/reference',sequence:x.sequence,cycle:x.cycle,values:x.values}));
export function signReference(privateKey,sequence,cycle,values){
 if(!Number.isSafeInteger(sequence)||sequence<0||!Number.isSafeInteger(cycle)||!Array.isArray(values)||values.length!==7||values.some(x=>typeof x!=='bigint'))throw Error('invalid-reference');
 const rec={sequence,cycle,values:values.map(String)};
 return {...rec,signature:sign(null,canonical(rec),privateKey).toString('base64')};
}
export class AnchoredDiverseClock{
 constructor(sensorKeys,publicKey,{toleranceQ=Q/4n,agreementQ=8n*Q/100n}={}){
  this.quorum=new DiverseQuorum(sensorKeys,{agreementQ,minGroups:2});this.publicKey=publicKey;this.toleranceQ=toleranceQ;this.lastReference=null;
 }
 evaluate(sensorRecords,reference){
  if(!reference||!Number.isSafeInteger(reference.sequence)||!Number.isSafeInteger(reference.cycle)||!Array.isArray(reference.values)||reference.values.length!==7||reference.values.some(x=>typeof x!=='string'||!/^[-]?\d+$/.test(x))||typeof reference.signature!=='string')return {ok:false,reason:'missing-or-malformed-reference'};
  if(!verify(null,canonical(reference),this.publicKey,Buffer.from(reference.signature,'base64')))return {ok:false,reason:'invalid-reference-signature'};
  if(this.lastReference&&(reference.sequence<=this.lastReference.sequence||reference.cycle<=this.lastReference.cycle))return {ok:false,reason:'reference-rollback'};
  const candidate=this.quorum.evaluate(sensorRecords);
  if(!candidate.ok)return candidate;
  const residuals=candidate.estimates.map((v,i)=>abs(v-BigInt(reference.values[i])));
  if(residuals.some(x=>x>this.toleranceQ))return {ok:false,reason:'reference-disagreement',maxResidualQ:String(residuals.reduce((a,b)=>a>b?a:b,0n))};
  this.lastReference={sequence:reference.sequence,cycle:reference.cycle};
  return {ok:true,estimates:candidate.estimates,participants:candidate.participants,maxResidualQ:String(residuals.reduce((a,b)=>a>b?a:b,0n))};
 }
}
export {Q,generateKeyPairSync};
