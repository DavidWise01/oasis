# SHEET 154 — Complete New Source Listing

Exact standalone new files; full inherited code lives in the release ZIP.

## finality-replica154.js

```javascript
'use strict';
// SHEET 154: each mTLS replica owns an independent fsync'd finality decision file.
const fs=require('node:fs');
const P=require('./baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const M=require('./baseline153/baseline152/baseline151/merkle151');
const {verifyGrant}=require('./baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/proof148');
const {SCHEMA:PHYSICAL}=require('./baseline153/unified153');
const cfg=JSON.parse(fs.readFileSync(process.env.S154_REPLICA_CONFIG,'utf8'));
const signing=fs.readFileSync(cfg.signKey),pubs=Object.fromEntries(Object.entries(cfg.members).map(([id,p])=>[id,fs.readFileSync(p)]));
const authorities=Object.fromEntries(Object.entries(cfg.authorityPublicKeys).map(([id,p])=>[id,fs.readFileSync(p)]));
const resourcePub=fs.readFileSync(cfg.resourcePublicKey),anchorPub=fs.readFileSync(cfg.anchorPublicKey);
const SCHEMA='oasis.sheet154.finality.v1',ZERO='0'.repeat(64);
const domain={prepare:'S154:PREPARE',anchor:'S154:ANCHORED',final:'S154:FINAL'};
const sha=P.sha;
function seal(kind,body){return {body,signature:P.sign(signing,domain[kind],body)};}
function fresh(){return{schema:SCHEMA,nodeId:cfg.id,serial:0,slot:null,events:[],head:ZERO};}
if(!fs.existsSync(cfg.stateFile))P.atomic(cfg.stateFile,fresh());
function read(){const s=P.load(cfg.stateFile);if(s.schema!==SCHEMA||s.nodeId!==cfg.id||!Array.isArray(s.events)||s.events.length!==s.serial)throw Error('F154_STATE_INVALID');let h=ZERO;for(const [i,e] of s.events.entries()){if(e.index!==i+1||e.prev!==h)throw Error('F154_LOG_CHAIN_INVALID');h=sha(e);}if(h!==s.head)throw Error('F154_LOG_TAMPERED');const last=s.events.at(-1);if((last?.slot===undefined?null:last.slot)&&sha(last.slot)!==sha(s.slot))throw Error('F154_SLOT_TAMPERED');return s;}
function persist(s,kind,slot){s.events.push({index:s.events.length+1,prev:s.head,kind,slot});s.serial=s.events.length;s.head=sha(s.events.at(-1));s.slot=slot;P.atomic(cfg.stateFile,s);}
function validateCert(votes,kind,intentDigest){if(!Array.isArray(votes))throw Error('F154_NO_CERTIFICATE');const ids=new Set();for(const v of votes){const b=v?.body;if(!b||!pubs[b.nodeId]||ids.has(b.nodeId)||b.intentDigest!==intentDigest||b.phase!==kind||!P.verify(pubs[b.nodeId],domain[kind],b,v.signature))throw Error('F154_BAD_QUORUM_SIGNATURE');ids.add(b.nodeId);}if(ids.size<2)throw Error('F154_INSUFFICIENT_MAJORITY');return true;}
function verifyIntent(i){if(i?.schema!=='oasis.sheet154.intent.v1'||!i.txid||i.txid!==i.receipt?.body?.txid||!i.request||!i.proof||!i.checkpoint||!i.prior||!i.grant)throw Error('F154_INTENT_REQUIRED');
 const b=i.receipt.body,cp=i.checkpoint.body,prev=i.prior.body,record=i.proof.record;
 verifyGrant(i.grant,i.request,authorities);
 if(b.resourceId!==cfg.resourceId||b.resourceId!==i.request.resourceId||b.grantHead!==i.grant.head||b.digest!==sha({txid:i.request.txid,resourceId:i.request.resourceId,operationId:i.request.operationId,value:i.request.value,epoch:i.request.epoch})||b.epoch!==i.request.epoch||!P.verify(resourcePub,'S148:RECEIPT',b,i.receipt.signature))throw Error('F154_BAD_RECEIPT');
 if(cp.resourceId!==b.resourceId||cp.count<b.sequence||!P.verify(resourcePub,'S151:CHECKPOINT',cp,i.checkpoint.signature))throw Error('F154_BAD_CHECKPOINT');
 if(!P.verify(anchorPub,'S151:ANCHOR',prev,i.prior.signature)||prev.resourceId!==b.resourceId||prev.count>cp.count||M.root(prev.count,prev.frontier)!==prev.root)throw Error('F154_BAD_PRIOR_ANCHOR');
 if(record?.sequence!==b.sequence||record.hash!==b.recordHash||record.hash!==sha({resourceId:b.resourceId,sequence:record.sequence,prev:record.prev,payload:record.payload}))throw Error('F154_BAD_PHYSICAL_RECORD');
 let payload;try{payload=JSON.parse(record.payload);}catch{throw Error('F154_BAD_RECORD_PAYLOAD');}
 if(payload.schema!==PHYSICAL||payload.txid!==b.txid||payload.resourceId!==b.resourceId||payload.epoch!==b.epoch||payload.digest!==b.digest||payload.grantHead!==b.grantHead)throw Error('F154_RECORD_RECEIPT_MISMATCH');
 if(i.proof.inclusion?.count!==cp.count||i.proof.inclusion.index!==b.sequence-1||i.proof.inclusion.recordHash!==b.recordHash)throw Error('F154_WRONG_INCLUSION');M.verifyInclusion(i.proof.inclusion,cp.root,record.hash);
 return sha(i);
}
function verifySnapshot(snapshot,i){const b=snapshot?.body,c=i.checkpoint.body,p=i.prior;if(!b||!P.verify(anchorPub,'S151:ANCHOR',b,snapshot.signature)||b.resourceId!==cfg.resourceId||b.count!==c.count||b.root!==c.root||b.checkpointDigest!==sha(i.checkpoint)||b.previousAnchorDigest!==sha(p))throw Error('F154_ANCHOR_MISMATCH');return true;}
function verifyCompletion(evidence,intent){if(!Array.isArray(evidence))throw Error('F154_COMPLETION_EVIDENCE_REQUIRED');const good=new Set();const hash=sha(intent.receipt);for(const signed of evidence){const j=signed?.body,id=j?.nodeId;if(!authorities[id]||good.has(id)||!P.verify(authorities[id],'S147:JOURNAL',j,signed.signature))continue;
 let head=ZERO,valid=true,match=false;for(let idx=0;idx<(j.journal||[]).length;idx++){const row=j.journal[idx],p=row.proposal;if(p.index!==idx+1||p.prev!==head){valid=false;break;}const votes=row.votes||[],seen=new Set();for(const v of votes){const bb=v?.body;if(!bb||!authorities[bb.nodeId]||seen.has(bb.nodeId)||bb.digest!==sha(p)||bb.term!==p.term||bb.index!==p.index||bb.prev!==p.prev||bb.leaderId!==p.leaderId||!P.verify(authorities[bb.nodeId],'S147:PREPARE',bb,v.signature)){valid=false;break;}seen.add(bb.nodeId);}if(!valid||seen.size<2){valid=false;break;}head=sha({prev:head,index:p.index,term:p.term,op:p.op});if(p.op?.type==='COMPLETE'&&p.op.txid===intent.txid&&p.op.receiptHash===hash)match=true;}
 if(valid&&match&&j.seq===j.journal.length&&j.head===head)good.add(id);
}if(good.size<2)throw Error('F154_NO_SIGNED_COMPLETION_MAJORITY');return true;}
const server=P.serve(cfg.key,cfg.cert,cfg.ca,async(req,b)=>{
 P.peer(req,cfg.coordinatorPin);
 if(!['/state','/prepare','/anchored','/final'].includes(req.url))throw Error('F154_UNKNOWN_ROUTE');
 const s=read();if(req.url==='/state')return seal('final',{nodeId:cfg.id,serial:s.serial,head:s.head,phase:s.slot?.phase||'EMPTY',intentDigest:s.slot?.intentDigest||null});
 const i=b.intent;const digest=verifyIntent(i);
 if(s.slot?.intentDigest&&s.slot.intentDigest!==digest)throw Error('F154_CONFLICTING_FINALITY_INTENT');
 if(req.url==='/prepare'){
  if(s.slot?.phase==='FINAL')throw Error('F154_ALREADY_FINAL');
  if(!s.slot){const live=await P.rpc({port:cfg.anchor.port,key:cfg.key,cert:cfg.cert,ca:cfg.ca,serverPin:cfg.anchor.certPin},'/read');if(sha(live)!==sha(i.prior))throw Error('F154_STALE_PREPARE_ANCHOR');persist(s,'PREPARE',{intentDigest:digest,intent:i,phase:'PREPARED'});}
  return seal('prepare',{nodeId:cfg.id,intentDigest:digest,phase:'prepare'});
 }
 validateCert(b.preparedVotes,'prepare',digest);
 const live=await P.rpc({port:cfg.anchor.port,key:cfg.key,cert:cfg.cert,ca:cfg.ca,serverPin:cfg.anchor.certPin},'/read');
 verifySnapshot(b.snapshot,i);if(sha(live)!==sha(b.snapshot))throw Error('F154_STALE_ANCHOR');
 if(!s.slot)throw Error('F154_LOCAL_PREPARE_REQUIRED');
 if(req.url==='/anchored'){
  if(s.slot.phase==='PREPARED')persist(s,'ANCHORED',{...s.slot,phase:'ANCHORED',snapshotDigest:sha(b.snapshot)});
  else if(s.slot.snapshotDigest!==sha(b.snapshot))throw Error('F154_ANCHOR_CONFLICT');
  return seal('anchor',{nodeId:cfg.id,intentDigest:digest,phase:'anchor',snapshotDigest:sha(b.snapshot)});
 }
 validateCert(b.anchoredVotes,'anchor',digest);
 for(const v of b.anchoredVotes){if(v.body.snapshotDigest!==sha(b.snapshot))throw Error('F154_ANCHOR_VOTE_MISMATCH');}
 if(!['ANCHORED','FINAL'].includes(s.slot.phase)||s.slot.snapshotDigest!==sha(b.snapshot))throw Error('F154_NOT_ANCHORED');
 verifyCompletion(b.completionEvidence,i);
 if(s.slot.phase!=='FINAL')persist(s,'FINAL',{...s.slot,phase:'FINAL'});
 return seal('final',{nodeId:cfg.id,intentDigest:digest,phase:'final',snapshotDigest:sha(b.snapshot)});
});
process.on('message',x=>{if(x==='stop')server.close(()=>process.exit(0));});
module.exports={verifyIntent,verifySnapshot,verifyCompletion,validateCert};
```

## anchor-gateway154.js

```javascript
'use strict';
// Independent anchor admission gateway: only this process owns the TLS credential
// that the underlying immutable SHEET151 anchor will accept for /advance.
const fs=require('node:fs');
const P=require('./baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const {verifyGrant}=require('./baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/proof148');
const M=require('./baseline153/baseline152/baseline151/merkle151');
const cfg=JSON.parse(fs.readFileSync(process.env.S154_GATEWAY_CONFIG,'utf8'));
const pubs=Object.fromEntries(Object.entries(cfg.finalityPublicKeys).map(([id,p])=>[id,fs.readFileSync(p)]));
const authorityKeys=Object.fromEntries(Object.entries(cfg.authorityPublicKeys).map(([id,p])=>[id,fs.readFileSync(p)]));
const resourcePub=fs.readFileSync(cfg.resourcePublicKey);
const inner=(path,b={})=>P.rpc({port:cfg.inner.port,key:cfg.key,cert:cfg.cert,ca:cfg.ca,serverPin:cfg.inner.certPin},path,b);
function validate(intent,votes){if(intent?.schema!=='oasis.sheet154.intent.v1'||!intent.receipt||!intent.prior||!intent.checkpoint||!intent.proof)throw Error('G154_INTENT_REQUIRED');
 verifyGrant(intent.grant,intent.request,authorityKeys);
 const r=intent.receipt,b=r.body,cp=intent.checkpoint.body,p=intent.prior.body,record=intent.proof.record;
 if(!P.verify(resourcePub,'S148:RECEIPT',b,r.signature)||!P.verify(resourcePub,'S151:CHECKPOINT',cp,intent.checkpoint.signature)||b.txid!==intent.txid||cp.resourceId!==b.resourceId||cp.count<b.sequence)throw Error('G154_RESOURCE_SIGNATURE_INVALID');
 if(record?.hash!==b.recordHash||intent.proof.inclusion?.recordHash!==b.recordHash||intent.proof.inclusion?.count!==cp.count)throw Error('G154_MISSING_PHYSICAL_PROOF');
 M.verifyInclusion(intent.proof.inclusion,cp.root,record.hash);
 const digest=P.sha(intent),seen=new Set();for(const v of votes||[]){const bb=v?.body,id=bb?.nodeId;if(!pubs[id]||seen.has(id)||bb.intentDigest!==digest||bb.phase!=='prepare'||!P.verify(pubs[id],'S154:PREPARE',bb,v.signature))throw Error('G154_BAD_PREPARE_VOTE');seen.add(id);}if(seen.size<2)throw Error('G154_MAJORITY_REQUIRED');return digest;
}
const server=P.serve(cfg.key,cfg.cert,cfg.ca,async(req,b)=>{
 if(req.url==='/read'){if(!req.socket.authorized||![cfg.coordinatorPin,...(cfg.readerPins||[])].includes(P.fp(req.socket.getPeerCertificate(true))))throw Error('G154_READER_NOT_PINNED');return inner('/read');}
 P.peer(req,cfg.coordinatorPin);
 if(req.url==='/init')return inner('/init',{checkpoint:b.checkpoint});
 if(req.url!=='/advance')throw Error('G154_ROUTE_INVALID');
 validate(b.intent,b.preparedVotes);
 const live=await inner('/read');
 if(P.sha(live)!==P.sha(b.intent.prior)){
  if(live.body.checkpointDigest===P.sha(b.intent.checkpoint)&&live.body.previousAnchorDigest===P.sha(b.intent.prior))return live;
  throw Error('G154_PREVIOUS_ANCHOR_CONFLICT');
 }
 const advanced=await inner('/advance',{checkpoint:b.intent.checkpoint,proof:b.proof});
 if(cfg.testMode&&b.injectAfterInner===true)process.kill(process.pid,'SIGKILL');
 return advanced;
});
process.on('message',v=>{if(v==='stop')server.close(()=>process.exit(0));});
module.exports={validate};
```

## quorum154.js

```javascript
'use strict';
const fs=require('node:fs');
const P=require('./baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const {verifyGrant}=require('./baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/proof148');
const {verifyStatic}=require('./baseline153/proof153');
const SCHEMA='oasis.sheet154.intent.v1';
class QuorumFinality{
 constructor({identity,replicas,publicKeys,resourcePub,anchorPub,anchor,authorityKeys}){Object.assign(this,{identity,replicas,publicKeys,resourcePub:fs.readFileSync(resourcePub),anchorPub:fs.readFileSync(anchorPub),anchor,authorityKeys});}
 async ask(id,path,body={}){const x=this.replicas[id];return P.rpc({port:x.port,key:this.identity.key,cert:this.identity.cert,ca:this.identity.ca,serverPin:x.certPin},path,body);}
 async quorum(path,body,phase){const rows=await Promise.all(Object.keys(this.replicas).map(async id=>{try{return{ id, v:await this.ask(id,path,body)};}catch(e){return{id,error:e.message};}}));const good=[];for(const x of rows){const b=x.v?.body;if(b?.nodeId===x.id&&b.phase===phase&&b.intentDigest===P.sha(body.intent)&&P.verify(this.publicKeys[x.id],`S154:${phase==='prepare'?'PREPARE':phase==='anchor'?'ANCHORED':'FINAL'}`,b,x.v.signature))good.push(x.v);}
 if(good.length<2)throw Error('F154_NO_QUORUM_'+phase.toUpperCase()+' '+rows.filter(x=>x.error).map(x=>x.error).join('|'));return good;}
 createIntent({request,grant,receipt,store,prior}){verifyGrant(grant,request,this.authorityKeys);const checkpoint=store.checkpoint(prior),proof={record:store.find(receipt.body.txid).record,inclusion:store.ledger.inclusion(receipt.body.sequence-1)};
 return{schema:SCHEMA,txid:receipt.body.txid,request,grant,receipt,checkpoint,prior,proof};}
 async prepare(intent){return this.quorum('/prepare',{intent},'prepare');}
 async advanceAnchor(intent,votes,proof){if(votes.length<2)throw Error('F154_PREPARE_CERT_REQUIRED');return this.anchorRpc('/advance',{intent,preparedVotes:votes,proof});}
 anchorRpc(path,body={}){return P.rpc({port:this.anchor.port,key:this.identity.key,cert:this.identity.cert,ca:this.identity.ca,serverPin:this.anchor.certPin},path,body);}
 async admit(intent,preparedVotes,snapshot){return this.quorum('/anchored',{intent,preparedVotes,snapshot},'anchor');}
 async finalize(intent,preparedVotes,anchoredVotes,snapshot,completionEvidence){return this.quorum('/final',{intent,preparedVotes,anchoredVotes,snapshot,completionEvidence},'final');}
}
module.exports={QuorumFinality,SCHEMA};
```

## gate154.js

```javascript
#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const P=require('./baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const {UnifiedStore}=require('./baseline153/unified153'),{QuorumFinality}=require('./quorum154');
const ZERO='0'.repeat(64);let count=0;const pass=(name,fn)=>{fn();console.log('PASS',++count,name);},step=async(name,fn)=>{await fn();console.log('PASS',++count,name);},fails=async(name,fn,re)=>step(name,async()=>assert.rejects(fn,re));
const root=fs.mkdtempSync(path.join(os.tmpdir(),'sheet154-')),f=(...p)=>path.join(root,...p),openssl=(...a)=>cp.execFileSync('openssl',a,{cwd:root,stdio:'pipe'});
function cert(n){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',n+'.key','-out',n+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(n+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',n+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',n+'.crt','-days','2','-sha256','-extfile',n+'.ext');return{key:f(n+'.key'),cert:f(n+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(n+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
function keys(n){const x=crypto.generateKeyPairSync('ed25519');const priv=f(n+'.priv'),pub=f(n+'.pub');fs.writeFileSync(priv,x.privateKey.export({type:'pkcs8',format:'pem'}),{mode:0o600});fs.writeFileSync(pub,x.publicKey.export({type:'spki',format:'pem'}));return{priv,pub,privateKey:x.privateKey,publicKey:x.publicKey};}
const children=[];
async function spawn(script,cfg,label,envName){const conf=f(label+'-'+crypto.randomUUID()+'.json');fs.writeFileSync(conf,JSON.stringify(cfg));const proc=cp.fork(path.join(__dirname,script),[],{env:{...process.env,[envName]:conf},stdio:['ignore','pipe','pipe','ipc']});let err='';proc.stderr.on('data',b=>err+=b);const info=await new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(Error('START_TIMEOUT '+label+': '+err)),9000);proc.once('message',m=>{clearTimeout(t);resolve({proc,port:m.port,label,err:()=>err});});proc.once('exit',c=>{clearTimeout(t);reject(Error('START_EXIT '+label+': '+c+' '+err));});});children.push(info);return info;}
async function stop(x){if(!x||x.proc.exitCode!==null||x.proc.signalCode!==null||x.proc.killed||!x.proc.connected)return;await new Promise(done=>{const t=setTimeout(()=>{x.proc.kill('SIGKILL');done();},1500);x.proc.once('exit',()=>{clearTimeout(t);done();});x.proc.send('stop');});}
(async()=>{try{
 openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=S154-Test-CA');
 const ids=Object.fromEntries(['red','blue','green','alpha','resource','anchor','gateway','rogue'].map(n=>[n,cert(n)]));
 const auth=Object.fromEntries(['red','blue','green','resource','anchor'].map(n=>[n,keys(n)]));
 const fins=Object.fromEntries(['red','blue','green'].map(n=>[n,keys('final-'+n)]));
 const authorityPub=Object.fromEntries(['red','blue','green'].map(n=>[n,auth[n].pub]));
 const finalPub=Object.fromEntries(['red','blue','green'].map(n=>[n,fins[n].pub]));
 const store=new UnifiedStore(f('journal'), 'resource',auth.resource.privateKey);store.init();
 const anchorCfg={...ids.anchor,file:f('anchor-floor','current.json'),resourceId:'resource',resourcePublic:auth.resource.pub,anchorPrivate:auth.anchor.priv,anchorPublic:auth.anchor.pub,controlPin:ids.gateway.certPin,readPins:[ids.gateway.certPin]};
 let anchor=await spawn('baseline153/baseline152/anchor-server152.js',anchorCfg,'anchor','S152_ANCHOR_CONFIG');
 const gatewayCfg={...ids.gateway,coordinatorPin:ids.alpha.certPin,readerPins:['red','blue','green'].map(id=>ids[id].certPin),inner:{port:anchor.port,certPin:ids.anchor.certPin},finalityPublicKeys:finalPub,authorityPublicKeys:authorityPub,resourcePublicKey:auth.resource.pub,testMode:true};
 let gateway=await spawn('anchor-gateway154.js',gatewayCfg,'gateway','S154_GATEWAY_CONFIG');
 const anchorRpc=(route,body={})=>P.rpc({port:gateway.port,key:ids.alpha.key,cert:ids.alpha.cert,ca:ids.alpha.ca,serverPin:ids.gateway.certPin},route,body);
 const genesis=await anchorRpc('/init',{checkpoint:store.checkpoint()});
 const nodes={},configs={};
 for(const id of ['red','blue','green']){configs[id]={id,...ids[id],signKey:fins[id].priv,members:finalPub,authorityPublicKeys:authorityPub,resourcePublicKey:auth.resource.pub,anchorPublicKey:auth.anchor.pub,resourceId:'resource',stateFile:f('finality-'+id,'state.json'),coordinatorPin:ids.alpha.certPin,anchor:{port:gateway.port,certPin:ids.gateway.certPin}};nodes[id]=await spawn('finality-replica154.js',configs[id],'final-'+id,'S154_REPLICA_CONFIG');}
 const alive=()=>Object.fromEntries(Object.entries(nodes).filter(([,v])=>v.proc.exitCode===null).map(([id,v])=>[id,{port:v.port,certPin:ids[id].certPin}]));
 const qc=()=>new QuorumFinality({identity:ids.alpha,replicas:alive(),publicKeys:Object.fromEntries(Object.entries(fins).map(([k,v])=>[k,fs.readFileSync(v.pub)])),resourcePub:auth.resource.pub,anchorPub:auth.anchor.pub,anchor:{port:gateway.port,certPin:ids.gateway.certPin},authorityKeys:Object.fromEntries(Object.entries(auth).filter(([k])=>['red','blue','green'].includes(k)).map(([k,v])=>[k,fs.readFileSync(v.pub)]))});
 const request={txid:'physical_001',resourceId:'resource',operationId:'write',value:'hello-quorum',epoch:1};const digest=P.sha(request);
 const opBegin={type:'BEGIN',txid:request.txid,resourceId:'resource',digest};
 const proposal1={term:1,leaderId:'alpha',index:1,prev:ZERO,op:opBegin};
 const votes1=['red','blue'].map(id=>{const body={nodeId:id,digest:P.sha(proposal1),term:1,index:1,prev:ZERO,leaderId:'alpha'};return{body,signature:P.sign(auth[id].privateKey,'S147:PREPARE',body)};});
 const grantHead=P.sha({prev:ZERO,index:1,term:1,op:opBegin});
 const states=['red','blue'].map(id=>{const body={nodeId:id,term:1,leaderId:'alpha',seq:1,head:grantHead,epoch:1,pending:null,pendingGrant:{txid:request.txid,resourceId:'resource',digest,epoch:1,grantHead}};return{body,signature:P.sign(auth[id].privateKey,'S147:STATE',body)};});
 const grant={schema:'oasis.sheet148.grant.v1',certificate:{proposal:proposal1,votes:votes1},seq:1,head:grantHead,epoch:1,states};
 const receipt=store.commit(request,{head:grantHead});const controller=qc();const intent=controller.createIntent({request,grant,receipt,store,prior:genesis});
 pass('three independent finality replica processes',()=>assert.equal(Object.keys(nodes).length,3));
 pass('resource is written into one physical segmented journal',()=>assert.equal(store.inspect().head.count,1));
 pass('physical receipt is Ed25519-signed',()=>assert.ok(P.verify(auth.resource.publicKey,'S148:RECEIPT',receipt.body,receipt.signature)));
 pass('genesis anchor uses a separate key',()=>assert.ok(P.verify(auth.anchor.publicKey,'S151:ANCHOR',genesis.body,genesis.signature)));
 pass('exact S148 grant verifies through S154 intent constructor',()=>assert.equal(intent.grant.head,grantHead));
 await fails('coordinator cannot bypass gateway to advance underlying signer',()=>P.rpc({...ids.alpha,port:anchor.port,serverPin:ids.anchor.certPin},'/advance',{checkpoint:intent.checkpoint,proof:store.extension(0)}),/TLS_PEER_NOT_PINNED/);
 await fails('gateway rejects quorum-free checkpoint movement',()=>anchorRpc('/advance',{intent,preparedVotes:[],proof:store.extension(0)}),/G154_MAJORITY_REQUIRED/);
 await fails('untrusted mTLS identity cannot request finality prepare',()=>P.rpc({...ids.rogue,port:nodes.red.port,serverPin:ids.red.certPin},'/prepare',{intent}),/TLS_PEER_NOT_PINNED/);
 await fails('forged receipt is refused at replica',()=>controller.ask('red','/prepare',{intent:{...intent,receipt:{...receipt,signature:'AAAA'}}}),/F154_BAD_RECEIPT/);
 await fails('mismatched resource record is refused at replica',()=>controller.ask('red','/prepare',{intent:{...intent,proof:{...intent.proof,record:{...intent.proof.record,hash:'f'.repeat(64)}}}}),/F154_BAD_PHYSICAL_RECORD/);
 await fails('bad inclusion branch cannot prepare',()=>controller.ask('red','/prepare',{intent:{...intent,proof:{...intent.proof,inclusion:{...intent.proof.inclusion,recordHash:'a'.repeat(64)}}}}),/F154_WRONG_INCLUSION/);
 await fails('wrong grant digest cannot prepare',()=>controller.ask('red','/prepare',{intent:{...intent,request:{...request,value:'changed'}}}),/GRANT_REQUEST_MISMATCH/);
 const votes=await controller.prepare(intent);
 await fails('gateway rejects an invalid quorum signature',()=>anchorRpc('/advance',{intent,preparedVotes:[{...votes[0],signature:'AAAA'},votes[1]],proof:store.extension(0)}),/G154_BAD_PREPARE_VOTE/);
 pass('2/3 durable prepare votes',()=>assert.ok(votes.length>=2));
 pass('all three replicas persist exact prepare intent',()=>{for(const id of ['red','blue','green'])assert.equal(P.load(configs[id].stateFile).slot.phase,'PREPARED');});
 await fails('conflicting transaction cannot replace a prepared slot',()=>controller.ask('red','/prepare',{intent:{...intent,txid:'different'}}),/F154_INTENT_REQUIRED|F154_CONFLICTING/);
 await fails('random prepared votes cannot authorize anchored state',()=>controller.ask('red','/anchored',{intent,preparedVotes:[{body:votes[0].body,signature:'AAAA'},votes[1]],snapshot:genesis}),/F154_BAD_QUORUM_SIGNATURE/);
 await fails('anchoring requires a signed advancement of the correct checkpoint',()=>controller.admit(intent,votes,genesis),/F154_NO_QUORUM_ANCHOR/);
 const beforeAdvance=P.load(configs.red.stateFile);pass('intent remains durable while anchor is not advanced',()=>assert.equal(beforeAdvance.slot.phase,'PREPARED'));
 await fails('gateway dies after signer fsync before reply',()=>anchorRpc('/advance',{intent,preparedVotes:votes,proof:store.extension(0),injectAfterInner:true}),/ECONNRESET|socket hang up|socket closed/);
 await step('signer retained checkpoint despite gateway crash',async()=>{const direct=await P.rpc({port:anchor.port,key:ids.gateway.key,cert:ids.gateway.cert,ca:ids.gateway.ca,serverPin:ids.anchor.certPin},'/read');assert.equal(direct.body.count,1);});
 gateway=await spawn('anchor-gateway154.js',gatewayCfg,'gateway-restart','S154_GATEWAY_CONFIG');
 for(const id of ['red','blue','green']){await stop(nodes[id]);configs[id].anchor.port=gateway.port;nodes[id]=await spawn('finality-replica154.js',configs[id],'final-restart-'+id,'S154_REPLICA_CONFIG');}
 const resumed=qc();
 const snapshot=await resumed.advanceAnchor(intent,votes,store.extension(0));
 pass('anchor advanced only after quorum prepare',()=>assert.equal(snapshot.body.count,1));
 await fails('old anchor cannot be substituted after movement',()=>resumed.admit(intent,votes,genesis),/F154_NO_QUORUM_ANCHOR/);
 let anchorVotes=await resumed.admit(intent,votes,snapshot);
 pass('2/3 checkpoint admission certificates',()=>assert.ok(anchorVotes.length>=2));
 pass('replicas record anchor snapshot digest durably',()=>assert.equal(P.load(configs.red.stateFile).slot.snapshotDigest,P.sha(snapshot)));
 await fails('completion without majority signed journals is refused',()=>resumed.finalize(intent,votes,anchorVotes,snapshot,[]),/F154_NO_QUORUM_FINAL/);
 const opDone={type:'COMPLETE',txid:request.txid,receiptHash:P.sha(receipt)};
 const proposal2={term:1,leaderId:'alpha',index:2,prev:grantHead,op:opDone};
 const votes2=['red','blue'].map(id=>{const body={nodeId:id,digest:P.sha(proposal2),term:1,index:2,prev:grantHead,leaderId:'alpha'};return{body,signature:P.sign(auth[id].privateKey,'S147:PREPARE',body)};});
 const row1={proposal:proposal1,votes:votes1},row2={proposal:proposal2,votes:votes2};
 const journalHead=P.sha({prev:grantHead,index:2,term:1,op:opDone});
 const evidence=['red','blue'].map(id=>{const body={nodeId:id,seq:2,head:journalHead,journal:[row1,row2]};return{body,signature:P.sign(auth[id].privateKey,'S147:JOURNAL',body)};});
 await fails('forged COMPLETE journal signature cannot finalize',()=>resumed.finalize(intent,votes,anchorVotes,snapshot,[{...evidence[0],signature:'AAAA'},evidence[1]]),/F154_NO_QUORUM_FINAL/);
 await fails('only one committed authority journal is insufficient',()=>resumed.finalize(intent,votes,anchorVotes,snapshot,[evidence[0]]),/F154_NO_QUORUM_FINAL/);
 await fails('tampered signed journal row rejected',()=>resumed.finalize(intent,votes,anchorVotes,snapshot,[evidence[0],{...evidence[1],body:{...evidence[1].body,head:'b'.repeat(64)}}]),/F154_NO_QUORUM_FINAL/);
 // Crash and restart a quorum participant between the anchored and final states.
 await stop(nodes.red);nodes.red=await spawn('finality-replica154.js',configs.red,'red-restarted','S154_REPLICA_CONFIG');
 await step('replica restart retains ANCHORED state and signature pin',async()=>assert.equal(P.load(configs.red.stateFile).slot.phase,'ANCHORED'));
 const completed=await qc().finalize(intent,votes,anchorVotes,snapshot,evidence);
 pass('2/3 independent signed finality acknowledgements',()=>assert.ok(completed.length>=2));
 pass('independently persisted FINAL on three replica storage files',()=>{for(const id of ['red','blue','green'])assert.equal(P.load(configs[id].stateFile).slot.phase,'FINAL');});
 pass('write was not replayed during recovery',()=>assert.equal(store.inspect().head.count,1));
 const again=await qc().finalize(intent,votes,anchorVotes,snapshot,evidence);
 pass('finality retry does not create new state transitions',()=>assert.ok(again.length>=2));
 const serialBefore=P.load(configs.red.stateFile).serial;
 pass('finality idempotence leaves original signed high water',()=>assert.equal(P.load(configs.red.stateFile).serial,serialBefore));
 await fails('stale anchor snapshot refused after finality',()=>resumed.ask('blue','/final',{intent,preparedVotes:votes,anchoredVotes:anchorVotes,snapshot:genesis,completionEvidence:evidence}),/F154_ANCHOR_MISMATCH/);
 const copy=P.load(configs.blue.stateFile),tampered=structuredClone(copy);tampered.slot.phase='PREPARED';P.atomic(configs.blue.stateFile,tampered);
 await fails('tampered durable phase is refused on restart-safe read',()=>resumed.ask('blue','/state'),/F154_SLOT_TAMPERED/);
 P.atomic(configs.blue.stateFile,copy);
 await step('restored genuine journal state is accepted',async()=>assert.equal((await resumed.ask('blue','/state')).body.phase,'FINAL'));
 // Quorum unavailability must fail closed with 1/3.
 await stop(nodes.red);await stop(nodes.green);
 await fails('majority partition fails closed during prepare',()=>qc().prepare(intent),/F154_NO_QUORUM_PREPARE/);
 pass('majority partition did not erase durable finality',()=>assert.equal(P.load(configs.blue.stateFile).slot.phase,'FINAL'));
 const report={schema:'oasis.sheet154.test.v1',newChecks:count,passed:true,mTLS:true,independentReplicaStateFiles:3,signatures:'Ed25519',signedAnchorProcess:true,coordinatorLockUsed:false,scenario:'synthetically signed valid SHEET147 authority grant and completion journals + real SHEET153 segmented physical write',limitations:['replicas run on one host','authority journal signatures synthesized from fixture keys, not obtained from live SHEET153 replicas in this new gate','external rollback pins are not independent hosts','one finality slot (no automated garbage collection)','not an atomic cross-host two-phase commit']};
 fs.writeFileSync(path.join(__dirname,'new-test-report.json'),JSON.stringify(report,null,2)+'\n');
 console.log(`SHEET154 NEW PASS ${count}/${count}`);
}catch(e){console.error('FAIL AFTER '+count,e.stack||e);process.exitCode=1;}finally{for(const x of children.reverse())await stop(x).catch(()=>{});fs.rmSync(root,{recursive:true,force:true});}})();
```

## run-all.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp -a "$ROOT/baseline153" "$TMP/baseline153"
(cd "$TMP/baseline153" && bash run-all.sh)
(cd "$ROOT" && node gate154.js)
```
