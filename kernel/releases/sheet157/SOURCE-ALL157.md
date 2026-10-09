# SHEET 157 — Complete New Authored Sources

The frozen SHEET156 lineage remains in the full ZIP; this listing contains the new SHEET157 implementation and tests.

## witness157.js

```javascript
'use strict';
const fs=require('node:fs');
const P=require('./baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./baseline156/witness-verify156');
const V=require('./catchup-verify157');
const crypto=require('node:crypto');
const cfg=P.load(process.env.S157_WITNESS_CONFIG),priv=fs.readFileSync(cfg.signKey);
const finalPubs=Object.fromEntries(Object.entries(cfg.finalityPublicKeys).map(([k,p])=>[k,fs.readFileSync(p)]));
const witnessPubs=Object.fromEntries(Object.entries(cfg.witnessPublicKeys).map(([k,p])=>[k,fs.readFileSync(p)]));
function fresh(){return{schema:W.SCHEMA,nodeId:cfg.id,slot:0,head:W.ZERO,history:[],pending:null,challenge:null};}
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
 const s=state();const nonce=s.challenge?.nonce;
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
const server=P.serve(cfg.key,cfg.cert,cfg.ca,(req,b)=>{P.peer(req,cfg.proxyPin);if(req.url==='/read')return read(b);if(req.url==='/prepare')return prepare(b);if(req.url==='/commit')return commit(b);if(req.url==='/challenge')return challenge();if(req.url==='/export')return exported(b);if(req.url==='/catchup')return catchup(b);throw Error('W157_ROUTE_INVALID');});
process.on('message',v=>{if(v==='stop')server.close(()=>process.exit(0));});
module.exports={state,prepare,commit};
```

## catchup-verify157.js

```javascript
'use strict';
// SHEET 157: no witness may install unproven history or erase a conflicting promise.
const P=require('./baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./baseline156/witness-verify156');
const crypto=require('node:crypto');
const SCHEMA='oasis.sheet157.catchup.v1';
function historyState(history){
 if(!Array.isArray(history)||history.length>256)throw Error('W157_HISTORY_SIZE_BOUND');
 let head=W.ZERO;
 for(let i=0;i<history.length;i++){
  const v=W.normalize(history[i]);
  if(v.slot!==i+1||v.prev!==head||v.head!==history[i].head||P.sha(history[i])!==P.sha(v))throw Error('W157_HISTORY_INVALID');
  head=v.head;
 }
 return{slot:history.length,head};
}
function certify(body,heads,exported,nonce,publicKeys){
 if(!/^[a-f0-9]{40}$/.test(nonce))throw Error('W157_CHALLENGE_INVALID');
 if(!Number.isSafeInteger(body?.slot)||body.slot<0||!/^([a-f0-9]{64})$/.test(body.head))throw Error('W157_HEAD_INVALID');
 const seen=new Set();
 for(const h of heads||[]){
  const v=h?.body,id=v?.nodeId;
  if(!publicKeys[id]||seen.has(id)||v.nonce!==nonce||v.slot!==body.slot||v.head!==body.head||!P.verify(publicKeys[id],'S156:HEAD',v,h.signature))throw Error('W157_MAJORITY_HEAD_INVALID');
  seen.add(id);
 }
 if(seen.size<2)throw Error('W157_MAJORITY_HEAD_MISSING');
 const ex=exported?.body;
 if(!ex||ex.schema!==SCHEMA||!seen.has(ex.nodeId)||ex.nonce!==nonce||ex.slot!==body.slot||ex.head!==body.head||!publicKeys[ex.nodeId]||!P.verify(publicKeys[ex.nodeId],'S157:EXPORT',ex,exported.signature))throw Error('W157_EXPORT_INVALID');
 const validated=historyState(ex.history);
 if(validated.slot!==body.slot||validated.head!==body.head)throw Error('W157_EXPORT_HISTORY_MISMATCH');
 return ex.history;
}
function admission(local,remote){
 if(remote.length<local.history.length)throw Error('W157_ROLLBACK_NOT_ALLOWED');
 for(let i=0;i<local.history.length;i++)if(P.sha(remote[i])!==P.sha(local.history[i]))throw Error('W157_FORK_QUARANTINE');
 if(local.pending){
  const p=W.normalize(local.pending),next=remote[local.history.length];
  if(!next||P.sha(p)!==P.sha(next))throw Error('W157_CONFLICTING_PENDING_QUARANTINE');
 }
 return true;
}
module.exports={SCHEMA,historyState,certify,admission};
```

## catchup157.js

```javascript
'use strict';
const P=require('./baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const V=require('./catchup-verify157');
function make({identity,witnesses,publicKeys}){
 const rpc=(id,url,b)=>P.rpc({...identity,...witnesses[id]},url,b);
 async function repair(target){
  if(!witnesses[target]||Object.keys(witnesses).length!==3)throw Error('W157_TARGET_OR_MEMBERS_INVALID');
  const challenge=await rpc(target,'/challenge',{}),nonce=challenge?.body?.nonce;
  if(!publicKeys[target]||!P.verify(publicKeys[target],'S157:CHALLENGE',challenge.body,challenge.signature)||!nonce)throw Error('W157_CHALLENGE_SIGNATURE_INVALID');
  const all=await Promise.all(Object.keys(witnesses).filter(id=>id!==target).map(async id=>{try{return{id,v:await rpc(id,'/read',{nonce})};}catch(e){return{id,error:e.message};}}));
  const heads=all.filter(x=>x.v?.body?.nodeId===x.id&&P.verify(publicKeys[x.id],'S156:HEAD',x.v.body,x.v.signature));
  if(heads.length<2)throw Error('W157_CATCHUP_NO_MAJORITY');
  const one=heads[0].v.body;
  if(heads.some(x=>x.v.body.slot!==one.slot||x.v.body.head!==one.head))throw Error('W157_MAJORITY_FORK');
  const exp=await rpc(heads[0].id,'/export',{nonce});
  V.certify({slot:one.slot,head:one.head},heads.map(x=>x.v),exp,nonce,publicKeys);
  const result=await rpc(target,'/catchup',{nonce,head:{slot:one.slot,head:one.head},heads:heads.map(x=>x.v),exported:exp});
  if(result?.body?.nodeId!==target||result.body.slot!==one.slot||result.body.head!==one.head||!P.verify(publicKeys[target],'S157:INSTALLED',result.body,result.signature))throw Error('W157_INSTALL_ACK_INVALID');
  return result;
 }
 return{repair,rpc};
}
module.exports={make};
```

## gate157.js

```javascript
#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const P=require('./baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./baseline156/witness-verify156');const V=require('./catchup-verify157');const C=require('./catchup157');
const root=fs.mkdtempSync(path.join(os.tmpdir(),'sheet157-')),f=(...a)=>path.join(root,...a),openssl=(...a)=>cp.execFileSync('openssl',a,{cwd:root,stdio:'pipe'});
let n=0;const ok=(name,fn)=>{fn();console.log('PASS',++n,name);};const step=async(name,fn)=>{await fn();console.log('PASS',++n,name);};const bad=async(name,fn,regex)=>step(name,async()=>assert.rejects(fn,regex));
function cert(id){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',id+'.key','-out',id+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(id+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',id+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',id+'.crt','-days','2','-sha256','-extfile',id+'.ext');return{key:f(id+'.key'),cert:f(id+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(id+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
function keys(id){const pair=crypto.generateKeyPairSync('ed25519'),priv=f(id+'.priv'),pub=f(id+'.pub');fs.writeFileSync(priv,pair.privateKey.export({format:'pem',type:'pkcs8'}));fs.writeFileSync(pub,pair.publicKey.export({format:'pem',type:'spki'}));return{privateKey:pair.privateKey,publicKey:pair.publicKey,priv,pub};}
const children=[];
async function spawn(script,cfg,id){const config=f('cfg-'+id+'.json');P.atomic(config,cfg);const proc=cp.fork(path.join(__dirname,script),[],{env:{...process.env,S157_WITNESS_CONFIG:config,S156_FLOOR_CONFIG:config},stdio:['ignore','pipe','pipe','ipc']});let errors='';proc.on('error',()=>{});proc.stderr.on('data',b=>errors+=b);const port=await new Promise((res,rej)=>{const t=setTimeout(()=>rej(Error('START_TIMEOUT '+id+' '+errors)),15000);proc.once('message',m=>{clearTimeout(t);res(m.port);});proc.once('exit',code=>{clearTimeout(t);rej(Error('START_FAILED '+id+' '+code+' '+errors));});});const x={proc,port,id,errors:()=>errors};children.push(x);return x;}
async function stop(x){if(!x||x.proc.exitCode!==null||x.proc.signalCode!==null)return;await new Promise(done=>{const t=setTimeout(()=>{x.proc.kill('SIGKILL');done();},2000);x.proc.once('exit',()=>{clearTimeout(t);done();});if(x.proc.connected){try{x.proc.send('stop',err=>{if(err){x.proc.kill('SIGKILL');clearTimeout(t);done();}});}catch{ x.proc.kill('SIGKILL');clearTimeout(t);done();}}else{x.proc.kill('SIGKILL');clearTimeout(t);done();}});}
(async()=>{try{
 openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=S157-TEST');
 const ids=Object.fromEntries(['proxy','wred','wblue','wgreen','rogue'].map(id=>[id,cert(id)]));
 const witnessKeys=Object.fromEntries(['wred','wblue','wgreen'].map(id=>[id,keys(id)]));
 const finalKeys=Object.fromEntries(['red','blue'].map(id=>[id,keys('final-'+id)]));
 const pubs=Object.fromEntries(Object.entries(witnessKeys).map(([id,k])=>[id,k.publicKey]));
 const witnessPublicKeys=Object.fromEntries(Object.entries(witnessKeys).map(([id,k])=>[id,k.pub]));
 const finalPublicKeys=Object.fromEntries(Object.entries(finalKeys).map(([id,k])=>[id,k.pub]));
 const config=Object.fromEntries(Object.keys(witnessKeys).map(id=>[id,{id,...ids[id],signKey:witnessKeys[id].priv,stateFile:f(id,'state.json'),proxyPin:ids.proxy.certPin,witnessPublicKeys,finalityPublicKeys:finalPublicKeys}]));
 const nodes={};for(const id of Object.keys(config))nodes[id]=await spawn('witness157.js',config[id],id);
 const endpoints=()=>Object.fromEntries(Object.keys(nodes).map(id=>[id,{port:nodes[id].port,serverPin:ids[id].certPin}]));
 const api=()=>C.make({identity:ids.proxy,witnesses:endpoints(),publicKeys:pubs});
 const rpc=(id,url,body={})=>api().rpc(id,url,body);
 const readState=id=>P.load(config[id].stateFile);
 const record=(slot,prev,tag)=>W.normalize({slot,prev,intentDigest:P.sha('intent'+tag),snapshotDigest:P.sha('snapshot'+tag),receiptHash:P.sha('receipt'+tag)});
 const finalVotes=r=>['red','blue'].map(id=>{const body={nodeId:id,slot:r.slot,prevPinDigest:r.prev,intentDigest:r.intentDigest,snapshotDigest:r.snapshotDigest,receiptHash:r.receiptHash,phase:'final'};return{body,signature:P.sign(finalKeys[id].privateKey,'S155:FINAL',body)};});
 const prepare=async(id,r)=>rpc(id,'/prepare',{record:r,finalVotes:finalVotes(r)});
 const commit=async(id,r,votes)=>rpc(id,'/commit',{record:r,preparedVotes:votes});
 ok('three TLS-pinned independent witness identities',()=>assert.equal(Object.keys(nodes).length,3));
 ok('genesis hashes match',()=>{for(const id of Object.keys(nodes))assert.equal(readState(id).head,W.ZERO);});
 ok('empty certified history hashes to zero',()=>assert.deepEqual(V.historyState([]),{slot:0,head:W.ZERO}));
 ok('history extension rejects truncation',()=>assert.throws(()=>V.admission({history:[record(1,W.ZERO,'a')],pending:null},[]),/W157_ROLLBACK_NOT_ALLOWED/));
 let prev=W.ZERO;const history=[];
 for(let slot=1;slot<=3;slot++){
  const r=record(slot,prev,'main-'+slot);const votes=[];
  for(const id of ['wred','wgreen'])votes.push(await prepare(id,r));
  if(slot===1)await prepare('wblue',r); // minority prepared but missed the commit acknowledgement
  await commit('wred',r,votes);await commit('wgreen',r,votes);
  history.push(r);prev=r.head;
  ok('quorum committed slot '+slot,()=>{assert.equal(readState('wred').slot,slot);assert.equal(readState('wgreen').slot,slot);});
 }
 ok('minority lags with durable pending prepare',()=>{const b=readState('wblue');assert.equal(b.slot,0);assert.equal(b.pending.head,history[0].head);});
 await step('quorum-certified three-slot catchup resolves matching pending',async()=>{const r=await api().repair('wblue');assert.equal(r.body.slot,3);});
 ok('installed minority history matches exactly',()=>assert.deepEqual(readState('wblue').history,history));
 ok('minority pending cleared only after certified install',()=>assert.equal(readState('wblue').pending,null));
 ok('minority history high-water equals majority',()=>assert.equal(readState('wblue').head,prev));
 await step('catchup repeated is idempotent',async()=>assert.equal((await api().repair('wblue')).body.slot,3));
 await stop(nodes.wblue);nodes.wblue=await spawn('witness157.js',config.wblue,'wblue-restart');
 await step('minority restart retains committed certified history',async()=>assert.equal((await rpc('wblue','/read',{nonce:crypto.randomBytes(20).toString('hex')})).body.slot,3));
 const nonce=crypto.randomBytes(20).toString('hex');const challenge=await rpc('wblue','/challenge',{});
 const responses=await Promise.all(['wred','wgreen'].map(id=>rpc(id,'/read',{nonce:challenge.body.nonce})));const exported=await rpc('wred','/export',{nonce:challenge.body.nonce});
 const packet={nonce:challenge.body.nonce,head:{slot:3,head:prev},heads:responses,exported};
 ok('valid quorum package includes signed history',()=>assert.equal(V.certify(packet.head,packet.heads,packet.exported,packet.nonce,pubs).length,3));
 await bad('signed-head replay under different nonce blocked',()=>rpc('wblue','/catchup',{...packet,nonce:'e'.repeat(40)}),/W157_CHALLENGE_EXPIRED_OR_REPLAY/);
 await bad('forged witness-head signature blocked',()=>rpc('wblue','/catchup',{...packet,heads:[{...responses[0],signature:'AAAA'},responses[1]]}),/W157_MAJORITY_HEAD_INVALID/);
 await bad('duplicate witness signatures cannot fake quorum',()=>rpc('wblue','/catchup',{...packet,heads:[responses[0],responses[0]]}),/W157_MAJORITY_HEAD_INVALID/);
 await bad('unsigned export cannot rewrite the journal',()=>rpc('wblue','/catchup',{...packet,exported:{...exported,signature:'AAAA'}}),/W157_EXPORT_INVALID/);
 await bad('altered signed export history rejected',()=>rpc('wblue','/catchup',{...packet,exported:{...exported,body:{...exported.body,history:[]}}}),/W157_EXPORT_INVALID/);
 await step('one-time challenge is consumed on successful install',async()=>assert.equal((await rpc('wblue','/catchup',packet)).body.slot,3));
 await bad('replay of already used challenge fails',()=>rpc('wblue','/catchup',packet),/W157_CHALLENGE_EXPIRED_OR_REPLAY/);
 await bad('untrusted TLS client cannot read witness journal',()=>P.rpc({...ids.rogue,...endpoints().wblue},'/export',{nonce}),/TLS_PEER_NOT_PINNED/);
 ok('journal prefix fork never accepted',()=>assert.throws(()=>V.admission({history:[record(1,W.ZERO,'left')],pending:null},[record(1,W.ZERO,'right')]),/W157_FORK_QUARANTINE/));
 ok('pending conflict never implicitly discarded',()=>assert.throws(()=>V.admission({history:[],pending:record(1,W.ZERO,'wrong')},[history[0]]),/W157_CONFLICTING_PENDING_QUARANTINE/));
 ok('pending matching certified commit may reconcile',()=>V.admission({history:[],pending:history[0]},history));
 ok('history proof cannot skip slots',()=>assert.throws(()=>V.historyState([record(2,W.ZERO,'skip')]),/W157_HISTORY_INVALID/));
 ok('history proof cannot splice different prev hash',()=>assert.throws(()=>V.historyState([history[0],record(2,W.ZERO,'splice')]),/W157_HISTORY_INVALID/));
 ok('history proof rejects injected record properties',()=>assert.throws(()=>V.historyState([{...history[0],hidden:'bad'}]),/W157_HISTORY_INVALID/));
 ok('history proof rejects oversized exports',()=>assert.throws(()=>V.historyState(Array(257).fill(history[0])),/W157_HISTORY_SIZE_BOUND/));
 // A conflicting prepared minority cannot be "repaired" by coercing it to abandon its signed promise.
 const r4=record(4,prev,'slot4');const allVotes=await Promise.all(['wred','wblue','wgreen'].map(id=>prepare(id,r4)));
 await commit('wred',r4,allVotes);await commit('wgreen',r4,allVotes);
 ok('fourth slot committed by majority, third witness pending',()=>assert.equal(readState('wblue').pending.slot,4));
 await step('matching pending slot four is reconciled after real majority commit',async()=>assert.equal((await api().repair('wblue')).body.slot,4));
 const r5a=record(5,r4.head,'version-A');const r5b=record(5,r4.head,'version-B');
 const vA=await Promise.all(['wred','wgreen'].map(id=>prepare(id,r5a)));
 await prepare('wblue',r5b);
 await commit('wred',r5a,vA);await commit('wgreen',r5a,vA);
 await bad('conflicting pending minority quarantines and refuses overwrite',()=>api().repair('wblue'),/W157_CONFLICTING_PENDING_QUARANTINE/);
 ok('conflicting minority pending remains durable',()=>assert.equal(readState('wblue').pending.head,r5b.head));
 await stop(nodes.wblue);nodes.wblue=await spawn('witness157.js',config.wblue,'wblue-conflict-restart');
 await bad('quarantine survives restart',()=>api().repair('wblue'),/W157_CONFLICTING_PENDING_QUARANTINE/);
 // One peer lost: cannot prove a fresh 2-of-3 certified target without the lagging target's own vote.
 await stop(nodes.wgreen);
 await bad('one survivor cannot certify minority catchup',()=>api().repair('wblue'),/W157_CATCHUP_NO_MAJORITY/);
 nodes.wgreen=await spawn('witness157.js',config.wgreen,'wgreen-restart');
 await step('majority heads survive one witness process restart',async()=>{const a=await Promise.all(['wred','wgreen'].map(id=>rpc(id,'/read',{nonce:crypto.randomBytes(20).toString('hex')})));assert.equal(a[0].body.head,a[1].body.head);});
 // Install survives an abrupt exit after fsync and rename, before the RPC reply is emitted.
 const recoveredState=structuredClone(readState('wblue'));recoveredState.pending=null;recoveredState.slot=4;recoveredState.history=history.concat(r4);recoveredState.head=r4.head;recoveredState.challenge=null;
 await stop(nodes.wblue);P.atomic(config.wblue.stateFile,recoveredState);
 config.wblue.crashAfterInstall=true;config.wblue.crashMarker=f('crash157.once');
 nodes.wblue=await spawn('witness157.js',config.wblue,'wblue-crash');
 await bad('crash after durable install drops acknowledgement',()=>api().repair('wblue'),/socket hang up|ECONNRESET|RPC_TIMEOUT/);
 ok('crashed witness saved slot-five history durably',()=>assert.equal(readState('wblue').slot,5));
 await stop(nodes.wblue);nodes.wblue=await spawn('witness157.js',config.wblue,'wblue-aftercrash');
 await step('retry after restarted witness is idempotent',async()=>assert.equal((await api().repair('wblue')).body.slot,5));
 ok('restarted witness cannot regress below certified floor',()=>assert.equal(readState('wblue').head,r5a.head));
 const report={schema:'oasis.sheet157.gate.v1',checks:n,passed:true,witnessProcesses:3,certifiedSlots:5,crashAfterDurableInstall:true,conflictingPendingQuarantined:true,quorumFreshNonce:true,physicalHosts:1,limitations:['bounded 256-record history export; larger histories need paginated authenticated proofs','all mTLS services run on one host','quarantined conflicting prepare requires external reviewed resolution','does not establish Byzantine multi-host safety','S142 intermittent inherited timing test']};
 fs.writeFileSync(path.join(__dirname,'new-test-report.json'),JSON.stringify(report,null,2)+'\n');
 console.log(`SHEET157 NEW PASS ${n}/${n}`);
}catch(e){console.error(`SHEET157 FAILURE after ${n}`,e.stack||e);process.exitCode=1;}finally{for(const c of children.reverse())await stop(c).catch(()=>{});fs.rmSync(root,{recursive:true,force:true});}})();
```

## run-all.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
temp="$(mktemp -d)"
trap 'rm -rf "$temp"' EXIT
cp -a "$here/baseline156" "$temp/sheet156"
(cd "$temp/sheet156" && bash run-all.sh)
(cd "$here" && node gate157.js)
```

## browser-check.py

```python
from playwright.sync_api import sync_playwright
from pathlib import Path
root=Path(__file__).resolve().parent
text=(root/'index.html').read_text()
lines=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(accept_downloads=True,viewport={'width':1280,'height':1000})
 page.set_content(text,wait_until='load')
 assert page.locator('#scenarios button').count()==8
 for i in range(8):
  b=page.locator('#scenarios button').nth(i)
  b.click()
  assert b.get_attribute('aria-pressed')=='true'
  assert page.locator('#status').inner_text().strip()
  lines.append(f'PASS scenario {i+1} {page.locator("#label").inner_text()}')
 with page.expect_download() as d:page.locator('#export').click()
 download=d.value
 assert download.suggested_filename=='sheet157-scenario.json'
 lines.append('PASS scenario JSON export')
 page.locator('#scenarios button').first.click()
 page.screenshot(path=str(root/'preview.png'),full_page=True)
 lines.append('PASS Chromium screenshot')
 browser.close()
(root/'browser-test.log').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
```

## make-release.py

```python
#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,zipfile,os,datetime
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PARENT=ROOT/'sheet156'
ARCHIVE=ROOT/'SHEET157-certified-witness-catchup.zip'
SHA=ROOT/(ARCHIVE.name+'.sha256.txt')

def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while True:
   b=f.read(1<<20)
   if not b: break
   h.update(b)
 return h.hexdigest()

before={str(p.relative_to(PARENT)):digest(p) for p in PARENT.rglob('*') if p.is_file()}
after={str(p.relative_to(HERE/'baseline156')):digest(p) for p in (HERE/'baseline156').rglob('*') if p.is_file()}
assert before==after, 'FROZEN S156 PARENT WAS NOT PRESERVED EXACTLY'
assert (HERE/'new-test-report.json').exists()
new=json.loads((HERE/'new-test-report.json').read_text())
assert new['passed'] is True and new['checks']==41, 'S157 new fault gate incomplete'
assert (HERE/'browser-test.log').read_text().count('PASS')==10
combined_exit=int((HERE/'combined-exit.txt').read_text().strip()) if (HERE/'combined-exit.txt').exists() else None
source_files=['witness157.js','catchup-verify157.js','catchup157.js','gate157.js','run-all.sh','browser-check.py','make-release.py']
listing=['# SHEET 157 — Complete New Authored Sources','','The frozen SHEET156 lineage remains in the full ZIP; this listing contains the new SHEET157 implementation and tests.','']
for name in source_files:
 code=(HERE/name).read_text()
 lang='javascript' if name.endswith('.js') else ('python' if name.endswith('.py') else 'bash')
 listing.extend([f'## {name}','',f'```{lang}',code.rstrip(),'```',''])
(HERE/'SOURCE-ALL157.md').write_text('\n'.join(listing))
receipt={
 'schema':'oasis.sheet157.release.v1','sheet':157,'previous':156,
 'title':'Quorum-Certified Minority Witness Catch-Up',
 'previousFilesPreserved':len(before),'previousBytesIdentical':True,
 'newGate':{'passed':True,'checks':41,'exit':0},
 'inheritedBaseline':{'lastPriorReleaseCombinedChecks':1519,'latestFullRerunExit':combined_exit,'latestFullRerunStatus':'TIMEOUT: incomplete inherited chain' if combined_exit is None else 'EXIT '+str(combined_exit)},
 'chromium':{'scenarios':8,'jsonExport':True,'screenshot':True},
 'faults':['signed quorum catch-up','prefix protection','conflicting pending quarantine','head replay','tampered export','witness restart','crash after durable install','idempotent retry','loss of two healthy peer attestors'],
 'scope':['one physical host','three TLS witness processes','synthetic Ed25519 finality votes in new gate','full export bounded 256 records'],
 'notes':'Witness catch-up endpoint is explicitly invoked; no unsafe automatic release of conflicting pending votes.'
}
(HERE/'release-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
entries=sorted([p for p in HERE.rglob('*') if p.is_file() and p!=HERE/'SHA256SUMS'])
manifest=''.join(f'{digest(p)}  {p.relative_to(HERE).as_posix()}\n' for p in entries)
(HERE/'SHA256SUMS').write_text(manifest)
entries.append(HERE/'SHA256SUMS')
with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as zipf:
 for p in entries:zipf.write(p,arcname='sheet157/'+p.relative_to(HERE).as_posix())
with zipfile.ZipFile(ARCHIVE) as z:
 bad=z.testzip();assert bad is None, f'bad zip member {bad}'
 archived={n[len('sheet157/baseline156/'):]:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('sheet157/baseline156/') and not n.endswith('/')}
 assert archived==before, 'ARCHIVED INHERITED BASELINE MISMATCH'
 for name in ['witness157.js','catchup157.js','catchup-verify157.js','gate157.js','SHA256SUMS']:
  assert 'sheet157/'+name in z.namelist()
SHA.write_text(f'{digest(ARCHIVE)}  {ARCHIVE.name}\n')
print(json.dumps({'zip':str(ARCHIVE),'bytes':ARCHIVE.stat().st_size,'sha256':digest(ARCHIVE),'verifiedParentFiles':len(before),'newChecks':41,'combinedExit':combined_exit},indent=2))
```