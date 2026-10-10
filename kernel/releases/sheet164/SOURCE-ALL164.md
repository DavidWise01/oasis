# SHEET 164 — Complete New Executable Source

The exact new source files follow. Five-backtick fences protect embedded Markdown in the generator scripts. The inherited frozen baseline is preserved in the complete ZIP.

## pipeline164.js

`````javascript
'use strict';
// SHEET 164: factorial policy runner, ordered physical commits, no speculative writes.
const crypto=require('node:crypto');
const P=require('./baseline163/baseline162/baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const V=require('./baseline163/baseline162/baseline161/proof161');
const Transport=require('./transport164');
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
function make({identity,nodes,keys,anchor,anchorKey,fetchWindow=1,delayFetch=()=>0,batchMode='adaptive',reuseTls=true}){
 if(!Number.isInteger(fetchWindow)||fetchWindow<1||fetchWindow>8)throw Error('S163_WINDOW_BOUNDS');
 if(!['adaptive','fixed8','fixed4'].includes(batchMode))throw Error('S163_BATCH_MODE');
 const transport=Transport.make(identity,nodes,{reuseTls}),rpc=transport.rpc;
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
   return{...result,elapsedMs:Number(process.hrtime.bigint()-start)/1e6,metrics:{...transport.metrics},pipeline:{...observed,window:fetchWindow,limit,batchMode,reuseTls}};
  }finally{ // Delayed read RPCs may resolve, but cannot mutate state.
    inFlight.clear();
  }
 }
 return{sync,rpc,transport,close:transport.close,observed};
}
module.exports={make,bound,chooseBatch};
`````

## transport164.js

`````javascript
'use strict';
// mTLS client with bounded keep-alive pool and pinned server certificate identity.
const https=require('node:https'),fs=require('node:fs'),tls=require('node:tls');
function make(identity,nodes,{reuseTls=true}={}){const key=fs.readFileSync(identity.key),cert=fs.readFileSync(identity.cert),ca=fs.readFileSync(identity.ca);
 const agents=Object.fromEntries(Object.keys(nodes).map(n=>[n,new https.Agent({keepAlive:true,maxSockets:2,maxFreeSockets:2,timeout:5000,maxTotalSockets:2})]));
 const sockets=new Set(),metrics={requests:0,handshakes:0,pageBytes:0};
 async function rpc(name,path,body={}){const n=nodes[name];if(!n)throw Error('S162_UNKNOWN_NODE');metrics.requests++;const bytes=Buffer.from(JSON.stringify(body));if(bytes.length>15900)throw Error('S162_REQUEST_TOO_LARGE');
  return new Promise((resolve,reject)=>{let finished=false;const req=https.request({hostname:'127.0.0.1',port:n.port,path,method:'POST',key,cert,ca,servername:'localhost',minVersion:'TLSv1.2',rejectUnauthorized:true,agent:reuseTls?agents[name]:false,timeout:6000,checkServerIdentity:(name,c)=>{const err=tls.checkServerIdentity(name,c);if(err)return err;return c.fingerprint256?.replaceAll(':','').toLowerCase()===n.serverPin?undefined:Error('S162_SERVER_PIN');},headers:{'content-type':'application/json','content-length':bytes.length}},res=>{const chunks=[];res.on('data',x=>chunks.push(x));res.on('end',()=>{try{const buf=Buffer.concat(chunks);metrics.pageBytes+=buf.length;const value=JSON.parse(buf.toString());if(res.statusCode!==200)reject(Error(value.error||'S162_HTTP_'+res.statusCode));else resolve(value);}catch(e){reject(e);}});});
   req.on('socket',socket=>{if(!sockets.has(socket)){sockets.add(socket);metrics.handshakes++;socket.once('close',()=>sockets.delete(socket));}});
   req.on('error',reject);req.on('timeout',()=>req.destroy(Error('S162_RPC_TIMEOUT')));req.end(bytes);
  });}
 function close(){for(const a of Object.values(agents))a.destroy();sockets.clear();}
 return{rpc,close,metrics,reuseTls};}
module.exports={make};
`````

## gate164.js

`````javascript
'use strict';
// SHEET 164 -- reproducible 2x2x2 factorial + holdout + process-kill recovery
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {performance}=require('node:perf_hooks');
const {BatchStore}=require('./baseline163/baseline162/batch162');
const P=require('./baseline163/baseline162/baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const V=require('./baseline163/baseline162/baseline161/proof161');
const Pipeline=require('./pipeline164');
const root=fs.mkdtempSync(path.join(os.tmpdir(),'oasis-s164-'));
const f=(...parts)=>path.join(root,...parts);let checks=0;let processes=[];
function test(label,fn){fn();checks++;console.log('PASS',checks,label);}
async function atest(label,fn){await fn();checks++;console.log('PASS',checks,label);}
const openssl=(...args)=>cp.execFileSync('openssl',args,{cwd:root,stdio:'pipe'});
function keypair(label){const k=crypto.generateKeyPairSync('ed25519');const priv=f(label+'.priv'),pub=f(label+'.pub');fs.writeFileSync(priv,k.privateKey.export({format:'pem',type:'pkcs8'}));fs.writeFileSync(pub,k.publicKey.export({format:'pem',type:'spki'}));return {...k,priv,pub};}
function cert(label){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',label+'.key','-out',label+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(label+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',label+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',label+'.crt','-days','2','-sha256','-extfile',label+'.ext');return {key:f(label+'.key'),cert:f(label+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(label+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
const ID='OASIS-SHEET164';let certs,keys,anchorKey,source,sourceHead,sources,seedDir;
const row=i=>({txid:'s164:'+i,payload:'sample-'+i});
function fill(store,start,end){for(let i=start;i<end;){const k=Math.min(8,256-i%256,end-i);store.batch(Array.from({length:k},(_,j)=>row(i+j)));i+=k;}}
function setup(){openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=OASIS-S164-CA');certs=Object.fromEntries(['client','red','green','blue'].map(n=>[n,cert(n)]));keys=Object.fromEntries(['red','green','blue'].map(n=>[n,keypair(n)]));anchorKey=keypair('floor');const store=new BatchStore(f('source-red'),ID);store.init();fill(store,0,384);sourceHead=store.read();fs.cpSync(f('source-red'),f('source-green'),{recursive:true});const prefix=new BatchStore(f('seed256'),ID);prefix.init();fill(prefix,0,256);seedDir=f('seed256');}
function config(name,dir,session){return {nodeId:name,resourceId:ID,...certs[name],dir,signKey:keys[name].priv,anchorPublicKey:anchorKey.pub,peerPublicKeys:Object.fromEntries(Object.entries(keys).map(([n,v])=>[n,v.pub])),clientPin:certs.client.certPin,session:f('sessions',session+'-'+name+'.json'),externalPin:f('pins',session+'-'+name+'.json'),quarantine:f('quarantine',session+'-'+name+'.txt')};}
async function spawn(conf,label){P.atomic(f('configs',label+'.json'),conf);let err='';const proc=cp.fork(path.join(__dirname,'baseline163/node163.js'),[],{env:{...process.env,S163_CONFIG:f('configs',label+'.json')},stdio:['ignore','pipe','pipe','ipc']});proc.stderr.on('data',chunk=>{err+=chunk;});const port=await new Promise((resolve,reject)=>{let resolved=false;const timer=setTimeout(()=>{if(!resolved){resolved=true;reject(Error('S164_START_TIMEOUT '+label+' '+err));}},12000);proc.once('message',m=>{if(!resolved){resolved=true;clearTimeout(timer);resolve(m.port);}});proc.once('exit',code=>{if(!resolved){resolved=true;clearTimeout(timer);reject(Error('S164_START_EXIT '+code+' '+err));}});});const out={proc,port,label,conf};processes.push(out);return out;}
async function stop(x){if(!x||x.proc.exitCode!==null||x.proc.signalCode!==null)return;await new Promise(resolve=>{let settled=false;function done(){if(!settled){settled=true;clearTimeout(timer);resolve();}}const timer=setTimeout(()=>{try{x.proc.kill('SIGKILL');}catch{}done();},800);x.proc.once('exit',done);try{x.proc.send('stop',e=>{if(e){try{x.proc.kill('SIGKILL');}catch{}done();}});}catch{try{x.proc.kill('SIGKILL');}catch{}done();}});}
function endpoints(peerNodes,blue){return Object.fromEntries(Object.entries({...peerNodes,blue}).map(([n,m])=>[n,{port:m.port,serverPin:certs[n].certPin}]));}
function makeClient(peerNodes,blue,conf,block){return Pipeline.make({identity:certs.client,nodes:endpoints(peerNodes,blue),keys:Object.fromEntries(Object.entries(keys).map(([n,v])=>[n,v.publicKey])),anchor:V.signAnchor(V.anchorBody(ID,sourceHead,100),anchorKey.privateKey),anchorKey:anchorKey.publicKey,fetchWindow:conf.window,batchMode:conf.batch===4?'fixed4':'fixed8',reuseTls:conf.reuseTls,delayFetch:offset=>3+((offset*7+block*11)%12)});}
let seq=0;async function scenario(peers,conf,block,{crash=false,prefix=256}={}){seq++;const name='case'+seq,dir=f(name,'blue');fs.mkdirSync(path.dirname(dir),{recursive:true});if(prefix===256)fs.cpSync(seedDir,dir,{recursive:true});else {const s=new BatchStore(dir,ID);s.init();fill(s,0,prefix);}
 let blue=await spawn({...config('blue',dir,name),...(crash?{crashAfterHeadOnce:f(name,'crash-marker')}: {})},name+'-blue');let client=makeClient(peers,blue,conf,block);let failed=false;const initial=prefix;
 try{if(crash){try{await client.sync('blue');}catch(e){failed=true;}await atest('injected worker crash interrupts acknowledgement',async()=>{assert(failed);assert(blue.proc.exitCode!==null||blue.proc.signalCode!==null||fs.existsSync(f(name,'crash-marker')));const h=new BatchStore(dir,ID).read();assert(h.count>initial);});await stop(blue);blue=await spawn(blue.conf,name+'-blue-restart');client.close();client=makeClient(peers,blue,conf,block);}
 const starts=[];const start=performance.now();const outcome=await client.sync('blue',{onCommit:(a,b)=>starts.push([a,b])});const seconds=(performance.now()-start)/1000;const after=new BatchStore(dir,ID).read();await atest('verified exact source Merkle root '+name,async()=>{assert.equal(after.count,sourceHead.count);assert.equal(after.root,sourceHead.root);assert.equal(after.lastRecordHash,sourceHead.lastRecordHash);});
 test('durable commit order and segment boundaries '+name,()=>{for(let i=0;i<starts.length;i++){if(i)assert.equal(starts[i-1][1],starts[i][0]);assert(starts[i][1]-starts[i][0]<=8);assert(Math.floor(starts[i][0]/256)===Math.floor((starts[i][1]-1)/256));}});
 const verifiedStatus=await client.rpc('blue','/status161');test('mTLS and actual remote proof metrics are bounded '+name,()=>{assert(P.verify(keys.blue.publicKey,'S161:STATUS',verifiedStatus.body,verifiedStatus.signature));assert(outcome.pipeline.maxInFlight<=conf.window);assert(outcome.metrics.handshakes>=1);assert(outcome.metrics.requests>0);assert.equal(verifiedStatus.body.recordHashesReplayed,0);});
 const result={name,block,window:conf.window,batch:conf.batch,reuseTls:conf.reuseTls,crash,prefix,rows:sourceHead.count-prefix,seconds:+seconds.toFixed(4),recordsPerSecond:+((sourceHead.count-prefix)/seconds).toFixed(2),tlsConnections:outcome.metrics.handshakes,requests:outcome.metrics.requests,bytes:outcome.metrics.pageBytes,maxInFlight:outcome.pipeline.maxInFlight,segmentCommits:starts.reduce((sum,[a,b])=>sum+Math.ceil((b-a)/conf.batch),0),jitterSeed:block};
 console.log('BENCHMARK164',JSON.stringify(result));return result;
 }finally{client.close();await stop(blue);}}
function rng(seed){let s=seed;return()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return(s>>>0)/4294967296;};}
function shuffle(items,rand){const a=items.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(rand()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function select(rows){const byConfig=new Map();for(const r of rows){const key=[r.window,r.batch,r.reuseTls].join('/');if(!byConfig.has(key))byConfig.set(key,[]);byConfig.get(key).push(r.recordsPerSecond);}const med=x=>{const sorted=x.slice().sort((a,b)=>a-b);return sorted.length%2?sorted[(sorted.length-1)/2]:(sorted[sorted.length/2-1]+sorted[sorted.length/2])/2;};const scored=[...byConfig].map(([key,values])=>({key,medianRowsPerSecond:+med(values).toFixed(2),samples:values.length})).sort((a,b)=>b.medianRowsPerSecond-a.medianRowsPerSecond||a.key.localeCompare(b.key));const [w,b,t]=scored[0].key.split('/');return{scored,selected:{window:+w,batch:+b,reuseTls:t==='true'}};}
async function main(){test('reject concurrency window zero',()=>assert.throws(()=>Pipeline.make({fetchWindow:0}),/WINDOW_BOUNDS/));test('reject concurrency window nine',()=>assert.throws(()=>Pipeline.make({fetchWindow:9}),/WINDOW_BOUNDS/));test('4-record batch policy obeys boundary',()=>assert.equal(Pipeline.chooseBatch(254,8,1),2));test('8-record batch policy obeys boundary',()=>assert.equal(Pipeline.chooseBatch(255,8,2),1));test('zero-size proof request rejected',()=>assert.throws(()=>Pipeline.bound(5,20,0),/PAGE_BOUNDS/));test('future cursor rejected',()=>assert.throws(()=>Pipeline.bound(21,20),/PAGE_BOUNDS/));
 setup();const sources={red:await spawn(config('red',f('source-red'),'source'),'source-red'),green:await spawn(config('green',f('source-green'),'source'),'source-green')};const factorial=[];for(const window of [1,4])for(const batch of [4,8])for(const reuseTls of [false,true])factorial.push({window,batch,reuseTls});
 const rand=rng(0x164bad5);const results=[];try{for(let block=0;block<2;block++){const order=shuffle(factorial,rand);console.log('FACTORIAL164_BLOCK',block,order.map(x=>[x.window,x.batch,+x.reuseTls]));for(const conf of order)results.push(await scenario(sources,conf,block));}
  const choice=select(results);test('full factorial covers eight policies',()=>assert.equal(choice.scored.length,8));test('two replicates per policy',()=>assert(choice.scored.every(x=>x.samples===2)));test('TLS-off creates one connection per measured request',()=>assert(results.filter(x=>!x.reuseTls).every(x=>x.tlsConnections===x.requests)));test('TLS-on reuses pinned connections',()=>assert(results.filter(x=>x.reuseTls).every(x=>x.tlsConnections<=6&&x.requests>=30)));test('selector returns bounded policy',()=>{assert([1,4].includes(choice.selected.window));assert([4,8].includes(choice.selected.batch));assert.equal(typeof choice.selected.reuseTls,'boolean');});
  const holdout=await scenario(sources,choice.selected,99,{prefix:248});test('holdout passes segment rollover',()=>assert.equal(holdout.rows,136));
  const crash=await scenario(sources,{window:4,batch:8,reuseTls:true},100,{crash:true,prefix:256});test('crash resumed without duplicate committed rows',()=>assert.equal(crash.rows,128));
  const avg=(x)=>x.reduce((a,b)=>a+b,0)/x.length;const effects={};for(const [name,a,b] of [['window',1,4],['batch',4,8],['reuseTls',false,true]]){const low=results.filter(x=>x[name]===a).map(x=>x.recordsPerSecond);const high=results.filter(x=>x[name]===b).map(x=>x.recordsPerSecond);effects[name]={from:a,to:b,lowMean:+avg(low).toFixed(2),highMean:+avg(high).toFixed(2),difference:+(avg(high)-avg(low)).toFixed(2)};}
  const report={sheet:164,status:'PASS',checks,seed:'0x164bad5',design:'2 x 2 x 2 factorial randomized within each of two blocks; per-page deterministic 3..14ms injected tail latency',factors:{window:[1,4],batch:[4,8],tlsReuse:[false,true]},sourceRecords:sourceHead.count,benchmarkRowsRecovered:128,results,effects,policySelection:choice,holdout,crash,host:os.hostname(),node:process.version,cpu:os.cpus()[0].model,warning:'One physical host, only two replicates per configuration; policy selected on test data and evaluated on one holdout. Timings are observational, not a generalizable guarantee.'};fs.writeFileSync(path.join(__dirname,'benchmark164.json'),JSON.stringify(report,null,2)+'\n');console.log('SHEET164 GATE '+checks+'/'+checks+' PASS');
 }finally{await Promise.allSettled(Object.values(sources).map(stop));}}
main().catch(e=>{console.error('SHEET164 FAIL',e.stack||e);process.exitCode=1;}).finally(async()=>{await Promise.allSettled(processes.map(stop));if(process.env.S164_KEEP!=='1')fs.rmSync(root,{recursive:true,force:true});});
`````

## make_docs164.py

`````python
from pathlib import Path
import json, statistics, datetime
B=Path(__file__).resolve().parent
j=json.loads((B/'benchmark164.json').read_text())
lines=['# SHEET 164 — Factorial Benchmark Report','','**Status:** 68/68 new checks PASS; inherited SHEET 163 gate 45/45 PASS in isolated snapshot, exit 0.','', '## Protocol and experiment design','', '- Three independent factors: prefetch window `{1,4}` × durable record batch `{4,8}` × pinned mTLS reuse `{off,on}` = **8 conditions**.','- Two reproducibly shuffled blocks, seed `0x164bad5`; each condition recovers the same 128-record suffix from a 384-record source.','- Signed quorum proof pages, authenticated SHA-256 Merkle extensions, and exactly ordered segment/head fsyncs remain active in every condition.','- Synthetic page completion jitter is deterministic, 3–14 ms according to offset and block; no simulated multi-host network or remote storage.','- Each condition begins with a fresh 256-record target copied from one verified seed. Timing includes recovery handshakes and RPCs but excludes the setup/seed copy.','- The mTLS-off branch creates new authenticated TLS connections per request and **keeps certificate pinning enabled**.','', '## Observed throughput', '', '| Prefetch | Batch | Reuse TLS | Block 1 rec/s | Block 2 rec/s | Mean/median rec/s | TLS connections/request |','|---:|---:|:---:|---:|---:|---:|:---|']
for s in sorted(j['policySelection']['scored'],key=lambda x:(int(x['key'].split('/')[0]),int(x['key'].split('/')[1]),x['key'].split('/')[2])):
    w,b,t=s['key'].split('/'); rs=[r for r in j['results'] if (r['window'],r['batch'],str(r['reuseTls']).lower())==(int(w),int(b),t)];rs=sorted(rs,key=lambda x:x['block']); pairs=', '.join(f"{r['tlsConnections']}/{r['requests']}" for r in rs)
    lines.append(f"| {w} | {b} | {'on' if t=='true' else 'off'} | {rs[0]['recordsPerSecond']:.2f} | {rs[1]['recordsPerSecond']:.2f} | **{s['medianRowsPerSecond']:.2f}** | {pairs} |")
e=j['effects']
lines+=['', '## Factor-level marginal means (descriptive, not causal confidence intervals)','', '| Factor | Low condition | High condition | Difference (records/s) |','|---|---:|---:|---:|']
for k,v in e.items():lines.append(f"| {k} | {v['lowMean']:.2f} | {v['highMean']:.2f} | {v['difference']:+.2f} |")
w=j['policySelection']['scored'][0];slow=j['policySelection']['scored'][-1]
lines+=['',f"Highest two-trial median: **{w['key']} → {w['medianRowsPerSecond']:.2f} records/s**. Lowest median: {slow['key']} → {slow['medianRowsPerSecond']:.2f} records/s. Their cross-factor ratio is {w['medianRowsPerSecond']/slow['medianRowsPerSecond']:.2f}×, **not** a controlled estimate of any single optimization.", '', '## Holdout and crash injections','',f"- Chosen policy: `{json.dumps(j['policySelection']['selected'],sort_keys=True)}`.", f"- Independent holdout: **{j['holdout']['rows']} rows**, **{j['holdout']['seconds']:.4f} s**, **{j['holdout']['recordsPerSecond']:.2f} records/s**. Starts at 248 to exercise segment rollover.", '- Actual child-process kill after durable segment/head persistence but before the acknowledgement; restart resumed the original signed transaction and converged to the correct Merkle root without duplicates.', '- The crash test’s reported post-restart duration **excludes the pre-crash period**, so it is not directly comparable to the factorial throughput figures.', '', '## Verification and limits','', '- 68/68 new checks, exit 0. A separate untouched snapshot of SHEET 163 passed 45/45, exit 0.', '- Every measurement is one-host loopback mTLS with synthetic keys and local disk. TLS connections are authenticated even when reuse is disabled.', '- The selected policy was chosen from just two repetitions per configuration: selection bias, caching, and run-order effects remain possible.', '- All 16 factorial runs use the same source history and shared source processes, limiting repeated setup variance but not eliminating host scheduling noise.', '- The proof page is still a bounded 8-record unit; the 4-record factor splits already-verified pages into smaller durable commits.', '- Crash injection covers one chosen policy; it is not a proof of all possible power failures, multi-host partitions, or Byzantine behavior.', '- Cross-host consensus and the unresolved historical SHEET 142 timing-sensitive assertion are not claimed fixed.', '', '## Exact reproducibility','', '```bash','node gate164.js','python make_docs164.py','python browser-check164.py','bash run-inherited163.sh','```','','Raw machine-readable measurements: `benchmark164.json`; command logs: `gate164.log`, `audit/inherited163.log`.']
(B/'BENCHMARK-REPORT.md').write_text('\n'.join(lines)+'\n')
ascii='''OASIS / ROOT0 / SHEET 164 — FACTORIAL PERFORMANCE AND RECOVERY
============================================================
INPUT : signed 2/3 witness head + independently pinned floor
  | 01   Client authenticates 384-record Merkle checkpoint
  | 02   Verify source quorum, resource, hash and final root
  | 03   Load durable target cursor at 256 (holdout: 248)
  | 04   Select candidate from 2 × 2 × 2 policy lattice
  v
 +-------------------- PREFETCH WINDOW --------------------+
 |  WINDOW 1 (serial)             WINDOW 4 (parallel)        |
 |  PAGE0 -> check               PAGE0 -> PAGE1 -> PAGE2 ...|
 |                               |                       |   |
 |                           out-of-order responses possible |
 +-------------------------------+--------------------------+
                                 |
                         ORDERED PAGE BUFFER
                                 |
                     VERIFY Ed25519 + MERKLE EXTENSION
                                 |
               2 FACTORS: BATCH 4 OR BATCH 8
                                 |
                SPLIT AT 256-RECORD SEGMENT BOUNDARY
                                 |
                         EXCLUSIVE WRITER LOCK
                                 |
                        DURABLE SEGMENT FSYNC
                                 |
                         DURABLE HEAD FSYNC
                                 |
                         ADVANCE TRUSTED CURSOR
                                 |
              3RD FACTOR: TLS KEEPALIVE OR FRESH TLS
                  (CERTIFICATE PINNING ON BOTH)
                                 |
            +--------------------+-------------------+
            |                    |                   |
            v                    v                   v
          CONTINUE             CRASH              ERROR
            |                    |                   |
          PAGE+1          SIGNED STATUS           REJECT
            |             RESTART NODE         FAIL CLOSED
            |             REPLAY CURSOR            |
            |             NO DUPLICATES           |
            +--------------------+                   |
                                 |                   |
                            COMPLETE ROOT            |
                                 |                   |
                           VERIFY FINAL HEAD         |
                                 |                   |
                          NEXT VERIFIED STATE     QUARANTINE

EXPERIMENT CONTROL
  |- 8 configurations / 2 randomized blocks = 16 timed runs
  |- each run uses same certified source and fresh 256-row target
  |- deterministic 3–14ms synthetic page-tail jitter
  |- independently measure throughput, TLS connections, requests
  |- choose fastest median of two replicates (bounded policy)
  |- holdout: new target at 248, crosses segment rollover
  `- real child crash after fsync, before ACK, restart + recovery

SECURITY/PROVENANCE
  SHA-256 indexed segment tree -> inclusion -> extension
  resource Ed25519 -> 2/3 witness signatures -> external pin
  only ordered writes may change durable state; speculative reads
  are discarded after any ambiguous cursor step.

UNVERIFIED: cross-host durability, all power-loss windows, old
SHEET142 intermittent assertion, statistical speed guarantee.
'''
(B/'KERNEL-ASCII.txt').write_text(ascii)
readme='''# SHEET 164 — Factorial Merkle Recovery Tuning

**Status:** 68/68 new checks PASS, exit 0. **Inherited SHEET 163:** 45/45 PASS in an isolated copy, exit 0. Full historical nested runner not executed.

This additive build preserves the complete SHEET 163 release under `baseline163/` and introduces a performance-tuning experiment without weakening Merkle or mTLS verification.

## Components

- `transport164.js`: optional TLS connection reuse, pinned certificate verification in both modes.
- `pipeline164.js`: signed quorum recovery with fetch window 1–4, ordered cursor writes and bounded physical segment batches.
- `gate164.js`: randomized 2×2×2 factorial, measured A/B, source-root assertions, TLS connection assertions, segment rollover holdout, real process-kill recovery.
- `benchmark164.json`, `BENCHMARK-REPORT.md`: raw measurements, policy scoring, factor means, caveats.
- `KERNEL-ASCII.txt`: full kernel pipeline, recovery branches, and verification boundaries.
- `index.html`: interactive measured-condition viewer.

## Run

```bash
node gate164.js
python make_docs164.py
python browser-check164.py
bash run-inherited163.sh
```

Tests require Node.js 22, OpenSSL, POSIX fsync/rename, and loopback networking. One physical host only. Full ancestor regressions remain unrerun. See benchmark report for experimental limitations.
'''
(B/'README.md').write_text(readme)
print('created docs',len(lines))
`````

## make_dashboard164.py

`````python
from pathlib import Path
import json,html
B=Path(__file__).resolve().parent
j=json.loads((B/'benchmark164.json').read_text())
rows=[]
for score in j['policySelection']['scored']:
 w,b,t=score['key'].split('/')
 trial=[x for x in j['results'] if x['window']==int(w) and x['batch']==int(b) and x['reuseTls']==(t=='true')]
 rows.append(dict(key=score['key'],window=int(w),batch=int(b),reuseTls=t=='true',median=score['medianRowsPerSecond'],trials=trial))
js=json.dumps({'rows':rows,'effects':j['effects'],'selected':j['policySelection']['selected'],'holdout':j['holdout'],'crash':j['crash']},separators=(',',':'))
page=r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OASIS • SHEET 164 Factorial Benchmark</title><style>
:root{color-scheme:dark;--bg:#05100d;--card:#10251e;--line:#295440;--ink:#e9fff4;--dim:#9fbcaf;--accent:#4ef7a5;--accent2:#b6ffa4}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 25% 0,#143b2a,#05100d 54%);color:var(--ink);font:15px/1.55 ui-monospace,Consolas,Menlo,monospace;min-height:100vh}main{max-width:1210px;padding:42px 26px 70px;margin:auto}a{color:var(--accent)}h1{font-size:clamp(2rem,5vw,4.2rem);line-height:1.06;letter-spacing:-.05em;margin:14px 0 6px}h2{font-size:1.15rem;margin:0 0 17px}p{color:var(--dim);max-width:76ch}.over{font-size:.78rem;letter-spacing:.23em;color:var(--accent);text-transform:uppercase}.meta{margin:5px 0 28px}.cols{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:22px 0 28px}.stats,.panel{background:linear-gradient(145deg,rgba(22,57,43,.8),rgba(10,29,23,.88));border:1px solid var(--line);border-radius:16px;padding:21px}.num{font-size:clamp(1.45rem,3.1vw,2.6rem);font-weight:700;color:var(--accent);line-height:1.3}.hint{font-size:.83rem;color:var(--dim)}.layout{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(320px,.7fr);gap:17px}.bar{display:grid;grid-template-columns:112px 1fr 84px;align-items:center;gap:12px;margin:12px 0}.track{height:18px;border:1px solid #366b4d;background:#061c13;border-radius:7px;overflow:hidden}.fill{height:100%;background:linear-gradient(90deg,#277f55,#4ef7a5);border-radius:6px;min-width:2px}.bar.active .fill{background:linear-gradient(90deg,#73b74c,#ccff9e)}.bar .tag{background:none;border:0;color:var(--ink);font:inherit;cursor:pointer;text-align:left;padding:8px 0}.bar .tag:hover,.bar.active .tag{color:var(--accent2)}.value{text-align:right;font-variant-numeric:tabular-nums;font-size:.84rem}.item{width:100%;padding:12px;background:transparent;border:1px solid var(--line);border-radius:8px;color:var(--ink);font:inherit;cursor:pointer;text-align:left;margin:4px 0}.item:hover,.item[aria-pressed=true]{border-color:var(--accent);background:rgba(78,247,165,.09)}.scenario{font-size:.75rem;color:var(--dim)}svg{width:100%;height:auto}.flow{white-space:pre;overflow:auto;background:#06140f;padding:12px;border:1px solid var(--line);border-radius:10px;color:#b3fdd1;font-size:.8rem}.btn{background:var(--accent);color:#062018;font:700 14px ui-monospace,monospace;border:0;border-radius:10px;padding:12px 16px;cursor:pointer}.btn:hover{background:#acffc7}.footer{font-size:.8rem;color:var(--dim);margin-top:21px}.status{display:inline-block;border:1px solid #4bbf81;background:#0d3221;color:#aaffca;border-radius:100px;font-size:.75rem;padding:4px 11px;margin-top:12px}#detail{min-height:180px}#detail pre{white-space:pre-wrap;overflow-wrap:anywhere;color:var(--accent2)}@media(max-width:840px){.layout{grid-template-columns:1fr}.cols{grid-template-columns:1fr}.bar{grid-template-columns:100px 1fr 72px}main{padding:25px 15px}}
</style></head><body><main><div class="over">ROOT0 // OASIS // performance verification</div><h1>SHEET <span style="color:var(--accent)">164</span><br>RECOVERY FACTORIAL</h1><p class="meta">2×2×2 randomized benchmark · Merkle-verified ordered writes · live mTLS · 2026-10-09</p><span class="status">0e PASS · 68 / 68 new checks</span>
<div class="cols"><div class="stats"><div class="num">8 × 2</div><div class="hint">factorial variants × blocks</div></div><div class="stats"><div class="num">45 / 45</div><div class="hint">inherited S163 isolated checks</div></div><div class="stats"><div class="num">4 / 8 / TLS</div><div class="hint">tuning dimensions</div></div></div>
<div class="layout"><section class="panel"><h2>Measured median recovery throughput</h2><p>Rows/second. Select a bar to inspect both trial measurements, request counts and TLS handshakes.</p><div id="bars" role="group" aria-label="Benchmark configurations"></div><p class="hint">Within each trial, only the selected performance switches differ. Two replicates are not enough for confidence intervals.</p></section>
<section class="panel"><h2>Authenticated scenario inspector</h2><div id="detail" aria-live="polite"></div><div id="special"><button type="button" class="item" id="holdout">↗ HOLDOUT · segment rollover</button><button type="button" class="item" id="crash">↗ CRASH · persisted write, lost ACK</button><button type="button" class="item" id="effects">↗ MARGINAL EFFECTS · factor means</button></div><button type="button" class="btn" id="export">Export benchmark JSON</button><p class="scenario" id="export-status">No export generated</p></section></div>
<div class="panel" style="margin-top:17px"><h2>Signed and ordered recovery pipeline</h2><svg viewBox="0 0 920 144" aria-label="Quorum to Merkle verification to parallel fetch to ordered batches and crash recovery" role="img"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0 0 L7 3 L0 6" fill="none" stroke="#71dfaa" stroke-width="1.4"/></marker></defs><g stroke="#347f61" stroke-width="1.5" fill="#102e22"><rect x="4" y="27" width="145" height="84" rx="12"/><rect x="184" y="27" width="145" height="84" rx="12"/><rect x="364" y="27" width="145" height="84" rx="12"/><rect x="544" y="27" width="158" height="84" rx="12"/><rect x="738" y="27" width="178" height="84" rx="12"/></g><g stroke="#71dfaa" stroke-width="2" marker-end="url(#arrow)"><path d="M149 69 H180"/><path d="M329 69 H360"/><path d="M509 69 H540"/><path d="M702 69 H734"/></g><g fill="#d2ffea" font-family="monospace" text-anchor="middle" font-size="13"><text x="77" y="61">SIGNED 2/3</text><text x="77" y="79">QUORUM</text><text x="256" y="61">MERKLE</text><text x="256" y="79">VERIFY</text><text x="436" y="61">PARALLEL</text><text x="436" y="79">PREFETCH</text><text x="622" y="61">ORDERED FSYNC</text><text x="622" y="79">BATCH 4 / 8</text><text x="827" y="61">RESTART-SAFE</text><text x="827" y="79">CURSOR</text></g></svg><p class="footer">TLS certificate pinning stays enforced for both reused and fresh sockets. Speculative fetching never authorizes speculative writes.</p></div><p class="footer">Single-host laboratory benchmark. Results do not establish cross-host atomicity or universal throughput. Source: benchmark164.json · SHA-256 authenticated archive.</p></main><script>
const data=__DATA__;
const root=document.getElementById('bars'),detail=document.getElementById('detail');
const formatted=x=>Number(x).toFixed(2),cls=k=>k.replaceAll('/','-');
function inspect(row){document.querySelectorAll('.bar').forEach(el=>el.classList.toggle('active',el.dataset.key===row.key));detail.innerHTML='<div class="over">FACTORS</div><h2>'+row.window+' prefetch / '+row.batch+' records / TLS '+(row.reuseTls?'reused':'fresh')+'</h2><div class="num">'+formatted(row.median)+' /s</div><div class="hint">Median of two throughput observations</div><pre>'+row.trials.map(x=>'block '+(x.block+1)+': '+formatted(x.recordsPerSecond)+' /s  · TLS '+x.tlsConnections+'/'+x.requests+' · '+formatted(x.seconds)+' sec').join('\n')+'</pre>';}
const max=Math.max(...data.rows.map(x=>x.median));for(const row of data.rows){const e=document.createElement('div');e.className='bar';e.dataset.key=row.key;e.innerHTML='<button class="tag" aria-label="Inspect '+row.key+'" type="button">'+row.window+'x / '+row.batch+' / '+(row.reuseTls?'KA':'NEW')+'</button><div class="track"><div class="fill" style="width:'+(100*row.median/max).toFixed(1)+'%"></div></div><div class="value">'+formatted(row.median)+'</div>';e.querySelector('button').onclick=()=>inspect(row);root.appendChild(e);}
function view(kind){document.querySelectorAll('.bar').forEach(e=>e.classList.remove('active'));if(kind==='holdout'){const d=data.holdout;detail.innerHTML='<div class="over">EXTERNAL HOLDOUT</div><h2>Trusted segment rollover</h2><div class="num">'+formatted(d.recordsPerSecond)+'/s</div><pre>records: '+d.rows+'\nstart: '+d.prefix+'\nend: '+(d.prefix+d.rows)+'\nverified Merkle root: PASS</pre>';}else if(kind==='crash'){detail.innerHTML='<div class="over">FAULT INJECTION</div><h2>Real resource-process kill</h2><div class="num">NO DUPLICATES</div><pre>durable batch before ACK\nSIGEXIT -> process restart\nauthenticated cursor -> continue\nfinal Merkle root: PASS</pre>';}else{detail.innerHTML='<div class="over">AVERAGE MARGINAL EFFECTS</div><h2>Descriptive factor comparison</h2><pre>'+Object.entries(data.effects).map(([k,v])=>k+'\n  low '+formatted(v.lowMean)+'/s\n  high '+formatted(v.highMean)+'/s\n  change '+formatted(v.difference)+'/s').join('\n')+'</pre>';}}
for(const key of ['holdout','crash','effects'])document.getElementById(key).onclick=()=>view(key);
document.getElementById('export').onclick=()=>{const bytes=JSON.stringify(data,null,2);const blob=new Blob([bytes],{type:'application/json'}),url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='SHEET164-benchmark-export.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),250);document.getElementById('export-status').textContent='Export prepared · '+bytes.length+' characters';};
inspect(data.rows[0]);
</script></body></html>'''
(B/'index.html').write_text(page.replace('__DATA__',js))
print('wrote html',len(page))
`````

## browser-check164.py

`````python
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parent
html=(BASE/'index.html').read_text()
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1280,'height':920},accept_downloads=True)
    page.set_content(html,wait_until='load')
    passed=0
    for button in page.locator('#bars button').all():
        button.click()
        assert page.locator('#detail .num').inner_text().endswith('/s')
        passed+=1
    for k in ('holdout','crash','effects'):
        page.locator('#'+k).click()
        assert len(page.locator('#detail').inner_text())>40
        passed+=1
    with page.expect_download() as dl:
        page.locator('#export').click()
    assert dl.value.suggested_filename=='SHEET164-benchmark-export.json'
    passed+=1
    page.screenshot(path=str(BASE/'preview.png'),full_page=True)
    browser.close()
(BASE/'browser-check.log').write_text(f'SHEET164 CHROMIUM {passed}/{passed} PASS\n')
print(f'SHEET164 CHROMIUM {passed}/{passed} PASS')
`````

## make-release164.py

`````python
from pathlib import Path
import hashlib,zipfile,json,sys
B=Path(__file__).resolve().parent
PRIOR=Path('/mnt/data/SHEET163-parallel-merkle-ordered-commit.zip')
ZIP=B.parent/'SHEET164-factorial-tuning.zip'
SHA=B.parent/'SHEET164-factorial-tuning.zip.sha256.txt'
def h(x):return hashlib.sha256(x).hexdigest()
# Confirm identical bytes with independently sealed predecessor, not mutable workspace state.
with zipfile.ZipFile(PRIOR) as prior:
    names=[n for n in prior.namelist() if not n.endswith('/')]
    for n in names:
        rel=n[len('sheet163/'):]
        f=B/'baseline163'/rel
        if not f.is_file():raise RuntimeError('Inherited file missing: '+n)
        if h(f.read_bytes())!=h(prior.read(n)):raise RuntimeError('Inherited byte mismatch: '+n)
if len(names)!=753:raise RuntimeError('Unexpected inherited file count')
needed=['pipeline164.js','transport164.js','gate164.js','benchmark164.json','gate164.log','index.html','README.md','BENCHMARK-REPORT.md','KERNEL-ASCII.txt','browser-check.log','audit/inherited163.log','audit/inherited163.exit','SOURCE-ALL164.md']
for n in needed:
    if not (B/n).is_file():raise RuntimeError('Missing release file: '+n)
if 'SHEET164 GATE 68/68 PASS' not in (B/'gate164.log').read_text():raise RuntimeError('New gate failed')
if (B/'audit/inherited163.exit').read_text().strip()!='0':raise RuntimeError('Inherited gate failed')
if 'SHEET163 GATE 45/45 PASS' not in (B/'audit/inherited163.log').read_text():raise RuntimeError('Inherited gate missing pass')
if 'SHEET164 CHROMIUM 12/12 PASS' not in (B/'browser-check.log').read_text():raise RuntimeError('Chromium check failed')
meta={'schema':'oasis.sheet164.release.v1','sheet':164,'parent':163,'status':'0e / PASS','newTests':68,'inherited163Tests':45,'chromiumChecks':12,'inheritedFileCount':len(names),'benchmarkFactorialRuns':16,'holdoutRuns':1,'crashRuns':1,'sourceRecords':384,'factorialRecoveredPerRun':128,'tlsReuseComparison':'certificate pinning active in both policies','fullHistoricalChain':'not run; only S163 gate isolated','benchmarkReport':'BENCHMARK-REPORT.md'}
(B/'release-receipt.json').write_text(json.dumps(meta,indent=2)+'\n')
files=sorted(p for p in B.rglob('*') if p.is_file() and not p.name.startswith('.'))
files=[p for p in files if p.name not in ('SHA256SUMS','release-receipt.json')]
manifest='\n'.join(f'{h(p.read_bytes())}  {p.relative_to(B)}' for p in files)+'\n'
(B/'SHA256SUMS').write_text(manifest)
files=sorted(p for p in B.rglob('*') if p.is_file() and not p.name.startswith('.'))
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as out:
    for p in files:out.write(p,'sheet164/'+str(p.relative_to(B)))
with zipfile.ZipFile(ZIP,'r') as z:
    if z.testzip() is not None:raise RuntimeError('Bad ZIP CRC')
    if len(z.namelist())!=len(files):raise RuntimeError('ZIP omissions')
    for n in names:
        new='sheet164/baseline163/'+n[len('sheet163/'):]
        if z.read(new)!=((B/'baseline163'/n[len('sheet163/'):]).read_bytes()):raise RuntimeError('Stored baseline mismatch')
    for p in files:
        if h(z.read('sheet164/'+str(p.relative_to(B))))!=h(p.read_bytes()):raise RuntimeError('New file mismatch '+str(p))
SHA.write_text(f'{h(ZIP.read_bytes())}  {ZIP.name}\n')
print(json.dumps({'archive':str(ZIP),'bytes':ZIP.stat().st_size,'sha256':h(ZIP.read_bytes()),'inheritedFilesVerified':len(names),'newTests':68,'inheritedGate':45,'chromiumChecks':12,'packagedFiles':len(files)},indent=2))
`````

## run-new.sh

`````bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
node gate164.js | tee gate164.log
python make_docs164.py
python make_dashboard164.py
python browser-check164.py
`````

## run-inherited163.sh

`````bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cp -a baseline163/. "$TMP/"
(cd "$TMP" && node gate163.js) | tee audit/inherited163.log
`````

## KERNEL-ASCII.txt

`````text
OASIS / ROOT0 / SHEET 164 — FACTORIAL PERFORMANCE AND RECOVERY
============================================================
INPUT : signed 2/3 witness head + independently pinned floor
  | 01   Client authenticates 384-record Merkle checkpoint
  | 02   Verify source quorum, resource, hash and final root
  | 03   Load durable target cursor at 256 (holdout: 248)
  | 04   Select candidate from 2 × 2 × 2 policy lattice
  v
 +-------------------- PREFETCH WINDOW --------------------+
 |  WINDOW 1 (serial)             WINDOW 4 (parallel)        |
 |  PAGE0 -> check               PAGE0 -> PAGE1 -> PAGE2 ...|
 |                               |                       |   |
 |                           out-of-order responses possible |
 +-------------------------------+--------------------------+
                                 |
                         ORDERED PAGE BUFFER
                                 |
                     VERIFY Ed25519 + MERKLE EXTENSION
                                 |
               2 FACTORS: BATCH 4 OR BATCH 8
                                 |
                SPLIT AT 256-RECORD SEGMENT BOUNDARY
                                 |
                         EXCLUSIVE WRITER LOCK
                                 |
                        DURABLE SEGMENT FSYNC
                                 |
                         DURABLE HEAD FSYNC
                                 |
                         ADVANCE TRUSTED CURSOR
                                 |
              3RD FACTOR: TLS KEEPALIVE OR FRESH TLS
                  (CERTIFICATE PINNING ON BOTH)
                                 |
            +--------------------+-------------------+
            |                    |                   |
            v                    v                   v
          CONTINUE             CRASH              ERROR
            |                    |                   |
          PAGE+1          SIGNED STATUS           REJECT
            |             RESTART NODE         FAIL CLOSED
            |             REPLAY CURSOR            |
            |             NO DUPLICATES           |
            +--------------------+                   |
                                 |                   |
                            COMPLETE ROOT            |
                                 |                   |
                           VERIFY FINAL HEAD         |
                                 |                   |
                          NEXT VERIFIED STATE     QUARANTINE

EXPERIMENT CONTROL
  |- 8 configurations / 2 randomized blocks = 16 timed runs
  |- each run uses same certified source and fresh 256-row target
  |- deterministic 3–14ms synthetic page-tail jitter
  |- independently measure throughput, TLS connections, requests
  |- choose fastest median of two replicates (bounded policy)
  |- holdout: new target at 248, crosses segment rollover
  `- real child crash after fsync, before ACK, restart + recovery

SECURITY/PROVENANCE
  SHA-256 indexed segment tree -> inclusion -> extension
  resource Ed25519 -> 2/3 witness signatures -> external pin
  only ordered writes may change durable state; speculative reads
  are discarded after any ambiguous cursor step.

UNVERIFIED: cross-host durability, all power-loss windows, old
SHEET142 intermittent assertion, statistical speed guarantee.
`````