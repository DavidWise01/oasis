'use strict';
const fs=require('node:fs');
const P=require('./baseline165/baseline164/baseline163/baseline162/baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const D=require('./decision166');
const cfg=JSON.parse(fs.readFileSync(process.env.S166_CONFIG,'utf8'));
const store=D.open(cfg.dir,fs.readFileSync(cfg.signKey),{pinDir:cfg.pinDir,crashAfterPin:!!cfg.crashAfterPin});
const server=P.serve(cfg.key,cfg.cert,cfg.ca,(req,data)=>{
 P.peer(req,cfg.clientPin);
 if(req.url==='/head166'){
  if(typeof data.nonce!=='string'||data.nonce.length<12||data.nonce.length>128)throw Error('S166_BAD_NONCE');
  return D.certify(store.read(),fs.readFileSync(cfg.signKey),data.nonce);
 }
 if(req.url==='/decide166'){
  if(typeof data.nonce!=='string'||data.nonce.length<12||data.nonce.length>128)throw Error('S166_BAD_NONCE');
  if(cfg.resourcePublicKey){
   const proof=data.resourceProof;
   if(!proof?.body||!P.verify(fs.readFileSync(cfg.resourcePublicKey),'S161:STATUS',proof.body,proof.signature))throw Error('S166_RESOURCE_PROOF_REQUIRED');
   if(proof.body.resourceId!==cfg.resourceId||proof.body.root!==data.root||!Number.isSafeInteger(proof.body.count)||proof.body.count<data.rows)throw Error('S166_RESOURCE_PROOF_MISMATCH');
  }
  return D.certify(store.advance(data),fs.readFileSync(cfg.signKey),data.nonce);
 }
 throw Error('S166_UNKNOWN_RPC');
});
process.on('message',m=>{if(m==='stop')server.close(()=>process.exit(0));});
