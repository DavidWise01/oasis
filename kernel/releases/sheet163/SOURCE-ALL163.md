# SHEET 163 — Complete New Executable Source

Frozen SHEET 162 archive is preserved exactly in `baseline162/`; the following sections contain the SHEET 163 authored sources.

## pipeline163.js

```javascript
'use strict';
// SHEET 163: fetch ahead, apply in strict durable cursor order. No speculative writes.
const crypto=require('node:crypto');
const P=require('./baseline162/baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const V=require('./baseline162/baseline161/proof161');
const Transport=require('./baseline162/transport162');
const MAX=8, SEGMENT=256;
function bound(offset,total,max=MAX){
 if(!Number.isSafeInteger(offset)||!Number.isSafeInteger(total)||offset<0||total<=offset||!Number.isInteger(max)||max<1||max>MAX)throw Error('S163_PAGE_BOUNDS');
 return Math.min(max,total-offset,SEGMENT-(offset%SEGMENT));
}
function chooseBatch(offset,rows,pressure=2){
 // Client controls performance hint only; verifier and server enforce maximum 8.
 if(!Number.isSafeInteger(offset)||offset<0||!Number.isInteger(rows)||rows<1||rows>MAX)throw Error('S163_BATCH_SHAPE');
 return Math.min(rows,SEGMENT-(offset%SEGMENT),pressure>=2?8:pressure===1?4:2);
}
function make({identity,nodes,keys,anchor,anchorKey,fetchWindow=1,delayFetch=()=>0,batchMode='adaptive'}){
 if(!Number.isInteger(fetchWindow)||fetchWindow<1||fetchWindow>8)throw Error('S163_WINDOW_BOUNDS');
 if(!['adaptive','fixed8','fixed4'].includes(batchMode))throw Error('S163_BATCH_MODE');
 const transport=Transport.make(identity,nodes),rpc=transport.rpc;
 const observed={issued:[],fetched:[],committed:[],maxInFlight:0,retries:0,fetchMs:0,commitMs:0};
 function signed(id,domain,msg){if(msg?.body?.nodeId!==id||!P.verify(keys[id],domain,msg.body,msg.signature))throw Error('S163_BAD_PEER_SIGN');return msg.body;}
 async function sync(targetName,{limit=8,onCommit=()=>{},onFetch=()=>{}}={}){
  if(!Number.isInteger(limit)||limit<1||limit>MAX)throw Error('S163_LIMIT');
  const ids=Object.keys(nodes).filter(id=>id!==targetName);
  if(ids.length!==2)throw Error('S163_PEERS');
  let state=signed(targetName,'S161:STATUS',await rpc(targetName,'/status161'));
  const nonce=state.nonce||crypto.randomBytes(20).toString('hex');
  const votes=await Promise.all(ids.map(id=>rpc(id,'/head161',{nonce})));
  const first=votes[0].body,target={resourceId:first.resourceId,count:first.count,root:first.root,lastRecordHash:first.lastRecordHash};
  V.certified(target,votes,nonce,keys);
  const pin=V.checkAnchor(anchor,anchorKey);
  if(pin.resourceId!==target.resourceId||pin.count!==target.count||pin.root!==target.root||pin.lastRecordHash!==target.lastRecordHash)throw Error('S163_EXTERNAL_PIN_MISMATCH');
  if(state.active&&(state.nonce!==nonce||P.sha(state.target)!==P.sha(target)))throw Error('S163_SESSION_FORK');
  if(!state.active)state=signed(targetName,'S161:STATUS',await rpc(targetName,'/begin161',{anchor,heads:votes,nonce,target}));
  const inFlight=new Map();let next=state.count;const start=process.hrtime.bigint();
  function queue(){
   while(inFlight.size<fetchWindow&&next<target.count){
    const from=next,span=bound(from,target.count,limit),peer=ids[Math.floor(from/limit)%ids.length];next+=span;
    observed.issued.push(from);let promise=(async()=>{const t=process.hrtime.bigint();
      const response=await rpc(peer,'/page161',{nonce,target,offset:from,limit:span});
      const d=Number(delayFetch(from));if(!Number.isFinite(d)||d<0||d>1000)throw Error('S163_DELAY_BOUNDS');
      if(d)await new Promise(resolve=>setTimeout(resolve,d));
      observed.fetchMs+=Number(process.hrtime.bigint()-t)/1e6;
      observed.fetched.push(from);onFetch(from);return{response,span};
    })().then(value=>({value}),error=>({error}));inFlight.set(from,promise);
    observed.maxInFlight=Math.max(observed.maxInFlight,inFlight.size);
   }
  }
  try{
   while(state.count<target.count){
    // Durable state is the only cursor; schedule remote speculative reads, not writes.
    const cursor=state.count;queue();const pending=inFlight.get(cursor);
    if(!pending)throw Error('S163_MISSING_ORDERED_PAGE');const got=await pending;inFlight.delete(cursor);
    if(got.error)throw got.error;
    const pressure=inFlight.size+1,batchHint=batchMode==='fixed8'?chooseBatch(cursor,got.value.span,2):batchMode==='fixed4'?chooseBatch(cursor,got.value.span,1):chooseBatch(cursor,got.value.span,pressure);
    const t=process.hrtime.bigint();let after;
    try{after=signed(targetName,'S161:STATUS',await rpc(targetName,'/apply163',{page:got.value.response,batchHint}));}
    catch(error){
     // An ACK can disappear *after* fsync. Read authenticated target state; never replay blindly.
     observed.retries++;
     try{after=signed(targetName,'S161:STATUS',await rpc(targetName,'/status161'));}
     catch{throw error;}
     if(after.count<=cursor)throw error;
    }
    observed.commitMs+=Number(process.hrtime.bigint()-t)/1e6;
    if(after.count<=cursor||after.count>target.count||after.count>cursor+got.value.span)throw Error('S163_CURSOR_INCONSISTENT');
    state=after;observed.committed.push(cursor);onCommit(cursor,state.count);
    if(state.count!==cursor+got.value.span){
      // Interruption within an otherwise valid page: discard prefetched work and
      // request new certified pages starting at the *durable* intermediate cursor.
      inFlight.clear();next=state.count;
    }
   }
   if(state.root!==target.root||state.lastRecordHash!==target.lastRecordHash)throw Error('S163_FINAL_MISMATCH');
   const result=signed(targetName,'S161:FINISH',await rpc(targetName,'/finish161'));
   return{...result,elapsedMs:Number(process.hrtime.bigint()-start)/1e6,metrics:{...transport.metrics},pipeline:{...observed,window:fetchWindow,limit,batchMode}};
  }finally{ // Delayed read RPCs may resolve, but cannot mutate state.
    inFlight.clear();
  }
 }
 return{sync,rpc,transport,close:transport.close,observed};
}
module.exports={make,bound,chooseBatch};
```

## node163.js

```javascript
'use strict';
const fs=require('node:fs');
const {BatchStore}=require('./baseline162/batch162');
const P=require('./baseline162/baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');

const V=require('./baseline162/baseline161/proof161');
const cfg=P.load(process.env.S163_CONFIG),key=fs.readFileSync(cfg.signKey),anchorKey=fs.readFileSync(cfg.anchorPublicKey),peers=Object.fromEntries(Object.entries(cfg.peerPublicKeys).map(([k,v])=>[k,fs.readFileSync(v)]));
const store=new BatchStore(cfg.dir,cfg.resourceId);
const loadSession=()=>fs.existsSync(cfg.session)?P.load(cfg.session):null;
const locked=()=>fs.existsSync(cfg.quarantine)&&fs.readFileSync(cfg.quarantine,'utf8').length>0;
function seal(domain,body){return {body,signature:P.sign(key,domain,body)};}
function status(){const h=store.read(),session=loadSession();return seal('S161:STATUS',{nodeId:cfg.nodeId,resourceId:cfg.resourceId,count:h.count,root:h.root,lastRecordHash:h.lastRecordHash,active:!!session,nonce:session?.nonce||null,target:session?.target||null,recordHashesReplayed:store.metrics.recordHashesReplayed,subtreeLookups:store.metrics.subtreeLookups,rssMiB:+(process.memoryUsage().rss/1048576).toFixed(2),batchMetrics:store.batchMetrics});}
function head(b){if(!/^[a-f0-9]{40}$/.test(b.nonce||''))throw Error('S161_NONCE');const h=store.read();return seal('S161:HEAD',{nodeId:cfg.nodeId,nonce:b.nonce,resourceId:cfg.resourceId,count:h.count,root:h.root,lastRecordHash:h.lastRecordHash});}
function page(b){if(!/^[a-f0-9]{40}$/.test(b.nonce||'')||b.target?.resourceId!==cfg.resourceId||!Number.isSafeInteger(b.offset)||!Number.isInteger(b.limit)||b.limit<1||b.limit>8)throw Error('S161_PAGE_REQUEST');const h=store.read();if(b.target.count!==h.count||b.target.root!==h.root||b.target.lastRecordHash!==h.lastRecordHash||b.offset<0||b.offset>=h.count)throw Error('S161_STALE_SOURCE');const end=Math.min(h.count,b.offset+b.limit);const records=[];for(let i=b.offset;i<end;i++)records.push({record:store.record(i),inclusion:store.inclusion(i,h.count)});const s=store.stateAt(end,h);return seal('S161:PAGE',{schema:'oasis.sheet161.page.v1',nodeId:cfg.nodeId,nonce:b.nonce,target:b.target,from:b.offset,to:end,records,extension:store.extension(b.offset,end),after:s,lastRecordHash:records.at(-1).record.hash});}
function begin(b){if(loadSession())throw Error('S161_ACTIVE_SESSION');if(locked())throw Error('S161_QUARANTINE');const floor=V.checkAnchor(b.anchor,anchorKey),target=b.target;if(floor.resourceId!==cfg.resourceId||floor.count!==target?.count||floor.root!==target.root||floor.lastRecordHash!==target.lastRecordHash)throw Error('S161_FLOOR_TARGET');V.certified(target,b.heads,b.nonce,peers);const h=store.read();if(h.count>target.count)throw Error('S161_LOCAL_AHEAD');if(h.count===target.count&&h.root!==target.root)throw Error('S161_LOCAL_FORK');if(fs.existsSync(cfg.externalPin)){const prev=P.load(cfg.externalPin);V.checkAnchor(prev,anchorKey);if(floor.sequence<prev.body.sequence||floor.count<prev.body.count||(floor.sequence===prev.body.sequence&&P.sha(prev.body)!==P.sha(floor)))throw Error('S161_ROLLBACK_FLOOR');}
 // Independently retained pin is durable before session authorization.
 P.atomic(cfg.externalPin,b.anchor);
 const session={schema:'oasis.sheet161.session.v1',nonce:b.nonce,target,anchor:b.anchor,allowed:b.heads.map(x=>x.body.nodeId),heads:b.heads};P.atomic(cfg.session,session);return status();}
function apply(b){if(locked())throw Error('S162_QUARANTINE');const s=loadSession();if(!s)throw Error('S161_NO_SESSION');const h=store.read();V.checkAnchor(s.anchor,anchorKey);if(P.sha(P.load(cfg.externalPin))!==P.sha(s.anchor))throw Error('S161_PIN_CHANGED');V.certified(s.target,s.heads,s.nonce,peers);
 const rows=V.verifyPage(b.page,{nonce:s.nonce,target:s.target,keys:peers,allowed:s.allowed,local:{count:h.count,frontier:h.frontier,root:h.root},lastRecordHash:h.lastRecordHash});
 let cursor=0;while(cursor<rows.length){const current=store.read();const capacity=256-current.count%256;const hint=Number.isInteger(b.batchHint)&&b.batchHint>=1&&b.batchHint<=8?b.batchHint:8;const part=rows.slice(cursor,cursor+Math.min(capacity,hint));store.batch(part,{expectedIndex:current.count});
  cursor+=part.length;
  if(cfg.crashAfterHeadOnce&&!fs.existsSync(cfg.crashAfterHeadOnce)){fs.writeFileSync(cfg.crashAfterHeadOnce,'after durable batch before ACK\n');process.exit(81);}
 }
 return status();}

function finish(){const s=loadSession();if(!s)throw Error('S161_NO_SESSION');const h=store.read();if(h.count!==s.target.count||h.root!==s.target.root||h.lastRecordHash!==s.target.lastRecordHash)throw Error('S161_NOT_FINAL');fs.unlinkSync(cfg.session);return seal('S161:FINISH',{nodeId:cfg.nodeId,count:h.count,root:h.root});}
const server=P.serve(cfg.key,cfg.cert,cfg.ca,(req,b)=>{P.peer(req,cfg.clientPin);switch(req.url){case'/status161':return status();case'/head161':return head(b);case'/page161':return page(b);case'/begin161':return begin(b);case'/apply161':return apply(b);case'/apply162':return apply(b);case'/apply163':return apply(b);case'/finish161':return finish();default:throw Error('S161_UNKNOWN_ROUTE');}});
process.on('message',x=>{if(x==='stop')server.close(()=>process.exit(0));});
```

## gate163.js

```javascript
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
```

## make_docs163.py

```python
from pathlib import Path
import json, statistics, hashlib, platform
P=Path(__file__).resolve().parent
bench=json.loads((P/'benchmark163.json').read_text())
rows=bench['allResults']; cond=bench['conditions']; find=lambda name:next(x for x in rows if x['name']==name)
report='''# SHEET 163 — Parallel Merkle Prefetch / Adaptive Segment Batching

## Benchmark protocol

- One physical machine, real local mTLS client/resource processes; Ed25519 quorum heads and signed external anchor floor.
- Identical SHEET 162 indexed source journal (**528 records**); fresh target begins at **128 records** for A/B trials.
- Exactly **400 records recovered** in every matched A/B run; **fixed 8-record batches** on both sides, different fetch concurrency only (1 vs. 4).
- Deterministic pseudo-random trial order (seed `0x163d`), with trial 1 parallel-first, trial 2 serial-first.
- Trial 1 uses ordinary local requests; trial 2 injects 14 ms extra delay on every third page, modelling higher response latency (not a physical network delay).
- All transactions verify the same source root, all commit cursors increase, and the proof-verifier's historical-hash replay count remains zero.

## Matched A/B results

| Trial | Extra response delay | Serial window=1 | Parallel window=4 | Observed ratio | Order |
|---|---|---:|---:|---:|---|
'''
for x in cond:
 report+=f"| {x['trial']} | {x['latencyMs']} ms (every third page) | {x['serialRowsPerSecond']:.2f} records/s | **{x['parallelRowsPerSecond']:.2f} records/s** | **{x['ratio']:.3f}×** | {' → '.join('parallel' if w==4 else 'serial' for w in x['order'])} |\n"
report+='''
**Interpretation:** This is an observed local A/B comparison (two conditions, one paired repetition each), not a population-level speedup guarantee. The fixed eight-record batches and persistent pinned TLS configuration are held equal within each pair, isolating speculative proof fetching as the primary changed variable. Workloads ran sequentially and may be affected by cache, disk, CPU, and event-loop variability.

## Batch-size and segment-boundary observations

| Scenario | Records | Commit size | Duration | Rate | Segment/head commits |
|---|---:|---|---:|---:|---:|
'''
for n,label in [('trial1-w4','Fixed 8; four fetches'),('batchsize-fixed4','Fixed 4; four fetches'),('boundary-prefetch','Adaptive 3 at boundary, then 8')]:
 r=find(n);report+=f"| {label} | {r['recovered']} | {r['batchMode']} | {r['durationMs']:.2f} ms | {r['recordsPerSecond']:.2f}/s | {r['segmentCommits']} / {r['headCommits']} |\n"
report+='''
The four-record run was **faster than the eight-record run** despite twice the number of commits. That result is retained as observed; this benchmark does **not** establish monotonic performance with batch size. The test beginning at record 253 exercises a 3-record boundary fragment before entering segment 256, with subsequent commits safely bounded to individual segments.

## Concurrency and proof correctness

- Source pages are fetched speculatively over pinned, persistent mTLS connections (bounded window 1–8).
- Page signatures, inclusion proofs, Merkle extensions, and the external anchor are checked before the target writes.
- Only the exact next cursor is sent for durable application; fetched responses may arrive out of order but commits cannot.
- A signed duplicate/replay is not blindly retried after an acknowledgement failure: the client re-reads the target's authenticated, durable cursor.
- A real process exited after fsync but before ACK, then restarted and completed without duplicate records.
- Existing SHEET 162 tests passed independently: **19/19 storage** and **24/24 network/crash**. New SHEET 163 gate: **45/45**. The full frozen SHEET 103–162 lineage was *not* freshly rerun.

## Limitations

- All test processes share one physical host and the same test CA; not independent-host network consensus.
- Connection metrics count **opened TLS sockets**, not packet-level or hardware-verified handshakes.
- Segment write and head persistence remain two distinct fsync transactions; interrupted writes may require quorum-reviewed reconciliation.
- A/B trials have only one sample per condition; variance and warm-cache effects can dominate.
- A further protocol change would be needed for true multi-host durability, remote storage barriers, and durable cross-host admission control.
'''
(P/'BENCHMARK-REPORT.md').write_text(report)
arch='''# SHEET 163 — Complete ASCII Execution and Fault Process

```text
                              OASIS / ROOT0
                                    |
                  FROZEN SHEET 162 STORAGE / WITNESSES
                                    |
                         SYNCHRONIZATION REQUEST
                                    |
                   +----------------+----------------+
                   |                                 |
             RESOURCE BLUE                    SOURCE RED + GREEN
                   |                                 |
       mTLS CLIENT CERT + SERVER PIN          SIGNED HEAD FETCH
                   |                                 |
             LOCAL DURABLE HEAD <---- 2/3 CERTIFIED RESOURCE HEAD
                   |                                 |
          VERIFY EXISTING SESSION             ANCHOR FLOOR CHECK
                   |                                 |
          PIN EXTERNAL CHECKPOINT              EPOCH / ROOT / COUNT
                   |                                 |
          PERSIST NONCE + TARGET <----------- SAME VERIFIED TARGET
                   |
             BOUNDED FETCH WINDOW
                   |
          +--------+--------+--------+--------+
          |        |        |        |        |
        PAGE n   PAGE n+1 PAGE n+2 PAGE n+3  ...
          |        |        |        |
        FETCH    FETCH    FETCH    FETCH  (parallel network reads only)
          |        |        |        |
          +--------+--------+--------+
                   |
           OUT-OF-ORDER ARRIVAL
                   |
            ORDERED PAGE BUFFER
                   |
             REQUIRE CURSOR n
                   |
              VERIFY SIGNER
                   |
          VERIFY INCLUSION + EXTENSION
                   |
          VERIFY LOCAL PEAK FRONTIER
                   |
         CHOOSE ADAPTIVE BATCH 1..8
                   |
         LIMIT TO 256-SEGMENT BOUNDARY
                   |
          +--------+--------+
          |                 |
        NORMAL            INVALID
          |                 |
   EXCLUSIVE WRITER LOCK   REJECT / NO WRITE
          |
      WRITE SEGMENT
          |
      FSYNC SEGMENT
          |
     PERSIST MERKLE INDEX
          |
        WRITE HEAD
          |
       FSYNC HEAD
          |
     SIGN DURABLE STATUS
          |
          +----------+-----------------+
          |                            |
        ACK                         CRASH / LOST ACK
          |                            |
   ADVANCE CURSOR               RESTART TARGET
          |                            |
      PREFETCH NEXT         READ SIGNED DURABLE CURSOR
          |                            |
          |                       COUNT ADVANCED?
          |                            |
          |                  +---------+----------+
          |                  |                    |
          |                 YES                   NO
          |                  |                    |
          |         DISCARD STALE PREFETCH    FAIL CLOSED
          |                  |
          +------------------+
                   |
            REFETCH FROM CURSOR
                   |
           VERIFY FINAL ROOT
                   |
             SIGNED FINISH
                   |
             NEXT VERIFIED
```

ADVERSARIAL MATRIX
  A1  remote pages reordered                 -> ordered commits only
  A2  malicious/invalid signed pages         -> fail closed in base verifier
  A3  segment boundary at cursor 253         -> 3-row fragment then full batches
  A4  crash after 8-row fsync, before ACK    -> restart and no duplicate
  A5  stale but signed external floor        -> SHEET 161 pin rollback rejection
  A6  concurrent speculative reads           -> no speculative durable writes
  A7  server identity substitution           -> mTLS fingerprint pin rejects
  A8  conflicting recovery session           -> reject mismatched nonce/target
  A9  segment persisted, head not committed  -> existing SHEET 162 quarantine

STORAGE COSTS
  BATCH_8   segment fsync + head fsync, once each per 8 records
  BATCH_4   segment fsync + head fsync, once each per 4 records
  BOUNDARY  truncate at segment capacity, never mix two physical segments

METRIC TERMS
  RPS = successfully recovered records / elapsed synchronization seconds
  MAX_IN_FLIGHT = number of concurrent page fetch promises
  NETWORK_BYTES = signed HTTP response bytes on mTLS connection
  SOCKETS = new socket objects, *not* independently measured handshakes
  DURABLE_COMMITS = count of completed segment and head fsync operations
```
'''
(P/'KERNEL-ASCII.md').write_text(arch)
(P/'KERNEL-ASCII.txt').write_text(arch)
readme=f'''# SHEET 163 — Parallel Merkle Fetch / Ordered Durable Commit

**Release status:** dedicated new gate **45/45 PASS**; inherited SHEET 162 storage **19/19** and SHEET 162 network **24/24** PASS on separate runs. The **complete historical lineage was not rerun**.

This additive extension preserves the entire SHEET 162 source tree in `baseline162/`. The principal new modules are:

- `pipeline163.js` — bounded parallel signed-proof fetch, strict ordered commit cursor, recovery after lost ACK, mTLS socket reuse.
- `node163.js` — backward-compatible protected resource with `/apply163`, receiver-side signature/proof verification, segment-boundary and batch-hint enforcement.
- `gate163.js` — reproducible one-host mTLS correctness, crash and randomized-order benchmark harness.
- `benchmark163.json` and `BENCHMARK-REPORT.md` — measured trial detail with benchmark limitations.
- `KERNEL-ASCII.txt` — complete execution, proof, persistence and recovery pipe.
- `index.html` — interactive SVG fault and benchmark dashboard.

## Baseline A/B

Source: **528 journal records**, target begins at **128**; each run recovers **400 records** with eight-record durable writes on both sides.

| Condition | Serial window 1 | Parallel window 4 | Speedup |
|---|---:|---:|---:|
'''
for x in cond:readme+=f"| Trial {x['trial']}, delay {x['latencyMs']} ms | {x['serialRowsPerSecond']:.2f}/s | {x['parallelRowsPerSecond']:.2f}/s | {x['ratio']:.3f}× |\n"
readme+='''
The A/B order is pseudo-randomized with a fixed seed, and one condition simulates 14 ms of delayed page completion. Treat these as local observations, not speed guarantees. The four-record batch comparison also ran faster than fixed-eight in one run, demonstrating that fewer fsync calls need not guarantee better throughput.

## Execute

```bash
node gate163.js
bash run-new.sh
```

No external JavaScript dependencies; Node.js 22, OpenSSL, POSIX filesystem semantics, and loopback networking were used. Running the full historical lineage can be costly and is not represented as completed here. Testing cannot prove independent-host consensus or physically separate rollback-fence enforcement.
'''
(P/'README.md').write_text(readme)
print('docs created',[(n,(P/n).stat().st_size) for n in ['README.md','BENCHMARK-REPORT.md','KERNEL-ASCII.txt']])
```

## make-release163.py

```python
from pathlib import Path
import json,hashlib,zipfile,datetime,os,stat,sys
ROOT=Path(__file__).resolve().parent
PARENT=ROOT/'baseline162'
ARCHIVE=ROOT.parent/'SHEET163-parallel-merkle-ordered-commit.zip'
SHA=ARCHIVE.with_name(ARCHIVE.name+'.sha256.txt')
def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for part in iter(lambda:f.read(1<<20),b''):h.update(part)
 return h.hexdigest()
def relhashes(folder):return {p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file()}
prior_zip=ROOT.parent/'SHEET162-batched-mtls-recovery.zip'
with zipfile.ZipFile(prior_zip) as published:
 before={name[len('sheet162/'):]:hashlib.sha256(published.read(name)).hexdigest() for name in published.namelist() if name.startswith('sheet162/') and not name.endswith('/')}
after=relhashes(PARENT)
assert before==after,(len(before),len(after),next(iter((before.items() ^ after.items())),None))
bench=json.loads((ROOT/'benchmark163.json').read_text())
assert bench['newChecks']==45
newlog=(ROOT/'full-new-gate.log').read_text();assert 'SHEET163 GATE 45/45 PASS' in newlog
assert 'SHEET162 UNIT 19/19 PASS' in (ROOT/'inherited162-unit.log').read_text()
assert 'SHEET162 GATE 24/24 PASS' in (ROOT/'inherited162-network.log').read_text()
assert 'SHEET163 CHROMIUM 11/11 PASS' in (ROOT/'browser-test.log').read_text()
manifest={}
for f in sorted(ROOT.rglob('*')):
 if f.is_file() and f.name not in {'SHA256SUMS','release-receipt.json','release-build.log'}:manifest[f.relative_to(ROOT).as_posix()]=digest(f)
(ROOT/'SHA256SUMS').write_text(''.join(f'{sha}  {name}\n' for name,sha in manifest.items()))
receipt={'schema':'oasis.sheet163.release.v1','sheet':163,'parent':162,'status':'0e / new PASS','tests':{'new':45,'newExit':0,'sheet162Unit':19,'sheet162Network':24,'chromiumInteractions':11,'fullHistoricalRun':'NOT RUN'},'benchmarks':bench['conditions'],'batchComparison':bench['batchComparison'],'preservedParentFiles':len(before),'preservedParentSha256Verified':True,'archive':ARCHIVE.name,'verificationLimit':'One physical host, TLS socket counters are not verified handshakes, repeat-limited randomized A/B, no global consensus', 'releaseUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(ROOT/'release-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
files=sorted((x for x in ROOT.rglob('*') if x.is_file()),key=lambda p:p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for file in files:
  rel='sheet163/'+file.relative_to(ROOT).as_posix()
  z.write(file,rel)
with zipfile.ZipFile(ARCHIVE) as z:
 assert z.testzip() is None
 names=set(z.namelist())
 assert len(names)==len(files)
 for rel,originalHash in before.items():
  name='sheet163/baseline162/'+rel
  assert name in names,name
  assert hashlib.sha256(z.read(name)).hexdigest()==originalHash,rel
 for needed in ['sheet163/pipeline163.js','sheet163/node163.js','sheet163/gate163.js','sheet163/KERNEL-ASCII.txt','sheet163/BENCHMARK-REPORT.md','sheet163/SHA256SUMS','sheet163/release-receipt.json','sheet163/index.html']:
  assert needed in names,needed
value=digest(ARCHIVE);SHA.write_text(f'{value}  {ARCHIVE.name}\n')
print(json.dumps({'archive':str(ARCHIVE),'bytes':ARCHIVE.stat().st_size,'sha256':value,'files':len(files),'inheritedFiles':len(before),'newChecks':45,'inheritedTests':43,'chromiumChecks':11},indent=2))
```

## run-new.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
node gate163.js
```

## browser-check.py

```python
from pathlib import Path
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page(accept_downloads=True,viewport={'width':1280,'height':920})
 page.set_content((P/'index.html').read_text(),wait_until='domcontentloaded')
 count=0
 for i in range(8):
  page.locator('.scenario').nth(i).click()
  assert page.locator('.scenario').nth(i).get_attribute('aria-pressed')=='true'
  assert page.locator('#detailTitle').inner_text().strip()
  print(f'PASS {count+1} scenario {i+1}');count+=1
 page.select_option('#trial','1');assert '329.52' in page.locator('#kpiFast').inner_text();print(f'PASS {count+1} benchmark toggle');count+=1
 with page.expect_download() as download:
  page.locator('#export').click()
 d=download.value
 assert d.suggested_filename=='sheet163-dashboard-evidence.json'
 assert 'prepared' in page.locator('#exportStatus').inner_text()
 print(f'PASS {count+1} JSON export');count+=1
 page.locator('#reset').click();assert page.locator('.scenario').first.get_attribute('aria-pressed')=='true';assert '298.71' in page.locator('#kpiFast').inner_text();print(f'PASS {count+1} reset');count+=1
 page.screenshot(path=str(P/'preview.png'),full_page=True)
 print(f'SHEET163 CHROMIUM {count}/{count} PASS')
 browser.close()
```

## KERNEL-ASCII.txt

```text
# SHEET 163 — Complete ASCII Execution and Fault Process

```text
                              OASIS / ROOT0
                                    |
                  FROZEN SHEET 162 STORAGE / WITNESSES
                                    |
                         SYNCHRONIZATION REQUEST
                                    |
                   +----------------+----------------+
                   |                                 |
             RESOURCE BLUE                    SOURCE RED + GREEN
                   |                                 |
       mTLS CLIENT CERT + SERVER PIN          SIGNED HEAD FETCH
                   |                                 |
             LOCAL DURABLE HEAD <---- 2/3 CERTIFIED RESOURCE HEAD
                   |                                 |
          VERIFY EXISTING SESSION             ANCHOR FLOOR CHECK
                   |                                 |
          PIN EXTERNAL CHECKPOINT              EPOCH / ROOT / COUNT
                   |                                 |
          PERSIST NONCE + TARGET <----------- SAME VERIFIED TARGET
                   |
             BOUNDED FETCH WINDOW
                   |
          +--------+--------+--------+--------+
          |        |        |        |        |
        PAGE n   PAGE n+1 PAGE n+2 PAGE n+3  ...
          |        |        |        |
        FETCH    FETCH    FETCH    FETCH  (parallel network reads only)
          |        |        |        |
          +--------+--------+--------+
                   |
           OUT-OF-ORDER ARRIVAL
                   |
            ORDERED PAGE BUFFER
                   |
             REQUIRE CURSOR n
                   |
              VERIFY SIGNER
                   |
          VERIFY INCLUSION + EXTENSION
                   |
          VERIFY LOCAL PEAK FRONTIER
                   |
         CHOOSE ADAPTIVE BATCH 1..8
                   |
         LIMIT TO 256-SEGMENT BOUNDARY
                   |
          +--------+--------+
          |                 |
        NORMAL            INVALID
          |                 |
   EXCLUSIVE WRITER LOCK   REJECT / NO WRITE
          |
      WRITE SEGMENT
          |
      FSYNC SEGMENT
          |
     PERSIST MERKLE INDEX
          |
        WRITE HEAD
          |
       FSYNC HEAD
          |
     SIGN DURABLE STATUS
          |
          +----------+-----------------+
          |                            |
        ACK                         CRASH / LOST ACK
          |                            |
   ADVANCE CURSOR               RESTART TARGET
          |                            |
      PREFETCH NEXT         READ SIGNED DURABLE CURSOR
          |                            |
          |                       COUNT ADVANCED?
          |                            |
          |                  +---------+----------+
          |                  |                    |
          |                 YES                   NO
          |                  |                    |
          |         DISCARD STALE PREFETCH    FAIL CLOSED
          |                  |
          +------------------+
                   |
            REFETCH FROM CURSOR
                   |
           VERIFY FINAL ROOT
                   |
             SIGNED FINISH
                   |
             NEXT VERIFIED
```

ADVERSARIAL MATRIX
  A1  remote pages reordered                 -> ordered commits only
  A2  malicious/invalid signed pages         -> fail closed in base verifier
  A3  segment boundary at cursor 253         -> 3-row fragment then full batches
  A4  crash after 8-row fsync, before ACK    -> restart and no duplicate
  A5  stale but signed external floor        -> SHEET 161 pin rollback rejection
  A6  concurrent speculative reads           -> no speculative durable writes
  A7  server identity substitution           -> mTLS fingerprint pin rejects
  A8  conflicting recovery session           -> reject mismatched nonce/target
  A9  segment persisted, head not committed  -> existing SHEET 162 quarantine

STORAGE COSTS
  BATCH_8   segment fsync + head fsync, once each per 8 records
  BATCH_4   segment fsync + head fsync, once each per 4 records
  BOUNDARY  truncate at segment capacity, never mix two physical segments

METRIC TERMS
  RPS = successfully recovered records / elapsed synchronization seconds
  MAX_IN_FLIGHT = number of concurrent page fetch promises
  NETWORK_BYTES = signed HTTP response bytes on mTLS connection
  SOCKETS = new socket objects, *not* independently measured handshakes
  DURABLE_COMMITS = count of completed segment and head fsync operations
```
```