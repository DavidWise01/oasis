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
