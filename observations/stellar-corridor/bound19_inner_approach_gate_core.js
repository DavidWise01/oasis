/* OASIS Natural Bound 19 | 2026-10-28
   Resolution-escalating near-inner-horizon DOMAIN GATE, not AMR.
   Reuse frozen Bound18 double-null Einstein-Maxwell-neutral-scalar core.
   Physical scope: small square patches at separately CHOSEN RN trapped
   starting radii. Not one continued worldline or late-v Price tail.
   Geometric units M=G=c=1,Q=.8, r-=.4, r+=1.6.
   Stop if the ENTIRE patch crosses selected guard r_guard=r-+0.0005(r+-r-),
   or evolution fails, mass/constraint/flux-identity refinement fails.
   The guard is a CHOSEN numerical gate, no universal invariant.
   No actual adaptive local mesh refinement, no curvatures fitted.
 */
(function(root){"use strict";
const E=root.Bound18EMS;if(!E)throw Error("Load frozen Bound18 source first");
const R_MINUS=.4,R_PLUS=1.6,GAP=1.2,GUARD_FRACTION=.0005,
 R_GUARD=R_MINUS+GAP*GUARD_FRACTION,
 DEFAULT=Object.freeze({Q:.8,A:.02,B:.015,L:.4}),
 NLIST=Object.freeze([24,48,96,192]),
 SCAN=Object.freeze([.8,.6,.5,.45,.42,.415,.41,.405]);
const almost=(x,y,eps=1e-8)=>Math.abs(x-y)<=eps*Math.max(1,Math.abs(x),Math.abs(y));
function sampleAt(grid,N,ii,jj){
 const {R,S,P}=grid,h=.4/N,r=R[ii][jj],s=S[ii][jj],
   ru=(R[ii+1][jj]-R[ii-1][jj])/(2*h),
   rv=(R[ii][jj+1]-R[ii][jj-1])/(2*h),
   pu=(P[ii+1][jj]-P[ii-1][jj])/(2*h),
   pv=(P[ii][jj+1]-P[ii][jj-1])/(2*h);
 return {r,s,ru,rv,pu,pv,mass:E.mass(r,s,ru,rv,.8)};
}
function fluxWitness(run){
 const N=run.N,c=N/2,h=DEFAULT.L/N,G=run.grid,p=sampleAt(G,N,c,c);
 const du=(sampleAt(G,N,c+1,c).mass-sampleAt(G,N,c-1,c).mass)/(2*h);
 const dv=(sampleAt(G,N,c,c+1).mass-sampleAt(G,N,c,c-1).mass)/(2*h);
 const expectedDu=-2*p.r*p.r*Math.exp(-2*p.s)*p.rv*p.pu*p.pu,
   expectedDv=-2*p.r*p.r*Math.exp(-2*p.s)*p.ru*p.pv*p.pv;
 return {
  m_u_numeric:du,m_u_from_flux_identity:expectedDu,
  m_u_residual:du-expectedDu,
  m_v_numeric:dv,m_v_from_flux_identity:expectedDv,
  m_v_residual:dv-expectedDv,
  source_spherical_mass_identity:
    "m_u=-2r²exp(-2sigma) r_v phi_u² ; m_v=-2r²exp(-2sigma) r_u phi_v²",
  midpoint_trapped:p.ru<0&&p.rv<0,
  positivity_expected_in_trapped_region:expectedDu>=0&&expectedDv>=0};
}
function monitorRun(N,{r0,A=DEFAULT.A,B=DEFAULT.B}){
 const run=E.evolve(N,{Q:DEFAULT.Q,r0,L:DEFAULT.L,A,B},true);
 // all computed interior plus corner (which is the minimum here)
 const minR=Math.min(run.minimum_interior_r,run.corner_r);
 const t=fluxWitness(run);
 return {N,r0,A,B,h:run.h,
  mass:run.center.mass,center_r:run.center.r,
  corner_r:run.corner_r,min_r_including_corner:minR,
  normalized_inner_gap:(minR-R_MINUS)/GAP,
  safe_wrt_declared_guard:minR>R_GUARD,
  Cuu_l2:run.constraints.Cuu_l2,Cvv_l2:run.constraints.Cvv_l2,
  Cuu_max:run.constraints.Cuu_max,Cvv_max:run.constraints.Cvv_max,
  midpoint_flux:t,mass_baseline_RN:1,
  delta_mass:run.center.mass-1,
  actual_Kerr_interpretation:false};
}
function ratio(first,second){return Math.abs(first)/Math.max(1e-30,Math.abs(second))}
function analyze(r0,A=DEFAULT.A,B=DEFAULT.B){
 if(!(Number.isFinite(r0)&&r0>R_MINUS&&r0<R_PLUS))throw Error("starting radius must be trapped RN r-<r0<r+");
 if(!(A>=0&&B>=0&&A<=.1&&B<=.1))throw Error("pulse amplitudes in [0,.1]");
 let records=[],status=null;
 for(const N of NLIST){
  try{
   const r=monitorRun(N,{r0,A,B});records.push(r);
   if(!r.safe_wrt_declared_guard){
    status="ABORT_PRE_INNER_GUARD";break;
   }
   if(!r.midpoint_flux.midpoint_trapped || !r.midpoint_flux.positivity_expected_in_trapped_region){
    status="ABORT_SIGN_OR_FLUX";break;
   }
  }catch(err){status="ABORT_EVOLUTION_DOMAIN";records.push({N,error:String(err)});break;}
 }
 if(status)return {r0,A,B,status,records,
   accepted:false,guard_radius:R_GUARD,stopped_without_extrapolation:true};
 const [a,b,c,d]=records;
 const metric=x=>x.mass+x.center_r;
 const solRatios=[ratio(metric(a)-metric(b),metric(b)-metric(c)),
   ratio(metric(b)-metric(c),metric(c)-metric(d))];
 // Use a scalar difference only (mass) for independent checkpoint convergence
 const massRatios=[ratio(a.mass-b.mass,b.mass-c.mass),ratio(b.mass-c.mass,c.mass-d.mass)];
 const cuRatios=[ratio(a.Cuu_l2,b.Cuu_l2),ratio(b.Cuu_l2,c.Cuu_l2),ratio(c.Cuu_l2,d.Cuu_l2)];
 const cvRatios=[ratio(a.Cvv_l2,b.Cvv_l2),ratio(b.Cvv_l2,c.Cvv_l2),ratio(c.Cvv_l2,d.Cvv_l2)];
 const fuRatios=[ratio(Math.abs(a.midpoint_flux.m_u_residual),Math.abs(b.midpoint_flux.m_u_residual)),
   ratio(Math.abs(b.midpoint_flux.m_u_residual),Math.abs(c.midpoint_flux.m_u_residual)),
   ratio(Math.abs(c.midpoint_flux.m_u_residual),Math.abs(d.midpoint_flux.m_u_residual))];
 const fvRatios=[ratio(Math.abs(a.midpoint_flux.m_v_residual),Math.abs(b.midpoint_flux.m_v_residual)),
   ratio(Math.abs(b.midpoint_flux.m_v_residual),Math.abs(c.midpoint_flux.m_v_residual)),
   ratio(Math.abs(c.midpoint_flux.m_v_residual),Math.abs(d.midpoint_flux.m_v_residual))];
 const convergenceCheck={
  mass_last_ratio:massRatios[1],
  Cuu_last_ratio:cuRatios[2],Cvv_last_ratio:cvRatios[2],
  m_u_flux_last_ratio:fuRatios[2],m_v_flux_last_ratio:fvRatios[2],
  expected_2nd_order_step_ratio:4,
  success:[massRatios[1],cuRatios[2],cvRatios[2],fuRatios[2],fvRatios[2]].every(x=>x>2.7&&x<5.3)};
 const accepted=convergenceCheck.success;
 return {r0,A,B,status:accepted?"ACCEPT_CONVERGENT_BEFORE_DECLARED_GUARD":"ABORT_REFINEMENT_UNVERIFIED",
  accepted,guard_radius:R_GUARD,records,
  convergenceCheck,ratios:{solution:solRatios,mass:massRatios,
   Cuu:cuRatios,Cvv:cvRatios,flux_u:fuRatios,flux_v:fvRatios},
  finest:d,maximum_sampled_depth_fraction:1-d.normalized_inner_gap,
  physically_realized_late_time_mass_inflation:false,
  local_adaptive_mesh_refinement_used:false,
  resolution_escalated_globally:true};
}
function scan(){
 return SCAN.map(r0=>analyze(r0));
}
function selfTest(){
 const x=scan(),accepted=x.filter(s=>s.accepted);
 if(accepted.length!==5||x.length!==8)throw Error("expected 5 accepted and 3 guarded");
 for(const a of accepted){
  if(!a.finest||a.finest.min_r_including_corner<=R_GUARD)throw Error("failed radius gate");
  if(a.ratios.mass[1]<=2.7||a.convergenceCheck.Cuu_last_ratio<=2.7||
   a.convergenceCheck.Cvv_last_ratio<=2.7)throw Error("refinement");
  if(a.convergenceCheck.m_u_flux_last_ratio<=2.7||a.convergenceCheck.m_v_flux_last_ratio<=2.7)
   throw Error("independent mass flux identity lacks convergence");
  if(!(a.finest.mass>1))throw Error("mass sign");
 }
 if(x[5].status!=="ABORT_PRE_INNER_GUARD"||
    x[6].status!=="ABORT_PRE_INNER_GUARD"||
    x[7].status!=="ABORT_EVOLUTION_DOMAIN")throw Error("guard statuses");
 const check=analyze(.42,.02,.015),baseline=E.evolve(192,{r0:.42,A:0,B:0});
 if(!almost(check.finest.mass,.0006852506301538+1,1e-8))throw Error("readback mass");
 if(Math.abs(baseline.center.mass-1)>1e-5)throw Error("vacuum mass");
 // Explicit amplitude-dependence witness: a reduced amplitude at .415
 // may pass the chosen 0.0005-gap guard, unlike .02/.015.
 const smaller=analyze(.415,.015,.01125);
 if(!smaller.accepted)throw Error("amplitude dependent domain gate");
 return {pass:true,kind:"resolution_escalation_not_local_AMR",
  physical_domain:"spherical charged RN+real scalar, NOT Kerr",
  charge_Q:DEFAULT.Q,r_minus:R_MINUS,r_plus:R_PLUS,chosen_guard:R_GUARD,
  accepted_count:accepted.length,aborted_count:x.length-accepted.length,
  scan_summary:x.map(z=>({r0:z.r0,status:z.status,finest_N:z.finest?.N||null,
    nearest_r:z.finest?.min_r_including_corner||z.records?.at(-1)?.min_r_including_corner||null,
    checkpoint_mass:z.finest?.mass||null,
    mass_2nd_order_ratio:z.convergenceCheck?.mass_last_ratio||null,
    Cuu_2nd_order_ratio:z.convergenceCheck?.Cuu_last_ratio||null,
    Cvv_2nd_order_ratio:z.convergenceCheck?.Cvv_last_ratio||null,
    mass_flux_u_ratio:z.convergenceCheck?.m_u_flux_last_ratio||null,
    mass_flux_v_ratio:z.convergenceCheck?.m_v_flux_last_ratio||null})),
  reduced_amplitude_at_r0_0415:{A:.015,B:.01125,status:smaller.status,
    nearest_r:smaller.finest?.min_r_including_corner,
    checkpoint_mass:smaller.finest?.mass},
  no_mass_inflation_at_inner_horizon_claim:true,center_prediction:null,
  actual_late_tail_initial_data_not_present:true};
}
const api=Object.freeze({DEFAULT,NLIST,SCAN,R_MINUS,R_PLUS,GAP,
 GUARD_FRACTION,R_GUARD,sampleAt,fluxWitness,monitorRun,analyze,scan,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.Bound19Guard=api;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
