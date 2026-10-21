import test from "node:test";
import assert from "node:assert/strict";
import {MIDFLIGHT_MODES,validMidflightMode,expectedMidflightBase,
 receiptAgrees,classifyMidflightSnapshot} from "./midflight-lab.mjs";

const digest="a".repeat(64);
const row={transferId:"mid-1",epoch:1,state:"RELEASE_PENDING",
 digest,sourceHex:"0102030405",deliveryKey:"mid-1:"+digest};
const goodReceipt={accepted:true,transferId:row.transferId,
 digest:row.digest,deliveryKey:row.deliveryKey};
const view=(value)=>({slots:Array.from({length:18},(_,i)=>({
 name:"Slot "+(i+1),status:"pending",value:i===17?value:"HELD"}))});
function snapshot(state="RELEASE_PENDING",effectCount=0,hasReceipt=false,
 hasJournalReceipt=false,violet="HELD"){
 const r={...row,state};
 if(hasJournalReceipt)r.receipt={...goodReceipt};
 return {row:r,receipt:hasReceipt?{...goodReceipt}:null,
 effectCount,view:view(violet)};
}

test("exact two unresolved IndexedDB transaction modes",()=>{
 assert.deepEqual(MIDFLIGHT_MODES,["RECEIVER_WRITE","JOURNAL_CONFIRM"]);
 assert.equal(validMidflightMode("RECEIVER_WRITE"),true);
 assert.equal(validMidflightMode("JOURNAL_CONFIRM"),true);
 assert.equal(validMidflightMode("EXTERNAL_SEND"),false);
 assert.throws(()=>expectedMidflightBase("BOGUS"),/UNKNOWN_MIDFLIGHT_MODE/);
});
test("baseline receiver and journal states are pending with distinct ledger receipt expectations",()=>{
 assert.deepEqual(expectedMidflightBase("RECEIVER_WRITE"),{
 journalState:"RELEASE_PENDING",receiverEffectCount:0});
 assert.deepEqual(expectedMidflightBase("JOURNAL_CONFIRM"),{
 journalState:"RELEASE_PENDING",receiverEffectCount:1});
});
test("interrupted receiver transaction cannot expose a partial effect",()=>{
 assert.equal(classifyMidflightSnapshot(snapshot()),"PENDING_NO_EFFECT");
 assert.equal(classifyMidflightSnapshot(snapshot("RELEASE_PENDING",1,true)),
  "PENDING_RECEIVER_ACCEPTED");
 assert.equal(classifyMidflightSnapshot(snapshot("RELEASE_PENDING",1,false)),
  "EFFECT_WITHOUT_RECEIPT");
 assert.equal(classifyMidflightSnapshot(snapshot("RELEASE_PENDING",0,true)),
  "RECEIPT_WITHOUT_EFFECT");
});
test("interrupted journal confirmation cannot verify without both receipts",()=>{
 assert.equal(classifyMidflightSnapshot(snapshot("RELEASE_PENDING",1,true,false)),
  "PENDING_RECEIVER_ACCEPTED");
 assert.equal(classifyMidflightSnapshot(snapshot("RELEASE_PENDING",1,true,true)),
  "PREMATURE_JOURNAL_RECEIPT");
 assert.equal(classifyMidflightSnapshot(snapshot("RELEASE_PENDING",1,true,false,"VERIFIED")),
  "PREMATURE_VERIFY");
});
test("VERIFIED requires independent receiver receipt and journal confirmation",()=>{
 assert.equal(classifyMidflightSnapshot(snapshot("CONFIRMED",1,true,true,"VERIFIED")),
  "CONFIRMED_VERIFIED");
 assert.equal(classifyMidflightSnapshot(snapshot("CONFIRMED",0,false,true,"AGREEMENT FAILED")),
  "CONFIRMED_WITHOUT_AGREEMENT");
 assert.equal(classifyMidflightSnapshot(snapshot("CONFIRMED",1,true,false,"AGREEMENT FAILED")),
  "CONFIRMED_WITHOUT_AGREEMENT");
});
test("forged receipt is rejected and duplicate ledger effects fail closed",()=>{
 assert.equal(receiptAgrees(row,goodReceipt),true);
 assert.equal(receiptAgrees(row,{...goodReceipt,accepted:false}),false);
 assert.equal(receiptAgrees(row,{...goodReceipt,digest:"0".repeat(64)}),false);
 const forged=snapshot("CONFIRMED",1,true,true,"VERIFIED");
 forged.receipt.digest="0".repeat(64);
 assert.equal(classifyMidflightSnapshot(forged),"FORGED_RECEIVER_RECEIPT");
 assert.equal(classifyMidflightSnapshot(snapshot("CONFIRMED",2,true,true,"VERIFIED")),
  "LEDGER_EFFECT_INVALID");
});
test("missing journal and unexpected journal states never authorize release",()=>{
 assert.equal(classifyMidflightSnapshot(null),"NO_JOURNAL");
 assert.equal(classifyMidflightSnapshot({row:null}),"NO_JOURNAL");
 assert.equal(classifyMidflightSnapshot(snapshot("PREPARED")),"UNEXPECTED_JOURNAL_STATE");
});
test("unchanged receiver record and duplicate retry cannot be confused with new confirmation",()=>{
 const s=snapshot("RELEASE_PENDING",1,true,false,"HELD");
 assert.equal(classifyMidflightSnapshot(s),"PENDING_RECEIVER_ACCEPTED");
 assert.equal(s.row.receipt,undefined);
 assert.equal(s.effectCount,1);
 assert.equal(s.view.slots[17].value,"HELD");
});
