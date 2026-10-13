import assert from 'node:assert/strict';
import {ADDRESS_SPACE} from './diatom.mjs';
import {bindTwin,rotateTwin,mirrorReverse} from './i-dd-processor.mjs';
import {OPCODES,initialState,applyGate,executeInstructions} from './gate-isa.mjs';
import {createInstructionPackets,validateInstructionPackets,referenceMatrixGate,buildLedger,verifyLedger,maximumDifference} from './ledger.mjs';
let assertions=0;
const ok=(condition,msg)=>{assert.ok(condition,msg);assertions++;};
const eq=(a,b,msg)=>{assert.deepEqual(a,b,msg);assertions++;};
const reject=(action,msg)=>{assert.throws(action,Error,msg);assertions++;};
const addresses=ADDRESS_SPACE.map(a=>a.address);
const twin=bindTwin(addresses,{sourceView:2,positiveView:3,negativeView:6});
const typed=createInstructionPackets(twin);
const ledger=buildLedger(twin);
const proof=verifyLedger(twin,ledger);
ok(proof.valid,'verified');
eq(ledger.entries.length,42,'full 42 gate ledger');
ok(ledger.summary.simulatorMaxDelta<1e-12,'independent oracle');
ok(ledger.summary.inverseRecoveryError<1e-12,'inverse recovery');
validateInstructionPackets(twin,typed.packets);assertions++;
for(const entry of ledger.entries){
 eq(entry.packet.sequence,entry.sequence,'typed ordered sequence');
 ok(/^[0-9a-f]{64}$/.test(entry.entryHash),'hash present');
}
// All 10 gates against independent dense 8x8 reference on a complex state.
let initial=initialState('zero');
initial=applyGate(initial,{op:'H',target:0,control:null});
initial=applyGate(initial,{op:'T',target:0,control:null});
initial=applyGate(initial,{op:'H',target:1,control:null});
initial=applyGate(initial,{op:'S',target:1,control:null});
for(const opcode of OPCODES){
 for(let target=0;target<3;target++){
  const control=['CX','CZ','SWAP'].includes(opcode)?(target+1)%3:null;
  const gate={op:opcode,target,control};
  const a=applyGate(initial,gate),b=referenceMatrixGate(initial,gate);
  ok(maximumDifference(a,b)<1e-12,'all gate targets independent comparison');
 }
}
const changed=structuredClone(ledger);
changed.entries[4].outputState[0][0]+=0.03;
reject(()=>verifyLedger(twin,changed),'tampered state rejected');
const changedHash=structuredClone(ledger);
changedHash.entries[4].entryHash='0'.repeat(64);
reject(()=>verifyLedger(twin,changedHash),'tampered link rejected');
const changedPacket=structuredClone(typed.packets);
changedPacket[1].opcode='CX';
reject(()=>validateInstructionPackets(twin,changedPacket),'tampered packet rejected');
const reordered=structuredClone(ledger);
[reordered.entries[0],reordered.entries[1]]=[reordered.entries[1],reordered.entries[0]];
reject(()=>verifyLedger(twin,reordered),'reordered entries rejected');
const dropped=structuredClone(ledger);dropped.entries.pop();
reject(()=>verifyLedger(twin,dropped),'truncated ledger rejected');
const other=rotateTwin(twin,7,1);
reject(()=>verifyLedger(other,ledger),'reject foreign projection witness');
const child=mirrorReverse(twin);
reject(()=>verifyLedger(child,ledger),'reject foreign generation');
const emptyTwin=bindTwin([],{sourceView:7});
const emptyLedger=buildLedger(emptyTwin,{initial:'zero'});
ok(verifyLedger(emptyTwin,emptyLedger).valid,'empty stream');
let cases=0;
for (const address of addresses)for(let sv=0;sv<8;sv++)for(let dv=0;dv<8;dv++){
 const item=bindTwin([address],{sourceView:sv,positiveView:dv,negativeView:7-dv});
 const l=buildLedger(item);const v=verifyLedger(item,l);
 ok(v.valid&&v.entries===1,'coordinate/view replay');cases++;
}
console.log(JSON.stringify({status:'PASS',version:'v0.4',assertions,
 token_view_pair_cases:cases,typed_packets:typed.packets.length,ledger_entries:ledger.entries.length,
 independent_single_gate_oracle_cases:OPCODES.length*3,
 max_independent_simulator_delta:ledger.summary.simulatorMaxDelta,
 inverse_recovery_error:ledger.summary.inverseRecoveryError,
 ledger_head:ledger.head,malformed_tamper_cases:7,
 quantum_hardware:'NOT IMPLEMENTED'},null,2));