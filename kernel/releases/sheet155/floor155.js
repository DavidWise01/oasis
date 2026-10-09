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
