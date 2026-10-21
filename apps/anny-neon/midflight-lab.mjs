// ANNY v16.1 lab-only: kill Chromium while an IndexedDB write transaction remains unresolved.
// This module does NOT alter Harvester v12–v15, its journal/receiver code, or production stores.
// Two independent scenarios mirror the receiver ledger write and the journal CONFIRMED write.
import {CommitJournal,IndexedDBJournalStore} from "./journal.mjs";
import {ReceiverLedger} from "./receiver.mjs";
import {readAnny,observeAnny} from "./anny-observer.mjs";

export const MIDFLIGHT_MODES=Object.freeze(["RECEIVER_WRITE","JOURNAL_CONFIRM"]);
const PREFIX="anny-midflight-v16-1-";
const SOURCE=Object.freeze([1,2,3,4,5]);
const DEADLINE_MS=45000;
const activeTx=new Map();

export function validMidflightMode(mode){return MIDFLIGHT_MODES.includes(mode)}
export function expectedMidflightBase(mode){
 if(!validMidflightMode(mode))throw Error("UNKNOWN_MIDFLIGHT_MODE");
 return Object.freeze({journalState:"RELEASE_PENDING",
  receiverEffectCount:mode==="RECEIVER_WRITE"?0:1});
}
export function receiptAgrees(row,receipt){
 return !!row&&!!receipt&&receipt.accepted===true
  && row.transferId===receipt.transferId
  && row.deliveryKey===receipt.deliveryKey && row.digest===receipt.digest;
}
// Snapshot classifier compares independent journal and receiver ledger records.
// Both writes may be visible OR neither, but partial receiver receipts/effects fail.
export function classifyMidflightSnapshot(s){
 if(!s||!s.row)return "NO_JOURNAL";
 const {row,receipt,effectCount,view}=s;
 if(!Number.isInteger(effectCount)||effectCount<0||effectCount>1)return "LEDGER_EFFECT_INVALID";
 if(row.receipt&&!receiptAgrees(row,row.receipt))return "FORGED_JOURNAL_RECEIPT";
 if(receipt&&!receiptAgrees(row,receipt))return "FORGED_RECEIVER_RECEIPT";
 if(effectCount===0&&receipt)return "RECEIPT_WITHOUT_EFFECT";
 if(effectCount===1&&!receipt)return "EFFECT_WITHOUT_RECEIPT";
 const violet=view?.slots?.[17]?.value ?? "HELD";
 if(row.state==="RELEASE_PENDING"){
   if(row.receipt)return "PREMATURE_JOURNAL_RECEIPT";
   if(violet!=="HELD")return "PREMATURE_VERIFY";
   return effectCount===0?"PENDING_NO_EFFECT":"PENDING_RECEIVER_ACCEPTED";
 }
 if(row.state==="CONFIRMED"){
   return effectCount===1&&receiptAgrees(row,receipt)&&receiptAgrees(row,row.receipt)&&violet==="VERIFIED"
    ?"CONFIRMED_VERIFIED":"CONFIRMED_WITHOUT_AGREEMENT";
 }
 return "UNEXPECTED_JOURNAL_STATE";
}
function getContext(mode,token){
 if(!validMidflightMode(mode))throw Error("UNKNOWN_MIDFLIGHT_MODE");
 if(typeof token!=="string"||!/^mid-[a-f0-9-]{36}$/.test(token))throw Error("INVALID_MIDFLIGHT_TOKEN");
 const name=PREFIX+mode.toLowerCase()+"-"+token;
 return {name,
  journal:new CommitJournal(new IndexedDBJournalStore(name)),
  receiver:new ReceiverLedger(new IndexedDBJournalStore(name))};
}
function payload(row){return {
 transferId:row.transferId,digest:row.digest,sourceHex:row.sourceHex,deliveryKey:row.deliveryKey
}}
export async function initializeMidflight(mode){
 if(!validMidflightMode(mode))throw Error("UNKNOWN_MIDFLIGHT_MODE");
 const token="mid-"+crypto.randomUUID();
 const {journal,receiver}=getContext(mode,token);
 const epoch=1,transferId=token;
 const acks=["A","B"].flatMap(path=>SOURCE.map((byte,position)=>({
   transferId,epoch,path,position,byte
 })));
 await journal.prepare({transferId,epoch,bytes:[...SOURCE],acks});
 await journal.commit(transferId,epoch);
 await journal.pending(transferId,epoch);
 if(mode==="JOURNAL_CONFIRM"){
  const row=await journal.read(transferId);
  await receiver.deliver(payload(row));
 }
 const baseline=await inspectMidflight(mode,token);
 if(baseline.row.state!=="RELEASE_PENDING"||baseline.classification!==
   (mode==="RECEIVER_WRITE"?"PENDING_NO_EFFECT":"PENDING_RECEIVER_ACCEPTED")){
  throw Error("MIDFLIGHT_BASELINE_INVALID");
 }
 return {mode,token,baseline:{phase:baseline.row.state,classification:baseline.classification,
   effectCount:baseline.effectCount,digest:baseline.row.digest}};
}
export async function inspectMidflight(mode,token){
 const {journal,receiver}=getContext(mode,token);
 const row=await journal.read(token);
 if(!row)return {mode,token,row:null,receipt:null,effectCount:0,classification:"NO_JOURNAL"};
 const receipt=await receiver.reconcile(row.deliveryKey);
 const effectCount=await receiver.effectCount(row.deliveryKey);
 const view=await readAnny(journal,receiver,token);
 const s={mode,token,row,receipt,effectCount,view};
 return {...s,classification:classifyMidflightSnapshot(s)};
}
export async function armMidflight(mode,token){
 const key=mode+":"+token;
 if(activeTx.has(key))throw Error("MIDFLIGHT_ALREADY_ACTIVE");
 const {journal,receiver}=getContext(mode,token);
 const baseline=await inspectMidflight(mode,token);
 const expected=mode==="RECEIVER_WRITE"?"PENDING_NO_EFFECT":"PENDING_RECEIVER_ACCEPTED";
 if(baseline.classification!==expected)throw Error("MIDFLIGHT_BASELINE_NOT_READY");
 const db=await journal.store.db();
 // Only the dedicated scratch DB is touched. Never the main Harvester DB.
 const tx=db.transaction("transfers","readwrite",{durability:"strict"});
 const objectStore=tx.objectStore("transfers");
 const state={mode,token,status:"QUEUED",progress:0,completed:false,aborted:false,
  startedAt:Date.now()};
 activeTx.set(key,{tx,state});
 const row=baseline.row;
 let timeout=setTimeout(()=>{
   if(!state.completed&&!state.aborted){try{tx.abort()}catch{}}
 },DEADLINE_MS);
 tx.oncomplete=()=>{
  clearTimeout(timeout);state.completed=true;state.status="COMMITTED";
  activeTx.delete(key);
 };
 tx.onabort=()=>{
  clearTimeout(timeout);state.aborted=true;state.status="ABORTED";
  activeTx.delete(key);
 };
 tx.onerror=()=>{state.status="ERROR"};
 const targetKey=mode==="RECEIVER_WRITE"?"receiver:"+row.deliveryKey:row.transferId;
 const receipt={deliveryKey:row.deliveryKey,digest:row.digest,transferId:row.transferId,accepted:true};
 const targetRecord=mode==="RECEIVER_WRITE"?
  {transferId:row.transferId,digest:row.digest,sourceHex:row.sourceHex,
    deliveryKey:row.deliveryKey,effectCount:1,receipt}:
  {...row,state:"CONFIRMED",receipt};
 // Put intended record within the same unresolved transaction as a stream of
 // harmless churn writes. If killed before commit, none can become visible.
 const first=objectStore.put(targetRecord,targetKey);
 first.onerror=()=>{state.status="ERROR";try{tx.abort()}catch{}};
 function pump(){
  if(state.aborted||state.completed)return;
  const request=objectStore.put({token,mode,progress:state.progress+1},
    "__midflight_churn__:"+token);
  request.onerror=()=>{state.status="ERROR";try{tx.abort()}catch{}};
  request.onsuccess=()=>{
   state.progress++;
   state.status="RUNNING";
   // Enqueue within an active IDB success callback, keeping transaction alive.
   // The external driver SIGKILLs after sampling RUNNING + progress.
   if(!state.aborted&&!state.completed)pump();
  };
 }
 first.onsuccess=()=>pump();
 return {mode,token,active:true,status:"QUEUED"};
}
export function midflightProgress(mode,token){
 const t=activeTx.get(mode+":"+token);
 return t?{...t.state}:{mode,token,status:"NOT_ACTIVE",progress:0,completed:false};
}
export function abortMidflight(mode,token){
 const t=activeTx.get(mode+":"+token);
 if(!t)return {status:"NOT_ACTIVE"};
 try{t.tx.abort()}catch(err){return {status:"ABORT_FAILED",error:String(err)}}
 return {status:"ABORT_REQUESTED"};
}
export async function reconcileMidflight(mode,token){
 // Read only: deliberately NEVER calls receiver.deliver or journal.confirm.
 return inspectMidflight(mode,token);
}
export async function continueMidflight(mode,token){
 const before=await inspectMidflight(mode,token);
 if(before.classification==="CONFIRMED_VERIFIED")
  return {status:"ALREADY_CONFIRMED",replayed:false,before,after:before};
 if(before.classification!=="PENDING_NO_EFFECT"&&
    before.classification!=="PENDING_RECEIVER_ACCEPTED")
  throw Error("MIDFLIGHT_FAIL_CLOSED:"+before.classification);
 if(mode==="JOURNAL_CONFIRM"&&before.classification!=="PENDING_RECEIVER_ACCEPTED")
  throw Error("MIDFLIGHT_JOURNAL_RECEIVER_MISSING");
 const {journal,receiver}=getContext(mode,token);
 let receipt=await receiver.reconcile(before.row.deliveryKey);
 let replayed=false;
 if(!receipt){
  if(mode!=="RECEIVER_WRITE")throw Error("MIDFLIGHT_UNEXPECTED_REPLAY");
  receipt=await receiver.deliver(payload(before.row));
  replayed=true;
 }
 if(!receiptAgrees(before.row,receipt))throw Error("MIDFLIGHT_RECEIPT_INVALID");
 if(await receiver.effectCount(before.row.deliveryKey)!==1)
   throw Error("MIDFLIGHT_EFFECT_COUNT_INVALID");
 await journal.confirm(token,before.row.epoch,receipt);
 const after=await inspectMidflight(mode,token);
 if(after.classification!=="CONFIRMED_VERIFIED")
   throw Error("MIDFLIGHT_CONFIRMATION_FAILED");
 return {status:"RECONCILED",replayed,before,after};
}
export async function duplicateMidflight(mode,token,n=5){
 if(!Number.isInteger(n)||n<1||n>10)throw Error("MIDFLIGHT_DUPLICATE_COUNT");
 const before=await inspectMidflight(mode,token);
 if(before.classification!=="CONFIRMED_VERIFIED")
  throw Error("MIDFLIGHT_NOT_CONFIRMED");
 const {receiver}=getContext(mode,token);
 const results=await Promise.allSettled(
  Array.from({length:n},()=>receiver.deliver(payload(before.row))));
 const after=await inspectMidflight(mode,token);
 return {attempts:n,allFulfilled:results.every(x=>x.status==="fulfilled"),
  effectCount:after.effectCount,classification:after.classification};
}
export async function forgedMidflight(mode,token){
 const s=await inspectMidflight(mode,token);
 if(!s.row||!s.receipt)return {status:"NO_RECEIPT",violet:"HELD"};
 const corrupted={...s.receipt,digest:"0".repeat(64)};
 const view=observeAnny(s.row,corrupted);
 return {status:"FORGED_RECEIPT",violet:view.slots[17].value};
}
export const annyMidflightLab=Object.freeze({
 modes:MIDFLIGHT_MODES,initialize:initializeMidflight,arm:armMidflight,
 progress:midflightProgress,inspect:inspectMidflight,reconcile:reconcileMidflight,
 abort:abortMidflight,continue:continueMidflight,
 duplicate:duplicateMidflight,forged:forgedMidflight
});
if(typeof window!=="undefined")window.annyMidflightLab=annyMidflightLab;
