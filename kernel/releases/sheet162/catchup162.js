'use strict';
const crypto=require('node:crypto');
const P=require('./baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const V=require('./baseline161/proof161');
const T=require('./transport162');
function make({identity,nodes,keys,anchor,anchorKey}){
 const transport=T.make(identity,nodes),rpc=transport.rpc;
 function signed(id,domain,item){if(item?.body?.nodeId!==id||!P.verify(keys[id],domain,item.body,item.signature))throw Error('S162_PEER_SIGNATURE');return item.body;}
 async function sync(targetName,{limit=8,onPage=()=>{}}={}){
  const ids=Object.keys(nodes).filter(n=>n!==targetName);if(ids.length!==2||limit<1||limit>8)throw Error('S162_PEER_CONFIG');let stat=signed(targetName,'S161:STATUS',await rpc(targetName,'/status161'));
  const nonce=stat.nonce||crypto.randomBytes(20).toString('hex');
  const heads=await Promise.all(ids.map(x=>rpc(x,'/head161',{nonce})));const first=heads[0].body,target={resourceId:first.resourceId,count:first.count,root:first.root,lastRecordHash:first.lastRecordHash};V.certified(target,heads,nonce,keys);
  const floor=V.checkAnchor(anchor,anchorKey);if(floor.resourceId!==target.resourceId||floor.count!==target.count||floor.root!==target.root||floor.lastRecordHash!==target.lastRecordHash)throw Error('S162_ANCHOR_MISMATCH');
  if(stat.active&&(stat.nonce!==nonce||P.sha(stat.target)!==P.sha(target)))throw Error('S162_SESSION_CONFLICT');
  if(!stat.active)stat=signed(targetName,'S161:STATUS',await rpc(targetName,'/begin161',{anchor,heads,nonce,target}));
  while(stat.count<target.count){const before=stat.count;const page=await rpc(ids[before%2],'/page161',{nonce,target,offset:before,limit});let after;
   try{after=signed(targetName,'S161:STATUS',await rpc(targetName,'/apply162',{page}));}catch(err){try{after=signed(targetName,'S161:STATUS',await rpc(targetName,'/status161'));if(after.count===before)throw err;}catch{throw err;}}
   if(after.count<=before||after.count>target.count)throw Error('S162_NO_PROGRESS');stat=after;onPage(stat.count,Buffer.byteLength(JSON.stringify(page)));
  }
  if(stat.root!==target.root)throw Error('S162_FINAL_ROOT');const receipt=signed(targetName,'S161:FINISH',await rpc(targetName,'/finish161'));return{...receipt,metrics:{...transport.metrics},finalCount:stat.count};
 }
 return{rpc,sync,transport,close:transport.close};
}
module.exports={make};
