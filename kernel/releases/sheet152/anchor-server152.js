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
