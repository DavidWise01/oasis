import test from "node:test";
import assert from "node:assert/strict";
import {CRASH_STAGES,validCrashStage,expectedAbruptState,
  receiptMatches,classifyAbruptEvidence} from "./crash-lab.mjs";

const digest="a".repeat(64);
const base={transferId:"t",epoch:1,sourceHex:"0102030405",
 digest,deliveryKey:"t:"+digest};
const receipt={transferId:"t",digest,deliveryKey:base.deliveryKey,accepted:true};
function evidence(state,{count=0,hasReceiver=false,hasJournalReceipt=false,
 violet="HELD"}={}){
 const record={...base,state};
 if(hasJournalReceipt)record.receipt={...receipt};
 return {record,receipt:hasReceiver?{...receipt}:null,effectCount:count,violet};
}

test("exact five interrupted durable checkpoints",()=>{
 assert.deepEqual(CRASH_STAGES,["PREPARED","COMMITTED","RELEASE_PENDING",
   "RECEIVER_RECORDED","CONFIRMED"]);
 assert(CRASH_STAGES.every(validCrashStage));
 assert.equal(validCrashStage("RELEASED"),false);
 assert.throws(()=>expectedAbruptState("RELEASED"),/UNKNOWN_ABRUPT_STAGE/);
});
test("expected journal states distinguish receipt recorded from commit confirmation",()=>{
 assert.deepEqual(CRASH_STAGES.map(s=>expectedAbruptState(s).state),
 ["PREPARED","COMMITTED","RELEASE_PENDING","RELEASE_PENDING","CONFIRMED"]);
 assert.deepEqual(CRASH_STAGES.map(s=>expectedAbruptState(s).receiverEffects),
 [0,0,0,1,1]);
 assert.deepEqual(CRASH_STAGES.map(s=>expectedAbruptState(s).confirmed),
 [false,false,false,false,true]);
});
test("precommit states refuse receiver effects",()=>{
 assert.equal(classifyAbruptEvidence(evidence("PREPARED")),"HOLD_PRECOMMIT");
 assert.equal(classifyAbruptEvidence(evidence("COMMITTED")),"HOLD_PRECOMMIT");
 assert.equal(classifyAbruptEvidence(evidence("COMMITTED",{count:1,hasReceiver:true})),"UNAUTHORIZED_EFFECT");
});
test("pending state distinguishes no receipt from durably accepted receiver",()=>{
 assert.equal(classifyAbruptEvidence(evidence("RELEASE_PENDING")),"PENDING_NO_EFFECT");
 assert.equal(classifyAbruptEvidence(evidence("RELEASE_PENDING",
 {count:1,hasReceiver:true})),"PENDING_RECEIVER_ACCEPTED");
 assert.equal(classifyAbruptEvidence(evidence("RELEASE_PENDING",
 {count:1,hasReceiver:false})),"PENDING_INCONSISTENT");
});
test("confirmed violet is gated by BOTH independent receipts",()=>{
 assert.equal(classifyAbruptEvidence(evidence("CONFIRMED",
 {count:1,hasReceiver:true,hasJournalReceipt:true,violet:"VERIFIED"})),
 "CONFIRMED_VERIFIED");
 assert.equal(classifyAbruptEvidence(evidence("CONFIRMED",
 {count:1,hasReceiver:false,hasJournalReceipt:true,violet:"AGREEMENT FAILED"})),
 "CONFIRMED_NOT_VERIFIED");
});
test("receipt mutation is rejected and cannot satisfy agreement",()=>{
 assert.equal(receiptMatches(base,receipt),true);
 assert.equal(receiptMatches(base,{...receipt,digest:"0".repeat(64)}),false);
 assert.equal(receiptMatches(base,{...receipt,accepted:false}),false);
 assert.equal(receiptMatches(base,{...receipt,transferId:"other"}),false);
 assert.equal(classifyAbruptEvidence({...evidence("CONFIRMED",
 {count:1,hasReceiver:true,hasJournalReceipt:true,violet:"VERIFIED"}),
 receipt:{...receipt,digest:"0".repeat(64)}}),"RECEIPT_MISMATCH");
});
test("duplicated ledger count fails closed even if receipts match",()=>{
 assert.equal(classifyAbruptEvidence(evidence("CONFIRMED",
 {count:2,hasReceiver:true,hasJournalReceipt:true,violet:"VERIFIED"})),"DUPLICATE_EFFECT");
});
test("missing record and unrecognized states fail closed",()=>{
 assert.equal(classifyAbruptEvidence(null),"NO_RECORD");
 assert.equal(classifyAbruptEvidence({record:null}),"NO_RECORD");
 assert.equal(classifyAbruptEvidence(evidence("UNKNOWN")),"UNKNOWN_JOURNAL_STATE");
});
test("wrong journal-stored receipt is rejected independently",()=>{
 const x=evidence("CONFIRMED",
 {count:1,hasReceiver:true,hasJournalReceipt:true,violet:"VERIFIED"});
 x.record.receipt.digest="0".repeat(64);
 assert.equal(classifyAbruptEvidence(x),"JOURNAL_RECEIPT_MISMATCH");
});
