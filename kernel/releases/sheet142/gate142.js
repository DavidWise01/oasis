#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),https=require('node:https'),cp=require('node:child_process');
const M=require('./baseline141/baseline140/membership140'),F=require('./baseline141/baseline140/baseline139/fleet139');
const W=require('./baseline141/baseline140/baseline139/baseline138/baseline137/baseline136/trust136');
const G=require('./baseline141/fencing141'); const S=require('./serial142');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'sheet142-'));const file=n=>path.join(tmp,n);
const pkey=()=>crypto.generateKeyPairSync('ed25519');const priv=k=>k.privateKey.export({format:'pem',type:'pkcs8'}),pub=k=>k.publicKey.export({format:'pem',type:'spki'});
const keys=Object.fromEntries(['amber','blue','green','red'].map(id=>[id,pkey()])),pins=Object.fromEntries(Object.entries(keys).map(([id,k])=>[id,pub(k)]));
const old=['blue','green','red'],next=['amber','blue','red'];const subset=ids=>Object.fromEntries(ids.map(x=>[x,pins[x]]));
const operators=Object.fromEntries(['op-a','op-b','op-c'].map(id=>[id,pkey()]));const opPins=Object.fromEntries(Object.entries(operators).map(([id,k])=>[id,pub(k)]));
const now=Date.now(),state=file('membership.json'),oldFleet=file('old-fleet.json'),newFleet=file('new-fleet.json');
const sign=(key,domain,body)=>M.sign(priv(key),domain,body);
const calls=[];let count=0;function ok(label,fn){fn();calls.push(label);count++;console.log('PASS',count,label);}async function asyncOk(label,fn){await fn();calls.push(label);count++;console.log('PASS',count,label);}const rejects=(p,re)=>assert.rejects(p,re);
function setupFleet(dest,ids){const b={schema:'oasis.sheet138.custody-policy.v1',sequence:1,previousHash:W.ZERO,revokedOperators:[],revokedHosts:[],enrollments:{},expiresAt:Date.now()+3600000};const policy={body:b,signatures:['op-a','op-b'].map(id=>({id,signature:W.sign(priv(operators[id]),'sheet138-custody-policy-v1',b)}))};F.stage(dest,policy,ids,opPins,subset(ids));for(const nodeId of ids){const a={schema:'oasis.sheet139.custody-ack-body.v1',nodeId,sequence:1,policyHash:W.sha(b),expiresAt:b.expiresAt,issuedAt:Date.now()};F.ingest(dest,{schema:'oasis.sheet139.custody-ack.v1',body:a,signature:W.sign(priv(keys[nodeId]),'sheet139-custody-ack-v1',a)},subset(ids));}return F.assertReady(dest,subset(ids),{requiredNodes:ids});}
function openssl(...args){cp.execFileSync('openssl',args,{cwd:tmp,stdio:'pipe'});}
function tlsCert(name,{otherCA=false}={}){const ca=otherCA?'evilca':'ca';openssl('req','-x509','-newkey','rsa:2048','-nodes','-days','1','-subj',`/CN=${ca}`,'-keyout',file(ca+'.key'),'-out',file(ca+'.crt'));// only call for base CA once
}
function makeSignedCert(name,ca='ca'){
 openssl('req','-newkey','rsa:2048','-nodes','-subj',`/CN=${name}`,'-keyout',file(name+'.key'),'-out',file(name+'.csr'));
 fs.writeFileSync(file(name+'.ext'),'subjectAltName=DNS:localhost,IP:127.0.0.1\nextendedKeyUsage=serverAuth,clientAuth\n');
 openssl('x509','-req','-in',file(name+'.csr'),'-CA',file(ca+'.crt'),'-CAkey',file(ca+'.key'),'-CAcreateserial','-out',file(name+'.crt'),'-days','1','-sha256','-extfile',file(name+'.ext'));
 return {ca:file(ca+'.crt'),key:file(name+'.key'),cert:file(name+'.crt')};
}
async function child(script,config){const configFile=file('config-'+Math.random().toString(16).slice(2)+'.json');fs.writeFileSync(configFile,JSON.stringify(config));const proc=cp.fork(path.join(__dirname,script),[],{env:{...process.env,SHEET142_CONFIG:configFile},stdio:['ignore','pipe','pipe','ipc']});let errs='';proc.stderr.on('data',c=>errs+=c.toString());
 const port=await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('PROCESS_TIMEOUT '+script+' '+errs)),5000);proc.once('message',m=>{clearTimeout(timeout);resolve(m.port);});proc.once('exit',c=>{clearTimeout(timeout);reject(Error('PROCESS_EARLY_EXIT '+c+' '+errs));});});return {proc,port,configFile};}
async function stop(s){if(!s||s.proc.exitCode!==null||s.proc.signalCode!==null)return;await new Promise(resolve=>{const timer=setTimeout(()=>{s.proc.kill('SIGKILL');resolve();},2000);s.proc.once('exit',()=>{clearTimeout(timer);resolve();});s.proc.send('stop');});}
async function call(port,body,{tls,expectedCode=200}={}){return await new Promise((resolve,reject)=>{const req=https.request({hostname:'127.0.0.1',port,path:'/write',method:'POST',ca:fs.readFileSync(tls.ca),key:fs.readFileSync(tls.key),cert:fs.readFileSync(tls.cert),rejectUnauthorized:true,servername:'localhost',agent:false,timeout:2300},res=>{let text='';res.on('data',c=>text+=c);res.on('end',()=>{try{const obj=JSON.parse(text);if(res.statusCode!==expectedCode)throw Error('STATUS_'+res.statusCode+':'+JSON.stringify(obj));resolve(obj);}catch(e){reject(e);}});});req.on('timeout',()=>req.destroy(Error('CLIENT_TIMEOUT')));req.on('error',reject);req.end(JSON.stringify(body));});}
(async()=>{const procs=[];try{
 setupFleet(oldFleet,old);M.init(state,{fleetFile:oldFleet,members:old,pins:subset(old)});
 const external=pkey(),pinPublic=pub(external),pinFile=file('external-pin.json');
 const updatePin=()=>fs.writeFileSync(pinFile,JSON.stringify(S.pinFor(state,priv(external)))+'\n');
 updatePin();
 ok('signed external pin validates',()=>assert.equal(S.readPin(pinFile,pinPublic).epoch,1));
 ok('wrong pinned public key rejects',()=>assert.throws(()=>S.readPin(pinFile,pub(pkey())),/PIN_SIGNATURE/));
 ok('altered signature rejects',()=>{const p=JSON.parse(fs.readFileSync(pinFile));p.signature='bogus';assert.throws(()=>S.verifyPin(p,pinPublic),/PIN_SIGNATURE/);});
 ok('altered signed epoch rejects',()=>{const p=JSON.parse(fs.readFileSync(pinFile));p.body.epoch=9;assert.throws(()=>S.verifyPin(p,pinPublic),/PIN_SIGNATURE/);});
 ok('invalid pin schema rejects',()=>assert.throws(()=>S.verifyPin({body:{schema:'fake'}},pinPublic),/PIN_SCHEMA/));
 ok('missing pin fails closed',()=>assert.throws(()=>S.readPin(file('missing-pin'),pinPublic),/EXTERNAL_PIN_UNAVAILABLE/));
 const certs={};openssl('req','-x509','-newkey','rsa:2048','-nodes','-days','1','-subj','/CN=ca','-keyout',file('ca.key'),'-out',file('ca.crt'));
 for(const name of ['resourceA','resourceB','writer'])certs[name]=makeSignedCert(name);
 openssl('req','-x509','-newkey','rsa:2048','-nodes','-days','1','-subj','/CN=evilca','-keyout',file('evilca.key'),'-out',file('evilca.crt'));
 certs.rogue=makeSignedCert('rogue','evilca');
 const pinPublicKey=file('pin.public.pem');fs.writeFileSync(pinPublicKey,pinPublic);
 const base={membershipFile:state,pinFile,pinPublicKey,testMode:true};
 const aCfg={...base,...certs.resourceA,resourceFile:file('resourceA.json')};
 const bCfg={...base,...certs.resourceB,resourceFile:file('resourceB.json')};
 const a=await child('resource142.js',aCfg),b=await child('resource142.js',bCfg);procs.push(a,b);
 ok('two distinct protected resource processes started',()=>{assert.notEqual(a.port,b.port);assert.equal(M.ready(state).fence,1);});
 const leaseOld=M.lease(state,'green',priv(keys.green),{ttlMs:60000});
 const req=(operationId,lease=leaseOld,value=operationId)=>({operationId,lease,value});
 await asyncOk('resource A commits through serialized membership lock',async()=>assert.equal((await call(a.port,req('first'),{tls:certs.writer})).status,'RESOURCE_COMMITTED'));
 await asyncOk('resource B commits through same membership lock',async()=>assert.equal((await call(b.port,req('second'),{tls:certs.writer})).status,'RESOURCE_COMMITTED'));
 ok('independent registers each have one record',()=>{assert.equal(G.read(aCfg.resourceFile).sequence,1);assert.equal(G.read(bCfg.resourceFile).sequence,1);});
 await asyncOk('idempotent same-operation replay',async()=>assert.equal((await call(a.port,req('first'),{tls:certs.writer})).status,'IDEMPOTENT_REPLAY'));
 await asyncOk('changed value under same ID rejected',async()=>assert.match((await call(a.port,req('first',leaseOld,'altered'),{tls:certs.writer,expectedCode:409})).error,/CONFLICT/));
 await asyncOk('forged lease rejected',async()=>{const bogus=structuredClone(leaseOld);bogus.signature='forged';assert.match((await call(a.port,req('forged',bogus),{tls:certs.writer,expectedCode:409})).error,/FENCE_SIGNATURE/);});
 await asyncOk('untrusted mTLS client rejected',async()=>await rejects(call(a.port,req('rogue'),{tls:certs.rogue}),/certificate|CERT|alert|unable to verify|self-signed|socket hang up|ECONNRESET/i));
 await asyncOk('simultaneous resource writes share membership lock',async()=>{const results=await Promise.allSettled([call(a.port,req('race-A'),{tls:certs.writer}),call(b.port,req('race-B'),{tls:certs.writer})]);assert.equal(results.filter(x=>x.status==='fulfilled').length,1);assert.equal(results.filter(x=>x.status==='rejected').length,1);assert.match(results.find(x=>x.status==='rejected').reason.message,/MEMBERSHIP_LOCKED/);});
 await asyncOk('rejected write can retry after contention',async()=>{const n=G.read(aCfg.resourceFile).sequence+G.read(bCfg.resourceFile).sequence;const op=G.read(aCfg.resourceFile).recordIndex['race-A']===undefined?'race-A':'race-B';const port=op==='race-A'?a.port:b.port;assert.equal((await call(port,req(op),{tls:certs.writer})).status,'RESOURCE_COMMITTED');assert.equal(G.read(aCfg.resourceFile).sequence+G.read(bCfg.resourceFile).sequence,n+1);});
 ok('signed external pin maintains floor',()=>{const c=S.readPin(pinFile,pinPublic);assert.equal(c.fence,1);assert.equal(S.recoverStatus({membershipFile:state,resourceFile:aCfg.resourceFile,pinFile,pinPublicKey:pinPublic}).status,'RECOVERABLE');});
 const proposed=M.proposalBody(M.ready(state),next,subset(next),Date.now()+120000);
 const opSig=['op-a','op-b'].map(id=>({id,signature:sign(operators[id],'oasis140:operator',proposed)}));
 const possession={amber:sign(keys.amber,'oasis140:possession',proposed)};
 await asyncOk('delayed resource write holds membership cutover lock',async()=>{
  const delayed=call(a.port,{...req('delayed-old'),testDelayMs:550},{tls:certs.writer});
  let locked=false;for(let i=0;i<30;i++){if(fs.existsSync(state+'.lock')){locked=true;break;}await new Promise(r=>setTimeout(r,20));}assert(locked);
  assert.throws(()=>M.propose(state,proposed,opSig,opPins,possession),/MEMBERSHIP_LOCKED/);
  assert.equal(M.read(state).pending,null);
  assert.equal((await delayed).status,'RESOURCE_COMMITTED');
  assert.equal(M.read(state).epoch,1);
 });
 ok('serialized write completes before membership proposal',()=>{const result=M.propose(state,proposed,opSig,opPins,possession);assert.equal(result.status,'JOINT_PENDING');});
 await asyncOk('joint transition blocks new writes',async()=>assert.match((await call(a.port,req('pending'),{tls:certs.writer,expectedCode:409})).error,/MEMBERSHIP_JOINT_PENDING/));
 ok('old 3/3 approval during joint',()=>{for(const id of old)M.accept(state,M.ackFor(priv(keys[id]),id,proposed,'JOINT_OLD'));assert(M.read(state).pending);});
 ok('new 3/3 approval during joint',()=>{for(const id of next)M.accept(state,M.ackFor(priv(keys[id]),id,proposed,'JOINT_NEW'));assert.equal(M.read(state).pending.state,'JOINT_CERTIFIED');});
 ok('new 3/3 final approval',()=>{for(const id of next)M.accept(state,M.ackFor(priv(keys[id]),id,proposed,'FINAL_NEW'));assert.equal(Object.keys(M.read(state).pending.finalAcks).length,3);});
 ok('new fleet certified',()=>{setupFleet(newFleet,next);assert.equal(F.assertReady(newFleet,subset(next),{requiredNodes:next}).status,'FLEET_VERIFIED');});
 ok('membership final cutover to epoch 2',()=>assert.equal(M.finish(state,{newFleetFile:newFleet,newAckPins:subset(next)}).fence,2));
 const fresh=M.lease(state,'amber',priv(keys.amber),{ttlMs:60000});
 await asyncOk('old lease rejected after cutover',async()=>assert.match((await call(a.port,req('stale'),{tls:certs.writer,expectedCode:409})).error,/FENCE_STALE/));
 await asyncOk('new epoch writer committed',async()=>assert.equal((await call(a.port,req('new-a',fresh),{tls:certs.writer})).fence,2));
 ok('resource retained epoch 2 high water',()=>{assert.equal(G.read(aCfg.resourceFile).fence,2);assert.equal(G.read(bCfg.resourceFile).fence,1);});
 ok('external pin advances to epoch 2',()=>{updatePin();assert.equal(S.readPin(pinFile,pinPublic).epoch,2);});
 await asyncOk('new pin keeps current writes valid',async()=>assert.equal((await call(b.port,req('new-b',fresh),{tls:certs.writer})).fence,2));
 const saved=fs.readFileSync(state);const oldSaved=file('rollback.json');
 // Prepare a real, correctly-hashed but older membership snapshot by temporarily inspecting the genesis history.
 const older=structuredClone(M.read(state));older.history=older.history.slice(0,1);older.epoch=1;older.fence=1;older.members=old;older.pins=subset(old);older.pending=null;older.fleet={1:older.fleet[1]};older.headHash=M.digest(older.history[0]);
 fs.writeFileSync(oldSaved,JSON.stringify({state:older,integrity:M.digest(older)}));
 ok('signed external epoch pin detects restored old membership',()=>assert.throws(()=>S.recoverStatus({membershipFile:oldSaved,resourceFile:aCfg.resourceFile,pinFile,pinPublicKey:pinPublic}),/MEMBERSHIP_ROLLBACK/));
 ok('signed pin detects incorrect head same epoch',()=>{const p=JSON.parse(fs.readFileSync(pinFile));p.body.headHash='1'.repeat(64);p.signature=M.sign(priv(external),S.PIN_DOMAIN,p.body);assert.throws(()=>S.checkPin(M.read(state),S.verifyPin(p,pinPublic)),/MEMBERSHIP_ROLLBACK/);});
 ok('resource register tampering rejected',()=>{const raw=JSON.parse(fs.readFileSync(aCfg.resourceFile));raw.state.sequence=99;const tmpfile=file('tamper.json');fs.writeFileSync(tmpfile,JSON.stringify(raw));assert.throws(()=>G.read(tmpfile),/RESOURCE_TAMPERED/);});
 ok('stale/orphan lock is held pending manual review',()=>{fs.mkdirSync(state+'.lock');assert.equal(S.recoverStatus({membershipFile:state,resourceFile:aCfg.resourceFile,pinFile,pinPublicKey:pinPublic}).status,'HOLD_MANUAL_LOCK_REVIEW');fs.rmdirSync(state+'.lock');});
 await asyncOk('orphan lock prevents any resource commit',async()=>{fs.mkdirSync(state+'.lock');try{assert.match((await call(a.port,req('lock-guard',fresh),{tls:certs.writer,expectedCode:409})).error,/MEMBERSHIP_LOCKED/);}finally{fs.rmdirSync(state+'.lock');}});
 await asyncOk('resource A survives process restart',async()=>{await stop(a);const restarted=await child('resource142.js',aCfg);procs.push(restarted);assert.equal((await call(restarted.port,req('restart-a',fresh),{tls:certs.writer})).fence,2);});
 ok('recovery status correctly verifies durable state',()=>{const r=S.recoverStatus({membershipFile:state,resourceFile:aCfg.resourceFile,pinFile,pinPublicKey:pinPublic});assert.equal(r.status,'RECOVERABLE');assert(r.resourceSequence>=4);});
 ok('two resource ledgers contain no stale-epoch writes after cutover',()=>{for(const f of [aCfg.resourceFile,bCfg.resourceFile]){const x=G.read(f);let seen2=false;for(const r of x.records){if(r.epoch===2)seen2=true;if(seen2)assert.equal(r.epoch,2);}}});
 const report={sheet:142,status:'PASS',checks:count,names:calls,scope:'serialized one-filesystem member/resource gate, two real local mTLS resource processes',limitations:['global linearizability assumes every membership mutation uses inherited M lock on one shared filesystem','orphan locks deliberately require operator review','cannot ensure atomic resource mutations across independent hosts','test-only CA and keys','external fence pin signed but not published to independent operator','not production-certified']};
 fs.writeFileSync(path.join(__dirname,'last-gate-report.json'),JSON.stringify(report,null,2)+'\n');
 console.log('SHEET142_REGRESSION_PASS '+count+'/'+count);
 }catch(e){console.error('SHEET142_REGRESSION_FAIL',e.stack||e);process.exitCode=1;}
 finally{await Promise.allSettled(procs.map(stop));fs.rmSync(tmp,{recursive:true,force:true});}})();
