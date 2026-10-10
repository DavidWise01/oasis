import {createHmac,timingSafeEqual} from 'node:crypto';
export const BLOCKADE='{-{+{%}+}-}';
export const Q=10n**33n; // 10^-36 seconds quantum, in one millisecond
const abs=x=>x<0n?-x:x;
const canonical=(id,seq,values)=>JSON.stringify({domain:'ROOT0/P405/sensor',id,seq,values:values.map(String)});
export function signSensor(id,seq,values,key){if(!Number.isSafeInteger(seq)||seq<0||values.length!==7||values.some(v=>typeof v!=='bigint'))throw Error('invalid readings');return {id,seq,values:values.map(String),mac:createHmac('sha256',key).update(canonical(id,seq,values)).digest('hex')};}
export function verifySensor(r,keys,last){
 if(!r||!keys.has(r.id)||!Number.isSafeInteger(r.seq)||r.seq<0||!Array.isArray(r.values)||r.values.length!==7||r.values.some(v=>typeof v!=='string'||!/^[-]?\d+$/.test(v))||typeof r.mac!=='string'||!/^[0-9a-f]{64}$/.test(r.mac))return {ok:false,reason:'invalid-reading'};
 const tag=createHmac('sha256',keys.get(r.id)).update(canonical(r.id,r.seq,r.values.map(BigInt))).digest();
 if(!timingSafeEqual(tag,Buffer.from(r.mac,'hex')))return {ok:false,reason:'bad-mac'};
 if(r.seq<= (last.get(r.id)??-1))return {ok:false,reason:'replay'};
 return {ok:true};
}
export class SensorQuorum {
 constructor(keys,{agreementQ=8n*Q/100n,toleranceQ=Q/4n}={}){if(keys.size<3)throw Error('requires three independent sensor identities');this.keys=keys;this.last=new Map();this.agreementQ=agreementQ;this.toleranceQ=toleranceQ;}
 evaluate(records){
  const valid=[],rejected=[];const seen=new Set();
  for(const r of records){if(seen.has(r.id)){rejected.push({id:r.id,reason:'duplicate-identity'});continue;}seen.add(r.id);
   const v=verifySensor(r,this.keys,this.last);if(v.ok)valid.push(r);else rejected.push({id:r.id,reason:v.reason});}
  if(valid.length<3)return {ok:false,reason:'insufficient-authenticated-sensors',rejected};
  const estimates=[],spread=[];
  for(let lane=0;lane<7;lane++){
   const x=valid.map(r=>BigInt(r.values[lane])).sort((a,b)=>a<b?-1:a>b?1:0);
   let best=null;
   for(const center of x){const near=x.filter(z=>abs(z-center)<=this.agreementQ);if(near.length>=2&&(!best||near.length>best.length))best=near;}
   if(!best)return {ok:false,reason:'no-agreement',lane,rejected};
   const sorted=[...best].sort((a,b)=>a<b?-1:a>b?1:0);
   const med=sorted[Math.floor((sorted.length-1)/2)];
   estimates.push(med);spread.push(sorted.at(-1)-sorted[0]);
  }
  for(const r of valid)this.last.set(r.id,r.seq);
  return {ok:true,estimates,spread,rejected};
 }
}
export function classify({estimated,trueOffset,deadlineMiss=false,boundQ=Q/4n}){
 if(deadlineMiss)return 'late';const error=abs(estimated-trueOffset);return error<=boundQ?'accepted':'quarantined';
}
