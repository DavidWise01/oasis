import {verifyAttestation,verifyAgainstTrusted} from './p373_anchor.mjs';
/** In-memory independent witness mock; MUST NOT be used as durable production trust. */
export class MonotonicWitness {
 #latest=null;
 constructor(publicKey){this.publicKey=publicKey;this.available=true;}
 publish(stamp){
  if(!this.available)return {ok:false,reason:'witness-unavailable'};
  if(!verifyAttestation(stamp,this.publicKey))return {ok:false,reason:'invalid-signature'};
  const prior=this.#latest;
  if(prior && (stamp.epoch<prior.epoch || stamp.count<prior.count || (stamp.epoch===prior.epoch && (stamp.count!==prior.count || stamp.head!==prior.head))))return {ok:false,reason:'rollback-or-fork'};
  this.#latest=structuredClone(stamp);return {ok:true};
 }
 latest(){return this.available&&this.#latest?structuredClone(this.#latest):null;}
}
export function verifyWithWitness(dbFile,localStamp,witness){
 const latest=witness.latest();
 if(!latest)return {ok:false,reason:'trusted-witness-unavailable'};
 if(!verifyAttestation(localStamp,witness.publicKey))return {ok:false,reason:'local-signature-invalid'};
 if(localStamp.epoch!==latest.epoch||localStamp.count!==latest.count||localStamp.head!==latest.head)return {ok:false,reason:'local-checkpoint-rollback'};
 const result=verifyAgainstTrusted(dbFile,localStamp,witness.publicKey,latest);
 return result.ok?{ok:true,expected:latest}:{ok:false,reason:result.reason};
}