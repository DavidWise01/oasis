'use strict';
const P=require('./baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const Q=require('./page-verify158');
function make({identity,witnesses,publicKeys}){
 const rpc=(id,url,b={})=>P.rpc({...identity,...witnesses[id]},url,b);
 function ack(id,domain,x){if(x?.body?.nodeId!==id||!P.verify(publicKeys[id],domain,x.body,x.signature))throw Error('W158_ACK_INVALID');return x.body;}
 async function repair(target,{pageSize=8,onPage=()=>{}}={}){
  if(!witnesses[target]||Object.keys(witnesses).length!==3||!Number.isInteger(pageSize)||pageSize<1||pageSize>Q.MAX_PAGE)throw Error('W158_CONFIG_INVALID');
  let status=ack(target,'S158:STATUS',await rpc(target,'/status158'));
  let peers=[],tgt;
  if(!status.active){
   const challenge=await rpc(target,'/challenge');const nonce=ack(target,'S157:CHALLENGE',challenge).nonce;
   const ids=Object.keys(witnesses).filter(id=>id!==target);
   const responses=await Promise.all(ids.map(async id=>{try{return{id,resp:await rpc(id,'/read',{nonce})};}catch(e){return{id,error:e.message};}}));
   const valid=responses.filter(x=>x.resp?.body?.nodeId===x.id&&P.verify(publicKeys[x.id],'S156:HEAD',x.resp.body,x.resp.signature));
   if(valid.length<2)throw Error('W158_MAJORITY_UNAVAILABLE');
   tgt={slot:valid[0].resp.body.slot,head:valid[0].resp.body.head};
   Q.certify(tgt,valid.map(x=>x.resp),nonce,publicKeys);
   const begun=await rpc(target,'/begin158',{nonce,target:tgt,heads:valid.map(x=>x.resp)});
   ack(target,'S158:BEGIN',begun);
   status=ack(target,'S158:STATUS',await rpc(target,'/status158'));
  }
  tgt=status.target;
  if(!tgt||!status.nonce)throw Error('W158_SESSION_MISSING');
  peers=Object.keys(witnesses).filter(id=>id!==target);
  let cursor=status.cursor;
  while(cursor<tgt.slot){
   let accepted=false,lastError;
   for(const peer of peers){
    try{
     const page=await rpc(peer,'/page158',{nonce:status.nonce,target:tgt,offset:cursor,limit:pageSize});
     const applied=await rpc(target,'/apply158',{page});
     const body=ack(target,'S158:APPLIED',applied);
     if(body.cursor<=cursor||body.cursor>tgt.slot)throw Error('W158_NONMONOTONIC_ACK');
     cursor=body.cursor;onPage(cursor);accepted=true;break;
    }catch(e){lastError=e; // A lost acknowledgement may conceal a durably applied page.
     try{const current=ack(target,'S158:STATUS',await rpc(target,'/status158'));if(current.active&&current.cursor>cursor&&current.target?.head===tgt.head&&current.nonce===status.nonce){cursor=current.cursor;onPage(cursor);accepted=true;break;}}catch{}
    }
   }
   if(!accepted)throw Error('W158_PAGE_RECOVERY_STOP: '+(lastError?.message||'no majority page source'));
  }
  const final=await rpc(target,'/finish158');const body=ack(target,'S158:FINISHED',final);
  if(body.slot!==tgt.slot||body.head!==tgt.head)throw Error('W158_FINAL_HEAD_MISMATCH');return final;
 }
 return{rpc,repair};
}
module.exports={make};
