/* OASIS | Natural Bound 12 | 2026-10-27
 * Schwarzschild geodesic deviation, local orthonormal freely falling frame.
 * Initial Jacobi displacements: 1 meter each radial and transverse
 * at r_start=100 r_s, with zero INITIAL RELATIVE VELOCITY (dξ/dτ=0).
 * These are freely falling neighboring probes, NOT a material body.
 * E=1 reference observer (rest at infinity), Schwarzschild nonrotating model.
 * Fundamental local equations:
 * ξr''=+c² rs/r³ ξr,  ξperp''=-c² rs/(2r³) ξperp.
 * Analytic solutions with w=T(r)/T(start)=(r/r_start)^(3/2):
 * f_r=4/5 w^(-1/3)+1/5 w^(4/3);
 * f_t=2 w^(1/3)-w^(2/3), in BOTH transverse directions.
 * Mathematical regime limited by the FIRST of:
 * (i) local Jacobi small-separation gate, max ξ <= .01 min(r,ell_curv)
 * where ell_curv=c/sqrt(|λ_r|)=sqrt(r³/rs);
 * (ii) declared K lp^4=1 stop from Bound 11.
 * A 1% bound is a chosen modeling criterion, NOT a universal failure threshold.
 */
(function(root){"use strict";
const C=299792458,GM_SUN=1.3271244e20,M=4.297e6,LP=1.616255e-35,
      RS=2*GM_SUN*M/C**2,START=100*RS,CURV_STOP=Math.pow(12*RS*RS*LP**4,1/6),
      T0=(2*RS/(3*C))*1000,TH=2*RS/(3*C),THRESHOLD=.01,N=729;
const CONSTANTS=Object.freeze({C,GM_SUN,M,LP,RS,START,CURV_STOP,T0,TH,THRESHOLD,N});
function requireFinitePositive(x,name){if(!(x>0)||!Number.isFinite(x))throw Error(name+" must be positive finite");}
function factors(r){
 requireFinitePositive(r,"r");
 if(r>START*(1+1e-12))return null;
 // Direct powers in r/start avoid subtracting the near-singularity elapsed time.
 const x=r/START;
 const w=x**1.5;
 const radial=.8*x**(-.5)+.2*x**2;
 const transverse=2*Math.sqrt(x)-x;
 return {w,radial,transverse,product:radial*transverse*transverse};
}
function curvatureLength(r){requireFinitePositive(r,"r");return Math.sqrt(r*r*r/RS);}
function tidal(r){
 requireFinitePositive(r,"r");
 const radial=C*C*RS/(r*r*r);
 return {radial,transverse:-radial/2,trace:radial-radial/2-radial/2};
}
function relativeAcceleration(r,separationM){
 const f=tidal(r);return {radial_m_s2:f.radial*separationM,
 transverse_m_s2:f.transverse*separationM};
}
function jacobi(r,initialM=1,smallFraction=THRESHOLD){
 requireFinitePositive(initialM,"initial separation");
 requireFinitePositive(smallFraction,"smallFraction");
 if(smallFraction>=1)throw Error("Fraction must be strictly below one");
 if(r===0)return {r,radial_m:null,transverse_m:null,status:"CENTER_UNRESOLVED"};
 if(!(r>0))throw Error("r positive or zero sentinel");
 if(r>START)return {r,radial_m:null,transverse_m:null,status:"BEFORE_START"};
 if(r<CURV_STOP)return {r,radial_m:null,transverse_m:null,status:"AFTER_HIGH_CURVATURE_STOP"};
 const f=factors(r), radialM=initialM*f.radial, transverseM=initialM*f.transverse,
       lcurv=curvatureLength(r),bound=smallFraction*Math.min(r,lcurv),
       maxSep=Math.max(Math.abs(radialM),Math.abs(transverseM));
 const ratio=maxSep/Math.min(r,lcurv),valid=maxSep<=bound*(1+1e-12);
 const T=TH*(r/RS)**1.5;
 return {r,radial_m:radialM,transverse_m:transverseM,
         radial_factor:f.radial,transverse_factor:f.transverse,
         volume_factor:f.product,
         radial_relative_accel_m_s2:tidal(r).radial*radialM,
         transverse_relative_accel_m_s2:tidal(r).transverse*transverseM,
         curvature_length_m:lcurv,
         gate_separation_m:bound,
         max_separation_over_local_scale:ratio,
         proper_time_to_formal_center_s:T,
         elapsed_proper_time_from_start_s:T0-T,
         status:!valid?"JACOBI_LINEARIZATION_INVALID":
           r===CURV_STOP?"NAMED_CLASSICAL_CURVATURE_STOP":
           r<RS?"FORMAL_SCHWARZSCHILD_INTERIOR_LINEAR_JACOBI":
           "EXTERIOR_LINEAR_JACOBI",
         usable_linearization:valid,
         after_curvature_stop:false};
}
function firstBreak(initialM=1,smallFraction=THRESHOLD){
 requireFinitePositive(initialM,"initialM");
 requireFinitePositive(smallFraction,"smallFraction");
 if(smallFraction>=1)throw Error("Fraction too large");
 const start=jacobi(START,initialM,smallFraction);
 if(!start.usable_linearization)
   return {r:START,already_invalid_at_start:true,source:"INITIAL_SPACING_TOO_LARGE"};
 const atStop=jacobi(CURV_STOP,initialM,smallFraction);
 if(atStop.usable_linearization)return {r:CURV_STOP,atCurvatureStop:true,source:"CLASSICAL_CURVATURE_GATE"};
 // Bisection on log radius; progressively smaller r is more deformed.
 let low=Math.log(CURV_STOP),high=Math.log(START);
 for(let i=0;i<240;i++){
   const mid=(low+high)/2,r=Math.exp(mid),v=jacobi(r,initialM,smallFraction);
   if(v.usable_linearization)high=mid;
   else low=mid;
 }
 const r=Math.exp(high),s=jacobi(r,initialM,smallFraction);
 return {r,atCurvatureStop:false,source:"ONE_PERCENT_JACOBI_LOCAL_CURVATURE_GATE",
         snapshot:s,remaining_formal_time_s:TH*(r/RS)**1.5,
         proper_after_horizon_s:TH*(1-(r/RS)**1.5)};
}
function sample(r,initialM=1,smallFraction=THRESHOLD){
 const point=jacobi(r,initialM,smallFraction),gate=firstBreak(initialM,smallFraction);
 if(point.radial_m===null)return point;
 return {...point,active_before_gate:r>=gate.r*(1-1e-12),
   reporting_status:point.usable_linearization?"SUPPORTED_LINEARIZED_MODEL":
     "INVALID_LINEARIZATION_VALUES_FOR_DIAGNOSTIC_ONLY"};
}
function selfTest(){
 const close=(a,b,t=1e-10)=>Math.abs(a-b)<=t*Math.max(1,Math.abs(a),Math.abs(b));
 const horizon=jacobi(RS),begin=jacobi(START),gate=firstBreak(1),tinyGate=firstBreak(.001);
 if(!close(begin.radial_factor,1)||!close(begin.transverse_factor,1))throw Error("initial separation");
 if(!close(horizon.radial_factor,8.00002)||!close(horizon.transverse_factor,.19))throw Error("horizon analytic");
 if(!close(horizon.volume_factor,8.00002*.19*.19))throw Error("volume result");
 if(!close(tidal(RS).trace,0,1e-16))throw Error("vacuum tidal trace");
 if(!close(tidal(RS).radial,-2*tidal(RS).transverse))throw Error("tide eigenvalues");
 if(!close(gate.r,3186234.8409372214,1e-8))throw Error("1m validity gate");
 if(!close(tinyGate.r,100757.59257545913,1e-8))throw Error("1mm validity gate");
 if(!close(gate.snapshot.max_separation_over_local_scale,.01,1e-8))throw Error("relative criterion");
 if(jacobi(CURV_STOP/2).radial_m!==null)throw Error("curvature gate wrongly crossed");
 if(jacobi(0).radial_m!==null)throw Error("center resolved");
 if(gate.r<=CURV_STOP||gate.r>=RS)throw Error("gate outside interior");
 if(!close(gate.snapshot.radial_m,504.8750214409288,1e-9))throw Error("gate radial separation");
 // Jacobi ODE via numerical finite differences in proper time.
 // T(r)=T0*(r/START)^1.5, remaining-to-zero time u.
 const checkRadius=[START/10,RS,RS*.1];
 for(const r of checkRadius){
   const u=TH*(r/RS)**1.5,h=1e-4*u;
   function f(u,side){
     const x=Math.pow(u/T0,2/3);
     return side==="radial"? .8*x**(-.5)+.2*x*x : 2*Math.sqrt(x)-x;
   }
   for(const side of ["radial","transverse"]){
     const second=(f(u+h,side)-2*f(u,side)+f(u-h,side))/(h*h);
     const exact=(side==="radial"?4/9:-2/9)/(u*u)*f(u,side);
     if(Math.abs((second-exact)/exact)>3e-7)throw Error("ODE residual "+side+" r="+r);
   }
 }
 let previous=jacobi(START).radial_factor;
 for(let j=1;j<=1000;j++){
   const rr=START*Math.exp(-j*Math.log(START/RS)/1000);
   const x=jacobi(rr);
   if(x.radial_factor<previous-1e-9)throw Error("radial contraction");
   if(x.transverse_factor>1+1e-10||x.transverse_factor<0)throw Error("transverse behavior");
   previous=x.radial_factor;
 }
 return {pass:true,initial_separation_m:1,
  initialization:"independent nearby freely falling probes with zero initial relative velocity",
  horizon_radial_m:horizon.radial_m,horizon_transverse_m:horizon.transverse_m,
  horizon_volume_ratio:horizon.volume_factor,
  maximum_validity_radius_1m_m:gate.r,
  remaining_formal_time_at_1m_gate_s:gate.remaining_formal_time_s,
  validity_gate_1m_relative_radial_m:gate.snapshot.radial_m,
  maximum_validity_radius_1mm_m:tinyGate.r,
  tidal_trace:"zero in vacuum instantaneous orthonormal frame",
  ode_finite_difference_tests:"PASS 3 radii × 2 directions",
  model_limitation:"Jacobi 1% criterion chosen, not biological/material breaking point",
  center_and_subcutoff_null:true};
}
const api=Object.freeze({...CONSTANTS,factors,curvatureLength,tidal,
 relativeAcceleration,jacobi,firstBreak,sample,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.Bound12Jacobi=api;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
