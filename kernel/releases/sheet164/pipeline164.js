'use strict';
// SHEET 164: factorial policy runner, ordered physical commits, no speculative writes.
const crypto=require('node:crypto');
const P=require('./baseline163/baseline162/baseline161/baseline160/baseline159/baseline158/baseline157/baseline156/baseline155/baseline154/baseline153/baseline152/baseline151/baseline150/baseline149/baseline148/baseline147/baseline146/protocol146');
const V=require('./baseline163/baseline162/baseline161/proof161');
const Transport=require('./transport164');
const MAX=8, SEGMENT=256;
function bound(offset,total,max=MAX){
 if(!Number.isSafeInteger(offset)||!Number.isSafeInteger(total)||offset<0||total<=offset||!Number.isInteger(max)||max<1||max>MAX)throw Error('S163_PAGE_BOUNDS');
 return Math.min(max,total-offset,SEGMENT-(offset%SEGMENT));
}
function chooseBatch(offset,rows,pressure=2){
 // Client controls performance hint only; verifier and server enforce maximum 8.
 if(!Number.isSafeInteger(offset)||offset<0||!Number.isInteger(rows)||rows<1||rows>MAX)throw Error('S163_BATCH_SHAPE');
 return Math.min(rows,SEGMENT-(offset%SEGMENT),pressure>=2?8:pressure===1?4:2);
}
function make({identity,nodes,keys,anchor,anchorKey,fetchWindow=1,delayFetch=()=>0,batchMode='adaptive',reuseTls=true}){
 if(!Number.isInteger(fetchWindow)||fetchWindow<1||fetchWindow>8)throw Error('S163_WINDOW_BOUNDS');
 if(!['adaptive','fixed8','fixed4'].includes(batchMode))throw Error('S163_BATCH_MODE');
 const transport=Transport.make(identity,nodes,{reuseTls}),rpc=transport.rpc;
 const observed={issued:[],fetched:[],committed:[],maxInFlight:0,retries:0,fetchMs:0,commitMs:0};
 function signed(id,domain,msg){if(msg?.body?.nodeId!==id||!P.verify(keys[id],domain,msg.body,msg.signature))throw Error('S163_BAD_PEER_SIGN');return msg.body;}
 async function sync(targetName,{limit=8,onCommit=()=>{},onFetch=()=>{}}={}){
  if(!Number.isInteger(limit)||limit<1||limit>MAX)throw Error('S163_LIMIT');
  const ids=Object.keys(nodes).filter(id=>id!==targetName);
  if(ids.length!==2)throw Error('S163_PEERS');
  let state=signed(targetName,'S161:STATUS',await rpc(targetName,'/status161'));
  const nonce=state.nonce||crypto.randomBytes(20).toString('hex');
  const votes=await Promise.all(ids.map(id=>rpc(id,'/head161',{nonce})));
  const first=votes[0].body,target={resourceId:first.resourceId,count:first.count,root:first.root,lastRecordHash:first.lastRecordHash};
  V.certified(target,votes,nonce,keys);
  const pin=V.checkAnchor(anchor,anchorKey);
  if(pin.resourceId!==target.resourceId||pin.count!==target.count||pin.root!==target.root||pin.lastRecordHash!==target.lastRecordHash)throw Error('S163_EXTERNAL_PIN_MISMATCH');
  if(state.active&&(state.nonce!==nonce||P.sha(state.target)!==P.sha(target)))throw Error('S163_SESSION_FORK');
  if(!state.active)state=signed(targetName,'S161:STATUS',await rpc(targetName,'/begin161',{anchor,heads:votes,nonce,target}));
  const inFlight=new Map();let next=state.count;const start=process.hrtime.bigint();
  function queue(){
   while(inFlight.size<fetchWindow&&next<target.count){
    const from=next,span=bound(from,target.count,limit),peer=ids[Math.floor(from/limit)%ids.length];next+=span;
    observed.issued.push(from);let promise=(async()=>{const t=process.hrtime.bigint();
      const response=await rpc(peer,'/page161',{nonce,target,offset:from,limit:span});
      const d=Number(delayFetch(from));if(!Number.isFinite(d)||d<0||d>1000)throw Error('S163_DELAY_BOUNDS');
      if(d)await new Promise(resolve=>setTimeout(resolve,d));
      observed.fetchMs+=Number(process.hrtime.bigint()-t)/1e6;
      observed.fetched.push(from);onFetch(from);return{response,span};
    })().then(value=>({value}),error=>({error}));inFlight.set(from,promise);
    observed.maxInFlight=Math.max(observed.maxInFlight,inFlight.size);
   }
  }
  try{
   while(state.count<target.count){
    // Durable state is the only cursor; schedule remote speculative reads, not writes.
    const cursor=state.count;queue();const pending=inFlight.get(cursor);
    if(!pending)throw Error('S163_MISSING_ORDERED_PAGE');const got=await pending;inFlight.delete(cursor);
    if(got.error)throw got.error;
    const pressure=inFlight.size+1,batchHint=batchMode==='fixed8'?chooseBatch(cursor,got.value.span,2):batchMode==='fixed4'?chooseBatch(cursor,got.value.span,1):chooseBatch(cursor,got.value.span,pressure);
    const t=process.hrtime.bigint();let after;
    try{after=signed(targetName,'S161:STATUS',await rpc(targetName,'/apply163',{page:got.value.response,batchHint}));}
    catch(error){
     // An ACK can disappear *after* fsync. Read authenticated target state; never replay blindly.
     observed.retries++;
     try{after=signed(targetName,'S161:STATUS',await rpc(targetName,'/status161'));}
     catch{throw error;}
     if(after.count<=cursor)throw error;
    }
    observed.commitMs+=Number(process.hrtime.bigint()-t)/1e6;
    if(after.count<=cursor||after.count>target.count||after.count>cursor+got.value.span)throw Error('S163_CURSOR_INCONSISTENT');
    state=after;observed.committed.push(cursor);onCommit(cursor,state.count);
    if(state.count!==cursor+got.value.span){
      // Interruption within an otherwise valid page: discard prefetched work and
      // request new certified pages starting at the *durable* intermediate cursor.
      inFlight.clear();next=state.count;
    }
   }
   if(state.root!==target.root||state.lastRecordHash!==target.lastRecordHash)throw Error('S163_FINAL_MISMATCH');
   const result=signed(targetName,'S161:FINISH',await rpc(targetName,'/finish161'));
   return{...result,elapsedMs:Number(process.hrtime.bigint()-start)/1e6,metrics:{...transport.metrics},pipeline:{...observed,window:fetchWindow,limit,batchMode,reuseTls}};
  }finally{ // Delayed read RPCs may resolve, but cannot mutate state.
    inFlight.clear();
  }
 }
 return{sync,rpc,transport,close:transport.close,observed};
}
module.exports={make,bound,chooseBatch};
