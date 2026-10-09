'use strict';
// SHEET 157: no witness may install unproven history or erase a conflicting promise.
const P=require('./baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./baseline156/witness-verify156');
const crypto=require('node:crypto');
const SCHEMA='oasis.sheet157.catchup.v1';
function historyState(history){
 if(!Array.isArray(history)||history.length>256)throw Error('W157_HISTORY_SIZE_BOUND');
 let head=W.ZERO;
 for(let i=0;i<history.length;i++){
  const v=W.normalize(history[i]);
  if(v.slot!==i+1||v.prev!==head||v.head!==history[i].head||P.sha(history[i])!==P.sha(v))throw Error('W157_HISTORY_INVALID');
  head=v.head;
 }
 return{slot:history.length,head};
}
function certify(body,heads,exported,nonce,publicKeys){
 if(!/^[a-f0-9]{40}$/.test(nonce))throw Error('W157_CHALLENGE_INVALID');
 if(!Number.isSafeInteger(body?.slot)||body.slot<0||!/^([a-f0-9]{64})$/.test(body.head))throw Error('W157_HEAD_INVALID');
 const seen=new Set();
 for(const h of heads||[]){
  const v=h?.body,id=v?.nodeId;
  if(!publicKeys[id]||seen.has(id)||v.nonce!==nonce||v.slot!==body.slot||v.head!==body.head||!P.verify(publicKeys[id],'S156:HEAD',v,h.signature))throw Error('W157_MAJORITY_HEAD_INVALID');
  seen.add(id);
 }
 if(seen.size<2)throw Error('W157_MAJORITY_HEAD_MISSING');
 const ex=exported?.body;
 if(!ex||ex.schema!==SCHEMA||!seen.has(ex.nodeId)||ex.nonce!==nonce||ex.slot!==body.slot||ex.head!==body.head||!publicKeys[ex.nodeId]||!P.verify(publicKeys[ex.nodeId],'S157:EXPORT',ex,exported.signature))throw Error('W157_EXPORT_INVALID');
 const validated=historyState(ex.history);
 if(validated.slot!==body.slot||validated.head!==body.head)throw Error('W157_EXPORT_HISTORY_MISMATCH');
 return ex.history;
}
function admission(local,remote){
 if(remote.length<local.history.length)throw Error('W157_ROLLBACK_NOT_ALLOWED');
 for(let i=0;i<local.history.length;i++)if(P.sha(remote[i])!==P.sha(local.history[i]))throw Error('W157_FORK_QUARANTINE');
 if(local.pending){
  const p=W.normalize(local.pending),next=remote[local.history.length];
  if(!next||P.sha(p)!==P.sha(next))throw Error('W157_CONFLICTING_PENDING_QUARANTINE');
 }
 return true;
}
module.exports={SCHEMA,historyState,certify,admission};
