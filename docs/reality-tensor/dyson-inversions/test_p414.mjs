import assert from 'node:assert/strict';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {join} from 'node:path';import {tmpdir} from 'node:os';
import {generateKeyPairSync} from 'node:crypto';import {fork} from 'node:child_process';
import {performance} from 'node:perf_hooks';
import {genesisGrant} from './p410_genesis.mjs';
import {DeploymentRegistry} from './p412_deployment.mjs';
import {inspect} from './p413_recovery.mjs';
const stages=['before-create','after-create','after-write','after-file-sync','after-dir-sync','after-authority-commit'];
const t0=performance.now();let checks=0;const records=[];
function check(v,label){assert.ok(v,label);checks++;}
for (const stage of stages){
 const dir=await mkdtemp(join(tmpdir(),'root-p414-'));
 try{
  const registry=join(dir,'registry'),authority=join(dir,'authority.db'),cfgpath=join(dir,'config.json');
  const pair=generateKeyPairSync('ed25519'),deployment='oasis/p414-'+stage;
  await DeploymentRegistry.provision(registry);
  const grant=genesisGrant(pair.privateKey,deployment);
  await writeFile(cfgpath,JSON.stringify({registry,authority,publicKey:pair.publicKey.export({format:'pem',type:'spki'}),deployment,grant,stopAt:stage}));
  const child=fork(new URL('./p414_worker.mjs',import.meta.url),[cfgpath],{stdio:['ignore','ignore','pipe','ipc']});
  let errors='';child.stderr?.on('data',data=>errors+=data);
  const exited=new Promise(resolve=>child.once('exit',(code,signal)=>resolve({code,signal})));
  try{
   await new Promise((resolve,reject)=>{
    const tm=setTimeout(()=>reject(Error('timeout at '+stage+' '+errors)),8000);
    const listener=m=>{if(m.stage===stage){clearTimeout(tm);child.off('message',listener);resolve();}};
    child.on('message',listener);
    child.once('error',reject);
    child.once('exit',(code,signal)=>{if(code!==null)reject(Error('early exit '+code+' '+errors));});
   });
   check(child.kill('SIGKILL'),'kill transmitted '+stage);
   const exit=await exited;check(exit.signal==='SIGKILL','SIGKILL observed '+stage);
   const state=await inspect(registry,authority,pair.publicKey,deployment);
   const expected=stage==='before-create'?'UNINITIALIZED':stage==='after-authority-commit'?'ACTIVE':'QUARANTINE';
   check(state.status===expected,stage+' expected '+expected+' got '+JSON.stringify(state));
   const retry=new DeploymentRegistry({directory:registry,authorityFile:authority,operatorKey:pair.publicKey,deployment});
   if(expected==='UNINITIALIZED')check((await retry.initialize(grant)).ok,'first genesis permitted before reservation');
   else check((await retry.initialize(grant)).reason==='deployment-already-reserved','cannot create second genesis '+stage);
   records.push({stage,signal:exit.signal,observedStatus:state.status,reason:state.reason??null});
  }finally{if(child.exitCode===null&&!child.killed)child.kill('SIGKILL');await exited;}
 }finally{await rm(dir,{recursive:true,force:true});}
}
check(records.length===6,'all crash boundaries exercised');
console.log(JSON.stringify({status:'PASS',assertions:checks,stages:records.length,killMethod:'SIGKILL after IPC checkpoint',elapsedMs:Number((performance.now()-t0).toFixed(3)),matrix:records,limitations:['No power-loss simulation','Local rollback not protected','Checkpoint kill is not arbitrary instruction kill']},null,2));