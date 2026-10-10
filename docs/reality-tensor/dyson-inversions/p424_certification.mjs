import {createHash,createPublicKey,verify} from 'node:crypto';
import {readFile} from 'node:fs/promises';
const canonical=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P424/certification/v1',deployment:x.deployment,controllerHost:x.controllerHost,witnessHost:x.witnessHost,controllerAdmin:x.controllerAdmin,witnessAdmin:x.witnessAdmin,controllerKeyDomain:x.controllerKeyDomain,witnessKeyDomain:x.witnessKeyDomain,checkpointEpoch:x.checkpointEpoch,checkpointDigest:x.checkpointDigest,tests:x.tests,nonce:x.nonce}));
const hex64=x=>typeof x==='string'&&/^[0-9a-f]{64}$/.test(x);
const id=x=>typeof x==='string'&&x.length>0&&x.length<=256;
export function evaluateCertification(record,{adminPublicKey,minimumEpoch=1,allowSimulated=false}={}){
 const failures=[];const fail=x=>failures.push(x);
 if(!record||typeof record!=='object')return {certified:false,failures:['missing-record']};
 for(const k of ['deployment','controllerHost','witnessHost','controllerAdmin','witnessAdmin','controllerKeyDomain','witnessKeyDomain','nonce'])if(!id(record[k]))fail('missing-'+k);
 if(record.controllerHost===record.witnessHost)fail('same-host');
 if(record.controllerAdmin===record.witnessAdmin)fail('shared-administration');
 if(record.controllerKeyDomain===record.witnessKeyDomain)fail('shared-key-custody');
 if(!Number.isSafeInteger(record.checkpointEpoch)||record.checkpointEpoch<minimumEpoch)fail('insufficient-epoch');
 if(!hex64(record.checkpointDigest))fail('invalid-checkpoint-digest');
 if(!Array.isArray(record.tests)||record.tests.length<4)fail('missing-tests');
 else for(const needed of ['controller_rollback','witness_outage','forged_receipt','witness_restart']){
  const matching=record.tests.filter(t=>t?.name===needed);
  if(matching.length!==1||matching[0].result!=='PASS'||!hex64(matching[0].evidenceHash))fail('unverified-'+needed);
  if(matching[0]?.simulated&&!allowSimulated)fail('simulated-'+needed);
 }
 if(!id(record.signature)||!adminPublicKey)fail('missing-attestation-signature');
 else try{const key=adminPublicKey?.type==='public'?adminPublicKey:createPublicKey(adminPublicKey);if(!verify(null,canonical(record),key,Buffer.from(record.signature,'base64')))fail('invalid-attestation-signature');}catch{fail('invalid-attestation-signature');}
 return {certified:failures.length===0,failures,scope:allowSimulated?'LAB_POLICY_CHECK_ONLY':'DOCUMENTARY_GATE_NOT_EXTERNAL_FACT_VERIFICATION',recordHash:createHash('sha256').update(canonical(record)).digest('hex')};
}
export async function certifyFile(filename,opts){return evaluateCertification(JSON.parse(await readFile(filename,'utf8')),opts)}
export {canonical as certificationPayload};