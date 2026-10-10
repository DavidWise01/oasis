'use strict';
// Live fallback: only a local performance watchdog may trigger automatic downgrade.
// All cryptographic/protocol failures propagate; they are never disguised as slow policies.
const fs=require('node:fs');
const P=require('./baseline164/baseline163/baseline162/baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const Policy=require('./policy165');
function validateOptions(o){Policy.validate(o.candidate);Policy.validate(o.baseline);if(!(o.minRows>=8&&Number.isSafeInteger(o.minRows))||!(o.minRowsPerSecond>=0&&Number.isFinite(o.minRowsPerSecond)))throw Error('S165_GUARD_OPTIONS');}
async function sync({factory,candidate,baseline=Policy.BASELINE,target='blue',minRows=32,minRowsPerSecond=0,decisionFile,onDecision=()=>{}}){
 validateOptions({candidate,baseline,minRows,minRowsPerSecond});if(typeof factory!=='function')throw Error('S165_FACTORY');
 let client=factory(candidate),mode='candidate',result,beginRows=null,start=performance.now(),lastRows=0,transition=null,checkCount=0;
 try{
  try{
   result=await client.sync(target,{onCommit:(from,to)=>{
     if(beginRows===null)beginRows=from;
     lastRows=to-beginRows;checkCount++;
     if(minRowsPerSecond&&lastRows>=minRows&&lastRows/((performance.now()-start)/1000)<minRowsPerSecond){
        const error=Error('S165_POLICY_DEGRADED');error.code='S165_POLICY_DEGRADED';throw error;
     }
   }});
  }catch(error){
    if(error.code!=='S165_POLICY_DEGRADED')throw error;
    mode='fallback';transition={reason:error.code,atDurableRecords:lastRows,checks:checkCount,candidate,baseline};
    client.close();
    if(decisionFile){ // local audit record only; not a consensus pin
      P.atomic(decisionFile,{schema:'oasis.sheet165.fallback.v1',...transition});
    }
    onDecision(transition);
    client=factory(baseline);result=await client.sync(target);
  }
  return {mode,transition,result};
 }finally{client.close();}
}
module.exports={sync};
