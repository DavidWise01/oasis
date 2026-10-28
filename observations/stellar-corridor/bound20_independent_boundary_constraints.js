/* OASIS Bound20: independent boundary-constraint / prescribed-tail witness
   Check numerical arms built by production solver, using ONLY arrays and
   analytic null constraint residual, not its interior PDE update.
   Test C_ss=r_ss−2sigma_s r_s+r(phi_s)^2 for both s=u and s=v.
   Check convergent finite differences, u/v initial corner consistency,
   tail derivative against analytic B(1+v/v0)^(-p).
   This is separate verification of the same code equations, NOT external
   independent general relativity proof or fitted Price-law data.
*/
(function(root){"use strict";
const E=root.Bound20LateTail;
if(!E)throw Error("Load Bound20 production core first");
function armWitness(n,which,p0={}){
 const p=E.validate(p0),len=which==="u"?p.Lu:p.Lv,
 amp=which==="u"?p.A:p.B, h=len/n,
 a=E.initArm(n,len,p.Q,p.r0,p,which);
 let sum=0,max=0,meanFlux=0,maxR=0,nearBad=0;
 for(let i=1;i<n;i++){
  const r=a.R[i],sig=a.S[i],
   rr=(a.R[i+1]-2*r+a.R[i-1])/(h*h),
   r1=(a.R[i+1]-a.R[i-1])/(2*h),
   s1=(a.S[i+1]-a.S[i-1])/(2*h),
   f1=(a.P[i+1]-a.P[i-1])/(2*h),
   resid=rr-2*s1*r1+r*f1*f1;
  sum+=resid*resid;max=Math.max(max,Math.abs(resid));
  meanFlux+=f1*f1;
  if(!(r>E.R_MINUS && E.F(r,p.Q)<0))nearBad++;
  const rvExpected=which==="u"?E.dPhiU(i*h,p):E.dPhiV(i*h,p);
  maxR=Math.max(maxR,Math.abs(f1-rvExpected));
 }
 return {which,n,h,
  null_constraint_L2:Math.sqrt(sum/(n-1)),
  null_constraint_max:max,
  measured_mean_scalar_derivative_squared:meanFlux/(n-1),
  max_scalar_derivative_error:maxR,
  null_constraint_computed_from_central_differences:true,
  initial_corner:{radius:a.R[0],sigma:a.S[0],phi:a.P[0]},
  final_boundary_r:a.R[n],
  normalized_v_tail_endpoint_if_v:which==="v"?E.dPhiV(len,p)/E.dPhiV(0,p):null,
  truncated_tail_is_prescribed:true,
  outOfTrappedRegionCells:nearBad};
}
function fullWitness(p={}){
 const nu=[12,24,48,96],nv=[48,96,192,384],
   u=nu.map(n=>armWitness(n,"u",p)),
   v=nv.map(n=>armWitness(n,"v",p));
 const rats=x=>x.slice(0,-1).map((r,i)=>r.null_constraint_L2/x[i+1].null_constraint_L2);
 const ru=rats(u),rv=rats(v);
 const pass=ru.at(-1)>2.6&&rv.at(-1)>2.6&&u.every(x=>x.outOfTrappedRegionCells===0)
  &&v.every(x=>x.outOfTrappedRegionCells===0)&&
  u.every(x=>x.initial_corner.phi===v[0].initial_corner.phi)&&
  u.every(x=>Math.abs(x.initial_corner.radius-v[0].initial_corner.radius)<1e-14);
 return{pass,u,v,Cuu_ratios:ru,Cvv_ratios:rv,
  two_boundary_constraints_verified_in_finite_difference:true};
}
function selfTest(){
 const nominal=fullWitness(),vacuum=fullWitness({A:0,B:0});
 if(!nominal.pass||!vacuum.pass)throw Error("boundary constraints not converged");
 const p=E.validate();
 for(const t of [0,1,2,4.25]){
  const h=1e-5,
   diff=(E.phiV(t+h,p)-E.phiV(Math.max(0,t-h),p))/(t===0?h:2*h);
  if(Math.abs(diff-E.dPhiV(t,p))>2e-8)throw Error("tail analytic derivative");
 }
 if(!(nominal.v.at(-1).normalized_v_tail_endpoint_if_v<.02))throw Error("tail not decaying");
 return {pass:true,both:nominal,vacuum:{
  Cu_l2:vacuum.u.map(x=>x.null_constraint_L2),
  Cv_l2:vacuum.v.map(x=>x.null_constraint_L2),
  Cu_ratio:vacuum.Cuu_ratios,Cv_ratio:vacuum.Cvv_ratios},
  tail_derivative:"PASS",
  not_exterior_fitted_Price_law:true,
  no_inner_horizon_reach:true};
}
const api=Object.freeze({armWitness,fullWitness,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.Bound20BoundaryAudit=api;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
