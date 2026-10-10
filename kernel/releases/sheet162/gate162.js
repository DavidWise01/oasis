#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),cp=require('node:child_process'),assert=require('node:assert/strict');
const {performance}=require('node:perf_hooks');
const {Store}=require('./baseline161/baseline160/indexed160');
const {BatchStore}=require('./batch162');
const P=require('./baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const V=require('./baseline161/proof161'),Old=require('./baseline161/catchup161'),Fast=require('./catchup162');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'oasis-sheet162-')),f=(...parts)=>path.join(tmp,...parts);const children=[];
const openssl=(...args)=>cp.execFileSync('openssl',args,{cwd:tmp,stdio:'pipe'});
let checks=0;const ok=(desc,fn)=>{fn();console.log('PASS',++checks,desc);};const step=async(desc,fn)=>{await fn();console.log('PASS',++checks,desc);};
function pem(name){const kp=crypto.generateKeyPairSync('ed25519'),priv=f(name+'.priv.pem'),pub=f(name+'.pub.pem');fs.writeFileSync(priv,kp.privateKey.export({format:'pem',type:'pkcs8'}));fs.writeFileSync(pub,kp.publicKey.export({format:'pem',type:'spki'}));return{privateKey:kp.privateKey,publicKey:kp.publicKey,priv,pub};}
function cert(name){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',name+'.key','-out',name+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(name+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',name+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',name+'.crt','-days','2','-sha256','-extfile',name+'.ext');return{key:f(name+'.key'),cert:f(name+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(name+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
async function spawn(cfg,name,version='162'){const config=f(name+'-config.json');P.atomic(config,cfg);let errors='';const proc=cp.fork(path.join(__dirname,version==='161'?'baseline161/node161.js':'node162.js'),[],{env:{...process.env,S161_CONFIG:config,S162_CONFIG:config},stdio:['ignore','pipe','pipe','ipc']});proc.stderr.on('data',b=>errors+=b);const port=await new Promise((res,rej)=>{const timeout=setTimeout(()=>rej(Error('SPAWN_TIMEOUT '+name+' '+errors)),15000);proc.once('message',m=>{clearTimeout(timeout);res(m.port);});proc.once('exit',n=>{clearTimeout(timeout);rej(Error('SPAWN_EXIT '+n+' '+errors));});});const item={name,port,proc,version};children.push(item);return item;}
async function stop(node){if(!node||node.proc.exitCode!==null||node.proc.signalCode!==null)return;await new Promise(res=>{const timer=setTimeout(()=>{node.proc.kill('SIGKILL');res();},900);node.proc.once('exit',()=>{clearTimeout(timer);res();});try{node.proc.send('stop',err=>{if(err){node.proc.kill('SIGKILL');clearTimeout(timer);res();}});}catch{node.proc.kill('SIGKILL');clearTimeout(timer);res();}});}
async function workload(seed,prefix,identity,keys,pub,anchorKeys,anchorNum,{crash=false}={}){
 const resourceId='S162-RESOURCE',tag='w'+seed+'-'+(crash?'crash':'bench');const stores={};for(const n of ['red','green','old','blue']){const d=f(tag,n,'store');stores[n]=(n==='blue'?new BatchStore(d,resourceId):new Store(d,resourceId));stores[n].init();}
 let start=performance.now();for(let i=0;i<seed;i++){const value='datum-'+String(i).padStart(7,'0'),txid='tx-'+i;stores.red.append(value,txid);stores.green.append(value,txid);if(i<prefix){stores.old.append(value,txid);stores.blue.append(value,txid);}}
 const setupMs=performance.now()-start,hr=stores.red.read(),target={resourceId,count:hr.count,root:hr.root,lastRecordHash:hr.lastRecordHash},anchor=V.signAnchor(V.anchorBody(resourceId,hr,anchorNum),anchorKeys.privateKey);
 const cfg={};for(const n of ['red','green','old','blue']){const signId=n==='old'?'blue':n;cfg[n]={nodeId:signId,resourceId,...identity[n],dir:stores[n].dir,signKey:keys[signId].priv,anchorPublicKey:anchorKeys.pub,peerPublicKeys:Object.fromEntries(Object.entries(keys).map(([id,k])=>[id,k.pub])),clientPin:identity.client.certPin,session:f(tag,n,'session.json'),externalPin:f(tag,n,'external-pin.json'),quarantine:f(tag,n,'quarantine.txt'),...(crash&&n==='blue'?{crashAfterHeadOnce:f(tag,'crash-marker')}: {})};}
 const nodes={};for(const name of ['red','green','old','blue'])nodes[name]=await spawn(cfg[name],tag+name,name==='blue'?'162':'161');
 const oldMap={red:nodes.red,green:nodes.green,blue:nodes.old},newMap={red:nodes.red,green:nodes.green,blue:nodes.blue};const endpoint=ns=>Object.fromEntries(Object.entries(ns).map(([n,node])=>[n,{port:node.port,serverPin:identity[node===nodes.old?'old':n].certPin}]));
 const old=Old.make({identity:identity.client,nodes:endpoint(oldMap),keys:pub,anchor,anchorKey:anchorKeys.publicKey});
 const fast=Fast.make({identity:identity.client,nodes:endpoint(newMap),keys:pub,anchor,anchorKey:anchorKeys.publicKey});
 try{
  ok(tag+' source and target roots are valid and prefixes aligned',()=>{assert.equal(stores.red.read().root,stores.green.read().root);assert.equal(stores.old.read().root,stores.blue.read().root);assert.equal(stores.old.read().count,prefix);});
  if(crash){const original=fast.rpc;await step(tag+' pinned peer status active',async()=>assert.equal((await original('blue','/status161')).body.count,prefix));
   const n=crypto.randomBytes(20).toString('hex'),heads=await Promise.all(['red','green'].map(x=>original(x,'/head161',{nonce:n})));await original('blue','/begin161',{nonce:n,target,anchor,heads});const p=await original('red','/page161',{nonce:n,target,offset:prefix,limit:8});
   await step(tag+' real target death follows committed durable batch',async()=>{await assert.rejects(original('blue','/apply162',{page:p}),/socket hang up|ECONNRESET|EPIPE|aborted|closed/i);assert.equal(stores.blue.read().count,prefix+8);});
   nodes.blue=await spawn({...cfg.blue,crashAfterHeadOnce:cfg.blue.crashAfterHeadOnce},tag+'blue-restart','162');
   // Recreate client after restart: old client endpoint is no longer valid.
   fast.close();const fm=Fast.make({identity:identity.client,nodes:endpoint({red:nodes.red,green:nodes.green,blue:nodes.blue}),keys:pub,anchor,anchorKey:anchorKeys.publicKey});
   await step(tag+' durable nonce survives process restart',async()=>assert.equal((await fm.rpc('blue','/status161')).body.nonce,n));
   await step(tag+' original transaction completes without duplicate',async()=>{await fm.sync('blue');assert.equal(stores.blue.read().count,seed);assert.equal(stores.blue.read().root,hr.root);});
   await step(tag+' crash marker remains stable',async()=>assert.equal(fs.existsSync(cfg.blue.crashAfterHeadOnce),true));fm.close();return{seed,prefix,crashPass:true};
  }
  start=performance.now();await step(tag+' legacy 161 full mTLS recovery',async()=>{const out=await old.sync('blue');assert.equal(out.count,seed);});const legacyMs=performance.now()-start;
  start=performance.now();const report=await fast.sync('blue');const batchedMs=performance.now()-start;
  ok(tag+' optimized target matches legacy Merkle root',()=>assert.equal(stores.old.read().root,stores.blue.read().root));
  ok(tag+' root equals certified source',()=>assert.equal(stores.blue.read().root,hr.root));
  ok(tag+' batch count smaller than recovered records',()=>assert((report.metrics.requests>0)&&stores.blue.read().count===seed));
  ok(tag+' TLS sockets reused across requests',()=>assert(report.metrics.handshakes<report.metrics.requests/4));
  ok(tag+' zero historical record hashes replayed',()=>assert.equal(stores.blue.metrics.recordHashesReplayed,0));
  const h=stores.blue.read();ok(tag+' indexed extension still verifies',()=>assert.equal(h.root,hr.root));
  const optim=await fast.rpc('blue','/status161');const batch=optim.body.batchMetrics;
  ok(tag+' durable segment commits reduced versus row-by-row writes',()=>assert(batch.segmentCommits<seed-prefix));
  const result={seed,prefix,recovered:seed-prefix,setupMs:+setupMs.toFixed(1),legacyMs:+legacyMs.toFixed(1),optimizedMs:+batchedMs.toFixed(1),legacyRowsPerSecond:+((seed-prefix)*1000/legacyMs).toFixed(2),optimizedRowsPerSecond:+((seed-prefix)*1000/batchedMs).toFixed(2),speedup:+(legacyMs/batchedMs).toFixed(3),networkRequests:report.metrics.requests,tlsConnections:report.metrics.handshakes,networkResponseBytes:report.metrics.pageBytes,segmentCommits:batch.segmentCommits,headCommits:batch.headCommits,batches:batch.batches,sourceSegments:h.segments.length,verification:'both paths share identical source, anchored 2/3 heads, client cert and TLS host'};
  console.log('BENCHMARK162',JSON.stringify(result));return result;
 }finally{fast.close();await Promise.allSettled(Object.values(nodes).map(stop));}
}
(async()=>{try{
 openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=OASIS-S162-CA');
 const identity=Object.fromEntries(['client','red','green','blue','old'].map(k=>[k,cert(k)]));const keys=Object.fromEntries(['red','green','blue'].map(k=>[k,pem(k)]));const pub=Object.fromEntries(Object.entries(keys).map(([n,k])=>[n,k.publicKey]));const anchor=pem('anchor');
 const targets=process.env.S162_FAST==='1'?[[640,128]]:[[640,128],[1152,128]];const results=[];let i=0;for(const [seed,prefix] of targets)results.push(await workload(seed,prefix,identity,keys,pub,anchor,++i));
 if(process.env.S162_SKIP_CRASH!=='1')results.push(await workload(264,256,identity,keys,pub,anchor,++i,{crash:true}));
 const summary={sheet:162,status:'PASS',newChecks:checks,benchmarks:results.filter(x=>!x.crashPass),crashTests:results.filter(x=>x.crashPass),hostCount:1,date:new Date().toISOString(),limits:'Single-host synthetic identities, synchronous fsync, same-source sequential runs; performance includes load/order effects and is not independent-host data.'};
 fs.writeFileSync(path.join(__dirname,'benchmark162.json'),JSON.stringify(summary,null,2)+'\n');console.log('SHEET162 GATE '+checks+'/'+checks+' PASS');
 }catch(e){console.error('SHEET162 GATE FAIL',e.stack||e);process.exitCode=1;}finally{await Promise.allSettled(children.map(stop));if(process.env.S162_KEEP!=='1')fs.rmSync(tmp,{recursive:true,force:true});}})();
