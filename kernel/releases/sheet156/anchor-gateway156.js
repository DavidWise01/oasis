'use strict';
// Independent anchor admission gateway: only this process owns the TLS credential
// that the underlying immutable SHEET151 anchor will accept for /advance.
const fs=require('node:fs'),crypto=require('node:crypto');
const W=require('./witness-verify156');
const P=require('./baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const {verifyGrant}=require('./baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/proof148');
const M=require('./baseline155/baseline154/baseline153/baseline152/baseline151/merkle151');
const cfg=JSON.parse(fs.readFileSync(process.env.S156_GATEWAY_CONFIG,'utf8'));
const pubs=Object.fromEntries(Object.entries(cfg.finalityPublicKeys).map(([id,p])=>[id,fs.readFileSync(p)]));
const authorityKeys=Object.fromEntries(Object.entries(cfg.authorityPublicKeys).map(([id,p])=>[id,fs.readFileSync(p)]));
const witnessKeys=Object.fromEntries(Object.entries(cfg.witnessPublicKeys).map(([id,p])=>[id,fs.readFileSync(p)]));
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
 const nonce=crypto.randomBytes(20).toString('hex');const floor=await P.rpc({port:cfg.floor.port,key:cfg.key,cert:cfg.cert,ca:cfg.ca,serverPin:cfg.floor.certPin},'/read',{nonce});W.verifyFloorReply(floor,nonce,witnessKeys);
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
