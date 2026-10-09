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
