// OASIS {{i & dd}} reversible gate ISA v0.3 — classical 3-qubit statevector simulator.
// Purely mathematical quantum model; no physical qubits or quantum advantage claimed.
import {createHash} from 'node:crypto';
import {ADDRESS_SPACE} from './diatom.mjs';
import {recoverTwin} from './i-dd-processor.mjs';
import {STATE as GHZ_STATE} from './three-qubit.mjs';

export const ISA='i-dd-gates/v0.3';
export const QUBITS=['i_branch','d+','d-'];
export const OPCODES=Object.freeze(['X','H','Z','S','SDG','T','TDG','CX','CZ','SWAP']);
const ADDRESS_INDEX = new Map(ADDRESS_SPACE.map((t,i)=>[t.address,i]));
const SQRT2=Math.sqrt(2), INV=Math.SQRT1_2;
const c=(re,im=0)=>[re,im];
const ADD=(a,b)=>[a[0]+b[0],a[1]+b[1]];
const MUL=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]];
const mat={
 X:[[c(0),c(1)],[c(1),c(0)]],
 H:[[c(INV),c(INV)],[c(INV),c(-INV)]],
 Z:[[c(1),c(0)],[c(0),c(-1)]],
 S:[[c(1),c(0)],[c(0),c(0,1)]],
 SDG:[[c(1),c(0)],[c(0),c(0,-1)]],
 T:[[c(1),c(0)],[c(0),c(INV,INV)]],
 TDG:[[c(1),c(0)],[c(0),c(INV,-INV)]]
};
const inverse={X:'X',H:'H',Z:'Z',S:'SDG',SDG:'S',T:'TDG',TDG:'T',CX:'CX',CZ:'CZ',SWAP:'SWAP'};
const digest=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
function fail(s){throw new Error('i-dd-isa: '+s);}
function isIndex(n){return Number.isInteger(n)&&n>=0&&n<=2;}
function norm(state){return state.reduce((n,[r,i])=>n+r*r+i*i,0);}
export function initialState(kind='correlated') {
 if(kind==='zero') return Array.from({length:8},(_,i)=>i===0?c(1):c(0));
 if(kind==='correlated') return GHZ_STATE.map(x=>c(x));
 throw new Error('unknown initial state');
}
export function validateState(state){
 if(!Array.isArray(state)||state.length!==8||state.some(a=>!Array.isArray(a)||a.length!==2||a.some(x=>typeof x!=='number'||!Number.isFinite(x)))) fail('expected eight finite complex amplitudes');
 if(Math.abs(norm(state)-1)>1e-9) fail('initial state is not normalized');
 return true;
}
export function mapAddress(address,step){
 const ordinal=ADDRESS_INDEX.get(address);
 if(ordinal===undefined || !Number.isSafeInteger(step)||step<0) fail('invalid coordinate or step');
 const op=OPCODES[ordinal%OPCODES.length];
 const target=(ordinal+Math.floor(ordinal/10))%3;
 const control=(target+1+(ordinal%2))%3; // always distinct from target
 return Object.freeze({step,address,ordinal,op,target,control:['CX','CZ','SWAP'].includes(op)?control:null});
}
export function compileTwin(packet){
 const addresses=recoverTwin(packet);
 const instructions=addresses.map((address,step)=>mapAddress(address,step));
 const parent={identitySeal:packet.identity.seal,sourceWitness:packet.witness,sourceView:packet.identity.sourceView,generation:packet.lineage.generation};
 const program={isa:ISA,source:parent,instructions};
 return {...program,digest:digest([program.isa,parent,instructions])};
}
export function verifyProgram(program,packet){
 const expected=compileTwin(packet);
 if(JSON.stringify(program)!==JSON.stringify(expected)) fail('program binding does not match twin identity and witness');
 return true;
}
function validateInstruction(ins){
 if(!ins||!OPCODES.includes(ins.op)||!isIndex(ins.target)||
    ((['CX','CZ','SWAP'].includes(ins.op)) && (!isIndex(ins.control)||ins.control===ins.target)) ||
    (!['CX','CZ','SWAP'].includes(ins.op) && ins.control!==null)) fail('malformed instruction');
}
export function applyGate(state,ins){
 validateState(state);validateInstruction(ins);
 const a=state.map(z=>z.slice());
 const mask=1<<(2-ins.target);
 if(mat[ins.op]){
  const M=mat[ins.op];
  for(let k=0;k<8;k++) if(!(k&mask)){
   const j=k|mask,lo=a[k],hi=a[j];
   a[k]=ADD(MUL(M[0][0],lo),MUL(M[0][1],hi));
   a[j]=ADD(MUL(M[1][0],lo),MUL(M[1][1],hi));
  }
 }else if(ins.op==='CX'){
  const cm=1<<(2-ins.control);
  for(let k=0;k<8;k++) if((k&cm)&&!(k&mask)){
   const j=k|mask;[a[k],a[j]]=[a[j],a[k]];
  }
 }else if(ins.op==='CZ'){
  const cm=1<<(2-ins.control);
  for(let k=0;k<8;k++) if((k&cm)&&(k&mask)) a[k]=c(-a[k][0],-a[k][1]);
 }else if(ins.op==='SWAP'){
  const cm=1<<(2-ins.control);
  for(let k=0;k<8;k++) if(!(k&cm)&&(k&mask)){
   const j=(k^cm)^mask;[a[k],a[j]]=[a[j],a[k]];
  }
 }
 if(Math.abs(norm(a)-1)>1e-9) fail('nonunitary gate result');
 return a;
}
export function inverseInstructions(instructions){
 if(!Array.isArray(instructions)) fail('bad instructions');
 return instructions.slice().reverse().map((ins,index)=>{
  validateInstruction(ins);
  return {...ins,step:index,op:inverse[ins.op]};
 });
}
export function executeInstructions(instructions,state){
 if(!Array.isArray(instructions)) fail('bad instructions');
 validateState(state);
 return instructions.reduce((s,ins)=>applyGate(s,ins),state.map(a=>a.slice()));
}
export function probabilityDistribution(state){
 validateState(state);
 return state.map(([re,im],i)=>({basis:i.toString(2).padStart(3,'0'),probability:re*re+im*im}));
}
export function reducedDensity(state,qubit){
 validateState(state);if(!isIndex(qubit)) fail('qubit must be 0..2');
 const out=[[[0,0],[0,0]],[[0,0],[0,0]]];
 const mask=1<<(2-qubit);
 for(let i=0;i<8;i++) if(!(i&mask)){
  const a=state[i], b=state[i|mask];
  const pair=[a,b];
  for(let u=0;u<2;u++) for(let v=0;v<2;v++) {
   const x=pair[u],y=pair[v];
   out[u][v]=ADD(out[u][v],MUL(x,c(y[0],-y[1])));
  }
 }
 return out;
}
export function purity(state,qubit){
 const r=reducedDensity(state,qubit);
 return r.reduce((sum,row)=>sum+row.reduce((s,z)=>s+z[0]*z[0]+z[1]*z[1],0),0);
}
export function executeTwin(packet,{initial='correlated'}={}){
 const program=compileTwin(packet);verifyProgram(program,packet);
 const start=initialState(initial);
 const final=executeInstructions(program.instructions,start);
 const recovered=executeInstructions(inverseInstructions(program.instructions),final);
 const maxError=Math.max(...start.flatMap((z,i)=>z.map((v,j)=>Math.abs(v-recovered[i][j]))));
 const distribution=probabilityDistribution(final);
 return {program,start,final,distribution,recovered,maxError,
    purities:[0,1,2].map(q=>purity(final,q)),
    outputDigest:digest([program.digest,initial,final.map(z=>z.map(n=>Number(n.toPrecision(14))))])};
}