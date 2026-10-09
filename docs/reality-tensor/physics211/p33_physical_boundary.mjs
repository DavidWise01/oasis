/**
 * ROOT0 P3.3 physical discrimination gate (SI units).
 * Model A: gauge-equivalent uniform scalar potential -> zero observable vacuum shift.
 * Model B: idealized 1D Pockels material with nonzero E from electrode difference.
 * All r, n, gap, length, overlap, etc. are EXTRA inputs. Not derived from cipher.
 */
export const CONSTANTS=Object.freeze({
  voltageV:-0.211,
  wavelengthVacuumM:600e-9,
  n:2.2,
  electroOpticCoeffMPerV:30e-12,
  gapM:10e-6,
  interactionLengthM:0.01,
  overlap:1,
  visibility:0.8,
  biasRad:Math.PI/2,
  planckLengthM:1.616255e-35,
  hbarEVs:6.582119569e-16,
  hcEVm:1.2398419843320026e-6
});
function finite(v,k){if(typeof v!=='number'||!Number.isFinite(v))throw new RangeError(`${k} must be finite`);return v;}
export function validate(p={}){
  const z={...CONSTANTS,...p};
  for(const [k,v] of Object.entries(z))finite(v,k);
  if(!(z.gapM>0 && z.interactionLengthM>=0 && z.wavelengthVacuumM>0 && z.n>0 &&
    z.overlap>=0 && z.overlap<=1 && z.visibility>=0 && z.visibility<=1 && z.planckLengthM>0))
    throw new RangeError('Invalid optical geometry / visibility / scale');
  return z;
}
/** Uniform constant potential: E=B=0, vacuum optical wavelength unchanged.
 * The absolute scalar potential is not an observable. */
export function uniformPotentialVacuum(p={}){
 const z=validate(p);
 return Object.freeze({electricFieldVPerM:0,deltaIndex:0,deltaPhaseRad:0,
   outputWavelengthVacuumM:z.wavelengthVacuumM,frequencyShiftHz:0,
   opticalPhaseShiftFromAbsolutePotentialRad:0,model:'gauge-equivalent vacuum null'});
}
/** Idealized linearly coupled single polarization/material configuration.
 * Electric field E=V/gap; d n = -(1/2)n^3 r overlap E;
 * d phi = 2pi * L * dn / lambda_vacuum. */
export function electroOptic(p={}){
 const z=validate(p);
 const E=z.voltageV/z.gapM;
 const dn=-0.5*z.n**3*z.electroOpticCoeffMPerV*z.overlap*E;
 const dphase=2*Math.PI*z.interactionLengthM*dn/z.wavelengthVacuumM;
 const nEff=z.n+dn;
 if(!(nEff>0))throw new RangeError('Unphysical linear extrapolation: n_eff<=0');
 const mediumWavelengthBeforeM=z.wavelengthVacuumM/z.n;
 const mediumWavelengthAfterM=z.wavelengthVacuumM/nEff;
 const normalizedIntensity=0.5*(1+z.visibility*Math.cos(z.biasRad+dphase));
 const nullIntensity=0.5*(1+z.visibility*Math.cos(z.biasRad));
 return Object.freeze({electricFieldVPerM:E,deltaIndex:dn,deltaPhaseRad:dphase,
   vacuumWavelengthShiftM:0,frequencyShiftHz:0,
   mediumWavelengthBeforeM,mediumWavelengthAfterM,
   mediumWavelengthShiftM:mediumWavelengthAfterM-mediumWavelengthBeforeM,
   normalizedIntensity,nullIntensity,normalizedIntensityContrast:normalizedIntensity-nullIntensity,
   model:'conditional Pockels material; fixed optical frequency'});
}
/** Gauge transformation: φ'=φ-∂tχ; A'=A+∂xχ, χ=u*x*t+v*t+w*x.
 * Potentials represented by affine derivative coefficients. */
export function gaugeTransform(base,chi){
 for(const [k,v] of Object.entries({...base,...chi}))finite(v,k);
 const out={phi0:base.phi0||0,phiX:base.phiX-chi.u,phiT:base.phiT||0,
  a0:base.a0||0,aT:base.aT+chi.u,aX:base.aX||0,
  gaugeU:chi.u,gaugeV:chi.v||0,gaugeW:chi.w||0};
 out.phi0-=chi.v||0;
 out.a0+=chi.w||0;
 return out;
}
export function electricField(base){return -base.phiX-base.aT;}
/** Gauge-invariant gap voltage: ∫ E dx (with fixed x and negligible fringe). */
export function gaugeInvariantVoltage(base,gapM){
 finite(gapM,'gapM'); if(gapM<=0)throw new RangeError('gap positive');
 return electricField(base)*gapM;
}
/** Reference φ for hypothetical CHARGED +/-e port only, not neutral photon.
 * This scalar phase is gauge dependent if no closed coherent reference included. */
export function referenceChargedPhase(p={},dtS=1e-15){const z=validate(p);finite(dtS,'dtS');if(dtS<=0)throw new RangeError('dt positive');return -z.voltageV*dtS/z.hbarEVs;}
/** A log view coordinate, not a physical voltage -> distance law. */
export function zoomLength(depth,p={}){
 const z=validate(p);finite(depth,'depth');if(depth<0||depth>1)throw new RangeError('depth in [0,1]');
 return z.wavelengthVacuumM*Math.exp(depth*Math.log(z.planckLengthM/z.wavelengthVacuumM));
}
export function prerequisitesMet(p={}){
 const z=validate(p);return Boolean(z.gapM>0 && z.n>0 && z.electroOpticCoeffMPerV!==0 && z.interactionLengthM>0 && z.overlap>0);
}
