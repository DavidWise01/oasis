'use strict';
const fs=require('node:fs');
const P=require('./baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./baseline157/baseline156/witness-verify156');
const V=require('./baseline157/catchup-verify157');
const Q=require('./page-verify158');
const crypto=require('node:crypto');
const cfg=P.load(process.env.S158_WITNESS_CONFIG),priv=fs.readFileSync(cfg.signKey);
const finalPubs=Object.fromEntries(Object.entries(cfg.finalityPublicKeys).map(([k,p])=>[k,fs.readFileSync(p)]));
const witnessPubs=Object.fromEntries(Object.entries(cfg.witnessPublicKeys).map(([k,p])=>[k,fs.readFileSync(p)]));
function fresh(){return{schema:W.SCHEMA,nodeId:cfg.id,slot:0,head:W.ZERO,history:[],pending:null,challenge:null};}
if(!fs.existsSync(cfg.stateFile))P.atomic(cfg.stateFile,fresh());
function state(){const s=P.load(cfg.stateFile);if(s.schema!==W.SCHEMA||s.nodeId!==cfg.id||s.history?.length!==s.slot)throw Error('W156_STATE_INVALID');let head=W.ZERO;for(let i=0;i<s.history.length;i++){const r=W.normalize(s.history[i]);if(r.slot!==i+1||r.prev!==head||r.head!==s.history[i].head)throw Error('W156_HASH_CHAIN_BROKEN');head=r.head;}if(head!==s.head)throw Error('W156_HISTORY_ROLLBACK_OR_TAMPER');if(s.pending){const r=W.normalize(s.pending);if(r.prev!==head||r.slot!==s.slot+1||r.head!==s.pending.head)throw Error('W156_PENDING_INVALID');}return s;}
function seal(domain,body){return{body,signature:P.sign(priv,domain,body)};}
function prepared(r){return seal('S156:PREPARE',{nodeId:cfg.id,slot:r.slot,head:r.head,prev:r.prev,recordDigest:P.sha(r)});}
function read(b){if(!/^[0-9a-f]{32,64}$/.test(b?.nonce||''))throw Error('W156_NONCE_REQUIRED');const s=state();return seal('S156:HEAD',{nodeId:cfg.id,nonce:b.nonce,slot:s.slot,head:s.head});}
function prepare(b){const s=state(),r=W.normalize(b.record);if(s.recovery)throw Error('W158_CATCHUP_HOLD');W.verifyFinalVotes(r,b.finalVotes,finalPubs);
 if(s.slot===r.slot&&s.head===r.head)return prepared(r);
 if(r.slot!==s.slot+1||r.prev!==s.head)throw Error('W156_STALE_OR_GAP');
 if(s.pending&&P.sha(s.pending)!==P.sha(r))throw Error('W156_CONFLICTING_PREPARE');
 if(!s.pending){s.pending=r;P.atomic(cfg.stateFile,s);}return prepared(r);
}
function commit(b){const s=state(),r=W.normalize(b.record);if(s.recovery)throw Error('W158_CATCHUP_HOLD');W.verifyPrepares(r,b.preparedVotes,witnessPubs);
 if(r.slot===s.slot&&r.head===s.head)return seal('S156:COMMIT',{nodeId:cfg.id,slot:s.slot,head:s.head,recordDigest:P.sha(r)});
 if(r.slot!==s.slot+1||r.prev!==s.head||!s.pending||P.sha(s.pending)!==P.sha(r))throw Error('W156_UNPREPARED_OR_CONFLICT');
 s.history.push(r);s.slot=r.slot;s.head=r.head;s.pending=null;P.atomic(cfg.stateFile,s);return seal('S156:COMMIT',{nodeId:cfg.id,slot:s.slot,head:s.head,recordDigest:P.sha(r)});
}
function challenge(){
 const s=state();const nonce=crypto.randomBytes(20).toString('hex');
 s.challenge={nonce,expires:Date.now()+45000};P.atomic(cfg.stateFile,s);
 return seal('S157:CHALLENGE',{nodeId:cfg.id,nonce,slot:s.slot,head:s.head});
}
function exported(b){
 const s=state();if(!/^[a-f0-9]{40}$/.test(b?.nonce))throw Error('W157_NONCE_REQUIRED');
 return seal('S157:EXPORT',{schema:V.SCHEMA,nodeId:cfg.id,nonce:b.nonce,slot:s.slot,head:s.head,history:s.history});
}
function catchup(b){
 const s=state();if(s.recovery)throw Error('W158_CATCHUP_HOLD');const nonce=s.challenge?.nonce;
 if(!nonce||s.challenge.expires<Date.now()||b?.nonce!==nonce)throw Error('W157_CHALLENGE_EXPIRED_OR_REPLAY');
 const remote=V.certify(b.head,b.heads,b.exported,nonce,witnessPubs);
 V.admission(s,remote);
 const newState={...s,slot:b.head.slot,head:b.head.head,history:remote,pending:null,challenge:null};
 P.atomic(cfg.stateFile,newState);
 if(cfg.crashAfterInstall&&!fs.existsSync(cfg.crashMarker)){
  fs.writeFileSync(cfg.crashMarker,'installed-before-reply\n');process.exit(71);
 }
 return seal('S157:INSTALLED',{nodeId:cfg.id,slot:newState.slot,head:newState.head,historyDigest:P.sha(newState.history)});
}
// SHEET158: durable, page-wise authenticated witness catchup. Any disagreement quarantines the state.
function begin158(b){
 const s=state(),nonce=s.challenge?.nonce;
 if(s.recovery)throw Error('W158_RECOVERY_ALREADY_ACTIVE');
 if(!nonce||s.challenge.expires<Date.now()||nonce!==b.nonce)throw Error('W158_CHALLENGE_EXPIRED');
 const signers=Q.certify(b.target,b.heads,nonce,witnessPubs);
 if(b.target.slot<s.slot||b.target.slot===s.slot&&b.target.head!==s.head)throw Error('W158_ROLLBACK_OR_FORK');
 s.recovery={nonce,target:b.target,signers,cursor:s.slot,head:s.head,staged:[],startedSlot:s.slot,startedHead:s.head};
 s.challenge=null;P.atomic(cfg.stateFile,s);
 return seal('S158:BEGIN',{nodeId:cfg.id,nonce,target:b.target,cursor:s.recovery.cursor});
}
function page158(b){
 const s=state(),body=Q.makePage({nodeId:cfg.id,nonce:b.nonce,target:b.target,history:s.history,offset:b.offset,limit:b.limit});
 return seal('S158:PAGE',body);
}
function status158(){
 const s=state(),r=s.recovery;
 return seal('S158:STATUS',{nodeId:cfg.id,active:!!r,nonce:r?.nonce||null,cursor:r?.cursor??s.slot,head:r?.head||s.head,target:r?.target||null,slot:s.slot});
}
function apply158(b){
 const s=state(),r=s.recovery;
 if(!r||!b?.page)throw Error('W158_NO_ACTIVE_RECOVERY');
 const rows=Q.verifyPage(b.page,{nonce:r.nonce,target:r.target,cursor:r.cursor,prev:r.head,signers:r.signers,keys:witnessPubs});
 Q.admitPending(s,r,rows);
 r.staged.push(...rows);r.cursor+=rows.length;r.head=rows[rows.length-1].head;
 P.atomic(cfg.stateFile,s);
 if(cfg.crashAfterPage&&!fs.existsSync(cfg.crashAfterPage)){
  fs.writeFileSync(cfg.crashAfterPage,'persisted-page-before-reply\n');process.exit(73);
 }
 return seal('S158:APPLIED',{nodeId:cfg.id,nonce:r.nonce,cursor:r.cursor,head:r.head});
}
function finish158(){
 const s=state(),r=s.recovery;
 if(!r){if(s.lastRecovery)return seal('S158:FINISHED',s.lastRecovery);throw Error('W158_NO_ACTIVE_RECOVERY');}
 if(r.cursor!==r.target.slot||r.head!==r.target.head||s.slot!==r.startedSlot||s.head!==r.startedHead)throw Error('W158_INCOMPLETE_OR_CHANGED');
 if(s.pending){const p=s.pending.slot-s.slot-1;if(p>=r.staged.length||P.sha(r.staged[p])!==P.sha(s.pending))throw Error('W158_PENDING_FORK_QUARANTINE');}
 s.history.push(...r.staged);s.slot=r.target.slot;s.head=r.target.head;s.pending=null;
 s.lastRecovery={nodeId:cfg.id,nonce:r.nonce,slot:s.slot,head:s.head,historyDigest:P.sha(s.history)};
 s.recovery=null;P.atomic(cfg.stateFile,s);
 return seal('S158:FINISHED',s.lastRecovery);
}
const server=P.serve(cfg.key,cfg.cert,cfg.ca,(req,b)=>{P.peer(req,cfg.proxyPin);if(req.url==='/read')return read(b);if(req.url==='/prepare')return prepare(b);if(req.url==='/commit')return commit(b);if(req.url==='/challenge')return challenge();if(req.url==='/export')return exported(b);if(req.url==='/catchup')return catchup(b);if(req.url==='/begin158')return begin158(b);if(req.url==='/page158')return page158(b);if(req.url==='/status158')return status158();if(req.url==='/apply158')return apply158(b);if(req.url==='/finish158')return finish158();throw Error('W157_ROUTE_INVALID');});
process.on('message',v=>{if(v==='stop')server.close(()=>process.exit(0));});
module.exports={state,prepare,commit};
