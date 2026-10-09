#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const P=require('./baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const {Coordinator}=require('./baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/coordinator147');
const {UnifiedStore}=require('./baseline154/baseline153/unified153');
const {QuorumSlots}=require('./quorum155');
const ZERO='0'.repeat(64);let count=0;
const pass=(label,fn)=>{fn();console.log('PASS',++count,label);},step=async(label,fn)=>{await fn();console.log('PASS',++count,label);},fails=async(label,fn,re)=>step(label,async()=>assert.rejects(fn,re));
const root=fs.mkdtempSync(path.join(os.tmpdir(),'sheet155-')),f=(...p)=>path.join(root,...p),openssl=(...a)=>cp.execFileSync('openssl',a,{cwd:root,stdio:'pipe'});
function cert(n){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',n+'.key','-out',n+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(n+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',n+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',n+'.crt','-days','2','-sha256','-extfile',n+'.ext');return{key:f(n+'.key'),cert:f(n+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(n+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
function keys(n){const x=crypto.generateKeyPairSync('ed25519');const priv=f(n+'.priv'),pub=f(n+'.pub');fs.writeFileSync(priv,x.privateKey.export({type:'pkcs8',format:'pem'}),{mode:0o600});fs.writeFileSync(pub,x.publicKey.export({type:'spki',format:'pem'}));return{priv,pub,privateKey:x.privateKey,publicKey:x.publicKey};}
const children=[];
async function spawn(script,cfg,label,envName){const conf=f(label+'-'+crypto.randomUUID()+'.json');fs.writeFileSync(conf,JSON.stringify(cfg));const proc=cp.fork(path.join(__dirname,script),[],{env:{...process.env,[envName]:conf},stdio:['ignore','pipe','pipe','ipc']});let err='';proc.stderr.on('data',b=>err+=b);const info=await new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(Error('START_TIMEOUT '+label+': '+err)),10000);proc.once('message',m=>{clearTimeout(t);resolve({proc,port:m.port,label,err:()=>err});});proc.once('exit',c=>{clearTimeout(t);reject(Error('START_EXIT '+label+': '+c+' '+err));});});children.push(info);return info;}
async function stop(x){if(!x||x.proc.exitCode!==null||x.proc.signalCode!==null||!x.proc.connected)return;await new Promise(done=>{const t=setTimeout(()=>{x.proc.kill('SIGKILL');done();},1500);x.proc.once('exit',()=>{clearTimeout(t);done();});x.proc.send('stop');});}
(async()=>{try{
 openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=S155-Test-CA');
 const ids=Object.fromEntries(['red','blue','green','alpha','beta','resource','anchor','gateway','floor','rogue'].map(n=>[n,cert(n)]));
 const auth=Object.fromEntries(['red','blue','green','resource','anchor','floor'].map(n=>[n,keys(n)]));
 const fins=Object.fromEntries(['red','blue','green'].map(n=>[n,keys('final-'+n)]));
 const authorityPub=Object.fromEntries(['red','blue','green'].map(n=>[n,auth[n].pub]));
 const finalPub=Object.fromEntries(['red','blue','green'].map(n=>[n,fins[n].pub]));
 const store=new UnifiedStore(f('journal'),'resource',auth.resource.privateKey);store.init();
 const authority={},authorityConfigs={};
 const authReaders={alpha:{certPin:ids.alpha.certPin},beta:{certPin:ids.beta.certPin},...Object.fromEntries(['red','blue','green'].map(n=>['reader_'+n,{certPin:ids[n].certPin}]))};
 for(const id of ['red','blue','green']){authorityConfigs[id]={id,...ids[id],signKey:auth[id].priv,members:Object.fromEntries(['red','blue','green'].map(n=>[n,{publicKey:auth[n].pub}])),leaders:authReaders,stateFile:f('authority-'+id,'state.json')};authority[id]=await spawn('baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/replica147.js',authorityConfigs[id],'authority-'+id,'S147_CONFIG');}
 const endpoints=()=>Object.fromEntries(['red','blue','green'].map(n=>[n,{port:authority[n].port,certPin:ids[n].certPin}]));
 const coord=(leaderId)=>new Coordinator({leaderId,identity:ids[leaderId],replicas:endpoints(),publicKeys:authorityPub});
 const anchorCfg={...ids.anchor,file:f('anchor-floor','current.json'),resourceId:'resource',resourcePublic:auth.resource.pub,anchorPrivate:auth.anchor.priv,anchorPublic:auth.anchor.pub,controlPin:ids.gateway.certPin,readPins:[ids.gateway.certPin]};
 const anchor=await spawn('baseline154/baseline153/baseline152/anchor-server152.js',anchorCfg,'anchor','S152_ANCHOR_CONFIG');
 const floorCfg={...ids.floor,signKey:auth.floor.priv,stateFile:f('floor','state.json'),coordinatorPin:ids.alpha.certPin,finalityPublicKeys:finalPub,readPins:['red','blue','green','gateway','alpha','beta'].map(id=>ids[id].certPin)};
 let floor=await spawn('floor155.js',floorCfg,'floor','S155_FLOOR_CONFIG');
 const floorRpc=(uri,b={})=>P.rpc({...ids.alpha,port:floor.port,serverPin:ids.floor.certPin},uri,b);
 const gatewayCfg={...ids.gateway,coordinatorPin:ids.alpha.certPin,readerPins:['red','blue','green'].map(id=>ids[id].certPin),inner:{port:anchor.port,certPin:ids.anchor.certPin},floor:{port:floor.port,certPin:ids.floor.certPin},floorPublicKey:auth.floor.pub,finalityPublicKeys:finalPub,authorityPublicKeys:authorityPub,resourcePublicKey:auth.resource.pub,testMode:true};
 let gateway=await spawn('anchor-gateway155.js',gatewayCfg,'gateway','S155_GATEWAY_CONFIG');
 const anchorRpc=(uri,b={})=>P.rpc({...ids.alpha,port:gateway.port,serverPin:ids.gateway.certPin},uri,b);
 let prior=await anchorRpc('/init',{checkpoint:store.checkpoint()});
 const nodes={},configs={};
 for(const id of ['red','blue','green']){configs[id]={id,...ids[id],signKey:fins[id].priv,members:finalPub,authorityPublicKeys:authorityPub,authorityMembers:endpoints(),authorityReaderId:'reader_'+id,resourcePublicKey:auth.resource.pub,anchorPublicKey:auth.anchor.pub,floorPublicKey:auth.floor.pub,resourceId:'resource',stateFile:f('finality-'+id,'state.json'),coordinatorPin:ids.alpha.certPin,anchor:{port:gateway.port,certPin:ids.gateway.certPin},floor:{port:floor.port,certPin:ids.floor.certPin}};nodes[id]=await spawn('finality-replica155.js',configs[id],'final-'+id,'S155_REPLICA_CONFIG');}
 const live=()=>Object.fromEntries(Object.entries(nodes).filter(([,v])=>v.proc.exitCode===null&&v.proc.signalCode===null).map(([id,v])=>[id,{port:v.port,certPin:ids[id].certPin}]));
 const qc=()=>new QuorumSlots({identity:ids.alpha,replicas:live(),publicKeys:Object.fromEntries(Object.entries(fins).map(([id,k])=>[id,k.publicKey])),resourcePub:auth.resource.pub,anchorPub:auth.anchor.pub,anchor:{port:gateway.port,certPin:ids.gateway.certPin},authorityKeys:Object.fromEntries(Object.entries(auth).filter(([id])=>['red','blue','green'].includes(id)).map(([id,k])=>[id,k.publicKey]))});
 pass('three live S147 authority mTLS processes',()=>assert.equal(Object.keys(authority).length,3));
 pass('three independent durable finality replicas',()=>assert.equal(Object.keys(nodes).length,3));
 pass('independent rollback-floor service',()=>assert.ok(floor.port>0));
 const genesisFloor=await floorRpc('/read');pass('signed genesis rollback floor',()=>assert.equal(genesisFloor.body.slot,0));
 const floorVotes=(intent,snapshot,finalVotes)=>({record:{slot:intent.slot,prev:intent.prevPinDigest,intentDigest:P.sha(intent),snapshotDigest:P.sha(snapshot),receiptHash:P.sha(intent.receipt)},finalVotes});
 let currentPin=genesisFloor.body.head,oldIntent=null,oldVotes=null,oldSnapshot=null;
 for(let n=1;n<=3;n++){
  const leader=n%2?'alpha':'beta';const a=coord(leader);await step(`cycle ${n}: real S147 leader election ${leader}`,async()=>{await a.elect();});
  const request={txid:'cycle_'+String(n).padStart(3,'0'),resourceId:'resource',operationId:'write',value:'ledger-'+n,epoch:1}, digest=P.sha(request);
  const begin=await a.run({type:'BEGIN',txid:request.txid,resourceId:'resource',digest});
  const states=['red','blue'].map(id=>begin.seq&&begin.head?null:null);
  const rows=await a.all('/state');const matching=rows.filter(r=>r.response?.body.seq===begin.seq&&r.response.body.head===begin.head).map(r=>r.response);
  assert.ok(matching.length>=2);
  const grant={schema:'oasis.sheet148.grant.v1',certificate:begin.certificate,seq:begin.seq,head:begin.head,epoch:begin.epoch,states:matching};
  pass(`cycle ${n}: real 2/3 BEGIN grant`,()=>assert.ok(matching.length>=2));
  const receipt=store.commit(request,{head:begin.head});pass(`cycle ${n}: physical segmented write`,()=>assert.equal(receipt.body.sequence,n));
  const intent={...qc().createIntent({request,grant,receipt,store,prior}),slot:n,prevPinDigest:currentPin};
  if(n===1){await fails('untrusted TLS identity cannot write finality replica',()=>P.rpc({...ids.rogue,port:nodes.red.port,serverPin:ids.red.certPin},'/prepare',{intent,slot:n,prevPinDigest:currentPin}),/TLS_PEER_NOT_PINNED/);
   await fails('gateway cannot advance without signed prepare quorum',()=>anchorRpc('/advance',{intent,preparedVotes:[],proof:store.extension(prior.body.count)}),/G155_MAJORITY_REQUIRED/);
   await fails('finality refuses unsigned receipt',()=>qc().ask('red','/prepare',{intent:{...intent,receipt:{...receipt,signature:'AAAA'}},slot:n,prevPinDigest:currentPin}),/F154_BAD_RECEIPT/);
   await fails('slot gap refused',()=>qc().ask('blue','/prepare',{intent,slot:3,prevPinDigest:currentPin}),/S155_SLOT_ORDER_OR_GAP/);}
  const votes=await qc().prepare(intent);pass(`cycle ${n}: 2/3 durable finality PREPARED`,()=>assert.ok(votes.length>=2));
  if(n===1){await fails('wrong prepared quorum domain rejected at gateway',()=>anchorRpc('/advance',{intent,preparedVotes:[{...votes[0],signature:'AAAA'},votes[1]],proof:store.extension(prior.body.count)}),/G155_BAD_PREPARE_VOTE/);
   await fails('coordinator denied direct signer advance',()=>P.rpc({...ids.alpha,port:anchor.port,serverPin:ids.anchor.certPin},'/advance',{checkpoint:intent.checkpoint,proof:store.extension(prior.body.count)}),/TLS_PEER_NOT_PINNED/);}
  const snap=await qc().advanceAnchor(intent,votes,store.extension(prior.body.count));pass(`cycle ${n}: anchored checkpoint advanced`,()=>assert.equal(snap.body.count,n));
  const anchored=await qc().admit(intent,votes,snap);pass(`cycle ${n}: signed ANCHORED quorum`,()=>assert.ok(anchored.length>=2));
  if(n===1)await fails('completion before live authority COMPLETE refused',()=>qc().finalize(intent,votes,anchored,snap,[]),/S155_LIVE_AUTHORITY_MAJORITY_REQUIRED|S155_NO_QUORUM_FINAL/);
  // This is an authentic S147 COMPLETE certificate, persisted in the live S147 replica journals.
  const done=await a.run({type:'COMPLETE',txid:request.txid,receiptHash:P.sha(receipt)});pass(`cycle ${n}: live majority COMPLETE`,()=>assert.ok(done.committedBy.length>=2));
  if(n===2){await stop(nodes.red);nodes.red=await spawn('finality-replica155.js',configs.red,'red-restarted','S155_REPLICA_CONFIG');await step('second cycle: restarted replica retained prepared and anchored state',async()=>assert.equal(P.load(configs.red.stateFile).slot.phase,'ANCHORED'));}
  const finalVotes=await qc().finalize(intent,votes,anchored,snap,[]);pass(`cycle ${n}: 2/3 verified live authority journals`,()=>assert.ok(finalVotes.length>=2));
  if(n===1){await fails('floor rejects missing final quorum',()=>floorRpc('/pin',{record:floorVotes(intent,snap,finalVotes).record,finalVotes:[finalVotes[0]]}),/S155_FLOOR_NEEDS_2_OF_3/);
   await fails('floor rejects altered final signatures',()=>floorRpc('/pin',{record:floorVotes(intent,snap,finalVotes).record,finalVotes:[{...finalVotes[0],signature:'AAAA'},finalVotes[1]]}),/S155_FLOOR_BAD_CERT/);}
  const pinned=await floorRpc('/pin',floorVotes(intent,snap,finalVotes));pass(`cycle ${n}: quorum-certified external pin`,()=>assert.equal(pinned.body.slot,n));
  currentPin=pinned.body.head;prior=snap;oldIntent=intent;oldVotes=votes;oldSnapshot=snap;
  pass(`cycle ${n}: no duplicate physical write`,()=>assert.equal(store.inspect().head.count,n));
  if(n===1){await fails('old signed floor snapshot cannot advance new slot',()=>qc().ask('blue','/prepare',{intent:{...intent,txid:'bad'},slot:2,prevPinDigest:ZERO}),/S155_PIN_ROLLBACK_OR_MISSING|F154_INTENT_REQUIRED/);}
 }
 pass('three unique physical transaction IDs committed',()=>assert.equal(new Set(store.inspect().records.map(x=>JSON.parse(x.payload).txid)).size,3));
 pass('finality replicas each retained three full slots',()=>{for(const id of ['red','blue','green'])assert.equal(P.load(configs[id].stateFile).finals.length,3);});
 const prevFile=P.load(configs.blue.stateFile);const snapFloor=await floorRpc('/read');pass('external floor pins slot three',()=>assert.equal(snapFloor.body.slot,3));
 // Rollback simulated by replacing one replica with its genesis state. Its own hash chain is valid but external floor detects it.
 const genesis={schema:'oasis.sheet155.finality.v1',nodeId:'blue',serial:0,head:ZERO,events:[],slot:null,finals:[]};P.atomic(configs.blue.stateFile,genesis);
 await fails('valid-looking local rollback detected against external pin',()=>qc().ask('blue','/state'),/S155_REPLICA_ROLLBACK_BELOW_EXTERNAL_FLOOR/);
 P.atomic(configs.blue.stateFile,prevFile);
 await step('restored authentic finality history passes rollback floor',async()=>assert.equal((await qc().ask('blue','/state')).body.completed,3));
 const floorStored=P.load(floorCfg.stateFile);pass('floor stores hash-linked three-slot history',()=>assert.equal(floorStored.history.length,3));
 const tampered=structuredClone(floorStored);tampered.history[0].receiptHash='f'.repeat(64);P.atomic(floorCfg.stateFile,tampered);
 await fails('tampering with external floor history halts further reads',()=>floorRpc('/read'),/S155_FLOOR_TAMPER/);
 P.atomic(floorCfg.stateFile,floorStored);
 await step('authentic floor history restores readable checkpoint',async()=>assert.equal((await floorRpc('/read')).body.slot,3));
 const pendingLeader=coord('beta');await pendingLeader.elect();const fourth={txid:'pending_004',resourceId:'resource',operationId:'write',value:'partition-proof',epoch:1};const fourthBegin=await pendingLeader.run({type:'BEGIN',txid:fourth.txid,resourceId:'resource',digest:P.sha(fourth)});const fourthStates=(await pendingLeader.all('/state')).filter(x=>x.response?.body.seq===fourthBegin.seq&&x.response.body.head===fourthBegin.head).map(x=>x.response);const fourthGrant={schema:'oasis.sheet148.grant.v1',certificate:fourthBegin.certificate,seq:fourthBegin.seq,head:fourthBegin.head,epoch:1,states:fourthStates};const fourthReceipt=store.commit(fourth,{head:fourthBegin.head});const fourthIntent={...qc().createIntent({request:fourth,grant:fourthGrant,receipt:fourthReceipt,store,prior}),slot:4,prevPinDigest:currentPin};
 pass('fourth real pending grant prepared as partition probe',()=>assert.equal(fourthReceipt.body.sequence,4));
 await stop(authority.red);await stop(authority.green);
 await fails('loss of two live authority replicas fails closed',()=>qc().ask('blue','/prepare',{intent:fourthIntent,slot:4,prevPinDigest:currentPin}),/S155_LIVE_AUTHORITY_MAJORITY_REQUIRED/);
 pass('partitioned fourth write remains unfinalized and pin stays on slot three',()=>assert.equal(P.load(floorCfg.stateFile).slot,3));
 const report={schema:'oasis.sheet155.test.v1',newChecks:count,passed:true,cycles:3,liveAuthorityReplicas:3,finalityReplicas:3,externalFloorProcess:1,physicalWrites:4,finalizedWrites:3,leaderReplacements:2,localHostOnly:true,limitations:['all services run on one physical host','external floor uses one signer and is not a distributed quorum itself','leader journal API is permitted for authenticated reader IDs','S147 COMPLETE operation still accepts receipt hash unless routed through higher layers','no global cross-host linearizability proof','S142 older timing-sensitive test']};
 fs.writeFileSync(path.join(__dirname,'new-test-report.json'),JSON.stringify(report,null,2)+'\n');console.log(`SHEET155 NEW PASS ${count}/${count}`);
}catch(e){console.error('FAIL AFTER '+count,e.stack||e);process.exitCode=1;}finally{for(const x of children.reverse())await stop(x).catch(()=>{});fs.rmSync(root,{recursive:true,force:true});}})();
