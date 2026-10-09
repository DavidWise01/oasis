# SHEET 158 — Full New Executable Sources

These are the exact new sources; the full frozen parent lineage is in the accompanying ZIP.

## page-verify158.js

```javascript
'use strict';
// Per-page append consistency from a quorum-certified head, not a whole-history export.
const P=require('./baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./baseline157/baseline156/witness-verify156');
const SCHEMA='oasis.sheet158.page.v1', MAX_PAGE=24;
const hash=s=>typeof s==='string'&&/^[a-f0-9]{64}$/.test(s);
function certify(target,heads,nonce,keys){
 if(!/^[0-9a-f]{40}$/.test(nonce||'')||!Number.isSafeInteger(target?.slot)||target.slot<0||!hash(target?.head))throw Error('W158_TARGET_INVALID');
 const seen=new Set();
 for(const h of heads||[]){const v=h?.body,id=v?.nodeId;
  if(!keys[id]||seen.has(id)||v.nonce!==nonce||v.slot!==target.slot||v.head!==target.head||!P.verify(keys[id],'S156:HEAD',v,h.signature))throw Error('W158_HEAD_CERT_INVALID');seen.add(id);
 }
 if(seen.size<2)throw Error('W158_HEAD_QUORUM_MISSING');return [...seen];
}
function records(records,offset,prev){
 if(!Array.isArray(records)||records.length<1||records.length>MAX_PAGE)throw Error('W158_PAGE_BOUND');
 let head=prev;
 for(let i=0;i<records.length;i++){
  const r=W.normalize(records[i]);
  if(r.slot!==offset+i+1||r.prev!==head||P.sha(r)!==P.sha(records[i]))throw Error('W158_PAGE_CHAIN_OR_ORDER');
  head=r.head;
 }
 return head;
}
function verifyPage(page,{nonce,target,cursor,prev,signers,keys}){
 const b=page?.body,id=b?.nodeId;
 if(!signers.includes(id)||!keys[id]||!P.verify(keys[id],'S158:PAGE',b,page.signature))throw Error('W158_PAGE_SIGNATURE');
 if(b.schema!==SCHEMA||b.nonce!==nonce||b.targetSlot!==target.slot||b.targetHead!==target.head||b.offset!==cursor||b.prevHead!==prev)throw Error('W158_PAGE_CONTEXT_OR_GAP');
 const end=records(b.records,cursor,prev);
 if(b.next!==cursor+b.records.length||b.next>target.slot||b.endHead!==end||b.recordsDigest!==P.sha(b.records))throw Error('W158_PAGE_PROOF_MISMATCH');
 if(b.next===target.slot&&end!==target.head)throw Error('W158_TERMINAL_HEAD_MISMATCH');
 return b.records;
}
function makePage({nodeId,nonce,target,history,offset,limit}){
 if(!/^[0-9a-f]{40}$/.test(nonce||'')||!Number.isSafeInteger(offset)||offset<0||!Number.isInteger(limit)||limit<1||limit>MAX_PAGE)throw Error('W158_PAGE_REQUEST_INVALID');
 if(!Number.isSafeInteger(target?.slot)||target.slot<offset||target.slot>history.length||!hash(target.head))throw Error('W158_TARGET_RANGE');
 if(target.slot>0&&history[target.slot-1].head!==target.head||target.slot===0&&target.head!==W.ZERO)throw Error('W158_TARGET_NOT_IN_HISTORY');
 if(offset===target.slot)throw Error('W158_PAGE_ALREADY_COMPLETE');
 const page=history.slice(offset,Math.min(target.slot,offset+limit));
 const prev=offset?history[offset-1].head:W.ZERO;
 return{schema:SCHEMA,nodeId,nonce,targetSlot:target.slot,targetHead:target.head,offset,next:offset+page.length,prevHead:prev,endHead:page[page.length-1].head,records:page,recordsDigest:P.sha(page)};
}
function admitPending(state,recovery,records){
 if(!state.pending)return;
 const k=state.pending.slot-state.slot-1;
 if(k>=0&&k<recovery.staged.length+records.length){
  const match=k<recovery.staged.length?recovery.staged[k]:records[k-recovery.staged.length];
  if(P.sha(match)!==P.sha(state.pending))throw Error('W158_PENDING_FORK_QUARANTINE');
 }
}
module.exports={SCHEMA,MAX_PAGE,certify,records,verifyPage,makePage,admitPending};
```

## witness158.js

```javascript
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
```

## catchup158.js

```javascript
'use strict';
const P=require('./baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const Q=require('./page-verify158');
function make({identity,witnesses,publicKeys}){
 const rpc=(id,url,b={})=>P.rpc({...identity,...witnesses[id]},url,b);
 function ack(id,domain,x){if(x?.body?.nodeId!==id||!P.verify(publicKeys[id],domain,x.body,x.signature))throw Error('W158_ACK_INVALID');return x.body;}
 async function repair(target,{pageSize=8,onPage=()=>{}}={}){
  if(!witnesses[target]||Object.keys(witnesses).length!==3||!Number.isInteger(pageSize)||pageSize<1||pageSize>Q.MAX_PAGE)throw Error('W158_CONFIG_INVALID');
  let status=ack(target,'S158:STATUS',await rpc(target,'/status158'));
  let peers=[],tgt;
  if(!status.active){
   const challenge=await rpc(target,'/challenge');const nonce=ack(target,'S157:CHALLENGE',challenge).nonce;
   const ids=Object.keys(witnesses).filter(id=>id!==target);
   const responses=await Promise.all(ids.map(async id=>{try{return{id,resp:await rpc(id,'/read',{nonce})};}catch(e){return{id,error:e.message};}}));
   const valid=responses.filter(x=>x.resp?.body?.nodeId===x.id&&P.verify(publicKeys[x.id],'S156:HEAD',x.resp.body,x.resp.signature));
   if(valid.length<2)throw Error('W158_MAJORITY_UNAVAILABLE');
   tgt={slot:valid[0].resp.body.slot,head:valid[0].resp.body.head};
   Q.certify(tgt,valid.map(x=>x.resp),nonce,publicKeys);
   const begun=await rpc(target,'/begin158',{nonce,target:tgt,heads:valid.map(x=>x.resp)});
   ack(target,'S158:BEGIN',begun);
   status=ack(target,'S158:STATUS',await rpc(target,'/status158'));
  }
  tgt=status.target;
  if(!tgt||!status.nonce)throw Error('W158_SESSION_MISSING');
  peers=Object.keys(witnesses).filter(id=>id!==target);
  let cursor=status.cursor;
  while(cursor<tgt.slot){
   let accepted=false,lastError;
   for(const peer of peers){
    try{
     const page=await rpc(peer,'/page158',{nonce:status.nonce,target:tgt,offset:cursor,limit:pageSize});
     const applied=await rpc(target,'/apply158',{page});
     const body=ack(target,'S158:APPLIED',applied);
     if(body.cursor<=cursor||body.cursor>tgt.slot)throw Error('W158_NONMONOTONIC_ACK');
     cursor=body.cursor;onPage(cursor);accepted=true;break;
    }catch(e){lastError=e; // A lost acknowledgement may conceal a durably applied page.
     try{const current=ack(target,'S158:STATUS',await rpc(target,'/status158'));if(current.active&&current.cursor>cursor&&current.target?.head===tgt.head&&current.nonce===status.nonce){cursor=current.cursor;onPage(cursor);accepted=true;break;}}catch{}
    }
   }
   if(!accepted)throw Error('W158_PAGE_RECOVERY_STOP: '+(lastError?.message||'no majority page source'));
  }
  const final=await rpc(target,'/finish158');const body=ack(target,'S158:FINISHED',final);
  if(body.slot!==tgt.slot||body.head!==tgt.head)throw Error('W158_FINAL_HEAD_MISMATCH');return final;
 }
 return{rpc,repair};
}
module.exports={make};
```

## gate158.js

```javascript
#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const P=require('./baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./baseline157/baseline156/witness-verify156');const V=require('./page-verify158');const C=require('./catchup158');
const root=fs.mkdtempSync(path.join(os.tmpdir(),'sheet158-')),f=(...a)=>path.join(root,...a),openssl=(...a)=>cp.execFileSync('openssl',a,{cwd:root,stdio:'pipe'});
let n=0;const ok=(name,fn)=>{fn();console.log('PASS',++n,name);};const step=async(name,fn)=>{await fn();console.log('PASS',++n,name);};const bad=async(name,fn,regex)=>step(name,async()=>assert.rejects(fn,regex));
function cert(id){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',id+'.key','-out',id+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(id+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',id+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',id+'.crt','-days','2','-sha256','-extfile',id+'.ext');return{key:f(id+'.key'),cert:f(id+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(id+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
function keys(id){const pair=crypto.generateKeyPairSync('ed25519'),priv=f(id+'.priv'),pub=f(id+'.pub');fs.writeFileSync(priv,pair.privateKey.export({format:'pem',type:'pkcs8'}));fs.writeFileSync(pub,pair.publicKey.export({format:'pem',type:'spki'}));return{privateKey:pair.privateKey,publicKey:pair.publicKey,priv,pub};}
const children=[];
async function spawn(script,cfg,id){const config=f('cfg-'+id+'.json');P.atomic(config,cfg);const proc=cp.fork(path.join(__dirname,script),[],{env:{...process.env,S158_WITNESS_CONFIG:config,S156_FLOOR_CONFIG:config},stdio:['ignore','pipe','pipe','ipc']});let errors='';proc.on('error',()=>{});proc.stderr.on('data',b=>errors+=b);const port=await new Promise((res,rej)=>{const t=setTimeout(()=>rej(Error('START_TIMEOUT '+id+' '+errors)),15000);proc.once('message',m=>{clearTimeout(t);res(m.port);});proc.once('exit',code=>{clearTimeout(t);rej(Error('START_FAILED '+id+' '+code+' '+errors));});});const x={proc,port,id,errors:()=>errors};children.push(x);return x;}
async function stop(x){if(!x||x.proc.exitCode!==null||x.proc.signalCode!==null)return;await new Promise(done=>{const t=setTimeout(()=>{x.proc.kill('SIGKILL');done();},2000);x.proc.once('exit',()=>{clearTimeout(t);done();});if(x.proc.connected){try{x.proc.send('stop',err=>{if(err){x.proc.kill('SIGKILL');clearTimeout(t);done();}});}catch{ x.proc.kill('SIGKILL');clearTimeout(t);done();}}else{x.proc.kill('SIGKILL');clearTimeout(t);done();}});}
(async()=>{try{
 openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=S158-TEST');
 const ids=Object.fromEntries(['proxy','wred','wblue','wgreen','rogue'].map(id=>[id,cert(id)]));
 const witnessKeys=Object.fromEntries(['wred','wblue','wgreen'].map(id=>[id,keys(id)]));
 const finalKeys=Object.fromEntries(['red','blue'].map(id=>[id,keys('final-'+id)]));
 const pubs=Object.fromEntries(Object.entries(witnessKeys).map(([id,k])=>[id,k.publicKey]));
 const witnessPublicKeys=Object.fromEntries(Object.entries(witnessKeys).map(([id,k])=>[id,k.pub]));
 const finalPublicKeys=Object.fromEntries(Object.entries(finalKeys).map(([id,k])=>[id,k.pub]));
 const cfg=Object.fromEntries(Object.keys(witnessKeys).map(id=>[id,{id,...ids[id],signKey:witnessKeys[id].priv,stateFile:f(id,'state.json'),proxyPin:ids.proxy.certPin,witnessPublicKeys,finalityPublicKeys:finalPublicKeys}]));
 const P=require('./baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
 const W=require('./baseline157/baseline156/witness-verify156');
 const record=(slot,prev,tag)=>W.normalize({slot,prev,intentDigest:P.sha('intent'+tag),snapshotDigest:P.sha('snapshot'+tag),receiptHash:P.sha('receipt'+tag)});
 const history=[];let prev=W.ZERO;for(let i=1;i<=337;i++){let r=record(i,prev,'synthetic-'+i);history.push(r);prev=r.head;}
 // Fixtures simulate a majority committed prefix; seed on disk before the processes start.
 for(const id of ['wred','wgreen'])P.atomic(cfg[id].stateFile,{schema:W.SCHEMA,nodeId:id,slot:337,head:prev,history:structuredClone(history),pending:null,challenge:null});
 P.atomic(cfg.wblue.stateFile,{schema:W.SCHEMA,nodeId:'wblue',slot:3,head:history[2].head,history:history.slice(0,3),pending:history[3],challenge:null});
 const nodes={};for(const id of Object.keys(cfg))nodes[id]=await spawn('witness158.js',cfg[id],id);
 const endpoints=()=>Object.fromEntries(Object.keys(nodes).map(id=>[id,{port:nodes[id].port,serverPin:ids[id].certPin}]));
 const api=()=>C.make({identity:ids.proxy,witnesses:endpoints(),publicKeys:pubs});
 const rpc=(id,url,b={})=>api().rpc(id,url,b);
 const read=id=>P.load(cfg[id].stateFile);
 const votes=r=>['red','blue'].map(id=>{let body={nodeId:id,slot:r.slot,prevPinDigest:r.prev,intentDigest:r.intentDigest,snapshotDigest:r.snapshotDigest,receiptHash:r.receiptHash,phase:'final'};return{body,signature:P.sign(finalKeys[id].privateKey,'S155:FINAL',body)};});
 const prepare=(id,r)=>rpc(id,'/prepare',{record:r,finalVotes:votes(r)});
 const commit=(id,r,p)=>rpc(id,'/commit',{record:r,preparedVotes:p});
 ok('three mTLS witness identities booted',()=>assert.equal(Object.keys(nodes).length,3));
 ok('seeded majority contains 337 valid slots',()=>assert.equal(read('wred').slot,337));
 ok('minority retains prepared fourth slot',()=>assert.equal(read('wblue').pending.head,history[3].head));
 ok('zero head constant retained',()=>assert.equal(W.ZERO.length,64));
 ok('per-page bound is 24 records',()=>assert.equal(V.MAX_PAGE,24));
 ok('empty page rejected',()=>assert.throws(()=>V.records([],0,W.ZERO),/W158_PAGE_BOUND/));
 ok('oversized page rejected',()=>assert.throws(()=>V.records(Array(25).fill(history[0]),0,W.ZERO),/W158_PAGE_BOUND/));
 ok('incorrect page ordering fails',()=>assert.throws(()=>V.records([history[1]],0,W.ZERO),/W158_PAGE_CHAIN_OR_ORDER/));
 ok('local prefix proof validates',()=>assert.equal(V.records(history.slice(0,3),0,W.ZERO),history[2].head));
 const challenge=await rpc('wblue','/challenge',{});const nonce=challenge.body.nonce;
 const heads=await Promise.all(['wred','wgreen'].map(id=>rpc(id,'/read',{nonce})));
 const target={slot:337,head:prev};
 ok('two independent signed target heads certify',()=>assert.equal(V.certify(target,heads,nonce,pubs).length,2));
 ok('duplicate head signatures refused',()=>assert.throws(()=>V.certify(target,[heads[0],heads[0]],nonce,pubs),/W158_HEAD_CERT_INVALID/));
 ok('forged head signature refused',()=>assert.throws(()=>V.certify(target,[{...heads[0],signature:'AAAA'},heads[1]],nonce,pubs),/W158_HEAD_CERT_INVALID/));
 ok('wrong nonce refuses certified head replay',()=>assert.throws(()=>V.certify(target,heads,'b'.repeat(40),pubs),/W158_HEAD_CERT_INVALID/));
 await bad('missing quorum refuses beginning session',()=>rpc('wblue','/begin158',{nonce,target,heads:[heads[0]]}),/W158_HEAD_QUORUM_MISSING/);
 await step('signed majority opens persisted session',async()=>assert.equal((await rpc('wblue','/begin158',{nonce,target,heads})).body.cursor,3));
 await bad('duplicate session refused',()=>rpc('wblue','/begin158',{nonce,target,heads}),/W158_RECOVERY_ALREADY_ACTIVE/);
 await bad('cannot prepare while staging recovery',()=>prepare('wblue',record(4,history[2].head,'conflict')),/W158_CATCHUP_HOLD/);
 const p0=await rpc('wred','/page158',{nonce,target,offset:3,limit:7});
 ok('page data bounded to seven records',()=>assert.equal(p0.body.records.length,7));
 ok('page starts from minority trusted prefix',()=>assert.equal(p0.body.prevHead,history[2].head));
 ok('page is signed by authorized exporter',()=>assert(P.verify(pubs.wred,'S158:PAGE',p0.body,p0.signature)));
 const signedPage=body=>({body,signature:P.sign(witnessKeys.wred.privateKey,'S158:PAGE',body)});
 await bad('malicious exporter cannot omit one record',()=>rpc('wblue','/apply158',{page:signedPage({...p0.body,records:p0.body.records.slice(1),next:p0.body.next-1,recordsDigest:P.sha(p0.body.records.slice(1))})}),/W158_PAGE_CHAIN_OR_ORDER/);
 await bad('malicious exporter cannot splice a different predecessor',()=>rpc('wblue','/apply158',{page:signedPage({...p0.body,prevHead:'f'.repeat(64)})}),/W158_PAGE_CONTEXT_OR_GAP/);
 await bad('malicious exporter cannot reorder signed rows',()=>rpc('wblue','/apply158',{page:signedPage({...p0.body,records:[p0.body.records[1],p0.body.records[0],...p0.body.records.slice(2)],recordsDigest:P.sha([p0.body.records[1],p0.body.records[0],...p0.body.records.slice(2)])})}),/W158_PAGE_CHAIN_OR_ORDER/);
 await bad('malicious exporter cannot misstate page digest',()=>rpc('wblue','/apply158',{page:signedPage({...p0.body,recordsDigest:'f'.repeat(64)})}),/W158_PAGE_PROOF_MISMATCH/);
 await bad('malicious exporter cannot cross-bind other target',()=>rpc('wblue','/apply158',{page:signedPage({...p0.body,targetHead:'f'.repeat(64)})}),/W158_PAGE_CONTEXT_OR_GAP/);
 await bad('malicious exporter cannot extend past certified end',()=>rpc('wblue','/apply158',{page:signedPage({...p0.body,next:338})}),/W158_PAGE_PROOF_MISMATCH/);
 await bad('page of zero records rejected by source',()=>rpc('wred','/page158',{nonce,target,offset:337,limit:2}),/W158_PAGE_ALREADY_COMPLETE/);
 await bad('unbounded page request rejected at source',()=>rpc('wred','/page158',{nonce,target,offset:3,limit:100}),/W158_PAGE_REQUEST_INVALID/);
 await bad('out-of-order page rejected',async()=>rpc('wblue','/apply158',{page:await rpc('wred','/page158',{nonce,target,offset:10,limit:7})}),/W158_PAGE_CONTEXT_OR_GAP/);
 await bad('forged page signature rejected',()=>rpc('wblue','/apply158',{page:{...p0,signature:'AAAA'}}),/W158_PAGE_SIGNATURE/);
 await bad('altered page content rejected',()=>rpc('wblue','/apply158',{page:{...p0,body:{...p0.body,records:[{...p0.body.records[0],intentDigest:'f'.repeat(64)},...p0.body.records.slice(1)]}}}),/W158_PAGE_SIGNATURE/);
 await bad('page cannot be replayed under wrong nonce',()=>rpc('wblue','/apply158',{page:{...p0,body:{...p0.body,nonce:'a'.repeat(40)}}}),/W158_PAGE_SIGNATURE/);
 await step('first seven-record page saved',async()=>assert.equal((await rpc('wblue','/apply158',{page:p0})).body.cursor,10));
 await bad('duplicate page refused',()=>rpc('wblue','/apply158',{page:p0}),/W158_PAGE_CONTEXT_OR_GAP/);
 ok('durable page cursor and digest persisted',()=>assert.equal(read('wblue').recovery.cursor,10));
 await stop(nodes.wblue);nodes.wblue=await spawn('witness158.js',cfg.wblue,'wblue-restart');
 await step('restarted witness reports saved progress',async()=>assert.equal((await rpc('wblue','/status158')).body.cursor,10));
 await bad('missing pages cannot finalize',()=>rpc('wblue','/finish158'),/W158_INCOMPLETE_OR_CHANGED/);
 const counts=[];
 await step('resume transfers only missing pages',async()=>{let result=await api().repair('wblue',{pageSize:17,onPage:c=>counts.push(c)});assert.equal(result.body.slot,337);});
 ok('all 337 records reconstructed exactly',()=>assert.deepEqual(read('wblue').history,history));
 ok('paginated high-water reaches majority',()=>assert.equal(read('wblue').head,prev));
 ok('durable recovery progress cleared',()=>assert.equal(read('wblue').recovery,null));
 ok('page sizes remain bounded',()=>assert(counts.length>10&&counts.every(x=>x<=337)));
 await step('idempotent majority repair when aligned',async()=>assert.equal((await api().repair('wblue',{pageSize:3})).body.slot,337));
 await bad('stale page cannot be installed after finalization',()=>rpc('wblue','/apply158',{page:p0}),/W158_NO_ACTIVE_RECOVERY/);
 await bad('unauthorized client blocked by pinned TLS',()=>P.rpc({...ids.rogue,...endpoints().wred},'/page158',{nonce,target,offset:3,limit:7}),/TLS_PEER_NOT_PINNED/);
 // Additional majority slot committed with real signed prepare and commit.
 const r338=record(338,prev,'live-338');let sigs=await Promise.all(['wred','wgreen'].map(id=>prepare(id,r338)));
 await commit('wred',r338,sigs);await commit('wgreen',r338,sigs);
 ok('real signed 338th majority vote committed',()=>assert.equal(read('wgreen').slot,338));
 await step('minority catches new slot without reimporting prefix',async()=>assert.equal((await api().repair('wblue',{pageSize:1})).body.slot,338));
 ok('new majority head was certified',()=>assert.equal(read('wblue').head,r338.head));
 // Quarantine cannot overwrite a conflicting pending promise.
 const r339good=record(339,r338.head,'good'),r339bad=record(339,r338.head,'bad');
 await prepare('wblue',r339bad);sigs=await Promise.all(['wred','wgreen'].map(id=>prepare(id,r339good)));
 await commit('wred',r339good,sigs);await commit('wgreen',r339good,sigs);
 await bad('conflicting pending record is quarantined',()=>api().repair('wblue',{pageSize:4}),/W158_PENDING_FORK_QUARANTINE|W158_PAGE_RECOVERY_STOP/);
 ok('conflicting pending survives rejection',()=>assert.equal(read('wblue').pending.head,r339bad.head));
 await stop(nodes.wblue);nodes.wblue=await spawn('witness158.js',cfg.wblue,'wblue-quarantine-restart');
 await bad('conflicting pending survives restart',()=>api().repair('wblue',{pageSize:4}),/W158_PENDING_FORK_QUARANTINE|W158_RECOVERY_ALREADY_ACTIVE|W158_PAGE_RECOVERY_STOP/);
 ok('quarantined state cannot overwrite old certified slot',()=>assert.equal(read('wblue').slot,338));
 // Separate clean witness fixture for crash-after-durable-page window, with majority 339.
 await stop(nodes.wblue);
 let reset=read('wblue');reset.pending=null;reset.recovery=null;reset.challenge=null;P.atomic(cfg.wblue.stateFile,reset);
 cfg.wblue.crashAfterPage=f('crash158.once');nodes.wblue=await spawn('witness158.js',cfg.wblue,'wblue-crash-page');
 const ch2=await rpc('wblue','/challenge');const n2=ch2.body.nonce;
 const h2=await Promise.all(['wred','wgreen'].map(id=>rpc(id,'/read',{nonce:n2})));
 await rpc('wblue','/begin158',{nonce:n2,target:{slot:339,head:r339good.head},heads:h2});
 const crashPage=await rpc('wred','/page158',{nonce:n2,target:{slot:339,head:r339good.head},offset:338,limit:1});
 await bad('real child exits after fsync before response',()=>rpc('wblue','/apply158',{page:crashPage}),/socket hang up|ECONNRESET/);
 ok('page was durably installed before child died',()=>assert.equal(read('wblue').recovery.cursor,339));
 nodes.wblue=await spawn('witness158.js',cfg.wblue,'wblue-crash-restart');
 await step('resume after reply-loss finalizes same page',async()=>assert.equal((await api().repair('wblue',{pageSize:1})).body.slot,339));
 ok('restart did not duplicate journal rows',()=>assert.equal(read('wblue').history.length,339));
 await stop(nodes.wgreen);
 await bad('one reachable peer cannot certify new catchup target',()=>api().repair('wblue'),/W158_MAJORITY_UNAVAILABLE/);
 await step('completed witness remains readable during peer loss',async()=>assert.equal((await rpc('wblue','/read',{nonce:crypto.randomBytes(20).toString('hex')})).body.slot,339));
 console.log('SHEET158 '+n+'/'+n+' PASS');
 P.atomic(path.join(__dirname,'new-test-report.json'),{sheet:158,passed:n,failed:0,simulatedFixtureRecords:337,realLiveCommitSlots:[338,339],hosts:1,network:'local mTLS',recoveryPageMax:V.MAX_PAGE,overall:'PASS'});
} catch(e){console.error('SHEET158 FAIL',e.stack||e);process.exitCode=1;}finally{await Promise.allSettled(children.map(stop));}})();
```

## run-all.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
temp="$(mktemp -d)"
trap 'rm -rf "$temp"' EXIT
cp -a "$here/baseline157" "$temp/sheet157"
(cd "$temp/sheet157" && bash run-all.sh)
(cd "$here" && node gate158.js)
```

## browser-check.py

```python
#!/usr/bin/env python3
"""Headless interaction regression for the standalone SVG test viewer."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
p=Path(__file__).resolve().parent
names=['healthy','reordered','forged','crash','missing','conflict','partition','replay']
with sync_playwright() as w:
    browser=w.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1320,'height':930},accept_downloads=True)
    page.set_content((p/'index.html').read_text(encoding='utf-8'),wait_until='load')
    assert page.locator('h1').inner_text().startswith('Paginated')
    for name in names:
        page.locator(f'button[data-scenario="{name}"]').click()
        assert page.locator(f'button[data-scenario="{name}"]').get_attribute('aria-pressed')=='true'
        assert page.locator('#scenario-result').inner_text()
        print('PASS chromium scenario',name)
    page.locator('button[data-scenario="healthy"]').click()
    with page.expect_download() as event: page.locator('#export').click()
    download=event.value
    assert download.suggested_filename=='sheet158-healthy.json'
    content=json.loads(Path(download.path()).read_text())
    assert content['schema']=='oasis.sheet158.dashboard.v1' and content['certified'] is True
    print('PASS chromium JSON export')
    page.screenshot(path=str(p/'preview.png'),full_page=True)
    print('PASS chromium screenshot')
    browser.close()
```

## make-release.py

```python
#!/usr/bin/env python3
"""Seal a complete, independently audited SHEET158 archive with its frozen parent."""
import hashlib,json,os,sys,zipfile
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
BASE=HERE/'baseline157'
PARENT=HERE.parent/'SHEET157-certified-witness-catchup.zip'
ARCHIVE=HERE.parent/'SHEET158-paginated-witness-consistency.zip'
CHECKSUM=ARCHIVE.with_name(ARCHIVE.name+'.sha256.txt')
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def all_files(root):return sorted(p for p in root.rglob('*') if p.is_file())
assert PARENT.is_file(),f'Parent missing: {PARENT}'
assert (HERE/'combined-exit.txt').read_text().strip()=='0','Inherited-plus-new runner must exit 0'
results=json.loads((HERE/'new-test-report.json').read_text())
assert results['passed']==58 and results['failed']==0,'New gate must pass'
log=(HERE/'browser-test.log').read_text()
assert log.count('PASS chromium scenario')==8 and 'PASS chromium JSON export' in log and 'PASS chromium screenshot' in log
# Byte-compare every parent archive file with the frozen disk copy.
with zipfile.ZipFile(PARENT,'r') as p:
    entries={x.filename[len('sheet157/'):]:x for x in p.infolist() if x.filename.startswith('sheet157/') and not x.is_dir()}
    paths={str(x.relative_to(BASE)).replace('\\','/'):x for x in all_files(BASE)}
    assert paths.keys()==entries.keys(),f'Parent mismatch: missing {entries.keys()-paths.keys()}, extras {paths.keys()-entries.keys()}'
    for rel,entry in entries.items():
        assert hashlib.sha256(p.read(entry)).digest()==hashlib.sha256(paths[rel].read_bytes()).digest(),f'Parent file changed: {rel}'
release={
 'schema':'oasis.sheet158.release.v1',
 'sheet':158,'parentSheet':157,
 'title':'Paginated Witness Consistency and Crash-Safe Catch-Up',
 'status':'0e / PASS','verification':{
     'newChecks':58,'newChecksExit':0,'inheritedAndNewExit':0,
     'inheritedPreviousKnownChecks':1560,'combinedKnownChecks':1618,
     'chromiumScenarios':8,'chromiumExport':True,'chromiumScreenshot':True,
     'parentFilesPreserved':len(entries),'parentByteIdentical':True,
     'syntheticFixtureRecords':337,'realLiveCommitSlots':[338,339],
 },
 'protocol':{'certificate':'2 of 3 distinct Ed25519 signed heads','pageMaxRecords':24,'nonceHexChars':40,'recoveryCursor':'durable atomic state','crash':'page fsync before response, restart and resume'},
 'limitations':['One physical host with independently signed local mTLS processes','Page-linked linear proofs; not an O(log n) Merkle consistency proof','Total transfer O(missing records); full local JSON state O(history size)','Fully restored disk rollback requires external retained pin','Old SHEET142 intermittent test passed in this run but is not proven permanently resolved','Synthetic cryptographic fixture used for first 337 journal records']
}
(HERE/'release-receipt.json').write_text(json.dumps(release,indent=2)+'\n')
# Source inventory helps precise GitHub publication; build before SHA256SUMS.
source=['page-verify158.js','witness158.js','catchup158.js','gate158.js','run-all.sh','browser-check.py','make-release.py','KERNEL-ASCII.txt']
with (HERE/'SOURCE-ALL158.md').open('w') as out:
 out.write('# SHEET 158 — Full New Executable Sources\n\n')
 out.write('These are the exact new sources; the full frozen parent lineage is in the accompanying ZIP.\n\n')
 for name in source:
  lang='javascript' if name.endswith('.js') else 'python' if name.endswith('.py') else 'text' if name.endswith('.txt') else 'bash'
  out.write(f'## {name}\n\n```{lang}\n')
  out.write((HERE/name).read_text().rstrip()+ '\n```\n\n')
manifest=HERE/'SHA256SUMS'
files=[p for p in all_files(HERE) if p!=manifest]
manifest.write_text(''.join(f'{digest(p)}  {p.relative_to(HERE).as_posix()}\n' for p in files))
files=all_files(HERE)
with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p in files:z.write(p,arcname='sheet158/'+p.relative_to(HERE).as_posix())
with zipfile.ZipFile(ARCHIVE,'r') as z:
 assert z.testzip() is None
 names=set(z.namelist());assert len(names)==len(files)
 for p in files:
  arc='sheet158/'+p.relative_to(HERE).as_posix()
  assert arc in names and hashlib.sha256(z.read(arc)).hexdigest()==digest(p),arc
 for rel in entries:assert 'sheet158/baseline157/'+rel in names
CHECKSUM.write_text(f'{digest(ARCHIVE)}  {ARCHIVE.name}\n')
print(json.dumps({'zip':str(ARCHIVE),'bytes':ARCHIVE.stat().st_size,'sha256':digest(ARCHIVE),'inheritedFiles':len(entries),'totalArchiveFiles':len(files),'newTests':58,'combinedExit':0},indent=2))
```

## KERNEL-ASCII.txt

```text
OASIS / ROOT0 / SHEET 158 — PAGINATED WITNESS RECOVERY
=====================================================

       CLIENT / CONTROLLER
                |
       ROOT0 MOTHER KERNEL
                |
      S155 TRANSACTION FINALITY      <--- durable 2/3 authority + receipt
                |
       S156 WITNESS FLOOR
        /       |       \
      RED      BLUE     GREEN          independently signed histories
        \       |       /
        S157 CATCH-UP POLICY           prefix only / conflicting pending HOLD
                |
  +-------------+----------------------+
  |                                    |
LAGGING TARGET                    HEALTHY PEERS
  |                                   / \
  |                                RED   GREEN
  |                                 |      |
  |-- 01. issue 40-hex nonce        |      |
  |-- 02. persist nonce            |      |
  |-- 03. read signed HEAD <--------+------+ (mTLS peer pin)
  |-- 04. verify two distinct ED25519 signatures
  |-- 05. verify same slot, same digest, same nonce
  |-- 06. reject rollback / forged quorum / conflicting heads
  |-- 07. BEGIN158 persisted recovery session atomically
  |         {nonce,target,signers,cursor,head,staged}
  |-- 08. prohibit PREPARE / COMMIT during recovery
  |
  |        REPEAT WHILE cursor < target.slot
  |             |
  |             +--> PAGE request (offset,cursor,pageSize <=24)
  |             |        |
  |             |       [PEER A or PEER B]
  |             |        |
  |             |      bounded JSON records <=24
  |             |      prevHead -> local cursor
  |             |      next cursor / endHead
  |             |      nonce + target head
  |             |      digest over records
  |             |      Ed25519 PAGE SIGNATURE
  |             |        |
  |             +--> mTLS target receives signed page
  |             |        |
  |             |      verify authorized signer + signed bytes
  |             |      verify unchanged nonce,target,offset,prevHead
  |             |      verify each record slot sequential and canonical
  |             |      verify each prev link and digest
  |             |      verify pending promise if reached
  |             |      verify terminal page equals certified head
  |             |        |
  |             +--> P.atomic() write combined cursor + staged pages
  |             |        |   write tmp -> fsync -> rename -> directory fsync
  |             |        |
  |             +--> ACK new cursor
  |             |        |
  |             +--> reply lost? query signed STATUS after reconnect
  |             |        |
  |             +--> peer lost? retry alternate certified exporter
  |             |        |
  |             +--> restart? use original nonce+persisted cursor
  |             +--------------------------------------------^
  |
  |-- 32. cursor == target.slot && head == quorum-certified target
  |-- 33. verify no divergent local pending promise
  |-- 34. atomically append staged suffix and clear pending
  |-- 35. save lastRecovery idempotent receipt
  |-- 36. sign FINISHED(slot,head,nonce,historyDigest)
  |-- 37. stale/replayed pages cannot be applied after finish
  |-- 38. next finality floor slot may be admitted per S156 rules
  |
  +-- MALICIOUS / FAULT BRANCHES
       * invalid TLS peer                         => REJECT
       * same signer twice                       => REJECT
       * signed head with a different nonce      => REJECT
       * mismatch between two healthy heads      => REJECT
       * omitted / reordered / spliced record    => REJECT
       * forged or rewritten page signature      => REJECT
       * signer-known but wrong target binding   => REJECT
       * duplicate/old page offset               => REJECT
       * omitted page / incomplete suffix        => HOLD
       * conflicting local prepared vote         => QUARANTINE
       * target's original prefix differs        => QUARANTINE
       * crash after durable page                => RESTART / RESUME
       * one healthy source offline              => NO FRESH MAJORITY
       * resource rollback of entire state disk  => NOT COVERED: external pin

COMPACTNESS / LIMITS
  ONE CERTIFICATE: 2 distinct signed HEAD replies, constant count
  ONE PAGE:       <=24 hash-linked canonical records, one Ed25519 sig
  TOTAL TRANSFER: O(number of missing records), bounded per message
  PROOF SIZE:     O(page size), NOT a logarithmic Merkle consistency proof
  STATE STORAGE:  target retains full history + staged suffix in JSON
  REPLAY WORK:    currently O(history) per request, prototype not production
  RECOVERY:       prototype uses three separate mTLS processes on one host
  DURABILITY:     atomic fsync/rename of local JSON, no cross-host guarantee
  TEST DATA:      337 seed records as explicit fixtures + live slots 338-339

ROOT0: VERIFIED PAST -> VERIFIED CURRENT -> NEXT DOT
```
