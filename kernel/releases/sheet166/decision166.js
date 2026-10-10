'use strict';
// Separately persisted Ed25519 decision signer. Single signer, not multi-host consensus.
const fs=require('node:fs'),path=require('node:path');
const P=require('./baseline165/baseline164/baseline163/baseline162/baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const DOM='S166:POLICY_HEAD';
const SCHEMA='oasis.sheet166.decision.v1';
function genesis(){return{schema:SCHEMA,generation:0,mode:'candidate',rows:0,prevHash:'0'.repeat(64),decisionId:'GENESIS',root:'GENESIS'};}
function certify(body,privateKey,nonce=''){return {body:{...body,nonce},signature:P.sign(privateKey,DOM,{...body,nonce})};}
function check(cert,publicKey,nonce){if(!cert||!P.verify(publicKey,DOM,cert.body,cert.signature)||cert.body.schema!==SCHEMA||cert.body.nonce!==nonce)throw Error('S166_BAD_HEAD_SIGNATURE');return cert.body;}
function open(dir,priv,{pinDir=dir,crashAfterPin=false}={}){
 fs.mkdirSync(dir,{recursive:true});fs.mkdirSync(pinDir,{recursive:true});
 const local=path.join(dir,'head.json'),pin=path.join(pinDir,'floor.json');
 if(!fs.existsSync(local)&&!fs.existsSync(pin)){const g=genesis();P.atomic(pin,g);P.atomic(local,g);}
 function read(){const l=P.load(local),p=P.load(pin);if(l.schema!==SCHEMA||p.schema!==SCHEMA||P.sha(l)!==P.sha(p))throw Error('S166_EXTERNAL_FLOOR_CONFLICT');return l;}
 function advance(req){let current=read();
  if(req.decisionId===current.decisionId&&req.expectedGeneration===current.generation-1&&req.to===current.mode)return current;
  if(req.expectedGeneration!==current.generation||req.expectedHead!==P.sha(current))throw Error('S166_STALE_FLOOR');
  if(!['baseline','candidate'].includes(req.to)||req.to===current.mode||req.from!==current.mode)throw Error('S166_MODE_FORK');
  if(!Number.isSafeInteger(req.rows)||req.rows<=current.rows||req.rows-current.rows<8)throw Error('S166_NONMONOTONIC_ROWS');
  if(!/^[a-f0-9]{64}$/.test(req.measurementDigest)||!/^[a-f0-9]{64}$/.test(req.root)||!/^[a-f0-9]{64}$/.test(req.decisionId))throw Error('S166_DECISION_BINDING');
  if(req.to==='candidate'&&req.reason!=='VERIFIED_HOLDOUT_REPROMOTION')throw Error('S166_PROMOTION_EVIDENCE');
  if(req.to==='baseline'&&req.reason!=='PERFORMANCE_DEGRADED')throw Error('S166_DOWNGRADE_EVIDENCE');
  const next={schema:SCHEMA,generation:current.generation+1,mode:req.to,rows:req.rows,prevHash:P.sha(current),decisionId:req.decisionId,root:req.root,measurementDigest:req.measurementDigest,reason:req.reason};
  // Pin first: a crash between these writes makes reads fail closed; no automatic pin rollback.
  P.atomic(pin,next);
  if(crashAfterPin){fs.writeFileSync(path.join(dir,'crash-marker'),'after-external-pin');process.kill(process.pid,'SIGKILL');}
  P.atomic(local,next);return next;
 }
 return{read,advance,local,pin};
}
module.exports={SCHEMA,DOM,genesis,check,certify,open};
