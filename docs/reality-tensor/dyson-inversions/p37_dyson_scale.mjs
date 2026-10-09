/**
 * ROOT0 P3.7 correction of P3.2–P3.6 voltage assumption.
 * USER: negative-energy inversions are Dyson-sphere shells;
 *       {{-211mv}} x 10^-35 is one scaled wrapper, not -211mV unscaled.
 * No claim of physical negative-energy matter, real Dyson spheres at Planck
 * length, or a voltage-to-length law.  The multiport shell maps are an added
 * norm-conserving scattering hypothesis, not electrodynamics.
 */
export const LITERAL = '{{-211mv}}x10^-35';
export const SHELL_LAYERS = Object.freeze(['-e', 'gray', '+e', 'white']);
export const CONSTANTS = Object.freeze({
  baseMillivolts: -211,
  scaleExponent: -35,
  scale: 1e-35,
  scaledVoltageV: (-211 / 1000) * 1e-35,
  hbarEVs: 6.582119569e-16,
  planckM: 1.616255e-35,
  defaultDtS: 1e-15,
  startRadiusM: 300e-9,
});
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const validCount=n=>Number.isInteger(n)&&n>=1&&n<=10;
export function check(p={}){
 const a={shells:10,capture:0.15,depth:1,dtS:CONSTANTS.defaultDtS,chargeSign:-1,
   wavelengthNm:600,startRadiusM:CONSTANTS.startRadiusM,...p};
 if(!validCount(a.shells)||!finite(a.capture)||a.capture<0||a.capture>1||
   !finite(a.depth)||a.depth<0||a.depth>1||!finite(a.dtS)||a.dtS<0||
   ![-1,1].includes(a.chargeSign)||!finite(a.wavelengthNm)||a.wavelengthNm<=0||
   !finite(a.startRadiusM)||a.startRadiusM<=CONSTANTS.planckM)
   throw new RangeError('Invalid shell, capture, depth, charge, wavelength or timestep');
 return a;
}
export function scaledPotentialV(){return CONSTANTS.scaledVoltageV;}
export function totalPortPhase(p={}){
 const a=check(p);
 // qV/ħ with numerical charge sign in elementary-charge units.
 return -(a.chargeSign*CONSTANTS.scaledVoltageV*a.dtS)/CONSTANTS.hbarEVs;
}
export function depthRadiusM(p={}){
 const a=check(p);
 return Math.exp((1-a.depth)*Math.log(a.startRadiusM)+a.depth*Math.log(CONSTANTS.planckM));
}
export function shellRadiusM(index,p={}){
 const a=check(p);
 if(!Number.isInteger(index)||index<0||index>=a.shells)throw new RangeError('shell index');
 const depth=a.depth*(index+1)/a.shells;
 return Math.exp((1-depth)*Math.log(a.startRadiusM)+depth*Math.log(CONSTANTS.planckM));
}
export const zero=()=>[0,0];
export const amplitude=(re,im=0)=>{
 if(!finite(re)||!finite(im))throw new RangeError('complex amplitude');
 return [re,im];
};
const clone=s=>s.map(v=>v.slice());
const mul=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]];
const expi=x=>[Math.cos(x),Math.sin(x)];
export const norm=s=>s.reduce((v,z)=>v+z[0]*z[0]+z[1]*z[1],0);
export function inputState(p={}){
 const a=check(p);
 return [amplitude(1),...Array.from({length:a.shells},zero)];
}
function validateState(state,n){
 if(!Array.isArray(state)||state.length!==n+1||!state.every(z=>Array.isArray(z)&&z.length===2&&z.every(finite)))
   throw new TypeError('Expected one traveling plus n capture complex channels');
}
function beam(a,b,capture,inverse=false){
 const t=Math.sqrt(1-capture),r=Math.sqrt(capture)*(inverse?-1:1);
 // U = [[t, i r], [i r, t]] and inverse U†.
 return [
  [t*a[0]-r*b[1],t*a[1]+r*b[0]],
  [t*b[0]-r*a[1],t*b[1]+r*a[0]]
 ];
}
export function forwardAt(state,index,p={}){
 const cfg=check(p);validateState(state,cfg.shells);
 if(!Number.isInteger(index)||index<0||index>=cfg.shells)throw new RangeError('shell index');
 const out=clone(state);
 // Charge potential is applied ONCE per full wrapper, distributed for numerical construction.
 const phased=mul(out[0],expi(totalPortPhase(cfg)/cfg.shells));
 const [travel,captured]=beam(phased,out[index+1],cfg.capture);
 out[0]=travel;out[index+1]=captured;
 return out;
}
export function backwardAt(state,index,p={}){
 const cfg=check(p);validateState(state,cfg.shells);
 if(!Number.isInteger(index)||index<0||index>=cfg.shells)throw new RangeError('shell index');
 const out=clone(state);
 const [travel,captured]=beam(out[0],out[index+1],cfg.capture,true);
 out[0]=mul(travel,expi(-totalPortPhase(cfg)/cfg.shells));out[index+1]=captured;
 return out;
}
export function forwardAll(state,p={}){const cfg=check(p);let cur=clone(state);for(let i=0;i<cfg.shells;i++)cur=forwardAt(cur,i,cfg);return cur;}
export function backwardAll(state,p={}){const cfg=check(p);let cur=clone(state);for(let i=cfg.shells-1;i>=0;i--)cur=backwardAt(cur,i,cfg);return cur;}
export function analyticPowers(p={}){
 const cfg=check(p),t=1-cfg.capture;
 return {traveling:t**cfg.shells,captured:Array.from({length:cfg.shells},(_,i)=>cfg.capture*t**i),
   sum:t**cfg.shells+cfg.capture*Array.from({length:cfg.shells},(_,i)=>t**i).reduce((x,y)=>x+y,0)};
}
export function physicsBoundary(){return Object.freeze({
  scaledVoltageIsMeasured:false,relativeScaleFactorIsDimensionless:true,
  physicalPlanckTransitDerived:false,physicalDysonShellsAsserted:false,
  inverseIsInformationPreservingMathematicalMap:true,
  PlanckRadiusIsIndependentDisplayCoordinate:true
});}
