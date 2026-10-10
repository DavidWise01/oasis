'use strict';
const P=require('./baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const M=require('./baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/merkle151');
const crypto=require('node:crypto');
const SCHEMA='oasis.sheet161.anchor.v1';
function anchorBody(resourceId,head,sequence=1){return {schema:SCHEMA,resourceId,count:head.count,root:head.root,lastRecordHash:head.lastRecordHash,sequence};}
function signAnchor(body,privateKey){return {body,signature:P.sign(privateKey,'S161:ANCHOR',body)};}
function checkAnchor(signed,pub){const b=signed?.body;if(b?.schema!==SCHEMA||!Number.isSafeInteger(b.count)||b.count<0||!Number.isSafeInteger(b.sequence)||b.sequence<1||!P.verify(pub,'S161:ANCHOR',b,signed.signature))throw Error('S161_ANCHOR_SIGNATURE');return b;}
function certified(target,heads,nonce,keys){if(!/^[a-f0-9]{40}$/.test(nonce||'')||!target||!Number.isSafeInteger(target.count)||target.count<0)throw Error('S161_CERT_TARGET');let ids=new Set();for(const item of heads||[]){const b=item?.body;if(!keys[b?.nodeId]||ids.has(b.nodeId)||b.nonce!==nonce||b.resourceId!==target.resourceId||b.count!==target.count||b.root!==target.root||b.lastRecordHash!==target.lastRecordHash||!P.verify(keys[b.nodeId],'S161:HEAD',b,item.signature))throw Error('S161_CERT_SIGNATURE');ids.add(b.nodeId);}if(ids.size<2)throw Error('S161_CERT_QUORUM');return true;}
function verifyPage(page,ctx){const b=page?.body,signer=b?.nodeId;if(!ctx.keys[signer]||!ctx.allowed.includes(signer)||!P.verify(ctx.keys[signer],'S161:PAGE',b,page.signature))throw Error('S161_PAGE_SIGNATURE');if(b.schema!=='oasis.sheet161.page.v1'||b.nonce!==ctx.nonce||P.sha(b.target)!==P.sha(ctx.target)||b.from!==ctx.local.count||b.records?.length<1||b.records?.length>8||b.to!==b.from+b.records.length||b.to>ctx.target.count)throw Error('S161_PAGE_CONTEXT');
 const after=b.after; if(!after||after.count!==b.to||M.root(after.count,after.frontier)!==after.root)throw Error('S161_PAGE_AFTER');M.verifyExtension(ctx.local,b.extension,after);
 let acc={count:ctx.local.count,frontier:ctx.local.frontier.slice()};let last=ctx.lastRecordHash;
 for(let i=0;i<b.records.length;i++){
  const entry=b.records[i],r=entry.record;
  if(r.sequence!==b.from+i+1||r.prev!==last||r.hash!==P.sha({schema:'oasis.sheet160.indexed.v1',id:ctx.target.resourceId,sequence:r.sequence,prev:r.prev,txid:r.txid,payload:r.payload}))throw Error('S161_RECORD_CHAIN');
  if(entry.inclusion.index!==b.from+i||entry.inclusion.count!==ctx.target.count||!M.verifyInclusion(entry.inclusion,ctx.target.root,r.hash))throw Error('S161_RECORD_INCLUSION');
  acc=M.appendPeak(acc.count,acc.frontier,1,M.leaf(acc.count,r.hash));last=r.hash;
 }
 if(acc.count!==after.count||M.root(acc.count,acc.frontier)!==after.root||last!==b.lastRecordHash)throw Error('S161_PAGE_ROOT');
 if(b.to===ctx.target.count&&last!==ctx.target.lastRecordHash)throw Error('S161_FINAL_TAIL');
 return b.records.map(x=>x.record);
}
module.exports={SCHEMA,anchorBody,signAnchor,checkAnchor,certified,verifyPage};
