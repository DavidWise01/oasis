/**
 * ROOT0 P3.2: black signed -211 mV potential wrapper around orange phase field.
 * This is an appended candidate interaction; the P3.1 source is untouched.
 * Electrical potential alone cannot imply Planck-length access.
 */
import * as C from './cipher208.mjs';
import * as W from './wave_kernel.mjs';
import * as T from './tensor_kernel.mjs';

export const VOLTAGE_V=-0.211;
export const MILLIVOLTS=-211;
export const ELEMENTARY_CHARGE_C=1.602176634e-19;
export const HBAR_EVS=6.582119569e-16;
export const HC_EVM=1.2398419843320026e-6;
export const PLANCK_LENGTH_M=1.616255e-35;
export const CHARGE_PORTS=Object.freeze([-1,+1]); // multiples of +e: -e, +e.
export const DEFAULT_DT_S=1e-15;
export const DEFAULTS=Object.freeze({voltageV:VOLTAGE_V,dtS:DEFAULT_DT_S,depth:0,wavelength:8,theta:Math.PI/6,barKick:Math.PI/2});
export const basePhotonEquivalentM=HC_EVM/Math.abs(VOLTAGE_V);
export const fullZoomDecades=Math.log10(basePhotonEquivalentM/PLANCK_LENGTH_M);
const close=(x,y,t=1e-12)=>Math.abs(x-y)<=t;
const c=(re,im)=>W.complex(re,im);
function mul(a,b){return c(a.re*b.re-a.im*b.im,a.re*b.im+a.im*b.re);}
function validate(p){
 if(!p||!Number.isFinite(p.voltageV)||!Number.isFinite(p.dtS)||p.dtS<=0||
 !Number.isFinite(p.depth)||p.depth<0||p.depth>1||
 !Number.isFinite(p.wavelength)||p.wavelength<=0||
 !Number.isFinite(p.theta)||!Number.isFinite(p.barKick))throw RangeError('Invalid wrapper parameters');
 return p;
}
export function potentialEnergyEV(port,p=DEFAULTS){
 validate(p);if(port!==0&&port!==1)throw RangeError('port must be 0 (-e) or 1 (+e)');
 return CHARGE_PORTS[port]*p.voltageV; // eV; q/e = +-1.
}
export function signedPotentialPhase(port,p=DEFAULTS){return -potentialEnergyEV(port,p)*p.dtS/HBAR_EVS;}
/** Diagonal unitary e^(-i q V dt / hbar) on [-e,+e]. */
export function applyVoltage(field,p=DEFAULTS,adjoint=false){
 validate(p);if(!Array.isArray(field)||field.length!==2)throw TypeError('Two complex port amplitudes required');
 return field.map((a,i)=>{
   if(!Number.isFinite(a.re)||!Number.isFinite(a.im))throw RangeError('Nonfinite field');
   const phi=signedPotentialPhase(i,p)*(adjoint?-1:1);
   return mul(a,c(Math.cos(phi),Math.sin(phi)));
 });
}
export function zoomLengthM(depth,p=DEFAULTS){
 validate({...p,depth});
 if(depth===0)return basePhotonEquivalentM;
 if(depth===1)return PLANCK_LENGTH_M;
 return basePhotonEquivalentM*Math.exp(depth*Math.log(PLANCK_LENGTH_M/basePhotonEquivalentM));
}
export function photonEquivalentEnergyEV(depth,p=DEFAULTS){return HC_EVM/zoomLengthM(depth,p);}
export function noPhysicalPlanckDerivation(){return true;}
export function normalizedNorm(field){return field.reduce((acc,v)=>acc+W.abs2(v),0);}
export function forwardGate(field,tick,p=DEFAULTS){
 validate(p);return applyVoltage(C.forwardGate(field,tick,p),p,false);
}
/**
 * In mirrored coordinates, inverse of D*U is M*U†*D†*M.
 * Since M swaps ±e ports, M*D†*M = D. Hence D precedes the
 * existing conjugated P3.1 inverse. The phase is NOT merely negated twice.
 */
export function inverseMirroredGate(field,tick,p=DEFAULTS){
 validate(p);return C.inverseMirroredGate(applyVoltage(field,p,false),tick,p);
}
export class WrappedCipher208 {
  #ledger=[];
  constructor(options={}){
   this.params=Object.freeze(validate({...DEFAULTS,...(options.params||{})}));
   this.seed=options.amplitudes?options.amplitudes.map(a=>c(a.re,a.im)):[c(1,0),c(0,0)];
   if(this.seed.length!==2)throw TypeError('Require two initial port amplitudes');
   this.field=this.seed.map(a=>c(a.re,a.im));
   this.origin=options.pairId??T.encodeTensor({outer:2301,inner:9237});
   if(!Number.isSafeInteger(this.origin)||this.origin<=0||this.origin>=T.TENSOR_SIZE||this.origin===C.mirrorUpsideDown(this.origin))throw RangeError('Pair must be nonzero and non-self-mirrored');
   this.address=this.origin;this.tick=0;this.mode='forward';this.initialNorm=normalizedNorm(this.seed);
  }
  get journal(){return [...this.#ledger];}
  get eventCount(){return this.#ledger.length;}
  get norm(){return normalizedNorm(this.field);}
  forward(){
   if(this.mode!=='forward'||this.tick===C.FULL_LENGTH)return null;
   const t=this.tick;this.field=forwardGate(this.field,t,this.params);this.tick++;
   const e=Object.freeze({seq:this.eventCount,kind:'forward-with-voltage',tick:t,sign:C.FORWARD[t],voltageV:this.params.voltageV,norm:this.norm});this.#ledger.push(e);return e;
  }
  flip(){
   if(this.mode!=='forward'||this.tick!==208)throw Error('Complete 208 gates first');
   this.field=C.mirrorPorts(this.field);this.address=C.mirrorUpsideDown(this.address);this.mode='backward';
   this.#ledger.push(Object.freeze({seq:this.eventCount,kind:'mirror-upside-down',tick:this.tick,norm:this.norm}));
  }
  backward(){
   if(this.mode!=='backward'||this.tick===0)return null;
   const t=--this.tick;this.field=inverseMirroredGate(this.field,t,this.params);
   const e=Object.freeze({seq:this.eventCount,kind:'inverse-with-voltage',tick:t,sign:C.BACKWARD[207-t],norm:this.norm});this.#ledger.push(e);return e;
  }
  recovered(tol=3e-11){return this.mode==='backward'&&this.tick===0&&this.address===C.mirrorUpsideDown(this.origin)&&
   C.distance(this.field[0],this.seed[1])<tol&&C.distance(this.field[1],this.seed[0])<tol;}
  reset(){this.field=this.seed.map(a=>c(a.re,a.im));this.address=this.origin;this.tick=0;this.mode='forward';
   this.#ledger.push(Object.freeze({seq:this.eventCount,kind:'reset-new-branch',tick:0,norm:this.norm}));}
}
