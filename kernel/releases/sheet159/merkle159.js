'use strict';
const P=require('./baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./baseline158/baseline157/baseline156/witness-verify156');
const M=require('./baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/merkle151');
const SCHEMA='oasis.sheet159.merkle.page.v1',MAX_PAGE=24;
const hex=s=>typeof s==='string'&&/^[a-f0-9]{64}$/.test(s);
function certify(target,checkpoints,nonce,keys){
 if(!/^[0-9a-f]{40}$/.test(nonce||'')||!Number.isSafeInteger(target?.slot)||target.slot<0||!hex(target?.head)||!hex(target?.merkleRoot))throw Error('W159_TARGET');
 const seen=new Set();
 for(const x of checkpoints||[]){const b=x?.body,id=b?.nodeId;
  if(!keys[id]||seen.has(id)||b.nonce!==nonce||b.slot!==target.slot||b.head!==target.head||b.merkleRoot!==target.merkleRoot||!Array.isArray(b.frontier)||!P.verify(keys[id],'S159:CHECKPOINT',b,x.signature))throw Error('W159_CHECKPOINT_SIGNATURE');
  if(M.root(b.slot,b.frontier)!==b.merkleRoot)throw Error('W159_CHECKPOINT_FRONTIER');
  seen.add(id);
 }
 if(seen.size<2)throw Error('W159_NO_QUORUM');return [...seen];
}
function verifyPage(page,{nonce,target,cursor,head,merkle,signers,keys}){
 const b=page?.body,id=b?.nodeId;
 if(!signers.includes(id)||!keys[id]||!P.verify(keys[id],'S159:PAGE',b,page.signature))throw Error('W159_PAGE_SIGNATURE');
 if(b.schema!==SCHEMA||b.nonce!==nonce||P.sha(b.target)!==P.sha(target)||b.offset!==cursor||b.prevHead!==head||b.priorRoot!==merkle.root)throw Error('W159_PAGE_CONTEXT');
 if(!Array.isArray(b.records)||b.records.length<1||b.records.length>MAX_PAGE||b.next!==cursor+b.records.length||b.next>target.slot)throw Error('W159_PAGE_SIZE');
 let current=head;
 for(let i=0;i<b.records.length;i++){const r=W.normalize(b.records[i]);if(r.slot!==cursor+i+1||r.prev!==current||P.sha(r)!==P.sha(b.records[i]))throw Error('W159_PAGE_CHAIN');current=r.head;}
 if(current!==b.endHead)throw Error('W159_END_HEAD');
 if(!Array.isArray(b.afterFrontier)||!hex(b.afterRoot))throw Error('W159_AFTER_ROOT');
 const newState=M.verifyExtension(merkle,b.extension,{count:b.next,frontier:b.afterFrontier,root:b.afterRoot});
 // Merkle proof must have exactly the hashes of the transmitted records, not only a consistent but unrelated subtree.
 const computed=b.records.reduce((s,row)=>M.appendPeak(s.count,s.frontier,1,M.leaf(s.count,P.sha(row))),{count:merkle.count,frontier:merkle.frontier.slice()});
 if(M.root(computed.count,computed.frontier)!==newState.root)throw Error('W159_PAGE_LEAF_SUBSTITUTION');
 if(b.next===target.slot&&(current!==target.head||newState.root!==target.merkleRoot))throw Error('W159_TARGET_MISMATCH');
 return b.records;
}
module.exports={SCHEMA,MAX_PAGE,certify,verifyPage};
