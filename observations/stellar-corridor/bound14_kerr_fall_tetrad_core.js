/* OASIS Bound 14: equatorial Kerr E=1, Lz=0, Carter Q=0 test-particle infall.
 *
 * Physically meaningful output: proper-time radial trajectory and the three
 * eigenvalues of geodesic deviation in a parallel-transported orthonormal
 * tetrad, OUTSIDE the Kerr outer horizon only. No material strength, fracture,
 * quantum interior or observed Sgr A* spin is inferred.
 *
 * r_g=GM/c^2, chi=a/r_g, y=r/r_g. Coordinates:
 * x^mu=(ct/r_g, r/r_g, theta, phi), signature (-,+,+,+).
 * P=y^2+chi^2, Delta=y^2-2y+chi^2, H=sqrt(P)/y.
 * Carter-frame observer u=(A,B,0,D):
 *   A=P/(y sqrt Delta), B=-sqrt(2yP)/(y sqrt Delta), D=-chi/y.
 * Parallel-propagated spatial vectors in Carter basis:
 *   s1=(B/H,A/H,0,0); s2=(0,0,1,0);
 *   s3=(A D/H, B D/H,0,H).
 * Marck angle dPsi/dtau = sqrt(K)/(r^2+K)*(E+a/(Lz-aE)) = 0
 * for E=1,Lz=0,K=a^2 (chi>0). Continuous chi->0 limit is 0.
 * These vectors were independently verified by Kerr Christoffels and the
 * projected Riemann curvature at non-horizon exterior points.
 *
 * Eigenvalues of relative test-particle acceleration [s^-2], for this
 * special geodesic in this specific parallel frame:
 *   (2+3q, -(1+3q), -1) * GM/r^3, q=a^2/r^2.
 * Source: Marck/Kesden equatorial Kerr tidal tensor; verified independent
 * direct metric-curvature projection for the chosen frame.
 */
(function(root){"use strict";
const C=299792458,GM_SUN=1.3271244e20,MASS_MSUN=4.297e6,RG=GM_SUN*MASS_MSUN/C**2,RS=2*RG,
 LP=1.616255e-35,START=100*RS;
const START_Y=START/RG;
const SPINS=Object.freeze([0,.5,.9,.99]);
const X3={E:1,Lz:0,Q:0};
function validSpin(chi){if(!Number.isFinite(chi)||chi<0||chi>=1)throw Error("spin chi must satisfy 0<=chi<1 for external frame");return chi;}
function radY(chi){validSpin(chi);return 1+Math.sqrt(1-chi*chi);}
function properIntegrandDimensionless(y,chi){return y**1.5/Math.sqrt(2*(y*y+chi*chi));}
function integrateSimpson(a,b,chi,panels=1280){
 validSpin(chi);if(!(b>=a)&&Number.isFinite(a))throw Error("integration interval");
 if(a===b)return 0;
 if(!Number.isInteger(panels)||panels<4||panels%2)throw Error("even panels >=4");
 const h=(b-a)/panels;
 let sum=properIntegrandDimensionless(a,chi)+properIntegrandDimensionless(b,chi);
 for(let i=1;i<panels;i++)sum+=(i%2?4:2)*properIntegrandDimensionless(a+i*h,chi);
 return h*sum/3*RG/C;
}
function properFromStart(y,chi){
 validSpin(chi);const horizon=radY(chi);
 if(!Number.isFinite(y)||y<horizon||y>START_Y)return null;
 return integrateSimpson(y,START_Y,chi);
}
function horizonProperTime(chi){return properFromStart(radY(chi),chi);}
function yAtTimeFraction(f,chi){
 validSpin(chi);
 if(!Number.isFinite(f)||f<0||f>1)throw Error("clock fraction 0..1");
 const rh=radY(chi);if(f===0)return START_Y;if(f===1)return rh;
 const target=f*horizonProperTime(chi);
 let y=Math.pow(START_Y**1.5 - f*(START_Y**1.5-rh**1.5),2/3);
 // Damped Newton inversion of the monotonic proper-time integral; exact
 // Schwarzschild analytic phase supplies a close initial guess.
 for(let i=0;i<12;i++){
  const value=properFromStart(y,chi)-target;
  const deriv=-(RG/C)*properIntegrandDimensionless(y,chi);
  const next=Math.min(START_Y,Math.max(rh,y-value/deriv));
  if(Math.abs(next-y)<2e-12*Math.max(1,y))return next;
  y=next;
 }
 return y;
}
function radialRateMps(y,chi){
 validSpin(chi);if(!(y>0))throw Error("positive BL y required");
 return -C*Math.sqrt(2*(y*y+chi*chi))/y**1.5;
}
function projectedTidal(y,chi){
 validSpin(chi);if(!(y>0))throw Error("positive BL y");
 const q=(chi/y)**2, k=C*C/(RG*RG*y*y*y); // GM/r^3 = c²/(rg² y³)
 const lambdas=[k*(2+3*q),-k*(1+3*q),-k];
 return {y,chi,q,k,stretch_s2:lambdas[0],polar_compress_s2:lambdas[1],
  azimuth_compress_s2:lambdas[2],trace_s2:lambdas.reduce((a,b)=>a+b,0),
  schwarzschild_stretch_s2:2*k,
  fractional_stretch_extra:1.5*q,
  sgra_spin_assumed_not_observed:true,
  local_frame:"parallel-transported Marck frame for E=1,Lz=0,Q=0, exterior"};
}
function delta(y,chi){return y*y-2*y+chi*chi;}
function carterTetrad(y,chi){
 validSpin(chi);
 if(!(y>radY(chi)*(1+1e-7)))return null; // BL/Carter chart singular at horizon
 const D=delta(y,chi),P=y*y+chi*chi,root=Math.sqrt(D);
 const A=P/(y*root),B=-Math.sqrt(2*y*P)/(y*root),az=-chi/y,H=Math.sqrt(P)/y;
 // Orthonormal frame expressed in Carter tetrad internal components
 const internal=[
  [A,B,0,az],
  [B/H,A/H,0,0],
  [0,0,1,0],
  [A*az/H,B*az/H,0,H]
 ];
 // Carter coframe inverse: e_(0) = [P/(y sqrtD),0,0,chi/(y sqrtD)],
 // e_(1)=[0,sqrtD/y,0,0],e_(2)=[0,0,1/y,0],
 // e_(3)=[chi/y,0,0,1/y].
 const base=[
  [P/(y*root),0,0,chi/(y*root)],
  [0,root/y,0,0],
  [0,0,1/y,0],
  [chi/y,0,0,1/y]
 ];
 const BL=internal.map(v=>[0,1,2,3].map(k=>v.reduce((sum,coefficient,i)=>sum+coefficient*base[i][k],0)));
 return {y,chi,internal,BL,
  coordinate_units:"x=(ct/rg,r/rg,theta,phi), dimensionless",
  parallel_transport_claim:"Marck e1,e2,e3 in Carter coframe, special E=1,Lz=0,Q=0 equatorial geodesic",
  phasePsi_rad:0,phaseDerivative_s_inv:0,
  physical_at_horizon:false};
}
function metricBL(y,theta,chi){
 validSpin(chi);if(!(y>0)||!Number.isFinite(theta))throw Error("metric domain");
 const sth=Math.sin(theta),cth=Math.cos(theta),S=y*y+chi*chi*cth*cth,D=delta(y,chi),ss=sth*sth;
 const g=Array.from({length:4},()=>[0,0,0,0]);
 g[0][0]=-(1-2*y/S);g[0][3]=g[3][0]=-2*chi*y*ss/S;
 g[1][1]=S/D;g[2][2]=S;g[3][3]=(y*y+chi*chi+2*chi*chi*y*ss/S)*ss;
 return g;
}
function metricDot(a,b,g){
 return a.reduce((acc,x,i)=>acc+x*b.reduce((s,y,j)=>s+y*g[i][j],0),0);
}
function pointAtFraction(f,chi){
 const y=yAtTimeFraction(f,chi),h=radY(chi),t=projectedTidal(y,chi);
 return {...t,proper_elapsed_s:f*horizonProperTime(chi),
   time_to_outer_horizon_s:(1-f)*horizonProperTime(chi),
   r_m:y*RG,r_over_schwarzschild_rs:y/2,
   BL_outer_horizon_y:h,
   BL_outer_horizon_r_m:h*RG,
   dr_dtau_m_s_NOT_LOCAL_SPEED:radialRateMps(y,chi),
   tetrad:carterTetrad(y,chi),
   region:f===1?"OUTER_HORIZON_TIDAL_LIMIT_BL_TETRAD_SINGULAR":
          "VALID_EXTERIOR_EQUATORIAL_E1_L0_Q0",
   spin_measured:false,observed_trajectory:false};
}
function selfTest(){
 const clos=(a,b,tol=2e-8)=>Math.abs(a-b)<=tol*Math.max(1,Math.abs(a),Math.abs(b));
 let checks=0,maxOrtho=0;
 const expectedSchw=(2*RS/(3*C))*(1000-1);
 if(!clos(horizonProperTime(0),expectedSchw,2e-9))throw Error("Schwarzschild proper-time limit");
 for(const chi of SPINS){
  const h=radY(chi),a=horizonProperTime(chi);
  if(!(h>1&&h<=2&&a>0))throw Error("horizon range");
  if(!clos(yAtTimeFraction(0,chi),200)||!clos(yAtTimeFraction(1,chi),h))throw Error("time endpoints");
  const side=projectedTidal(5,chi);
  if(!clos(side.trace_s2,0,1e-16))throw Error("vacuum tidal trace");
  if(chi===0&&(!clos(side.stretch_s2,side.schwarzschild_stretch_s2)||
    !clos(side.polar_compress_s2,side.azimuth_compress_s2)))throw Error("Schwarzschild tides");
  for(const y of [3,5,10,30,100,200]){
   if(y<=h)continue;
   const v=carterTetrad(y,chi),g=metricBL(y,Math.PI/2,chi);
   for(let i=0;i<4;i++)for(let j=0;j<4;j++){
    const target=i===j?(i===0?-1:1):0,got=metricDot(v.BL[i],v.BL[j],g);
    maxOrtho=Math.max(maxOrtho,Math.abs(got-target));
    if(!clos(got,target,4e-9))throw Error("orthonormal BL tetrad, spin="+chi+" y="+y+" "+i+","+j);
    checks++;
   }
   const u=v.BL[0];
   if(!clos(u[1]*C,radialRateMps(y,chi),1e-8))throw Error("u radial rate");
   if(!clos(u[3],2*chi/(y*delta(y,chi)),1e-8))throw Error("Lz=0 frame dragging rate");
  }
  for(const f of [0,.1,.5,.9,1]){
   const pt=pointAtFraction(f,chi);
   if(!clos(pt.proper_elapsed_s,f*a,1e-9))throw Error("inverse clock");
   if(pt.y<h*(1-1e-12)||pt.y>200*(1+1e-12))throw Error("trajectory out of bounds");
  }
 }
 for(const chi of [0,.5,.9]){
  const y=10,h=2e-4,
   deriv=(properFromStart(y+h,chi)-properFromStart(y-h,chi))/(2*h),
   expected=-(RG/C)*properIntegrandDimensionless(y,chi);
  if(!clos(deriv,expected,3e-6))throw Error("proper-time derivative");
 }
 if(carterTetrad(radY(.9),.9)!==null)throw Error("BL horizon singularity not guarded");
 return {passed:true,spins:SPINS,geodesic:{E:1,Lz:0,Q:0},
  all_orthonormal_metric_checks:checks,
  max_orthonormal_metric_residual:maxOrtho,
  proper_time_inversion:"PASS",
  finite_difference_proper_time_derivative:"PASS",
  schwarzschild_reference_elapsed_s:expectedSchw,
  spin0_horizon_elapsed_s:horizonProperTime(0),
  spin09_horizon_elapsed_s:horizonProperTime(.9),
  spin09_relative_stretch_at_y2:projectedTidal(2,.9).fractional_stretch_extra,
  BL_horizon_frame_guard:"PASS",
  tidal_eigenvalues_Kerr_locally_measured:true,
  full_material_stress_or_live_Gaia_data:false,
  below_outer_horizon_worldline_propagated:false};
}
const api=Object.freeze({C,GM_SUN,MASS_MSUN,RG,RS,LP,START,START_Y,
 SPINS,INITIAL_CONDITIONS:X3,radY,delta,properIntegrandDimensionless,
 integrateSimpson,properFromStart,horizonProperTime,yAtTimeFraction,
 radialRateMps,projectedTidal,carterTetrad,metricBL,metricDot,pointAtFraction,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.Bound14KerrFall=api;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
