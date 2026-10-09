/** ROOT0 P3.1 — 208-address cyclic cipher using 16 overlapping, 14-glyph windows.
 * USER facts: literal glyph '..||..|....|||', 1/16 of 208, forward 208 then
 * reverse inverted mirrored upside-down. MODEL POLICY (new): neighboring
 * 14-glyph windows share exactly one seam, alternating glyph polarity, so each
 * contributes 13 *new* symbols. Reflect z by additive inversion modulo 10,
 * and mirror the silo ports. These choices are explicit, not user-frozen.
 * Not a claim about real photons, quantum amplitudes, or the physical universe.
 */
import {gate,complex,abs2} from './wave_kernel.mjs';
import {encode4,decode4,encodeTensor,decodeTensor,SILO_SIZE,TENSOR_SIZE,ZERO} from './tensor_kernel.mjs';
export const MOTIF='..||..|....|||';
export const FRAME_COUNT=16;
export const WINDOW_LENGTH=14;
export const ADVANCE=13;
export const FULL_LENGTH=208;
export const PORTS=Object.freeze(['-e','+e']);
export const DEFAULTS=Object.freeze({wavelength:8,theta:Math.PI/6,barKick:Math.PI/2});
export const inverseGlyph=g=>g==='.'?'|':g==='|'?'.':(()=>{throw Error('Unknown glyph')})();
export const invertSymbols=s=>Array.from(s,inverseGlyph).join('');
export const reverseInvert=s=>invertSymbols([...s].reverse().join(''));
export const windows=Object.freeze(Array.from({length:FRAME_COUNT},(_,p)=>p%2?invertSymbols(MOTIF):MOTIF));
// Each phase contributes its first 13 symbols; its 14th is a shared seam.
export const FORWARD=windows.map(w=>w.slice(0,ADVANCE)).join('');
export const BACKWARD=reverseInvert(FORWARD);
if(MOTIF.length!==14||FORWARD.length!==FULL_LENGTH||BACKWARD.length!==FULL_LENGTH)throw Error('Cipher length mismatch');
export function validateSeams(){
  const checked=[];
  for(let p=0;p<FRAME_COUNT;p++){
    const start=p*ADVANCE;
    const expanded=Array.from({length:WINDOW_LENGTH},(_,j)=>FORWARD[(start+j)%FULL_LENGTH]).join('');
    if(expanded!==windows[p])throw Error('Open seam at frame '+p);
    checked.push(Object.freeze({frame:p,start,overlapAt:(start+ADVANCE)%FULL_LENGTH,shared:windows[p][13],next:windows[(p+1)%FRAME_COUNT][0]}));
  }
  return checked;
}
export const SEAMS=Object.freeze(validateSeams());
if(reverseInvert(BACKWARD)!==FORWARD)throw Error('Mirror-inverse glyph not involutive');
const finite=x=>Number.isFinite(x);
export function checkParameters(p){
  if(!p||!finite(p.wavelength)||p.wavelength<=0||!finite(p.theta)||!finite(p.barKick))throw RangeError('Need wavelength>0 and finite theta/barKick');
  return p;
}
// Phase at each tick uses 208 unique glyphs and no double-counted seam.
export function phaseAt208(tick,p=DEFAULTS){
  checkParameters(p);
  if(!Number.isSafeInteger(tick)||tick<0)throw RangeError('Invalid cipher tick');
  const cycles=Math.floor(tick/FULL_LENGTH),remaining=tick%FULL_LENGTH;
  let dots=cycles*COUNT.dot,bars=cycles*COUNT.bar;
  for(let k=0;k<remaining;k++)FORWARD[k]==='.'?dots++:bars++;
  return 2*Math.PI*dots/p.wavelength + p.barKick*bars;
}
export const COUNT=Object.freeze({dot:[...FORWARD].filter(v=>v==='.').length,bar:[...FORWARD].filter(v=>v==='|').length});
export function reflectZ(id){
  const address=decode4(id);
  address[2]=(10-address[2])%10; // upside-down axis is relative to pinned 0, mod 10.
  return encode4(address);
}
export function mirrorUpsideDown(id){
  const p=decodeTensor(id);
  return encodeTensor({outer:reflectZ(p.inner),inner:reflectZ(p.outer)});
}
export function mirrorPorts(field){
  if(!Array.isArray(field)||field.length!==2)throw TypeError('Two amplitude ports required');
  return [field[1],field[0]];
}
const clone=z=>complex(z.re,z.im);
export const distance=(a,b)=>Math.hypot(a.re-b.re,a.im-b.im);
export const norm=ab=>abs2(ab[0])+abs2(ab[1]);
export function forwardGate(amplitudes,tick,params=DEFAULTS){
  if(!Number.isSafeInteger(tick)||tick<0||tick>=FULL_LENGTH)throw RangeError('Forward tick 0..207');
  return gate(amplitudes[0],amplitudes[1],params.theta,phaseAt208(tick,params));
}
export function inverseMirroredGate(mirrored,tick,params=DEFAULTS){
  if(!Number.isSafeInteger(tick)||tick<0||tick>=FULL_LENGTH)throw RangeError('Backward tick 0..207');
  // M U† M^-1 = U(-theta,-phi) for two ports swapped under the mirror M.
  return gate(mirrored[0],mirrored[1],-params.theta,-phaseAt208(tick,params));
}
export class Cipher208 {
  #journal=[];
  constructor(options={}){
    this.params={...checkParameters({...DEFAULTS,...(options.params||{})})};
    this.seed=options.amplitudes?options.amplitudes.map(clone):[complex(1,0),complex(0,0)];
    if(this.seed.length!==2)throw TypeError('Need exactly two complex amplitudes');
    this.amplitudes=this.seed.map(clone);
    this.origin=options.pairId??encodeTensor({outer:2301,inner:9237});
    if(this.origin<=0||this.origin>=TENSOR_SIZE||this.origin===mirrorUpsideDown(this.origin))throw RangeError('Select nonzero, distinct mirrored pair');
    this.address=this.origin;
    this.tick=0;
    this.mode='forward';
    this.initialNorm=norm(this.seed);
  }
  get journal(){return [...this.#journal];}
  get totalEvents(){return this.#journal.length;}
  get energyProxy(){return norm(this.amplitudes);}
  get currentGlyph(){return this.mode==='forward'?FORWARD[this.tick]??'DONE':BACKWARD[FULL_LENGTH-this.tick]??'DONE';}
  forward(){
    if(this.mode!=='forward'||this.tick===FULL_LENGTH)return null;
    const prior=this.tick;
    this.amplitudes=forwardGate(this.amplitudes,prior,this.params);
    this.tick++;
    const event=Object.freeze({seq:this.#journal.length,mode:'forward',sourceTick:prior,symbol:FORWARD[prior],energyProxy:this.energyProxy});
    this.#journal.push(event);return event;
  }
  beginMirroredReverse(){
    if(this.mode!=='forward'||this.tick!==FULL_LENGTH)throw Error('Finish 208 forward steps before mirrored reversal');
    this.amplitudes=mirrorPorts(this.amplitudes);
    this.address=mirrorUpsideDown(this.address);
    this.mode='backward';
    this.#journal.push(Object.freeze({seq:this.#journal.length,mode:'mirror-and-flip-z',sourceTick:208,energyProxy:this.energyProxy}));
  }
  backward(){
    if(this.mode!=='backward'||this.tick===0)return null;
    const prior=this.tick-1;
    this.amplitudes=inverseMirroredGate(this.amplitudes,prior,this.params);
    this.tick--;
    const event=Object.freeze({seq:this.#journal.length,mode:'inverse-mirrored-upside-down',sourceTick:prior,
      symbol:BACKWARD[FULL_LENGTH-1-prior],energyProxy:this.energyProxy});
    this.#journal.push(event);return event;
  }
  // Recovery is a read-only comparison; the mirror-frame end is M(seed).
  recovered(tolerance=2e-11){
    return this.mode==='backward'&&this.tick===0&&
      distance(this.amplitudes[0],this.seed[1])<tolerance&&
      distance(this.amplitudes[1],this.seed[0])<tolerance&&
      this.address===mirrorUpsideDown(this.origin);
  }
  restart(){
    this.amplitudes=this.seed.map(clone);this.tick=0;this.mode='forward';this.address=this.origin;
    this.#journal.push(Object.freeze({seq:this.#journal.length,mode:'new-branch-restart',sourceTick:0,energyProxy:this.energyProxy}));
  }
}
