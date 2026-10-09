/** ROOT0 P3.6 -E[gray{+e{white}}] Planck bubble hypothesis gate.
 * User literal prefix: "{-e{gray{+e{white}}" (unclosed).
 * This candidate closes the two trailing braces for a visual tree only.
 * Physical facts: 211mV alone cannot produce photons at the Planck wavelength.
 * The Bethe-type thin, perfectly conducting aperture law is an extrapolation
 * that DOES NOT claim validity near quantum-gravity scales. 
 */
export const GLYPH = '{-e{gray{+e{white}}';
export const COMPLETED_FOR_DISPLAY = GLYPH + '}}';
export const REGIONS = Object.freeze(['-e','gray','+e','white']);
export const CONSTANTS=Object.freeze({
  planckM:1.616255e-35,
  h_Js:6.62607015e-34,
  c_ms:299792458,
  e_C:1.602176634e-19,
  hbar_eVs:6.582119569e-16,
  shellVoltageV:-0.211,
  referenceNm:600,
  referenceFilmTransmission:0.13805358429274417,
  bethePrefactor:64/(27*Math.PI*Math.PI),
});
export function guard(p={}) {
 const v={wavelengthNm:600,depth:0,voltageV:-0.211,dtS:1e-15,
   filmTransmission:CONSTANTS.referenceFilmTransmission,entranceRadiusM:300e-9,...p};
 for(const key of Object.keys(v)) if(!Number.isFinite(v[key]))throw new RangeError(`nonfinite ${key}`);
 if(v.wavelengthNm<=0||v.depth<0||v.depth>1||v.dtS<0||v.filmTransmission<0||v.filmTransmission>1||v.entranceRadiusM<=CONSTANTS.planckM)throw new RangeError('invalid domain');
 return v;
}
export function radiusM(p={}){
 const v=guard(p);
 return Math.exp(Math.log(v.entranceRadiusM)*(1-v.depth)+Math.log(CONSTANTS.planckM)*v.depth);
}
export function logRadiusM(p={}){return Math.log10(radiusM(p));}
export function photonEnergyEV(wavelengthNm){
 if(!Number.isFinite(wavelengthNm)||wavelengthNm<=0)throw new RangeError('lambda>0');
 return CONSTANTS.h_Js*CONSTANTS.c_ms/(wavelengthNm*1e-9*CONSTANTS.e_C);
}
export function chargedPhaseRad(chargeSign,voltageV=-.211,dtS=1e-15){
 if(![-1,1].includes(chargeSign)||!Number.isFinite(voltageV)||!Number.isFinite(dtS)||dtS<0)throw new RangeError('invalid charged port');
 return -(chargeSign*voltageV*dtS)/CONSTANTS.hbar_eVs;
}
export function apertureLog10T(p={}){
 const v=guard(p),lambda=v.wavelengthNm*1e-9,r=radiusM(v),kr=2*Math.PI*r/lambda;
 // Bethe-Bouwkamp C (k*r)^4 in ideal zero-thickness perfect conductor.
 // Defined *only for kr <= 0.1*. All large apertures are outside the bound.
 if(kr>0.1)return null;
 return Math.log10(CONSTANTS.bethePrefactor)+4*Math.log10(kr);
}
export function apertureStatus(p={}){
 const v=guard(p),r=radiusM(v),lambda=v.wavelengthNm*1e-9;
 const log10=apertureLog10T(v);
 return {radiusM:r,radiusToWavelength:r/lambda,log10T:log10,
  knownContinuumValidity:r>=1e-9 ? 'MODEL_RANGE_WITH_APPROXIMATIONS':'EXTRAPOLATION_BELOW_NANOMETER',
  nearPlanck: r<1e-30,domainOK:log10!==null};
}
export function theoreticalTransmission(p={}){
 const v=guard(p),status=apertureStatus(v);
 if(status.log10T===null)return {...status,Taperture:null,Twhite:null};
 const tap=10**status.log10T;
 return {...status,Taperture:tap,Twhite:v.filmTransmission*tap,
  log10Twhite:status.log10T+(v.filmTransmission>0?Math.log10(v.filmTransmission):-Infinity)};
}
// Complex values represented as pairs [real,imag]. 3 ports: white photon,
// outer electrum loss channel, gray aperture loss channel. This is a
// hypothetical unitary dilation, not observed microscopic optical physics.
export function cmul(a,b){return[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]];}
export function normSquared(state){return state.reduce((s,a)=>s+a[0]**2+a[1]**2,0);}
export function beamMix(state,i,j,transmission,inverse=false){
 if(!Array.isArray(state)||state.length!==3||!(transmission>=0&&transmission<=1))throw new RangeError('invalid state/gate');
 const a=state.map(z=>z.slice());let t=Math.sqrt(transmission),r=Math.sqrt(1-transmission)*(inverse?-1:1);
 // U=[t,i r;i r,t], U^dagger=[t,-i r;-i r,t]
 const ia=[-r*a[j][1],r*a[j][0]], ib=[-r*a[i][1],r*a[i][0]];
 a[i]=[t*a[i][0]+ia[0],t*a[i][1]+ia[1]];
 a[j]=[t*a[j][0]+ib[0],t*a[j][1]+ib[1]];
 return a;
}
export function propagate(state,p={}){
 const v=guard(p),t=theoreticalTransmission(v);
 if(t.Taperture===null)throw new RangeError('ideal aperture approximation only when k*r <=0.1');
 return beamMix(beamMix(state,0,1,v.filmTransmission),0,2,t.Taperture);
}
export function unpropagate(state,p={}){
 const v=guard(p),t=theoreticalTransmission(v);
 if(t.Taperture===null)throw new RangeError('ideal aperture approximation only when k*r <=0.1');
 return beamMix(beamMix(state,0,2,t.Taperture,true),0,1,v.filmTransmission,true);
}
export function planckAudit(p={}){
 const v=guard(p),lPlanck=CONSTANTS.planckM;
 const energy211=0.211,lambda211nm=CONSTANTS.h_Js*CONSTANTS.c_ms/(energy211*CONSTANTS.e_C)*1e9;
 const energyAtPlanck=CONSTANTS.h_Js*CONSTANTS.c_ms/(lPlanck*CONSTANTS.e_C);
 const predicted=theoreticalTransmission(v);
 return {
  ...predicted,lambda211nm,energyAtPlanckEV:energyAtPlanck,
  energy211ev:energy211,energyRatio:energyAtPlanck/energy211,
  opticalEnergyEV:photonEnergyEV(v.wavelengthNm),
  voltsToPhotonAtPlanckDerived:false,
  regime:predicted.nearPlanck?'INVALID_PHYSICAL_EXTRAPOLATION':'CONDITIONAL_IDEAL_APERTURE',
  physicalQuantumGravityProven:false
 };
}
