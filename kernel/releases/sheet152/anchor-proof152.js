'use strict';
// SHEET 152: binds the legacy 128-record S150 journal to the segmented S151
// journal without conflating their distinct Merkle root formats.
const P=require('./baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const J=require('./baseline151/baseline150/journal150');
const M=require('./baseline151/merkle151');
const {SCHEMA:ANCHOR}=require('./baseline151/anchor151');
const {CP}=require('./baseline151/ledger151');
const SCHEMA='oasis.sheet152.binding.v1';
function payload(receipt,journalProof){
 return P.sha({schema:SCHEMA,resourceId:receipt.body.resourceId,txid:receipt.body.txid,
   receiptHash:P.sha(receipt),recordHash:receipt.body.recordHash,
   checkpointDigest:P.sha(journalProof.checkpoint)});
}
function bundle(ledger,receipt,journalProof,checkpoint,snapshot){
 const records=ledger.read().records;const found=records.find(x=>x.payload===payload(receipt,journalProof));
 if(!found)throw Error('ANCHOR_BINDING_RECORD_NOT_FOUND');
 return{schema:SCHEMA,record:found,checkpoint,snapshot,proof:ledger.inclusion(found.sequence-1)};
}
function verifyStatic(receipt,journalProof,proof,resourceKey,anchorKey,prior){
 if(!receipt?.body||!resourceKey||!anchorKey||proof?.schema!==SCHEMA)throw Error('ANCHOR_PROOF_REQUIRED');
 // Exact old proof is still checked by S150; do not call 151 Merkle proofs "S150".
 J.verifyBundle(journalProof,receipt,resourceKey,prior||null);
 const cp=proof.checkpoint?.body,s=proof.snapshot?.body,r=proof.record;
 if(!cp||cp.schema!==CP||cp.resourceId!==receipt.body.resourceId||!P.verify(resourceKey,'S151:CHECKPOINT',cp,proof.checkpoint.signature))throw Error('ANCHOR_RESOURCE_CHECKPOINT_INVALID');
 if(!s||s.schema!==ANCHOR||s.resourceId!==receipt.body.resourceId||!P.verify(anchorKey,'S151:ANCHOR',s,proof.snapshot.signature))throw Error('ANCHOR_SNAPSHOT_SIGNATURE_INVALID');
 if(s.checkpointDigest!==P.sha(proof.checkpoint)||s.count!==cp.count||s.root!==cp.root||M.root(s.count,s.frontier)!==s.root||!Number.isSafeInteger(s.serial)||s.serial<0)throw Error('ANCHOR_CHECKPOINT_MISMATCH');
 if(!r||!Number.isSafeInteger(r.sequence)||r.sequence<1||r.payload!==payload(receipt,journalProof)||r.hash!==P.sha({resourceId:cp.resourceId,sequence:r.sequence,prev:r.prev,payload:r.payload}))throw Error('ANCHOR_BINDING_MISMATCH');
 if(proof.proof?.index!==r.sequence-1||proof.proof?.count!==cp.count||proof.proof?.recordHash!==r.hash||r.sequence>cp.count)throw Error('ANCHOR_INCLUSION_BINDING_INVALID');
 M.verifyInclusion(proof.proof,cp.root,r.hash);
 return{resourceId:cp.resourceId,count:s.count,serial:s.serial,root:s.root,snapshotDigest:P.sha(proof.snapshot)};
}
function verifyLive(op,live){
 if(!op?.anchorProof?.snapshot||!live?.body)throw Error('ANCHOR_LIVE_UNAVAILABLE');
 if(P.sha(op.anchorProof.snapshot)!==P.sha(live))throw Error('ANCHOR_STALE_LIVE_HEAD');
 return true;
}
module.exports={SCHEMA,payload,bundle,verifyStatic,verifyLive};
