import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync} from 'node:fs';
import vm from 'node:vm';
import {makeTransition,verifyStrict,legalMove,applyMove, countOccupied} from './strict_t2_v2.mjs';

const SOURCE=readFileSync(new URL('./p13-i13-t2-original-pinned.mjs',import.meta.url));
const gitBlob=createHash('sha1').update(Buffer.concat([Buffer.from(`blob ${SOURCE.length}\0`),SOURCE])).digest('hex');
assert.equal(gitBlob,'49cb50bab98039e5b5c1b45e7e95f20cf76d3abe');
const sandbox={createHash, console:{log:()=>{}},process:{exitCode:0}};
vm.createContext(sandbox);
vm.runInContext(SOURCE.toString().replace('import { createHash } from "node:crypto";','')+'\n;globalThis.exportsT2={move,verify};', sandbox);
assert.equal(sandbox.process.exitCode,0);
const {move:sourceMove,verify:sourceVerify}=sandbox.exportsT2;

const PHYS=['in','out','vacant','occupied'];
const AXES=['3x3','abc','-abc'];
const isBinary=slots=>slots.every(c=>c==='vacant'||c==='occupied');
const observer=s=>({...s,slots:[...s.slots], axes:[...s.axes],witnessed:true});
function* fullStates(){
 for(let n=0;n<4**5;n++){
  let k=n,slots=[];
  for(let i=0;i<5;i++){slots.push(PHYS[k%4]);k=Math.floor(k/4);}
  for(const x of AXES)for(const y of AXES)for(const z of AXES)
   for(const witnessed of [false,true])yield {slots,axes:[x,y,z],witnessed};
 }
}
function liftTransition(s,from,to){
 if(!isBinary(s.slots) || !legalMove(s.slots,from,to)) return null;
 const tx=makeTransition(s.slots,from,to);
 if(!verifyStrict(tx))throw Error('STRICT_REFUTED_VALID_TRANSITION');
 return {slots:[...tx.after],axes:[...s.axes],witnessed:s.witnessed,tx};
}
let totalStates=0,admissibleStates=0,rejectedMixed=0,totalCandidates=0,
 legalLift=0,illegalLift=0,strictPass=0,sourceCompare=0,occupancyPass=0,
 axesPass=0,witnessPass=0,reversePass=0,sourceMutationPass=0,
 witnessCommutationPass=0,mixedSourceAccepted=0,unexpectedBugs=0;
const acceptedByOccupancy=[0,0,0,0,0,0];
let witnessError=null, firstMixedSource=null;
for(const s of fullStates()){
 totalStates++;
 const pure=isBinary(s.slots);
 if(pure)admissibleStates++;else rejectedMixed++;
 for(let from=0;from<5;from++)for(let to=0;to<5;to++){
  totalCandidates++;
  const before=JSON.stringify(s);
  const lifted=liftTransition(s,from,to);
  let originalAccepted=false, originalTx=null;
  try{originalTx=sourceMove(s.slots,from,to);originalAccepted=true;}catch{}
  if(!pure && originalAccepted){
   mixedSourceAccepted++;
   if(!firstMixedSource)firstMixedSource={slots:s.slots,from,to,operation:originalTx.operation};
  }
  if(!lifted){illegalLift++;if(pure&&originalAccepted)unexpectedBugs++;continue;}
  legalLift++;
  assert(pure&&originalAccepted);
  const m=lifted.tx;
  assert(sourceVerify(m));
  assert.equal(JSON.stringify(m.after),JSON.stringify([...originalTx.after]));
  assert.equal(m.receipt,originalTx.receipt);
  sourceCompare++;
  if(verifyStrict(m))strictPass++;
  if(countOccupied(s.slots)===countOccupied(lifted.slots))occupancyPass++;
  if(JSON.stringify(s.axes)===JSON.stringify(lifted.axes))axesPass++;
  if(s.witnessed===lifted.witnessed)witnessPass++;
  if(JSON.stringify(s.slots)===JSON.stringify(applyMove(lifted.slots,to,from)))reversePass++;
  if(JSON.stringify(s)===before)sourceMutationPass++;
  acceptedByOccupancy[countOccupied(s.slots)]++;
  const witnessedFirst=liftTransition(observer(s),from,to);
  const observedSecond=observer(lifted);
  if(witnessedFirst && JSON.stringify({slots:witnessedFirst.slots,axes:witnessedFirst.axes,witnessed:witnessedFirst.witnessed})===
       JSON.stringify({slots:observedSecond.slots,axes:observedSecond.axes,witnessed:observedSecond.witnessed}))
   witnessCommutationPass++;
  else if(!witnessError) witnessError={state:s,from,to};
 }
}
const oneSlice=32*27*2;
assert.equal(totalStates,4**5*3**3*2);
assert.equal(admissibleStates,oneSlice);
assert.equal(rejectedMixed,totalStates-oneSlice);
assert.equal(totalCandidates,totalStates*25);
assert.equal(legalLift,80*27*2);
assert.equal(illegalLift,totalCandidates-legalLift);
assert.deepEqual(acceptedByOccupancy,[0,540,1620,1620,540,0]);
for(const n of [strictPass,sourceCompare,occupancyPass,axesPass,witnessPass,reversePass,sourceMutationPass,witnessCommutationPass])assert.equal(n,legalLift);
assert.equal(mixedSourceAccepted,560*54);
assert.equal(unexpectedBugs,0);
assert.equal(witnessError,null);

// Domain attack: naïve projection destroys domain and yields 3^5 colliding all-vacant inputs.
const allVacantProjection=s=>s.map(x=>x==='occupied'?'occupied':'vacant');
const allZeroPreimages=3**5;
const witnesses=['vacant','in','out'];
let seenEmpty=0;
for(let n=0;n<4**5;n++){
 let k=n,slots=[];for(let i=0;i<5;i++){slots.push(PHYS[k%4]);k=Math.floor(k/4)}
 if(allVacantProjection(slots).every(x=>x==='vacant'))seenEmpty++;
}
assert.equal(seenEmpty,allZeroPreimages);
// Exact commutation against non-binary is not asserted: lift is defined only on admissible slice.
const result={
 schema:'ROOT0-P1.5-partial-refinement', originalGitBlob:gitBlob, originalSuite:'PASS',
 fullStateCount:totalStates, embeddedBinaryWitnessStates:admissibleStates, outsideDomain:rejectedMixed,
 slicePercent:100*admissibleStates/totalStates,
 candidateSourceTargetPairs:totalCandidates, legalLiftedMoves:legalLift,
 rejectedLiftedPairs:illegalLift, degreeByOccupancy:acceptedByOccupancy,
 strictAccepted:strictPass, originalMoveMatches:sourceCompare,
 conservedOccupancy:occupancyPass, retainedAxes:axesPass,retainedWitness:witnessPass,
 reversibleMoves:reversePass, retainedOriginalInput:sourceMutationPass,
 observerCommutationOnDefinedMoves:witnessCommutationPass,
 originalSourceMixedAlphabetAccepted:mixedSourceAccepted,
 firstMixedSource, naiveProjectionAllVacantPreimages:seenEmpty,
 refinements:{finiteEmbeddedSlice:'PASS',totalFrozenSpace:'FAIL_UNDEFINED_ON_IN_OUT',physicalExperimentPrediction:'NOT_ESTABLISHED',leanCompiled:false}
};
writeFileSync(new URL('./p15-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
