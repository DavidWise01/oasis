'use strict';
const crypto=require('node:crypto');
const P=require('./baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const V=require('./proof161');
function make({identity,nodes,keys,anchor,anchorKey}){
 const rpc=(name,path,body={})=>P.rpc({...identity,...nodes[name]},path,body);
 function verifySigned(id,domain,item){if(item?.body?.nodeId!==id||!P.verify(keys[id],domain,item.body,item.signature))throw Error('S161_PEER_SIGNATURE');return item.body;}
 async function sync(targetName,{limit=8,onPage=()=>{},nonce:forcedNonce}={}){
  const nodeIds=Object.keys(nodes).filter(x=>x!==targetName);
  let stat=verifySigned(targetName,'S161:STATUS',await rpc(targetName,'/status161'));
  const nonce=forcedNonce||stat.nonce||crypto.randomBytes(20).toString('hex');
  if(nodeIds.length!==2||limit<1||limit>8)throw Error('S161_SYNC_CONFIG');
  const heads=await Promise.all(nodeIds.map(id=>rpc(id,'/head161',{nonce})));const source=heads[0].body;
  const target={resourceId:source.resourceId,count:source.count,root:source.root,lastRecordHash:source.lastRecordHash};
  V.certified(target,heads,nonce,keys);const pinned=V.checkAnchor(anchor,anchorKey);
  if(pinned.resourceId!==target.resourceId||pinned.count!==target.count||pinned.root!==target.root||pinned.lastRecordHash!==target.lastRecordHash)throw Error('S161_EXTERNAL_ANCHOR_MISMATCH');
  if(stat.active&&(stat.nonce!==nonce||P.sha(stat.target)!==P.sha(target)))throw Error('S161_SESSION_TARGET_MISMATCH');
  if(!stat.active){stat=verifySigned(targetName,'S161:STATUS',await rpc(targetName,'/begin161',{anchor,heads,nonce,target}));}
  while(stat.count<target.count){const src=nodeIds[stat.count%2],page=await rpc(src,'/page161',{nonce,target,offset:stat.count,limit});let before=stat.count;
   try{stat=verifySigned(targetName,'S161:STATUS',await rpc(targetName,'/apply161',{page}));}
   catch(e){try{const after=verifySigned(targetName,'S161:STATUS',await rpc(targetName,'/status161'));if(after.count>before){stat=after;}else throw e;}catch{throw e;}}
   if(stat.count<=before||stat.count>target.count)throw Error('S161_NO_FORWARD_PROGRESS');onPage(stat.count,Buffer.byteLength(JSON.stringify(page)));
  }
  if(stat.root!==target.root)throw Error('S161_FINAL_ROOT');return verifySigned(targetName,'S161:FINISH',await rpc(targetName,'/finish161'));
 }
 return{rpc,sync};
}
module.exports={make};
