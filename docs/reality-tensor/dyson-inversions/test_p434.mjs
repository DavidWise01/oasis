import assert from 'node:assert/strict';import {generateKeyPairSync} from 'node:crypto';import {mkdtemp,writeFile,rm} from 'node:fs/promises';import {join} from 'node:path';import {tmpdir} from 'node:os';import {fork} from 'node:child_process';import {performance} from 'node:perf_hooks';import {StrictCasWitness,signIntent} from './p434_cas.mjs';
const start=performance.now();let checks=0;function check(v,msg){assert.ok(v,msg);checks++}
const dir=await mkdtemp(join(tmpdir(),'p433-'));const owner=generateKeyPairSync('ed25519'),w=generateKeyPairSync('ed25519');const pem=(k,type)=>k.export({format:'pem',type});const a='a'.repeat(64),b='b'.repeat(64),c='c'.repeat(64);const crash=[];
try{
for(const stage of ['transaction-start','intent-written','checkpoint-written','committed']){
 const db=join(dir,stage+'.sqlite'),dep='root0/'+stage;let gate=new StrictCasWitness(db,w.privateKey,w.publicKey,owner.publicKey);
 check(gate.initialize(dep,a).ok,stage+' genesis');check(typeof gate.publish==='undefined',stage+' unsafe publication method blocked');gate.close();
 const intent=signIntent(owner.privateKey,{deployment:dep,epoch:1,priorHead:a,nextHead:b,nonce:'1'.repeat(32)});
 const cfg=join(dir,stage+'.json');await writeFile(cfg,JSON.stringify({db,intent,killAt:stage,witnessPrivate:pem(w.privateKey,'pkcs8'),witnessPublic:pem(w.publicKey,'spki'),ownerPublic:pem(owner.publicKey,'spki')}));
 const child=fork(new URL('./p434_worker.mjs',import.meta.url),[cfg],{stdio:['ignore','ignore','pipe','ipc']});let err='';child.stderr.on('data',x=>err+=x);
 const ex=new Promise(resolve=>child.once('exit',(code,signal)=>resolve({code,signal})));
 try{await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('timeout '+stage+' '+err)),7000);child.once('message',m=>{clearTimeout(timer);m.stage===stage?resolve():reject(Error('bad stage'))});child.once('error',reject)});child.kill('SIGKILL');check((await ex).signal==='SIGKILL',stage+' real kill')}finally{child.kill('SIGKILL');}
 gate=new StrictCasWitness(db,w.privateKey,w.publicKey,owner.publicKey);const old=gate.read(dep);check(old.ok,stage+' signed recovery');const expected=stage==='committed'?1:0;check(old.stamp.epoch===expected,stage+' atomic rollback/commit');
 const alt=signIntent(owner.privateKey,{deployment:dep,epoch:1,priorHead:a,nextHead:c,nonce:'2'.repeat(32)});
 if(expected===0){check(gate.cas(alt).ok,stage+' fresh CAS allowed');check(!gate.cas(intent).ok,stage+' conflicting former intent denied');}
 else {check(gate.cas(intent).duplicate===true,'committed retry idempotent');check(!gate.cas(alt).ok,'committed conflicting intent denied');}
 gate.close();crash.push({stage,epochAfterKill:expected});
}
console.log(JSON.stringify({status:'PASS',assertions:checks,crashMatrix:crash,elapsedMs:Number((performance.now()-start).toFixed(3))},null,2));
}finally{await rm(dir,{recursive:true,force:true})}