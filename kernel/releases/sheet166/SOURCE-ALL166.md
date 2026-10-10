# SHEET 166 — Complete New Authored Source

Exact new authored source files follow; complete historical frozen lineage remains inside the ZIP.

## policy166.js

`````javascript
'use strict';
// Pure, deterministic hysteresis; measurement inputs are performance observations, not security evidence.
const S165=require('./baseline165/policy165');
const RULES=Object.freeze({badBelow:.88,goodAbove:1.18,minDwellRows:48,cooldownRows:96,badWindows:3,goodWindows:4,driftBelow:.91,driftWindows:3});
const VALID_MODES=['candidate','baseline'];
function positive(n){return Number.isFinite(n)&&n>0;}
function initial(mode='candidate',atRows=0){if(!VALID_MODES.includes(mode)||!Number.isSafeInteger(atRows)||atRows<0)throw Error('S166_INITIAL');return{mode,rows:atRows,lastSwitchRows:atRows,cooldownUntilRows:0,bad:0,good:0,drift:0,fast:null,slow:null,driftDetected:false,windows:0};}
function validate(s){if(!s||!VALID_MODES.includes(s.mode)||!Number.isSafeInteger(s.rows)||s.rows<0||s.lastSwitchRows>s.rows)throw Error('S166_STATE');return s;}
function observe(state,{rows,rate,baselineRate,holdoutPassed=false}={},rules=RULES){
 validate(state);if(!Number.isSafeInteger(rows)||rows<=state.rows||!positive(rate)||!positive(baselineRate))throw Error('S166_SAMPLE');
 const ratio=rate/baselineRate;let s={...state,rows,windows:state.windows+1};
 s.fast=state.fast===null?ratio:0.45*ratio+0.55*state.fast;
 s.slow=state.slow===null?ratio:0.12*ratio+0.88*state.slow;
 s.drift= s.fast<s.slow*rules.driftBelow?state.drift+1:0;
 s.driftDetected=s.drift>=rules.driftWindows;
 s.bad=ratio<rules.badBelow?state.bad+1:0;
 s.good=ratio>rules.goodAbove?state.good+1:0;
 const dwell=rows-state.lastSwitchRows>=rules.minDwellRows;
 let transition=null;
 if(s.mode==='candidate'&&dwell&&s.bad>=rules.badWindows){
   transition={from:'candidate',to:'baseline',reason:'PERFORMANCE_DEGRADED',atRows:rows,observedRatio:+ratio.toFixed(5),windows:s.bad};
 }else if(s.mode==='baseline'&&dwell&&rows>=state.cooldownUntilRows&&s.good>=rules.goodWindows&&holdoutPassed===true){
   transition={from:'baseline',to:'candidate',reason:'VERIFIED_HOLDOUT_REPROMOTION',atRows:rows,observedRatio:+ratio.toFixed(5),windows:s.good};
 }
 return{state:s,transition,ratio};
}
function afterSigned(state,transition,rules=RULES){
 validate(state);if(!transition||state.mode!==transition.from||state.rows!==transition.atRows||!VALID_MODES.includes(transition.to)||transition.to===state.mode)throw Error('S166_TRANSITION_FORK');
 const s={...state,mode:transition.to,lastSwitchRows:state.rows,bad:0,good:0,drift:0,driftDetected:false,fast:null,slow:null};
 if(transition.to==='baseline')s.cooldownUntilRows=state.rows+rules.cooldownRows;
 return s;
}
function chooseVerifiedPolicy(state,optimized,baseline=S165.BASELINE){validate(state);S165.validate(optimized);S165.validate(baseline);return state.mode==='candidate'?optimized:baseline;}
module.exports={RULES,initial,observe,afterSigned,validate,chooseVerifiedPolicy};
`````

## decision166.js

`````javascript
'use strict';
// Separately persisted Ed25519 decision signer. Single signer, not multi-host consensus.
const fs=require('node:fs'),path=require('node:path');
const P=require('./baseline165/baseline164/baseline163/baseline162/baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const DOM='S166:POLICY_HEAD';
const SCHEMA='oasis.sheet166.decision.v1';
function genesis(){return{schema:SCHEMA,generation:0,mode:'candidate',rows:0,prevHash:'0'.repeat(64),decisionId:'GENESIS',root:'GENESIS'};}
function certify(body,privateKey,nonce=''){return {body:{...body,nonce},signature:P.sign(privateKey,DOM,{...body,nonce})};}
function check(cert,publicKey,nonce){if(!cert||!P.verify(publicKey,DOM,cert.body,cert.signature)||cert.body.schema!==SCHEMA||cert.body.nonce!==nonce)throw Error('S166_BAD_HEAD_SIGNATURE');return cert.body;}
function open(dir,priv,{pinDir=dir,crashAfterPin=false}={}){
 fs.mkdirSync(dir,{recursive:true});fs.mkdirSync(pinDir,{recursive:true});
 const local=path.join(dir,'head.json'),pin=path.join(pinDir,'floor.json');
 if(!fs.existsSync(local)&&!fs.existsSync(pin)){const g=genesis();P.atomic(pin,g);P.atomic(local,g);}
 function read(){const l=P.load(local),p=P.load(pin);if(l.schema!==SCHEMA||p.schema!==SCHEMA||P.sha(l)!==P.sha(p))throw Error('S166_EXTERNAL_FLOOR_CONFLICT');return l;}
 function advance(req){let current=read();
  if(req.decisionId===current.decisionId&&req.expectedGeneration===current.generation-1&&req.to===current.mode)return current;
  if(req.expectedGeneration!==current.generation||req.expectedHead!==P.sha(current))throw Error('S166_STALE_FLOOR');
  if(!['baseline','candidate'].includes(req.to)||req.to===current.mode||req.from!==current.mode)throw Error('S166_MODE_FORK');
  if(!Number.isSafeInteger(req.rows)||req.rows<=current.rows||req.rows-current.rows<8)throw Error('S166_NONMONOTONIC_ROWS');
  if(!/^[a-f0-9]{64}$/.test(req.measurementDigest)||!/^[a-f0-9]{64}$/.test(req.root)||!/^[a-f0-9]{64}$/.test(req.decisionId))throw Error('S166_DECISION_BINDING');
  if(req.to==='candidate'&&req.reason!=='VERIFIED_HOLDOUT_REPROMOTION')throw Error('S166_PROMOTION_EVIDENCE');
  if(req.to==='baseline'&&req.reason!=='PERFORMANCE_DEGRADED')throw Error('S166_DOWNGRADE_EVIDENCE');
  const next={schema:SCHEMA,generation:current.generation+1,mode:req.to,rows:req.rows,prevHash:P.sha(current),decisionId:req.decisionId,root:req.root,measurementDigest:req.measurementDigest,reason:req.reason};
  // Pin first: a crash between these writes makes reads fail closed; no automatic pin rollback.
  P.atomic(pin,next);
  if(crashAfterPin){fs.writeFileSync(path.join(dir,'crash-marker'),'after-external-pin');process.kill(process.pid,'SIGKILL');}
  P.atomic(local,next);return next;
 }
 return{read,advance,local,pin};
}
module.exports={SCHEMA,DOM,genesis,check,certify,open};
`````

## decision-server166.js

`````javascript
'use strict';
const fs=require('node:fs');
const P=require('./baseline165/baseline164/baseline163/baseline162/baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const D=require('./decision166');
const cfg=JSON.parse(fs.readFileSync(process.env.S166_CONFIG,'utf8'));
const store=D.open(cfg.dir,fs.readFileSync(cfg.signKey),{pinDir:cfg.pinDir,crashAfterPin:!!cfg.crashAfterPin});
const server=P.serve(cfg.key,cfg.cert,cfg.ca,(req,data)=>{
 P.peer(req,cfg.clientPin);
 if(req.url==='/head166'){
  if(typeof data.nonce!=='string'||data.nonce.length<12||data.nonce.length>128)throw Error('S166_BAD_NONCE');
  return D.certify(store.read(),fs.readFileSync(cfg.signKey),data.nonce);
 }
 if(req.url==='/decide166'){
  if(typeof data.nonce!=='string'||data.nonce.length<12||data.nonce.length>128)throw Error('S166_BAD_NONCE');
  if(cfg.resourcePublicKey){
   const proof=data.resourceProof;
   if(!proof?.body||!P.verify(fs.readFileSync(cfg.resourcePublicKey),'S161:STATUS',proof.body,proof.signature))throw Error('S166_RESOURCE_PROOF_REQUIRED');
   if(proof.body.resourceId!==cfg.resourceId||proof.body.root!==data.root||!Number.isSafeInteger(proof.body.count)||proof.body.count<data.rows)throw Error('S166_RESOURCE_PROOF_MISMATCH');
  }
  return D.certify(store.advance(data),fs.readFileSync(cfg.signKey),data.nonce);
 }
 throw Error('S166_UNKNOWN_RPC');
});
process.on('message',m=>{if(m==='stop')server.close(()=>process.exit(0));});
`````

## guard166.js

`````javascript
'use strict';
// Hysteresis first, independently certified fallback second, then authenticated durable recovery.
const crypto=require('node:crypto');
const Policy=require('./policy166'),D=require('./decision166');
const S165=require('./baseline165/policy165');
const P=require('./baseline165/baseline164/baseline163/baseline162/baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const nonce=()=>crypto.randomBytes(16).toString('hex');
async function head(rpc,publicKey){const n=nonce(),cert=await rpc('/head166',{nonce:n});const {nonce:challenge,...body}=D.check(cert,publicKey,n);return body;}
async function decide(rpc,publicKey,proposal,measurementDigest,root,resourceProof){const before=await head(rpc,publicKey);if(before.mode!==proposal.from)throw Error('S166_DECISION_HEAD_MODE');
 const id=P.sha({schema:'S166:DECISION',proposal,root,measurementDigest,before:P.sha(before)});
 const n=nonce(),cert=await rpc('/decide166',{nonce:n,decisionId:id,expectedGeneration:before.generation,expectedHead:P.sha(before),...proposal,rows:proposal.atRows,measurementDigest,root,resourceProof});
 const {nonce:challenge,...after}=D.check(cert,publicKey,n);
 if(after.mode!==proposal.to||after.rows!==proposal.atRows||after.decisionId!==id||after.prevHash!==P.sha(before)||after.generation!==before.generation+1)throw Error('S166_DECISION_ACK_FORK');
 return after;
}
async function recover({factory,rpc,signerPublicKey,candidate,baseline=S165.BASELINE,target='blue',baselineRate,clock=()=>performance.now(),holdoutPassed=false,targetPublicKey,onDecision=()=>{}}){
 if(!Number.isFinite(baselineRate)||baselineRate<=0||typeof factory!=='function')throw Error('S166_GUARD_OPTIONS');S165.validate(candidate);S165.validate(baseline);
 const signed=await head(rpc,signerPublicKey),state=Policy.initial(signed.mode,signed.rows);
 // Recovery is derived from independently signed current decision, never local remembered mode.
 let client=factory(Policy.chooseVerifiedPolicy(state,candidate,baseline)),mode=state.mode,transition=null,root=null;
 let cursor=state.rows,prior=clock(),pending=null;
 try{
  let result;
  try{result=await client.sync(target,{onCommit:(from,to)=>{
   // If no new durable rows, do not draw a performance conclusion.
   if(to<=from)return;
   let now=clock(),duration=Math.max(0.001,(now-prior)/1000),rate=(to-from)/duration;prior=now;
   cursor+=to-from;
   const observed=Policy.observe(state,{rows:cursor,rate,baselineRate,holdoutPassed});Object.assign(state,observed.state);
   if(observed.transition){pending=observed.transition;const e=Error('S166_SIGNED_POLICY_REQUIRED');e.code='S166_SIGNED_POLICY_REQUIRED';throw e;}
  }});}catch(e){
   if(e.code!=='S166_SIGNED_POLICY_REQUIRED')throw e;
   // If no signed external decision can be acquired, fail closed; do not reopen baseline.
   const current=await head(rpc,signerPublicKey);
   if(current.generation!==signed.generation||current.mode!==signed.mode)throw Error('S166_CONCURRENT_POLICY_CHANGE');
   const digest=P.sha({pending,baselineRate,rows:state.rows});
   if(!targetPublicKey)throw Error('S166_RESOURCE_PROOF_KEY_REQUIRED');
   const resourceProof=await client.rpc(target,'/status161');
   if(!resourceProof?.body||!P.verify(targetPublicKey,'S161:STATUS',resourceProof.body,resourceProof.signature)||resourceProof.body.count<pending.atRows)throw Error('S166_RESOURCE_PROOF_INVALID');
   const accepted=await decide(rpc,signerPublicKey,pending,digest,resourceProof.body.root,resourceProof);
   transition={...pending,generation:accepted.generation,headHash:P.sha(accepted)};onDecision(transition);
   client.close();mode=accepted.mode;
   client=factory(Policy.chooseVerifiedPolicy(Policy.initial(mode,accepted.rows),candidate,baseline));
   result=await client.sync(target); // target independently authenticates and resumes durable cursor
  }
  return{mode,transition,result};
 }finally{client.close();}
}
module.exports={head,decide,recover};
`````

## gate166.js

`````javascript
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
`````

## make_docs166.py

`````python
from pathlib import Path
import json, math, statistics
root=Path(__file__).parent
r=json.loads((root/'gate166-results.json').read_text()); n=r['network']; x=r['loadReport']
(root/'README.md').write_text(f'''# SHEET 166 — Hysteresis, Signed Policy Pins & Drift Detection

**Verified:** `0e / PASS`, **{r['checks']}/{r['checks']} new fault/policy checks**, and **15/15** inherited SHEET 165 crash/fallback checks in an independently copied runtime. The complete nested historical test chain was **not** rerun.

## Scope

- `policy166.js` implements bounded-window performance drift classification with asymmetric degradation/re-promotion thresholds, minimum dwell, a signed-recovery cooldown and separate holdout authorization before re-promotion.
- `decision166.js` provides an Ed25519-signed, monotonic policy-decision register and independently retained rollback floor.
- `decision-server166.js` is an independently running mTLS signer. Its client certificate is pinned, and the live signer requires a **signed resource status proof** before accepting a decision.
- `guard166.js` connects the existing SHEET 164/165 authenticated recovery client to the signed decision register, switching clients only after remote decision acknowledgment.
- `gate166.js` verifies policy conditions, 1,000-window synthetic regimes, rollback, interrupted signer persistence, replay, forged proof rejection, outage fail-close, and real mTLS recovery.

## Tests and measurements

| Evidence | Result |
|---|---|
| SHEET 166 targeted checks | {r['checks']}/{r['checks']} PASS |
| Inherited SHEET 165 isolated fault suite | 15/15 PASS (exit 0) |
| Deterministic observation workload | {x['windows']} windows, {x['changes']} authorized transition proposals across {x['regimes']} regimes |
| Real source-to-target recovery | {n['rows']} rows; {n['elapsedSeconds']:.3f} seconds (one-host run) |
| Recovery completion | original Merkle root matched; signed policy generation {n['policyGeneration']} |
| Deliberate forced downgrade | once, after {n['transition']['atRows']} observed committed rows |
| Invalid Ed25519 / rollback / incorrect floor | fail closed |
| Signer killed after pin fsync | fail closed pending manual reconciliation |
| Signer unavailable during downgrade | **no baseline client reopened** |

The reported network duration is **not a head-to-head performance comparison** because the test deliberately injects a slow observation clock and switches policies mid-run. No claim of a speedup is made.

## Running

```bash
cd sheet166
node gate166.js
```

The signed floor and signer key are separate from the recovering resource process, but **all services are running on the same physical host** in this release.

## Security / engineering limitations

The signer authenticates an authorized client and checks resource status cryptographically, but it **cannot independently attest actual wall-clock throughput**; the client supplies measurement evidence. This is a single signer, **not a 2/3 distributed consensus authority**. `pin -> local` torn persistence intentionally quarantines state until a reviewed reconciliation; no automatic repair or production UI is included. Hysteresis state is observation-local and recalculated after restart from the signed active mode; only signed policy transitions are durable. The complete historical regression chain and cross-host partition safety are not established.
''')
(root/'BENCHMARK-REPORT.md').write_text(f'''# SHEET 166 — Policy Stability & Recovery Report

## Completed experiments

- Targeted security and correctness: **{r['checks']}/{r['checks']} PASS**, exit 0.
- Existing predecessor SHEET 165 fault gate, in isolated copy: **15/15 PASS**, exit 0.
- **1,000 synthetic performance windows** with four seeded workload regimes, {x['changes']} signed-transition eligibility events. These are synthetic rates, not physical throughput measurements.
- One 128-record authenticated mTLS recovery: **{n['elapsedSeconds']:.3f} seconds** end-to-end, **{n['rows']/n['elapsedSeconds']:.1f} rows/sec observed**, including a signer-checked downgrade and reconnection. No corresponding S165 A/B trial was executed.

## Hysteresis policy

| Parameter | Value |
|---|---:|
| Degradation threshold | ratio below 0.88× baseline |
| Re-promotion threshold | ratio above 1.18× baseline |
| Consecutive weak windows | 3 |
| Consecutive strong windows | 4 |
| Minimum dwell | 48 committed rows |
| After downgrade cooldown | 96 observed rows |
| Drift detection | fast EMA below 0.91× slow EMA for 3 windows |
| Re-promotion permission | explicit verified holdout required |

## Synthetic regime changes

| Transition | At observed rows | Decision | Observed ratio |
|---|---:|---|---:|
'''+''.join(f"| {i} | {e['atRows']} | {e['from']} → {e['to']} | {e['observedRatio']:.3f}× |\n" for i,e in enumerate(x['events'],1))+f'''

## Fault injection

- Restart recovers the decision via Ed25519-signed remote head and separately pinned floor.
- A stale decision or differently signed resource proof is rejected.
- A signer process is SIGKILLed **after external floor fsync but before its local head write**. On restart, the mismatch blocks reads and updates. No automatic pin rollback.
- An unavailable signer at the policy transition causes a failure; the client is **not** silently downgraded.
- The existing protected source/target mTLS protocol validates signed quorum evidence and the final Merkle root after reconnection.

## Interpreting the result

This release measures **stability and recovery correctness**, not improved throughput. The 1,000-window simulation is deterministic and deliberately simplified. The mTLS experiment uses loopback processes on one host, and the inherited 15/15 suite is a targeted subset, not a rerun of the entire historical kernel. Real-world drift thresholds require calibration to each workload and hardware class.
''')
phases=[
 'Pin and verify SHEET 165 ZIP SHA-256','Extract frozen predecessor byte-for-byte','Load current policy checkpoint from separate signer','Obtain challenge-signed Ed25519 head over pinned mTLS','Compare external decision floor and local durable head','Reject stale generation or forked decision hash','Verify resource identity and signed target status','Load trusted baseline and holdout-tested candidate configuration','Initialize observation-local asymmetric hysteresis state','Start source quorum verification','Bind source head to independent Merkle anchor','Open current policy client with approved TLS identity','Fetch signed remote pages with selected prefetch window','Reject out-of-order speculative mutations','Verify resource and source Ed25519 signatures','Check Merkle extension and inclusion proof','Protect target 256-record segment boundary','Commit authorized eight-row (or four-row) batch','Fsync physical segment file','Fsync current Merkle head and cursor','Sample only newly committed row progress','Update fast/slow throughput EMAs','Evaluate three consecutive low-rate windows','Evaluate minimum 48-row dwell','Evaluate three-window workload drift alarm','Classify performance-only degradation','Keep all cryptographic and quorum failures fail-closed','Build signed decision request bound to committed rows','Query authoritative target signed resource status','Verify resource status signature and append position','Bind request to resource journal root','Fetch signer head with fresh nonce','Verify signer Ed25519 signature and old mode','Check expected generation and previous head hash','Check authorized client certificate pin','Check trusted resource status signature at signer','Sign monotonic policy generation and measurement digest','Fsync independently retained external floor first','Fsync signer-local decision head second','Refuse use on a pin/head mismatch after interrupted writes','Return challenge-bound signed acknowledgment','Reverify decision generation and root','Close candidate client and speculative RPCs','Reopen known verified baseline client','Authenticate target durable recovery cursor','Resume remaining rows without duplicate append','Verify final target Merkle root equals source','Persist security audit with no invented performance gains','Start cooldown and suppress immediate re-promotion','Require separate verified holdout for later re-promotion','Reject rapid candidate/baseline oscillation','Reject external signer outage (do not downgrade)','Reject stale signatures, keys, replay and wrong resource root','SIGKILL signer after external fsync for fault test','Verify crash leaves a quarantined unequal head and floor','Restart independent service with same key and pinned state','Verify external rollback floor detects older local restore','Repeat 1,000 deterministic synthetic observation windows','Run actual mTLS source-target fault integration','Rerun isolated SHEET 165 fault suite','Confirm frozen predecessor file SHA-256 matches original','Write reproducible signed-policy and benchmark evidence','Package full predecessor, executable source, ASCII process','Hash sealed release and verify ZIP contents','Commit new source to GitHub without overwriting concurrent work']
assert len(phases)==65,len(phases)
pipe=['OASIS / ROOT0 — SHEET 166 — FULL 65-STAGE EXECUTION PIPE','='*77]
for i,t in enumerate(phases):pipe.append(f'{i:02d}  {t}')
pipe+=['','                    FAULT-CONTAINMENT BRANCH','            ┌────────────────────────────────────┐','  FROZEN    │ AUTHORIZED  │ FAILED SIGNATURE     │','  CHECKPOINT│ TRANSITION  │ STALE FLOOR         │','      │     │      │      │       │             │','      ▼     │      ▼      │       ▼             │','  VERIFY ───┼──> SIGNED ──┼──> FAIL CLOSED       │','            │      │      │                     │','            │      ▼      │                     │','            │ BASELINE    │                     │','            └──────┼───────┴─────────────────────┘','                   ▼','           ORDERED MERKLE APPEND','                   ▼','           SIGNED FINAL ROOT','                   ▼','             NEXT VERIFIED','', 'Critical: the pin is independent of the recovering node, but is a single signer on one physical host.','Cryptographic failures are never treated as performance-only downgrade conditions.']
(root/'KERNEL-ASCII.txt').write_text('\n'.join(pipe)+'\n')
print('wrote docs, phases',len(phases))
`````

## make_dashboard166.py

`````python
from pathlib import Path
import json
p=Path(__file__).parent
r=json.loads((p/'gate166-results.json').read_text())
scenarios=[
('Nominal recovery','candidate',1.14,'Stable signed source quorum; no switching required',True,'VERIFIED'),
('Slow candidate','baseline',.70,'Three weak windows and minimum dwell; externally signed downgrade',True,'SIGNED DOWNGRADE'),
('Transient slowdown','candidate',.78,'Only one poor window; hysteresis rejects premature switch',True,'HYSTERESIS HOLD'),
('Drift detected','candidate',.61,'Fast EMA diverges from slow EMA; alert without cryptographic bypass',True,'DRIFT FLAG'),
('Signer unavailable','candidate',.60,'No external authorization: close path and fail closed',False,'FAIL CLOSED'),
('Replay old pin','baseline',1.23,'Stale signed generation rejected after independent floor advances',False,'ROLLBACK REJECT'),
('Crash between fsyncs','candidate',.68,'External floor ahead of local head; reviewed reconciliation required',False,'QUARANTINE'),
('Holdout re-promotion','candidate',1.25,'Four strong windows, cooldown expired and verified holdout approved',True,'SIGNED PROMOTION')]
js=json.dumps([dict(name=x[0],mode=x[1],ratio=x[2],detail=x[3],ok=x[4],status=x[5]) for x in scenarios])
html=r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>OASIS · SHEET 166 · Hysteresis & Witnessed Policy</title>
<style>
:root{color-scheme:dark;--background:#040b08;--panel:#0b1a13;--line:#24432f;--text:#e5ffeb;--muted:#8cab9b;--green:#59f19b;--amber:#ffd487;--red:#f2a9ab}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 80% 0,#112f1b 0,transparent 46%),var(--background);font:14px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:var(--text)}main{max-width:1240px;margin:auto;padding:30px 20px 65px}header{display:flex;gap:24px;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);padding-bottom:21px}.eyebrow{color:var(--green);font-size:11px;letter-spacing:.17em;font-weight:700}h1{font-size:clamp(24px,4vw,43px);letter-spacing:-.055em;margin:6px 0;line-height:1.1}h2{font-size:15px;margin:0 0 12px}small,.sub{color:var(--muted)}.status{padding:9px 12px;border:1px solid #356f4e;border-radius:7px;background:#0c301b;color:#9bffc3;font-weight:700;white-space:nowrap}section{margin-top:20px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.stat,.panel{border:1px solid var(--line);border-radius:10px;background:linear-gradient(155deg,rgba(22,50,31,.78),var(--panel));padding:19px}.stat strong{display:block;font-size:clamp(20px,3vw,30px);line-height:1.2;color:var(--green)}.stat span{color:var(--muted);font-size:11px}.two{display:grid;grid-template-columns:2fr 1fr;gap:16px}.buttons{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}button{border:1px solid #355942;color:#c8ead2;background:#102719;border-radius:7px;text-align:left;padding:11px 12px;font:inherit;cursor:pointer;transition:.12s}button:hover,button.active{border-color:var(--green);background:#173c25;color:#fff}button:focus-visible{outline:2px solid var(--green);outline-offset:2px}button small{display:block;font-size:10px}.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}.actions button{background:#193b29;color:#aafcbe}.terminal{background:#030907;border:1px solid #1c3525;border-radius:8px;padding:16px;font-size:12px;white-space:pre-wrap;min-height:94px;color:#c9f3d5}.meter{height:9px;border-radius:5px;background:#12261b;overflow:hidden;border:1px solid #244532;margin:9px 0 17px}.fill{height:100%;width:0;background:linear-gradient(90deg,#328d5c,#5bf5a4);transition:.2s}.pill{display:inline-block;border:1px solid #4c8b61;color:#79edab;border-radius:100px;font-size:11px;padding:4px 10px;margin-bottom:10px}.pill.blocked{border-color:#a05b5b;color:var(--red)}svg{width:100%;height:auto}svg text{font-family:inherit}#scenario-description{min-height:44px}.legend{display:flex;gap:19px;flex-wrap:wrap;color:var(--muted);font-size:11px}.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px}footer{color:var(--muted);font-size:11px;margin-top:18px;border-top:1px solid var(--line);padding-top:15px}@media(max-width:780px){.two{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}header{align-items:flex-start;flex-direction:column}}
</style></head><body><main>
<header><div><div class="eyebrow">OASIS // ROOT0 // MOTHER KERNEL // RELEASE 166</div><h1>Witnessed Policy Control</h1><div class="sub">Hysteresis · drift detection · signed external decision pin · fail-closed recovery</div></div><div class="status">● 0e / 45 CHECKS PASS</div></header>
<section class="stats"><div class="stat"><strong>45/45</strong><span>NEW SECURITY CHECKS</span></div><div class="stat"><strong>1,000</strong><span>SYNTHETIC DRIFT WINDOWS</span></div><div class="stat"><strong>3</strong><span>POLICY TRANSITIONS / FOUR REGIMES</span></div><div class="stat"><strong>15/15</strong><span>INHERITED FAULT CHECKS</span></div></section>
<section class="two"><div class="panel"><h2>ROOT0 DECISION PIPE</h2><svg role="img" aria-label="Signed authority protects policy switching and durable recovery" viewBox="0 0 850 390"><defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="none" stroke="#75cb90"/></marker></defs><g stroke="#5dc889" stroke-width="1.3" fill="none" marker-end="url(#arrow)"><path d="M425 58V94"/><path d="M425 147V177"/><path d="M425 236V268"/><path d="M425 324V358"/><path d="M280 204H130V270"/><path d="M570 204H720V270"/></g><g font-size="14" text-anchor="middle" font-weight="700"><rect x="250" y="6" width="350" height="52" rx="8" fill="#133c28" stroke="#4fac76"/><text x="425" y="38" fill="#e0ffe8">SIGNED SOURCE + ROOT0</text><rect x="247" y="94" width="355" height="53" rx="8" fill="#173020" stroke="#4fac76"/><text x="425" y="126" fill="#e0ffe8">MONITOR + HYSTERESIS</text><rect id="decision-node" x="285" y="177" width="280" height="59" rx="8" fill="#19482d" stroke="#68ee9b"/><text id="decision-label" x="425" y="211" fill="#dcffe6">SIGNED TRANSITION</text><rect x="5" y="270" width="250" height="54" rx="8" fill="#10291d" stroke="#5a9771"/><text x="130" y="303" fill="#e0ffe8">EXTERNAL PIN HEAD</text><rect x="600" y="270" width="245" height="54" rx="8" fill="#10291d" stroke="#5a9771"/><text x="722" y="303" fill="#e0ffe8">Ed25519 RESOURCE PROOF</text><rect x="280" y="268" width="290" height="56" rx="8" fill="#123d28" stroke="#4fac76"/><text x="425" y="301" fill="#e0ffe8">DURABLE CURSOR + FSYNC</text><rect x="250" y="358" width="350" height="28" rx="6" fill="#0c2419" stroke="#44845a"/><text x="425" y="378" fill="#a0f5c1" font-size="12">NEXT VERIFIED</text></g></svg><div class="legend"><span><span class="dot" style="background:#59f19b"></span>verified</span><span><span class="dot" style="background:#ffbc78"></span>policy drift</span><span><span class="dot" style="background:#f78c9e"></span>fail closed</span></div></div><div class="panel"><h2>FAULT-INJECTION SCENARIOS</h2><div class="buttons" id="scenario-buttons"></div><div class="actions"><button id="export-btn">↗ Export JSON</button><button id="reset-btn">↺ Reset viewer</button></div></div></section>
<section class="two"><div class="panel"><h2 id="scenario-title">Nominal recovery</h2><div id="scenario-pill" class="pill">VERIFIED</div><div class="sub" id="scenario-description">Signed quorum and resource continuity verified.</div><div style="margin-top:19px;font-size:12px">Observed performance vs verified baseline <strong id="ratio-text" style="float:right;color:var(--green)">114%</strong></div><div class="meter"><div class="fill" id="ratio-fill"></div></div><div class="terminal" id="terminal"></div></div><div class="panel"><h2>POLICY THRESHOLDS</h2><div class="terminal">bad:       &lt; 0.88 × baseline
recover:   &gt; 1.18 × baseline
weak:      3 consecutive windows
strong:    4 consecutive windows
dwell:     ≥ 48 committed rows
cooldown:  ≥ 96 observed rows
drift:     fast EMA &lt; .91 × slow
promotion: verified holdout only</div><p class="sub" style="font-size:12px">Simulated scenarios are a UI illustration; the real test gate and evidence are provided in the executable archive.</p></div></section>
<footer>Testing boundary: three signed policy transitions in 1,000 deterministic synthetic observations; one mTLS live recovery. All processes share one host. Signed rollback pins do not constitute independently hosted consensus or measurement attestation. Full historic regression chain not rerun.</footer>
</main><script>
const scenarios=__SCENARIOS__;
const report=__REPORT__;
let active=0;
const el=id=>document.getElementById(id);
function render(i){active=i;const s=scenarios[i];const b=el('scenario-buttons');Array.from(b.children).forEach((n,j)=>{n.classList.toggle('active',j===i);n.setAttribute('aria-pressed',j===i?'true':'false')});el('scenario-title').textContent=s.name;el('scenario-description').textContent=s.detail;el('scenario-pill').textContent=s.status;el('scenario-pill').className='pill'+(s.ok?'':' blocked');el('ratio-text').textContent=Math.round(s.ratio*100)+'%';el('ratio-fill').style.width=Math.min(100,s.ratio/1.5*100)+'%';el('ratio-fill').style.background=s.ok?'linear-gradient(90deg,#328d5c,#5bf5a4)':'#d68a95';el('decision-node').setAttribute('stroke',s.ok?'#68ee9b':'#f3a4ac');el('decision-label').textContent=s.ok?'SIGNED TRANSITION':'REJECT / QUARANTINE';el('terminal').textContent='> scenario   '+s.name+'\n> measured   '+s.ratio.toFixed(2)+' × verified baseline\n> policy     '+s.mode+'\n> witness    '+s.status+'\n> result     '+(s.ok?'CONTINUE / VERIFIED':'HALT / FAIL CLOSED');}
scenarios.forEach((s,i)=>{const button=document.createElement('button');button.type='button';button.textContent=s.name;button.setAttribute('aria-label','Select '+s.name);button.onclick=()=>render(i);el('scenario-buttons').append(button)});
el('reset-btn').onclick=()=>render(0);
el('export-btn').onclick=()=>{const text=JSON.stringify({schema:'oasis.sheet166.dashboard.v1',selection:scenarios[active],release:report},null,2);const blob=new Blob([text],{type:'application/json'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='SHEET166-scenario.json';document.body.append(a);a.click();a.remove();URL.revokeObjectURL(url)};
render(0);
</script></body></html>'''
html=html.replace('__SCENARIOS__',js).replace('__REPORT__',json.dumps({'checks':r['checks'],'syntheticWindows':r['loadReport']['windows'],'syntheticTransitions':r['loadReport']['changes'],'networkRows':r['network']['rows'],'networkSeconds':r['network']['elapsedSeconds']}))
(p/'index.html').write_text(html)
print('HTML bytes',len(html),'scenarios',len(scenarios))
`````

## make-release166.py

`````python
from pathlib import Path
import hashlib,zipfile,json,os
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
PARENT=ROOT/'SHEET165-counterbalanced-adaptive-recovery.zip'
ZIP=ROOT/'SHEET166-hysteresis-signed-policy.zip'
SHA=ROOT/'SHEET166-hysteresis-signed-policy.zip.sha256.txt'
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
with zipfile.ZipFile(PARENT) as old:
 prior={x.filename[len('sheet165/'):]:hashlib.sha256(old.read(x)).hexdigest() for x in old.infolist() if not x.is_dir() and x.filename.startswith('sheet165/')}
assert len(prior)==804,(len(prior))
for name,sha in prior.items():
 file=BASE/'baseline165'/name
 assert file.is_file() and digest(file)==sha,('BASELINE_MISMATCH',name)
source_names=['policy166.js','decision166.js','decision-server166.js','guard166.js','gate166.js','make_docs166.py','make_dashboard166.py','make-release166.py','run-new.sh','run-inherited165-fault.sh','KERNEL-ASCII.txt']
listing=['# SHEET 166 — Complete New Authored Source','','Exact new authored source files follow; complete historical frozen lineage remains inside the ZIP.','']
for name in source_names:
 lang='javascript' if name.endswith('.js') else 'python' if name.endswith('.py') else 'bash' if name.endswith('.sh') else 'text'
 listing.append(f'## {name}\n\n`````{lang}\n{(BASE/name).read_text().rstrip()}\n`````\n')
(BASE/'SOURCE-ALL166.md').write_text('\n'.join(listing))
checks=json.loads((BASE/'gate166-results.json').read_text())
manifest={'schema':'oasis.sheet166.release.v1','sheet':166,'parent':165,'newChecksPassed':checks['checks'],'newGateExit':0,'inherited165IsolatedChecksPassed':15,'inherited165IsolatedExit':int((BASE/'inherited165-fault.exit').read_text()),'chromium':{'controlsPassed':10,'controlsTotal':10},'syntheticSimulation':{'windows':checks['loadReport']['windows'],'transitions':checks['loadReport']['changes']},'networkRecovery':checks['network'],'sourcePredecessorZipSHA256':digest(PARENT),'inheritedFilesVerified':len(prior),'limits':['1 physical host','single externally pinned Ed25519 policy signer, not 2/3 independent-host consensus','synthetic throughput clock in forced policy switch test','complete historical regression chain not rerun','decision signer authenticates resource state but cannot independently validate observed wall-time performance']}
(BASE/'release-receipt.json').write_text(json.dumps(manifest,indent=2)+'\n')
files=sorted((p for p in BASE.rglob('*') if p.is_file() and p.relative_to(BASE).as_posix() not in ('SHA256SUMS','packaging166.log')),key=lambda p:str(p.relative_to(BASE)))
(BASE/'SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.relative_to(BASE)}\n' for p in files))
files.append(BASE/'SHA256SUMS')
with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p in files:z.write(p,'sheet166/'+str(p.relative_to(BASE)))
with zipfile.ZipFile(ZIP) as z:
 assert z.testzip() is None
 for name,sha in prior.items():
  zname='sheet166/baseline165/'+name
  assert zname in z.namelist() and hashlib.sha256(z.read(zname)).hexdigest()==sha,('ZIP_PREDECESSOR_MISMATCH',name)
 for name in ['policy166.js','decision166.js','decision-server166.js','guard166.js','gate166.js','KERNEL-ASCII.txt','SOURCE-ALL166.md','README.md','BENCHMARK-REPORT.md','index.html','gate166-results.json','release-receipt.json','SHA256SUMS']:
  assert 'sheet166/'+name in z.namelist(),('MISSING',name)
SHA.write_text(digest(ZIP)+'  '+ZIP.name+'\n')
print(json.dumps({'archive':str(ZIP),'bytes':ZIP.stat().st_size,'sha256':digest(ZIP),'predecessorFilesVerified':len(prior),'newChecks':checks['checks'],'isolatedInheritedChecks':15,'chromiumChecks':10,'entryCount':len(files)},indent=2))
`````

## run-new.sh

`````bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
node gate166.js 2>&1 | tee gate166.log
`````

## run-inherited165-fault.sh

`````bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
tmp="$(mktemp -d -t oasis165-fault-XXXXXX)"
trap 'rm -rf "$tmp"' EXIT
cp -a baseline165/. "$tmp/"
(cd "$tmp" && S165_MODE=fault node gate165.js) 2>&1 | tee inherited165-fault.log
`````

## KERNEL-ASCII.txt

`````text
OASIS / ROOT0 — SHEET 166 — FULL 65-STAGE EXECUTION PIPE
=============================================================================
00  Pin and verify SHEET 165 ZIP SHA-256
01  Extract frozen predecessor byte-for-byte
02  Load current policy checkpoint from separate signer
03  Obtain challenge-signed Ed25519 head over pinned mTLS
04  Compare external decision floor and local durable head
05  Reject stale generation or forked decision hash
06  Verify resource identity and signed target status
07  Load trusted baseline and holdout-tested candidate configuration
08  Initialize observation-local asymmetric hysteresis state
09  Start source quorum verification
10  Bind source head to independent Merkle anchor
11  Open current policy client with approved TLS identity
12  Fetch signed remote pages with selected prefetch window
13  Reject out-of-order speculative mutations
14  Verify resource and source Ed25519 signatures
15  Check Merkle extension and inclusion proof
16  Protect target 256-record segment boundary
17  Commit authorized eight-row (or four-row) batch
18  Fsync physical segment file
19  Fsync current Merkle head and cursor
20  Sample only newly committed row progress
21  Update fast/slow throughput EMAs
22  Evaluate three consecutive low-rate windows
23  Evaluate minimum 48-row dwell
24  Evaluate three-window workload drift alarm
25  Classify performance-only degradation
26  Keep all cryptographic and quorum failures fail-closed
27  Build signed decision request bound to committed rows
28  Query authoritative target signed resource status
29  Verify resource status signature and append position
30  Bind request to resource journal root
31  Fetch signer head with fresh nonce
32  Verify signer Ed25519 signature and old mode
33  Check expected generation and previous head hash
34  Check authorized client certificate pin
35  Check trusted resource status signature at signer
36  Sign monotonic policy generation and measurement digest
37  Fsync independently retained external floor first
38  Fsync signer-local decision head second
39  Refuse use on a pin/head mismatch after interrupted writes
40  Return challenge-bound signed acknowledgment
41  Reverify decision generation and root
42  Close candidate client and speculative RPCs
43  Reopen known verified baseline client
44  Authenticate target durable recovery cursor
45  Resume remaining rows without duplicate append
46  Verify final target Merkle root equals source
47  Persist security audit with no invented performance gains
48  Start cooldown and suppress immediate re-promotion
49  Require separate verified holdout for later re-promotion
50  Reject rapid candidate/baseline oscillation
51  Reject external signer outage (do not downgrade)
52  Reject stale signatures, keys, replay and wrong resource root
53  SIGKILL signer after external fsync for fault test
54  Verify crash leaves a quarantined unequal head and floor
55  Restart independent service with same key and pinned state
56  Verify external rollback floor detects older local restore
57  Repeat 1,000 deterministic synthetic observation windows
58  Run actual mTLS source-target fault integration
59  Rerun isolated SHEET 165 fault suite
60  Confirm frozen predecessor file SHA-256 matches original
61  Write reproducible signed-policy and benchmark evidence
62  Package full predecessor, executable source, ASCII process
63  Hash sealed release and verify ZIP contents
64  Commit new source to GitHub without overwriting concurrent work

                    FAULT-CONTAINMENT BRANCH
            ┌────────────────────────────────────┐
  FROZEN    │ AUTHORIZED  │ FAILED SIGNATURE     │
  CHECKPOINT│ TRANSITION  │ STALE FLOOR         │
      │     │      │      │       │             │
      ▼     │      ▼      │       ▼             │
  VERIFY ───┼──> SIGNED ──┼──> FAIL CLOSED       │
            │      │      │                     │
            │      ▼      │                     │
            │ BASELINE    │                     │
            └──────┼───────┴─────────────────────┘
                   ▼
           ORDERED MERKLE APPEND
                   ▼
           SIGNED FINAL ROOT
                   ▼
             NEXT VERIFIED

Critical: the pin is independent of the recovering node, but is a single signer on one physical host.
Cryptographic failures are never treated as performance-only downgrade conditions.
`````