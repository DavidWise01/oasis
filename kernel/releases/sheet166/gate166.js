const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {performance}=require('node:perf_hooks');
const {BatchStore}=require('./baseline165/baseline164/baseline163/baseline162/batch162');
const P=require('./baseline165/baseline164/baseline163/baseline162/baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const V=require('./baseline165/baseline164/baseline163/baseline162/baseline161/proof161');
const Pipeline=require('./baseline165/baseline164/pipeline164');
const Policy=require('./baseline165/policy165');
const Guard=require('./baseline165/guard165');
const root=fs.mkdtempSync(path.join(os.tmpdir(),'oasis-s166-'));
const f=(...parts)=>path.join(root,...parts);let checks=0;let processes=[];
function test(label,fn){fn();checks++;console.log('PASS',checks,label);}
async function atest(label,fn){await fn();checks++;console.log('PASS',checks,label);}
const openssl=(...args)=>cp.execFileSync('openssl',args,{cwd:root,stdio:'pipe'});
function keypair(label){const k=crypto.generateKeyPairSync('ed25519');const priv=f(label+'.priv'),pub=f(label+'.pub');fs.writeFileSync(priv,k.privateKey.export({format:'pem',type:'pkcs8'}));fs.writeFileSync(pub,k.publicKey.export({format:'pem',type:'spki'}));return {...k,priv,pub};}
function cert(label){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',label+'.key','-out',label+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(label+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',label+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',label+'.crt','-days','2','-sha256','-extfile',label+'.ext');return {key:f(label+'.key'),cert:f(label+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(label+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
const ID='OASIS-SHEET165';let certs,keys,anchorKey,source,sourceHead,sources,seedDir;
const row=i=>({txid:'s165:'+i,payload:'sample-'+i});
function fill(store,start,end){for(let i=start;i<end;){const k=Math.min(8,256-i%256,end-i);store.batch(Array.from({length:k},(_,j)=>row(i+j)));i+=k;}}
function setup(){openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=OASIS-S164-CA');certs=Object.fromEntries(['client','red','green','blue'].map(n=>[n,cert(n)]));keys=Object.fromEntries(['red','green','blue'].map(n=>[n,keypair(n)]));anchorKey=keypair('floor');const store=new BatchStore(f('source-red'),ID);store.init();fill(store,0,384);sourceHead=store.read();fs.cpSync(f('source-red'),f('source-green'),{recursive:true});const prefix=new BatchStore(f('seed256'),ID);prefix.init();fill(prefix,0,256);seedDir=f('seed256');}
function config(name,dir,session){return {nodeId:name,resourceId:ID,...certs[name],dir,signKey:keys[name].priv,anchorPublicKey:anchorKey.pub,peerPublicKeys:Object.fromEntries(Object.entries(keys).map(([n,v])=>[n,v.pub])),clientPin:certs.client.certPin,session:f('sessions',session+'-'+name+'.json'),externalPin:f('pins',session+'-'+name+'.json'),quarantine:f('quarantine',session+'-'+name+'.txt')};}
async function spawn(conf,label){P.atomic(f('configs',label+'.json'),conf);let err='';const proc=cp.fork(path.join(__dirname,'baseline165/baseline164/baseline163/node163.js'),[],{env:{...process.env,S163_CONFIG:f('configs',label+'.json')},stdio:['ignore','pipe','pipe','ipc']});proc.stderr.on('data',chunk=>{err+=chunk;});const port=await new Promise((resolve,reject)=>{let resolved=false;const timer=setTimeout(()=>{if(!resolved){resolved=true;reject(Error('S165_START_TIMEOUT '+label+' '+err));}},12000);proc.once('message',m=>{if(!resolved){resolved=true;clearTimeout(timer);resolve(m.port);}});proc.once('exit',code=>{if(!resolved){resolved=true;clearTimeout(timer);reject(Error('S165_START_EXIT '+code+' '+err));}});});const out={proc,port,label,conf};processes.push(out);return out;}
async function stop(x){if(!x||x.proc.exitCode!==null||x.proc.signalCode!==null)return;await new Promise(resolve=>{let settled=false;function done(){if(!settled){settled=true;clearTimeout(timer);resolve();}}const timer=setTimeout(()=>{try{x.proc.kill('SIGKILL');}catch{}done();},800);x.proc.once('exit',done);try{x.proc.send('stop',e=>{if(e){try{x.proc.kill('SIGKILL');}catch{}done();}});}catch{try{x.proc.kill('SIGKILL');}catch{}done();}});}
function endpoints(peerNodes,blue){return Object.fromEntries(Object.entries({...peerNodes,blue}).map(([n,m])=>[n,{port:m.port,serverPin:certs[n].certPin}]));}
function makeClient(peerNodes,blue,conf,block){return Pipeline.make({identity:certs.client,nodes:endpoints(peerNodes,blue),keys:Object.fromEntries(Object.entries(keys).map(([n,v])=>[n,v.publicKey])),anchor:V.signAnchor(V.anchorBody(ID,sourceHead,100),anchorKey.privateKey),anchorKey:anchorKey.publicKey,fetchWindow:conf.window,batchMode:conf.batch===4?'fixed4':'fixed8',reuseTls:conf.reuseTls,delayFetch:offset=>block===900?16+((offset*7)%24):3+((offset*7+block*11)%12)});}
let seq=0;

const H=require('./policy166'),D=require('./decision166'),G=require('./guard166');
const wait=ms=>new Promise(r=>setTimeout(r,ms));
async function signer({dir,pinDir,crashAfterPin=false,serverCert=certs.policy,label='policy',resourcePublicKey=null}={}){
 const c={dir:dir||f('authority'),pinDir:pinDir||f('remote-pin'),crashAfterPin,...serverCert,signKey:keys.policy.priv,clientPin:certs.client.certPin,...(resourcePublicKey?{resourcePublicKey,resourceId:ID}:{})};
 const file=f('configs',label+'.json');P.atomic(file,c);let err='';const proc=cp.fork(path.join(__dirname,'decision-server166.js'),[],{env:{...process.env,S166_CONFIG:file},stdio:['ignore','pipe','pipe','ipc']});proc.stderr.on('data',b=>err+=b);
 const port=await new Promise((resolve,reject)=>{let done=false;const tm=setTimeout(()=>{if(!done){done=true;reject(Error('SIGNER_START_TIMEOUT '+err));}},9000);proc.once('message',m=>{if(!done){done=true;clearTimeout(tm);resolve(m.port);}});proc.once('exit',c=>{if(!done){done=true;clearTimeout(tm);reject(Error('SIGNER_EXIT '+c+' '+err));}});});
 const n={proc,port,conf:c,label};processes.push(n);return n;
}
const prpc=n=>(url,payload)=>P.rpc({port:n.port,key:certs.client.key,cert:certs.client.cert,ca:certs.client.ca,serverPin:certs.policy.certPin},url,payload);
const goodReq=(head,to,rows)=>{const req={expectedGeneration:head.generation,expectedHead:P.sha(head),from:head.mode,to,rows,reason:to==='baseline'?'PERFORMANCE_DEGRADED':'VERIFIED_HOLDOUT_REPROMOTION',root:P.sha('test-record-root-'+rows),measurementDigest:P.sha('sample-'+rows)};req.decisionId=P.sha(req);return req;};
async function run(){
 test('hysteresis starts in candidate',()=>assert.equal(H.initial().mode,'candidate'));
 test('bad input rejected',()=>assert.throws(()=>H.initial('invalid'),/INITIAL/));
 test('negative rates fail closed',()=>assert.throws(()=>H.observe(H.initial(),{rows:8,rate:-1,baselineRate:100}),/SAMPLE/));
 test('no duplicate row observation',()=>assert.throws(()=>H.observe(H.initial(),{rows:0,rate:50,baselineRate:100}),/SAMPLE/));
 test('unsupported candidate policy blocked',()=>assert.throws(()=>H.chooseVerifiedPolicy(H.initial(),{window:99,batch:8,reuseTls:true}),/BOUNDS/));
 let state=H.initial(),downs=0,drifts=0;
 for(let i=1;i<=80;i++){
  const rate=i%12<6?80:110,step=H.observe(state,{rows:i*8,rate,baselineRate:100});state=step.state;
  if(step.state.driftDetected)drifts++;
  if(step.transition){downs++;state=H.afterSigned(state,step.transition);}
 }
 test('alternating load does not oscillate policy',()=>assert(downs<=1));
 test('minimum dwell and consecutive windows delay fallback',()=>{let s=H.initial();for(let i=1;i<=5;i++){const x=H.observe(s,{rows:i*8,rate:i%2?81:130,baselineRate:100});assert(!x.transition);s=x.state;}});
 test('synthetic degradation produces fallback only after minimum dwell',()=>{let s=H.initial(),hit=null;for(let i=1;i<=8;i++){let x=H.observe(s,{rows:i*8,rate:60,baselineRate:100});s=x.state;if(x.transition){hit=x.transition;break;}}assert(hit&&hit.atRows>=48&&hit.to==='baseline');});
 test('promotion requires verified holdout',()=>{let s=H.initial('baseline',48);s.lastSwitchRows=0;s.cooldownUntilRows=96;for(let i=1;i<=20;i++){const x=H.observe(s,{rows:48+i*8,rate:150,baselineRate:100});assert(!x.transition);s=x.state;}});
 test('drift detector flags abrupt throughput collapse',()=>{let s=H.initial();for(let i=1;i<=20;i++)s=H.observe(s,{rows:i*8,rate:140,baselineRate:100}).state;for(let i=21;i<=30;i++)s=H.observe(s,{rows:i*8,rate:35,baselineRate:100}).state;assert(s.driftDetected);});
 test('promotion cannot bypass cooldown',()=>{let s=H.initial('baseline',64);s.lastSwitchRows=64;s.cooldownUntilRows=320;for(let i=1;i<=10;i++){const x=H.observe(s,{rows:64+i*8,rate:150,baselineRate:100,holdoutPassed:true});assert(!x.transition);s=x.state;}});
 test('signed transition refuses wrong origin state',()=>assert.throws(()=>H.afterSigned(H.initial(),{from:'baseline',to:'candidate',atRows:0}),/FORK/));
 test('signature rejects modification and nonce replay',()=>{const k=crypto.generateKeyPairSync('ed25519'),h=D.certify(D.genesis(),k.privateKey,'nonce123456789');assert.equal(D.check(h,k.publicKey,'nonce123456789').generation,0);assert.throws(()=>D.check(h,k.publicKey,'differentnonce123'),/SIGNATURE/);assert.throws(()=>D.check({...h,body:{...h.body,mode:'baseline'}},k.publicKey,'nonce123456789'),/SIGNATURE/);});
 // 1,000-window drift simulation, deterministic seed and injected regime changes.
 const rng=Policy.rng(166166);let s=H.initial(),events=[];let regime;
 for(let i=1;i<=1000;i++){
  regime=i<300?1.25:i<600?.72:i<900?1.22:.77;
  let ratio=regime*(.95+rng()*.1),sample=H.observe(s,{rows:i*8,rate:ratio*100,baselineRate:100,holdoutPassed:i>=600});s=sample.state;
  if(sample.transition){events.push(sample.transition);s=H.afterSigned(s,sample.transition);}
 }
 test('1,000-window drift simulation terminates',()=>assert.equal(s.windows,1000));
 test('1,000-window hysteresis limits policy flapping',()=>assert(events.length<=4&&events.length>=2));
 test('all simulated transitions respect 48-record minimum dwell',()=>{let last=0;for(const e of events){assert(e.atRows-last>=48);last=e.atRows;}});
 test('fallback precedes promotion in simulated timeline',()=>assert(events[0].to==='baseline'&&events[1].to==='candidate'));

 test('cooldown expires only after persisted row threshold',()=>{let s=H.initial('baseline',48);s.lastSwitchRows=48;s.cooldownUntilRows=144;let change;for(let i=1;i<=14;i++){const o=H.observe(s,{rows:48+i*8,rate:200,baselineRate:100,holdoutPassed:true});s=o.state;if(o.transition){change=o.transition;break;}}assert(change&&change.atRows>=144);});
 test('promoted policy requires trusted sign-off',()=>{let s=H.initial('baseline',48);s.lastSwitchRows=0;s.cooldownUntilRows=80;let got;for(let i=1;i<=7;i++){let o=H.observe(s,{rows:48+i*8,rate:180,baselineRate:100,holdoutPassed:true});s=o.state;if(o.transition){got=o.transition;break;}}assert(got&&got.reason==='VERIFIED_HOLDOUT_REPROMOTION');});
 test('candidate cannot promote directly',()=>{let s=H.initial();for(let i=1;i<=10;i++){const o=H.observe(s,{rows:i*8,rate:200,baselineRate:100,holdoutPassed:true});assert(!o.transition);s=o.state;}});
 test('signed witness rejects unsigned mode changes',()=>{let s=D.genesis();assert.throws(()=>D.check({body:s,signature:'bad'},keys.policy?.publicKey??crypto.generateKeyPairSync('ed25519').publicKey,''),/SIGNATURE/);});
 test('policy drift does not bypass signature gate',()=>{let s=H.initial();for(let i=1;i<=12;i++)s=H.observe(s,{rows:i*8,rate:i<6?130:50,baselineRate:100}).state;assert.equal(s.mode,'candidate');});
 const loadReport={windows:1000,events,changes:events.length,regimes:4};
 // Independently persisted external signer served via mTLS.
 const external=await signer();const rpc=prpc(external);let head=await G.head(rpc,keys.policy.publicKey);
 await atest('external authority starts at signed genesis',async()=>assert.equal(head.generation,0));
 await atest('pinned mTLS refuses wrong server fingerprint',async()=>{await assert.rejects(P.rpc({port:external.port,key:certs.client.key,cert:certs.client.cert,ca:certs.client.ca,serverPin:certs.green.certPin},'/head166',{nonce:'nonce-that-is-long'}),/SERVER_PIN_MISMATCH/);});
 await atest('mTLS unauthorized client certificate rejected',async()=>{await assert.rejects(P.rpc({port:external.port,key:certs.intruder.key,cert:certs.intruder.cert,ca:certs.intruder.ca,serverPin:certs.policy.certPin},'/head166',{nonce:'nonce-that-is-long'}),/TLS_PEER_NOT_PINNED/);});
 const req=goodReq(head,'baseline',64);
 let signed=await rpc('/decide166',{...req,nonce:'nonce1longenough'});
 await atest('separate signer durably authorizes fallback',async()=>assert.equal(D.check(signed,keys.policy.publicKey,'nonce1longenough').mode,'baseline'));
 await atest('signed external pin equals independently durable local head',async()=>assert.deepEqual(P.load(f('authority','head.json')),P.load(f('remote-pin','floor.json'))));
 await atest('replayed idempotent decision preserves generation',async()=>{let result=await rpc('/decide166',{...req,nonce:'nonce2longenough'});assert.equal(result.body.generation,1);});
 await atest('stale conflicting decision fails closed',async()=>await assert.rejects(rpc('/decide166',{...goodReq(head,'baseline',80),nonce:'nonce3longenough'}),/STALE_FLOOR/));

 await atest('wrong reason fails signer mode policy',async()=>{const cur=await G.head(rpc,keys.policy.publicKey);const bad={...goodReq(cur,'candidate',160),reason:'UNVERIFIED_PROMOTION',nonce:'nonce6longenough'};await assert.rejects(rpc('/decide166',bad),/PROMOTION_EVIDENCE/);});
 await atest('malformed measurement digest rejected',async()=>{const cur=await G.head(rpc,keys.policy.publicKey);const bad={...goodReq(cur,'candidate',160),measurementDigest:'bad',nonce:'nonce7longenough'};await assert.rejects(rpc('/decide166',bad),/DECISION_BINDING/);});
 await atest('nonincreasing observed rows rejected by signer',async()=>{const cur=await G.head(rpc,keys.policy.publicKey);const bad={...goodReq(cur,'candidate',cur.rows),nonce:'nonce8longenough'};await assert.rejects(rpc('/decide166',bad),/NONMONOTONIC_ROWS/);});
 await atest('unauthenticated read nonce refused',async()=>await assert.rejects(rpc('/head166',{nonce:'short'}),/BAD_NONCE/));
 await atest('signed read survives server restart',async()=>{await stop(external);const restarted=await signer({label:'policy-restart'});const x=await G.head(prpc(restarted),keys.policy.publicKey);assert.equal(x.generation,1);await stop(restarted);});
 const other=await signer({dir:f('rollback-state'),pinDir:f('rollback-pin'),label:'rollback'});
 let orpc=prpc(other);let g=await G.head(orpc,keys.policy.publicKey);await orpc('/decide166',{...goodReq(g,'baseline',64),nonce:'nonce4longenough'});
 await atest('rollback of local head rejected against independent pin',async()=>{await stop(other);P.atomic(f('rollback-state','head.json'),D.genesis());await assert.rejects((async()=>{let n=await signer({dir:f('rollback-state'),pinDir:f('rollback-pin'),label:'rollback-stale'});try{return await G.head(prpc(n),keys.policy.publicKey);}finally{await stop(n);}})(),/FLOOR_CONFLICT/);});
 await atest('external floor lost fails closed on signer start',async()=>{fs.rmSync(f('rollback-pin','floor.json'));assert.throws(()=>D.open(f('rollback-state'),keys.policy.privateKey,{pinDir:f('rollback-pin')}).read(),/STATE_MISSING/);});
 // External pin written; process killed before local head. No silent rollback.
 const crash=await signer({dir:f('crash-state'),pinDir:f('crash-pin'),crashAfterPin:true,label:'crash-signer'});const crpc=prpc(crash),prev=await G.head(crpc,keys.policy.publicKey);
 await atest('hard signer crash after durable external pin detected',async()=>{await assert.rejects(crpc('/decide166',{...goodReq(prev,'baseline',64),nonce:'nonce5longenough'}));await wait(120);assert(fs.existsSync(f('crash-state','crash-marker')));});
 await atest('partial signer commit blocks automatic restart',async()=>{await stop(crash);const restarted=await signer({dir:f('crash-state'),pinDir:f('crash-pin'),label:'crash-restart'});await assert.rejects(G.head(prpc(restarted),keys.policy.publicKey),/FLOOR_CONFLICT/);await stop(restarted);});

 const offline=await signer({dir:f('offline-state'),pinDir:f('offline-pin'),label:'offline-signer'});let candidateRuns=0;
 await atest('signer outage at downgrade refuses reopening baseline client',async()=>{
   let fakeNow=0;
   const factory=policy=>{candidateRuns++;return {close:()=>{},sync:async(target,{onCommit})=>{
     for(let i=0;i<8;i++){
       if(i===5){offline.proc.kill('SIGKILL');await wait(90);}
       onCommit(i*8,(i+1)*8);
     }
   }};};
   await assert.rejects(G.recover({factory,rpc:prpc(offline),signerPublicKey:keys.policy.publicKey,targetPublicKey:keys.blue.publicKey,candidate:{window:4,batch:8,reuseTls:true},baselineRate:100,clock:()=>{fakeNow+=200;return fakeNow;}}));
   assert.equal(candidateRuns,1);
 });
 // Full mTLS source/target + externally signed downgrade. Authenticate before fallback.
 const sources={red:await spawn(config('red',f('source-red'),'src'),'src-red'),green:await spawn(config('green',f('source-green'),'src'),'src-green')};
 let blue;let network;
 try{
  const dir=f('target-blue');fs.cpSync(seedDir,dir,{recursive:true});blue=await spawn(config('blue',dir,'blue'),'blue');
  // Fresh external floor with candidate genesis. Target starts at 256 durable records.
  const liveSigner=await signer({dir:f('live-policy'),pinDir:f('live-pin'),label:'live-policy',resourcePublicKey:keys.blue.pub});const liveRpc=prpc(liveSigner);

  await atest('resource-attested signer rejects hash-only policy changes',async()=>{const h=await G.head(liveRpc,keys.policy.publicKey);await assert.rejects(liveRpc('/decide166',{...goodReq(h,'baseline',48),nonce:'resourcebinding123'}),/RESOURCE_PROOF_REQUIRED/);});
  await atest('resource-attested signer rejects forged proof even with valid row evidence',async()=>{const h=await G.head(liveRpc,keys.policy.publicKey);await assert.rejects(liveRpc('/decide166',{...goodReq(h,'baseline',48),nonce:'resourcebinding456',resourceProof:{body:{resourceId:ID,count:300,root:P.sha('wrong')},signature:'forged'}}),/RESOURCE_PROOF_REQUIRED/);});
  let calls=0,manualClock=0,provenances=[];
  const factory=policy=>{calls++;return makeClient(sources,blue,policy,0);};
  const liveBegin=performance.now();
  const result=await G.recover({factory,rpc:liveRpc,signerPublicKey:keys.policy.publicKey,candidate:{window:4,batch:8,reuseTls:true},baseline:Policy.BASELINE,baselineRate:100,targetPublicKey:keys.blue.publicKey,clock:()=>{manualClock+=200;return manualClock;},onDecision:x=>provenances.push(x)});
  const after=new BatchStore(dir,ID).read();
  await atest('real mTLS protected recovery finishes at certified source root',async()=>{assert.equal(after.root,sourceHead.root);assert.equal(after.count,sourceHead.count);});
  await atest('real mTLS runtime switched only after signed downgrade',async()=>{assert.equal(result.mode,'baseline');assert(provenances.length===1);assert.equal(calls,2);});
  const now=await G.head(liveRpc,keys.policy.publicKey);
  await atest('live policy checkpoint survives complete physical recovery',async()=>{assert.equal(now.mode,'baseline');assert.equal(now.generation,1);});
  await atest('cryptographic wrong source root never permits performance fallback',async()=>{await assert.rejects(G.recover({factory:()=>({sync:async()=>{throw Error('S166_CRYPTOGRAPHIC_REJECTION')},close:()=>{}}),rpc:liveRpc,signerPublicKey:keys.policy.publicKey,candidate:{window:4,batch:8,reuseTls:true},baselineRate:100}),/CRYPTOGRAPHIC_REJECTION/);});
  network={rows:after.count-256,head:after.root,mode:result.mode,transition:provenances[0],policyGeneration:now.generation,clientRestarts:calls-1,elapsedSeconds:+((performance.now()-liveBegin)/1000).toFixed(5),signedRpcCount:3};
  await stop(liveSigner);
 }finally{await stop(blue);await Promise.allSettled(Object.values(sources).map(stop));}
 const result={schema:'oasis.sheet166.gate.v1',checks,loadReport,network};
 fs.writeFileSync(path.join(__dirname,'gate166-results.json'),JSON.stringify(result,null,2)+'\n');
 console.log('SHEET166 '+checks+'/'+checks+' PASS');
}
setup();certs.policy=cert('policy');certs.intruder=cert('intruder');keys.policy=keypair('policy-sign');
run().catch(e=>{console.error('SHEET166 FAIL',e.stack||e);process.exitCode=1;}).finally(async()=>{await Promise.allSettled(processes.map(stop));if(process.env.S166_KEEP!=='1')fs.rmSync(root,{recursive:true,force:true});});
