/* OASIS Natural Bound 16 | 2026-10-27
   LATE ADVANCED-TIME TAIL + CAUCHY-HORIZON BLUESHIFT DIAGNOSTIC.
   THIS IS NOT A SOLUTION OF THE PERTURBED EINSTEIN EQUATIONS.
   Based on stationary Kerr kappa_- magnitude, Poisson-Israel blueshift
   and an explicitly ASSUMED power-law incoming tail.
   S(v) = epsilon (v/v0)^(-p) exp(|kappa_-| (v-v0)/c).
   Let t_g=rg/c, x=(v-v0)/(c t_g) [dimensionless] and
   x0=v0/(c t_g)>0. Then log10 S = log10epsilon +
       [beta*x - p*ln(1+x/x0)] / ln(10),
   beta=rg*|kappa_-|=sqrt(1-chi^2)/(2*(1-sqrt(1-chi^2))).
   v is advanced-null-coordinate length; Δv/c=x*t_g is a
   NORMALIZED LATE-TIME EXTERNAL CLOCK. It is NOT proper time from Bound15.
   S is an arbitrary dimensionless sensitivity indicator, NOT physical
   stress-energy, mass, Kretschmann, curvature, or a backreacted metric.
   Chi=0 has NO separate inner Cauchy horizon: diagnostic deliberately
   returns null, never division by zero.
*/
(function(root){"use strict";
const C=299792458,GM_SUN=1.3271244e20,M=4.297e6,RG=GM_SUN*M/C**2,TG=RG/C,LN10=Math.LN10;
const SPINS=Object.freeze([0,.5,.9,.99]),DEFAULTS=Object.freeze({epsilon:1e-9,p:7,x0:100,xMax:1000,thresholdLog10:0});
const assertPos=(x,n)=>{if(!(Number.isFinite(x)&&x>0))throw Error(n+" must be positive finite");return x};
function kerr(chi){
 if(!Number.isFinite(chi)||chi<0||chi>=1)throw Error("spin must satisfy 0<=chi<1");
 const q=Math.sqrt(1-chi*chi),outer=1+q,inner=1-q;
 if(chi===0)return {chi,hasInnerCauchyHorizon:false,outerY:2,innerY:0,
   beta:null,innerSurfaceGravityAbsPerM:null,innerSurfaceGravityRatePerS:null,
   eFoldTimeS:null,reason:"Schwarzschild has no distinct inner horizon."};
 const beta=q/(2*inner),rate=beta/TG;
 return {chi,outerY:outer,innerY:inner,hasInnerCauchyHorizon:true,beta,
  innerSurfaceGravityAbsPerM:beta/RG,innerSurfaceGravityRatePerS:rate,
  eFoldTimeS:1/rate,
  horizon_gap_RG:2*q,
  note:"Absolute INNER-horizon surface gravity of EXACT stationary Kerr with generator normalized at infinity. Perturbed spacetime not solved."};
}
function options(input={}){
 const a={...DEFAULTS,...input};
 assertPos(a.epsilon,"epsilon");assertPos(a.p,"p");assertPos(a.x0,"x0");
 assertPos(a.xMax,"xMax");
 if(!Number.isFinite(a.thresholdLog10))throw Error("Finite log10 threshold required");
 return a;
}
function log10Tail(chi,x,settings={}){
 const k=kerr(chi),o=options(settings);
 if(!Number.isFinite(x)||x<0)throw Error("late advanced-time shift x>=0");
 if(!k.hasInnerCauchyHorizon)return null;
 return Math.log10(o.epsilon)+(k.beta*x-o.p*Math.log1p(x/o.x0))/LN10;
}
function derivativeLn(chi,x,settings={}){
 const k=kerr(chi),o=options(settings);
 if(!(x>=0&&Number.isFinite(x)))throw Error("x>=0 required");
 return k.hasInnerCauchyHorizon?k.beta-o.p/(o.x0+x):null;
}
function turningPoint(chi,settings={}){
 const k=kerr(chi),o=options(settings);
 if(!k.hasInnerCauchyHorizon)return null;
 return Math.max(0,o.p/k.beta-o.x0);
}
function threshold(chi,settings={}){
 const k=kerr(chi),o=options(settings);
 if(!k.hasInnerCauchyHorizon)return {status:"NO_INNER_HORIZON",x:null,timeS:null};
 const at0=log10Tail(chi,0,o)-o.thresholdLog10;
 if(at0>=0)return {status:"ALREADY_AT_OR_ABOVE_THRESHOLD",x:0,timeS:0};
 const xmin=turningPoint(chi,o);
 // From xmin onward logS grows monotonically. Find first upward crossing.
 let hi=Math.max(1,xmin+1),maxX=1e7;
 while(log10Tail(chi,hi,o)<o.thresholdLog10&&hi<maxX)hi=Math.min(maxX,hi*2);
 if(log10Tail(chi,hi,o)<o.thresholdLog10)
  return {status:"NOT_REACHED_WITHIN_SEARCH_HORIZON",x:null,timeS:null,maxX};
 let lo=xmin;
 for(let i=0;i<80;i++){const mid=(hi+lo)/2;
  if(log10Tail(chi,mid,o)>=o.thresholdLog10)hi=mid;else lo=mid}
 return {status:"CROSSED_ASSUMED_TOY_THRESHOLD",x:hi,timeS:hi*TG,
   diagnostic_only:true,not_a_mass_inflation_onset_time:true};
}
function point(chi,x,settings={}){
 const k=kerr(chi),o=options(settings);
 const amp=log10Tail(chi,x,o);
 return {chi,x_advanced_shift_in_rg_units:x,advanced_time_shift_seconds:x*TG,
   dimensionless_late_time_ratio:1+x/o.x0,
   assumed_tail_p:o.p,assumed_reference_x0:o.x0,assumed_perturbation_epsilon:o.epsilon,
   log10_tail_before_blueshift:Math.log10(o.epsilon)-o.p*Math.log1p(x/o.x0)/LN10,
   log10_blueshift_contribution:k.hasInnerCauchyHorizon?k.beta*x/LN10:null,
   log10_sensitivity_proxy:amp,derivative_ln_proxy:derivativeLn(chi,x,o),
   stationary_inner_kappa_rate_per_s:k.innerSurfaceGravityRatePerS,
   inner_horizon_exists:k.hasInnerCauchyHorizon,
   status:k.hasInnerCauchyHorizon?"TOY_LATE_ADVANCED_TIME_SENSITIVITY_ONLY":
    "NO_DISTINCT_INNER_HORIZON_DIAGNOSTIC_DISABLED",
   geometry_backreaction_computed:false,
   perturbation_flux_observed:false,
   physical_center_prediction:null};
}
function selfTest(){
 const close=(a,b,t=1e-10)=>Math.abs(a-b)<=t*Math.max(1,Math.abs(a),Math.abs(b));
 if(kerr(0).beta!==null||log10Tail(0,10)!==null||threshold(0).x!==null)throw Error("chi0 exclusion");
 for(const chi of SPINS.slice(1)){
  const k=kerr(chi),q=Math.sqrt(1-chi*chi);
  const direct=(k.outerY-k.innerY)/(2*(k.innerY*k.innerY+chi*chi));
  if(!close(k.beta,direct,1e-10))throw Error("Kerr kappa inner geometric identity");
  if(!close(k.beta, q/(2*(1-q))))throw Error("Kerr second kappa identity");
  if(!close(k.innerSurfaceGravityRatePerS*k.eFoldTimeS,1))throw Error("physical time units");
  if(!close(log10Tail(chi,0),Math.log10(DEFAULTS.epsilon)))throw Error("initial amplitude");
  for(const x of [0,1,10,100,1000]){
    const h=1e-4,der=(log10Tail(chi,x+h)-log10Tail(chi,Math.max(0,x-h)))*
      LN10/(x===0?h:2*h);
    if(!close(der,derivativeLn(chi,x),1e-6))throw Error("derivative test");
  }
  const first=threshold(chi);
  if(first.x===null||!close(log10Tail(chi,first.x),DEFAULTS.thresholdLog10,1e-8))
   throw Error("threshold bisection");
  if(derivativeLn(chi,first.x)<=0)throw Error("threshold wrong branch");
  const xMin=turningPoint(chi);
  if(xMin>0&&!close(derivativeLn(chi,xMin),0,1e-8))throw Error("turning point");
 }
 const k99=kerr(.99),k9=kerr(.9),k5=kerr(.5);
 if(!(k99.beta<k9.beta&&k9.beta<k5.beta))throw Error("spin order at selected values");
 const huge=point(.5,1e6);
 if(!Number.isFinite(huge.log10_sensitivity_proxy))throw Error("log overflow");
 if(huge.log10_sensitivity_proxy<1e5)throw Error("incorrect large amplification");
 let invalidCaught=false;try{options({epsilon:0})}catch{invalidCaught=true}
 if(!invalidCaught)throw Error("bad input not guarded");
 return {passed:true,test_spins:SPINS,kg_seconds:TG,
  spin_zero_has_no_inner_horizon:true,inner_surface_gravity_formula:"PASS",
  time_units:"PASS",local_derivative:"PASS",turning_point:"PASS",
  threshold_bracketing:"PASS",log_overflow_protection:"PASS",
  large_growth_is_not_a_solved_perturbed_metric:true,
  default_crossings:SPINS.map(chi=>({chi,kappa:kerr(chi).innerSurfaceGravityRatePerS,
   efold_s:kerr(chi).eFoldTimeS,threshold:threshold(chi)}))};
}
const api=Object.freeze({C,GM_SUN,M,RG,TG,SPINS,DEFAULTS,kerr,options,
 log10Tail,derivativeLn,turningPoint,threshold,point,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.Bound16MassInflation=api;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
