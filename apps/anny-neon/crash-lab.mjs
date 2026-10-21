// ANNY v16.1 abrupt-Chromium-kill laboratory. Synthetic 5-byte source only.
// Uses a dedicated IndexedDB namespace per test stage; NEVER touches production
// transfer IDs or the normal GitHub Pages Harvester database.
// This module does not kill the browser. The external test driver owns SIGKILL.
import {CommitJournal,IndexedDBJournalStore} from "./journal.mjs";
import {ReceiverLedger} from "./receiver.mjs";
import {readAnny,observeAnny} from "./anny-observer.mjs";

export const CRASH_STAGES=Object.freeze([
  "PREPARED","COMMITTED","RELEASE_PENDING","RECEIVER_RECORDED","CONFIRMED"
]);
const BYTES=Object.freeze([1,2,3,4,5]);
const STORE_PREFIX="anny-abrupt-boundary-v16-1-";
const KEY_PREFIX="anny-abrupt-boundary-transfer-";

export function validCrashStage(stage){return CRASH_STAGES.includes(stage)}
export function expectedAbruptState(stage){
  if(!validCrashStage(stage))throw Error("UNKNOWN_ABRUPT_STAGE");
  const state=stage==="RECEIVER_RECORDED"?"RELEASE_PENDING":stage;
  const receiverEffects=(stage==="RECEIVER_RECORDED"||stage==="CONFIRMED")?1:0;
  return Object.freeze({state,receiverEffects,confirmed:stage==="CONFIRMED"});
}
export function receiptMatches(row,receipt){
 return !!row && !!receipt
  && receipt.accepted===true
  && receipt.transferId===row.transferId
  && receipt.digest===row.digest
  && receipt.deliveryKey===row.deliveryKey;
}
export function classifyAbruptEvidence(snapshot){
 if(!snapshot||!snapshot.record)return "NO_RECORD";
 const row=snapshot.record;
 if(snapshot.effectCount>1)return "DUPLICATE_EFFECT";
 if(snapshot.receipt && !receiptMatches(row,snapshot.receipt))return "RECEIPT_MISMATCH";
 if(row.receipt && !receiptMatches(row,row.receipt))return "JOURNAL_RECEIPT_MISMATCH";
 if(row.state==="CONFIRMED"){
   return receiptMatches(row,snapshot.receipt) &&
       snapshot.violet==="VERIFIED" && snapshot.effectCount===1
       ? "CONFIRMED_VERIFIED":"CONFIRMED_NOT_VERIFIED";
 }
 if(row.state==="PREPARED"||row.state==="COMMITTED"){
   return snapshot.effectCount===0 && !snapshot.receipt && snapshot.violet==="HELD"
    ? "HOLD_PRECOMMIT":"UNAUTHORIZED_EFFECT";
 }
 if(row.state==="RELEASE_PENDING"){
   if(snapshot.effectCount===0 && !snapshot.receipt && snapshot.violet==="HELD")
     return "PENDING_NO_EFFECT";
   if(snapshot.effectCount===1 && receiptMatches(row,snapshot.receipt)
      && snapshot.violet==="HELD")return "PENDING_RECEIVER_ACCEPTED";
   return "PENDING_INCONSISTENT";
 }
 return "UNKNOWN_JOURNAL_STATE";
}
function payload(row){return {
 transferId:row.transferId,deliveryKey:row.deliveryKey,
 digest:row.digest,sourceHex:row.sourceHex
}}
function stores(stage){
 if(!validCrashStage(stage))throw Error("UNKNOWN_ABRUPT_STAGE");
 const name=STORE_PREFIX+stage.toLowerCase();
 // NEW independent IndexedDB connections for the journal and receiver.
 return {
  journal:new CommitJournal(new IndexedDBJournalStore(name)),
  receiver:new ReceiverLedger(new IndexedDBJournalStore(name))
 };
}
function idFor(stage){
 if(!validCrashStage(stage))throw Error("UNKNOWN_ABRUPT_STAGE");
 return localStorage.getItem(KEY_PREFIX+stage.toLowerCase());
}
export async function snapshotAbrupt(stage,providedId=null){
 if(!validCrashStage(stage))throw Error("UNKNOWN_ABRUPT_STAGE");
 if(providedId!==null && (typeof providedId!=="string" ||
    !providedId.startsWith("abr-"+stage.toLowerCase()+"-") ||
    providedId.length>256))throw Error("INVALID_EXTERNAL_TRANSFER_LOOKUP");
 // External witness ID survives outside a killed browser. Never rely on
 // localStorage durability as a prerequisite for reading IndexedDB evidence.
 const id=providedId ?? idFor(stage);
 if(!id)return {stage,transferId:null,record:null,receipt:null,
   effectCount:0,phase:"NO_TRANSFER",violet:"HELD",decision:"NO_RECORD"};
 const {journal,receiver}=stores(stage);
 const row=await journal.read(id);
 const receipt=row?await receiver.reconcile(row.deliveryKey):null;
 const effectCount=row?await receiver.effectCount(row.deliveryKey):0;
 const view=row?await readAnny(journal,receiver,id):null;
 const result={stage,transferId:id,record:row,receipt,effectCount,
   phase:view?.phase||"NO_TRANSFER",violet:view?.slots[17].value||"HELD"};
 result.decision=classifyAbruptEvidence(result);
 return result;
}
export async function armAbrupt(stage){
 if(!validCrashStage(stage))throw Error("UNKNOWN_ABRUPT_STAGE");
 if(idFor(stage))throw Error("ABRUPT_STAGE_ALREADY_ARMED");
 const id="abr-"+stage.toLowerCase()+"-"+crypto.randomUUID();
 localStorage.setItem(KEY_PREFIX+stage.toLowerCase(),id);
 const {journal,receiver}=stores(stage);
 const epoch=1;
 const acks=["A","B"].flatMap(path=>
   BYTES.map((byte,position)=>({transferId:id,epoch,path,position,byte})));
 await journal.prepare({transferId:id,epoch,bytes:[...BYTES],acks});
 if(stage==="PREPARED")return snapshotAbrupt(stage);
 await journal.commit(id,epoch);
 if(stage==="COMMITTED")return snapshotAbrupt(stage);
 await journal.pending(id,epoch);
 if(stage==="RELEASE_PENDING")return snapshotAbrupt(stage);
 const row=await journal.read(id);
 const receipt=await receiver.deliver(payload(row));
 if(!receiptMatches(row,receipt))throw Error("ABRUPT_RECEIVER_MISMATCH");
 if(stage==="RECEIVER_RECORDED")return snapshotAbrupt(stage);
 await journal.confirm(id,epoch,receipt);
 return snapshotAbrupt(stage);
}
export async function reconcileAbrupt(stage,providedId=null){
 // READ ONLY: does not retry delivery or authorize a release.
 return snapshotAbrupt(stage,providedId);
}
export async function resumeAbrupt(stage,providedId=null){
 const before=await snapshotAbrupt(stage,providedId);
 const row=before.record;
 if(!row)throw Error("ABRUPT_RECORD_MISSING");
 const {journal,receiver}=stores(stage);
 const decision=classifyAbruptEvidence(before);
 if(decision==="HOLD_PRECOMMIT")return {
  status:"HOLD_PRECOMMIT", before,after:await snapshotAbrupt(stage,providedId),replayed:false
 };
 if(decision==="CONFIRMED_VERIFIED")return {
  status:"ALREADY_CONFIRMED",before,after:await snapshotAbrupt(stage),replayed:false
 };
 if(decision!=="PENDING_NO_EFFECT"&&decision!=="PENDING_RECEIVER_ACCEPTED")
   throw Error("ABRUPT_FAIL_CLOSED:"+decision);
 // Explicit synthetic continuation; no external-effect guarantee.
 // Reconcile the independent ledger FIRST; never blindly deliver twice.
 let receipt=await receiver.reconcile(row.deliveryKey);
 let replayed=false;
 if(!receipt){
   receipt=await receiver.deliver(payload(row));
   replayed=true;
 }
 if(!receiptMatches(row,receipt))throw Error("ABRUPT_RECEIPT_MISMATCH");
 if(await receiver.effectCount(row.deliveryKey)!==1)
   throw Error("ABRUPT_LEDGER_EFFECT_COUNT");
 await journal.confirm(row.transferId,row.epoch,receipt);
 const after=await snapshotAbrupt(stage,providedId);
 if(after.decision!=="CONFIRMED_VERIFIED")throw Error("ABRUPT_RESUME_NOT_VERIFIED");
 return {status:"RECONCILED",before,after,replayed};
}
export async function duplicateAbrupt(stage,n=5,providedId=null){
 if(!Number.isInteger(n)||n<1||n>10)throw Error("ABRUPT_DUPLICATE_COUNT");
 const before=await snapshotAbrupt(stage,providedId);
 if(before.decision!=="CONFIRMED_VERIFIED")throw Error("ABRUPT_NOT_CONFIRMED");
 const {receiver}=stores(stage);
 const replies=await Promise.allSettled(
   Array.from({length:n},()=>receiver.deliver(payload(before.record))));
 const after=await snapshotAbrupt(stage,providedId);
 return {
  attempts:n,allFulfilled:replies.every(r=>r.status==="fulfilled"),
  effectCount:after.effectCount,decision:after.decision
 };
}
export async function forgedObserverAbrupt(stage,providedId=null){
 const before=await snapshotAbrupt(stage,providedId);
 if(!before.record||!before.receipt)return {status:"NO_RECEIPT"};
 const forged={...before.receipt,digest:"0".repeat(64)};
 const result=observeAnny(before.record,forged);
 return {status:"FORGED_RECEIPT",violet:result.slots[17].value};
}
// Dedicated read-only interface to the browser driver, no auto-resume on reload.
export const annyCrashLab=Object.freeze({
 stages:CRASH_STAGES,expected:expectedAbruptState,
 arm:armAbrupt,snapshot:snapshotAbrupt,reconcile:reconcileAbrupt,
 resume:resumeAbrupt,duplicate:duplicateAbrupt,forged:forgedObserverAbrupt
});
if(typeof window!=="undefined")window.annyCrashLab=annyCrashLab;
