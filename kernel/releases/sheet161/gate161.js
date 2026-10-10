#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),cp=require('node:child_process'),assert=require('node:assert/strict'),{performance}=require('node:perf_hooks');
const {Store}=require('./baseline160/indexed160');
const P=require('./baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const M=require('./baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/merkle151');
const V=require('./proof161'),C=require('./catchup161');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'oasis-sheet161-'));const f=(...a)=>path.join(tmp,...a);let n=0;const ok=(s,fn)=>{fn();console.log('PASS',++n,s);};const step=async(s,fn)=>{await fn();console.log('PASS',++n,s);};const bad=async(s,fn,re)=>step(s,()=>assert.rejects(fn,re));const openssl=(...args)=>cp.execFileSync('openssl',args,{cwd:tmp,stdio:'pipe'});
const children=[];
function pem(id){const pair=crypto.generateKeyPairSync('ed25519'),priv=f(id+'.priv.pem'),pub=f(id+'.pub.pem');fs.writeFileSync(priv,pair.privateKey.export({format:'pem',type:'pkcs8'}));fs.writeFileSync(pub,pair.publicKey.export({format:'pem',type:'spki'}));return{privateKey:pair.privateKey,publicKey:pair.publicKey,priv,pub};}
function cert(id){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',id+'.key','-out',id+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(id+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',id+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',id+'.crt','-days','2','-sha256','-extfile',id+'.ext');return{key:f(id+'.key'),cert:f(id+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(id+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
async function spawn(cfg,name){const config=f('cfg-'+name+'.json');P.atomic(config,cfg);let err='';const proc=cp.fork(path.join(__dirname,'node161.js'),[],{env:{...process.env,S161_CONFIG:config},stdio:['ignore','pipe','pipe','ipc']});proc.stderr.on('data',b=>err+=b);const port=await new Promise((res,rej)=>{const timer=setTimeout(()=>rej(Error('START_TIMEOUT '+name+' '+err)),15000);proc.once('message',x=>{clearTimeout(timer);res(x.port);});proc.once('exit',code=>{clearTimeout(timer);rej(Error('START_EXIT '+code+' '+err));});});const item={proc,port,name};children.push(item);return item;}
async function stop(x){if(!x||x.proc.exitCode!==null||x.proc.signalCode!==null)return;await new Promise(resolve=>{const t=setTimeout(()=>{x.proc.kill('SIGKILL');resolve();},1500);x.proc.once('exit',()=>{clearTimeout(t);resolve();});try{x.proc.send('stop',e=>{if(e){x.proc.kill('SIGKILL');clearTimeout(t);resolve();}});}catch{x.proc.kill('SIGKILL');clearTimeout(t);resolve();}});}
(async()=>{try{
 openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=OASIS-S161-CA');
 const ids=Object.fromEntries(['client','red','green','blue','rogue'].map(id=>[id,cert(id)]));const keys=Object.fromEntries(['red','green','blue'].map(id=>[id,pem(id)])),publicKeys=Object.fromEntries(Object.entries(keys).map(([id,k])=>[id,k.publicKey]));const anchorKeys=pem('anchor');const resourceId='S161-RESOURCE';
 const stores={};for(const id of ['red','green','blue']){stores[id]=new Store(f(id,'store'),resourceId);stores[id].init();}
 const seed=Number(process.env.S161_SEED||640),prefix=Number(process.env.S161_PREFIX||32);
 let start=performance.now();for(let i=0;i<seed;i++){const pay='datum-'+String(i).padStart(6,'0');stores.red.append(pay,'tx-'+i);stores.green.append(pay,'tx-'+i);if(i<prefix)stores.blue.append(pay,'tx-'+i);}const seedMs=performance.now()-start;
 const hr=stores.red.read(),hg=stores.green.read(),hb=stores.blue.read();const tgt={resourceId,count:hr.count,root:hr.root,lastRecordHash:hr.lastRecordHash};const anchor=V.signAnchor(V.anchorBody(resourceId,hr,1),anchorKeys.privateKey);
 ok('both mTLS sources have identical signed Merkle head',()=>assert.equal(hr.root,hg.root));
 ok('recovery target intentionally behind the quorum',()=>assert.equal(hb.count,prefix));
 ok('physical 256-record segment rollover exercised',()=>assert(hr.count>512&&hr.segments.length>=3));
 ok('externally signed floor checkpoint authentic',()=>assert.equal(V.checkAnchor(anchor,anchorKeys.publicKey).count,seed));
 ok('forged floor checkpoint denied',()=>assert.throws(()=>V.checkAnchor({...anchor,signature:'wrong'},anchorKeys.publicKey),/S161_ANCHOR_SIGNATURE/));
 const cfg={};for(const id of ['red','green','blue'])cfg[id]={nodeId:id,resourceId,...ids[id],dir:stores[id].dir,signKey:keys[id].priv,anchorPublicKey:anchorKeys.pub,peerPublicKeys:Object.fromEntries(Object.entries(keys).map(([k,v])=>[k,v.pub])),clientPin:ids.client.certPin,session:f(id,'session.json'),externalPin:f(id,'external-pin.json'),quarantine:f(id,'quarantine.txt'),...(id==='blue'?{crashOnce:f('blue-crash-once')}:{})};
 const nodes={};for(const id of ['red','green','blue'])nodes[id]=await spawn(cfg[id],id);
 const endpoints=()=>Object.fromEntries(Object.entries(nodes).map(([id,node])=>[id,{port:node.port,serverPin:ids[id].certPin}]));
 const api=()=>C.make({identity:ids.client,nodes:endpoints(),keys:publicKeys,anchor,anchorKey:anchorKeys.publicKey});const rpc=(id,p,b)=>api().rpc(id,p,b);
 await step('three pinned mTLS indexed-proof endpoints started',async()=>assert.equal((await rpc('red','/status161')).body.count,seed));
 const nonce=crypto.randomBytes(20).toString('hex'),heads=await Promise.all(['red','green'].map(x=>rpc(x,'/head161',{nonce})));
 ok('majority heads certify anchor root',()=>assert.equal(V.certified(tgt,heads,nonce,publicKeys),true));
 ok('duplicate signer cannot create majority',()=>assert.throws(()=>V.certified(tgt,[heads[0],heads[0]],nonce,publicKeys),/S161_CERT_SIGNATURE/));
 ok('one signer is not a majority',()=>assert.throws(()=>V.certified(tgt,heads.slice(0,1),nonce,publicKeys),/S161_CERT_QUORUM/));
 await bad('TLS unpinned client rejected',()=>P.rpc({...ids.rogue,...endpoints().red},'/head161',{nonce}),/TLS_PEER_NOT_PINNED/);
 const pg=(await rpc('red','/page161',{nonce,target:tgt,offset:prefix,limit:6}));
 ok('network Merkle page has bounded six records',()=>assert.equal(pg.body.records.length,6));
 await step('proof request touches no historical hash replay',async()=>assert.equal((await rpc('red','/status161')).body.recordHashesReplayed,0));
 const bstate=stores.blue.read();
 ok('network inclusion and extension verify against live indexed source',()=>assert.equal(V.verifyPage(pg,{nonce,target:tgt,keys:publicKeys,allowed:['red','green'],local:{count:bstate.count,frontier:bstate.frontier,root:bstate.root},lastRecordHash:bstate.lastRecordHash}).length,6));
 ok('tampered leaf rejected',()=>{const b=structuredClone(pg);b.body.records[0].record.payload='forged';b.signature=P.sign(keys.red.privateKey,'S161:PAGE',b.body);assert.throws(()=>V.verifyPage(b,{nonce,target:tgt,keys:publicKeys,allowed:['red','green'],local:{count:bstate.count,frontier:bstate.frontier,root:bstate.root},lastRecordHash:bstate.lastRecordHash}),/S161_RECORD_CHAIN/);});
 ok('tampered inclusion proof rejected',()=>{const b=structuredClone(pg);b.body.records[0].inclusion.siblings[0]='f'.repeat(64);b.signature=P.sign(keys.red.privateKey,'S161:PAGE',b.body);assert.throws(()=>V.verifyPage(b,{nonce,target:tgt,keys:publicKeys,allowed:['red','green'],local:{count:bstate.count,frontier:bstate.frontier,root:bstate.root},lastRecordHash:bstate.lastRecordHash}),/INCLUSION_PEAK_MISMATCH|INCLUSION_ROOT_MISMATCH/);});
 ok('tampered extension rejected',()=>{const b=structuredClone(pg);b.body.extension.blocks[0].root='f'.repeat(64);b.signature=P.sign(keys.red.privateKey,'S161:PAGE',b.body);assert.throws(()=>V.verifyPage(b,{nonce,target:tgt,keys:publicKeys,allowed:['red','green'],local:{count:bstate.count,frontier:bstate.frontier,root:bstate.root},lastRecordHash:bstate.lastRecordHash}),/EXTENSION_ROOT_MISMATCH/);});
 await bad('one signed head cannot open recovery',()=>rpc('blue','/begin161',{nonce,target:tgt,anchor,heads:[heads[0]]}),/S161_CERT_QUORUM/);
 await bad('forged external floor denies recovery',()=>rpc('blue','/begin161',{nonce,target:tgt,anchor:{...anchor,signature:'invalid'},heads}),/S161_ANCHOR_SIGNATURE/);
 await step('begin persists independent rollback pin before recovery',async()=>assert.equal((await rpc('blue','/begin161',{nonce,target:tgt,anchor,heads})).body.active,true));
 ok('rollback pin retained out of the journal',()=>assert.equal(P.load(cfg.blue.externalPin).body.root,tgt.root));
 await bad('out-of-order page rejected',async()=>rpc('blue','/apply161',{page:await rpc('green','/page161',{nonce,target:tgt,offset:prefix+8,limit:4})}),/S161_PAGE_CONTEXT/);
 await bad('forged signed page rejected',()=>rpc('blue','/apply161',{page:{...pg,signature:'bad'}}),/S161_PAGE_SIGNATURE/);
 await bad('real target process killed after fsync before ACK',()=>rpc('blue','/apply161',{page:pg}),/socket hang up|ECONNRESET|EPIPE/);
 ok('single record survived process kill',()=>assert.equal(stores.blue.read().count,prefix+1));
 nodes.blue=await spawn(cfg.blue,'blue-restart');
 await step('durable session resumes with the original signed nonce',async()=>assert.equal((await rpc('blue','/status161')).body.nonce,nonce));
 const pages=[],pageBytes=[];start=performance.now();await step('network recovery completes using indexed proofs',async()=>{const r=await api().sync('blue',{limit:8,onPage:(n,bytes)=>{pages.push(n);pageBytes.push(bytes)}});assert.equal(r.count,seed);});const recoveryMs=performance.now()-start;
 ok('target and certified source roots equal',()=>assert.equal(stores.blue.read().root,hr.root));
 ok('restart consumed exactly the missing records without duplication',()=>assert.equal(stores.blue.read().count,seed));
 ok('target no longer has an active recovery session',()=>assert.equal(fs.existsSync(cfg.blue.session),false));
 await step('network recovery never replayed historical hashes',async()=>assert.equal((await rpc('blue','/status161')).body.recordHashesReplayed,0));
 ok('more than two network pages transferred',()=>assert(pages.length>2));
 await bad('post-finalization stale page denied',()=>rpc('blue','/apply161',{page:pg}),/S161_NO_SESSION/);
 const olderHead={...tgt,count:tgt.count-1};const older=V.signAnchor({...V.anchorBody(resourceId,hr,1),count:hr.count-1},anchorKeys.privateKey);
 await bad('older signed rollback floor refused',()=>rpc('blue','/begin161',{nonce:crypto.randomBytes(20).toString('hex'),target:olderHead,anchor:older,heads}),/S161_CERT_SIGNATURE|S161_FLOOR_TARGET/);
 // New slot moves certified head forward while retaining the old signed high-water pin.
 const nextPay='datum-'+seed;stores.red.append(nextPay,'tx-'+seed);stores.green.append(nextPay,'tx-'+seed);const h2=stores.red.read();
 const anchor2=V.signAnchor(V.anchorBody(resourceId,h2,2),anchorKeys.privateKey);
 await step('next independently pinned epoch is recovered',async()=>{const a2=C.make({identity:ids.client,nodes:endpoints(),keys:publicKeys,anchor:anchor2,anchorKey:anchorKeys.publicKey});await a2.sync('blue',{limit:1});assert.equal(stores.blue.read().root,h2.root);});
 ok('pin advances monotonically to epoch two',()=>assert.equal(P.load(cfg.blue.externalPin).body.sequence,2));
 const h3=stores.red.read(),n3=crypto.randomBytes(20).toString('hex'),sameHeads=await Promise.all(['red','green'].map(id=>rpc(id,'/head161',{nonce:n3})));
 const signedOldSeq=V.signAnchor(V.anchorBody(resourceId,h3,1),anchorKeys.privateKey);
 await bad('valid but stale external anchor sequence rejected',()=>rpc('blue','/begin161',{nonce:n3,target:{resourceId,count:h3.count,root:h3.root,lastRecordHash:h3.lastRecordHash},anchor:signedOldSeq,heads:sameHeads}),/S161_ROLLBACK_FLOOR/);
 const finalStatus=(await rpc('blue','/status161')).body;const report={sheet:161,status:'PASS',newChecks:n,physicalHostCount:1,sourceNodes:2,targetNodes:1,initialRecords:seed,targetStart:prefix,caughtUpRecords:seed-prefix,sourceSegmentSize:256,networkPages:pages.length,networkPageBytes:pageBytes.reduce((a,b)=>a+b,0),meanPageBytes:+(pageBytes.reduce((a,b)=>a+b,0)/pageBytes.length).toFixed(1),maxPageBytes:Math.max(...pageBytes),receiverRssMiB:finalStatus.rssMiB,sourceSeedMs:+seedMs.toFixed(2),recoveryMs:+recoveryMs.toFixed(2),recoveryRecordsPerSecond:+((seed-prefix)/(recoveryMs/1000)).toFixed(2),meanNetworkPageMs:+(recoveryMs/pages.length).toFixed(2),currentRoot:h2.root,recordHashesReplayedOnOrdinaryPath:0,crashWindow:'after fsync, before response',note:'Single physical host. TLS handshakes per RPC. Benchmark includes per-record fsync, page proofs and network roundtrips.'};
 fs.writeFileSync(path.join(__dirname,'benchmark161.json'),JSON.stringify(report,null,2)+'\n');
 fs.writeFileSync(path.join(__dirname,'new-test-report.json'),JSON.stringify({sheet:161,passed:n,failed:0,status:'PASS'},null,2)+'\n');
 console.log('SHEET161 GATE '+n+'/'+n+' PASS');console.log('SHEET161 BENCHMARK '+JSON.stringify(report));
 }catch(e){console.error('SHEET161 GATE FAIL',e.stack||e);process.exitCode=1;}finally{await Promise.allSettled(children.map(stop));if(!process.env.S161_KEEP_FIXTURE)fs.rmSync(tmp,{recursive:true,force:true});}})();
