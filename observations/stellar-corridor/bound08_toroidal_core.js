/* OASIS | Natural Bound 08 | 2026-10-27
   Exact lazy cyclic Hamiltonian traversal on 24! permutations, with a
   synchronized 3-bit Gray register and 729 logical station addresses.

   No astronomical mass, acceleration, or energy is derived from permutations.
   No attempt is made to materialize the 24! states.

   Mathematical basis: Steinhaus-Johnson-Trotter "plain changes",
   recursive insertion of the new largest symbol from alternate ends.
   Every neighboring permutation differs by an adjacent swap, including seam.
*/
(function(root){
"use strict";
const OPERATORS=24;
const STATIONS=729;
const GRAY_PERIOD=8n;
function factorial(n){
 if(!Number.isInteger(n)||n<1||n>100)throw Error("factorial integer 1..100 required");
 let a=1n;
 for(let i=2n;i<=BigInt(n);i++)a*=i;
 return a;
}
const SIZE=factorial(OPERATORS);
const VISITS_PER_STATION=SIZE/BigInt(STATIONS);
if(SIZE%BigInt(STATIONS)!==0n||SIZE%GRAY_PERIOD!==0n)
 throw Error("The 729-station and 8-state Gray ring must divide the 24! cycle");
function normalizedRank(rank,n=OPERATORS){
 const count=factorial(n);
 let a=typeof rank==="bigint"?rank:BigInt(rank);
 return (a%count+count)%count;
}
function sjtUnrank(n,rank){
 if(!Number.isInteger(n)||n<1||n>OPERATORS)throw Error("operator count 1..24 required");
 let r=normalizedRank(rank,n);
 if(n===1)return [1];
 const quotient=r/BigInt(n);
 const digit=Number(r%BigInt(n));
 const perm=sjtUnrank(n-1,quotient);
 const slot=quotient%2n===0n?n-1-digit:digit;
 perm.splice(slot,0,n);
 return perm;
}
function sjtRank(perm){
 if(!Array.isArray(perm)||perm.length<1||perm.length>OPERATORS)
  throw Error("Expected a permutation of length 1..24");
 const n=perm.length;
 if(new Set(perm).size!==n||!perm.every(v=>Number.isInteger(v)&&v>=1&&v<=n))
  throw Error("Not a permutation of 1.."+n);
 if(n===1)return 0n;
 const slot=perm.indexOf(n);
 const ancestor=sjtRank(perm.filter(v=>v!==n));
 const digit=ancestor%2n===0n?n-1-slot:slot;
 return ancestor*BigInt(n)+BigInt(digit);
}
function grayNumber(rank){
 const phase=Number(normalizedRank(rank)%GRAY_PERIOD);
 return phase^(phase>>1);
}
function grayBits(rank){return grayNumber(rank).toString(2).padStart(3,"0");}
function stationIndex(rank){
 return Number(normalizedRank(rank)%BigInt(STATIONS));
}
function stationLabel(rank){return String(stationIndex(rank)).padStart(3,"0");}
function adjacentSwap(a,b){
 if(a.length!==b.length)throw Error("Permutations have different lengths");
 const diffs=[];
 for(let i=0;i<a.length;i++)if(a[i]!==b[i])diffs.push(i);
 if(diffs.length!==2||diffs[1]!==diffs[0]+1||a[diffs[0]]!==b[diffs[1]]||a[diffs[1]]!==b[diffs[0]])
  return null;
 return {leftIndex:diffs[0],rightIndex:diffs[1],
         leftSymbolBefore:a[diffs[0]],rightSymbolBefore:a[diffs[1]]};
}
function state(rank){
 const r=normalizedRank(rank);
 return {rank:r,gray:grayBits(r),grayNumber:grayNumber(r),
         station:stationIndex(r),stationLabel:stationLabel(r),
         permutation:sjtUnrank(OPERATORS,r),
         visitWithinStation:r/BigInt(STATIONS),
         nextRank:(r+1n)%SIZE};
}
function transition(rank,offset=1n){
 const a=state(rank),b=state(a.rank+BigInt(offset));
 const oneStep=offset===1n||offset===-1n;
 const swap=oneStep?adjacentSwap(a.permutation,b.permutation):null;
 const changedBits=(a.grayNumber^b.grayNumber).toString(2).split("1").length-1;
 return {before:a,after:b,adjacent:swap,
         grayHammingDistance:changedBits,
         isSingleStepValid:oneStep&&!!swap&&changedBits===1};
}
function selfTest(){
 const checks={};
 for(let n=2;n<=8;n++){
  const count=Number(factorial(n));
  const seen=new Set();
  let old=sjtUnrank(n,0n);
  for(let i=0;i<count;i++){
   const p=sjtUnrank(n,BigInt(i));
   const key=p.join(",");
   if(seen.has(key))throw Error("Repeated rank n="+n+" i="+i);
   seen.add(key);
   if(sjtRank(p)!==BigInt(i))throw Error("rank/unrank n="+n+" i="+i);
   if(i>0&&!adjacentSwap(old,p))throw Error("nonadjacent step n="+n+" i="+i);
   old=p;
  }
  if(!adjacentSwap(old,sjtUnrank(n,0n)))throw Error("seam n="+n);
  if(seen.size!==count)throw Error("exhaustiveness n="+n);
 }
 checks.smallNExhaustive="PASS n=2..8, including wrap";
 let cur=17n;
 const sample=[0n,1n,2n,8n,728n,729n,SIZE-1n,SIZE-2n,SIZE/2n,VISITS_PER_STATION];
 for(let i=0;i<600;i++){
  cur=(cur*6364136223846793005n+1442695040888963407n)%SIZE;
  sample.push(cur);
 }
 for(const r of sample){
  const p=sjtUnrank(OPERATORS,r);
  if(sjtRank(p)!==r)throw Error("24! rank/unrank roundtrip at "+r);
  const t=transition(r,1n);
  if(!t.isSingleStepValid)throw Error("24! adjacency / Gray at "+r);
  if(stationIndex(r)!==Number(r%729n))throw Error("station modulo");
 }
 checks.sampled24FactorialRanks="PASS "+sample.length+" exact BigInt ranks";
 if(SIZE!==620448401733239439360000n)throw Error("24! constant wrong");
 if(VISITS_PER_STATION!==851095201280163840000n)throw Error("visits/station wrong");
 if(state(0n).gray!=="000"||state(1n).gray!=="001")throw Error("opening 000 -> 001");
 if(state(SIZE-1n).gray!=="100")throw Error("closing Gray label wrong");
 if(stationIndex(0n)!==0||stationIndex(1n)!==1||stationIndex(SIZE-1n)!==728)
  throw Error("station boundary");
 const seam=transition(SIZE-1n,1n);
 if(!seam.isSingleStepValid||seam.adjacent.leftIndex!==0)throw Error("toroidal seam");
 checks.firstStep="000 -> 001; adjacent symbols 23 and 24";
 checks.seam="rank N-1 -> 0; Gray 100 -> 000; adjacent symbols 2 and 1";
 checks.fair729Visits="24!/729 exact = "+VISITS_PER_STATION;
 checks.grayPeriod="8, Gray one-bit for every step including cycle seam";
 checks.astronomicalClaim="NO: symbolic address projection only";
 return checks;
}
const api=Object.freeze({OPERATORS,STATIONS,SIZE,VISITS_PER_STATION,
 factorial,normalizedRank,sjtUnrank,sjtRank,grayBits,grayNumber,
 stationIndex,stationLabel,adjacentSwap,state,transition,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.Bound08Toroid=api;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
