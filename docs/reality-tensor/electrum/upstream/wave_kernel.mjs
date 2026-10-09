import * as T from './tensor_kernel.mjs';
const W=(()=>{
/* ROOT0 P3.0 — signed wavelength/amplitude interaction candidate.
 * Carrier {-e{ ..||..|....||| }+e} is immutable as a token pattern.
 * Dot -> phase advance 2π/λ; bar -> phase kick κ are new modelling choices.
 * -e / +e mark conjugate port phases, not validated physical charges.
 * Pair tensor addresses by transpose (o,i) <-> (i,o). The 10,000
 * diagonal locations, including Complex[0]=(0,0), do not mix.
 * First apply P2.9 reversible routing; then a 2x2 unitary mix on each
 * transpose pair. Inverse applies conjugate unitary then inverse routing.
 * Numerical floating-point reversibility is approximate, not bit exact.
 */
const {SILO_SIZE,TENSOR_SIZE,ZERO,encodeTensor,decodeTensor,next,previous,validatePair}=T;
const GLYPH='{-e{ ..||..|....||| }+e}';
const MOTIF='..||..|....|||';
const DOTS=8, BARS=6;
if(MOTIF.length!==14||[...MOTIF].filter(x=>x==='.').length!==DOTS||[...MOTIF].filter(x=>x==='|').length!==BARS)throw Error('Carrier motif broken');
const isFiniteNumber=x=>typeof x==='number'&&Number.isFinite(x);
const paramsCheck=p=>{
  if(!p||!isFiniteNumber(p.wavelength)||p.wavelength<=0||!isFiniteNumber(p.theta)||!isFiniteNumber(p.barKick)||!isFiniteNumber(p.pruneEpsilon)||p.pruneEpsilon<0)throw new RangeError('Need wavelength>0, finite coupling θ, bar kick κ, pruneEpsilon≥0');
  return p;
};
function parseCarrier(s){
  if(s!==GLYPH)throw new Error('Carrier must match literal {-e{ ..||..|....||| }+e}');
  return Object.freeze({signedPorts:['-e','+e'],motif:MOTIF,
    runs:[{token:'.',count:2},{token:'|',count:2},{token:'.',count:2},{token:'|',count:1},{token:'.',count:4},{token:'|',count:3}],
    dots:DOTS,bars:BARS,length:MOTIF.length});
}
const DEFAULT_PARAMS=Object.freeze({wavelength:8,theta:Math.PI/6,barKick:Math.PI/2,pruneEpsilon:1e-14});
function phaseAt(sample,wavelength,barKick=Math.PI/2){
  if(!Number.isSafeInteger(sample)||sample<0||!isFiniteNumber(wavelength)||wavelength<=0||!isFiniteNumber(barKick))throw new RangeError('Invalid phase sample or wavelength');
  const turns=Math.floor(sample/MOTIF.length),tail=sample%MOTIF.length;
  let dots=DOTS*turns,bars=BARS*turns;
  for(let k=0;k<tail;k++)if(MOTIF[k]==='.')dots++;else bars++;
  return (2*Math.PI/wavelength)*dots+barKick*bars;
}
function complex(re=0,im=0){
  if(!isFiniteNumber(re)||!isFiniteNumber(im))throw new RangeError('Nonfinite complex amplitude');
  return {re,im};
}
function abs2(z){return z.re*z.re+z.im*z.im;}
const plus=(a,b)=>({re:a.re+b.re,im:a.im+b.im});
const scale=(a,x)=>({re:a.re*x,im:a.im*x});
const times=(a,b)=>({re:a.re*b.re-a.im*b.im,im:a.re*b.im+a.im*b.re});
const ZERO_COMPLEX=Object.freeze({re:0,im:0});
function gate(a,b,theta,phi){
  if(!isFiniteNumber(theta)||!isFiniteNumber(phi))throw new RangeError('Nonfinite gate parameters');
  const c=Math.cos(theta),s=Math.sin(theta),f={re:Math.cos(phi),im:Math.sin(phi)};
  const iExp={re:-s*f.im,im:s*f.re}; // +i sin(theta) exp(+i phi)
  const iConj={re:s*f.im,im:s*f.re}; // +i sin(theta) exp(-i phi)
  return [plus(scale(a,c),times(iExp,b)),plus(times(iConj,a),scale(b,c))];
}
const transposeId=id=>{
  if(!Number.isSafeInteger(id)||id<0||id>=TENSOR_SIZE)throw new RangeError('Tensor id out of range');
  const o=Math.floor(id/SILO_SIZE),i=id%SILO_SIZE;
  return i*SILO_SIZE+o;
};
function normSquared(field){let sum=0;for(const z of field.values())sum+=abs2(z);return sum;}
function addSeed(field,pair,re,im=0){
  validatePair(pair);if(pair.outer===0&&pair.inner===0)throw new Error('Complex[0] cannot carry a changing wave amplitude');
  const id=encodeTensor(pair);field.set(id,complex(re,im));return id;
}
const collectPairs=field=>{
  const pairs=new Set();
  for(const id of field.keys()){
    const t=transposeId(id);
    if(t!==id)pairs.add(Math.min(id,t));
  }
  return [...pairs].sort((x,y)=>x-y);
};
function mix(field,tick,params=DEFAULT_PARAMS,inverse=false){
  if(field.has(0))throw new Error("Complex[0] anchor must not carry a wave amplitude");
  paramsCheck(params);
  if(!Number.isSafeInteger(tick)||tick<0)throw new RangeError('Invalid time tick');
  const out=new Map(field);
  for(const first of collectPairs(field)){
    const second=transposeId(first),o=Math.floor(first/SILO_SIZE),i=first%SILO_SIZE;
    const salt=o%10+i%10;
    const phi=phaseAt(tick+salt,params.wavelength,params.barKick);
    const [a,b]=gate(field.get(first)||ZERO_COMPLEX,field.get(second)||ZERO_COMPLEX,inverse?-params.theta:params.theta,phi);
    for(const [id,z] of [[first,a],[second,b]]){
      if(Math.hypot(z.re,z.im)<=params.pruneEpsilon)out.delete(id);
      else out.set(id,z);
    }
  }
  out.delete(0);return out;
}
function route(field,tick,inverse=false){
  if(field.has(0))throw new Error("Complex[0] anchor must not carry a wave amplitude");
  if(!Number.isSafeInteger(tick)||tick<0)throw new RangeError('Invalid time tick');
  const out=new Map();
  for(const [id,z] of field){
    const p=decodeTensor(id),m=inverse?previous(p,tick):next(p,tick);
    const nid=encodeTensor(m);
    if(out.has(nid))throw new Error('Collision in supposedly reversible P2.9 routing');
    out.set(nid,z);
  }
  out.delete(0);return out;
}
function waveStep(field,tick,params=DEFAULT_PARAMS){return mix(route(field,tick),tick,params);}
function waveUnstep(field,tick,params=DEFAULT_PARAMS){return route(mix(field,tick,params,true),tick,true);}
class WaveTensor {
  #field=new Map();#ledger=[];
  constructor(params=DEFAULT_PARAMS){this.params={...paramsCheck(params)};this.tick=0;}
  get amplitudes(){return new Map(this.#field);}
  get eventCount(){return this.#ledger.length;}
  get events(){return [...this.#ledger];}
  get energyProxy(){return normSquared(this.#field);}
  get occupied(){return this.#field.size;}
  seed(pair,amplitude,phase=0){
    if(this.tick!==0||this.eventCount!==0)throw new Error('Seed only at initial state; create a new branch to reseed');
    if(!isFiniteNumber(amplitude)||amplitude<0||!isFiniteNumber(phase))throw new RangeError('Invalid amplitude or phase');
    return addSeed(this.#field,pair,amplitude*Math.cos(phase),amplitude*Math.sin(phase));
  }
  forward(){
    const before=this.energyProxy;
    const after=waveStep(this.#field,this.tick,this.params);
    const n=normSquared(after);this.#field=after;
    const e=Object.freeze({seq:this.#ledger.length,kind:'forward',tick:this.tick,beforeNorm:before,afterNorm:n,active:after.size});
    this.#ledger.push(e);this.tick++;return e;
  }
  reverse(){
    if(this.tick===0)return null;
    const before=this.energyProxy,at=this.tick-1;
    const after=waveUnstep(this.#field,at,this.params);
    const e=Object.freeze({seq:this.#ledger.length,kind:'compensating-reverse',tick:at,beforeNorm:before,afterNorm:normSquared(after),active:after.size});
    this.#ledger.push(e);this.#field=after;this.tick--;return e;
  }
}

return {GLYPH,MOTIF,DOTS,parseCarrier,DEFAULT_PARAMS,phaseAt,complex,abs2,ZERO_COMPLEX,gate,transposeId,normSquared,addSeed,mix,route,waveStep,waveUnstep,WaveTensor};
})();
export const {GLYPH,MOTIF,DOTS,parseCarrier,DEFAULT_PARAMS,phaseAt,complex,abs2,ZERO_COMPLEX,gate,transposeId,normSquared,addSeed,mix,route,waveStep,waveUnstep,WaveTensor}=W;
