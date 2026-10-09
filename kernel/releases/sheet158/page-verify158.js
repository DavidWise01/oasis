'use strict';
// Per-page append consistency from a quorum-certified head, not a whole-history export.
const P=require('./baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const W=require('./baseline157/baseline156/witness-verify156');
const SCHEMA='oasis.sheet158.page.v1', MAX_PAGE=24;
const hash=s=>typeof s==='string'&&/^[a-f0-9]{64}$/.test(s);
function certify(target,heads,nonce,keys){
 if(!/^[0-9a-f]{40}$/.test(nonce||'')||!Number.isSafeInteger(target?.slot)||target.slot<0||!hash(target?.head))throw Error('W158_TARGET_INVALID');
 const seen=new Set();
 for(const h of heads||[]){const v=h?.body,id=v?.nodeId;
  if(!keys[id]||seen.has(id)||v.nonce!==nonce||v.slot!==target.slot||v.head!==target.head||!P.verify(keys[id],'S156:HEAD',v,h.signature))throw Error('W158_HEAD_CERT_INVALID');seen.add(id);
 }
 if(seen.size<2)throw Error('W158_HEAD_QUORUM_MISSING');return [...seen];
}
function records(records,offset,prev){
 if(!Array.isArray(records)||records.length<1||records.length>MAX_PAGE)throw Error('W158_PAGE_BOUND');
 let head=prev;
 for(let i=0;i<records.length;i++){
  const r=W.normalize(records[i]);
  if(r.slot!==offset+i+1||r.prev!==head||P.sha(r)!==P.sha(records[i]))throw Error('W158_PAGE_CHAIN_OR_ORDER');
  head=r.head;
 }
 return head;
}
function verifyPage(page,{nonce,target,cursor,prev,signers,keys}){
 const b=page?.body,id=b?.nodeId;
 if(!signers.includes(id)||!keys[id]||!P.verify(keys[id],'S158:PAGE',b,page.signature))throw Error('W158_PAGE_SIGNATURE');
 if(b.schema!==SCHEMA||b.nonce!==nonce||b.targetSlot!==target.slot||b.targetHead!==target.head||b.offset!==cursor||b.prevHead!==prev)throw Error('W158_PAGE_CONTEXT_OR_GAP');
 const end=records(b.records,cursor,prev);
 if(b.next!==cursor+b.records.length||b.next>target.slot||b.endHead!==end||b.recordsDigest!==P.sha(b.records))throw Error('W158_PAGE_PROOF_MISMATCH');
 if(b.next===target.slot&&end!==target.head)throw Error('W158_TERMINAL_HEAD_MISMATCH');
 return b.records;
}
function makePage({nodeId,nonce,target,history,offset,limit}){
 if(!/^[0-9a-f]{40}$/.test(nonce||'')||!Number.isSafeInteger(offset)||offset<0||!Number.isInteger(limit)||limit<1||limit>MAX_PAGE)throw Error('W158_PAGE_REQUEST_INVALID');
 if(!Number.isSafeInteger(target?.slot)||target.slot<offset||target.slot>history.length||!hash(target.head))throw Error('W158_TARGET_RANGE');
 if(target.slot>0&&history[target.slot-1].head!==target.head||target.slot===0&&target.head!==W.ZERO)throw Error('W158_TARGET_NOT_IN_HISTORY');
 if(offset===target.slot)throw Error('W158_PAGE_ALREADY_COMPLETE');
 const page=history.slice(offset,Math.min(target.slot,offset+limit));
 const prev=offset?history[offset-1].head:W.ZERO;
 return{schema:SCHEMA,nodeId,nonce,targetSlot:target.slot,targetHead:target.head,offset,next:offset+page.length,prevHead:prev,endHead:page[page.length-1].head,records:page,recordsDigest:P.sha(page)};
}
function admitPending(state,recovery,records){
 if(!state.pending)return;
 const k=state.pending.slot-state.slot-1;
 if(k>=0&&k<recovery.staged.length+records.length){
  const match=k<recovery.staged.length?recovery.staged[k]:records[k-recovery.staged.length];
  if(P.sha(match)!==P.sha(state.pending))throw Error('W158_PENDING_FORK_QUARANTINE');
 }
}
module.exports={SCHEMA,MAX_PAGE,certify,records,verifyPage,makePage,admitPending};
