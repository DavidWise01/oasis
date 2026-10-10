import {verify,createPublicKey} from 'node:crypto';
import {ControllerStore} from './p421_controller.mjs';
const canonical=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P418/anchor/v1',deployment:x.deployment,epoch:x.epoch,head:x.digest}));
export class PinnedWitnessGuard {
 constructor(dbPath,deployment,pinnedKey){this.controller=new ControllerStore(dbPath,deployment);this.deployment=deployment;this.pinned=createPublicKey(pinnedKey);this.floor=null;}
 check(response){
  if(!response?.ok||!response.stamp)return {ok:false,reason:'witness-unavailable'};
  const s=response.stamp;
  if(s.deployment!==this.deployment||!Number.isSafeInteger(s.epoch)||s.epoch<0||typeof s.digest!=='string'||!/^[0-9a-f]{64}$/.test(s.digest)||typeof s.signature!=='string'||!/^[A-Za-z0-9+/]+={0,2}$/.test(s.signature))return {ok:false,reason:'malformed-attestation'};
  let trusted=false;try{trusted=verify(null,canonical(s),this.pinned,Buffer.from(s.signature,'base64'));}catch{}
  if(!trusted)return {ok:false,reason:'invalid-anchor-signature'};
  if(this.floor && (s.epoch<this.floor.epoch||(s.epoch===this.floor.epoch&&s.digest!==this.floor.digest)))return {ok:false,reason:'stale-or-forked-attestation'};
  const state=this.controller.reconcile(s);
  if(!state.ok)return state;
  this.floor={epoch:s.epoch,digest:s.digest};
  return {ok:true,epoch:s.epoch};
 }
 close(){this.controller.close();}
}