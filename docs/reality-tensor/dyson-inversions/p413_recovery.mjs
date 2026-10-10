import {readFile,stat} from 'node:fs/promises';
import {join} from 'node:path';
import {createHash,verify} from 'node:crypto';
import {GenesisAuthority} from './p410_genesis.mjs';
const sha=s=>createHash('sha256').update(s).digest('hex');
const key=d=>sha('ROOT0/P412/deployment/'+d);
const canon=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P413/recovery',deployment:x.deployment,reservationDigest:x.reservationDigest,action:x.action,sequence:x.sequence}));
export function signableRecovery(r){return canon(r);}
export async function inspect(registry,authority,operatorKey,deployment){
 let provisioning;try{provisioning=await readFile(join(registry,'PROVISIONED'),'utf8')}catch{return {status:'QUARANTINE',reason:'missing-registry'}};
 if(provisioning!=='ROOT0:P412:ACTIVE\n')return {status:'QUARANTINE',reason:'invalid-registry'};
 let record;let raw;try{raw=await readFile(join(registry,key(deployment)+'.json'),'utf8')}catch(e){return e.code==='ENOENT'?{status:'UNINITIALIZED',reason:'no-reservation'}:{status:'QUARANTINE',reason:'reservation-unreadable'}};try{record=JSON.parse(raw)}catch{return {status:'QUARANTINE',reason:'malformed-reservation'}};
 if(record.deployment!==deployment||typeof record.grantHash!=='string')return {status:'QUARANTINE',reason:'invalid-reservation'};
 let store;try{await stat(authority);store=new GenesisAuthority(authority,operatorKey,deployment)}catch{return {status:'QUARANTINE',reason:'reserved-without-authority',reservationDigest:sha(JSON.stringify(record))}};
 try{const current=store.status();return current.ok?{status:'ACTIVE',epoch:current.epoch,reservationDigest:sha(JSON.stringify(record))}:{status:'QUARANTINE',reason:'invalid-authority',reservationDigest:sha(JSON.stringify(record))};}finally{store.close()}
}
export async function recoverWithIntent({registry,authority,operatorKey,deployment,intent,adminPublicKey}){
 const prior=await inspect(registry,authority,operatorKey,deployment);
 if(prior.status!=='QUARANTINE'||prior.reason!=='reserved-without-authority')return {ok:false,reason:'not-recoverable'};
 if(!intent||intent.deployment!==deployment||intent.reservationDigest!==prior.reservationDigest||intent.action!=='REVIEW_REQUIRED'||!Number.isSafeInteger(intent.sequence)||intent.sequence<1)return {ok:false,reason:'bad-intent'};
 try{if(!verify(null,canon(intent),adminPublicKey,Buffer.from(intent.signature,'base64')))return {ok:false,reason:'invalid-signature'}}catch{return {ok:false,reason:'invalid-signature'}};
 return {ok:false,reason:'manual-independent-witness-review-required',verifiedIntent:true};
}