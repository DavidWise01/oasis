import {fingerprint,verifyVote} from './p359_witness.mjs';
import {CrashWitness} from './p361_crash.mjs';
/** Abstract trusted authority. reserve() MUST be atomic, durable, nonrollbackable.
 * InMemoryAuthority is ONLY a simulation, not a production authority.
 */
export class InMemoryAuthority {
 #records=new Map(); available=true;
 async reserve(id,cp){
  if(!this.available)throw Error('authority-unavailable');
  const group=id+'|'+cp.context, fingerprintValue=fingerprint(cp);
  let state=this.#records.get(group);
  if(!state){state={maxEpoch:-1,records:new Map()};this.#records.set(group,state);}
  const old=state.records.get(cp.epoch);
  if(old){if(old!==fingerprintValue)return {ok:false,reason:'trusted-conflict'};return {ok:true,previous:true};}
  if(cp.epoch<=state.maxEpoch)return {ok:false,reason:'epoch-rollback'};
  state.records.set(cp.epoch,fingerprintValue);state.maxEpoch=cp.epoch;
  return {ok:true,previous:false};
 }
 inspect(id,cp){const group=this.#records.get(id+'|'+cp.context);return {maxEpoch:group?.maxEpoch??-1,reserved:group?.records.has(cp.epoch)??false};}
}
export class WatermarkedWitness {
 constructor(primaryDir,anchorDir,keys,authority){this.primaryDir=primaryDir;this.anchorDir=anchorDir;this.keys=keys;this.authority=authority;}
 async vote(id,cp,privateKey){
  if(!this.keys.has(id))return {ok:false,reason:'unknown-witness'};
  let reservation;try{reservation=await this.authority.reserve(id,cp);}catch{return {ok:false,reason:'authority-unavailable'};}
  if(!reservation.ok)return reservation;
  const primary=new CrashWitness(this.primaryDir,this.keys);
  if(reservation.previous){const inspected=await primary.inspect(id,cp);
   if(inspected.status!=='committed')return {ok:false,reason:'trusted-quarantine'};
   const recovered=await primary.vote(id,cp,privateKey);
   if(recovered.ok&&recovered.duplicate&&verifyVote(recovered.vote,this.keys))return recovered;
   return {ok:false,reason:'trusted-quarantine'};
  }
  try{return await primary.vote(id,cp,privateKey);}catch{return {ok:false,reason:'local-write-failed-quarantined'};}
 }
}