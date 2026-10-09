'use strict';
// SHEET 154: each mTLS replica owns an independent fsync'd finality decision file.
const fs=require('node:fs');
const P=require('./baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const M=require('./baseline153/baseline152/baseline151/merkle151');
const {verifyGrant}=require('./baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/proof148');
const {SCHEMA:PHYSICAL}=require('./baseline153/unified153');
const cfg=JSON.parse(fs.readFileSync(process.env.S154_REPLICA_CONFIG,'utf8'));
const signing=fs.readFileSync(cfg.signKey),pubs=Object.fromEntries(Object.entries(cfg.members).map(([id,p])=>[id,fs.readFileSync(p)]));
const authorities=Object.fromEntries(Object.entries(cfg.authorityPublicKeys).map(([id,p])=>[id,fs.readFileSync(p)]));
const resourcePub=fs.readFileSync(cfg.resourcePublicKey),anchorPub=fs.readFileSync(cfg.anchorPublicKey);
const SCHEMA='oasis.sheet154.finality.v1',ZERO='0'.repeat(64);
const domain={prepare:'S154:PREPARE',anchor:'S154:ANCHORED',final:'S154:FINAL'};
const sha=P.sha;
function seal(kind,body){return {body,signature:P.sign(signing,domain[kind],body)};}
function fresh(){return{schema:SCHEMA,nodeId:cfg.id,serial:0,slot:null,events:[],head:ZERO};}
if(!fs.existsSync(cfg.stateFile))P.atomic(cfg.stateFile,fresh());
function read(){const s=P.load(cfg.stateFile);if(s.schema!==SCHEMA||s.nodeId!==cfg.id||!Array.isArray(s.events)||s.events.length!==s.serial)throw Error('F154_STATE_INVALID');let h=ZERO;for(const [i,e] of s.events.entries()){if(e.index!==i+1||e.prev!==h)throw Error('F154_LOG_CHAIN_INVALID');h=sha(e);}if(h!==s.head)throw Error('F154_LOG_TAMPERED');const last=s.events.at(-1);if((last?.slot===undefined?null:last.slot)&&sha(last.slot)!==sha(s.slot))throw Error('F154_SLOT_TAMPERED');return s;}
function persist(s,kind,slot){s.events.push({index:s.events.length+1,prev:s.head,kind,slot});s.serial=s.events.length;s.head=sha(s.events.at(-1));s.slot=slot;P.atomic(cfg.stateFile,s);}
function validateCert(votes,kind,intentDigest){if(!Array.isArray(votes))throw Error('F154_NO_CERTIFICATE');const ids=new Set();for(const v of votes){const b=v?.body;if(!b||!pubs[b.nodeId]||ids.has(b.nodeId)||b.intentDigest!==intentDigest||b.phase!==kind||!P.verify(pubs[b.nodeId],domain[kind],b,v.signature))throw Error('F154_BAD_QUORUM_SIGNATURE');ids.add(b.nodeId);}if(ids.size<2)throw Error('F154_INSUFFICIENT_MAJORITY');return true;}
function verifyIntent(i){if(i?.schema!=='oasis.sheet154.intent.v1'||!i.txid||i.txid!==i.receipt?.body?.txid||!i.request||!i.proof||!i.checkpoint||!i.prior||!i.grant)throw Error('F154_INTENT_REQUIRED');
 const b=i.receipt.body,cp=i.checkpoint.body,prev=i.prior.body,record=i.proof.record;
 verifyGrant(i.grant,i.request,authorities);
 if(b.resourceId!==cfg.resourceId||b.resourceId!==i.request.resourceId||b.grantHead!==i.grant.head||b.digest!==sha({txid:i.request.txid,resourceId:i.request.resourceId,operationId:i.request.operationId,value:i.request.value,epoch:i.request.epoch})||b.epoch!==i.request.epoch||!P.verify(resourcePub,'S148:RECEIPT',b,i.receipt.signature))throw Error('F154_BAD_RECEIPT');
 if(cp.resourceId!==b.resourceId||cp.count<b.sequence||!P.verify(resourcePub,'S151:CHECKPOINT',cp,i.checkpoint.signature))throw Error('F154_BAD_CHECKPOINT');
 if(!P.verify(anchorPub,'S151:ANCHOR',prev,i.prior.signature)||prev.resourceId!==b.resourceId||prev.count>cp.count||M.root(prev.count,prev.frontier)!==prev.root)throw Error('F154_BAD_PRIOR_ANCHOR');
 if(record?.sequence!==b.sequence||record.hash!==b.recordHash||record.hash!==sha({resourceId:b.resourceId,sequence:record.sequence,prev:record.prev,payload:record.payload}))throw Error('F154_BAD_PHYSICAL_RECORD');
 let payload;try{payload=JSON.parse(record.payload);}catch{throw Error('F154_BAD_RECORD_PAYLOAD');}
 if(payload.schema!==PHYSICAL||payload.txid!==b.txid||payload.resourceId!==b.resourceId||payload.epoch!==b.epoch||payload.digest!==b.digest||payload.grantHead!==b.grantHead)throw Error('F154_RECORD_RECEIPT_MISMATCH');
 if(i.proof.inclusion?.count!==cp.count||i.proof.inclusion.index!==b.sequence-1||i.proof.inclusion.recordHash!==b.recordHash)throw Error('F154_WRONG_INCLUSION');M.verifyInclusion(i.proof.inclusion,cp.root,record.hash);
 return sha(i);
}
function verifySnapshot(snapshot,i){const b=snapshot?.body,c=i.checkpoint.body,p=i.prior;if(!b||!P.verify(anchorPub,'S151:ANCHOR',b,snapshot.signature)||b.resourceId!==cfg.resourceId||b.count!==c.count||b.root!==c.root||b.checkpointDigest!==sha(i.checkpoint)||b.previousAnchorDigest!==sha(p))throw Error('F154_ANCHOR_MISMATCH');return true;}
function verifyCompletion(evidence,intent){if(!Array.isArray(evidence))throw Error('F154_COMPLETION_EVIDENCE_REQUIRED');const good=new Set();const hash=sha(intent.receipt);for(const signed of evidence){const j=signed?.body,id=j?.nodeId;if(!authorities[id]||good.has(id)||!P.verify(authorities[id],'S147:JOURNAL',j,signed.signature))continue;
 let head=ZERO,valid=true,match=false;for(let idx=0;idx<(j.journal||[]).length;idx++){const row=j.journal[idx],p=row.proposal;if(p.index!==idx+1||p.prev!==head){valid=false;break;}const votes=row.votes||[],seen=new Set();for(const v of votes){const bb=v?.body;if(!bb||!authorities[bb.nodeId]||seen.has(bb.nodeId)||bb.digest!==sha(p)||bb.term!==p.term||bb.index!==p.index||bb.prev!==p.prev||bb.leaderId!==p.leaderId||!P.verify(authorities[bb.nodeId],'S147:PREPARE',bb,v.signature)){valid=false;break;}seen.add(bb.nodeId);}if(!valid||seen.size<2){valid=false;break;}head=sha({prev:head,index:p.index,term:p.term,op:p.op});if(p.op?.type==='COMPLETE'&&p.op.txid===intent.txid&&p.op.receiptHash===hash)match=true;}
 if(valid&&match&&j.seq===j.journal.length&&j.head===head)good.add(id);
}if(good.size<2)throw Error('F154_NO_SIGNED_COMPLETION_MAJORITY');return true;}
const server=P.serve(cfg.key,cfg.cert,cfg.ca,async(req,b)=>{
 P.peer(req,cfg.coordinatorPin);
 if(!['/state','/prepare','/anchored','/final'].includes(req.url))throw Error('F154_UNKNOWN_ROUTE');
 const s=read();if(req.url==='/state')return seal('final',{nodeId:cfg.id,serial:s.serial,head:s.head,phase:s.slot?.phase||'EMPTY',intentDigest:s.slot?.intentDigest||null});
 const i=b.intent;const digest=verifyIntent(i);
 if(s.slot?.intentDigest&&s.slot.intentDigest!==digest)throw Error('F154_CONFLICTING_FINALITY_INTENT');
 if(req.url==='/prepare'){
  if(s.slot?.phase==='FINAL')throw Error('F154_ALREADY_FINAL');
  if(!s.slot){const live=await P.rpc({port:cfg.anchor.port,key:cfg.key,cert:cfg.cert,ca:cfg.ca,serverPin:cfg.anchor.certPin},'/read');if(sha(live)!==sha(i.prior))throw Error('F154_STALE_PREPARE_ANCHOR');persist(s,'PREPARE',{intentDigest:digest,intent:i,phase:'PREPARED'});}
  return seal('prepare',{nodeId:cfg.id,intentDigest:digest,phase:'prepare'});
 }
 validateCert(b.preparedVotes,'prepare',digest);
 const live=await P.rpc({port:cfg.anchor.port,key:cfg.key,cert:cfg.cert,ca:cfg.ca,serverPin:cfg.anchor.certPin},'/read');
 verifySnapshot(b.snapshot,i);if(sha(live)!==sha(b.snapshot))throw Error('F154_STALE_ANCHOR');
 if(!s.slot)throw Error('F154_LOCAL_PREPARE_REQUIRED');
 if(req.url==='/anchored'){
  if(s.slot.phase==='PREPARED')persist(s,'ANCHORED',{...s.slot,phase:'ANCHORED',snapshotDigest:sha(b.snapshot)});
  else if(s.slot.snapshotDigest!==sha(b.snapshot))throw Error('F154_ANCHOR_CONFLICT');
  return seal('anchor',{nodeId:cfg.id,intentDigest:digest,phase:'anchor',snapshotDigest:sha(b.snapshot)});
 }
 validateCert(b.anchoredVotes,'anchor',digest);
 for(const v of b.anchoredVotes){if(v.body.snapshotDigest!==sha(b.snapshot))throw Error('F154_ANCHOR_VOTE_MISMATCH');}
 if(!['ANCHORED','FINAL'].includes(s.slot.phase)||s.slot.snapshotDigest!==sha(b.snapshot))throw Error('F154_NOT_ANCHORED');
 verifyCompletion(b.completionEvidence,i);
 if(s.slot.phase!=='FINAL')persist(s,'FINAL',{...s.slot,phase:'FINAL'});
 return seal('final',{nodeId:cfg.id,intentDigest:digest,phase:'final',snapshotDigest:sha(b.snapshot)});
});
process.on('message',x=>{if(x==='stop')server.close(()=>process.exit(0));});
module.exports={verifyIntent,verifySnapshot,verifyCompletion,validateCert};
