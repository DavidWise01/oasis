import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import vm from 'node:vm';

// Exact frozen SOURCE, not a substituted physical transition operator.
const source = readFileSync(new URL('./p13-i13-t2-original-pinned.mjs',import.meta.url));
const gitBlob = createHash('sha1').update(Buffer.concat([Buffer.from(`blob ${source.length}\0`),source])).digest('hex');
assert.equal(gitBlob,'49cb50bab98039e5b5c1b45e7e95f20cf76d3abe');
const cx = {createHash,console:{log(){}},process:{exitCode:0}};
vm.createContext(cx);
vm.runInContext(source.toString().replace('import { createHash } from "node:crypto";','')+'\n;globalThis.t2={move,verify}',cx,{timeout:5000});
assert.equal(cx.process.exitCode,0);
const {move:sourceMove,verify:sourceVerify}=cx.t2;

const SIGMA=['in','out','vacant','occupied'];
const N=5, PHYS=4**N, CONTEXTS=3**3*2;
const EDGES=[];for(let i=0;i<5;i++){EDGES.push([i,(i+1)%5]);EDGES.push([i,(i+4)%5]);}
function decode(n){const slots=[];for(let i=0;i<N;i++){slots.push(SIGMA[n%4]);n=Math.floor(n/4)}return slots;}
function encode(slots){let n=0,scale=1;for(let i=0;i<N;i++){let d=SIGMA.indexOf(slots[i]);assert(d>=0);n+=d*scale;scale*=4;}return n;}
function step(slots){
  for(let action=0;action<EDGES.length;action++){
    const [i,j]=EDGES[action];
    if(slots[i]!=='occupied'||slots[j]!=='vacant')continue;
    const before=JSON.stringify(slots);
    const tx=sourceMove(slots,i,j);
    assert(sourceVerify(tx));
    assert.equal(JSON.stringify(slots),before,'sourceMove unexpectedly mutated input');
    return {slots:[...tx.after],action,receipt:tx.receipt};
  }
  return {slots:[...slots],action:10,receipt:null}; // explicit STUTTER tag
}
const next=new Uint16Array(PHYS),actions=new Uint8Array(PHYS),fibres=Array.from({length:PHYS},()=>[]);
let transitionCases=0,stutters=0;
for(let s=0;s<PHYS;s++){
  const before=decode(s),out=step(before),y=encode(out.slots);
  next[s]=y;actions[s]=out.action;fibres[y].push(s);
  assert.deepEqual(decode(y),out.slots); // no tag transport loss
  if(out.action===10)stutters++;else transitionCases++;
}
for(const f of fibres)f.sort((a,b)=>a-b);
const rank=new Uint8Array(PHYS),width=new Uint8Array(PHYS);
let fixedCap=0, bitsVariable=0, shannon=0, tripleExample=null, ambiguousExamples=[];
const fibreHistogram={0:0,1:0,2:0,3:0};
for(let y=0;y<PHYS;y++){
  const fibre=fibres[y],m=fibre.length;
  assert(m<=3,'unexpected predecessor multiplicity');
  fibreHistogram[m]=(fibreHistogram[m]??0)+1;
  if(m===3&&!tripleExample)tripleExample={output:decode(y),predecessors:fibre.map(decode),actions:fibre.map(s=>actions[s])};
  if(m>1 && ambiguousExamples.length<3)ambiguousExamples.push({output:decode(y),predecessors:fibre.map(decode)});
  for(let k=0;k<m;k++){
    const x=fibre[k];rank[x]=k;width[x]=Math.ceil(Math.log2(m));
    bitsVariable+=width[x];
    shannon+=Math.log2(m)/PHYS;
    fixedCap=Math.max(fixedCap,width[x]);
    assert.equal(fibre[rank[x]],x);
  }
}
assert.deepEqual(fibreHistogram,{0:91,1:847,2:81,3:5}); // 91 outputs unreachable under scheduler
assert.equal(transitionCases,450);
assert.equal(stutters,574);
assert.equal(bitsVariable,192);
assert.equal(fixedCap,2);
const perContextUnique=fibreHistogram[1]+fibreHistogram[2]+fibreHistogram[3];
assert.equal(perContextUnique,933);
assert.equal(perContextUnique*CONTEXTS,50382);
assert.equal(bitsVariable*CONTEXTS,10368);
let reconstructed=0,oneStepTaggedCollisions=0;
const keyedPairs=new Set();
for(let ctx=0;ctx<CONTEXTS;ctx++){
  for(let s=0;s<PHYS;s++){
    const y=next[s],k=rank[s],sourceRecovered=fibres[y][k];
    assert.equal(sourceRecovered,s);
    // 'ctx' carries all orientation and witness metadata forward unchanged.
    const pair=`${ctx}:${y}:${k}`;
    if(keyedPairs.has(pair))oneStepTaggedCollisions++;else keyedPairs.add(pair);
    reconstructed++;
  }
}
assert.equal(oneStepTaggedCollisions,0);
assert.equal(reconstructed,55296);
assert.equal(keyedPairs.size,55296);
// Every physical word, every independently carried orientation/witness flag, 20 steps.
let recoveredPaths=0,recoveredTransitions=0,badRankRejections=0;
for(let ctx=0;ctx<CONTEXTS;ctx++)for(let initial=0;initial<PHYS;initial++){
  let current=initial;const tags=[];
  for(let t=0;t<20;t++){
    tags.push(rank[current]);current=next[current];recoveredTransitions++;
  }
  for(let t=19;t>=0;t--){
    const before=fibres[current][tags[t]];
    assert(before!==undefined,'unrecognized predecessor rank');
    assert.equal(next[before],current);
    current=before;
  }
  assert.equal(current,initial);
  recoveredPaths++;
}
assert.equal(recoveredPaths,55296);
assert.equal(recoveredTransitions,1105920);
// A forced out-of-range rank is refused.
for(const fibre of fibres){if(fibre.length>0 && fibre.length<3){assert.equal(fibre[3],undefined);badRankRejections++}}
// Tag authenticity is separate: two *correctly encoded* alternatives can share the same output.
const y3=encode(tripleExample.output);
const alternatives=fibres[y3];
assert.equal(alternatives.length,3);
for(let k=0;k<3;k++)assert.equal(next[alternatives[k]],y3);
assert.notEqual(alternatives[0],alternatives[1]);

const result={
 schema:'ROOT0-P1.8-conditional-predecessor-code',frozenSourceGitBlob:gitBlob,
 fullCarrierStates:PHYS*CONTEXTS,physicalWords:PHYS,contexts:CONTEXTS,
 oneStepStateOnlyDistinctImages:perContextUnique*CONTEXTS,
 physicalOutputsWithNoPredecessor:fibreHistogram[0],
 physicalOutputFibreHistogram:fibreHistogram,
 physicalMoves:transitionCases,physicalStutters:stutters,
 worstCasePredecessorCount:3,worstCaseMinimalBits:fixedCap,
 globalEdgeOrStutterActionCount:EDGES.length+1,globalFixedActionBits:Math.ceil(Math.log2(EDGES.length+1)),
 conditionalCodeMeanBitsPerState:bitsVariable/PHYS,
 conditionalEntropyUniformPriorBits:shannon,
 conditionalPrefixlessWidthBitsTotalForFullCarrier:bitsVariable*CONTEXTS,
 uniqueTaggedPairs:keyedPairs.size,oneStepTaggedCollisions,
 oneStepRecovered:reconstructed,
 reversePaths:recoveredPaths,stepsPerPath:20,reversedStepChecks:recoveredTransitions,
 invalidRankTestCases:badRankRejections,
 tripleExample, ambiguousExamples,
 detectedLimits:{requiresKnowledgeOfExactScheduler:true,requiresCorrectOutputAndRank:true,unauthenticatedRankCanSelectAnotherValidPredecessor:true,oneStepAverageEntropyDependsOnUniformInitialPrior:true},
 leanCompilerAvailable:false,physicalPredictionWithUnits:false,simulationTheoryEstablished:false,
 status:'PASS_FINITE_INFORMATION_LOSS_BOUND_AND_EXHAUSTIVE_INVERSE'
};
const dest=new URL('./P18-results.json',import.meta.url);
writeFileSync(dest,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));