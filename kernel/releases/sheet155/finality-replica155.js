'use strict';
// SHEET155: verified live S147 /journal reads; multi-slot durable finality.
const fs=require('node:fs');
const P=require('./baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const M=require('./baseline154/baseline153/baseline152/baseline151/merkle151');
const {verifyGrant}=require('./baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/proof148');
const {SCHEMA:PHYSICAL}=require('./baseline154/baseline153/unified153');
const cfg=P.load(process.env.S155_REPLICA_CONFIG),signing=fs.readFileSync(cfg.signKey);
const pubs=Object.fromEntries(Object.entries(cfg.members).map(([id,p])=>[id,fs.readFileSync(p)]));
const authorities=Object.fromEntries(Object.entries(cfg.authorityPublicKeys).map(([id,p])=>[id,fs.readFileSync(p)]));
const resourcePub=fs.readFileSync(cfg.resourcePublicKey),anchorPub=fs.readFileSync(cfg.anchorPublicKey),floorPub=fs.readFileSync(cfg.floorPublicKey);
const SCHEMA='oasis.sheet155.finality.v1',ZERO='0'.repeat(64),sha=P.sha;
const domain={prepare:'S155:PREPARE',anchor:'S155:ANCHORED',final:'S155:FINAL'};
function seal(kind,body){return{body,signature:P.sign(signing,domain[kind],body)};}
function fresh(){return{schema:SCHEMA,nodeId:cfg.id,serial:0,head:ZERO,events:[],slot:null,finals:[]};}
if(!fs.existsSync(cfg.stateFile))P.atomic(cfg.stateFile,fresh());
function read(){const s=P.load(cfg.stateFile);if(s.schema!==SCHEMA||s.nodeId!==cfg.id||!Array.isArray(s.events)||s.events.length!==s.serial||!Array.isArray(s.finals))throw Error('S155_STATE_INVALID');let h=ZERO,prevFinal=ZERO,count=0;for(const [i,e] of s.events.entries()){if(e.index!==i+1||e.prev!==h||e.slot?.slot!==count+1)throw Error('S155_JOURNAL_CHAIN_INVALID');h=sha(e);if(e.kind==='FINAL'){count++;const item=s.finals[count-1];if(!item||item.slot!==count||item.intentDigest!==e.slot.intentDigest||item.prevPinDigest!==e.slot.prevPinDigest||item.snapshotDigest!==e.slot.snapshotDigest||item.receiptHash!==e.slot.receiptHash)throw Error('S155_FINAL_HISTORY_INVALID');prevFinal=sha(item);}}if(h!==s.head||count!==s.finals.length||s.slot&&(s.slot.slot!==count+1||s.slot.intentDigest!==s.events.at(-1)?.slot?.intentDigest))throw Error('S155_STATE_ROLLBACK_OR_TAMPER');return s;}
function persist(s,kind,slot){const e={index:s.events.length+1,prev:s.head,kind,slot};s.events.push(e);s.serial=s.events.length;s.head=sha(e);s.slot=slot;if(kind==='FINAL'){s.finals.push({slot:slot.slot,prevPinDigest:slot.prevPinDigest,intentDigest:slot.intentDigest,snapshotDigest:slot.snapshotDigest,receiptHash:slot.receiptHash});s.slot=null;}P.atomic(cfg.stateFile,s);}
function validateCert(votes,kind,digest,slot,prevPinDigest,snapshotDigest){if(!Array.isArray(votes))throw Error('S155_CERT_REQUIRED');const ids=new Set();for(const vote of votes){const v=vote?.body,id=v?.nodeId;if(!pubs[id]||ids.has(id)||v.phase!==kind||v.intentDigest!==digest||v.slot!==slot||v.prevPinDigest!==prevPinDigest||snapshotDigest&&v.snapshotDigest!==snapshotDigest||!P.verify(pubs[id],domain[kind],v,vote.signature))throw Error('S155_BAD_CERT');ids.add(id);}if(ids.size<2)throw Error('S155_NO_MAJORITY');}
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

async function anchorRead(){const v=await P.rpc({port:cfg.anchor.port,key:cfg.key,cert:cfg.cert,ca:cfg.ca,serverPin:cfg.anchor.certPin},'/read');if(!P.verify(anchorPub,'S151:ANCHOR',v.body,v.signature))throw Error('S155_ANCHOR_UNTRUSTED');return v;}
async function floorRead(){const v=await P.rpc({port:cfg.floor.port,key:cfg.key,cert:cfg.cert,ca:cfg.ca,serverPin:cfg.floor.certPin},'/read');if(!P.verify(floorPub,'S155:FLOOR',v.body,v.signature))throw Error('S155_FLOOR_UNTRUSTED');return v;}
async function liveJournals(){const valid=[];for(const [id,ref] of Object.entries(cfg.authorityMembers)){try{const r=await P.rpc({port:ref.port,key:cfg.key,cert:cfg.cert,ca:cfg.ca,serverPin:ref.certPin},'/journal',{leaderId:cfg.authorityReaderId});if(r.body?.nodeId===id&&P.verify(authorities[id],'S147:JOURNAL',r.body,r.signature))valid.push(r);}catch{}}return valid;}
function matchingJournalMajority(rows,intent,wantCompleted){const digest=sha(intent.receipt),matches=[];for(const x of rows){const j=x.body;let h=ZERO,begin=false,done=false,valid=true;for(const row of j.journal||[]){const p=row.proposal;if(p.index!== (j.journal.indexOf(row)+1)||p.prev!==h){valid=false;break;}const ids=new Set();for(const v of row.votes||[]){const b=v?.body;if(!authorities[b?.nodeId]||ids.has(b.nodeId)||b.digest!==sha(p)||b.index!==p.index||b.term!==p.term||b.prev!==p.prev||b.leaderId!==p.leaderId||!P.verify(authorities[b.nodeId],'S147:PREPARE',b,v.signature)){valid=false;break;}ids.add(b.nodeId);}if(!valid||ids.size<2){valid=false;break;}h=sha({prev:h,index:p.index,term:p.term,op:p.op});if(p.op.type==='BEGIN'&&p.op.txid===intent.txid&&p.op.digest===intent.receipt.body.digest)begin=true;if(p.op.type==='COMPLETE'&&p.op.txid===intent.txid&&p.op.receiptHash===digest)done=true;}
 if(valid&&h===j.head&&j.seq===j.journal.length&&begin&&(wantCompleted?done:!done))matches.push(j);}
 if(matches.length<2)throw Error('S155_LIVE_AUTHORITY_MAJORITY_REQUIRED');const kinds=new Set(matches.map(j=>j.seq+':'+j.head));if(kinds.size!==1)throw Error('S155_LIVE_AUTHORITY_HEAD_DIVERGENCE');return true;}
let busy=false;
async function onRequest(req,b){
 P.peer(req,cfg.coordinatorPin);
 if(!['/state','/prepare','/anchored','/final'].includes(req.url))throw Error('S155_UNKNOWN_ROUTE');
 const s=read();if(req.url==='/state'){const floor=await floorRead();if(floor.body.slot>s.finals.length)throw Error('S155_REPLICA_ROLLBACK_BELOW_EXTERNAL_FLOOR');return seal('final',{nodeId:cfg.id,serial:s.serial,head:s.head,completed:s.finals.length,phase:s.slot?.phase||'IDLE',slot:s.slot?.slot||null});}
 const intent=b.intent,slot=b.slot,prevPinDigest=b.prevPinDigest,digest=verifyIntent(intent);
 if(!Number.isSafeInteger(slot)||slot!==s.finals.length+1||!/^([a-f0-9]{64})$/.test(prevPinDigest||''))throw Error('S155_SLOT_ORDER_OR_GAP');
 const snapshot=await floorRead();if(snapshot.body.slot!==slot-1||snapshot.body.head!==prevPinDigest)throw Error('S155_PIN_ROLLBACK_OR_MISSING');
 if(s.slot?.intentDigest&&s.slot.intentDigest!==digest)throw Error('S155_CONFLICTING_SLOT');
 if(req.url==='/prepare'){
  if(!s.slot){const live=await anchorRead();if(sha(live)!==sha(intent.prior))throw Error('S155_STALE_ANCHOR');matchingJournalMajority(await liveJournals(),intent,false);persist(s,'PREPARED',{slot,prevPinDigest,intentDigest:digest,intent,phase:'PREPARED'});}
  return seal('prepare',{nodeId:cfg.id,intentDigest:digest,slot,prevPinDigest,phase:'prepare'});
 }
 validateCert(b.preparedVotes,'prepare',digest,slot,prevPinDigest);
 verifySnapshot(b.snapshot,intent);const live=await anchorRead();if(sha(live)!==sha(b.snapshot))throw Error('S155_STALE_ANCHOR');
 if(!s.slot)throw Error('S155_NO_LOCAL_PREPARE');
 if(req.url==='/anchored'){
  if(s.slot.phase==='PREPARED')persist(s,'ANCHORED',{...s.slot,phase:'ANCHORED',snapshotDigest:sha(b.snapshot)});
  else if(s.slot.snapshotDigest!==sha(b.snapshot))throw Error('S155_ANCHOR_CONFLICT');
  return seal('anchor',{nodeId:cfg.id,intentDigest:digest,slot,prevPinDigest,phase:'anchor',snapshotDigest:sha(b.snapshot)});
 }
 validateCert(b.anchoredVotes,'anchor',digest,slot,prevPinDigest,sha(b.snapshot));
 if(s.slot.phase!=='ANCHORED'&&s.slot.phase!=='FINAL')throw Error('S155_NOT_ANCHORED');
 matchingJournalMajority(await liveJournals(),intent,true); // LIVE S147 authority journals, never coordinator fixtures
 const receiptHash=sha(intent.receipt),snapshotDigest=sha(b.snapshot);
 if(s.slot.phase!=='FINAL')persist(s,'FINAL',{...s.slot,phase:'FINAL',snapshotDigest,receiptHash});
 return seal('final',{nodeId:cfg.id,intentDigest:digest,slot,prevPinDigest,phase:'final',snapshotDigest,receiptHash});
}
const server=P.serve(cfg.key,cfg.cert,cfg.ca,async(req,b)=>{if(req.url==='/state')return onRequest(req,b);if(busy)throw Error('S155_REPLICA_BUSY');busy=true;try{return await onRequest(req,b);}finally{busy=false;}});
process.on('message',v=>{if(v==='stop')server.close(()=>process.exit(0));});
module.exports={verifyIntent,verifySnapshot,matchingJournalMajority};
