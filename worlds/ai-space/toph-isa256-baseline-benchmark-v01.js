'use strict';
/* Run with: node worlds/ai-space/toph-isa256-baseline-benchmark-v01.js
   Local checkout must have the.source code at environment TOPH_ISA256_SOURCE_PATH.
   No repo/production code is modified. */
const assert=require('node:assert/strict');
const {performance}=require('node:perf_hooks');
const source=process.env.TOPH_ISA256_SOURCE_PATH;
if(!source)throw Error('Set TOPH_ISA256_SOURCE_PATH to exact the.source TOPH-Kernel-v1.0/isa256-kernel.js');
const {execute,createObserveTellShareLoop}=require(source);
const checks=[];
function test(name,fn){try{assert.ok(fn());checks.push({name,status:'PASS'});}catch(e){checks.push({name,status:'FAIL',reason:e.message});}}
function rejected(fn){try{fn();return false}catch{return true}}
for(const n of [1,4,32]){
 const p=createObserveTellShareLoop(n),a=execute(p),b=execute(p);
 test('deterministic_'+n,()=>JSON.stringify(a)===JSON.stringify(b));
 test('accounting_'+n,()=>a.cycles===5*n+1&&a.witness.length===n+1&&a.mode==='perp');
}
test('reject_unknown_opcode',()=>rejected(()=>execute([{op:'UNKNOWN'}])));
test('reject_nonarray',()=>rejected(()=>execute('OBSERVE')));
test('halt_stops',()=>execute([{op:'HALT'},{op:'OBSERVE'}]).signals.observe===0);
test('reject_negative_signal',()=>rejected(()=>execute([{op:'OBSERVE',arg:-5},{op:'HALT'}])));
test('reject_unsafe_seed',()=>rejected(()=>execute([{op:'HALT'}],{observe:1e99})));
test('register_readback',()=>Array.isArray(execute([{op:'LOAD_IMM',dst:0,arg:5},{op:'HALT'}]).registers));
test('witness_integrity_hash',()=>execute([{op:'DOT'},{op:'HALT'}]).witness.every(w=>typeof w.hash==='string'));
const n=50000,p=createObserveTellShareLoop(n),start=performance.now(),r=execute(p),duration_s=(performance.now()-start)/1000;
const report={schema:'oasis/benchmark/toph-isa256/v01',node:process.version,checks,passed:checks.filter(x=>x.status==='PASS').length,failed:checks.filter(x=>x.status==='FAIL').length,throughput:{instructions:p.length,seconds:duration_s,instructions_per_second:Math.round(p.length/duration_s),witnesses:r.witness.length},note:'Measured dispatch throughput only. Checks 10-13 are desired hardening capabilities, not asserted historical source features.'};
console.log(JSON.stringify(report,null,2));
