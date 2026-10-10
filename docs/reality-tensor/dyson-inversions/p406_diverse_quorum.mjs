import {verifySensor,Q} from './p405_sensor_quorum.mjs';
const abs=x=>x<0n?-x:x;
export class DiverseQuorum {
 constructor(keys,{agreementQ=8n*Q/100n,minGroups=2,quorum=Math.floor(keys.size/2)+1}={}){this.keys=keys;this.agreementQ=agreementQ;this.minGroups=minGroups;this.quorum=quorum;this.last=new Map();}
 evaluate(records){
  const valid=[],rejected=[],seen=new Set();
  for(const r of records){if(seen.has(r.id)){rejected.push('duplicate');continue;}seen.add(r.id);const v=verifySensor(r,this.keys,this.last);if(!v.ok){rejected.push(v.reason);continue;}valid.push(r);}
  if(valid.length<this.quorum)return {ok:false,reason:'insufficient-quorum',rejected};
  const subsets=[];const n=valid.length;
  for(let mask=1;mask<(1<<n);mask++){
   const subset=valid.filter((_,i)=>mask&(1<<i));if(subset.length<this.quorum)continue;
   if(new Set(subset.map(s=>this.keys.get(s.id).group)).size<this.minGroups)continue;
   const lanes=Array.from({length:7},(_,k)=>subset.map(s=>BigInt(s.values[k])).sort((a,b)=>a<b?-1:a>b?1:0));
   if(lanes.some(l=>l.at(-1)-l[0]>this.agreementQ))continue;
   subsets.push({subset,lanes});
  }
  if(!subsets.length)return {ok:false,reason:'no-diverse-consensus',rejected};
  subsets.sort((a,b)=>b.subset.length-a.subset.length||a.subset.map(x=>x.id).join().localeCompare(b.subset.map(x=>x.id).join()));
  const best=subsets[0];const estimates=best.lanes.map(a=>a[Math.floor((a.length-1)/2)]);
  if(subsets.some(s=>s.subset.length===best.subset.length&&s.lanes.some((a,k)=>abs(a[Math.floor((a.length-1)/2)]-estimates[k])>this.agreementQ)))return {ok:false,reason:'ambiguous-quorums',rejected};
  for(const r of valid)this.last.set(r.id,r.seq);
  return {ok:true,estimates,participants:best.subset.map(x=>x.id),rejected};
 }
}
