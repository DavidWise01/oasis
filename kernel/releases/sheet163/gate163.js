'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {performance}=require('node:perf_hooks');
const {BatchStore}=require('./baseline162/batch162');
const P=require('./baseline162/baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const V=require('./baseline162/baseline161/proof161');
const Pipeline=require('./pipeline163');
let checks=0;function test(label,fn){fn();console.log('PASS',++checks,label);}async function asyncTest(label,fn){await fn();console.log('PASS',++checks,label);}
const root=fs.mkdtempSync(path.join(os.tmpdir(),'sheet163-'));
const f=(...p)=>path.join(root,...p);let members=[];
const openssl=(...args)=>cp.execFileSync('openssl',args,{cwd:root,stdio:'pipe'});
function signKeys(name){const keys=crypto.generateKeyPairSync('ed25519'),priv=f(name+'.priv'),pub=f(name+'.pub');fs.writeFileSync(priv,keys.privateKey.export({format:'pem',type:'pkcs8'}));fs.writeFileSync(pub,keys.publicKey.export({format:'pem',type:'spki'}));return{...keys,priv,pub};}
function cert(name){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',name+'.key','-out',name+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(name+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',name+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',name+'.crt','-days','2','-sha256','-extfile',name+'.ext');return{key:f(name+'.key'),cert:f(name+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(name+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
function makeRows(from,to){const out=[];for(let i=from;i<to;i++)out.push({payload:'proof-data-'+i,txid:'tx:'+i});return out;}
function fill(store,end){for(let i=0;i<end;){const count=Math.min(8,256-(i%256),end-i);store.batch(makeRows(i,i+count));i+=count;}}
async function spawn(cfg,name){const file=f(name+'.json');P.atomic(file,cfg);let err='';const proc=cp.fork(path.join(__dirname,'node163.js'),[],{env:{...process.env,S163_CONFIG:file},stdio:['ignore','pipe','pipe','ipc']});proc.stderr.on('data',x=>err+=x);const port=await new Promise((resolve,reject)=>{let done=false;const timeout=setTimeout(()=>{if(!done){done=true;reject(Error('S163_SPAWN_TIMEOUT '+name+' '+err));}},15000);proc.once('message',m=>{if(!done){done=true;clearTimeout(timeout);resolve(m.port);}});proc.once('exit',code=>{if(!done){done=true;clearTimeout(timeout);reject(Error('S163_SPAWN_EXIT '+name+' '+code+' '+err));}});});const member={name,proc,port,cfg};members.push(member);return member;}
async function stop(x){if(!x||x.proc.exitCode!==null||x.proc.signalCode!==null)return;await new Promise(resolve=>{const timer=setTimeout(()=>{x.proc.kill('SIGKILL');resolve();},1200);x.proc.once('exit',()=>{clearTimeout(timer);resolve();});try{x.proc.send('stop',err=>{if(err){x.proc.kill('SIGKILL');clearTimeout(timer);resolve();}});}catch{x.proc.kill('SIGKILL');clearTimeout(timer);resolve();}});}
const id='S163-RESOURCE';
let data,ca,certs,signatures,anchorK,sourceRoot,sourceTarget;
function setup(){openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=OASIS-S163-CA');
 certs=Object.fromEntries(['client','red','green','blue'].map(n=>[n,cert(n)]));signatures=Object.fromEntries(['red','green','blue'].map(n=>[n,signKeys(n)]));anchorK=signKeys('external-floor');
 sourceRoot=f('source-red');const s=new BatchStore(sourceRoot,id);s.init();fill(s,528);sourceTarget=s.read();fs.cpSync(sourceRoot,f('source-green'),{recursive:true});
}
function options(name,dir){return{nodeId:name,resourceId:id,...certs[name],dir,signKey:signatures[name].priv,anchorPublicKey:anchorK.pub,peerPublicKeys:Object.fromEntries(Object.entries(signatures).map(([k,v])=>[k,v.pub])),clientPin:certs.client.certPin,session:f('sessions',name+'-'+path.basename(path.dirname(dir))+'-'+path.basename(dir)+'.json'),externalPin:f('pins',name+'-'+path.basename(path.dirname(dir))+'-'+path.basename(dir)+'.json'),quarantine:f('quarantine',name+'-'+path.basename(path.dirname(dir))+'-'+path.basename(dir)+'.txt')};}
function endpoint(ms){return Object.fromEntries(Object.entries(ms).map(([name,m])=>[name,{port:m.port,serverPin:certs[name].certPin}]));}
function makeClient(ms,win,delay=0,mode='adaptive'){const nodeConfig=endpoint(ms);return Pipeline.make({identity:certs.client,nodes:nodeConfig,keys:Object.fromEntries(Object.entries(signatures).map(([k,v])=>[k,v.publicKey])),anchor:V.signAnchor(V.anchorBody(id,sourceTarget,100),anchorK.privateKey),anchorKey:anchorK.publicKey,fetchWindow:win,batchMode:mode,delayFetch:(offset)=>delay?((Math.floor(offset/8)%3===0)?delay:0):0});}
async function scenario({name,window=1,latencyMs=0,prefix=128,crash=false,batchMode='adaptive'}){
 const dirs={red:sourceRoot,green:f('source-green'),blue:f(name,'blue')};const target=new BatchStore(dirs.blue,id);target.init();fill(target,prefix);
 const nodes={};for(const n of ['red','green','blue'])nodes[n]=await spawn(options(n,dirs[n]),name+'-'+n);
 let client=makeClient(nodes,window,latencyMs,batchMode);let out;
 try{
  if(crash){
   const count=target.read().count;const config=nodes.blue.cfg;config.crashAfterHeadOnce=f(name,'crash-after-head');await stop(nodes.blue);nodes.blue=await spawn(config,name+'-blue-armed');client.close();client=makeClient(nodes,window,latencyMs,batchMode);
   const n=crypto.randomBytes(20).toString('hex'),floor=V.signAnchor(V.anchorBody(id,sourceTarget,100),anchorK.privateKey),heads=await Promise.all(['red','green'].map(k=>client.rpc(k,'/head161',{nonce:n})));
   await client.rpc('blue','/begin161',{nonce:n,anchor:floor,heads,target:{resourceId:id,count:sourceTarget.count,root:sourceTarget.root,lastRecordHash:sourceTarget.lastRecordHash}});
   const page=await client.rpc('red','/page161',{nonce:n,target:{resourceId:id,count:sourceTarget.count,root:sourceTarget.root,lastRecordHash:sourceTarget.lastRecordHash},offset:count,limit:Pipeline.bound(count,sourceTarget.count,8)});
   await asyncTest('real worker SIGEXIT after durable adaptive batch but before ACK',async()=>{await assert.rejects(client.rpc('blue','/apply163',{page,batchHint:8}),/ECONNRESET|aborted|socket hang up|closed/i);assert.equal(target.read().count,count+8);});
   await stop(nodes.blue);nodes.blue=await spawn(config,name+'-blue-resume');client.close();client=makeClient(nodes,window,latencyMs,batchMode);
   await asyncTest('signed nonce and durable cursor survive restart',async()=>{const a=(await client.rpc('blue','/status161')).body;assert.equal(a.nonce,n);assert.equal(a.count,count+8);});
  }
  const t=performance.now();let commits=[];out=await client.sync('blue',{onCommit:(start,end)=>commits.push({start,end})});const ms=performance.now()-t;
  const h=target.read();await asyncTest(name+' converges to certified source root',async()=>{assert.equal(h.count,sourceTarget.count);assert.equal(h.root,sourceTarget.root);assert.equal(h.lastRecordHash,sourceTarget.lastRecordHash);});
  test(name+' commit positions strictly increase',()=>{for(let i=1;i<commits.length;i++)assert(commits[i-1].end<=commits[i].start);});
  test(name+' no historical hashes replayed',()=>assert.equal(target.metrics.recordHashesReplayed,0));
  test(name+' bounded concurrency and efficient persistent mTLS',()=>{assert(out.pipeline.maxInFlight<=window);assert(out.metrics.handshakes<=6);assert(out.metrics.handshakes<out.metrics.requests/3);});
  const info=(await client.rpc('blue','/status161')).body;
  const record={name,window,batchMode,latencyMs,prefix,recovered:sourceTarget.count-prefix,durationMs:+ms.toFixed(2),recordsPerSecond:+((sourceTarget.count-prefix)*1000/ms).toFixed(2),fetchMs:+out.pipeline.fetchMs.toFixed(2),commitMs:+out.pipeline.commitMs.toFixed(2),maxInFlight:out.pipeline.maxInFlight,fetchOutOfOrder:out.pipeline.fetched.some((n,i,a)=>i>0&&n<a[i-1]),networkRequests:out.metrics.requests,tlsConnections:out.metrics.handshakes,networkBytes:out.metrics.pageBytes,segmentCommits:info.batchMetrics.segmentCommits,headCommits:info.batchMetrics.headCommits,commitOrder:commits.map(c=>c.start),crash};
  console.log('BENCHMARK163',JSON.stringify(record));return record;
 }finally{client.close();await Promise.allSettled(Object.values(nodes).map(stop));}
}
async function main(){
 test('page bound at segment 255',()=>assert.equal(Pipeline.bound(255,270),1));
 test('page bound at segment 256',()=>assert.equal(Pipeline.bound(256,270),8));
 test('page bound at tail',()=>assert.equal(Pipeline.bound(263,267),4));
 test('reject zero page limit',()=>assert.throws(()=>Pipeline.bound(1,10,0),/S163_PAGE_BOUNDS/));
 test('reject speculative cursor beyond target',()=>assert.throws(()=>Pipeline.bound(11,10),/S163_PAGE_BOUNDS/));
 test('adaptive pressure 0 uses two-row batch',()=>assert.equal(Pipeline.chooseBatch(100,8,0),2));
 test('adaptive pressure 1 uses four-row batch',()=>assert.equal(Pipeline.chooseBatch(100,8,1),4));
 test('adaptive pressure 2 uses eight-row batch',()=>assert.equal(Pipeline.chooseBatch(100,8,2),8));
 test('adaptive batch cannot cross segment',()=>assert.equal(Pipeline.chooseBatch(253,8,2),3));
 test('reject invalid batch length',()=>assert.throws(()=>Pipeline.chooseBatch(0,9,2),/S163_BATCH_SHAPE/));
 test('reject excessive speculative window',()=>assert.throws(()=>Pipeline.make({fetchWindow:9}),/S163_WINDOW_BOUNDS/));
 test('reject unknown batch policy',()=>assert.throws(()=>Pipeline.make({fetchWindow:1,batchMode:'unsafe'}),/S163_BATCH_MODE/));
 setup();test('source Merkle root exactly duplicated',()=>{const green=new BatchStore(f('source-green'),id);assert.equal(green.read().root,sourceTarget.root);});
 let results=[];
 // Deterministic pseudo-random A/B order; seed and order are recorded.
 let rng=0x163d;const rand=()=>{rng^=rng<<13;rng^=rng>>>17;rng^=rng<<5;return rng>>>0;};
 for(let trial=0;trial<2;trial++){
  const order=(rand()&1)?[1,4]:[4,1];
  for(const w of order)results.push(await scenario({name:'trial'+(trial+1)+'-w'+w,window:w,batchMode:'fixed8',prefix:128,latencyMs:trial===0?0:14}));
 }
 const boundary=await scenario({name:'boundary-prefetch',window:4,batchMode:'adaptive',prefix:253,latencyMs:18});results.push(boundary);
 const half=await scenario({name:'batchsize-fixed4',window:4,batchMode:'fixed4',prefix:128,latencyMs:0});results.push(half);
 test('boundary workload includes multi-sized durable chunks',()=>{assert(boundary.segmentCommits>=1);assert.equal(boundary.recovered,275);});
 test('prefetch completes pages out of order under delay injection',()=>{const candidates=results.filter(r=>r.window===4&&r.latencyMs>0);assert(candidates.some(r=>r.fetchOutOfOrder));});
 await scenario({name:'crash-resume',window:4,prefix:256,crash:true});
 const summaries=[];for(let trial=1;trial<=2;trial++){const a=results.find(r=>r.name===`trial${trial}-w1`),b=results.find(r=>r.name===`trial${trial}-w4`);summaries.push({trial,latencyMs:a.latencyMs,serialRowsPerSecond:a.recordsPerSecond,parallelRowsPerSecond:b.recordsPerSecond,ratio:+(a.durationMs/b.durationMs).toFixed(3),order:results.filter(x=>x.name.startsWith('trial'+trial)).map(x=>x.window)});}
 const full=results.find(x=>x.name==='trial1-w4');const batchRatio=+(half.durationMs/full.durationMs).toFixed(3);const summary={batchComparison:{fixed8:full.durationMs,fixed4:half.durationMs,ratioFixed8OverFixed4:batchRatio},sheet:163,status:'PASS',newChecks:checks,sourceRecords:sourceTarget.count,conditions:summaries,allResults:results,benchmarkType:'deterministically randomized order, same source and target prefix, A/B one-host mTLS; one condition injects 14ms page-tail delay',warning:'TLS and source operations are on one physical host, benchmark is not generalizable; externally pinned floor is synthetic test signer',date:new Date().toISOString()};
 fs.writeFileSync(path.join(__dirname,'benchmark163.json'),JSON.stringify(summary,null,2)+'\n');
 console.log('SHEET163 GATE '+checks+'/'+checks+' PASS');
}
main().catch(e=>{console.error('SHEET163 FAIL',e.stack||e);process.exitCode=1;}).finally(async()=>{await Promise.allSettled(members.map(stop));if(process.env.S163_KEEP!=='1')fs.rmSync(root,{force:true,recursive:true});});
