import assert from 'node:assert/strict';import {mkdtemp,writeFile,rm} from 'node:fs/promises';import {join} from 'node:path';import {tmpdir} from 'node:os';import {generateKeyPairSync,sign} from 'node:crypto';import {fork} from 'node:child_process';import {performance} from 'node:perf_hooks';
import {genesisGrant} from './p410_genesis.mjs';import {DeploymentRegistry} from './p412_deployment.mjs';import {inspect,recoverWithIntent,signableRecovery} from './p413_recovery.mjs';
const t=performance.now(),dir=await mkdtemp(join(tmpdir(),'root-p413-'));let checks=0;function eq(a,b){assert.deepEqual(a,b);checks++}function yes(v){assert.ok(v);checks++}
try{
 const kp=generateKeyPairSync('ed25519'),admin=generateKeyPairSync('ed25519');const registry=join(dir,'registry'),authority=join(dir,'authority.db'),deployment='oasis/p413';await DeploymentRegistry.provision(registry);
 const grant=genesisGrant(kp.privateKey,deployment);const payload=join(dir,'payload.json');await writeFile(payload,JSON.stringify({registry,authority,deployment,grant,publicKey:kp.publicKey.export({format:'pem',type:'spki'})}));
 eq((await inspect(registry,authority,kp.publicKey,deployment)).status,'UNINITIALIZED');
 const child=fork(new URL('./p413_worker.mjs',import.meta.url),[payload,'after-reserve'],{stdio:['ignore','ignore','pipe','ipc']});
 const msg=await new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('worker-timeout')),5000);child.once('message',m=>{clearTimeout(timeout);resolve(m)});child.once('exit',(code,signal)=>{clearTimeout(timeout);reject(Error('early worker exit '+code+' '+signal))})});
 yes(msg.ready);eq(msg.result.reason,'injected-interruption-reservation-retained');child.kill('SIGKILL');const exit=await new Promise(resolve=>child.once('exit',(code,signal)=>resolve({code,signal})));eq(exit.signal,'SIGKILL');
 let state=await inspect(registry,authority,kp.publicKey,deployment);eq(state.status,'QUARANTINE');eq(state.reason,'reserved-without-authority');
 let reg=new DeploymentRegistry({directory:registry,authorityFile:authority,operatorKey:kp.publicKey,deployment});eq((await reg.initialize(grant)).reason,'deployment-already-reserved');
 const intent={deployment,reservationDigest:state.reservationDigest,action:'REVIEW_REQUIRED',sequence:1};intent.signature=sign(null,signableRecovery(intent),admin.privateKey).toString('base64');
 const rec=await recoverWithIntent({registry,authority,operatorKey:kp.publicKey,deployment,intent,adminPublicKey:admin.publicKey});eq(rec.reason,'manual-independent-witness-review-required');yes(rec.verifiedIntent);
 const tampered={...intent,sequence:2};eq((await recoverWithIntent({registry,authority,operatorKey:kp.publicKey,deployment,intent:tampered,adminPublicKey:admin.publicKey})).reason,'invalid-signature');
 const badKey=generateKeyPairSync('ed25519');eq((await recoverWithIntent({registry,authority,operatorKey:kp.publicKey,deployment,intent,adminPublicKey:badKey.publicKey})).reason,'invalid-signature');
 console.log(JSON.stringify({status:'PASS',assertions:checks,killedWorker:true,quarantineAfterKill:true,requiresManualReview:true,elapsedMs:Number((performance.now()-t).toFixed(3))}));
}finally{await rm(dir,{recursive:true,force:true})}