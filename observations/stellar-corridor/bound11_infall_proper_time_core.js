/* OASIS Bound 11: E=1 radial timelike geodesic, nonspinning Schwarzschild.
   Model source values carry forward from Bound 10 (CODATA lP, Sgr A* mass).
   From REST AT INFINITY implies nonzero inward radial speed at start 100 rs.
   Geodesic invariant: proper time τ of an infalling test particle.
   The prior common inertial boost and factorial rank are independent of τ.
   Curvature criterion K lP^4 >= 1 is a DECLARED FORMAL STOP, not a verified
   microscopic surface. No physical data/model is generated beyond this stop.
*/
(function(root) {
"use strict";
const C = 299792458;
const GM_SUN = 1.3271244e20;
const MASS_SUN = 4.297e6;
const LP = 1.616255e-35;
const PLANCK_TIME = LP / C;
const RS = 2 * GM_SUN * MASS_SUN / (C*C);
const START = 100*RS;
const STOP = Math.pow(12*RS*RS*LP**4,1/6);
const RATE = 2*RS/(3*C);
const HORIZON_FROM_START = RATE*(100**1.5-1);
const FORMAL_HORIZON_TO_ZERO = RATE;
const STOP_REMAINING_FORMAL = 2*Math.pow(12,0.25)/3 * PLANCK_TIME;
const N = 729;
const CONST = Object.freeze({C,GM_SUN,MASS_SUN,LP,PLANCK_TIME,RS,START,STOP,
 RATE,HORIZON_FROM_START,FORMAL_HORIZON_TO_ZERO,STOP_REMAINING_FORMAL,N});
function assertRadius(r) {
 if(!Number.isFinite(r)||r<=0)throw Error("Positive finite areal radius required");
}
function tauRemainingFormal(r) {
 assertRadius(r);
 // Proper time from r to formal r=0 in the classical E=1 Schwarzschild model.
 // It is only a physics-supported continuation for radii above the STOP.
 return RATE*Math.pow(r/RS,1.5);
}
function properFromStart(r) {
 assertRadius(r);
 if(Math.abs(r/START-1)<1e-12)return 0;
 if(r>START*(1+1e-12))return null; // not traversed from selected start
 if(r<STOP*(1-1e-12))return null;  // no extrapolated physical record past stop
 // DOUBLE precision cancellation for r<<rs: this near-constant number is
 // useful for display only; the separate remaining-time clock is robust.
 return RATE*1000 - tauRemainingFormal(r);
}
function properToStop(r) {
 assertRadius(r);
 if(r<STOP||r>START)return null;
 // Stable around high curvature: tau(r)-tau(STOP) before loss in
 // big start-minus-small subtraction.
 const q=Math.pow(r/STOP,1.5);
 return STOP_REMAINING_FORMAL*(q-1);
}
function properAfterHorizon(r) {
 assertRadius(r);
 if(r>RS||r<STOP)return null;
 // stable far from horizon: remaining to zero at horizon minus remaining at r
 return FORMAL_HORIZON_TO_ZERO - tauRemainingFormal(r);
}
function coordinateRadialDerivative(r) {
 assertRadius(r);
 if(r<STOP||r>START)return null;
 return -C*Math.sqrt(RS/r); // dr/dτ, not locally measured velocity
}
function tidalRates(r) {
 assertRadius(r);
 if(r<STOP||r>START)return null;
 const radial=C*C*RS/(r*r*r);
 return {radial_stretch_per_s2:radial,
         transverse_compression_per_s2:-radial/2};
}
function curvature(r) {
 assertRadius(r);
 if(r<STOP||r>START)return null;
 const log10Klp4=Math.log10(12)+2*Math.log10(RS/LP)
                 -6*Math.log10(r/LP);
 return {log10_K_times_lp4:log10Klp4,
         K_times_lp4:10**log10Klp4};
}
function regime(r) {
 if(r===0)return "CENTER_SENTINEL_NOT_ON_WORLDLINE";
 if(r<STOP)return "UNRESOLVED_BEYOND_FORMAL_CURVATURE_STOP";
 if(r>START)return "OUTSIDE_CHOSEN_WORLDLINE_START";
 if(r<RS)return "CLASSICAL_INTERIOR_FORMAL_INEFFECTIVE_QUANTUM_DESCRIPTION";
 if(Math.abs(r/RS-1)<1e-12)return "SCHWARZSCHILD_HORIZON_CROSSED_IN_FINITE_PROPER_TIME";
 return "SCHWARZSCHILD_EXTERIOR_E1_RADIAL_FREEFALL";
}
function point(r,tag="") {
 if(r===0)return {tag,radius_m:0,regime:regime(r),proper_elapsed_s:null,
     proper_to_cutoff_s:null,radial_tidal_s2:null,log10_Klp4:null};
 assertRadius(r);
 const good=r>=STOP&&r<=START;
 const curv=good?curvature(r):null,tidal=good?tidalRates(r):null;
 return {tag,radius_m:r,r_over_rs:r/RS,
  regime:regime(r),
  proper_elapsed_s:good?properFromStart(r):null,
  proper_to_cutoff_s:good?properToStop(r):null,
  proper_since_horizon_s:good?properAfterHorizon(r):null,
  remaining_formal_to_zero_s:good?tauRemainingFormal(r):null,
  radial_tidal_s2:tidal?.radial_stretch_per_s2??null,
  transverse_tidal_s2:tidal?.transverse_compression_per_s2??null,
  dr_dproper_m_s:good?coordinateRadialDerivative(r):null,
  log10_Klp4:curv?.log10_K_times_lp4??null,
  verified_observation:false,
  stop_is_model_threshold:true};
}
function markers() {
 return [
  point(START,"START_100RS_E1_NOT_REST_HERE"),
  point(3*RS,"SCHWARZSCHILD_ISCO"),
  point(1.5*RS,"PHOTON_SPHERE"),
  point(RS,"HORIZON"),
  point(STOP,"FORMAL_KLP4_EQUAL_ONE_STOP"),
  point(LP,"PLANCK_LENGTH_BEYOND_STOP_NOT_TRAJECTORY"),
  point(0,"CENTER_SENTINEL_NOT_WORLDLINE")
 ];
}
function radiusAtFraction(fraction,phase) {
 if(!Number.isFinite(fraction)||fraction<0||fraction>1)throw Error("fraction 0..1 required");
 if(phase==="exterior"){
  if(fraction===0)return START;
  if(fraction===1)return RS;
  // tau from start to horizon follows x=r/rs cubed-over-two.
  const power=1000-fraction*999;
  return RS*Math.pow(power,2/3);
 }
 if(phase==="interior"){
  if(fraction===0)return RS;
  // horizon r=RS to named curvature cutoff; at phase=1 do not
  // round its tiny nonzero radius to classical r=0.
  if(fraction===1)return STOP;
  const tiny=Math.pow(STOP/RS,1.5);
  const power=(1-fraction)+fraction*tiny;
  return RS*Math.pow(power,2/3);
 }
 throw Error("phase must be exterior or interior");
}
function radiusAtRemainingToCutoffPlanckTimes(planckTimes){
 if(!Number.isFinite(planckTimes)||planckTimes<0)throw Error("Nonnegative finite Planck-time count required");
 const formalRemainingInTp=planckTimes+STOP_REMAINING_FORMAL/PLANCK_TIME;
 const r=STOP*Math.pow(formalRemainingInTp/(STOP_REMAINING_FORMAL/PLANCK_TIME),2/3);
 if(r>START)return null;
 return r;
}
function selfTest(){
 const close=(a,b,tol=1e-11)=>Math.abs(a-b)<=tol*Math.max(1,Math.abs(a),Math.abs(b));
 if(!close(START/RS,100))throw Error("start mass scale wrong");
 if(!close(tauRemainingFormal(RS),2*RS/(3*C)))throw Error("horizon remaining time wrong");
 if(!close(properFromStart(START),0))throw Error("start zero time wrong");
 if(!close(properFromStart(RS),HORIZON_FROM_START))throw Error("horizon elapsed time wrong");
 if(!close(properToStop(STOP),0))throw Error("cutoff stop time wrong");
 if(!close(STOP_REMAINING_FORMAL/PLANCK_TIME,2*Math.pow(12,.25)/3))throw Error("universal coefficient wrong");
 if(Math.abs(curvature(STOP).log10_K_times_lp4)>1e-12)throw Error("K*lp^4 stop not 1");
 if(!close(tidalRates(RS).radial_stretch_per_s2,C*C/RS**2))throw Error("tidal rate wrong");
 if(!close(radiusAtFraction(0,"exterior"),START)||!close(radiusAtFraction(1,"exterior"),RS))throw Error("exterior endpoints wrong");
 if(!close(radiusAtFraction(0,"interior"),RS)||!close(radiusAtFraction(1,"interior"),STOP))throw Error("interior endpoints wrong");
 if(properFromStart(STOP/10)!==null||properFromStart(START*10)!==null)throw Error("invalid extrapolation");
 if(point(LP).proper_elapsed_s!==null||point(0).proper_elapsed_s!==null)throw Error("unresolved region assigned worldline");
 if(!close(radiusAtRemainingToCutoffPlanckTimes(0),STOP))throw Error("Planck clock endpoint wrong");
 for(let i=0;i<=1000;i++){
  const f=i/1000;
  for(const phase of ["exterior","interior"]){
    const r=radiusAtFraction(f,phase);
    if(!Number.isFinite(r)||r<STOP*(1-1e-11)||r>START*(1+1e-11))throw Error("trajectory out of bounds");
    const info=point(r);
    if(info.proper_elapsed_s===null)throw Error("missing clock");
  }
 }
 const marks=markers();
 if(marks.length!==7||marks[4].proper_to_cutoff_s!==0||marks[5].proper_elapsed_s!==null)throw Error("boundary status");
 return {pass:true,initial_condition:"E=1 radial geodesic rest AT INFINITY, passing 100rs with nonzero inward speed",
  horizon_elapsed_s:HORIZON_FROM_START,
  horizon_to_classical_center_formal_s:FORMAL_HORIZON_TO_ZERO,
  curvature_cutoff_radius_m:STOP,
  cutoff_to_formal_center_planck_times:STOP_REMAINING_FORMAL/PLANCK_TIME,
  start_to_horizon_hours:HORIZON_FROM_START/3600,
  start_radius_m:START,
  planck_reference_and_zero_not_on_valid_worldline:true,
  derivative_and_inverse_phases_tested:2002,
  common_bulk_boost_changes_proper_time:false,
  factorial_rank_is_time:false};
}
const API=Object.freeze({...CONST,tauRemainingFormal,properFromStart,properToStop,
 properAfterHorizon,coordinateRadialDerivative,tidalRates,curvature,regime,point,
 markers,radiusAtFraction,radiusAtRemainingToCutoffPlanckTimes,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=API;
root.Bound11Infall=API;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
