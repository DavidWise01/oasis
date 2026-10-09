'use strict';
const crypto=require('node:crypto');
const P=require('./baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const ZERO='0'.repeat(64), SCHEMA='oasis.sheet156.witness.v1';
function normalize(record){
 if(!record||!Number.isSafeInteger(record.slot)||record.slot<1||![record.prev,record.intentDigest,record.snapshotDigest,record.receiptHash].every(s=>typeof s==='string'&&/^[0-9a-f]{64}$/.test(s)))throw Error('W156_RECORD_INVALID');
 const {slot,prev,intentDigest,snapshotDigest,receiptHash}=record;
 return {slot,prev,intentDigest,snapshotDigest,receiptHash,head:P.sha({slot,prev,intentDigest,snapshotDigest,receiptHash})};
}
function verifyFinalVotes(record,votes,pubs){
 const seen=new Set();for(const vote of votes||[]){const v=vote?.body,id=v?.nodeId;if(!pubs[id]||seen.has(id)||v.slot!==record.slot||v.prevPinDigest!==record.prev||v.intentDigest!==record.intentDigest||v.snapshotDigest!==record.snapshotDigest||v.receiptHash!==record.receiptHash||v.phase!=='final'||!P.verify(pubs[id],'S155:FINAL',v,vote.signature))throw Error('W156_FINAL_CERT_INVALID');seen.add(id);}if(seen.size<2)throw Error('W156_FINAL_CERT_NEEDS_MAJORITY');
}
function verifyPrepares(record,votes,pubs){
 const seen=new Set();for(const vote of votes||[]){const v=vote?.body,id=v?.nodeId;if(!pubs[id]||seen.has(id)||v.slot!==record.slot||v.head!==record.head||v.prev!==record.prev||v.recordDigest!==P.sha(record)||!P.verify(pubs[id],'S156:PREPARE',v,vote.signature))throw Error('W156_PREPARE_CERT_INVALID');seen.add(id);}if(seen.size<2)throw Error('W156_PREPARE_CERT_NEEDS_MAJORITY');
}
function verifyFloorReply(reply,nonce,witnessPublicKeys){
 if(!reply||!reply.body||!Number.isSafeInteger(reply.body.slot)||!/^([0-9a-f]{64})$/.test(reply.body.head)||!nonce||reply.nonce!==nonce)throw Error('W156_FLOOR_PROOF_MISSING');
 const seen=new Set();for(const vote of reply.witnessHeads||[]){const v=vote?.body,id=v?.nodeId;if(!witnessPublicKeys[id]||seen.has(id)||v.nonce!==nonce||v.slot!==reply.body.slot||v.head!==reply.body.head||!P.verify(witnessPublicKeys[id],'S156:HEAD',v,vote.signature))throw Error('W156_FLOOR_HEAD_BAD_SIGNATURE');seen.add(id);}if(seen.size<2)throw Error('W156_FLOOR_NEEDS_2_OF_3_FRESH_HEADS');return true;
}
module.exports={ZERO,SCHEMA,normalize,verifyFinalVotes,verifyPrepares,verifyFloorReply};
