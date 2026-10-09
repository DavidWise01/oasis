'use strict';
// Reviewed repair of EXACTLY ONE fully persisted segment record after a torn head.
// Cannot invent a write and cannot release orphaned SHEET 142/144 locks.
const fs=require('node:fs'),path=require('node:path');
const P=require('./baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const M=require('./baseline151/merkle151');
const {SCHEMA:LEDGER,SIZE}=require('./baseline151/ledger151');
const DOMAIN='S152:RECOVERY_APPROVAL';
function review(dir,resourceId,anchor,anchorKey,operators,plan,approvals){
 const headfile=path.join(dir,'head.json'),head=P.load(headfile),recordCount=head.count,segmentDir=path.join(dir,'segments');
 const root=M.root(head.count,head.frontier);
 if(head.schema!==LEDGER||head.resourceId!==resourceId||root!==head.root||!Number.isSafeInteger(recordCount)||recordCount<0)throw Error('RECOVERY_HEAD_INVALID');
 if(!anchor?.body||!P.verify(anchorKey,'S151:ANCHOR',anchor.body,anchor.signature)||anchor.body.resourceId!==resourceId||anchor.body.count>recordCount||!Number.isSafeInteger(anchor.body.serial))throw Error('RECOVERY_ANCHOR_INVALID');
 const current=path.join(dir,'recovery152-decision.json');
 const index=Math.floor(recordCount/SIZE),segname=path.join(segmentDir,'segment-'+String(index).padStart(6,'0')+'.json');
 const names=fs.readdirSync(segmentDir).filter(x=>x.endsWith('.json')).sort();
 if(names.length!==index+1||names.at(-1)!==path.basename(segname))throw Error('RECOVERY_SEGMENT_SHAPE');
 const seg=P.load(segname);if(seg.schema!==LEDGER||seg.resourceId!==resourceId||seg.index!==index||!Array.isArray(seg.records)||seg.records.length!==recordCount%SIZE+1)throw Error('RECOVERY_NOT_SINGLE_TORN_APPEND');
 const record=seg.records.at(-1);if(record.sequence!==recordCount+1||record.prev!==head.lastRecordHash||record.hash!==P.sha({resourceId,sequence:record.sequence,prev:record.prev,payload:record.payload}))throw Error('RECOVERY_RECORD_INVALID');
 const expected={schema:'oasis.sheet152.review.v1',resourceId,headCount:recordCount,headRoot:head.root,appendHash:record.hash,anchorDigest:P.sha(anchor)};
 if(P.sha(expected)!==P.sha(plan))throw Error('RECOVERY_PLAN_MISMATCH');
 const seen=new Set();for(const vote of approvals||[]){const id=vote?.id,pub=operators[id];if(!pub||seen.has(id)||!P.verify(pub,DOMAIN,expected,vote.signature))throw Error('RECOVERY_VOTE_INVALID');seen.add(id);}if(seen.size<2)throw Error('RECOVERY_QUORUM_REQUIRED');
 if(fs.existsSync(current))throw Error('RECOVERY_DECISION_ALREADY_RECORDED');
 // Hold the existing writer lock; no lock stealing. An abandoned lock needs
 // separate operator resolution and is intentionally not cleared here.
 const lock=path.join(dir,'.writer.lock');let fd;try{fd=fs.openSync(lock,'wx',0o600);}catch(e){if(e.code==='EEXIST')throw Error('RECOVERY_WRITER_LOCK_HELD');throw e;}
 try{
  const cur=P.load(headfile);if(P.sha(cur)!==P.sha(head))throw Error('RECOVERY_RACED_HEAD');
  const next=M.appendPeak(head.count,head.frontier,1,M.leaf(head.count,record.hash));
  P.atomic(current,{plan:expected,approvals,phase:'APPROVED',nextRoot:M.root(next.count,next.frontier)});
  P.atomic(headfile,{schema:LEDGER,resourceId,count:next.count,root:M.root(next.count,next.frontier),lastRecordHash:record.hash,frontier:next.frontier,segmentSize:SIZE});
  P.atomic(current,{plan:expected,approvals,phase:'RECOVERED',nextRoot:M.root(next.count,next.frontier)});
  return{status:'RECOVERED',count:next.count,hash:record.hash};
 }finally{if(fd!==undefined){fs.closeSync(fd);fs.unlinkSync(lock);}}
}
module.exports={review,DOMAIN};
