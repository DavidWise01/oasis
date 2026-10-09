'use strict';
// SHEET142: single-filesystem serialized resource mutations and membership operations.
// Intended only for membership operations that use M.withLock on the same membershipFile.
const fs=require('node:fs'),crypto=require('node:crypto');
const M=require('./baseline141/baseline140/membership140');
const G=require('./baseline141/fencing141');
const PIN_DOMAIN='oasis142:external-fence-pin:v1';
const PIN_SCHEMA='oasis.sheet142.external-pin.v1';
function fail(msg){throw Error(msg);}
function pinFor(membershipFile,signingPrivate,{now=Date.now()}={}){
 const s=M.ready(membershipFile,{now});
 const body={schema:PIN_SCHEMA,epoch:s.epoch,fence:s.fence,headHash:s.headHash,issuedAt:now};
 return {body,signature:M.sign(signingPrivate,PIN_DOMAIN,body)};
}
function verifyPin(pin,pinnedPublicKey){
 const b=pin?.body;
 if(!b||b.schema!==PIN_SCHEMA||!Number.isSafeInteger(b.epoch)||b.epoch<1||!Number.isSafeInteger(b.fence)||b.fence<1||!/^[0-9a-f]{64}$/.test(b.headHash)||!Number.isSafeInteger(b.issuedAt))fail('PIN_SCHEMA');
 if(!M.verify(pinnedPublicKey,PIN_DOMAIN,b,pin.signature))fail('PIN_SIGNATURE');
 return b;
}
function readPin(file,publicKey){
 let raw;try{raw=fs.readFileSync(file,'utf8');}catch{fail('EXTERNAL_PIN_UNAVAILABLE');}
 let pin;try{pin=JSON.parse(raw);}catch{fail('EXTERNAL_PIN_UNREADABLE');}
 return verifyPin(pin,publicKey);
}
function checkPin(s,b){
 if(s.epoch<b.epoch||(s.epoch===b.epoch&&s.headHash!==b.headHash))fail('MEMBERSHIP_ROLLBACK');
 if(s.epoch===b.epoch&&s.fence!==b.fence)fail('PIN_FENCE_MISMATCH');
 return true;
}
function checkRequest(body){
 if(!body||typeof body.operationId!=='string'||!/^[a-zA-Z0-9_-]{1,64}$/.test(body.operationId)||typeof body.value!=='string'||body.value.length>256||!body.lease)fail('RESOURCE_REQUEST_INVALID');
}
function writeState(s,b,body){
 if(s.epoch>b.epoch||s.fence>b.fence||(s.epoch===b.epoch&&s.headHash!==b.headHash))fail('RESOURCE_AUTHORITY_ROLLBACK');
 const valueHash=G.hash(body.value),prior=s.recordIndex[body.operationId];
 if(prior!==undefined){
  if(s.records[prior].valueHash!==valueHash)fail('RESOURCE_OPERATION_CONFLICT');
  return {status:'IDEMPOTENT_REPLAY',sequence:s.records[prior].sequence,epoch:s.records[prior].epoch,fence:s.records[prior].fence};
 }
 const previous=s.records.length?s.records[s.records.length-1].receiptHash:M.ZERO;
 const rec={sequence:s.sequence+1,previous,epoch:b.epoch,fence:b.fence,headHash:b.headHash,operationId:body.operationId,valueHash,writer:body.lease.body.node};
 rec.receiptHash=G.hash({...rec,receiptHash:undefined});
 s.epoch=b.epoch;s.fence=b.fence;s.headHash=b.headHash;s.sequence++;
 s.recordIndex[body.operationId]=s.records.length;s.records.push(rec);
 return {status:'RESOURCE_COMMITTED',sequence:s.sequence,epoch:b.epoch,fence:b.fence,receiptHash:rec.receiptHash};
}
async function commit({membershipFile,resourceFile,pinFile,pinPublicKey},body,{delayInsideLockMs=0}={}){
 checkRequest(body);
 const pin=readPin(pinFile,pinPublicKey);
 // M.authorize acquires membershipFile+'.lock' for the entire callback, including disk mutation.
 // M.propose/accept/finish use the same lock. No process-external stale-check gap remains
 // *within this single shared-filesystem trust boundary*.
 return (await M.authorize(membershipFile,body.lease,async()=>{
  const member=M.ready(membershipFile,{externalPin:pin});checkPin(member,pin);
  return G.withLock(resourceFile,async()=>{
   const s=G.read(resourceFile);
   if(delayInsideLockMs){
    if(!Number.isInteger(delayInsideLockMs)||delayInsideLockMs<0||delayInsideLockMs>1200)fail('TEST_DELAY_INVALID');
    await new Promise(r=>setTimeout(r,delayInsideLockMs));
   }
   const result=writeState(s,member,body);
   if(result.status==='RESOURCE_COMMITTED')G.save(resourceFile,s);
   return result;
  });
 },{externalPin:pin})).result;
}
function recoverStatus({membershipFile,resourceFile,pinFile,pinPublicKey}){
 const pin=readPin(pinFile,pinPublicKey);const s=M.read(membershipFile);checkPin(s,pin);
 // The presence of a lock is not interpreted as an expired lease.
 if(fs.existsSync(membershipFile+'.lock')||fs.existsSync(resourceFile+'.lock'))return {status:'HOLD_MANUAL_LOCK_REVIEW',epoch:s.epoch,fence:s.fence};
 const r=G.read(resourceFile);
 if(r.epoch>s.epoch||r.fence>s.fence||(r.epoch===s.epoch&&r.epoch!==0&&r.headHash!==s.headHash))fail('RESOURCE_AUTHORITY_ROLLBACK');
 return {status:'RECOVERABLE',epoch:s.epoch,fence:s.fence,resourceSequence:r.sequence};
}
module.exports={PIN_SCHEMA,PIN_DOMAIN,pinFor,verifyPin,readPin,checkPin,checkRequest,writeState,commit,recoverStatus};
