'use strict';
const fs=require('node:fs');
const P=require('./baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./witness-verify156');
const cfg=P.load(process.env.S156_WITNESS_CONFIG),priv=fs.readFileSync(cfg.signKey);
const finalPubs=Object.fromEntries(Object.entries(cfg.finalityPublicKeys).map(([k,p])=>[k,fs.readFileSync(p)]));
const witnessPubs=Object.fromEntries(Object.entries(cfg.witnessPublicKeys).map(([k,p])=>[k,fs.readFileSync(p)]));
function fresh(){return{schema:W.SCHEMA,nodeId:cfg.id,slot:0,head:W.ZERO,history:[],pending:null};}
if(!fs.existsSync(cfg.stateFile))P.atomic(cfg.stateFile,fresh());
function state(){const s=P.load(cfg.stateFile);if(s.schema!==W.SCHEMA||s.nodeId!==cfg.id||s.history?.length!==s.slot)throw Error('W156_STATE_INVALID');let head=W.ZERO;for(let i=0;i<s.history.length;i++){const r=W.normalize(s.history[i]);if(r.slot!==i+1||r.prev!==head||r.head!==s.history[i].head)throw Error('W156_HASH_CHAIN_BROKEN');head=r.head;}if(head!==s.head)throw Error('W156_HISTORY_ROLLBACK_OR_TAMPER');if(s.pending){const r=W.normalize(s.pending);if(r.prev!==head||r.slot!==s.slot+1||r.head!==s.pending.head)throw Error('W156_PENDING_INVALID');}return s;}
function seal(domain,body){return{body,signature:P.sign(priv,domain,body)};}
function prepared(r){return seal('S156:PREPARE',{nodeId:cfg.id,slot:r.slot,head:r.head,prev:r.prev,recordDigest:P.sha(r)});}
function read(b){if(!/^[0-9a-f]{32,64}$/.test(b?.nonce||''))throw Error('W156_NONCE_REQUIRED');const s=state();return seal('S156:HEAD',{nodeId:cfg.id,nonce:b.nonce,slot:s.slot,head:s.head});}
function prepare(b){const s=state(),r=W.normalize(b.record);W.verifyFinalVotes(r,b.finalVotes,finalPubs);
 if(s.slot===r.slot&&s.head===r.head)return prepared(r);
 if(r.slot!==s.slot+1||r.prev!==s.head)throw Error('W156_STALE_OR_GAP');
 if(s.pending&&P.sha(s.pending)!==P.sha(r))throw Error('W156_CONFLICTING_PREPARE');
 if(!s.pending){s.pending=r;P.atomic(cfg.stateFile,s);}return prepared(r);
}
function commit(b){const s=state(),r=W.normalize(b.record);W.verifyPrepares(r,b.preparedVotes,witnessPubs);
 if(r.slot===s.slot&&r.head===s.head)return seal('S156:COMMIT',{nodeId:cfg.id,slot:s.slot,head:s.head,recordDigest:P.sha(r)});
 if(r.slot!==s.slot+1||r.prev!==s.head||!s.pending||P.sha(s.pending)!==P.sha(r))throw Error('W156_UNPREPARED_OR_CONFLICT');
 s.history.push(r);s.slot=r.slot;s.head=r.head;s.pending=null;P.atomic(cfg.stateFile,s);return seal('S156:COMMIT',{nodeId:cfg.id,slot:s.slot,head:s.head,recordDigest:P.sha(r)});
}
const server=P.serve(cfg.key,cfg.cert,cfg.ca,(req,b)=>{P.peer(req,cfg.proxyPin);if(req.url==='/read')return read(b);if(req.url==='/prepare')return prepare(b);if(req.url==='/commit')return commit(b);throw Error('W156_ROUTE_INVALID');});
process.on('message',v=>{if(v==='stop')server.close(()=>process.exit(0));});
module.exports={state,prepare,commit};
