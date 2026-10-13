import assert from 'node:assert/strict';
import {ADDRESS_SPACE} from './diatom.mjs';
import {bindTwin,rotateTwin,recoverTwin} from './i-dd-processor.mjs';
import {OPCODES,ISA,mapAddress,compileTwin,verifyProgram,executeTwin,
 initialState,applyGate,inverseInstructions,executeInstructions,
 probabilityDistribution,reducedDensity,purity} from './gate-isa.mjs';
let checks=0;
function eq(a,b,name){assert.deepEqual(a,b,name);checks++;}
function ok(cond,name){assert.ok(cond,name);checks++;}
function reject(fn,name){assert.throws(fn,Error,name);checks++;}
const tol=1e-12;
const near=(x,y,name)=>ok(Math.abs(x-y)<tol,name+` ${x} vs ${y}`);
const close=(a,b,name)=>{ok(a.length===b.length,name+' length');for(let i=0;i<a.length;i++)for(let j=0;j<2;j++) near(a[i][j],b[i][j],name+`[${i}][${j}]`);};
const addresses=ADDRESS_SPACE.map(x=>x.address);
const full=bindTwin(addresses,{sourceView:2,positiveView:3,negativeView:6});
const run=executeTwin(full);
eq(recoverTwin(full),addresses,'source preserved');
eq(run.program.instructions.length,42,'42 gate instructions');
eq(run.program.isa,ISA,'ISA tag');
ok(run.maxError<tol,'full circuit reversible');
eq(new Set(run.program.instructions.map(x=>x.op)).size,10,'all 10 ops represented');
for(let i=0;i<3;i++)near(run.purities[i],purity(run.final,i),'reported density purity');
near(run.distribution.reduce((s,x)=>s+x.probability,0),1,'probability 1');
const rot=rotateTwin(full,7,1), runRot=executeTwin(rot);
eq(run.program.instructions,runRot.program.instructions,'view-independent compiled gates');
close(run.final,runRot.final,'view-independent state');
ok(run.program.digest!==runRot.program.digest,'projection-specific program digest');
ok(full.identity.seal===rot.identity.seal,'identity seal preserved across projections');
reject(()=>verifyProgram(run.program,rot),'reject program bound to other witness');
const tampered=structuredClone(full);tampered.rails.negative.cells[0].nodes[0]='i1:0';
reject(()=>compileTwin(tampered),'reject altered carrier');
const tamperedHash=structuredClone(full);tamperedHash.witness='0'.repeat(64);
reject(()=>executeTwin(tamperedHash),'reject altered witness');
// Core 2,688 token/view-pair cases are each compiled, simulated, and recovered.
let roundTripCases=0;
for (const addr of addresses) for (let sourceView=0;sourceView<8;sourceView++) for (let destinationView=0;destinationView<8;destinationView++){
 const twin=bindTwin([addr],{sourceView,positiveView:destinationView,negativeView:7-destinationView});
 const {program,maxError,distribution}=executeTwin(twin);
 eq(program.instructions[0].address,addr,'coordinate preserved');
 ok(maxError<tol,'inverse gate state recovery');
 near(distribution.reduce((s,x)=>s+x.probability,0),1,'unitary norm');
 roundTripCases++;
}
// Every supported operation is unitary with explicit inverse on a complex superposition.
const complex=initialState('zero');
let s=applyGate(complex,{op:'H',target:0,control:null});
s=applyGate(s,{op:'S',target:0,control:null});
s=applyGate(s,{op:'H',target:1,control:null});
s=applyGate(s,{op:'T',target:1,control:null});
for (const op of OPCODES){
 const ins={op,target:2,control:['CX','CZ','SWAP'].includes(op)?1:null};
 const transformed=applyGate(s,ins);
 const inversed=inverseInstructions([ins]);
 close(executeInstructions(inversed,transformed),s,'single operation inverse '+op);
 near(probabilityDistribution(transformed).reduce((n,x)=>n+x.probability,0),1,'unitary '+op);
}
// Prepare a known 3-qubit entangled GHZ state from |000> using H and CNOT gates.
const ghzCircuit=[{op:'H',target:0,control:null},
 {op:'CX',target:1,control:0},{op:'CX',target:2,control:0}];
const ghz=executeInstructions(ghzCircuit,initialState('zero'));
const ghzDist=probabilityDistribution(ghz);
near(ghzDist[0].probability,.5,'GHZ |000> 50%');
near(ghzDist[7].probability,.5,'GHZ |111> 50%');
for (let i=1;i<7;i++)near(ghzDist[i].probability,0,'GHZ no other outcomes');
for(let q=0;q<3;q++){
 const rho=reducedDensity(ghz,q);
 near(rho[0][0][0],.5,'GHZ marginal 0');
 near(rho[1][1][0],.5,'GHZ marginal 1');
 near(purity(ghz,q),.5,'GHZ entanglement mathematical check');
}
// Configuration validation and negative examples.
reject(()=>mapAddress('i9:0',0),'bad source token');
reject(()=>mapAddress('i1:0',-1),'negative sequence');
reject(()=>applyGate(initialState('zero'),{op:'CX',control:1,target:1}),'self-control');
reject(()=>applyGate(initialState('zero'),{op:'MEASURE',control:null,target:0}),'no irreversible measurement in gate ISA');
reject(()=>applyGate(Array(8).fill([2,0]),{op:'H',control:null,target:0}),'unnormalized input');
reject(()=>executeInstructions([],Array(8).fill([NaN,0])),'NaN state rejected');
console.log(JSON.stringify({status:'PASS',release:'{{i & dd}}/v0.3',
    token_view_pair_cases:roundTripCases,assertions:checks,operations:OPCODES,
    full_stream_tokens:42,carriers:2,cells:22,full_circuit_max_inverse_error:run.maxError,
    source_identity_seal:full.identity.seal,source_rail_witness:full.witness,
    program_digest:run.program.digest,output_digest:run.outputDigest,
    ghz_distribution:{'000':ghzDist[0].probability,'111':ghzDist[7].probability},
    hardware_quantum_entanglement:'NOT CLAIMED'},null,2));