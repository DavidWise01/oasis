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
