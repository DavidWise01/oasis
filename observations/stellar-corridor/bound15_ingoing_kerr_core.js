/* OASIS Bound15 | ingoing Kerr, continuous E=1,Lz=0,Q=0 local PP tetrad
   This is a stationary EXACT KERR model, NOT a verified physical interior.
   The ingoing chart is regular across the FUTURE outer horizon.
   End of interpretation is a DECLARED 1%-of-horizon-gap guard outside the
   Cauchy horizon; chi=0 instead ends at 0.02rg purely as a numeric/model guard.
   Metric units rg=GM/c^2; coord x=(v/rg, r/rg, theta, phi_tilde), v has length.
   Metric signature (-+++).
*/
(function(root){"use strict";
const K=root.Bound14KerrFall;
if(!K)throw Error("Load Bound14 core first.");
const C=K.C, RG=K.RG, RS=K.RS, MASS=K.MASS_MSUN,LP=K.LP;
const SPINS=Object.freeze([0,.5,.9,.99]);
const START_Y=K.START_Y, GUARD_FRACTION=.01,COUNT=729;
const indices=()=>[0,1,2,3];
function limits(chi){
 if(!(Number.isFinite(chi)&&chi>=0&&chi<1))throw Error("0<=chi<1 required");
 const s=Math.sqrt(1-chi*chi),outer=1+s,inner=1-s;
 const stop=inner+GUARD_FRACTION*(outer-inner);
 return {chi,y_outer:outer,y_inner:inner,y_stop:stop,
  guard_fraction:GUARD_FRACTION,
  kind:chi===0?"NONROTATING_POSITIVE_RADIUS_GUARD_NO_CAUCHY_HORIZON":
  "PRE_CAUCHY_HORIZON_1PERCENT_GAP_MODEL_GUARD",
  outer_radius_m:outer*RG,inner_radius_m:inner*RG,stop_radius_m:stop*RG};
}
function metric(y,theta,chi){
 if(!(y>0&&Number.isFinite(y)&&Number.isFinite(theta)))throw Error("metric domain");
 const sn=Math.sin(theta),sn2=sn*sn,cs=Math.cos(theta),S=y*y+chi*chi*cs*cs,P=y*y+chi*chi;
 const g=indices().map(()=>[0,0,0,0]);
 g[0][0]=-1+2*y/S;g[0][1]=g[1][0]=1;
 g[0][3]=g[3][0]=-2*chi*y*sn2/S;
 g[1][3]=g[3][1]=-chi*sn2;
 g[2][2]=S;
 g[3][3]=(P+2*chi*chi*y*sn2/S)*sn2;
 return g;
}
function inverseMetric(y,theta,chi){
 if(!(y>0&&Number.isFinite(y)&&Number.isFinite(theta)))throw Error("inverse metric domain");
 const sn2=Math.sin(theta)**2,S=y*y+chi*chi*Math.cos(theta)**2,P=y*y+chi*chi,D=P-2*y;
 const inv=indices().map(()=>[0,0,0,0]);
 inv[0][0]=chi*chi*sn2/S;
 inv[0][1]=inv[1][0]=P/S;
 inv[0][3]=inv[3][0]=chi/S;
 inv[1][1]=D/S;
 inv[1][3]=inv[3][1]=chi/S;
 inv[2][2]=1/S;
 inv[3][3]=1/(S*sn2);
 return inv;
}
function frame(y,chi){
 if(!(Number.isFinite(y)&&y>0))throw Error("r>0");
 limits(chi);
 const P=y*y+chi*chi,W=Math.sqrt(2*y*P),S=Math.sqrt(P),den=P+W;
 // Finite rationalized limits of Carter/Marck E1L0Q0 tetrad after
 // dv=dt+(P/Delta)dr; dphi_+=dphi+(chi/Delta)dr.
 // No division by Delta appears anywhere in this representation.
 const u=[(P*P/den-chi*chi)/(y*y),-W/(y*y),0,-2*chi/(y*(2*y+W))];
 const e1=[P*S/(y*den),S/y,0,chi*S/(y*den)];
 const e2=[0,0,1/y,0];
 const e3=[2*chi*S/(y*(2*y+W)),chi*W/(y*y*S),0,
  S*(y*y+W)/(y*y*den)];
 return {y,chi,PP_basis_ing:[u,e1,e2,e3],
  frame_coordinates:"(v/rg, y, theta, phi_+), future-ingoing Kerr",
  horizon_regular_in_chart:true,continued_from_bound14:true};
}
function dot(a,b,g){return a.reduce((z,v,i)=>z+v*b.reduce((w,x,j)=>w+x*g[i][j],0),0)}
function properTimeFromStart(y,chi){
 const l=limits(chi);
 if(!(y>=l.y_stop&&y<=START_Y))return null;
 return K.integrateSimpson(y,START_Y,chi);
}
function outerClock(chi){const l=limits(chi);return properTimeFromStart(l.y_outer,chi)}
function stopClock(chi){const l=limits(chi);return properTimeFromStart(l.y_stop,chi)}
function horizonToStop(chi){const l=limits(chi);return K.integrateSimpson(l.y_stop,l.y_outer,chi);}
function yAtInteriorClockFraction(f,chi){
 const l=limits(chi);
 if(!(f>=0&&f<=1&&Number.isFinite(f)))throw Error("fraction must be 0..1");
 if(f===0)return l.y_outer;if(f===1)return l.y_stop;
 const target=f*horizonToStop(chi);
 let lo=l.y_stop,hi=l.y_outer;
 // Enough for the interior seconds scale; avoid subtracting the 7.8h
 // accumulated exterior clock when finding a short inside interval.
 for(let i=0;i<48;i++){
  const mid=(lo+hi)/2,t=K.integrateSimpson(mid,l.y_outer,chi);
  if(t>target)lo=mid;else hi=mid;
 }
 return (lo+hi)/2;
}
function tidalAt(y,chi){
 if(!(y>0))throw Error("positive y");
 const l=limits(chi),r=K.projectedTidal(y,chi);
 const t=properTimeFromStart(y,chi);
 return {...r,r_m:y*RG,
  trajectory_proper_since_selected_start_s:t,
  since_outer_horizon_s:t===null?null:K.integrateSimpson(y,l.y_outer,chi),
  after_first_Cauchy_guard:y<l.y_stop,
  declared_status:y>l.y_outer?"EXTERIOR_MODEL":
   y===l.y_outer?"FUTURE_OUTER_HORIZON_REGULAR_INGOING_CHART":
   y>=l.y_stop?"INTERIOR_EXACT_KERR_BEFORE_MODEL_CAUCHY_GUARD":
   "OUTSIDE_DECLARED_MODEL_SCOPE",
  not_observed:true,
  curvature_note:"Kerr vacuum solution, NOT stable astrophysical interior"};
}
function positionAtFraction(f,chi){
 const l=limits(chi),y=yAtInteriorClockFraction(f,chi);
 const m=metric(y,Math.PI/2,chi),F=frame(y,chi);
 const proper=outerClock(chi)+f*horizonToStop(chi);
 return {index_fraction:f,chi,y,r_m:y*RG,
  elapsed_from_selected_start_proper_s:proper,
  elapsed_since_outer_crossing_proper_s:f*horizonToStop(chi),
  remaining_to_model_guard_proper_s:(1-f)*horizonToStop(chi),
  outer_horizon_y:l.y_outer,inner_horizon_y:l.y_inner,guard_y:l.y_stop,
  frame_ing:F.PP_basis_ing,
  local_eigenvalues:tidalAt(y,chi),
  metric_chart:"future ingoing EF Kerr",
  model_stop_status:f===1?"STOP_AT_DECLARED_PRE_INNER_HORIZON_GUARD":
   f===0?"OUTER_HORIZON_CROSSED_COORDINATE_REGULAR":
    "INTERIOR_EXACT_KERR_IDEALIZATION_ONLY",
  physical_quantum_or_inner_horizon_outcome:"UNKNOWN",
  physical_actual_stellar_observation:false};
}
function selfTest(){
 const close=(a,b,tol=1e-9)=>Math.abs(a-b)<=tol*Math.max(1,Math.abs(a),Math.abs(b));
 let checks=0,maxErr=0,maxMetricInv=0;
 for(const chi of SPINS){
  const l=limits(chi);
  if(!(l.y_stop>l.y_inner&&l.y_stop<l.y_outer))throw Error("inner guard");
  const insideTime=horizonToStop(chi);
  if(!(insideTime>0))throw Error("infall proper time positive");
  if(!close(outerClock(chi),K.horizonProperTime(chi),1e-8))throw Error("Bound14 clock mismatch");
  if(!close(yAtInteriorClockFraction(0,chi),l.y_outer)||
     !close(yAtInteriorClockFraction(1,chi),l.y_stop))throw Error("interior endpoints");
  for(const y of [l.y_outer+1, l.y_outer, (l.y_outer+l.y_stop)/2, l.y_stop]){
   const G=metric(y,Math.PI/2,chi),Gi=inverseMetric(y,Math.PI/2,chi),F=frame(y,chi);
   for(let a=0;a<4;a++)for(let b=0;b<4;b++){
    const target=a===b?1:0;
    let result=0;for(let j=0;j<4;j++)result+=G[a][j]*Gi[j][b];
    maxMetricInv=Math.max(maxMetricInv,Math.abs(result-target));
    if(!close(result,target,1e-8))throw Error("inverse ingoing metric");
    const want=a===b?(a===0?-1:1):0;
    const value=dot(F.PP_basis_ing[a],F.PP_basis_ing[b],G);
    maxErr=Math.max(maxErr,Math.abs(value-want));
    if(!close(value,want,1e-8))throw Error("orthonormality across horizon");
    checks++;
   }
   if(!close(F.PP_basis_ing[0][1]*K.C,K.radialRateMps(y,chi),1e-8))throw Error("radial geodesic");
   if(!close(tidalAt(y,chi).trace_s2,0,1e-15))throw Error("vacuum trace");
  }
  for(const f of [0,.1,.5,.9,1]){
   const y=yAtInteriorClockFraction(f,chi),p=positionAtFraction(f,chi);
   if(y<l.y_stop*(1-1e-12)||y>l.y_outer*(1+1e-12))throw Error("invalid trajectory");
   if(!close(p.elapsed_since_outer_crossing_proper_s,f*insideTime))throw Error("inside clock");
  }
  if(!close(horizonToStop(chi),stopClock(chi)-outerClock(chi),1e-8))throw Error("continuous clock");
 }
 if(!close(K.projectedTidal(2,0).stretch_s2,tidalAt(2,0).stretch_s2))throw Error("schwarzschild continuation");
 return {pass:true,spin_scenarios:SPINS,
  metric_inverse_checked:"PASS",metric_and_tetrad_component_comparisons:checks,
  max_tetrad_minkowski_error:maxErr,max_metric_inverse_error:maxMetricInv,
  all_future_horizon_frame_components_finite:true,
  Schwarzschild_horizon_clock_consistent_with_bound14:true,
  model_guard_not_actual_inner_physical_boundary:true,
  results:SPINS.map(chi=>{const l=limits(chi);return {chi,r_plus_y:l.y_outer,r_minus_y:l.y_inner,stop_y:l.y_stop,
    horizon_to_guard_proper_s:horizonToStop(chi),outer_horizon_proper_from_start_s:outerClock(chi),
    stop_kind:l.kind}}),
  physical_center_prediction:false,actual_inner_horizon_stability_verified:false};
}
const api=Object.freeze({SPINS,C,RG,RS,MASS,LP,START_Y,GUARD_FRACTION,COUNT,
 limits,metric,inverseMetric,frame,dot,properTimeFromStart,outerClock,stopClock,
 horizonToStop,yAtInteriorClockFraction,tidalAt,positionAtFraction,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.Bound15IngoingKerr=api;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
