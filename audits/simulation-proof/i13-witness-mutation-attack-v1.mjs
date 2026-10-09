/** I13 witness mutation attack. See original frozen tester in I13-H1.1.
 * Finite operational mutation testing, not empirical simulation evidence. */
import assert from "node:assert/strict";
const PHYSICAL=["in","out","vacant","occupied"],ORIENTATIONS=["3x3","abc","-abc"];
const MARKERS=["root-0","event-1"];
const encode=s=>JSON.stringify({physical:s.physical,orientation:s.orientation});
function* states(){
 for(let n=0;n<1024;n++){
  let cur=n,physical=[];
  for(let i=0;i<5;i++){physical.push(PHYSICAL[cur%4]);cur=Math.floor(cur/4);}
  for(const x of ORIENTATIONS)for(const y of ORIENTATIONS)for(const z of ORIENTATIONS)
   for(const witnessed of [false,true])yield{physical,orientation:[x,y,z],witnessed,ledger:[...MARKERS]};
 }
}
function validObserve(s){return{physical:[...s.physical],orientation:[...s.orientation],
 witnessed:true,ledger:[...s.ledger,`witness:${s.witnessed?'1':'0'}=>1`]};}
const target=s=>s.physical.every(x=>x==="in")&&s.orientation.every(x=>x==="3x3")&&!s.witnessed;
function poisonPayload(s){const t=validObserve(s);if(target(s))t.physical[0]="out";return t;}
function poisonHistory(s){const t=validObserve(s);if(target(s))t.ledger[0]="overwritten";return t;}
function audit(observe){
 let checked=0,payloadFaults=0,historyFaults=0,flipFaults=0,inputMutations=0,firstFault=null;
 for(const s of states()){
  const before=JSON.stringify(s),out=observe(s);checked++;
  const physicalSame=encode(s)===encode(out);
  const ledgerPrefix=s.ledger.length<=out.ledger.length&&s.ledger.every((entry,i)=>entry===out.ledger[i]);
  const witnessIsTrue=out.witnessed===true,sourceUnchanged=JSON.stringify(s)===before;
  if(!physicalSame)payloadFaults++;if(!ledgerPrefix)historyFaults++;
  if(!witnessIsTrue)flipFaults++;if(!sourceUnchanged)inputMutations++;
  if((!physicalSame||!ledgerPrefix||!witnessIsTrue||!sourceUnchanged)&&!firstFault)
    firstFault={source:encode(s),wasWitnessed:s.witnessed,physicalSame,ledgerPrefix,witnessIsTrue,sourceUnchanged};
 }
 return{checked,payloadFaults,historyFaults,flipFaults,inputMutations,firstFault,
 pass:payloadFaults===0&&historyFaults===0&&flipFaults===0&&inputMutations===0};
}
const baseline=audit(validObserve),injectedPhysical=audit(poisonPayload),
 injectedHistory=audit(poisonHistory);
assert.equal(baseline.checked,55296);
assert.equal(baseline.pass,true);
assert.equal(injectedPhysical.checked,55296);
assert.equal(injectedPhysical.payloadFaults,1);
assert.equal(injectedPhysical.pass,false);
assert.equal(injectedHistory.historyFaults,1);
assert.equal(injectedHistory.pass,false);
console.log(JSON.stringify({schema:"i13-witness-mutation-attack-v1",baseline,injectedPhysical,injectedHistory,
 frozenCheckerBlindSpot:"before and after are reconstructed from the same unchanged payload"},null,2));
