// OASIS {{i & dd}} v0.4 — typed gate packets, append-only SHA-256 hash chain,
// independent dense-matrix statevector reference implementation.
// Cryptographic hashes here are integrity checks, NOT signatures or external attestations.
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {compileTwin,applyGate,initialState,OPCODES,validateState,executeInstructions,inverseInstructions} from './gate-isa.mjs';
import {recoverTwin} from './i-dd-processor.mjs';
export const LEDGER_VERSION='i-dd-ledger/v0.4';
export const PACKET_VERSION='i-dd-instruction/v0.4';
export const EPSILON=1e-12;
const sha = value => createHash('sha256').update(JSON.stringify(value)).digest('hex');
const fail = why => {throw new Error('i-dd-v0.4: '+why)};
const copy = value => structuredClone(value);
const eq = (a,b)=>isDeepStrictEqual(a,b);
const abs2 = z => z[0]**2+z[1]**2;
const multiply=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]];
const plus=(a,b)=>[a[0]+b[0],a[1]+b[1]];
const stateNorm = s=>s.reduce((sum,x)=>sum+abs2(x),0);
export const maximumDifference=(a,b)=>Math.max(...a.map((c,i)=>Math.hypot(c[0]-b[i][0],c[1]-b[i][1])));

// Dense 8x8 complex-matrix oracle built by basis-column mapping. No optimized
// pairwise gate application from v0.3 is reused by this reference function.
export function referenceMatrixGate(state,ins){
  validateState(state);
  if(!ins || !OPCODES.includes(ins.op) || !Number.isInteger(ins.target) || ins.target<0 || ins.target>2) fail('bad gate target');
  const two=['CX','CZ','SWAP'].includes(ins.op);
  if(two ? !Number.isInteger(ins.control)||ins.control<0||ins.control>2||ins.target===ins.control : ins.control!==null) fail('bad gate control');
  const tmask=1<<(2-ins.target), cmask=two?1<<(2-ins.control):0;
  const a=Math.SQRT1_2;
  const single={X:[[[0,0],[1,0]],[[1,0],[0,0]]],
    H:[[[a,0],[a,0]],[[a,0],[-a,0]]],
    Z:[[[1,0],[0,0]],[[0,0],[-1,0]]],
    S:[[[1,0],[0,0]],[[0,0],[0,1]]],
    SDG:[[[1,0],[0,0]],[[0,0],[0,-1]]],
    T:[[[1,0],[0,0]],[[0,0],[a,a]]],
    TDG:[[[1,0],[0,0]],[[0,0],[a,-a]]]};
  const matrix=Array.from({length:8},()=>Array.from({length:8},()=>[0,0]));
  for(let col=0;col<8;col++){
    if(!two){
      const bit=(col&tmask)?1:0,zero=col&~tmask;
      matrix[zero][col]=copy(single[ins.op][0][bit]);
      matrix[zero|tmask][col]=copy(single[ins.op][1][bit]);
    } else if(ins.op==='CX'){
      matrix[(col&cmask)?col^tmask:col][col]=[1,0];
    } else if(ins.op==='CZ'){
      matrix[col][col]=[(col&cmask)&&(col&tmask)?-1:1,0];
    } else if(ins.op==='SWAP'){
      const t=(col&tmask)?1:0,ctrl=(col&cmask)?1:0;
      matrix[t===ctrl?col:col^tmask^cmask][col]=[1,0];
    }
  }
  const out=Array.from({length:8},()=>[0,0]);
  for(let r=0;r<8;r++)for(let col=0;col<8;col++)out[r]=plus(out[r],multiply(matrix[r][col],state[col]));
  if(Math.abs(stateNorm(out)-1)>1e-9) fail('reference oracle not normalized');
  return out;
}
export function createInstructionPackets(twin){
  recoverTwin(twin);
  const program=compileTwin(twin);
  const instructionPackets=program.instructions.map(ins=>{
    const packet={type:PACKET_VERSION,sequence:ins.step,coordinate:ins.address,
      ordinal:ins.ordinal,opcode:ins.op,target:ins.target,control:ins.control,
      sourceView:twin.identity.sourceView,identitySeal:twin.identity.seal,
      railWitness:twin.witness,programDigest:program.digest};
    return {...packet,packetDigest:sha(['typed-instruction',packet])};
  });
  return {program,packets:instructionPackets};
}
export function validateInstructionPackets(twin,provided){
  const expected=createInstructionPackets(twin);
  if(!Array.isArray(provided)||!eq(provided,expected.packets)) fail('typed packet mismatch');
  return true;
}
function toGate(packet){return {op:packet.opcode,target:packet.target,control:packet.control};}
export function buildLedger(twin,{initial='correlated'}={}){
  recoverTwin(twin);
  const {program,packets}=createInstructionPackets(twin);
  const first=initialState(initial);
  const header={ledger:LEDGER_VERSION,programDigest:program.digest,identitySeal:twin.identity.seal,
    railWitness:twin.witness,sourceView:twin.identity.sourceView,generation:twin.lineage.generation,
    initialKind:initial,initialHash:sha(['state',first]),gateCount:packets.length};
  const genesis=sha(['genesis',header]);
  let head=genesis,state=copy(first),worstDelta=0;
  const entries=[];
  for(const packet of packets){
    const gate=toGate(packet);
    const optimized=applyGate(state,gate);
    const independent=referenceMatrixGate(state,gate);
    const delta=maximumDifference(optimized,independent);
    if(delta>EPSILON) fail('independent simulator mismatch at gate '+packet.sequence);
    worstDelta=Math.max(worstDelta,delta);
    const body={sequence:packet.sequence,parentHead:head,packet,
      inputHash:sha(['state',state]),outputHash:sha(['state',optimized]),
      outputState:optimized,oracleMaxDelta:delta};
    const entry={...body,entryHash:sha(['ledger-entry',body])};
    entries.push(entry);head=entry.entryHash;state=optimized;
  }
  const undo=executeInstructions(inverseInstructions(program.instructions),state);
  const recoveryError=maximumDifference(undo,first);
  if(recoveryError>EPSILON) fail('inverse recovery exceeded tolerance');
  return {header,genesis,entries,head,summary:{gates:entries.length,simulatorMaxDelta:worstDelta,
    inverseRecoveryError:recoveryError,finalHash:sha(['state',state])}};
}
export function verifyLedger(twin,ledger){
  if(!ledger||typeof ledger!=='object'||!Array.isArray(ledger.entries)) fail('missing ledger');
  const rebuilt=buildLedger(twin,{initial:ledger.header?.initialKind});
  if(!eq(ledger,rebuilt)) fail('ledger does not match independently reconstructed execution');
  return {valid:true,entries:rebuilt.entries.length,head:rebuilt.head,
    simulatorMaxDelta:rebuilt.summary.simulatorMaxDelta,
    inverseRecoveryError:rebuilt.summary.inverseRecoveryError};
}