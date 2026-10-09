#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const P=require('./baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./baseline156/witness-verify156');const V=require('./catchup-verify157');const C=require('./catchup157');
const root=fs.mkdtempSync(path.join(os.tmpdir(),'sheet157-')),f=(...a)=>path.join(root,...a),openssl=(...a)=>cp.execFileSync('openssl',a,{cwd:root,stdio:'pipe'});
let n=0;const ok=(name,fn)=>{fn();console.log('PASS',++n,name);};const step=async(name,fn)=>{await fn();console.log('PASS',++n,name);};const bad=async(name,fn,regex)=>step(name,async()=>assert.rejects(fn,regex));
function cert(id){openssl('req','-new','-newkey','rsa:2048','-nodes','-keyout',id+'.key','-out',id+'.csr','-subj','/CN=localhost');fs.writeFileSync(f(id+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=clientAuth,serverAuth\n');openssl('x509','-req','-in',id+'.csr','-CA','ca.crt','-CAkey','ca.key','-CAcreateserial','-out',id+'.crt','-days','2','-sha256','-extfile',id+'.ext');return{key:f(id+'.key'),cert:f(id+'.crt'),ca:f('ca.crt'),certPin:new crypto.X509Certificate(fs.readFileSync(f(id+'.crt'))).fingerprint256.replaceAll(':','').toLowerCase()};}
function keys(id){const pair=crypto.generateKeyPairSync('ed25519'),priv=f(id+'.priv'),pub=f(id+'.pub');fs.writeFileSync(priv,pair.privateKey.export({format:'pem',type:'pkcs8'}));fs.writeFileSync(pub,pair.publicKey.export({format:'pem',type:'spki'}));return{privateKey:pair.privateKey,publicKey:pair.publicKey,priv,pub};}
const children=[];
async function spawn(script,cfg,id){const config=f('cfg-'+id+'.json');P.atomic(config,cfg);const proc=cp.fork(path.join(__dirname,script),[],{env:{...process.env,S157_WITNESS_CONFIG:config,S156_FLOOR_CONFIG:config},stdio:['ignore','pipe','pipe','ipc']});let errors='';proc.on('error',()=>{});proc.stderr.on('data',b=>errors+=b);const port=await new Promise((res,rej)=>{const t=setTimeout(()=>rej(Error('START_TIMEOUT '+id+' '+errors)),15000);proc.once('message',m=>{clearTimeout(t);res(m.port);});proc.once('exit',code=>{clearTimeout(t);rej(Error('START_FAILED '+id+' '+code+' '+errors));});});const x={proc,port,id,errors:()=>errors};children.push(x);return x;}
async function stop(x){if(!x||x.proc.exitCode!==null||x.proc.signalCode!==null)return;await new Promise(done=>{const t=setTimeout(()=>{x.proc.kill('SIGKILL');done();},2000);x.proc.once('exit',()=>{clearTimeout(t);done();});if(x.proc.connected){try{x.proc.send('stop',err=>{if(err){x.proc.kill('SIGKILL');clearTimeout(t);done();}});}catch{ x.proc.kill('SIGKILL');clearTimeout(t);done();}}else{x.proc.kill('SIGKILL');clearTimeout(t);done();}});}
(async()=>{try{
 openssl('req','-x509','-new','-newkey','rsa:2048','-nodes','-keyout','ca.key','-out','ca.crt','-days','2','-subj','/CN=S157-TEST');
 const ids=Object.fromEntries(['proxy','wred','wblue','wgreen','rogue'].map(id=>[id,cert(id)]));
 const witnessKeys=Object.fromEntries(['wred','wblue','wgreen'].map(id=>[id,keys(id)]));
 const finalKeys=Object.fromEntries(['red','blue'].map(id=>[id,keys('final-'+id)]));
 const pubs=Object.fromEntries(Object.entries(witnessKeys).map(([id,k])=>[id,k.publicKey]));
 const witnessPublicKeys=Object.fromEntries(Object.entries(witnessKeys).map(([id,k])=>[id,k.pub]));
 const finalPublicKeys=Object.fromEntries(Object.entries(finalKeys).map(([id,k])=>[id,k.pub]));
 const config=Object.fromEntries(Object.keys(witnessKeys).map(id=>[id,{id,...ids[id],signKey:witnessKeys[id].priv,stateFile:f(id,'state.json'),proxyPin:ids.proxy.certPin,witnessPublicKeys,finalityPublicKeys:finalPublicKeys}]));
 const nodes={};for(const id of Object.keys(config))nodes[id]=await spawn('witness157.js',config[id],id);
 const endpoints=()=>Object.fromEntries(Object.keys(nodes).map(id=>[id,{port:nodes[id].port,serverPin:ids[id].certPin}]));
 const api=()=>C.make({identity:ids.proxy,witnesses:endpoints(),publicKeys:pubs});
 const rpc=(id,url,body={})=>api().rpc(id,url,body);
 const readState=id=>P.load(config[id].stateFile);
 const record=(slot,prev,tag)=>W.normalize({slot,prev,intentDigest:P.sha('intent'+tag),snapshotDigest:P.sha('snapshot'+tag),receiptHash:P.sha('receipt'+tag)});
 const finalVotes=r=>['red','blue'].map(id=>{const body={nodeId:id,slot:r.slot,prevPinDigest:r.prev,intentDigest:r.intentDigest,snapshotDigest:r.snapshotDigest,receiptHash:r.receiptHash,phase:'final'};return{body,signature:P.sign(finalKeys[id].privateKey,'S155:FINAL',body)};});
 const prepare=async(id,r)=>rpc(id,'/prepare',{record:r,finalVotes:finalVotes(r)});
 const commit=async(id,r,votes)=>rpc(id,'/commit',{record:r,preparedVotes:votes});
 ok('three TLS-pinned independent witness identities',()=>assert.equal(Object.keys(nodes).length,3));
 ok('genesis hashes match',()=>{for(const id of Object.keys(nodes))assert.equal(readState(id).head,W.ZERO);});
 ok('empty certified history hashes to zero',()=>assert.deepEqual(V.historyState([]),{slot:0,head:W.ZERO}));
 ok('history extension rejects truncation',()=>assert.throws(()=>V.admission({history:[record(1,W.ZERO,'a')],pending:null},[]),/W157_ROLLBACK_NOT_ALLOWED/));
 let prev=W.ZERO;const history=[];
 for(let slot=1;slot<=3;slot++){
  const r=record(slot,prev,'main-'+slot);const votes=[];
  for(const id of ['wred','wgreen'])votes.push(await prepare(id,r));
  if(slot===1)await prepare('wblue',r); // minority prepared but missed the commit acknowledgement
  await commit('wred',r,votes);await commit('wgreen',r,votes);
  history.push(r);prev=r.head;
  ok('quorum committed slot '+slot,()=>{assert.equal(readState('wred').slot,slot);assert.equal(readState('wgreen').slot,slot);});
 }
 ok('minority lags with durable pending prepare',()=>{const b=readState('wblue');assert.equal(b.slot,0);assert.equal(b.pending.head,history[0].head);});
 await step('quorum-certified three-slot catchup resolves matching pending',async()=>{const r=await api().repair('wblue');assert.equal(r.body.slot,3);});
 ok('installed minority history matches exactly',()=>assert.deepEqual(readState('wblue').history,history));
 ok('minority pending cleared only after certified install',()=>assert.equal(readState('wblue').pending,null));
 ok('minority history high-water equals majority',()=>assert.equal(readState('wblue').head,prev));
 await step('catchup repeated is idempotent',async()=>assert.equal((await api().repair('wblue')).body.slot,3));
 await stop(nodes.wblue);nodes.wblue=await spawn('witness157.js',config.wblue,'wblue-restart');
 await step('minority restart retains committed certified history',async()=>assert.equal((await rpc('wblue','/read',{nonce:crypto.randomBytes(20).toString('hex')})).body.slot,3));
 const nonce=crypto.randomBytes(20).toString('hex');const challenge=await rpc('wblue','/challenge',{});
 const responses=await Promise.all(['wred','wgreen'].map(id=>rpc(id,'/read',{nonce:challenge.body.nonce})));const exported=await rpc('wred','/export',{nonce:challenge.body.nonce});
 const packet={nonce:challenge.body.nonce,head:{slot:3,head:prev},heads:responses,exported};
 ok('valid quorum package includes signed history',()=>assert.equal(V.certify(packet.head,packet.heads,packet.exported,packet.nonce,pubs).length,3));
 await bad('signed-head replay under different nonce blocked',()=>rpc('wblue','/catchup',{...packet,nonce:'e'.repeat(40)}),/W157_CHALLENGE_EXPIRED_OR_REPLAY/);
 await bad('forged witness-head signature blocked',()=>rpc('wblue','/catchup',{...packet,heads:[{...responses[0],signature:'AAAA'},responses[1]]}),/W157_MAJORITY_HEAD_INVALID/);
 await bad('duplicate witness signatures cannot fake quorum',()=>rpc('wblue','/catchup',{...packet,heads:[responses[0],responses[0]]}),/W157_MAJORITY_HEAD_INVALID/);
 await bad('unsigned export cannot rewrite the journal',()=>rpc('wblue','/catchup',{...packet,exported:{...exported,signature:'AAAA'}}),/W157_EXPORT_INVALID/);
 await bad('altered signed export history rejected',()=>rpc('wblue','/catchup',{...packet,exported:{...exported,body:{...exported.body,history:[]}}}),/W157_EXPORT_INVALID/);
 await step('one-time challenge is consumed on successful install',async()=>assert.equal((await rpc('wblue','/catchup',packet)).body.slot,3));
 await bad('replay of already used challenge fails',()=>rpc('wblue','/catchup',packet),/W157_CHALLENGE_EXPIRED_OR_REPLAY/);
 await bad('untrusted TLS client cannot read witness journal',()=>P.rpc({...ids.rogue,...endpoints().wblue},'/export',{nonce}),/TLS_PEER_NOT_PINNED/);
 ok('journal prefix fork never accepted',()=>assert.throws(()=>V.admission({history:[record(1,W.ZERO,'left')],pending:null},[record(1,W.ZERO,'right')]),/W157_FORK_QUARANTINE/));
 ok('pending conflict never implicitly discarded',()=>assert.throws(()=>V.admission({history:[],pending:record(1,W.ZERO,'wrong')},[history[0]]),/W157_CONFLICTING_PENDING_QUARANTINE/));
 ok('pending matching certified commit may reconcile',()=>V.admission({history:[],pending:history[0]},history));
 ok('history proof cannot skip slots',()=>assert.throws(()=>V.historyState([record(2,W.ZERO,'skip')]),/W157_HISTORY_INVALID/));
 ok('history proof cannot splice different prev hash',()=>assert.throws(()=>V.historyState([history[0],record(2,W.ZERO,'splice')]),/W157_HISTORY_INVALID/));
 ok('history proof rejects injected record properties',()=>assert.throws(()=>V.historyState([{...history[0],hidden:'bad'}]),/W157_HISTORY_INVALID/));
 ok('history proof rejects oversized exports',()=>assert.throws(()=>V.historyState(Array(257).fill(history[0])),/W157_HISTORY_SIZE_BOUND/));
 // A conflicting prepared minority cannot be "repaired" by coercing it to abandon its signed promise.
 const r4=record(4,prev,'slot4');const allVotes=await Promise.all(['wred','wblue','wgreen'].map(id=>prepare(id,r4)));
 await commit('wred',r4,allVotes);await commit('wgreen',r4,allVotes);
 ok('fourth slot committed by majority, third witness pending',()=>assert.equal(readState('wblue').pending.slot,4));
 await step('matching pending slot four is reconciled after real majority commit',async()=>assert.equal((await api().repair('wblue')).body.slot,4));
 const r5a=record(5,r4.head,'version-A');const r5b=record(5,r4.head,'version-B');
 const vA=await Promise.all(['wred','wgreen'].map(id=>prepare(id,r5a)));
 await prepare('wblue',r5b);
 await commit('wred',r5a,vA);await commit('wgreen',r5a,vA);
 await bad('conflicting pending minority quarantines and refuses overwrite',()=>api().repair('wblue'),/W157_CONFLICTING_PENDING_QUARANTINE/);
 ok('conflicting minority pending remains durable',()=>assert.equal(readState('wblue').pending.head,r5b.head));
 await stop(nodes.wblue);nodes.wblue=await spawn('witness157.js',config.wblue,'wblue-conflict-restart');
 await bad('quarantine survives restart',()=>api().repair('wblue'),/W157_CONFLICTING_PENDING_QUARANTINE/);
 // One peer lost: cannot prove a fresh 2-of-3 certified target without the lagging target's own vote.
 await stop(nodes.wgreen);
 await bad('one survivor cannot certify minority catchup',()=>api().repair('wblue'),/W157_CATCHUP_NO_MAJORITY/);
 nodes.wgreen=await spawn('witness157.js',config.wgreen,'wgreen-restart');
 await step('majority heads survive one witness process restart',async()=>{const a=await Promise.all(['wred','wgreen'].map(id=>rpc(id,'/read',{nonce:crypto.randomBytes(20).toString('hex')})));assert.equal(a[0].body.head,a[1].body.head);});
 // Install survives an abrupt exit after fsync and rename, before the RPC reply is emitted.
 const recoveredState=structuredClone(readState('wblue'));recoveredState.pending=null;recoveredState.slot=4;recoveredState.history=history.concat(r4);recoveredState.head=r4.head;recoveredState.challenge=null;
 await stop(nodes.wblue);P.atomic(config.wblue.stateFile,recoveredState);
 config.wblue.crashAfterInstall=true;config.wblue.crashMarker=f('crash157.once');
 nodes.wblue=await spawn('witness157.js',config.wblue,'wblue-crash');
 await bad('crash after durable install drops acknowledgement',()=>api().repair('wblue'),/socket hang up|ECONNRESET|RPC_TIMEOUT/);
 ok('crashed witness saved slot-five history durably',()=>assert.equal(readState('wblue').slot,5));
 await stop(nodes.wblue);nodes.wblue=await spawn('witness157.js',config.wblue,'wblue-aftercrash');
 await step('retry after restarted witness is idempotent',async()=>assert.equal((await api().repair('wblue')).body.slot,5));
 ok('restarted witness cannot regress below certified floor',()=>assert.equal(readState('wblue').head,r5a.head));
 const report={schema:'oasis.sheet157.gate.v1',checks:n,passed:true,witnessProcesses:3,certifiedSlots:5,crashAfterDurableInstall:true,conflictingPendingQuarantined:true,quorumFreshNonce:true,physicalHosts:1,limitations:['bounded 256-record history export; larger histories need paginated authenticated proofs','all mTLS services run on one host','quarantined conflicting prepare requires external reviewed resolution','does not establish Byzantine multi-host safety','S142 intermittent inherited timing test']};
 fs.writeFileSync(path.join(__dirname,'new-test-report.json'),JSON.stringify(report,null,2)+'\n');
 console.log(`SHEET157 NEW PASS ${n}/${n}`);
}catch(e){console.error(`SHEET157 FAILURE after ${n}`,e.stack||e);process.exitCode=1;}finally{for(const c of children.reverse())await stop(c).catch(()=>{});fs.rmSync(root,{recursive:true,force:true});}})();
