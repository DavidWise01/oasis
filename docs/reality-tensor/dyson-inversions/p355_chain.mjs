import {createHash} from 'node:crypto';
import {compose} from './p354_hardened.mjs';
export const GENESIS='0'.repeat(64);
const digest=s=>createHash('sha256').update(s).digest('hex');
const canonical=x=>JSON.stringify(x);
export function payload(envelope,channel,structure,spinor,depth=4){
 const s=compose({envelope,channel,structure,spinor,depth});
 return {envelope,channel,structure,spinor,depth,root:s.root,sheet:s.sheet,prime:s.prime,axis:s.axis,sign:s.sign,digits:s.digits};
}
export function append(records,items,head=records.length?records.at(-1).hash:GENESIS){
 const result=[...records];
 for(const item of items){const seq=result.length, prev=seq?result.at(-1).hash:GENESIS;
   if(prev!==head)throw Error('head mismatch');
   const hash=digest(canonical({seq,prev,item}));result.push({seq,prev,item,hash});head=hash;
 }
 return result;
}
export function checkpoint(records){return {length:records.length,head:records.length?records.at(-1).hash:GENESIS};}
export function verify(records,anchor=null){
 let prev=GENESIS;
 for(let i=0;i<records.length;i++){
  const r=records[i];if(r.seq!==i||r.prev!==prev||r.hash!==digest(canonical({seq:i,prev,item:r.item})))return {ok:false,reason:'chain',index:i};
  const expected=payload(r.item.envelope,r.item.channel,r.item.structure,r.item.spinor,r.item.depth);
  if(canonical(expected)!==canonical(r.item))return {ok:false,reason:'payload',index:i};
  prev=r.hash;
 }
 if(anchor&&(anchor.length!==records.length||anchor.head!==prev))return {ok:false,reason:'checkpoint'};
 return {ok:true,length:records.length,head:prev};
}
export function* items(envelope,channel=0,structure=0,count=1440,depth=4){for(let k=0;k<count;k++)yield payload(envelope,channel,structure,k,depth);}
