'use strict';
const P=require('./baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const V=require('./catchup-verify157');
function make({identity,witnesses,publicKeys}){
 const rpc=(id,url,b)=>P.rpc({...identity,...witnesses[id]},url,b);
 async function repair(target){
  if(!witnesses[target]||Object.keys(witnesses).length!==3)throw Error('W157_TARGET_OR_MEMBERS_INVALID');
  const challenge=await rpc(target,'/challenge',{}),nonce=challenge?.body?.nonce;
  if(!publicKeys[target]||!P.verify(publicKeys[target],'S157:CHALLENGE',challenge.body,challenge.signature)||!nonce)throw Error('W157_CHALLENGE_SIGNATURE_INVALID');
  const all=await Promise.all(Object.keys(witnesses).filter(id=>id!==target).map(async id=>{try{return{id,v:await rpc(id,'/read',{nonce})};}catch(e){return{id,error:e.message};}}));
  const heads=all.filter(x=>x.v?.body?.nodeId===x.id&&P.verify(publicKeys[x.id],'S156:HEAD',x.v.body,x.v.signature));
  if(heads.length<2)throw Error('W157_CATCHUP_NO_MAJORITY');
  const one=heads[0].v.body;
  if(heads.some(x=>x.v.body.slot!==one.slot||x.v.body.head!==one.head))throw Error('W157_MAJORITY_FORK');
  const exp=await rpc(heads[0].id,'/export',{nonce});
  V.certify({slot:one.slot,head:one.head},heads.map(x=>x.v),exp,nonce,publicKeys);
  const result=await rpc(target,'/catchup',{nonce,head:{slot:one.slot,head:one.head},heads:heads.map(x=>x.v),exported:exp});
  if(result?.body?.nodeId!==target||result.body.slot!==one.slot||result.body.head!==one.head||!P.verify(publicKeys[target],'S157:INSTALLED',result.body,result.signature))throw Error('W157_INSTALL_ACK_INVALID');
  return result;
 }
 return{repair,rpc};
}
module.exports={make};
