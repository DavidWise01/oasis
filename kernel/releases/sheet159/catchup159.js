'use strict';
const P=require('./baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const H=require('./merkle159');
function make({identity,witnesses,publicKeys}){
 const rpc=(id,url,b={})=>P.rpc({...identity,...witnesses[id]},url,b);
 function ack(id,domain,response){if(response?.body?.nodeId!==id||!P.verify(publicKeys[id],domain,response.body,response.signature))throw Error('W159_ACK_SIGNATURE');return response.body;}
 async function repair(target,{pageSize=16,onPage=()=>{}}={}){
  if(!witnesses[target]||Object.keys(witnesses).length!==3||!Number.isInteger(pageSize)||pageSize<1||pageSize>H.MAX_PAGE)throw Error('W159_CONFIG');
  let status=ack(target,'S159:STATUS',await rpc(target,'/status159'));
  let certified;
  if(!status.active){
   const nonce=ack(target,'S157:CHALLENGE',await rpc(target,'/challenge')).nonce;
   const peers=Object.keys(witnesses).filter(x=>x!==target),checks=[];
   for(const id of peers){try{const a=await rpc(id,'/checkpoint159',{nonce});ack(id,'S159:CHECKPOINT',a);checks.push(a);}catch{}}
   if(checks.length<2)throw Error('W159_NO_QUORUM');
   certified={slot:checks[0].body.slot,head:checks[0].body.head,merkleRoot:checks[0].body.merkleRoot};
   H.certify(certified,checks,nonce,publicKeys);
   ack(target,'S159:BEGIN',await rpc(target,'/begin159',{nonce,target:certified,checkpoints:checks}));
   status=ack(target,'S159:STATUS',await rpc(target,'/status159'));
  }
  certified=status.target;
  if(!certified||!status.nonce)throw Error('W159_SESSION');
  const peers=Object.keys(witnesses).filter(x=>x!==target);
  let cursor=status.cursor;
  while(cursor<certified.slot){
   let accepted=false,last;
   for(const id of peers){
    try{const page=await rpc(id,'/page159',{nonce:status.nonce,target:certified,offset:cursor,limit:pageSize});
     const result=ack(target,'S159:APPLIED',await rpc(target,'/apply159',{page}));
     if(result.cursor<=cursor||result.cursor>certified.slot)throw Error('W159_ACK_CURSOR');
     cursor=result.cursor;onPage(cursor);accepted=true;break;
    }catch(e){last=e;
     // An acknowledgement can be lost after durable write; consult the signed persisted cursor.
     try{const s=ack(target,'S159:STATUS',await rpc(target,'/status159'));if(s.active&&s.nonce===status.nonce&&s.target?.merkleRoot===certified.merkleRoot&&s.cursor>cursor){cursor=s.cursor;onPage(cursor);accepted=true;break;}}catch{}
    }
   }
   if(!accepted)throw Error('W159_STOPPED: '+(last?.message||'no source'));
  }
  const result=await rpc(target,'/finish159'),end=ack(target,'S159:FINISHED',result);
  if(end.slot!==certified.slot||end.head!==certified.head||end.merkleRoot!==certified.merkleRoot)throw Error('W159_FINAL_MISMATCH');return result;
 }
 return{rpc,repair};
}
module.exports={make};
