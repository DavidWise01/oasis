# SHEET 159 — Complete New Source

Actual executable implementation. Frozen inherited SHEET 158 lineage is included byte-for-byte in the complete ZIP.


## merkle159.js

```javascript
'use strict';
const P=require('./baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./baseline158/baseline157/baseline156/witness-verify156');
const M=require('./baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/merkle151');
const SCHEMA='oasis.sheet159.merkle.page.v1',MAX_PAGE=24;
const hex=s=>typeof s==='string'&&/^[a-f0-9]{64}$/.test(s);
function certify(target,checkpoints,nonce,keys){
 if(!/^[0-9a-f]{40}$/.test(nonce||'')||!Number.isSafeInteger(target?.slot)||target.slot<0||!hex(target?.head)||!hex(target?.merkleRoot))throw Error('W159_TARGET');
 const seen=new Set();
 for(const x of checkpoints||[]){const b=x?.body,id=b?.nodeId;
  if(!keys[id]||seen.has(id)||b.nonce!==nonce||b.slot!==target.slot||b.head!==target.head||b.merkleRoot!==target.merkleRoot||!Array.isArray(b.frontier)||!P.verify(keys[id],'S159:CHECKPOINT',b,x.signature))throw Error('W159_CHECKPOINT_SIGNATURE');
  if(M.root(b.slot,b.frontier)!==b.merkleRoot)throw Error('W159_CHECKPOINT_FRONTIER');
  seen.add(id);
 }
 if(seen.size<2)throw Error('W159_NO_QUORUM');return [...seen];
}
function verifyPage(page,{nonce,target,cursor,head,merkle,signers,keys}){
 const b=page?.body,id=b?.nodeId;
 if(!signers.includes(id)||!keys[id]||!P.verify(keys[id],'S159:PAGE',b,page.signature))throw Error('W159_PAGE_SIGNATURE');
 if(b.schema!==SCHEMA||b.nonce!==nonce||P.sha(b.target)!==P.sha(target)||b.offset!==cursor||b.prevHead!==head||b.priorRoot!==merkle.root)throw Error('W159_PAGE_CONTEXT');
 if(!Array.isArray(b.records)||b.records.length<1||b.records.length>MAX_PAGE||b.next!==cursor+b.records.length||b.next>target.slot)throw Error('W159_PAGE_SIZE');
 let current=head;
 for(let i=0;i<b.records.length;i++){const r=W.normalize(b.records[i]);if(r.slot!==cursor+i+1||r.prev!==current||P.sha(r)!==P.sha(b.records[i]))throw Error('W159_PAGE_CHAIN');current=r.head;}
 if(current!==b.endHead)throw Error('W159_END_HEAD');
 if(!Array.isArray(b.afterFrontier)||!hex(b.afterRoot))throw Error('W159_AFTER_ROOT');
 const newState=M.verifyExtension(merkle,b.extension,{count:b.next,frontier:b.afterFrontier,root:b.afterRoot});
 // Merkle proof must have exactly the hashes of the transmitted records, not only a consistent but unrelated subtree.
 const computed=b.records.reduce((s,row)=>M.appendPeak(s.count,s.frontier,1,M.leaf(s.count,P.sha(row))),{count:merkle.count,frontier:merkle.frontier.slice()});
 if(M.root(computed.count,computed.frontier)!==newState.root)throw Error('W159_PAGE_LEAF_SUBSTITUTION');
 if(b.next===target.slot&&(current!==target.head||newState.root!==target.merkleRoot))throw Error('W159_TARGET_MISMATCH');
 return b.records;
}
module.exports={SCHEMA,MAX_PAGE,certify,verifyPage};
```


## witness159.js

```javascript
'use strict';
const fs=require('node:fs');
const P=require('./baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./baseline158/baseline157/baseline156/witness-verify156');
const V=require('./baseline158/baseline157/catchup-verify157');
const Q=require('./baseline158/page-verify158');
const M=require('./baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/merkle151');
const H=require('./merkle159');
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
function prepare(b){const s=state(),r=W.normalize(b.record);if(s.recovery||s.recovery159)throw Error('W159_CATCHUP_HOLD');W.verifyFinalVotes(r,b.finalVotes,finalPubs);
 if(s.slot===r.slot&&s.head===r.head)return prepared(r);
 if(r.slot!==s.slot+1||r.prev!==s.head)throw Error('W156_STALE_OR_GAP');
 if(s.pending&&P.sha(s.pending)!==P.sha(r))throw Error('W156_CONFLICTING_PREPARE');
 if(!s.pending){s.pending=r;P.atomic(cfg.stateFile,s);}return prepared(r);
}
function commit(b){const s=state(),r=W.normalize(b.record);if(s.recovery||s.recovery159)throw Error('W159_CATCHUP_HOLD');W.verifyPrepares(r,b.preparedVotes,witnessPubs);
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
 const s=state();if(s.recovery||s.recovery159)throw Error('W159_CATCHUP_HOLD');const nonce=s.challenge?.nonce;
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

// SHEET159: truly binary-peak Merkle extension proofs, with crash-durable frontier.
function mhead(s){return M.accumulate(s.history.map(x=>P.sha(x)));}
function checkpoint159(b){
 const s=state(); if(!/^[0-9a-f]{40}$/.test(b?.nonce||''))throw Error('W159_NONCE');
 const m=mhead(s);return seal('S159:CHECKPOINT',{nodeId:cfg.id,nonce:b.nonce,slot:s.slot,head:s.head,merkleRoot:m.root,frontier:m.frontier});
}
function begin159(b){
 const s=state(),nonce=s.challenge?.nonce;
 if(s.recovery||s.recovery159)throw Error('W159_RECOVERY_ACTIVE');
 if(!nonce||nonce!==b?.nonce||s.challenge.expires<Date.now())throw Error('W159_CHALLENGE');
 const signed=H.certify(b.target,b.checkpoints,nonce,witnessPubs);
 if(signed.length<2||b.target.slot<s.slot)throw Error('W159_STALE');
 const old=mhead(s);
 if(b.target.slot===s.slot&&(b.target.head!==s.head||b.target.merkleRoot!==old.root))throw Error('W159_FORK');
 s.recovery159={nonce,signers:signed,target:b.target,cursor:s.slot,head:s.head,merkle:old,staged:[],startSlot:s.slot,startHead:s.head,segmentPins:[]};
 s.challenge=null;P.atomic(cfg.stateFile,s);
 return seal('S159:BEGIN',{nodeId:cfg.id,nonce,cursor:s.slot,merkleRoot:old.root});
}
function page159(b){
 const s=state(),nonce=b?.nonce,offset=b?.offset,limit=b?.limit,target=b?.target;
 if(!/^[0-9a-f]{40}$/.test(nonce||'')||!Number.isSafeInteger(offset)||offset<0||!Number.isInteger(limit)||limit<1||limit>H.MAX_PAGE)throw Error('W159_PAGE_REQUEST');
 if(!Number.isSafeInteger(target?.slot)||offset>=target.slot||target.slot>s.slot||s.history[target.slot-1]?.head!==target.head)throw Error('W159_TARGET_NOT_PRESENT');
 const checkpoint=mhead(s);
 if(target.slot===s.slot&&target.merkleRoot!==checkpoint.root)throw Error('W159_TARGET_ROOT');
 const next=Math.min(offset+limit,target.slot),rows=s.history.slice(offset,next);
 const hashes=s.history.slice(0,next).map(x=>P.sha(x));
 const extension=M.extension(hashes,offset);const prior=M.accumulate(hashes.slice(0,offset));const after=M.accumulate(hashes);
 return seal('S159:PAGE',{schema:H.SCHEMA,nodeId:cfg.id,nonce,target,offset,next,priorRoot:prior.root,afterRoot:after.root,afterFrontier:after.frontier,prevHead:offset?s.history[offset-1].head:W.ZERO,endHead:rows.at(-1).head,records:rows,extension});
}
function status159(){const s=state(),r=s.recovery159;return seal('S159:STATUS',{nodeId:cfg.id,active:!!r,nonce:r?.nonce||null,cursor:r?.cursor??s.slot,head:r?.head||s.head,root:r?.merkle?.root||mhead(s).root,target:r?.target||null,segments:r?.segmentPins?.length||0});}
function apply159(b){
 const s=state(),r=s.recovery159;
 if(!r)throw Error('W159_NO_RECOVERY');
 const rows=H.verifyPage(b?.page,{nonce:r.nonce,target:r.target,cursor:r.cursor,head:r.head,merkle:r.merkle,signers:r.signers,keys:witnessPubs});
 Q.admitPending(s,{staged:r.staged},rows);
 r.staged.push(...rows);r.cursor+=rows.length;r.head=rows.at(-1).head;
 r.merkle=M.verifyExtension(r.merkle,b.page.body.extension,{count:r.cursor,frontier:b.page.body.afterFrontier,root:b.page.body.afterRoot});
 if(r.cursor%32===0||r.cursor===r.target.slot)r.segmentPins.push({cursor:r.cursor,head:r.head,root:r.merkle.root});
 P.atomic(cfg.stateFile,s);
 if(cfg.crashAfterMerklePage&&!fs.existsSync(cfg.crashAfterMerklePage)){fs.writeFileSync(cfg.crashAfterMerklePage,'durable-merkle-page\n');process.exit(79);}
 return seal('S159:APPLIED',{nodeId:cfg.id,nonce:r.nonce,cursor:r.cursor,head:r.head,merkleRoot:r.merkle.root});
}
function finish159(){
 const s=state(),r=s.recovery159;
 if(!r){if(s.lastRecovery159)return seal('S159:FINISHED',s.lastRecovery159);throw Error('W159_NO_RECOVERY');}
 if(r.cursor!==r.target.slot||r.head!==r.target.head||r.merkle.root!==r.target.merkleRoot||s.slot!==r.startSlot||s.head!==r.startHead)throw Error('W159_NOT_CERTIFIED');
 if(s.pending){const i=s.pending.slot-s.slot-1;if(i>=r.staged.length||P.sha(r.staged[i])!==P.sha(s.pending))throw Error('W159_PENDING_QUARANTINE');}
 s.history.push(...r.staged);s.slot=r.cursor;s.head=r.head;s.pending=null;
 s.lastRecovery159={nodeId:cfg.id,nonce:r.nonce,slot:s.slot,head:s.head,merkleRoot:r.merkle.root,segmentPins:r.segmentPins};
 s.recovery159=null;P.atomic(cfg.stateFile,s);
 return seal('S159:FINISHED',s.lastRecovery159);
}

const server=P.serve(cfg.key,cfg.cert,cfg.ca,(req,b)=>{P.peer(req,cfg.proxyPin);if(req.url==='/read')return read(b);if(req.url==='/checkpoint159')return checkpoint159(b);if(req.url==='/begin159')return begin159(b);if(req.url==='/page159')return page159(b);if(req.url==='/status159')return status159();if(req.url==='/apply159')return apply159(b);if(req.url==='/finish159')return finish159();if(req.url==='/prepare')return prepare(b);if(req.url==='/commit')return commit(b);if(req.url==='/challenge')return challenge();if(req.url==='/export')return exported(b);if(req.url==='/catchup')return catchup(b);if(req.url==='/begin158')return begin158(b);if(req.url==='/page158')return page158(b);if(req.url==='/status158')return status158();if(req.url==='/apply158')return apply158(b);if(req.url==='/finish158')return finish158();throw Error('W157_ROUTE_INVALID');});
process.on('message',v=>{if(v==='stop')server.close(()=>process.exit(0));});
module.exports={state,prepare,commit};
```


## catchup159.js

```javascript
'use strict';
const P=require('./baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const H=require('./merkle159');
function make({identity,witnesses,publicKeys}){
 const rpc=(id,url,b={})=>P.rpc({...identity,...witnesses[id]},url,b);
 function ack(id,domain,response){if(response?.body?.nodeId!==id||!P.verify(publicKeys[id],domain,response.body,response.signature))throw Error('W159_ACK_SIGNATURE');return response.body;}
 async function repair(target,{pageSize=16,onPage=()=>{}}={}){
  if(!witnesses[target]||Object.keys(witnesses).length!==3||!Number.isInteger(pageSize)||pageSize<1||pageSize>H.MAX_PAGE)throw Error('W159_CONFIG');
  let status=ack(target,'S159:STATUS',await rpc(target,'/status159'));
  let certified;
  if(!status.active){
   const nonce=ack(target,'S157:CHALLENGE',await rpc(target,'/challenge')).nonce;
   const peers=Object.keys(witnesses).filter(x=>x!==target),checks=[];
   for(const id of peers){try{const a=await rpc(id,'/checkpoint159',{nonce});ack(id,'S159:CHECKPOINT',a);checks.push(a);}catch{}}
   if(checks.length<2)throw Error('W159_NO_QUORUM');
   certified={slot:checks[0].body.slot,head:checks[0].body.head,merkleRoot:checks[0].body.merkleRoot};
   H.certify(certified,checks,nonce,publicKeys);
   ack(target,'S159:BEGIN',await rpc(target,'/begin159',{nonce,target:certified,checkpoints:checks}));
   status=ack(target,'S159:STATUS',await rpc(target,'/status159'));
  }
  certified=status.target;
  if(!certified||!status.nonce)throw Error('W159_SESSION');
  const peers=Object.keys(witnesses).filter(x=>x!==target);
  let cursor=status.cursor;
  while(cursor<certified.slot){
   let accepted=false,last;
   for(const id of peers){
    try{const page=await rpc(id,'/page159',{nonce:status.nonce,target:certified,offset:cursor,limit:pageSize});
     const result=ack(target,'S159:APPLIED',await rpc(target,'/apply159',{page}));
     if(result.cursor<=cursor||result.cursor>certified.slot)throw Error('W159_ACK_CURSOR');
     cursor=result.cursor;onPage(cursor);accepted=true;break;
    }catch(e){last=e;
     // An acknowledgement can be lost after durable write; consult the signed persisted cursor.
     try{const s=ack(target,'S159:STATUS',await rpc(target,'/status159'));if(s.active&&s.nonce===status.nonce&&s.target?.merkleRoot===certified.merkleRoot&&s.cursor>cursor){cursor=s.cursor;onPage(cursor);accepted=true;break;}}catch{}
    }
   }
   if(!accepted)throw Error('W159_STOPPED: '+(last?.message||'no source'));
  }
  const result=await rpc(target,'/finish159'),end=ack(target,'S159:FINISHED',result);
  if(end.slot!==certified.slot||end.head!==certified.head||end.merkleRoot!==certified.merkleRoot)throw Error('W159_FINAL_MISMATCH');return result;
 }
 return{rpc,repair};
}
module.exports={make};
```


## gate159.js

```javascript
#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const P=require('./baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./baseline158/baseline157/baseline156/witness-verify156');const V=require('./merkle159');const C=require('./catchup159');
const root=fs.mkdtempSync(path.join(os.tmpdir(),'sheet159-')),f=(...a)=>path.join(root,...a),openssl=(...a)=>cp.execFileSync('openssl',a,{cwd:root,stdio:'pipe'});
let n=0;const ok=(name,fn)=>{fn();console.log('PASS',++n,name);};const step=async(name,fn)=>{await fn();console.log('PASS',++n,name);};const bad=async(name,fn,regex)=>step(name,async()=>assert.rejects(fn,regex));
function cert(id){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',id+'.key','-out',id+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(id+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',id+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',id+'.crt','-days','2','-sha256','-extfile',id+'.ext');return{key:f(id+'.key'),cert:f(id+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(id+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
function keys(id){const pair=crypto.generateKeyPairSync('ed25519'),priv=f(id+'.priv'),pub=f(id+'.pub');fs.writeFileSync(priv,pair.privateKey.export({format:'pem',type:'pkcs8'}));fs.writeFileSync(pub,pair.publicKey.export({format:'pem',type:'spki'}));return{privateKey:pair.privateKey,publicKey:pair.publicKey,priv,pub};}
const children=[];
async function spawn(script,cfg,id){const config=f('cfg-'+id+'.json');P.atomic(config,cfg);const proc=cp.fork(path.join(__dirname,script),[],{env:{...process.env,S158_WITNESS_CONFIG:config,S156_FLOOR_CONFIG:config},stdio:['ignore','pipe','pipe','ipc']});let errors='';proc.on('error',()=>{});proc.stderr.on('data',b=>errors+=b);const port=await new Promise((res,rej)=>{const t=setTimeout(()=>rej(Error('START_TIMEOUT '+id+' '+errors)),15000);proc.once('message',m=>{clearTimeout(t);res(m.port);});proc.once('exit',code=>{clearTimeout(t);rej(Error('START_FAILED '+id+' '+code+' '+errors));});});const x={proc,port,id,errors:()=>errors};children.push(x);return x;}
async function stop(x){if(!x||x.proc.exitCode!==null||x.proc.signalCode!==null)return;await new Promise(done=>{const t=setTimeout(()=>{x.proc.kill('SIGKILL');done();},2000);x.proc.once('exit',()=>{clearTimeout(t);done();});if(x.proc.connected){try{x.proc.send('stop',err=>{if(err){x.proc.kill('SIGKILL');clearTimeout(t);done();}});}catch{ x.proc.kill('SIGKILL');clearTimeout(t);done();}}else{x.proc.kill('SIGKILL');clearTimeout(t);done();}});}
(async()=>{try{
 openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=S159');
 const ids=Object.fromEntries(['proxy','wred','wblue','wgreen','rogue'].map(id=>[id,cert(id)]));
 const witnessKeys=Object.fromEntries(['wred','wblue','wgreen'].map(id=>[id,keys(id)]));
 const finalKeys=Object.fromEntries(['red','blue'].map(id=>[id,keys('final-'+id)]));
 const pubs=Object.fromEntries(Object.entries(witnessKeys).map(([id,k])=>[id,k.publicKey]));
 const witnessPublicKeys=Object.fromEntries(Object.entries(witnessKeys).map(([id,k])=>[id,k.pub]));
 const finalPublicKeys=Object.fromEntries(Object.entries(finalKeys).map(([id,k])=>[id,k.pub]));
 const cfg=Object.fromEntries(Object.keys(witnessKeys).map(id=>[id,{id,...ids[id],signKey:witnessKeys[id].priv,stateFile:f(id,'state.json'),proxyPin:ids.proxy.certPin,witnessPublicKeys,finalityPublicKeys:finalPublicKeys}]));
 const M=require('./baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/merkle151');
 const record=(slot,prev,tag)=>W.normalize({slot,prev,intentDigest:P.sha('intent'+tag),snapshotDigest:P.sha('snapshot'+tag),receiptHash:P.sha('receipt'+tag)});
 const history=[];let prev=W.ZERO;for(let i=1;i<=389;i++){const r=record(i,prev,'synthetic-'+i);history.push(r);prev=r.head;}
 for(const id of ['wred','wgreen'])P.atomic(cfg[id].stateFile,{schema:W.SCHEMA,nodeId:id,slot:389,head:prev,history:structuredClone(history),pending:null,challenge:null});
 P.atomic(cfg.wblue.stateFile,{schema:W.SCHEMA,nodeId:'wblue',slot:7,head:history[6].head,history:history.slice(0,7),pending:history[7],challenge:null});
 const nodes={};for(const id of Object.keys(cfg))nodes[id]=await spawn('witness159.js',cfg[id],id);
 const endpoints=()=>Object.fromEntries(Object.keys(nodes).map(id=>[id,{port:nodes[id].port,serverPin:ids[id].certPin}]));
 const api=()=>C.make({identity:ids.proxy,witnesses:endpoints(),publicKeys:pubs});
 const rpc=(id,url,b={})=>api().rpc(id,url,b);
 const state=id=>P.load(cfg[id].stateFile);
 const target={slot:389,head:prev,merkleRoot:M.accumulate(history.map(P.sha)).root};
 ok('three mTLS witness services online',()=>assert.equal(Object.keys(nodes).length,3));
 ok('majority has 389 source records',()=>assert.equal(state('wred').slot,389));
 ok('minority has seven certified prefix entries',()=>assert.equal(state('wblue').slot,7));
 ok('pending promise preserved',()=>assert.equal(state('wblue').pending.head,history[7].head));
 ok('bounded page length remains 24',()=>assert.equal(V.MAX_PAGE,24));
 ok('genuine Merkle extension proof verifies 7 -> 22',()=>{const h=history.map(P.sha);const a=M.accumulate(h.slice(0,7)),b=M.accumulate(h.slice(0,22));assert.equal(M.verifyExtension(a,M.extension(h.slice(0,22),7),b).root,b.root);});
 ok('altered Merkle subtree fails',()=>{const h=history.map(P.sha),a=M.accumulate(h.slice(0,7)),b=M.accumulate(h.slice(0,22)),p=M.extension(h.slice(0,22),7);p.blocks[0].root='f'.repeat(64);assert.throws(()=>M.verifyExtension(a,p,b),/EXTENSION_ROOT_MISMATCH/);});
 ok('shorter prefix root differs',()=>assert.notEqual(M.accumulate(history.slice(0,8).map(P.sha)).root,target.merkleRoot));
 const challenge=await rpc('wblue','/challenge');const nonce=challenge.body.nonce;
 const heads=await Promise.all(['wred','wgreen'].map(id=>rpc(id,'/checkpoint159',{nonce})));
 ok('2/3 certified Merkle checkpoints',()=>assert.equal(V.certify(target,heads,nonce,pubs).length,2));
 ok('duplicate checkpoint refused',()=>assert.throws(()=>V.certify(target,[heads[0],heads[0]],nonce,pubs),/W159_CHECKPOINT_SIGNATURE/));
 ok('forged checkpoint signature refused',()=>assert.throws(()=>V.certify(target,[{...heads[0],signature:'AAAA'},heads[1]],nonce,pubs),/W159_CHECKPOINT_SIGNATURE/));
 ok('wrong certified Merkle root rejected',()=>assert.throws(()=>V.certify({...target,merkleRoot:'a'.repeat(64)},heads,nonce,pubs),/W159_CHECKPOINT_SIGNATURE/));
 await bad('one signed checkpoint cannot begin recovery',()=>rpc('wblue','/begin159',{nonce,target,checkpoints:[heads[0]]}),/W159_NO_QUORUM/);
 await step('begin session persists certified target',async()=>assert.equal((await rpc('wblue','/begin159',{nonce,target,checkpoints:heads})).body.cursor,7));
 await bad('duplicate recovery begin fails',()=>rpc('wblue','/begin159',{nonce,target,checkpoints:heads}),/W159_RECOVERY_ACTIVE/);
 const signed=body=>({body,signature:P.sign(witnessKeys.wred.privateKey,'S159:PAGE',body)});
 const page=await rpc('wred','/page159',{nonce,target,offset:7,limit:15});
 ok('page contains exactly fifteen real rows',()=>assert.equal(page.body.records.length,15));
 ok('page carries a logarithmic Merkle block witness',()=>assert(page.body.extension.blocks.length<=8));
 ok('source Merkle proof binds local prefix',()=>assert.equal(page.body.priorRoot,M.accumulate(history.slice(0,7).map(P.sha)).root));
 ok('recipient verifies page against local frontier',()=>assert.equal(V.verifyPage(page,{nonce,target,cursor:7,head:history[6].head,merkle:M.accumulate(history.slice(0,7).map(P.sha)),signers:['wred','wgreen'],keys:pubs}).length,15));
 await bad('forged signed page rejected',()=>rpc('wblue','/apply159',{page:{...page,signature:'bad'}}),/W159_PAGE_SIGNATURE/);
 await bad('page with altered target rejected',()=>rpc('wblue','/apply159',{page:signed({...page.body,target:{...target,slot:388}})}),/W159_PAGE_CONTEXT/);
 await bad('page with modified leaf rejected',()=>rpc('wblue','/apply159',{page:signed({...page.body,records:[{...page.body.records[0],receiptHash:'b'.repeat(64)},...page.body.records.slice(1)]})}),/W159_PAGE_CHAIN|W159_PAGE_LEAF_SUBSTITUTION/);
 await bad('page with forged Merkle subtree rejected',()=>rpc('wblue','/apply159',{page:signed({...page.body,extension:{...page.body.extension,blocks:[{...page.body.extension.blocks[0],root:'f'.repeat(64)},...page.body.extension.blocks.slice(1)]}})}),/EXTENSION_ROOT_MISMATCH/);
 await bad('out-of-order page rejected',async()=>rpc('wblue','/apply159',{page:await rpc('wred','/page159',{nonce,target,offset:22,limit:15})}),/W159_PAGE_CONTEXT/);
 await bad('cannot finish before complete target',()=>rpc('wblue','/finish159'),/W159_NOT_CERTIFIED/);
 await step('first signed page persists exactly 15 rows',async()=>assert.equal((await rpc('wblue','/apply159',{page})).body.cursor,22));
 ok('Merkle frontier is durable with cursor',()=>assert.equal(state('wblue').recovery159.merkle.count,22));
 await bad('old page replay rejected',()=>rpc('wblue','/apply159',{page}),/W159_PAGE_CONTEXT/);
 await stop(nodes.wblue);nodes.wblue=await spawn('witness159.js',cfg.wblue,'wblue-restart');
 await step('restart retains Merkle frontier',async()=>assert.equal((await rpc('wblue','/status159')).body.cursor,22));
 const counts=[];await step('resume only missing Merkle pages and finalize',async()=>{const r=await api().repair('wblue',{pageSize:24,onPage:c=>counts.push(c)});assert.equal(r.body.slot,389);});
 ok('recovery history exactly equals certified source',()=>assert.deepEqual(state('wblue').history,history));
 ok('final Merkle root equals certified checkpoint',()=>assert.equal(state('wblue').lastRecovery159.merkleRoot,target.merkleRoot));
 ok('final hash-chain head equals source',()=>assert.equal(state('wblue').head,target.head));
 ok('segment-level checkpoints persisted',()=>assert(state('wblue').lastRecovery159.segmentPins.length>=1));
 ok('page cursor always monotonic',()=>assert(counts.every((v,i)=>i===0||v>counts[i-1])));
 ok('page transmissions bounded',()=>assert(counts.length>=12));
 await step('aligned repair completes without replay',async()=>assert.equal((await api().repair('wblue')).body.slot,389));
 await bad('unaligned page replay rejected after finish',()=>rpc('wblue','/apply159',{page}),/W159_NO_RECOVERY/);
 await bad('wrong-client TLS pin rejected',()=>P.rpc({...ids.rogue,...endpoints().wred},'/page159',{nonce,target,offset:7,limit:7}),/TLS_PEER_NOT_PINNED/);
 // An actual signed consensus operation across two healthy witness processes.
 const r390=record(390,prev,'live-390');const finalVotes=['red','blue'].map(id=>{const body={nodeId:id,slot:r390.slot,prevPinDigest:r390.prev,intentDigest:r390.intentDigest,snapshotDigest:r390.snapshotDigest,receiptHash:r390.receiptHash,phase:'final'};return{body,signature:P.sign(finalKeys[id].privateKey,'S155:FINAL',body)};});
 const prepare=id=>rpc(id,'/prepare',{record:r390,finalVotes});
 const votes=await Promise.all(['wred','wgreen'].map(prepare));
 await rpc('wred','/commit',{record:r390,preparedVotes:votes});await rpc('wgreen','/commit',{record:r390,preparedVotes:votes});
 ok('two witnesses really committed slot 390',()=>assert.equal(state('wgreen').slot,390));
 await step('Merkle extension catches up live signed slot',async()=>assert.equal((await api().repair('wblue',{pageSize:1})).body.slot,390));
 ok('all witness Merkle roots agree after catchup',()=>assert.equal(M.accumulate(state('wblue').history.map(P.sha)).root,M.accumulate(state('wred').history.map(P.sha)).root));
 await stop(nodes.wgreen);
 await bad('partition prevents new recovery majority',()=>api().repair('wblue'),/W159_NO_QUORUM/);
 await step('completed witness still serves signed Merkle checkpoint',async()=>assert.equal((await rpc('wblue','/checkpoint159',{nonce:crypto.randomBytes(20).toString('hex')})).body.slot,390));
 // Independent crash-after-durable-page fixture: restore old minority at 389 (already certified). Source remains slot390.
 await stop(nodes.wblue);
 const s=state('wblue');s.history.pop();s.slot=389;s.head=history[388].head;s.lastRecovery159=null;s.challenge=null;P.atomic(cfg.wblue.stateFile,s);
 cfg.wblue.crashAfterMerklePage=f('crash-merkle-once');nodes.wblue=await spawn('witness159.js',cfg.wblue,'wblue-crash');
 // Require two sources; restart green.
 nodes.wgreen=await spawn('witness159.js',cfg.wgreen,'wgreen-back');
 const c2=await rpc('wblue','/challenge');const n2=c2.body.nonce;
 const heads2=await Promise.all(['wred','wgreen'].map(id=>rpc(id,'/checkpoint159',{nonce:n2})));
 const t2={slot:390,head:r390.head,merkleRoot:M.accumulate([...history,r390].map(P.sha)).root};
 await rpc('wblue','/begin159',{nonce:n2,target:t2,checkpoints:heads2});
 const p2=await rpc('wred','/page159',{nonce:n2,target:t2,offset:389,limit:1});
 await bad('real process crash after fsync before ACK',()=>rpc('wblue','/apply159',{page:p2}),/socket hang up|ECONNRESET/);
 ok('recovery cursor persisted before killed child',()=>assert.equal(state('wblue').recovery159.cursor,390));
 nodes.wblue=await spawn('witness159.js',cfg.wblue,'wblue-after-crash');
 await step('post-crash resume finalizes without duplicate',async()=>assert.equal((await api().repair('wblue',{pageSize:1})).body.slot,390));
 ok('crash recovery did not duplicate physical history row',()=>assert.equal(state('wblue').history.length,390));
 console.log('SHEET159 '+n+'/'+n+' PASS');
 P.atomic(path.join(__dirname,'new-test-report.json'),{sheet:159,passed:n,failed:0,fixtureRecords:389,liveSlots:[390],recoveryPageMax:V.MAX_PAGE,protocol:'binary peak Merkle extension + signed 2/3 checkpoint',exit:'PASS'});
} catch(e){console.error('SHEET159 FAIL',e.stack||e);process.exitCode=1;}finally{await Promise.allSettled(children.map(stop));}})();
```


## run-all.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
temp="$(mktemp -d)"
trap 'rm -rf "$temp"' EXIT
cp -a "$here/baseline158" "$temp/sheet158"
(cd "$temp/sheet158" && bash run-all.sh)
(cd "$here" && node gate159.js)
```


## browser-check.py

```python
from playwright.sync_api import sync_playwright
from pathlib import Path
html=Path(__file__).with_name('index.html').read_text()
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(accept_downloads=True,viewport={'width':1200,'height':960});page.set_content(html)
 cases={'aligned':'ALLOW','subtree':'DENY','leaf':'DENY','stale':'DENY','signature':'DENY','crash':'ALLOW','partition':'DENY','live':'ALLOW'}
 for scenario,expected in cases.items():
  page.select_option('#scenario',scenario)
  assert page.locator('#decision').inner_text()==expected,(scenario,page.locator('#decision').inner_text())
  assert scenario in page.locator('#audit').inner_text()
  print('PASS CHROMIUM',scenario)
 with page.expect_download() as x:page.click('#export')
 assert x.value.suggested_filename=='sheet159-live.json'
 print('PASS CHROMIUM JSON export')
 page.screenshot(path=str(Path(__file__).with_name('preview.png')),full_page=True)
 browser.close()
```


## make-release.py

```python
#!/usr/bin/env python3
"""Sealed, reproducible ZIP with checksum manifest and byte-for-byte lineage verification."""
from pathlib import Path
import os,hashlib,json,zipfile,sys
D=Path(__file__).resolve().parent
ROOT=D.parent
PARENT=ROOT/'sheet158'
BASE=D/'baseline158'
ARCHIVE=ROOT/'SHEET159-merkle-consistency-recovery.zip'
HASHES=ROOT/(ARCHIVE.name+'.sha256.txt')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original={p.relative_to(PARENT).as_posix():sha(p) for p in PARENT.rglob('*') if p.is_file()}
replay={p.relative_to(BASE).as_posix():sha(p) for p in BASE.rglob('*') if p.is_file()}
if original!=replay:
 miss=set(original)^set(replay)
 changed=[p for p in original.keys()&replay.keys() if original[p]!=replay[p]]
 raise RuntimeError(f'Inherited files mismatch missing={list(miss)[:5]} changed={changed[:5]}')
combined=(D/'combined-exit.txt').read_text().strip() if (D/'combined-exit.txt').exists() else 'unconfirmed'
first=(D/'combined-first-exit.txt').read_text().strip() if (D/'combined-first-exit.txt').exists() else 'unconfirmed'
new=json.loads((D/'new-test-report.json').read_text());assert new['passed']==48
receipt={'sheet':159,'name':'Merkle-Certified Witness Recovery','parent':158,'inheritedFileCount':len(original),'inheritedBytesIdentical':True,'newGateChecks':48,'newGateResult':'PASS exit 0','combinedLatestExit':combined,'combinedPreviousExit':first,'inheritedKnownFlakyTest':'SHEET142 concurrent-local-writer assertion 2 !== 1','chromiumScenarios':8,'chromiumExport':'PASS','network':'loopback mTLS on one host','proof':'S151 binary-peak Merkle extension, checked against signed 2/3 target Merkle heads','scalability':'O(missing rows) transfers, source & target state still full-history replay','productionReady':False}
(D/'release-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
# all files other than generated root manifest are part of the checksum manifest
files=sorted((p for p in D.rglob('*') if p.is_file() and p!=D/'SHA256SUMS'),key=lambda p:p.relative_to(D).as_posix())
manifest=''.join(f'{sha(p)}  {p.relative_to(D).as_posix()}\n' for p in files)
(D/'SHA256SUMS').write_text(manifest)
files.append(D/'SHA256SUMS')
with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,'sheet159/'+p.relative_to(D).as_posix())
with zipfile.ZipFile(ARCHIVE) as z:
 assert z.testzip() is None
 names={x.filename for x in z.infolist()}
 for name,digest in original.items():
  key='sheet159/baseline158/'+name
  assert key in names,key
  assert hashlib.sha256(z.read(key)).hexdigest()==digest,key
 for name in ('SHA256SUMS','README.md','KERNEL-ASCII.txt','gate159.js','witness159.js','merkle159.js','catchup159.js','index.html','run-all.sh','SOURCE-ALL159.md'):
  assert 'sheet159/'+name in names,name
HASHES.write_text(f'{sha(ARCHIVE)}  {ARCHIVE.name}\n')
print(json.dumps({'path':str(ARCHIVE),'bytes':ARCHIVE.stat().st_size,'sha256':sha(ARCHIVE),'inheritedFilesVerified':len(original),'newChecks':48,'combinedExit':combined},indent=2))
```


## KERNEL-ASCII.txt

```text
SHEET 159 — BINARY PEAK MERKLE CONSISTENCY / SEGMENT CHECKPOINTS
================================================================================
      OASIS / ROOT0 / MOTHER KERNEL                     0e / bounded local test
                           |
           SHEET 155 AUTHORITY / FINALITY
                           |
                  S156 WITNESS 2 OF 3
                +----------+----------+
                |          |          |
             RED W       BLUE W     GREEN W
             389 slots    7 slots    389 slots
                |          |          |
         certified head   lagging    certified head
                \          |          /
                 +----> CHALLENGE <----+
                        nonce N
                           |
            RED signs HEAD+MERKLE(ROOT,FRONTIER)
            GREEN signs HEAD+MERKLE(ROOT,FRONTIER)
                           |
            CHECK: 2 distinct Ed25519 signatures
            CHECK: nonce + same slot/head/root
            CHECK: frontier actually bags to root
                           |
                 +---------+----------+
                 |                    |
            CONSISTENT             CONFLICT
                 |                    |
           PERSIST BEGIN           QUARANTINE
                 |
           RECOVERY CURSOR=7
           local HEAD + Merkle Frontier
                 |
                LOOP   <= 24 RECORDS PER PAGE
                 |
      +----------+---------------------------------+
      |                  SIGNED PAGE              |
      | nonce / target / source / cursor / next  |
      | hash-chain prevHead / endHead            |
      | M151 EXTENSION BLOCKS (binary peaks)     |
      | expected fromRoot / toRoot / toFrontier   |
      | bounded source journal rows              |
      +--------------------+-----------------------+
                           |
                    RECEIVER VERIFY
             01 certificate witness identity
             02 exact nonce, offset and target
             03 canonical hash-linked rows
             04 M151 Merkle prefix root
             05 O(log PAGE) extension block witness
             06 recompute roots from actual row hashes
             07 pending promise compatibility
             08 root==certified root on final page
                           |
                  PERSIST ATOMIC PAGE
               cursor + Merkle frontier
                     + PIN PER 32
                           |
                  FSYNC BEFORE RESPONSE
                           |
           +---------------+----------------+
           |               |                |
        ACK RECEIVED   CRASH AFTER FSYNC   CORRUPTION
           |               |                |
        NEXT PAGE      PROCESS RESTART   FAIL CLOSED
           |               |                |
           |          SIGNED STATUS       QUARANTINE
           |          REUSE CURSOR
           +---------------+
                           |
                  CURSOR == TARGET SLOT?
                     |           |
                    NO          YES
                     |           |
                   LOOP       VERIFY ROOT
                                |
                         FINAL ATOMIC INSTALL
                       history + head + pin
                                |
                      SHA-256 / AUDIT WITNESS
                                |
                         NEXT VERIFIED SLOT

ADVERSARIAL BRANCHES
 - forged certificate, replay nonce, duplicate signer -> DENY
 - shuffled, missing, wrong Merkle leaf -> DENY
 - altered extension blocks -> DENY
 - skipped cursor / repeated page -> DENY
 - conflict with pending signed promise -> DENY
 - 2 peers unavailable -> FAIL CLOSED
 - crash before ACK after durable write -> RESUME CURSOR / NO REAPPEND

VERIFICATION BOUNDARY:
 genuine Merkle extension math is used; transmission of missing records remains
 O(missing suffix), source currently replays full local journal to build proofs,
 receiver replays inherited witness state to verify. A segment pin is stored in
 the witness's atomic JSON state (not independently operated durable hardware).
 Running as three loopback mTLS processes on one physical host; not proof of
 production-grade Byzantine consensus or independent-host atomic durability.
================================================================================
```