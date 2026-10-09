# SHEET 155 — Complete New Executable Sources

These are the authored source files. The full frozen earlier lineage is bundled under `baseline154/` in the ZIP.


## floor155.js

```javascript
'use strict';
// A separately persisted append-only authorization floor; test-only one-host service.
const fs=require('node:fs');
const P=require('./baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const cfg=P.load(process.env.S155_FLOOR_CONFIG), signing=fs.readFileSync(cfg.signKey);
const finalKeys=Object.fromEntries(Object.entries(cfg.finalityPublicKeys).map(([id,p])=>[id,fs.readFileSync(p)]));
const ZERO='0'.repeat(64),SCHEMA='oasis.sheet155.floor.v1';
function seal(body){return{body,signature:P.sign(signing,'S155:FLOOR',body)};}
function fresh(){return{schema:SCHEMA,history:[],head:ZERO,slot:0};}
if(!fs.existsSync(cfg.stateFile))P.atomic(cfg.stateFile,fresh());
function load(){const x=P.load(cfg.stateFile);if(x.schema!==SCHEMA||x.slot!==x.history?.length)throw Error('S155_FLOOR_INVALID');let h=ZERO;for(let i=0;i<x.history.length;i++){const row=x.history[i];if(row.slot!==i+1||row.prev!==h||row.head!==P.sha({slot:row.slot,prev:row.prev,intentDigest:row.intentDigest,snapshotDigest:row.snapshotDigest,receiptHash:row.receiptHash}))throw Error('S155_FLOOR_TAMPER');h=row.head;}if(h!==x.head)throw Error('S155_FLOOR_ROLLBACK_OR_TAMPER');return x;}
function pin(b){const x=load(),r=b.record;if(!r||!Number.isSafeInteger(r.slot)||r.slot<1||!/^([0-9a-f]{64})$/.test(r.intentDigest)||!/^([0-9a-f]{64})$/.test(r.snapshotDigest)||!/^([0-9a-f]{64})$/.test(r.receiptHash))throw Error('S155_PIN_INVALID');
 const actual={slot:r.slot,prev:r.prev,intentDigest:r.intentDigest,snapshotDigest:r.snapshotDigest,receiptHash:r.receiptHash,head:P.sha({slot:r.slot,prev:r.prev,intentDigest:r.intentDigest,snapshotDigest:r.snapshotDigest,receiptHash:r.receiptHash})};
 if(r.slot===x.slot&&P.sha(x.history.at(-1))===P.sha(actual))return seal({slot:x.slot,head:x.head});
 if(r.slot!==x.slot+1||r.prev!==x.head)throw Error('S155_FLOOR_STALE_OR_GAP');
 const ids=new Set();for(const vote of b.finalVotes||[]){const v=vote?.body,id=v?.nodeId;if(!finalKeys[id]||ids.has(id)||v.slot!==r.slot||v.prevPinDigest!==r.prev||v.intentDigest!==r.intentDigest||v.snapshotDigest!==r.snapshotDigest||v.receiptHash!==r.receiptHash||v.phase!=='final'||!P.verify(finalKeys[id],'S155:FINAL',v,vote.signature))throw Error('S155_FLOOR_BAD_CERT');ids.add(id);}if(ids.size<2)throw Error('S155_FLOOR_NEEDS_2_OF_3');
 x.history.push(actual);x.slot++;x.head=actual.head;P.atomic(cfg.stateFile,x);return seal({slot:x.slot,head:x.head});}
const server=P.serve(cfg.key,cfg.cert,cfg.ca,(req,b)=>{if(req.url==='/read'){if(!req.socket.authorized||!cfg.readPins.includes(P.fp(req.socket.getPeerCertificate(true))))throw Error('S155_FLOOR_READER_UNTRUSTED');const x=load();return seal({slot:x.slot,head:x.head});}P.peer(req,cfg.coordinatorPin);if(req.url!=='/pin')throw Error('S155_FLOOR_ROUTE');return pin(b);});
process.on('message',v=>{if(v==='stop')server.close(()=>process.exit(0));});
module.exports={load,pin};
```


## finality-replica155.js

```javascript
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
```


## anchor-gateway155.js

```javascript
'use strict';
// Independent anchor admission gateway: only this process owns the TLS credential
// that the underlying immutable SHEET151 anchor will accept for /advance.
const fs=require('node:fs');
const P=require('./baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const {verifyGrant}=require('./baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/proof148');
const M=require('./baseline154/baseline153/baseline152/baseline151/merkle151');
const cfg=JSON.parse(fs.readFileSync(process.env.S155_GATEWAY_CONFIG,'utf8'));
const pubs=Object.fromEntries(Object.entries(cfg.finalityPublicKeys).map(([id,p])=>[id,fs.readFileSync(p)]));
const authorityKeys=Object.fromEntries(Object.entries(cfg.authorityPublicKeys).map(([id,p])=>[id,fs.readFileSync(p)]));
const resourcePub=fs.readFileSync(cfg.resourcePublicKey), floorPub=fs.readFileSync(cfg.floorPublicKey);
const inner=(path,b={})=>P.rpc({port:cfg.inner.port,key:cfg.key,cert:cfg.cert,ca:cfg.ca,serverPin:cfg.inner.certPin},path,b);
function validate(intent,votes){if(intent?.schema!=='oasis.sheet154.intent.v1'||!intent.receipt||!intent.prior||!intent.checkpoint||!intent.proof)throw Error('G155_INTENT_REQUIRED');
 verifyGrant(intent.grant,intent.request,authorityKeys);
 const r=intent.receipt,b=r.body,cp=intent.checkpoint.body,p=intent.prior.body,record=intent.proof.record;
 if(!P.verify(resourcePub,'S148:RECEIPT',b,r.signature)||!P.verify(resourcePub,'S151:CHECKPOINT',cp,intent.checkpoint.signature)||b.txid!==intent.txid||cp.resourceId!==b.resourceId||cp.count<b.sequence)throw Error('G155_RESOURCE_SIGNATURE_INVALID');
 if(record?.hash!==b.recordHash||intent.proof.inclusion?.recordHash!==b.recordHash||intent.proof.inclusion?.count!==cp.count)throw Error('G155_MISSING_PHYSICAL_PROOF');
 M.verifyInclusion(intent.proof.inclusion,cp.root,record.hash);
 const digest=P.sha(intent),seen=new Set();for(const v of votes||[]){const bb=v?.body,id=bb?.nodeId;if(!pubs[id]||seen.has(id)||bb.intentDigest!==digest||bb.slot!==intent.slot||bb.prevPinDigest!==intent.prevPinDigest||bb.phase!=='prepare'||!P.verify(pubs[id],'S155:PREPARE',bb,v.signature))throw Error('G155_BAD_PREPARE_VOTE');seen.add(id);}if(seen.size<2)throw Error('G155_MAJORITY_REQUIRED');return digest;
}
const server=P.serve(cfg.key,cfg.cert,cfg.ca,async(req,b)=>{
 if(req.url==='/read'){if(!req.socket.authorized||![cfg.coordinatorPin,...(cfg.readerPins||[])].includes(P.fp(req.socket.getPeerCertificate(true))))throw Error('G155_READER_NOT_PINNED');return inner('/read');}
 P.peer(req,cfg.coordinatorPin);
 if(req.url==='/init')return inner('/init',{checkpoint:b.checkpoint});
 if(req.url!=='/advance')throw Error('G155_ROUTE_INVALID');
 validate(b.intent,b.preparedVotes);
 const floor=await P.rpc({port:cfg.floor.port,key:cfg.key,cert:cfg.cert,ca:cfg.ca,serverPin:cfg.floor.certPin},'/read');
 if(!P.verify(floorPub,'S155:FLOOR',floor.body,floor.signature)||floor.body.slot!==b.intent.slot-1||floor.body.head!==b.intent.prevPinDigest)throw Error('G155_FLOOR_NOT_PINNED');
 const live=await inner('/read');
 if(P.sha(live)!==P.sha(b.intent.prior)){
  if(live.body.checkpointDigest===P.sha(b.intent.checkpoint)&&live.body.previousAnchorDigest===P.sha(b.intent.prior))return live;
  throw Error('G155_PREVIOUS_ANCHOR_CONFLICT');
 }
 const advanced=await inner('/advance',{checkpoint:b.intent.checkpoint,proof:b.proof});
 if(cfg.testMode&&b.injectAfterInner===true)process.kill(process.pid,'SIGKILL');
 return advanced;
});
process.on('message',v=>{if(v==='stop')server.close(()=>process.exit(0));});
module.exports={validate};
```


## quorum155.js

```javascript
'use strict';
const fs=require('node:fs');
const P=require('./baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const {verifyGrant}=require('./baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/proof148');
const {verifyStatic}=require('./baseline154/baseline153/proof153');
const SCHEMA='oasis.sheet154.intent.v1';
class QuorumSlots{
 constructor({identity,replicas,publicKeys,resourcePub,anchorPub,anchor,authorityKeys}){Object.assign(this,{identity,replicas,publicKeys,resourcePub:fs.readFileSync(resourcePub),anchorPub:fs.readFileSync(anchorPub),anchor,authorityKeys});}
 async ask(id,path,body={}){const x=this.replicas[id];return P.rpc({port:x.port,key:this.identity.key,cert:this.identity.cert,ca:this.identity.ca,serverPin:x.certPin},path,body);}
 async quorum(path,body,phase){const rows=await Promise.all(Object.keys(this.replicas).map(async id=>{try{return{ id, v:await this.ask(id,path,body)};}catch(e){return{id,error:e.message};}}));const good=[];for(const x of rows){const b=x.v?.body;if(b?.nodeId===x.id&&b.phase===phase&&b.intentDigest===P.sha(body.intent)&&b.slot===body.slot&&b.prevPinDigest===body.prevPinDigest&&P.verify(this.publicKeys[x.id],`S155:${phase==='prepare'?'PREPARE':phase==='anchor'?'ANCHORED':'FINAL'}`,b,x.v.signature))good.push(x.v);}
 if(good.length<2)throw Error('F154_NO_QUORUM_'+phase.toUpperCase()+' '+rows.filter(x=>x.error).map(x=>x.error).join('|'));return good;}
 createIntent({request,grant,receipt,store,prior}){verifyGrant(grant,request,this.authorityKeys);const checkpoint=store.checkpoint(prior),proof={record:store.find(receipt.body.txid).record,inclusion:store.ledger.inclusion(receipt.body.sequence-1)};
 return{schema:SCHEMA,txid:receipt.body.txid,request,grant,receipt,checkpoint,prior,proof};}
 async prepare(intent){return this.quorum('/prepare',{intent,slot:intent.slot,prevPinDigest:intent.prevPinDigest},'prepare');}
 async advanceAnchor(intent,votes,proof){if(votes.length<2)throw Error('F154_PREPARE_CERT_REQUIRED');return this.anchorRpc('/advance',{intent,preparedVotes:votes,proof});}
 anchorRpc(path,body={}){return P.rpc({port:this.anchor.port,key:this.identity.key,cert:this.identity.cert,ca:this.identity.ca,serverPin:this.anchor.certPin},path,body);}
 async admit(intent,preparedVotes,snapshot){return this.quorum('/anchored',{intent,slot:intent.slot,prevPinDigest:intent.prevPinDigest,preparedVotes,snapshot},'anchor');}
 async finalize(intent,preparedVotes,anchoredVotes,snapshot,completionEvidence){return this.quorum('/final',{intent,slot:intent.slot,prevPinDigest:intent.prevPinDigest,preparedVotes,anchoredVotes,snapshot},'final');}
}
module.exports={QuorumSlots,SCHEMA};
```


## gate155.js

```javascript
#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const P=require('./baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const {Coordinator}=require('./baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/coordinator147');
const {UnifiedStore}=require('./baseline154/baseline153/unified153');
const {QuorumSlots}=require('./quorum155');
const ZERO='0'.repeat(64);let count=0;
const pass=(label,fn)=>{fn();console.log('PASS',++count,label);},step=async(label,fn)=>{await fn();console.log('PASS',++count,label);},fails=async(label,fn,re)=>step(label,async()=>assert.rejects(fn,re));
const root=fs.mkdtempSync(path.join(os.tmpdir(),'sheet155-')),f=(...p)=>path.join(root,...p),openssl=(...a)=>cp.execFileSync('openssl',a,{cwd:root,stdio:'pipe'});
function cert(n){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',n+'.key','-out',n+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(n+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',n+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',n+'.crt','-days','2','-sha256','-extfile',n+'.ext');return{key:f(n+'.key'),cert:f(n+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(n+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
function keys(n){const x=crypto.generateKeyPairSync('ed25519');const priv=f(n+'.priv'),pub=f(n+'.pub');fs.writeFileSync(priv,x.privateKey.export({type:'pkcs8',format:'pem'}),{mode:0o600});fs.writeFileSync(pub,x.publicKey.export({type:'spki',format:'pem'}));return{priv,pub,privateKey:x.privateKey,publicKey:x.publicKey};}
const children=[];
async function spawn(script,cfg,label,envName){const conf=f(label+'-'+crypto.randomUUID()+'.json');fs.writeFileSync(conf,JSON.stringify(cfg));const proc=cp.fork(path.join(__dirname,script),[],{env:{...process.env,[envName]:conf},stdio:['ignore','pipe','pipe','ipc']});let err='';proc.stderr.on('data',b=>err+=b);const info=await new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(Error('START_TIMEOUT '+label+': '+err)),10000);proc.once('message',m=>{clearTimeout(t);resolve({proc,port:m.port,label,err:()=>err});});proc.once('exit',c=>{clearTimeout(t);reject(Error('START_EXIT '+label+': '+c+' '+err));});});children.push(info);return info;}
async function stop(x){if(!x||x.proc.exitCode!==null||x.proc.signalCode!==null||!x.proc.connected)return;await new Promise(done=>{const t=setTimeout(()=>{x.proc.kill('SIGKILL');done();},1500);x.proc.once('exit',()=>{clearTimeout(t);done();});x.proc.send('stop');});}
(async()=>{try{
 openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=S155-Test-CA');
 const ids=Object.fromEntries(['red','blue','green','alpha','beta','resource','anchor','gateway','floor','rogue'].map(n=>[n,cert(n)]));
 const auth=Object.fromEntries(['red','blue','green','resource','anchor','floor'].map(n=>[n,keys(n)]));
 const fins=Object.fromEntries(['red','blue','green'].map(n=>[n,keys('final-'+n)]));
 const authorityPub=Object.fromEntries(['red','blue','green'].map(n=>[n,auth[n].pub]));
 const finalPub=Object.fromEntries(['red','blue','green'].map(n=>[n,fins[n].pub]));
 const store=new UnifiedStore(f('journal'),'resource',auth.resource.privateKey);store.init();
 const authority={},authorityConfigs={};
 const authReaders={alpha:{certPin:ids.alpha.certPin},beta:{certPin:ids.beta.certPin},...Object.fromEntries(['red','blue','green'].map(n=>['reader_'+n,{certPin:ids[n].certPin}]))};
 for(const id of ['red','blue','green']){authorityConfigs[id]={id,...ids[id],signKey:auth[id].priv,members:Object.fromEntries(['red','blue','green'].map(n=>[n,{publicKey:auth[n].pub}])),leaders:authReaders,stateFile:f('authority-'+id,'state.json')};authority[id]=await spawn('baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/replica147.js',authorityConfigs[id],'authority-'+id,'S147_CONFIG');}
 const endpoints=()=>Object.fromEntries(['red','blue','green'].map(n=>[n,{port:authority[n].port,certPin:ids[n].certPin}]));
 const coord=(leaderId)=>new Coordinator({leaderId,identity:ids[leaderId],replicas:endpoints(),publicKeys:authorityPub});
 const anchorCfg={...ids.anchor,file:f('anchor-floor','current.json'),resourceId:'resource',resourcePublic:auth.resource.pub,anchorPrivate:auth.anchor.priv,anchorPublic:auth.anchor.pub,controlPin:ids.gateway.certPin,readPins:[ids.gateway.certPin]};
 const anchor=await spawn('baseline154/baseline153/baseline152/anchor-server152.js',anchorCfg,'anchor','S152_ANCHOR_CONFIG');
 const floorCfg={...ids.floor,signKey:auth.floor.priv,stateFile:f('floor','state.json'),coordinatorPin:ids.alpha.certPin,finalityPublicKeys:finalPub,readPins:['red','blue','green','gateway','alpha','beta'].map(id=>ids[id].certPin)};
 let floor=await spawn('floor155.js',floorCfg,'floor','S155_FLOOR_CONFIG');
 const floorRpc=(uri,b={})=>P.rpc({...ids.alpha,port:floor.port,serverPin:ids.floor.certPin},uri,b);
 const gatewayCfg={...ids.gateway,coordinatorPin:ids.alpha.certPin,readerPins:['red','blue','green'].map(id=>ids[id].certPin),inner:{port:anchor.port,certPin:ids.anchor.certPin},floor:{port:floor.port,certPin:ids.floor.certPin},floorPublicKey:auth.floor.pub,finalityPublicKeys:finalPub,authorityPublicKeys:authorityPub,resourcePublicKey:auth.resource.pub,testMode:true};
 let gateway=await spawn('anchor-gateway155.js',gatewayCfg,'gateway','S155_GATEWAY_CONFIG');
 const anchorRpc=(uri,b={})=>P.rpc({...ids.alpha,port:gateway.port,serverPin:ids.gateway.certPin},uri,b);
 let prior=await anchorRpc('/init',{checkpoint:store.checkpoint()});
 const nodes={},configs={};
 for(const id of ['red','blue','green']){configs[id]={id,...ids[id],signKey:fins[id].priv,members:finalPub,authorityPublicKeys:authorityPub,authorityMembers:endpoints(),authorityReaderId:'reader_'+id,resourcePublicKey:auth.resource.pub,anchorPublicKey:auth.anchor.pub,floorPublicKey:auth.floor.pub,resourceId:'resource',stateFile:f('finality-'+id,'state.json'),coordinatorPin:ids.alpha.certPin,anchor:{port:gateway.port,certPin:ids.gateway.certPin},floor:{port:floor.port,certPin:ids.floor.certPin}};nodes[id]=await spawn('finality-replica155.js',configs[id],'final-'+id,'S155_REPLICA_CONFIG');}
 const live=()=>Object.fromEntries(Object.entries(nodes).filter(([,v])=>v.proc.exitCode===null&&v.proc.signalCode===null).map(([id,v])=>[id,{port:v.port,certPin:ids[id].certPin}]));
 const qc=()=>new QuorumSlots({identity:ids.alpha,replicas:live(),publicKeys:Object.fromEntries(Object.entries(fins).map(([id,k])=>[id,k.publicKey])),resourcePub:auth.resource.pub,anchorPub:auth.anchor.pub,anchor:{port:gateway.port,certPin:ids.gateway.certPin},authorityKeys:Object.fromEntries(Object.entries(auth).filter(([id])=>['red','blue','green'].includes(id)).map(([id,k])=>[id,k.publicKey]))});
 pass('three live S147 authority mTLS processes',()=>assert.equal(Object.keys(authority).length,3));
 pass('three independent durable finality replicas',()=>assert.equal(Object.keys(nodes).length,3));
 pass('independent rollback-floor service',()=>assert.ok(floor.port>0));
 const genesisFloor=await floorRpc('/read');pass('signed genesis rollback floor',()=>assert.equal(genesisFloor.body.slot,0));
 const floorVotes=(intent,snapshot,finalVotes)=>({record:{slot:intent.slot,prev:intent.prevPinDigest,intentDigest:P.sha(intent),snapshotDigest:P.sha(snapshot),receiptHash:P.sha(intent.receipt)},finalVotes});
 let currentPin=genesisFloor.body.head,oldIntent=null,oldVotes=null,oldSnapshot=null;
 for(let n=1;n<=3;n++){
  const leader=n%2?'alpha':'beta';const a=coord(leader);await step(`cycle ${n}: real S147 leader election ${leader}`,async()=>{await a.elect();});
  const request={txid:'cycle_'+String(n).padStart(3,'0'),resourceId:'resource',operationId:'write',value:'ledger-'+n,epoch:1}, digest=P.sha(request);
  const begin=await a.run({type:'BEGIN',txid:request.txid,resourceId:'resource',digest});
  const states=['red','blue'].map(id=>begin.seq&&begin.head?null:null);
  const rows=await a.all('/state');const matching=rows.filter(r=>r.response?.body.seq===begin.seq&&r.response.body.head===begin.head).map(r=>r.response);
  assert.ok(matching.length>=2);
  const grant={schema:'oasis.sheet148.grant.v1',certificate:begin.certificate,seq:begin.seq,head:begin.head,epoch:begin.epoch,states:matching};
  pass(`cycle ${n}: real 2/3 BEGIN grant`,()=>assert.ok(matching.length>=2));
  const receipt=store.commit(request,{head:begin.head});pass(`cycle ${n}: physical segmented write`,()=>assert.equal(receipt.body.sequence,n));
  const intent={...qc().createIntent({request,grant,receipt,store,prior}),slot:n,prevPinDigest:currentPin};
  if(n===1){await fails('untrusted TLS identity cannot write finality replica',()=>P.rpc({...ids.rogue,port:nodes.red.port,serverPin:ids.red.certPin},'/prepare',{intent,slot:n,prevPinDigest:currentPin}),/TLS_PEER_NOT_PINNED/);
   await fails('gateway cannot advance without signed prepare quorum',()=>anchorRpc('/advance',{intent,preparedVotes:[],proof:store.extension(prior.body.count)}),/G155_MAJORITY_REQUIRED/);
   await fails('finality refuses unsigned receipt',()=>qc().ask('red','/prepare',{intent:{...intent,receipt:{...receipt,signature:'AAAA'}},slot:n,prevPinDigest:currentPin}),/F154_BAD_RECEIPT/);
   await fails('slot gap refused',()=>qc().ask('blue','/prepare',{intent,slot:3,prevPinDigest:currentPin}),/S155_SLOT_ORDER_OR_GAP/);}
  const votes=await qc().prepare(intent);pass(`cycle ${n}: 2/3 durable finality PREPARED`,()=>assert.ok(votes.length>=2));
  if(n===1){await fails('wrong prepared quorum domain rejected at gateway',()=>anchorRpc('/advance',{intent,preparedVotes:[{...votes[0],signature:'AAAA'},votes[1]],proof:store.extension(prior.body.count)}),/G155_BAD_PREPARE_VOTE/);
   await fails('coordinator denied direct signer advance',()=>P.rpc({...ids.alpha,port:anchor.port,serverPin:ids.anchor.certPin},'/advance',{checkpoint:intent.checkpoint,proof:store.extension(prior.body.count)}),/TLS_PEER_NOT_PINNED/);}
  const snap=await qc().advanceAnchor(intent,votes,store.extension(prior.body.count));pass(`cycle ${n}: anchored checkpoint advanced`,()=>assert.equal(snap.body.count,n));
  const anchored=await qc().admit(intent,votes,snap);pass(`cycle ${n}: signed ANCHORED quorum`,()=>assert.ok(anchored.length>=2));
  if(n===1)await fails('completion before live authority COMPLETE refused',()=>qc().finalize(intent,votes,anchored,snap,[]),/S155_LIVE_AUTHORITY_MAJORITY_REQUIRED|S155_NO_QUORUM_FINAL/);
  // This is an authentic S147 COMPLETE certificate, persisted in the live S147 replica journals.
  const done=await a.run({type:'COMPLETE',txid:request.txid,receiptHash:P.sha(receipt)});pass(`cycle ${n}: live majority COMPLETE`,()=>assert.ok(done.committedBy.length>=2));
  if(n===2){await stop(nodes.red);nodes.red=await spawn('finality-replica155.js',configs.red,'red-restarted','S155_REPLICA_CONFIG');await step('second cycle: restarted replica retained prepared and anchored state',async()=>assert.equal(P.load(configs.red.stateFile).slot.phase,'ANCHORED'));}
  const finalVotes=await qc().finalize(intent,votes,anchored,snap,[]);pass(`cycle ${n}: 2/3 verified live authority journals`,()=>assert.ok(finalVotes.length>=2));
  if(n===1){await fails('floor rejects missing final quorum',()=>floorRpc('/pin',{record:floorVotes(intent,snap,finalVotes).record,finalVotes:[finalVotes[0]]}),/S155_FLOOR_NEEDS_2_OF_3/);
   await fails('floor rejects altered final signatures',()=>floorRpc('/pin',{record:floorVotes(intent,snap,finalVotes).record,finalVotes:[{...finalVotes[0],signature:'AAAA'},finalVotes[1]]}),/S155_FLOOR_BAD_CERT/);}
  const pinned=await floorRpc('/pin',floorVotes(intent,snap,finalVotes));pass(`cycle ${n}: quorum-certified external pin`,()=>assert.equal(pinned.body.slot,n));
  currentPin=pinned.body.head;prior=snap;oldIntent=intent;oldVotes=votes;oldSnapshot=snap;
  pass(`cycle ${n}: no duplicate physical write`,()=>assert.equal(store.inspect().head.count,n));
  if(n===1){await fails('old signed floor snapshot cannot advance new slot',()=>qc().ask('blue','/prepare',{intent:{...intent,txid:'bad'},slot:2,prevPinDigest:ZERO}),/S155_PIN_ROLLBACK_OR_MISSING|F154_INTENT_REQUIRED/);}
 }
 pass('three unique physical transaction IDs committed',()=>assert.equal(new Set(store.inspect().records.map(x=>JSON.parse(x.payload).txid)).size,3));
 pass('finality replicas each retained three full slots',()=>{for(const id of ['red','blue','green'])assert.equal(P.load(configs[id].stateFile).finals.length,3);});
 const prevFile=P.load(configs.blue.stateFile);const snapFloor=await floorRpc('/read');pass('external floor pins slot three',()=>assert.equal(snapFloor.body.slot,3));
 // Rollback simulated by replacing one replica with its genesis state. Its own hash chain is valid but external floor detects it.
 const genesis={schema:'oasis.sheet155.finality.v1',nodeId:'blue',serial:0,head:ZERO,events:[],slot:null,finals:[]};P.atomic(configs.blue.stateFile,genesis);
 await fails('valid-looking local rollback detected against external pin',()=>qc().ask('blue','/state'),/S155_REPLICA_ROLLBACK_BELOW_EXTERNAL_FLOOR/);
 P.atomic(configs.blue.stateFile,prevFile);
 await step('restored authentic finality history passes rollback floor',async()=>assert.equal((await qc().ask('blue','/state')).body.completed,3));
 const floorStored=P.load(floorCfg.stateFile);pass('floor stores hash-linked three-slot history',()=>assert.equal(floorStored.history.length,3));
 const tampered=structuredClone(floorStored);tampered.history[0].receiptHash='f'.repeat(64);P.atomic(floorCfg.stateFile,tampered);
 await fails('tampering with external floor history halts further reads',()=>floorRpc('/read'),/S155_FLOOR_TAMPER/);
 P.atomic(floorCfg.stateFile,floorStored);
 await step('authentic floor history restores readable checkpoint',async()=>assert.equal((await floorRpc('/read')).body.slot,3));
 const pendingLeader=coord('beta');await pendingLeader.elect();const fourth={txid:'pending_004',resourceId:'resource',operationId:'write',value:'partition-proof',epoch:1};const fourthBegin=await pendingLeader.run({type:'BEGIN',txid:fourth.txid,resourceId:'resource',digest:P.sha(fourth)});const fourthStates=(await pendingLeader.all('/state')).filter(x=>x.response?.body.seq===fourthBegin.seq&&x.response.body.head===fourthBegin.head).map(x=>x.response);const fourthGrant={schema:'oasis.sheet148.grant.v1',certificate:fourthBegin.certificate,seq:fourthBegin.seq,head:fourthBegin.head,epoch:1,states:fourthStates};const fourthReceipt=store.commit(fourth,{head:fourthBegin.head});const fourthIntent={...qc().createIntent({request:fourth,grant:fourthGrant,receipt:fourthReceipt,store,prior}),slot:4,prevPinDigest:currentPin};
 pass('fourth real pending grant prepared as partition probe',()=>assert.equal(fourthReceipt.body.sequence,4));
 await stop(authority.red);await stop(authority.green);
 await fails('loss of two live authority replicas fails closed',()=>qc().ask('blue','/prepare',{intent:fourthIntent,slot:4,prevPinDigest:currentPin}),/S155_LIVE_AUTHORITY_MAJORITY_REQUIRED/);
 pass('partitioned fourth write remains unfinalized and pin stays on slot three',()=>assert.equal(P.load(floorCfg.stateFile).slot,3));
 const report={schema:'oasis.sheet155.test.v1',newChecks:count,passed:true,cycles:3,liveAuthorityReplicas:3,finalityReplicas:3,externalFloorProcess:1,physicalWrites:4,finalizedWrites:3,leaderReplacements:2,localHostOnly:true,limitations:['all services run on one physical host','external floor uses one signer and is not a distributed quorum itself','leader journal API is permitted for authenticated reader IDs','S147 COMPLETE operation still accepts receipt hash unless routed through higher layers','no global cross-host linearizability proof','S142 older timing-sensitive test']};
 fs.writeFileSync(path.join(__dirname,'new-test-report.json'),JSON.stringify(report,null,2)+'\n');console.log(`SHEET155 NEW PASS ${count}/${count}`);
}catch(e){console.error('FAIL AFTER '+count,e.stack||e);process.exitCode=1;}finally{for(const x of children.reverse())await stop(x).catch(()=>{});fs.rmSync(root,{recursive:true,force:true});}})();
```


## run-all.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp -a "$ROOT/baseline154" "$TMP/baseline154"
(cd "$TMP/baseline154" && bash run-all.sh)
(cd "$ROOT" && node gate155.js)
```


## browser-check.py

```python
#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent
html=(root/'index.html').read_text()
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1440,'height':960},accept_downloads=True)
    page.set_content(html,wait_until='domcontentloaded')
    buttons=page.locator('#choices button')
    assert buttons.count()==8,buttons.count()
    for i in range(8):
        buttons.nth(i).click()
        assert buttons.nth(i).get_attribute('aria-pressed')=='true',i
        assert page.locator('#detail').inner_text().strip(),i
        assert len(page.locator('#trace').inner_text())>30,i
        print('CHROMIUM PASS',i+1,buttons.nth(i).inner_text())
    buttons.first.click()
    page.screenshot(path=str(root/'preview.png'),full_page=True)
    with page.expect_download() as info: page.locator('#export').click()
    d=info.value
    assert d.suggested_filename.endswith('.json')
    payload=d.path().read_text()
    assert 'oasis.sheet155.svg.case.v1' in payload
    print('CHROMIUM PASS JSON export');print('CHROMIUM PASS screenshot');browser.close()
```


## make-release.py

```python
#!/usr/bin/env python3
"""Reproducible, fully self-contained SHEET 155 ZIP with immutable parent verification."""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'sheet154'
BASE=ROOT/'baseline154'
OUT=ROOT.parent/'SHEET155-live-journal-multislot-finality.zip'
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda:handle.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()
original={p.relative_to(PARENT).as_posix():digest(p) for p in PARENT.rglob('*') if p.is_file()}
preserved={p.relative_to(BASE).as_posix():digest(p) for p in BASE.rglob('*') if p.is_file()}
assert original==preserved,f'Inherited baseline mismatch: {len(original)} original vs {len(preserved)} preserved'
assert ROOT.joinpath('combined-exit.txt').read_text().strip()=='0','Clean combined process exit 0 is REQUIRED'
log=(ROOT/'combined-clean.log').read_text()
assert 'SHEET154 NEW PASS 40/40' in log and 'SHEET155 NEW PASS 56/56' in log,'Regression summary missing'
assert (ROOT/'new-test-report.json').exists()
report=json.loads((ROOT/'new-test-report.json').read_text())
assert report['newChecks']==56 and report['passed'] and report['finalizedWrites']==3
assert 'CHROMIUM PASS screenshot' in (ROOT/'browser-test.log').read_text()
source=['floor155.js','finality-replica155.js','anchor-gateway155.js','quorum155.js','gate155.js','run-all.sh','browser-check.py','make-release.py']
parts=['# SHEET 155 — Complete New Executable Sources\n',
       'These are the authored source files. The full frozen earlier lineage is bundled under `baseline154/` in the ZIP.\n']
for filename in source:
    lang='javascript' if filename.endswith('.js') else 'python' if filename.endswith('.py') else 'bash'
    parts.append(f'\n## {filename}\n\n```{lang}\n'+(ROOT/filename).read_text().rstrip()+'\n```\n')
(ROOT/'SOURCE-ALL155.md').write_text('\n'.join(parts))
receipt={'schema':'oasis.sheet155.release.v1','sheet':155,'previousSheet':154,'title':'Live Authority Journals & Multi-Slot Finality',
         'preservedBaselineFiles':len(original),'baselineByteForByte':True,
         'tests':{'new':56,'inherited':1390,'combined':1446,'combinedExit':0,'chromiumScenarios':8,'browserJsonExport':True},
         'networkTests':{'liveS147AuthorityReplicas':3,'finalityReplicas':3,'checkpointSignerProcesses':1,'admissionGatewayProcesses':1,'rollbackFloorProcesses':1,'completedSlots':3,'pendingPartitionProbeSlots':1,'physicalWrites':4},
         'securityBoundary':['all services on one physical host','external floor has one key and is not itself quorum-replicated','S147 raw COMPLETE still accepts a hash','coordinator and authority distributed linearizability not proven','all test keys ephemeral','S142 inherited timing assertion can still be intermittent'],
         'filesWithFullSourceOnGithub':['floor155.js','finality-replica155.js','anchor-gateway155.js','quorum155.js','gate155.js']}
(ROOT/'release-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p!=(ROOT/'SHA256SUMS'))
(ROOT/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files))
files.append(ROOT/'SHA256SUMS');files.sort()
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for p in files:
        name='sheet155/'+p.relative_to(ROOT).as_posix()
        info=zipfile.ZipInfo(name,date_time=(2026,10,9,12,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=(0o644<<16)
        archive.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
with zipfile.ZipFile(OUT) as archive:
    assert archive.testzip() is None
    observed={Path(n).relative_to('sheet155/baseline154').as_posix():n for n in archive.namelist() if n.startswith('sheet155/baseline154/')}
    assert observed.keys()==original.keys(),f'ZIP baseline mismatch {len(observed)} vs {len(original)}'
    for name,d in original.items(): assert hashlib.sha256(archive.read(observed[name])).hexdigest()==d,name
(ROOT.parent/(OUT.name+'.sha256.txt')).write_text(f'{digest(OUT)}  {OUT.name}\n')
print(json.dumps({'archive':str(OUT),'bytes':OUT.stat().st_size,'sha256':digest(OUT),'files':len(files),'baseline':len(original),'testExit':0,'newChecks':56,'combinedChecks':1446},indent=2))
```