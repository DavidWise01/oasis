/**
 * ROOT0 P3.5 — wavelength-dependent Au/Ag electrum countermodels.
 * The Au and Ag datasets are Johnson & Christy (1972), pure-element experimental n,k,
 * transcribed from refractiveindex.info-database CC0, 44 shared wavelengths.
 * Source repository: polyanskiy/refractiveindex.info-database
 * Au: database/data/main/Au/nk/Johnson.yml; git blob cf2f1b2c490d60bea818096920e323da94bbb540
 * Ag: database/data/main/Ag/nk/Johnson.yml; git blob fcace717cd05616f344cf732784253260d5c3769
 * They are NOT measured electrum/alloy optical constants. Alloy mixing is explicitly an assumption.
 */
import * as FCC from '../electrum/electrum_fcc.mjs';
import * as Cipher from '../cipher208/cipher208.mjs';

const wavelengthsUm=[.1879,.1916,.1953,.1993,.2033,.2073,.2119,.2164,.2214,.2262,.2313,.2371,.2426,.2490,.2551,.2616,.2689,.2761,.2844,.2924,.3009,.3107,.3204,.3315,.3425,.3542,.3679,.3815,.3974,.4133,.4305,.4509,.4714,.4959,.5209,.5486,.5821,.6168,.6595,.7045,.7560,.8211,.8920,.9840];
const auN=[1.28,1.32,1.34,1.33,1.33,1.30,1.30,1.30,1.30,1.31,1.30,1.32,1.32,1.33,1.33,1.35,1.38,1.43,1.47,1.49,1.53,1.53,1.54,1.48,1.48,1.50,1.48,1.46,1.47,1.46,1.45,1.38,1.31,1.04,.62,.43,.29,.21,.14,.13,.14,.16,.17,.22];
const auK=[1.188,1.203,1.226,1.251,1.277,1.304,1.350,1.387,1.427,1.460,1.497,1.536,1.577,1.631,1.688,1.749,1.803,1.847,1.869,1.878,1.889,1.893,1.898,1.883,1.871,1.866,1.895,1.933,1.952,1.958,1.948,1.914,1.849,1.833,2.081,2.455,2.863,3.272,3.697,4.103,4.542,5.083,5.663,6.350];
const agN=[1.07,1.10,1.12,1.14,1.15,1.18,1.20,1.22,1.25,1.26,1.28,1.28,1.30,1.31,1.33,1.35,1.38,1.41,1.41,1.39,1.34,1.13,.81,.17,.14,.10,.07,.05,.05,.05,.04,.04,.05,.05,.05,.06,.05,.06,.05,.04,.03,.04,.04,.04];
const agK=[1.212,1.232,1.255,1.277,1.296,1.312,1.325,1.336,1.342,1.344,1.357,1.367,1.378,1.389,1.393,1.387,1.372,1.331,1.264,1.161,.964,.616,.392,.829,1.142,1.419,1.657,1.864,2.070,2.275,2.462,2.657,2.869,3.093,3.324,3.586,3.858,4.152,4.483,4.838,5.242,5.727,6.312,6.992];
if([auN,auK,agN,agK].some(a=>a.length!==wavelengthsUm.length))throw Error('Broken optical table');
export const RAW=Object.freeze(wavelengthsUm.map((u,i)=>Object.freeze({nm:u*1000,Au:Object.freeze({n:auN[i],k:auK[i]}),Ag:Object.freeze({n:agN[i],k:agK[i]})})));
export const SOURCES=Object.freeze({paper:'P. B. Johnson and R. W. Christy, Physical Review B 6, 4370 (1972)',AuBlob:'cf2f1b2c490d60bea818096920e323da94bbb540',AgBlob:'fcace717cd05616f344cf732784253260d5c3769',pureMetalOnly:true});
export const LIMITS=Object.freeze({minNm:400,maxNm:900});
const finite=(v,n)=>{if(typeof v!=='number'||!Number.isFinite(v))throw new RangeError(n+' finite required');return v;};
export function measuredElement(name,nm){
 if(!['Au','Ag'].includes(name))throw new RangeError('Au/Ag required');finite(nm,'wavelength');
 if(nm<RAW[0].nm||nm>RAW.at(-1).nm)throw new RangeError('Outside measured data; no extrapolation');
 let hi=RAW.findIndex(x=>x.nm>=nm);if(hi===0)return {...RAW[0][name]};
 if(hi<0)hi=RAW.length-1;
 let p=RAW[hi-1],q=RAW[hi],t=(nm-p.nm)/(q.nm-p.nm);
 return {n:p[name].n+t*(q[name].n-p[name].n),k:p[name].k+t*(q[name].k-p[name].k)};
}
export function epsilon(n,k){return {re:n*n-k*k,im:2*n*k};}
export function opticalIndexFromEpsilon(z){
 const mod=Math.hypot(z.re,z.im);return {n:Math.sqrt(Math.max(0,(mod+z.re)/2)),k:Math.sqrt(Math.max(0,(mod-z.re)/2))};
}
export function compositionAu(p={}){const d=FCC.atomicFractions({auWeight:p.auWeight??79,agWeight:p.agWeight??21,compositionBasis:p.compositionBasis??'mass'});return d.fAu;}
export function alloyIndex(nm,p={}){
 const x=compositionAu(p),a=measuredElement('Au',nm),b=measuredElement('Ag',nm);
 const method=p.method??'epsilon';if(!['epsilon','nk'].includes(method))throw new RangeError('method');
 if(method==='nk')return {n:x*a.n+(1-x)*b.n,k:x*a.k+(1-x)*b.k,xAu:x,method};
 const ea=epsilon(a.n,a.k),eb=epsilon(b.n,b.k);
 const e={re:x*ea.re+(1-x)*eb.re,im:x*ea.im+(1-x)*eb.im};
 return {...opticalIndexFromEpsilon(e),xAu:x,method};
}
export function opticalFilm(nm,p={}){
 finite(nm,'nm');const d=finite(p.thicknessNm??30,'thicknessNm');if(d<0)throw new RangeError('thickness');
 const i=alloyIndex(nm,p);return {...i,...FCC.slabOptics({wavelengthM:nm*1e-9,thicknessM:d*1e-9,nReal:i.n,kappa:i.k}),nm};
}
export function cipherSpectrum(){
 const s=Cipher.FORWARD.split('').map(c=>c==='.'?1:-1),N=s.length;
 const spectrum=Array.from({length:N/2+1},(_,m)=>{
  let re=0,im=0;for(let j=0;j<N;j++){let t=2*Math.PI*m*j/N;re+=s[j]*Math.cos(t);im-=s[j]*Math.sin(t);}
  return {mode:m,magnitude:Math.hypot(re,im)/N};
 });
 const candidates=spectrum.filter(x=>x.mode>0);
 const dominant=[...candidates].sort((a,b)=>b.magnitude-a.magnitude||a.mode-b.mode)[0];
 return {spectrum,dominant,DC:spectrum[0].magnitude};
}
export const CIPHER_SPECTRUM=cipherSpectrum();
export function cipherPhase(nm,p={}){
 const gamma=finite(p.cipherRadPerVolt??0,'cipher coefficient'),voltage=finite(p.voltageV??-.211,'voltage')-finite(p.referenceV??0,'reference');
 const pitch=finite(p.pitchNm??500,'optical pitch');if(pitch<=0||nm<=0)throw new RangeError('lengths >0');
 // Model-only, not a derived physical coupling. Wavelength conversion requires new pitch parameter.
 return gamma*voltage*CIPHER_SPECTRUM.dominant.magnitude*Math.cos(2*Math.PI*CIPHER_SPECTRUM.dominant.mode*pitch/nm);
}
export function spectrumAt(nm,p={}){
 const film=opticalFilm(nm,p),dv=finite(p.voltageV??-.211,'voltage')-finite(p.referenceV??0,'reference');
 const surface=finite(p.surfaceRadPerVolt??0,'surface coefficient')*dv;
 const extra=cipherPhase(nm,p);
 const phase=surface+extra;
 const carrierPhi=Math.atan2(film.transmission.im,film.transmission.re);
 const visibility=finite(p.visibility??.85,'visibility');if(visibility<0||visibility>1)throw new RangeError('visibility');
 const refPhi=finite(p.referencePhaseRad??Math.PI/2,'reference phase');
 const signal=.5*(1+visibility*Math.cos(carrierPhi+phase-refPhi));
 const nullSignal=.5*(1+visibility*Math.cos(carrierPhi-refPhi));
 return {...film,baselineInterferometer:nullSignal,interferometer:signal,relativeInterferometer:signal-nullSignal,
  extraPhaseRad:extra,surfacePhaseRad:surface,phaseRad:phase,frequencyShiftHz:0,physicallyDerived:false};
}
export function calculatedSpectrum(p={},from=400,to=900,step=5){
 if(!Number.isInteger(step)||step<1||from<RAW[0].nm||to>RAW.at(-1).nm||from>to)throw new RangeError('range');
 return Array.from({length:Math.floor((to-from)/step)+1},(_,j)=>spectrumAt(from+j*step,p));
}
