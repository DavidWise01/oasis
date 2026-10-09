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
