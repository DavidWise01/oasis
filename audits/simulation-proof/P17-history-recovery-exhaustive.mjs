import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import vm from 'node:vm';

const src=readFileSync(new URL('./p13-i13-t2-original-pinned.mjs',import.meta.url));
const blob=createHash('sha1').update(Buffer.concat([Buffer.from(`blob ${src.length}\0`),src])).digest('hex');
assert.equal(blob,'49cb50bab98039e5b5c1b45e7e95f20cf76d3abe');
const cx={createHash,console:{log(){}},process:{exitCode:0}};
vm.createContext(cx);
vm.runInContext(src.toString().replace('import { createHash } from "node:crypto";','')+'\n;globalThis.t2={move,verify}',cx,{timeout:5000});
assert.equal(cx.process.exitCode,0);
const {move:sourceMove,verify:sourceVerify}=cx.t2;
const SIGMA=['in','out','vacant','occupied'], ORIENT=['3x3','abc','-abc'];
const sha=s=>createHash('sha256').update(s).digest('hex');
const hashState=s=>sha(JSON.stringify([s.slots,s.axes,s.witnessed]));
const edges=[];for(let i=0;i<5;i++){edges.push([i,(i+1)%5]);edges.push([i,(i+4)%5])}
const legal=(slots,i,j)=> slots[i]==='occupied'&&slots[j]==='vacant'&&((i+1)%5===j||(i+4)%5===j);
const clone=s=>({slots:[...s.slots],axes:[...s.axes],witnessed:s.witnessed});
const stateKey=s=>JSON.stringify([s.slots,s.axes,s.witnessed]);
const equalState=(s,t)=>stateKey(s)===stateKey(t);
function step(s){
  for(const [i,j] of edges){
    if(!legal(s.slots,i,j))continue;
    const tx=sourceMove(s.slots,i,j);
    assert(sourceVerify(tx));
    return {state:{slots:[...tx.after],axes:[...s.axes],witnessed:s.witnessed},action:[i,j],originalReceipt:tx.receipt};
  }
  return {state:clone(s),action:null,originalReceipt:null};
}
function undo(current,action){
  const prev=clone(current);
  if(action!==null){
    assert(Array.isArray(action)&&action.length===2);
    const [i,j]=action;
    assert(edges.some(([a,b])=>a===i&&b===j));
    // Original T2's inverse move is legal for a previously legal forward edge.
    const tx=sourceMove(prev.slots,j,i);
    prev.slots=[...tx.after];
  }
  const replay=step(prev);
  assert(equalState(replay.state,current));
  assert.deepEqual(replay.action,action);
  return prev;
}

function* states(){
 for(let id=0;id<4**5;id++){
  let c=id,slots=[];for(let i=0;i<5;i++){slots.push(SIGMA[c%4]);c=Math.floor(c/4)}
  for(let x=0;x<3;x++)for(let y=0;y<3;y++)for(let z=0;z<3;z++)for(let w=0;w<2;w++)
    yield {slots:[...slots],axes:[ORIENT[x],ORIENT[y],ORIENT[z]],witnessed:w};
 }
}
let sourceCount=0,injectiveCollision=0,undoPass=0,stutters=0,fullMove=0,sourceUntouched=0;
const imageAction=new Set(),imageFibre=new Map(),fibreDist=new Map();let collisionWitness=null;
for(const s of states()){
 const original=stateKey(s),{state:next,action}=step(s);sourceCount++;
 if(original===stateKey(s))sourceUntouched++;
 if(action===null)stutters++;else fullMove++;
 if(equalState(undo(next,action),s))undoPass++;
 const aug=JSON.stringify([stateKey(next),action]);
 if(imageAction.has(aug))injectiveCollision++;else imageAction.add(aug);
 const k=stateKey(next);const old=imageFibre.get(k)||[];
 if(old.length===1&&!collisionWitness)collisionWitness={twoPredecessors:[old[0],original],sharedNext:k};
 old.push(original);imageFibre.set(k,old);
}
for(const preimages of imageFibre.values())fibreDist.set(preimages.length,(fibreDist.get(preimages.length)||0)+1);
const maxFibre=Math.max(...fibreDist.keys());
const largestFibre=[...imageFibre.entries()].find(([,prior])=>prior.length===maxFibre);
assert(largestFibre && largestFibre[1].length===3);
const tripleExample={next:JSON.parse(largestFibre[0]),predecessors:largestFibre[1].map(x=>JSON.parse(x))};
const tripleActions=tripleExample.predecessors.map(([slots,axes,witnessed])=>step({slots,axes,witnessed}).action);
assert.equal(new Set(tripleActions.map(v=>JSON.stringify(v))).size,3);
tripleExample.actions=tripleActions;
const overwrittenFibre=[...fibreDist.entries()].sort((a,b)=>a[0]-b[0]);
assert.equal(sourceCount,55296);assert.equal(undoPass,55296);assert.equal(injectiveCollision,0);
assert.equal(sourceUntouched,55296);assert.equal(stutters,30996);assert.equal(fullMove,24300);
assert.equal(sourceCount-[...imageFibre.keys()].length,4914);
assert(maxFibre>1);

// Append-only authenticated-by-anchor history: not a signature!
const originHash='0'.repeat(64);
function append(seq,prevDigest,before,{state:after,action,originalReceipt}){
 const body={seq,prevDigest,beforeHash:hashState(before),afterHash:hashState(after),action,originalReceipt};
 return {...body,digest:sha(JSON.stringify(body))};
}
function generate(s,count){
 const events=[];let state=clone(s),prevDigest=originHash;
 for(let seq=0;seq<count;seq++){
  const outcome=step(state),event=append(seq,prevDigest,state,outcome);
  events.push(event);state=outcome.state;prevDigest=event.digest;
 }
 return {start:clone(s),final:state,events,anchor:prevDigest};
}
function verifyTranscript(trace,trustStart=true,trustAnchor=true){
 const {events}=trace;
 if(!Array.isArray(events)||!trace.final||!trace.start)return false;
 let current=clone(trace.start),prevDigest=originHash;
 try{
  for(let i=0;i<events.length;i++){
   const e=events[i], outcome=step(current);
   if(e.seq!==i||e.prevDigest!==prevDigest||e.beforeHash!==hashState(current)||e.afterHash!==hashState(outcome.state)||
      JSON.stringify(e.action)!==JSON.stringify(outcome.action)||e.originalReceipt!==outcome.originalReceipt)return false;
   const body={seq:e.seq,prevDigest:e.prevDigest,beforeHash:e.beforeHash,afterHash:e.afterHash,action:e.action,originalReceipt:e.originalReceipt};
   if(e.digest!==sha(JSON.stringify(body)))return false;
   current=outcome.state;prevDigest=e.digest;
  }
  if(!equalState(current,trace.final))return false;
  if(trustStart && !equalState(trace.start,trace.trustedStart??trace.start))return false;
  if(trustAnchor && prevDigest!==trace.trustedAnchor)return false;
  return true;
 }catch{return false}
}
function reverseTranscript(final,events){
 let current=clone(final);
 for(let i=events.length-1;i>=0;i--){
  if(hashState(current)!==events[i].afterHash)throw Error('MISMATCHED_AFTER_EVENT');
  current=undo(current,events[i].action);
  if(hashState(current)!==events[i].beforeHash)throw Error('MISMATCHED_BEFORE_EVENT');
 }
 return current;
}
const cycleStart={slots:['occupied','vacant','vacant','vacant','vacant'],axes:['3x3','abc','-abc'],witnessed:0};
const t15=generate(cycleStart,15);t15.trustedAnchor=t15.anchor;t15.trustedStart=t15.start;
assert(verifyTranscript(t15));assert(equalState(reverseTranscript(t15.final,t15.events),cycleStart));
assert(equalState(t15.start,t15.final));
assert.equal(t15.events.length,15);
assert.equal(new Set(t15.events.map(e=>e.digest)).size,15);
// Need compare actual V1 receipt repetitions: cycle path should repeat every 5 steps.
assert.equal(t15.events[0].originalReceipt,t15.events[5].originalReceipt);
assert.equal(t15.events[5].originalReceipt,t15.events[10].originalReceipt);
assert.notEqual(t15.events[0].digest,t15.events[5].digest);

// Full-path backward recovery on 400 diverse seeds through 20 transitions.
let extendedRecovered=0, extendedChecks=0;
for(const s of states()){
 if(extendedChecks%138!==0){extendedChecks++;continue}
 const trace=generate(s,20);trace.trustedAnchor=trace.anchor;trace.trustedStart=trace.start;
 assert(verifyTranscript(trace));
 assert(equalState(reverseTranscript(trace.final,trace.events),s));
 extendedRecovered++;extendedChecks++;
}
function cloneTrace(t){return JSON.parse(JSON.stringify(t))}
const attackResults={};
const alterations={
  deleted:t=>t.events.splice(3,1),
  reordered:t=>[t.events[2],t.events[3]]=[t.events[3],t.events[2]],
  replayed:t=>t.events.splice(4,0,t.events[3]),
  payloadTampered:t=>t.events[4].afterHash='f'.repeat(64),
  digestTampered:t=>t.events[4].digest='a'.repeat(64),
  operationTampered:t=>t.events[4].action=[0,4],
  wrongAnchor:t=>t.trustedAnchor='f'.repeat(64)
};
for(const [label,mutation] of Object.entries(alterations)){
 const attack=cloneTrace(t15);mutation(attack);
 attackResults[label]=!verifyTranscript(attack);
 assert.equal(attackResults[label],true,label);
}
// Alternative valid histories (both generated honestly) have the SAME final state, but different starts
// and different root digests. If nobody trusts either initial state or the final anchor, neither
// the cryptographic chaining nor equality of final state selects which physical history was real.
const x={slots:['occupied','vacant','vacant','in','in'],axes:['3x3','3x3','3x3'],witnessed:0};
const y={slots:['vacant','vacant','occupied','in','in'],axes:['3x3','3x3','3x3'],witnessed:0};
const histA=generate(x,1),histB=generate(y,1);
assert(equalState(histA.final,histB.final));
assert.notEqual(histA.anchor,histB.anchor);
histA.trustedAnchor=histA.anchor;histB.trustedAnchor=histB.anchor;
assert(verifyTranscript(histA));assert(verifyTranscript(histB));
const alternateUnderTrustedA=cloneTrace(histB);alternateUnderTrustedA.trustedAnchor=histA.anchor;
assert.equal(verifyTranscript(alternateUnderTrustedA),false);
assert(equalState(reverseTranscript(histA.final,histA.events),x));
assert(equalState(reverseTranscript(histB.final,histB.events),y));
// An attacker can make a fully valid self-consistent rehashed alternative without external anchoring.
const evidence={
 name:'ROOT0-I13-P1.7-recoverability',originalGitBlob:blob,
 fullFrozenStates:sourceCount,immediateMoveStates:fullMove,stutters,
 schedulerDistinctImages:imageFibre.size,duplicateInputImages:sourceCount-imageFibre.size,
 maxFibre, fibreDistribution:Object.fromEntries(overwrittenFibre),
 tripleExample,
 oneStepActionTaggedInjective:imageAction.size===sourceCount,
 actionTaggedCollisions:injectiveCollision,recoverableOneStep:undoPass,
 informationLowerBoundBitsPerAmbiguousImage:Math.ceil(Math.log2(maxFibre)),
 cycle15:{length:15,physicalStateReturned:equalState(t15.start,t15.final),
   originalReceiptRepeat:[0,5,10].map(i=>t15.events[i].originalReceipt),
   distinctEventDigests:new Set(t15.events.map(e=>e.digest)).size,historyRecovered:true},
 twentyStepSample:{tested:extendedRecovered,stepsPerTest:20,reverseRecoveryPass:extendedRecovered},
 detectedAttacks:attackResults,
 alternativeOriginsSameFinal:{differentStarts:true,fullyValidHistories:true,differentChainAnchors:true,otherHistoryFailsWhenCheckedAgainstOriginalAnchor:true,
  needsExternalTrustToChooseHistoricallyActual:true},
 theorem:'Pair (deterministic next state, chosen directed edge or stutter marker) is injective over frozen carrier.',
 physicalTimeDemonstrated:false,simulationTheoryProven:false,
 leanCompiled:false,classification:'FINITE_MODEL_PROOF_ONLY'
};
writeFileSync(new URL('./P17-results.json',import.meta.url),JSON.stringify(evidence,null,2)+'\n');
console.log(JSON.stringify(evidence,null,2));
