import {verify,createPublicKey} from 'node:crypto';
const wire=x=>Buffer.from(JSON.stringify({domain:'ROOT0/P454/request',deployment:x.deployment,nonce:x.nonce,action:x.action,stamp:x.stamp??null,policyEpoch:x.policyEpoch}));
/** Enforce distinct Ed25519 roles for certificate rotation and checkpoint operations. */
export function verifyRoleBoundRequest(req,{controllerPublic,rotationRequesterPublic}){
 if(!req||!['ROTATE','OBSERVE','COMPARE','LATEST'].includes(req.action))return false;
 const candidate=req.action==='ROTATE'?rotationRequesterPublic:controllerPublic;
 if(!candidate)return false;
 try{return verify(null,wire(req),candidate?.type==='public'?candidate:createPublicKey(candidate),Buffer.from(req.signature,'base64'))}catch{return false}
}