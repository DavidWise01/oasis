/* OASIS Natural Bound 13 | 2026-10-27
   Layer A: quasi-static, one-dimensional elastic uniform rod in local
            Schwarzschild E=1 freely falling frame; hypothetical material.
   Layer B: exact stationary Kerr horizon, static limit, ISCO and horizon area
            for dimensionless spin chi. DO NOT substitute Kerr metrics into
            Schwarzschild free-fall Jacobi/stress formulas.
   No Kerr free-fall tetrad has been specified or fitted: Kerr tidal eigenvalues
   and Kerr material stresses are intentionally UNAVAILABLE.
   24! rank remains a symbolic registry, not time/energy/mass flow.
*/
(function(root){"use strict";
const C=299792458,GM_SUN=1.3271244e20,MS=4.297e6,LP=1.616255e-35;
const RG=GM_SUN*MS/C**2,RS=2*RG,START=100*RS;
const K_STOP=Math.pow(12*RS*RS*LP**4,1/6);
const DEFAULT=Object.freeze({label:"STEEL_LIKE_ILLUSTRATIVE",rho:7800,
 E:200e9,yieldStress:250e6,L:1,quasiLimit:.1,localLimit:.01});
const KNOWN_STEEL=Object.freeze({...DEFAULT});
const KNOWN_ALUMINUM=Object.freeze({label:"ALUMINUM_LIKE_ILLUSTRATIVE",
 rho:2700,E:70e9,yieldStress:150e6,L:1,quasiLimit:.1,localLimit:.01});
const CONSTANTS=Object.freeze({C,GM_SUN,MS,LP,RG,RS,START,K_STOP,DEFAULT,KNOWN_STEEL,KNOWN_ALUMINUM});
function positive(x,name){if(!Number.isFinite(x)||x<=0)throw Error(name+" must be finite >0");return x;}
function material(m=DEFAULT){const a={...DEFAULT,...m};
 for(const k of ["rho","E","yieldStress","L","quasiLimit","localLimit"])positive(a[k],k);
 if(a.quasiLimit>=1||a.localLimit>=1)throw Error("Limit must be <1");
 return a;}
function lambdaR(r){positive(r,"radius");return C*C*RS/(r*r*r);}
function curvatureLength(r){positive(r,"radius");return Math.sqrt(r*r*r/RS);}
function stressAt(r,m=DEFAULT){
 let a=material(m);
 if(!(r>0))return {r,status:"ZERO_UNRESOLVED",radialStressPa:null};
 if(r>K_STOP&&r>START)return {r,status:"OUTSIDE_CHOSEN_WORLDLINE",radialStressPa:null};
 if(r<K_STOP)return {r,status:"AFTER_CLASSICAL_CURVATURE_STOP",radialStressPa:null};
 const lam=lambdaR(r),cSound=Math.sqrt(a.E/a.rho),waveTime=a.L/cSound,
 tidalTime=1/Math.sqrt(lam),waveRatio=waveTime/tidalTime,
 smallRatio=a.L/Math.min(r,curvatureLength(r));
 // Rigid quasi-static 1D rod maintained near center geodesic,
 // ρ λ integral of a uniform rod from midpoint to free end:
 // sigma(x)=rho*lambda*(L²/8 − x²/2) with |x|<=L/2.
 // At midpoint radial stress is positive tension; each transverse
 // axis with half magnitude is a negative-compression proxy.
 const sigma=a.rho*lam*a.L*a.L/8,trans=-sigma/2;
 const stressFraction=sigma/a.yieldStress;
 let status=stressFraction>=1?"YIELD_PROXY_EXCEEDED":
    waveRatio>a.quasiLimit?"QUASISTATIC_WAVE_GATE_FAILED":
    smallRatio>a.localLimit?"LOCAL_LENGTH_GATE_FAILED":
    "WITHIN_ALL_CHOSEN_QUASISTATIC_GATES";
 return {r,status,lambdaR_s2:lam,
         radialStressPa:sigma,eachTransverseStressPa:trans,
         yieldFraction:stressFraction,characteristicWaveSpeedMps:cSound,
         waveCrossingS:waveTime,tidalTimeS:tidalTime,
         waveToTidalTime:waveRatio,localSmallnessRatio:smallRatio,
         curvatureLengthM:curvatureLength(r),
         stressProfile:"sigma(x)=rho*lambda*(L*L/8 - x*x/2); -L/2<=x<=L/2",
         extrapolatedStressOnly:status!=="WITHIN_ALL_CHOSEN_QUASISTATIC_GATES",
         materialIsMeasured:false,
         kerrStress:null};
}
function thresholdRadii(m=DEFAULT){
 const a=material(m);
 // sigma=rho*c²*rs*L²/(8r³); set = yield stress.
 const rYield=Math.cbrt(a.rho*C*C*RS*a.L*a.L/(8*a.yieldStress));
 // (L/sqrt(E/rho)) sqrt(c² rs/r³) = quasiLimit
 const rWave=Math.cbrt(a.rho*C*C*RS*a.L*a.L/(a.E*a.quasiLimit*a.quasiLimit));
 // L/min(r,sqrt(r³/rs)) <= localLimit. At r<=rs curvature length
 // is smaller; at r>=rs r is smaller.
 const rLength=Math.max(a.L/a.localLimit,
  Math.cbrt(a.L*a.L*RS/(a.localLimit*a.localLimit)));
 const firstFromStart=Math.max(rYield,rWave,rLength,K_STOP);
 const reasons=[];
 const eps=1e-8;
 if(Math.abs(rYield/firstFromStart-1)<eps)reasons.push("YIELD_PROXY");
 if(Math.abs(rWave/firstFromStart-1)<eps)reasons.push("WAVE_QUASISTATIC_GATE");
 if(Math.abs(rLength/firstFromStart-1)<eps)reasons.push("BODY_LOCAL_LENGTH_GATE");
 if(Math.abs(K_STOP/firstFromStart-1)<eps)reasons.push("CLASSICAL_CURVATURE_GATE");
 return {rYield,rWave,rLength,rCurvature:K_STOP,firstFromStart,
         firstReasons:reasons,startsOutsideValidity:firstFromStart>=START};
}
function kerr(chi){
 if(!Number.isFinite(chi)||chi<0||chi>1)throw Error("spin chi must be 0..1");
 const q=Math.sqrt(Math.max(0,1-chi*chi)),a=chi*RG;
 const rPlus=RG*(1+q),rMinus=RG*(1-q);
 const z1=1+Math.cbrt(1-chi*chi)*(Math.cbrt(1+chi)+Math.cbrt(1-chi));
 const z2=Math.sqrt(3*chi*chi+z1*z1);
 const disc=Math.sqrt(Math.max(0,(3-z1)*(3+z1+2*z2)));
 const iscoPro=RG*(3+z2-disc),iscoRetro=RG*(3+z2+disc);
 const rErgoEq=2*RG,rErgoPole=rPlus;
 const area=4*Math.PI*(rPlus*rPlus+a*a);
 const horizonEquivalentRadius=Math.sqrt(area/(4*Math.PI));
 const omegaH=C*chi/(2*RG*(1+q));
 return {chi,r_g_m:RG,r_plus_m:rPlus,r_minus_m:rMinus,
   r_ergosurface_equator_m:rErgoEq,r_ergosurface_pole_m:rErgoPole,
   equatorial_ergoregion_width_m:rErgoEq-rPlus,
   isco_prograde_m:iscoPro,isco_retrograde_m:iscoRetro,
   horizon_area_m2:area,horizon_equivalent_area_radius_m:horizonEquivalentRadius,
   horizon_angular_rad_s:omegaH,horizon_frequency_hz:omegaH/(2*Math.PI),
   kerr_electric_tidal_falling_tetrad_eigenvalues_s2:null,
   kerr_body_stress_pa:null,
   spin_measured_for_SgrA:false,
   spin_is_assumed_parameter:true,
   kerr_areal_coordinate_caution:"Boyer-Lindquist r is not the Kerr horizon areal radius."};
}
function kerrKretschmann(r,theta,chi){
 positive(r,"r");if(!Number.isFinite(theta))throw Error("theta must be finite");
 const spin=kerr(chi),a=chi*RG,ct=Math.cos(theta),v=a*a*ct*ct,rr=r*r;
 // K=48 rg²*(r^6 - 15r^4 a²cos²theta +15r²a⁴cos^4theta
 // -a^6cos^6theta)/(r² +a²cos²theta)^6
 const numerator=(rr*rr*rr-15*rr*rr*v+15*rr*v*v-v*v*v);
 const denominator=Math.pow(rr+v,6);
 return 48*RG*RG*numerator/denominator;
}
function selfTest(){
 const close=(x,y,t=1e-9)=>Math.abs(x-y)<=t*Math.max(1,Math.abs(x),Math.abs(y));
 const a=stressAt(START),h=stressAt(RS);
 if(!close(a.radialStressPa,DEFAULT.rho*lambdaR(START)/8))throw Error("initial stress");
 if(!close(h.radialStressPa,DEFAULT.rho*lambdaR(RS)/8))throw Error("horizon stress");
 if(!close(h.eachTransverseStressPa,-h.radialStressPa/2))throw Error("transverse stress");
 if(!close(h.characteristicWaveSpeedMps,Math.sqrt(DEFAULT.E/DEFAULT.rho)))throw Error("sound speed");
 const threshold=thresholdRadii(DEFAULT);
 if(!close(stressAt(threshold.rYield).yieldFraction,1))throw Error("yield radius");
 if(!close(stressAt(threshold.rWave).waveToTidalTime,DEFAULT.quasiLimit))throw Error("wave radius");
 if(!close(stressAt(threshold.rLength).localSmallnessRatio,DEFAULT.localLimit))throw Error("local length radius");
 if(stressAt(K_STOP/10).radialStressPa!==null)throw Error("curvature stop breached");
 let k0=kerr(0),k9=kerr(.9),k1=kerr(1);
 if(!close(k0.r_plus_m,RS)||!close(k0.isco_prograde_m,3*RS)||
    !close(k0.isco_retrograde_m,3*RS))throw Error("Schwarzschild limit failed");
 if(!close(k1.r_plus_m,RG)||!close(k1.isco_prograde_m,RG,1e-7)||
    !close(k1.isco_retrograde_m,9*RG,1e-7))throw Error("extremal limit");
 if(!(k9.isco_prograde_m<k0.isco_prograde_m&&
      k9.isco_retrograde_m>k0.isco_retrograde_m))throw Error("ISCO ordering");
 if(!close(k9.r_ergosurface_equator_m,RS))throw Error("equatorial static limit");
 if(!close(k9.horizon_equivalent_area_radius_m**2,
         k9.r_plus_m**2+(.9*RG)**2))throw Error("intrinsic area");
 for(const spin of [0,.2,.5,.9,.99,1]){
  for(const r of [3*RG,6*RG,12*RG]){
   const eq=kerrKretschmann(r,Math.PI/2,spin);
   const schw=48*RG*RG/r**6;
   if(!close(eq,schw,1e-10))throw Error("K equatorial test "+spin);
   if(spin===0&&!close(kerrKretschmann(r,0,spin),schw))
    throw Error("K zero-spin angle independence");
  }
 }
 // exact 1D rod stress equilibrium: dσ/dx=-rho λ x, σ(±L/2)=0
 const lambda=lambdaR(6*RG),v=DEFAULT.rho*lambda,half=DEFAULT.L/2;
 const sigma=x=>v*(DEFAULT.L**2/8-x*x/2);
 const d=.0001;
 for(const x of [-.2,0,.2]){
  const deriv=(sigma(x+d)-sigma(x-d))/(2*d);
  if(!close(deriv,-v*x,1e-8))throw Error("rod balance");
 }
 if(!close(sigma(half),0)||!close(sigma(-half),0))throw Error("free ends");
 if(kerr(.9).kerr_electric_tidal_falling_tetrad_eigenvalues_s2!==null)
  throw Error("fabricated Kerr falling-frame tidal eigenvalues");
 return {pass:true,model:"quasistatic_1d_free_end_rod_plus_independent_Kerr_geometry",
  steel_like_horizon_stress_pa:h.radialStressPa,
  steel_like_r_yield_km:threshold.rYield/1000,
  steel_like_r_wave_km:threshold.rWave/1000,
  steel_like_first_gate_km:threshold.firstFromStart/1000,
  first_gate_reasons:threshold.firstReasons,
  kerr_spin0_horizon_r_s:"PASS",kerr_spin0_isco_3rs:"PASS",
  kerr_spin1_limit:"PASS",equatorial_K_spin_independence:"PASS",
  material_midpoint_stress_balance:"PASS",tetrad_force_not_fabricated:true};
}
const api=Object.freeze({...CONSTANTS,material,lambdaR,curvatureLength,
 stressAt,thresholdRadii,kerr,kerrKretschmann,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.Bound13MaterialKerr=api;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
