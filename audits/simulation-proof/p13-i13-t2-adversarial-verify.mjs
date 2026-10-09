import assert from "node:assert/strict";
import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import vm from "node:vm";
// Original frozen code is a byte-for-byte pinned Git snapshot in the same folder.
const src=readFileSync(new URL("./p13-i13-t2-original-pinned.mjs",import.meta.url));
const blob=createHash("sha1").update(Buffer.concat([Buffer.from("blob "+src.length+"\0"),src])).digest("hex");
assert.equal(blob,"49cb50bab98039e5b5c1b45e7e95f20cf76d3abe");
const context={createHash,console:{log(){}},process:{exitCode:0}};
vm.createContext(context);
vm.runInContext(src.toString().replace('import { createHash } from "node:crypto";','')+
 "\n;globalThis.EXPORTED={move,verify,sha256,canonical};",context);
assert.equal(context.process.exitCode,0);
const {move,verify,sha256,canonical}=context.EXPORTED;
const hash=t=>sha256(canonical(t.before)+"::"+t.operation+"::"+canonical(t.after));
const sign=t=>({...t,receipt:hash(t)});
const base=["occupied","vacant","vacant","vacant","vacant"];
function strict(t){
 if(!Array.isArray(t.before)||!Array.isArray(t.after)||t.before.length!==5||t.after.length!==5)return false;
 if(![...t.before,...t.after].every(x=>x==="occupied"||x==="vacant"))return false;
 const m=/^move:([0-4])->([0-4])(:\|\|\|)?$/.exec(t.operation);
 if(!m)return false;
 try{
  const legal=move(t.before,Number(m[1]),Number(m[2]));
  return legal.operation===t.operation &&
    JSON.stringify(legal.after)===JSON.stringify(t.after) &&
    legal.receipt===t.receipt && verify(t);
 }catch{return false}
}
const forged=[
 ["nonadjacent",sign({before:base,operation:"move:0->2",after:["vacant","vacant","occupied","vacant","vacant"]})],
 ["occupancyCreated",sign({before:base,operation:"move:0->1",after:["vacant","occupied","occupied","vacant","vacant"]})],
 ["occupancyLost",sign({before:base,operation:"move:0->1",after:["vacant","vacant","vacant","vacant","vacant"]})],
 ["falseSeam",sign({before:base,operation:"move:0->4:|||",after:["vacant","occupied","vacant","vacant","vacant"]})],
 ["alienValue",sign({before:["occupied","alien","vacant","vacant","vacant"],operation:"move:0->1",after:["vacant","occupied","vacant","vacant","vacant"]})],
 ["unknownOperator",sign({before:base,operation:"invoke:override",after:["vacant","occupied","vacant","vacant","vacant"]})]
];
for(const [name,t] of forged){assert(verify(t),name+" raw expected acceptance");assert(!strict(t),name+" strict expected rejection");}
let candidates=0,legal=0,strictPass=0,conservation=0;
for(let mask=0;mask<32;mask++){
 const state=Array.from({length:5},(_,i)=>(mask>>i)&1?"occupied":"vacant");
 for(let f=0;f<5;f++)for(let t=0;t<5;t++){
  candidates++;
  try{
   const result=move(state,f,t);legal++;
   if(strict(result))strictPass++;
   if(result.before.filter(x=>x==="occupied").length===result.after.filter(x=>x==="occupied").length)conservation++;
  }catch{}
 }
}
assert.equal(candidates,800);assert.equal(legal,80);assert.equal(strictPass,80);assert.equal(conservation,80);
const sourceAdmitsAlien=move(["occupied","vacant","alien","vacant","vacant"],0,1);
assert(verify(sourceAdmitsAlien));assert(!strict(sourceAdmitsAlien));
console.log(JSON.stringify({schema:"ROOT0-I13-P1.3",gitBlob:blob,originalSuite:"PASS",candidates,legal,strictPass,conservation,forgedRawAccepted:6,forgedStrictAccepted:0,sourceAdmitsAlien:true,leanCompiled:false,physicalSimulationProven:false},null,2));
