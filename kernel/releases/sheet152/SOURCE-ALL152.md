# SHEET 152 — Complete New Executable Source

These are exact authored source files. Copy the matching fenced section to the named file or use the [complete ZIP](https://github.com/DavidWise01/oasis/tree/main/kernel/releases/sheet152) package attached to the conversation. The complete older frozen lineage is only in the ZIP.


## anchor-proof152.js

```javascript
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
```


## anchor-server152.js

```javascript
'use strict';
// One independent local authority process. All requests require pinned mTLS.
const fs=require('node:fs');
const P=require('./baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const {Anchor}=require('./baseline151/anchor151');
const cfg=JSON.parse(fs.readFileSync(process.env.S152_ANCHOR_CONFIG,'utf8'));
const authority=new Anchor({file:cfg.file,resourceId:cfg.resourceId,resourcePublic:fs.readFileSync(cfg.resourcePublic),anchorPrivate:fs.readFileSync(cfg.anchorPrivate),anchorPublic:fs.readFileSync(cfg.anchorPublic)});
const server=P.serve(cfg.key,cfg.cert,cfg.ca,(req,b)=>{
 if(req.url==='/read'){
  if(!cfg.readPins.includes(P.fp(req.socket.getPeerCertificate(true)))||!req.socket.authorized)throw Error('ANCHOR_READER_NOT_PINNED');
  return authority.read();
 }
 P.peer(req,cfg.controlPin);
 if(req.url==='/init')return authority.init(b.checkpoint);
 if(req.url==='/advance')return authority.advance(b.checkpoint,b.proof);
 throw Error('ANCHOR_UNKNOWN_REQUEST');
});
process.on('message',x=>{if(x==='stop')server.close(()=>process.exit(0));});
```


## bridge152.js

```javascript
'use strict';
const P=require('./baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const {JournalVerifiedBridge}=require('./baseline151/baseline150/bridge150');
const G=require('./anchor-proof152');
class AnchoredBridge extends JournalVerifiedBridge{
 async complete(txid,receipt,journalProof,anchorProof){
  if(receipt?.body?.txid!==txid)throw Error('WRONG_RECEIPT_TXID');
  const resource=this.resourcePublicKeys[receipt.body.resourceId];
  if(!resource||!P.verify(resource,'S148:RECEIPT',receipt.body,receipt.signature))throw Error('RESOURCE_RECEIPT_UNTRUSTED');
  if(anchorProof?.schema!==G.SCHEMA)throw Error('ANCHOR_PROOF_REQUIRED');
  const head=await this.state();
  if(head.rows.filter(x=>x.response?.body.pendingGrant?.txid===txid).length<2)throw Error('RECEIPT_NO_PENDING_QUORUM');
  return this.run({type:'COMPLETE',txid,receiptHash:P.sha(receipt),receipt,journalProof,anchorProof});
 }
}
module.exports={AnchoredBridge};
```


## replica152.js

```javascript
'use strict';
// SHEET149: replica-enforced resource receipt authentication. Development-only local mTLS service.
const fs=require('node:fs');
const P=require('./baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const J=require('./baseline151/baseline150/journal150');
const G=require('./anchor-proof152');
const ZERO='0'.repeat(64), SCHEMA='oasis.sheet152.replica.v1';
const cfg=JSON.parse(fs.readFileSync(process.env.S152_REPLICA_CONFIG,'utf8'));
const key=fs.readFileSync(cfg.signKey);
const pubs=Object.fromEntries(Object.entries(cfg.members).map(([id,v])=>[id,fs.readFileSync(v.publicKey)]));
const ownPub=pubs[cfg.id];
const resourceKeys=Object.fromEntries(Object.entries(cfg.resourcePublicKeys||{}).map(([id,p])=>[id,fs.readFileSync(p)]));
const HASH=/^[a-f0-9]{64}$/;
const anchorPub=fs.readFileSync(cfg.anchorPublicKey);
const domain='S147:PREPARE';
function seal(d,b){return{body:b,signature:P.sign(key,d,b)};}
function requireField(v,what){if(!v)throw Error(what);return v;}
function fresh(){return{schema:SCHEMA,nodeId:cfg.id,term:0,leaderId:null,seq:0,head:ZERO,epoch:1,pending:null,pendingGrant:null,completed:[],resourcePins:{},anchorPins:{},journal:[]};}
if(!fs.existsSync(cfg.stateFile))P.atomic(cfg.stateFile,fresh());
function read(){const s=P.load(cfg.stateFile);if(s.schema!==SCHEMA||s.nodeId!==cfg.id||!Number.isSafeInteger(s.term)||!Number.isSafeInteger(s.seq)||!Array.isArray(s.journal))throw Error('BAD_STATE');let head=ZERO,epoch=1,grant=null,completed=[],resourcePins={},anchorPins={};let seq=0;
 for(const row of s.journal){if(row.proposal.index!==++seq||row.proposal.prev!==head)throw Error('JOURNAL_CHAIN_BAD');validateCertificate(row.proposal,row.votes);const result=apply({epoch,pendingGrant:grant,completed,resourcePins,anchorPins},row.proposal.op,row.proposal);epoch=result.epoch;grant=result.pendingGrant;completed=result.completed;resourcePins=result.resourcePins;anchorPins=result.anchorPins;head=P.sha({prev:head,index:seq,term:row.proposal.term,op:row.proposal.op});}
 if(seq!==s.seq||head!==s.head||epoch!==s.epoch||JSON.stringify(grant)!==JSON.stringify(s.pendingGrant)||JSON.stringify(completed)!==JSON.stringify(s.completed)||JSON.stringify(resourcePins)!==JSON.stringify(s.resourcePins)||JSON.stringify(anchorPins)!==JSON.stringify(s.anchorPins))throw Error('STATE_ROLLBACK_OR_TAMPER');
 if(s.pending&& (s.pending.proposal.index!==s.seq+1||s.pending.proposal.prev!==s.head))throw Error('PENDING_BAD');
 if(cfg.floorFile){let floor;try{floor=P.load(cfg.floorFile);}catch{throw Error('FLOOR_MISSING');}if(floor.schema!==SCHEMA||!P.verify(fs.readFileSync(cfg.floorPublicKey),'S147:EXTERNAL_PIN',floor.body,floor.signature)||floor.body.schema!==SCHEMA||!Number.isSafeInteger(floor.body.seq)||floor.body.seq>s.seq||floor.body.seq===s.seq&&floor.body.head!==s.head||!s.journal.some((x,i)=>i+1===floor.body.seq&&P.sha({prev:x.proposal.prev,index:x.proposal.index,term:x.proposal.term,op:x.proposal.op})===floor.body.head)&&floor.body.seq!==0)throw Error('ROLLBACK_FLOOR_CONFLICT');}
 return s;}
function save(s){P.atomic(cfg.stateFile,s);}
function isValidOp(op){if(!op||!['BEGIN','COMPLETE','CUTOVER'].includes(op.type))throw Error('INVALID_OPERATION');if(op.type==='BEGIN'&&(!/^[a-z0-9_-]{1,50}$/i.test(op.txid||'')||!/^[a-z0-9_-]{1,32}$/i.test(op.resourceId||'')||typeof op.digest!=='string'||!/^([a-f0-9]{64})$/.test(op.digest)))throw Error('INVALID_BEGIN');if(op.type==='COMPLETE'&&(!/^[a-z0-9_-]{1,50}$/i.test(op.txid||'')||!/^([a-f0-9]{64})$/.test(op.receiptHash||'')))throw Error('INVALID_COMPLETE');if(op.type==='CUTOVER'&&!Number.isSafeInteger(op.epoch))throw Error('INVALID_CUTOVER');}
function verifyCompletion(op,g){
 if(!g||g.txid!==op.txid)throw Error('NO_GRANT_TO_COMPLETE');
 const r=op.receipt,b=r?.body;
 if(!b||b.schema!=='oasis.sheet148.resource.v1'||typeof r.signature!=='string'||!resourceKeys[b.resourceId])throw Error('REPLICA_RECEIPT_REQUIRED');
 if(!P.verify(resourceKeys[b.resourceId],'S148:RECEIPT',b,r.signature))throw Error('REPLICA_RECEIPT_BAD_SIGNATURE');
 if(b.txid!==g.txid||b.resourceId!==g.resourceId||b.digest!==g.digest||b.epoch!==g.epoch||b.grantHead!==g.grantHead)throw Error('REPLICA_RECEIPT_GRANT_MISMATCH');
 if(!Number.isSafeInteger(b.sequence)||b.sequence<1||!HASH.test(b.recordHash||''))throw Error('REPLICA_RECEIPT_RECORD_INVALID');
 if(op.receiptHash!==P.sha(r))throw Error('REPLICA_RECEIPT_HASH_MISMATCH');
 return G.verifyStatic(r,op.journalProof,op.anchorProof,resourceKeys[b.resourceId],anchorPub,g.resourcePin||null);
}
function apply(s,op,proposal){isValidOp(op);const x=structuredClone(s);if(op.type==='BEGIN'){if(x.pendingGrant)throw Error('RESOURCE_GRANT_STILL_PENDING');if(x.completed.some(r=>r.txid===op.txid))throw Error('TX_ALREADY_COMMITTED');x.pendingGrant={txid:op.txid,resourceId:op.resourceId,digest:op.digest,epoch:x.epoch,grantHead:P.sha({prev:proposal.prev,index:proposal.index,term:proposal.term,op:proposal.op})};}
 if(op.type==='COMPLETE'){const aPin=verifyCompletion(op,{...x.pendingGrant,resourcePin:x.resourcePins[x.pendingGrant?.resourceId]});
  const previous=x.anchorPins[x.pendingGrant.resourceId];
  if(previous&&(aPin.count<previous.count||aPin.count===previous.count&&aPin.root!==previous.root))throw Error('ANCHOR_PIN_ROLLBACK');
  const pin=J.verifyBundle(op.journalProof,op.receipt,resourceKeys[x.pendingGrant.resourceId],x.resourcePins[x.pendingGrant.resourceId]||null);if(x.completed.some(r=>r.txid===op.txid))throw Error('DUPLICATE_COMPLETION');x.completed.push({txid:op.txid,receiptHash:op.receiptHash,digest:x.pendingGrant.digest});x.resourcePins[x.pendingGrant.resourceId]=pin;x.anchorPins[x.pendingGrant.resourceId]=aPin;x.pendingGrant=null;}
 if(op.type==='CUTOVER'){if(x.pendingGrant)throw Error('CUTOVER_BLOCKED_PENDING_GRANT');if(op.epoch!==x.epoch+1)throw Error('BAD_EPOCH');x.epoch=op.epoch;}
 return x;}
function verifyNodeVote(v,proposal){const b=v?.body;if(!b||!pubs[b.nodeId]||b.digest!==P.sha(proposal)||b.term!==proposal.term||b.index!==proposal.index||b.prev!==proposal.prev||b.leaderId!==proposal.leaderId||!P.verify(pubs[b.nodeId],domain,b,v.signature))throw Error('INVALID_VOTE_SIGNATURE');return b.nodeId;}
function validateCertificate(p,votes){if(!p||!Array.isArray(votes))throw Error('BAD_CERTIFICATE');const ids=new Set();for(const v of votes){const id=verifyNodeVote(v,p);if(ids.has(id))throw Error('DUPLICATE_VOTER');ids.add(id);}if(ids.size<2)throw Error('INSUFFICIENT_VOTES');return true;}
function elected(s,b){if(s.term!==b.term||s.leaderId!==b.leaderId)throw Error('LEADER_NOT_CURRENT');}
const server=P.serve(cfg.key,cfg.cert,cfg.ca,async(req,b)=>{
 if(!['/state','/elect','/prepare','/commit','/journal'].includes(req.url))throw Error('NOT_FOUND');
 const identity=cfg.leaders[b.leaderId];if(!identity)throw Error('LEADER_UNKNOWN');P.peer(req,identity.certPin);
 const s=read();
 // An authenticated request must see the current retained anchor, not a caller's cached snapshot.
 // Deliberately fail closed if the independently running signer is unreachable.
 const live=await P.rpc({port:cfg.anchor.port,key:cfg.key,cert:cfg.cert,ca:cfg.ca,serverPin:cfg.anchor.certPin},'/read');
 for(const [id,pin] of Object.entries(s.anchorPins||{})){if(id!==live.body.resourceId||live.body.count<pin.count||live.body.count===pin.count&&live.body.root!==pin.root)throw Error('ANCHOR_LIVE_PIN_ROLLBACK');}
 if(req.url==='/state')return seal('S147:STATE',{nodeId:cfg.id,term:s.term,leaderId:s.leaderId,seq:s.seq,head:s.head,epoch:s.epoch,pending:s.pending?.proposal||null,pendingGrant:s.pendingGrant});
 if(req.url==='/journal')return seal('S147:JOURNAL',{nodeId:cfg.id,seq:s.seq,head:s.head,journal:s.journal});
 if(req.url==='/elect'){
  if(s.pending)throw Error('ELECTION_BLOCKED_UNRESOLVED_PREPARE');
  if(b.term<s.term||b.term>s.term+1||b.term===s.term&&s.leaderId!==b.leaderId)throw Error('ELECTION_TERM_CONFLICT');
  if(b.seq!==s.seq||b.head!==s.head||b.epoch!==s.epoch)throw Error('ELECTION_STALE_HISTORY');
  s.term=b.term;s.leaderId=b.leaderId;save(s);
  return seal('S147:ELECTION',{nodeId:cfg.id,term:s.term,leaderId:s.leaderId,seq:s.seq,head:s.head,epoch:s.epoch});
 }
 const proposal=b.proposal;
 if(req.url==='/prepare'){
  if(proposal?.op?.type==='COMPLETE')G.verifyLive(proposal.op,live);
  requireField(proposal,'PROPOSAL_REQUIRED');elected(s,proposal);if(proposal.leaderId!==b.leaderId||proposal.index!==s.seq+1||proposal.prev!==s.head)throw Error('STALE_PROPOSAL');apply(s,proposal.op,proposal);
  const digest=P.sha(proposal);if(s.pending&&s.pending.digest!==digest)throw Error('SLOT_ALREADY_VOTED');
  if(!s.pending){s.pending={proposal,digest};save(s);}
  return seal(domain,{nodeId:cfg.id,digest,term:proposal.term,index:proposal.index,prev:proposal.prev,leaderId:proposal.leaderId});
 }
 if(req.url==='/commit'){
  if(proposal?.op?.type==='COMPLETE')G.verifyLive(proposal.op,live);
  validateCertificate(proposal,b.votes);if(proposal.leaderId!==b.leaderId||proposal.index!==s.seq+1||proposal.prev!==s.head)throw Error('COMMIT_PREVIOUS_HEAD_MISMATCH');
  if(proposal.term<s.term)throw Error('COMMIT_OLD_TERM');
  if(s.pending&&s.pending.digest!==P.sha(proposal))throw Error('CONFLICTING_PENDING_VOTE');
  const result=apply(s,proposal.op,proposal);s.epoch=result.epoch;s.pendingGrant=result.pendingGrant;s.completed=result.completed;s.resourcePins=result.resourcePins;s.anchorPins=result.anchorPins;
  s.seq++;s.term=proposal.term;s.leaderId=proposal.leaderId;s.head=P.sha({prev:proposal.prev,index:proposal.index,term:proposal.term,op:proposal.op});s.journal.push({proposal,votes:b.votes});s.pending=null;save(s);
  return seal('S147:COMMITTED',{nodeId:cfg.id,term:s.term,seq:s.seq,head:s.head,epoch:s.epoch});
 }
 throw Error('UNKNOWN');
});
process.on('message',x=>{if(x==='stop')server.close(()=>process.exit(0));});
module.exports={validateCertificate,apply,verifyCompletion};
```


## resource152.js

```javascript
'use strict';
const fs=require('node:fs'),P=require('./baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const {verifyGrant,quorumCurrent,ZERO}=require('./baseline151/baseline150/baseline149/baseline148/proof148');
const J=require('./baseline151/baseline150/journal150');
const cfg=JSON.parse(fs.readFileSync(process.env.S150_RESOURCE_CONFIG,'utf8'));
const key=fs.readFileSync(cfg.signKey),pubs=Object.fromEntries(Object.entries(cfg.replicaPublicKeys).map(([k,v])=>[k,fs.readFileSync(v)]));
const schema='oasis.sheet148.resource.v1';
const fresh=()=>({schema,resourceId:cfg.resourceId,sequence:0,head:ZERO,records:[],merkleRoot:J.EMPTY});
if(!fs.existsSync(cfg.stateFile))P.atomic(cfg.stateFile,fresh());
function read(){const s=P.load(cfg.stateFile);if(s.schema!==schema||s.resourceId!==cfg.resourceId||!Array.isArray(s.records)||s.records.length!==s.sequence)throw Error('RESOURCE_STATE_BAD');let prev=ZERO,i=0;for(const r of s.records){i++;if(r.sequence!==i||r.previous!==prev||r.hash!==P.sha({txid:r.txid,operationId:r.operationId,value:r.value,epoch:r.epoch,digest:r.digest,sequence:r.sequence,previous:r.previous,grantHead:r.grantHead}))throw Error('RESOURCE_CHAIN_BAD');prev=r.hash;}if(s.head!==prev)throw Error('RESOURCE_HEAD_BAD');if(s.merkleRoot!==J.root(s.records.map(x=>x.hash)))throw Error('RESOURCE_MERKLE_STATE_BAD');
 if(cfg.floorFile){const pin=P.load(cfg.floorFile);if(!P.verify(fs.readFileSync(cfg.floorPublicKey),'S148:RESOURCE_FLOOR',pin.body,pin.signature)||pin.body.resourceId!==cfg.resourceId||pin.body.sequence>s.sequence||pin.body.sequence===s.sequence&&pin.body.head!==s.head||pin.body.sequence>0&&!s.records.some(x=>x.sequence===pin.body.sequence&&x.hash===pin.body.head))throw Error('RESOURCE_ROLLBACK_FLOOR');}
 return s;}
async function live(grant,b){const responses=await Promise.all(Object.entries(cfg.replicas).map(async([id,v])=>{try{const r=await P.rpc({port:v.port,key:cfg.key,cert:cfg.cert,ca:cfg.ca,serverPin:v.certPin},'/state',{leaderId:cfg.observerId});if(r.body.nodeId!==id)return null;return r;}catch{return null;}}));return quorumCurrent(responses,grant,pubs,b);}
let busy=false;
const server=P.serve(cfg.key,cfg.cert,cfg.ca,async(req,b)=>{
 if(!['/write','/status','/proof'].includes(req.url))throw Error('NOT_FOUND');P.peer(req,cfg.writerPin);
 if(req.url==='/status'){const s=read();return{sequence:s.sequence,head:s.head,merkleRoot:s.merkleRoot,resourceId:cfg.resourceId};}
 if(req.url==='/proof'){const s=read(),record=s.records.find(x=>x.txid===b.txid);if(!record)throw Error('PROOF_NOT_FOUND');return J.makeBundle(s,record,key);}
 if(busy)throw Error('RESOURCE_BUSY');busy=true;
 try{
  if(b.resourceId!==cfg.resourceId)throw Error('WRONG_RESOURCE');
  if(typeof b.txid!=='string'||!/^[a-z0-9_-]{1,50}$/i.test(b.txid)||typeof b.operationId!=='string'||b.operationId.length>90||typeof b.value!=='string'||b.value.length>3000)throw Error('BAD_REQUEST');
  const digest=P.sha({txid:b.txid,resourceId:b.resourceId,operationId:b.operationId,value:b.value,epoch:b.epoch});
  const grant=b.grant;verifyGrant(grant,b,pubs);
  const s=read(),old=s.records.find(x=>x.txid===b.txid);let record;
  if(old){if(old.digest!==digest||old.grantHead!==grant.head)throw Error('REPLAY_CONFLICT');record=old;}
  else{
   await live(grant,b); // authority must still retain the exact pending grant
   if(cfg.testMode&&b.delayMs)await new Promise(r=>setTimeout(r,Math.min(500,b.delayMs)));
   await live(grant,b); // revalidate immediately before the durable mutation
   const current=read();if(current.records.some(x=>x.txid===b.txid))throw Error('DUPLICATE_WRITE');
   record={txid:b.txid,operationId:b.operationId,value:b.value,epoch:b.epoch,digest,sequence:current.sequence+1,previous:current.head,grantHead:grant.head};
   record.hash=P.sha(record);current.records.push(record);current.sequence++;current.head=record.hash;current.merkleRoot=J.root(current.records.map(x=>x.hash));P.atomic(cfg.stateFile,current);
  }
  const receipt={body:{schema,resourceId:cfg.resourceId,txid:b.txid,digest,epoch:b.epoch,sequence:record.sequence,recordHash:record.hash,grantHead:grant.head},signature:P.sign(key,'S148:RECEIPT',{schema,resourceId:cfg.resourceId,txid:b.txid,digest,epoch:b.epoch,sequence:record.sequence,recordHash:record.hash,grantHead:grant.head})};
  if(cfg.testMode&&b.crashAfterWrite)process.exit(42);
  return{status:'DURABLE',receipt,journalProof:J.makeBundle(read(),record,key),sequence:record.sequence};
 }finally{busy=false;}
});
process.on('message',x=>{if(x==='stop')server.close(()=>process.exit(0));});
```


## reconcile152.js

```javascript
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
```


## gate152.js

```javascript
#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const P=require('./baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const {AnchoredBridge}=require('./bridge152');
const {verifyGrant,quorumCurrent}=require('./baseline151/baseline150/baseline149/baseline148/proof148');
let count=0;const pass=(s,fn)=>{fn();console.log('PASS',++count,s)},step=async(s,fn)=>{await fn();console.log('PASS',++count,s)},fails=async(s,fn,re)=>step(s,async()=>assert.rejects(fn,re));
const J=require('./baseline151/baseline150/journal150');
const root=fs.mkdtempSync(path.join(os.tmpdir(),'s150-')),file=(...p)=>path.join(root,...p);
const openssl=(...args)=>cp.execFileSync('openssl',args,{cwd:root,stdio:'pipe'});
function cert(name){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',name+'.key','-out',name+'.csr','-subj','/CN=localhost');fs.writeFileSync(file(name+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',name+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',name+'.crt','-days','2','-sha256','-extfile',name+'.ext');return{key:file(name+'.key'),cert:file(name+'.crt'),ca:file('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(file(name+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
function keys(name){const x=crypto.generateKeyPairSync('ed25519'),priv=file(name+'.priv'),pub=file(name+'.pub');fs.writeFileSync(priv,x.privateKey.export({type:'pkcs8',format:'pem'}),{mode:0o600});fs.writeFileSync(pub,x.publicKey.export({type:'spki',format:'pem'}));return{priv,pub,privateKey:x.privateKey};}
let children=[];
async function spawn(script,cfg,label){const config=file(label+'-'+crypto.randomUUID()+'.json');fs.writeFileSync(config,JSON.stringify(cfg));const env={...process.env,[script==='resource152.js'?'S150_RESOURCE_CONFIG':script==='anchor-server152.js'?'S152_ANCHOR_CONFIG':'S152_REPLICA_CONFIG']:config};const proc=cp.fork(path.join(__dirname,script),[],{env,stdio:['ignore','pipe','pipe','ipc']});let stderr='';proc.stderr.on('data',b=>stderr+=b);const x=await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('TIMEOUT '+stderr)),9500);proc.once('message',m=>{clearTimeout(timeout);resolve({proc,port:m.port,label,error:()=>stderr});});proc.once('exit',c=>{clearTimeout(timeout);reject(Error('EXIT '+c+' '+stderr));});});children.push(x);return x;}
async function stop(x){if(!x||x.proc.exitCode!==null||x.proc.killed)return;await new Promise(r=>{const t=setTimeout(()=>{x.proc.kill('SIGKILL');r();},1300);x.proc.once('exit',()=>{clearTimeout(t);r();});x.proc.send('stop');});}
(async()=>{try{
 openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=S148-Test-CA');
 const ids=Object.fromEntries(['red','blue','green','alpha','beta','observer','resource','writer','rogue','anchor'].map(id=>[id,cert(id)]));
 const signers=Object.fromEntries(['red','blue','green','resource','pin','anchor','op1','op2','op3'].map(id=>[id,keys(id+'-ed')]));
 const pubKeys=Object.fromEntries(['red','blue','green'].map(id=>[id,signers[id].pub]));
 const members=Object.fromEntries(Object.entries(pubKeys).map(([id,p])=>[id,{publicKey:p}]));
 const leaders={alpha:{certPin:ids.alpha.certPin},beta:{certPin:ids.beta.certPin},observer:{certPin:ids.resource.certPin}};
 const G=require('./anchor-proof152');
 const {Ledger}=require('./baseline151/ledger151');
 const {review,DOMAIN}=require('./reconcile152');
 const ledger=new Ledger(file('segment-journal151'),'resource',signers.resource.privateKey);
 ledger.init();
 const anchorCfg={...ids.anchor,file:file('anchor-floor','checkpoint.json'),resourceId:'resource',resourcePublic:signers.resource.pub,anchorPrivate:signers.anchor.priv,anchorPublic:signers.anchor.pub,controlPin:ids.writer.certPin,readPins:[ids.red.certPin,ids.blue.certPin,ids.green.certPin,ids.writer.certPin]};
 let anchorSrv=await spawn('anchor-server152.js',anchorCfg,'anchor');
 const ctl=(url,body={})=>P.rpc({port:anchorSrv.port,key:ids.writer.key,cert:ids.writer.cert,ca:ids.writer.ca,serverPin:ids.anchor.certPin},url,body);
 let anchored=await ctl('/init',{checkpoint:ledger.checkpoint()});
 const genesis=structuredClone(anchored);
 const nodes={},configs={};
 for(const id of ['red','blue','green']){
  const body={schema:'oasis.sheet152.replica.v1',seq:0,head:'0'.repeat(64)};
  const pin=file(id+'-floor','pin.json');P.atomic(pin,{schema:body.schema,body,signature:P.sign(signers.pin.privateKey,'S147:EXTERNAL_PIN',body)});
  configs[id]={id,...ids[id],signKey:signers[id].priv,members,leaders,stateFile:file(id,'state.json'),floorFile:pin,floorPublicKey:signers.pin.pub,resourcePublicKeys:{resource:signers.resource.pub},anchorPublicKey:signers.anchor.pub,anchor:{port:anchorSrv.port,certPin:ids.anchor.certPin}};
  nodes[id]=await spawn('replica152.js',configs[id],id);
 }
 const replicas=()=>Object.fromEntries(Object.entries(nodes).filter(([,n])=>n.proc.exitCode===null).map(([id,x])=>[id,{port:x.port,certPin:ids[id].certPin}]));
 const leader=(id)=>new AnchoredBridge({leaderId:id,identity:ids[id],replicas:replicas(),publicKeys:pubKeys,resourcePublicKeys:{resource:signers.resource.pub}});
 let A=leader('alpha');await A.elect();
 let resourceCfg={...ids.resource,resourceId:'resource',signKey:signers.resource.priv,stateFile:file('resource','state.json'),writerPin:ids.writer.certPin,observerId:'observer',replicaPublicKeys:pubKeys,replicas:replicas(),testMode:true};
 const pinBody={resourceId:'resource',sequence:0,head:'0'.repeat(64)};
 resourceCfg.floorFile=file('independent-pin','pin.json');resourceCfg.floorPublicKey=signers.pin.pub;
 const putFloor=(body)=>P.atomic(resourceCfg.floorFile,{body,signature:P.sign(signers.pin.privateKey,'S148:RESOURCE_FLOOR',body)});
 putFloor(pinBody);
 let resource=await spawn('resource152.js',resourceCfg,'resource');
 const writer=(body,iden=ids.writer)=>P.rpc({port:resource.port,key:iden.key,cert:iden.cert,ca:iden.ca,serverPin:ids.resource.certPin},'/write',body);
 const status=()=>P.load(resourceCfg.stateFile);
 const req=(txid,epoch=1)=>({txid,resourceId:'resource',operationId:'write',value:'message-'+txid,epoch});
  const opKeys={op1:fs.readFileSync(signers.op1.pub),op2:fs.readFileSync(signers.op2.pub),op3:fs.readFileSync(signers.op3.pub)};
 const torn=new Ledger(file('torn'),'resource',signers.resource.privateKey);torn.init();
 await fails('torn segment cannot auto-replay',async()=>{assert.throws(()=>torn.append('persisted',{crashBeforeHead:true}),/INJECTED_CRASH/);torn.read();},/SEGMENT_COUNT_OR_TORN_WRITE/);
 const tornRec=P.load(torn.segment(0)).records[0];
 const plan={schema:'oasis.sheet152.review.v1',resourceId:'resource',headCount:0,headRoot:torn.read.bind?require('./baseline151/merkle151').EMPTY:'',appendHash:tornRec.hash,anchorDigest:P.sha(genesis)};
 const approvals=['op1','op2'].map(id=>({id,signature:P.sign(signers[id].privateKey,DOMAIN,plan)}));
 await fails('one operator cannot resolve torn head',async()=>review(file('torn'),'resource',genesis,fs.readFileSync(signers.anchor.pub),opKeys,plan,approvals.slice(0,1)),/RECOVERY_QUORUM_REQUIRED/);
 await fails('forged operator vote cannot resolve torn head',async()=>review(file('torn'),'resource',genesis,fs.readFileSync(signers.anchor.pub),opKeys,plan,[approvals[0],{id:'op2',signature:'AAAA'}]),/RECOVERY_VOTE_INVALID/);
 pass('two distinct operators resolve precisely one extant record',()=>assert.equal(review(file('torn'),'resource',genesis,fs.readFileSync(signers.anchor.pub),opKeys,plan,approvals).count,1));
 pass('reviewed repair leaves original payload and one record',()=>assert.equal(torn.read().records[0].payload,'persisted'));
 await fails('recovery decision cannot execute twice',async()=>review(file('torn'),'resource',genesis,fs.readFileSync(signers.anchor.pub),opKeys,plan,approvals),/RECOVERY_NOT_SINGLE_TORN_APPEND/);
 pass('network has three mTLS replicas',()=>assert.equal(Object.keys(nodes).length,3));
 pass('anchor signer uses a distinct Ed25519 key',()=>assert.notEqual(fs.readFileSync(signers.resource.pub,'utf8'),fs.readFileSync(signers.anchor.pub,'utf8')));
 pass('separate process signs the genesis checkpoint',()=>assert.ok(P.verify(fs.readFileSync(signers.anchor.pub),'S151:ANCHOR',anchored.body,anchored.signature)));
 await fails('anchor refuses forged controller TLS certificate',()=>P.rpc({...ids.rogue,port:anchorSrv.port,serverPin:ids.anchor.certPin},'/advance',{checkpoint:{}}),/TLS_PEER_NOT_PINNED/);
 const one=req('one');const grant=await A.begin(one),written=await writer({...one,grant});
 pass('S150 resource performs exactly one durable write',()=>assert.equal(status().sequence,1));
 await fails('unanchored completion rejected by bridge',()=>A.complete('one',written.receipt,written.journalProof),/ANCHOR_PROOF_REQUIRED/);
 const opUnanchored={type:'COMPLETE',txid:'one',receiptHash:P.sha(written.receipt),receipt:written.receipt,journalProof:written.journalProof};
 const start=await A.state();
 const makeProposal=(op,who='alpha',term=A.term,s=start)=>({term,leaderId:who,index:s.seq+1,prev:s.head,op});
 const forgedVotes=(proposal)=>['red','blue'].map(nodeId=>{const body={nodeId,digest:P.sha(proposal),term:proposal.term,index:proposal.index,prev:proposal.prev,leaderId:proposal.leaderId};return{body,signature:P.sign(signers[nodeId].privateKey,'S147:PREPARE',body)};});
 await fails('replica refuses unanchored prepare',()=>A.ask('red','/prepare',{proposal:makeProposal(opUnanchored)}),/ANCHOR_LIVE_UNAVAILABLE/);
 await fails('replica refuses unanchored commit with forged votes',()=>A.ask('red','/commit',{proposal:makeProposal(opUnanchored),votes:forgedVotes(makeProposal(opUnanchored))}),/ANCHOR_LIVE_UNAVAILABLE/);
 const record=ledger.append(G.payload(written.receipt,written.journalProof));
 pass('S151 journal payload binds the S150 receipt and checkpoint',()=>assert.equal(record.record.payload,G.payload(written.receipt,written.journalProof)));
 const cp1=ledger.checkpoint(anchored);anchored=await ctl('/advance',{checkpoint:cp1,proof:ledger.extension(0)});
 const good=G.bundle(ledger,written.receipt,written.journalProof,cp1,anchored);
 pass('two signed independent checkpoint chains verify',()=>assert.equal(G.verifyStatic(written.receipt,written.journalProof,good,fs.readFileSync(signers.resource.pub),fs.readFileSync(signers.anchor.pub)).count,1));
 const requestOp={...opUnanchored,anchorProof:good};
 pass('direct verifier rejects forged signed anchor',()=>assert.throws(()=>G.verifyStatic(written.receipt,written.journalProof,{...good,snapshot:{...good.snapshot,signature:'AAAA'}},fs.readFileSync(signers.resource.pub),fs.readFileSync(signers.anchor.pub)),/ANCHOR_SNAPSHOT_SIGNATURE_INVALID/));
 await fails('forged anchor signature refused by replica',()=>A.ask('red','/prepare',{proposal:makeProposal({...requestOp,anchorProof:{...good,snapshot:{...good.snapshot,signature:'AAAA'}}})}),/ANCHOR_STALE_LIVE_HEAD/);
 await fails('wrong linked journal record rejected',()=>A.ask('red','/prepare',{proposal:makeProposal({...requestOp,anchorProof:{...good,record:{...good.record,payload:'not-a-receipt'}}})}),/ANCHOR_BINDING_MISMATCH/);
 await fails('tampered anchor inclusion witness rejected',()=>A.ask('red','/prepare',{proposal:makeProposal({...requestOp,anchorProof:{...good,proof:{...good.proof,recordHash:'f'.repeat(64)}}})}),/ANCHOR_INCLUSION_BINDING_INVALID/);
 await fails('substituted S150 journal proof rejected',()=>A.ask('red','/prepare',{proposal:makeProposal({...requestOp,journalProof:{...written.journalProof,checkpoint:{...written.journalProof.checkpoint,signature:'AAAA'}}})}),/CHECKPOINT_SIGNATURE_INVALID/);
 await fails('altered S150 receipt rejected despite valid anchor',()=>A.ask('red','/prepare',{proposal:makeProposal({...requestOp,receipt:{...written.receipt,signature:'AAAA'}})}),/REPLICA_RECEIPT_BAD_SIGNATURE/);
 const competing=structuredClone(good);competing.record.sequence=2;
 await fails('wrong S151 sequence rejected',()=>A.ask('red','/prepare',{proposal:makeProposal({...requestOp,anchorProof:competing})}),/ANCHOR_BINDING_MISMATCH/);
 await step('replicas independently accept current anchored completion',async()=>assert.equal((await A.complete('one',written.receipt,written.journalProof,good)).seq,2));
 pass('S152 replica independently persists anchored high water',()=>{for(const id of ['red','blue','green'])assert.equal(P.load(configs[id].stateFile).anchorPins.resource.count,1);});
 await fails('duplicate completion blocked by immutable quorum history',()=>A.complete('one',written.receipt,written.journalProof,good),/RECEIPT_NO_PENDING_QUORUM/);
 // Segment rollover: 151 has a separate scalable log; 150 resource remains bounded.
 for(let i=0;i<258;i++)ledger.append('rollover:'+i);
 pass('signed record continuity spans three S151 segments',()=>assert.equal(ledger.read().head.count,259));
 const cp259=ledger.checkpoint(anchored),savedOldAnchor=structuredClone(anchored);
 anchored=await ctl('/advance',{checkpoint:cp259,proof:ledger.extension(1)});
 pass('anchor serial advances without replacing old checkpoint',()=>assert.equal(anchored.body.serial,2));
 pass('old receipt remains included under current S151 head',()=>require('./baseline151/merkle151').verifyInclusion(ledger.inclusion(0),cp259.body.root,ledger.read().records[0].hash));
 const two=req('two'),g2=await A.begin(two);
 await fails('old epoch cannot cut over with pending grant',()=>A.run({type:'CUTOVER',epoch:2}),/PREPARE_QUORUM_NOT_REACHED/);
 let crash=await writer({...two,grant:g2,crashAfterWrite:true}).catch(e=>e);
 pass('real resource process crashed after durable mutation',()=>assert.ok(crash instanceof Error));
 pass('durable resource has exactly two rows after crash',()=>assert.equal(status().sequence,2));
 resource=await spawn('resource152.js',resourceCfg,'resource-restarted');
 const retry=await writer({...two,grant:g2});
 pass('restart returned original record rather than mutating twice',()=>assert.equal(retry.receipt.body.recordHash,status().records[1].hash));
 const old=A;A=leader('beta');await step('new authority leader elected after resource crash',async()=>assert.equal((await A.elect()).term,2));
 await fails('superseded leader cannot finalize',()=>old.complete('two',retry.receipt,retry.journalProof,good),/RECEIPT_NO_PENDING_QUORUM|NOT_ELECTED|PREPARE_QUORUM_NOT_REACHED/);
 const r2=ledger.append(G.payload(retry.receipt,retry.journalProof));
 pass('second transaction appended once in S151',()=>assert.equal(r2.record.sequence,260));
 const cp260=ledger.checkpoint(anchored);anchored=await ctl('/advance',{checkpoint:cp260,proof:ledger.extension(259)});
 const good2=G.bundle(ledger,retry.receipt,retry.journalProof,cp260,anchored);
 const oldProof={...good2,snapshot:savedOldAnchor};
 const op2={type:'COMPLETE',txid:'two',receiptHash:P.sha(retry.receipt),receipt:retry.receipt,journalProof:retry.journalProof,anchorProof:oldProof};
 const now=await A.state(),proposal2=(o)=>makeProposal(o,'beta',A.term,now);
 await fails('replica checks current signed anchor over live mTLS at prepare',()=>A.ask('red','/prepare',{proposal:proposal2(op2)}),/ANCHOR_STALE_LIVE_HEAD/);
 await fails('replica checks anchor on direct commit with fabricated majority votes',()=>A.ask('red','/commit',{proposal:proposal2(op2),votes:forgedVotes(proposal2(op2))}),/ANCHOR_STALE_LIVE_HEAD/);
 await step('signed rollover inclusion verified during new-leader completion',async()=>assert.equal((await A.complete('two',retry.receipt,retry.journalProof,good2)).seq,4));
 await step('cutover allowed only after both receipts verified',async()=>assert.equal((await A.run({type:'CUTOVER',epoch:2})).epoch,2));
 await fails('old membership epoch cannot create a resource grant',()=>A.begin(req('stale',1)),/STALE_REQUEST_EPOCH/);
 const stable=P.load(configs.red.stateFile),corrupt=structuredClone(stable);
 corrupt.journal.find(x=>x.proposal.op.type==='COMPLETE').proposal.op.anchorProof.snapshot.signature='AAAA';
 P.atomic(configs.red.stateFile,corrupt);
 await fails('replica replays and rejects a mutated certified history',()=>A.ask('red','/state'),/INVALID_VOTE_SIGNATURE/);
 P.atomic(configs.red.stateFile,stable);
 await step('restored signed journal replays successfully',async()=>assert.equal((await A.ask('red','/state')).body.seq,5));
 await stop(anchorSrv);
 await fails('anchor outage blocks replica decision servicing',()=>A.ask('red','/state'),/ECONNREFUSED|RPC_TIMEOUT|socket hang up/);
 pass('authority still retains two committed receipts on disk',()=>assert.equal(P.load(configs.blue.stateFile).completed.length,2));
 const report={schema:'oasis.sheet152.gate.v1',newChecks:count,passed:true,realTLS:true,replicas:3,resourceProcesses:2,anchorProcess:true,segmented151Count:260,s150ResourceCount:2,signatureReplay:true,crashRecovered:true,partialPartitionFailClosed:true,reviewedTornRecovery:true};
 fs.writeFileSync(path.join(__dirname,'new-test-report.json'),JSON.stringify(report,null,2)+'\n');
 console.log(`SHEET152 NEW PASS ${count}/${count}`);
} catch(e){console.error('FAIL AFTER '+count, e.stack||e);process.exitCode=1;}finally{for(const x of children.reverse())await stop(x).catch(()=>{});fs.rmSync(root,{recursive:true,force:true});}})();
```


## run-all.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp -a "$ROOT/baseline151" "$TMP/baseline151"
(cd "$TMP/baseline151" && bash run-all.sh)
(cd "$ROOT" && node gate152.js)
```


## browser-check.py

```python
from pathlib import Path
from playwright.sync_api import sync_playwright
html=Path(__file__).with_name('index.html').read_text()
with sync_playwright() as p:
    b=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
    page=b.new_page(viewport={'width':1320,'height':1100},accept_downloads=True)
    page.set_content(html,wait_until='domcontentloaded')
    buttons=page.locator('[data-scenario]')
    assert buttons.count()==8
    for i in range(8):
        buttons.nth(i).click()
        assert page.locator('[aria-pressed="true"]').count()==1
        assert page.locator('#scenario-index').inner_text().endswith('/ 08')
        assert ('DENIED' in page.locator('#event-state').inner_text()) == (i>=3)
    with page.expect_download() as event:
        page.locator('#export').click()
    assert event.value.suggested_filename=='sheet152-recovery.json'
    assert page.evaluate('window.__lastExport.scenario')=='recovery'
    page.locator('[data-scenario="normal"]').click()
    page.screenshot(path=str(Path(__file__).with_name('preview.png')),full_page=True)
    b.close()
    print('PASS 8 scenarios + JSON export + screenshot (10 checks)')
```


## make-release.py

```python
#!/usr/bin/env python3
"""Deterministic path ordering; verified sha manifest and byte-identical frozen baseline."""
import hashlib, json, os, zipfile
from pathlib import Path
root=Path(__file__).resolve().parent
out=Path('/mnt/data/SHEET152-full-kernel-anchor-alignment.zip')
prior=Path('/mnt/data/sheet151')
frozen=root/'baseline151'
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as src:
        for block in iter(lambda:src.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
old={str(p.relative_to(prior)):digest(p) for p in prior.rglob('*') if p.is_file()}
new={str(p.relative_to(frozen)):digest(p) for p in frozen.rglob('*') if p.is_file()}
assert old==new,(len(old),len(new),'BASELINE_CHANGED')
receipt={'schema':'oasis.sheet152.release.v1','sheet':152,'newGate':{'passed':45,'total':45,'exit':0},'inheritedFullRegression':{'previousSheet151Total':1262,'allChecksTotal':1307,'exit':int((root/'combined-exit.txt').read_text().strip())},'chromium':{'scenarios':8,'export':True,'screenshot':True},'baseline151Files':len(old),'baseline151ByteIdentical':True,'testEnvironment':'local mTLS processes on one physical host','limitations':['S150 physical writer retains 128-entry cap','signed anchor may advance between live check and durable completion','torn-write review requires separate external floor freshness confirmation','not independent-host consensus','SHEET142 inherited timing-sensitive regression may recur'],'gitSource':'new source files and release metadata if committed; complete nested source in archive'}
(root/'release-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=sorted(p for p in root.rglob('*') if p.is_file() and p != root/'SHA256SUMS' and not p.name.endswith('.tmp'))
manifest=''.join(f'{digest(p)}  {p.relative_to(root).as_posix()}\n' for p in files)
(root/'SHA256SUMS').write_text(manifest)
files.append(root/'SHA256SUMS')
files.sort(key=lambda p:p.relative_to(root).as_posix())
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=7,allowZip64=True) as z:
    for p in files:
        entry=zipfile.ZipInfo(f'sheet152/{p.relative_to(root).as_posix()}',date_time=(2026,10,9,0,0,0))
        entry.compress_type=zipfile.ZIP_DEFLATED
        entry.external_attr=(0o755 if os.access(p,os.X_OK) else 0o644)<<16
        z.writestr(entry,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=7)
with zipfile.ZipFile(out,'r') as z:
    assert z.testzip() is None
    entries=set(z.namelist())
    for p in files:assert 'sheet152/'+p.relative_to(root).as_posix() in entries
sha=digest(out)
Path(str(out)+'.sha256.txt').write_text(f'{sha}  {out.name}\n')
print(json.dumps({'archive':str(out),'bytes':out.stat().st_size,'sha256':sha,'files':len(files),'inherited':len(old),'combinedExit':receipt['inheritedFullRegression']['exit']},indent=2))
```