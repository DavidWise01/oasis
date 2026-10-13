// OASIS {{i & dd}} v0.8 — finite coherent statevector atop FROZEN v0.7 floor.
// Simulation on CPU, not physical entanglement or quantum acceleration.
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {tokenize,walk,CODE,PASSES} from './frozen/dual5-floor-v0.7/dual5.mjs';
import freeze from './frozen/dual5-floor-v0.7/FLOOR-MANIFEST-v0.7.json' with {type:'json'};
export const VERSION='i-dd-quantum/v0.8';
export const MAX_LOCAL_DIM=16; // reference simulator resource bound; universal {{i}} language remains unbounded.
export const BOUND_CODE='UUDDLRLRBASS';
export function assertFloor(){
 if(CODE!==BOUND_CODE||PASSES!==5)throw new Error('Frozen floor instruction mismatch');
 for(const entry of freeze.files.filter(x=>x.name==='dual5.mjs')){
  const path=new URL('./frozen/dual5-floor-v0.7/'+entry.name,import.meta.url);
  const actual=createHash('sha256').update(readFileSync(path)).digest('hex');
  if(actual!==entry.sha256)throw new Error('FROZEN FLOOR SHA256 mismatch');
 }
 return {version:freeze.version,source:freeze.files.find(x=>x.name==='dual5.mjs').sha256};
}
function fail(s){throw new Error('quantum-dual: '+s);}
function dim(n){if(!Number.isInteger(n)||n<2||n>MAX_LOCAL_DIM)fail('local n must be 2..'+MAX_LOCAL_DIM);return n;}
function idx(a,b,n){return 2*(a*n+b);}
function clone(s){return new Float64Array(s);}
export function norm(s){let t=0;for(let i=0;i<s.length;i+=2)t+=s[i]**2+s[i+1]**2;return t;}
export function zeroState(n){dim(n);const z=new Float64Array(2*n*n);z[0]=1;return z;}
function stateCheck(s,n){dim(n);if(!(s instanceof Float64Array)||s.length!==2*n*n||!s.every(Number.isFinite)||Math.abs(norm(s)-1)>1e-9)fail('bad normalized complex state');}
export function qftLeft(state,n,inverse=false){
 stateCheck(state,n);
 const dst=new Float64Array(state.length),scale=1/Math.sqrt(n),sign=inverse?-1:1;
 for(let a=0;a<n;a++)for(let b=0;b<n;b++){
  let re=0,im=0;
  for(let k=0;k<n;k++){
   const theta=sign*2*Math.PI*a*k/n,ca=Math.cos(theta),sa=Math.sin(theta),p=idx(k,b,n);
   re+=state[p]*ca-state[p+1]*sa;
   im+=state[p]*sa+state[p+1]*ca;
  }
  const q=idx(a,b,n);dst[q]=re*scale;dst[q+1]=im*scale;
 }
 return dst;
}
export function controlledAdd(state,n,inverse=false){
 stateCheck(state,n);const dst=new Float64Array(state.length);
 for(let a=0;a<n;a++)for(let b=0;b<n;b++){
  const from=idx(a,b,n),to=idx(a,((b+(inverse?-a:a))%n+n)%n,n);
  dst[to]=state[from];dst[to+1]=state[from+1];
 }
 return dst;
}
function permutation(v,n){
 if(!Array.isArray(v)||v.length!==n||new Set(v).size!==n||v.some(i=>!Number.isInteger(i)||i<0||i>=n))fail('invalid local permutation');
}
export function railMaps(tokens){
 assertFloor();const n=dim(tokens.length); const records=tokenize(tokens);
 const positive=walk(records,false).items.map(t=>t.slot);
 const negative=walk(records.slice().reverse(),true).items.map(t=>t.slot);
 const pos=Array.from({length:n},(_,j)=>positive.indexOf(j));
 const neg=Array.from({length:n},(_,j)=>negative.indexOf(j));
 permutation(pos,n);permutation(neg,n);
 return {n,positive:pos,negative:neg,positiveOrder:positive,negativeOrder:negative};
}
export function localPermute(state,n,positive,negative,inverse=false){
 stateCheck(state,n);permutation(positive,n);permutation(negative,n);
 const dst=new Float64Array(state.length);
 for(let a=0;a<n;a++)for(let b=0;b<n;b++){
  const to=inverse?idx(a,b,n):idx(positive[a],negative[b],n);
  const from=inverse?idx(positive[a],negative[b],n):idx(a,b,n);
  dst[to]=state[from];dst[to+1]=state[from+1];
 }
 return dst;
}
export function joint(state,n){
 stateCheck(state,n);const values=[];
 for(let a=0;a<n;a++)for(let b=0;b<n;b++){
  const p=idx(a,b,n);values.push({positive:a,negative:b,probability:state[p]**2+state[p+1]**2});
 }
 return values;
}
export function reducedLeft(state,n){
 stateCheck(state,n);
 const rho=new Float64Array(2*n*n);
 for(let a=0;a<n;a++)for(let b=0;b<n;b++){
  let re=0,im=0;
  for(let j=0;j<n;j++){
   const x=idx(a,j,n),y=idx(b,j,n),xr=state[x],xi=state[x+1],yr=state[y],yi=state[y+1];
   re+=xr*yr+xi*yi;
   im+=xi*yr-xr*yi;
  }
  const k=idx(a,b,n);rho[k]=re;rho[k+1]=im;
 }
 return rho;
}
export function purity(state,n){const rho=reducedLeft(state,n);let x=0;for(let i=0;i<rho.length;i+=2)x+=rho[i]**2+rho[i+1]**2;return x;}
export function entanglementEntropyDiagonal(state,n){
 const rho=reducedLeft(state,n);let entropy=0;
 for(let a=0;a<n;a++)for(let b=0;b<n;b++){
  const k=idx(a,b,n);
  if(a!==b && Math.hypot(rho[k],rho[k+1])>1e-9)fail('entropy helper requires diagonal reduced density');
 }
 for(let j=0;j<n;j++){const p=rho[idx(j,j,n)];if(p>0)entropy-=p*Math.log2(p);}
 return entropy;
}
export function buildCoherent(tokens){
 const maps=railMaps(tokens),{n}=maps;
 const start=zeroState(n);
 const fourier=qftLeft(start,n);
 const entangled=controlledAdd(fourier,n);
 const output=localPermute(entangled,n,maps.positive,maps.negative);
 const undoLocal=localPermute(output,n,maps.positive,maps.negative,true);
 const undoAdd=controlledAdd(undoLocal,n,true);
 const restored=qftLeft(undoAdd,n,true);
 const maxInverseError=Math.max(...restored.map((x,i)=>Math.abs(x-start[i])));
 const product=localPermute(start,n,maps.positive,maps.negative);
 return {version:VERSION,maps,start,fourier,entangled,output,restored,product,
  maxInverseError,entropyBits:entanglementEntropyDiagonal(output,n),purity:purity(output,n),
  productPurity:purity(product,n),distribution:joint(output,n)};
}
