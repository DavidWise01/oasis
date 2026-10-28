/* OASIS NATURAL CHECK 17 | Exact LOCAL DTR null-shell crossing, 2026-10-27
   Reissner-Nordström spherical Einstein-Maxwell thin-null-shell toy.
   Not rotating Kerr. Not Sgr A* charge measurement. No time-evolution PDE.
   Units G=c=M_background=1 and charge q=Q/M with 0<q<1.
   Four vacuum regions at same crossing sphere r:
     f_i=1-2 M_i/r+q^2/r^2, all have common fixed charge q
     M_0=1; M_in=1+din; M_out=1+dout;
     M_f=1+din+dout - 2 din*dout / (r f0).
   DTR exact: f0 * f_final = f_in * f_out.
   The background RN f0 is negative inside outer horizon and outside
   inner horizon, so with positive din/dout the crossing term is positive.
   Two-stream shell-crossing is a LOCAL junction, not a continuous mass
   inflation Einstein-field evolution. Interpret near inner horizon only
   with compatible null-shell causal orientation and matching conditions.
   Uses stable horizon-factorized f0=-(gap^2 * delta*(1-delta))/r^2.
 */
(function(root){"use strict";
const CHARGES=Object.freeze([.5,.8,.95,.99]);
const DEFAULT=Object.freeze({q:.8,din:1e-4,dout:1e-4,delta:.001});
const COUNT=729,DELTA_MIN=1e-10,DELTA_MAX=0.1,RG_SGRA_M=1.3271244e20*4.297e6/(299792458**2);
function nonneg(x,n){if(!Number.isFinite(x)||x<0)throw Error(n+" must be finite and nonnegative");return x;}
function parameters(p={}){
 const a={...DEFAULT,...p};
 if(!Number.isFinite(a.q)||a.q<=0||a.q>=1)throw Error("0 < q=Q/M < 1 required (charged spherical toy only)");
 nonneg(a.din,"din");nonneg(a.dout,"dout");
 if(!(a.delta>0&&a.delta<1&&Number.isFinite(a.delta)))throw Error("0<delta<1 required");
 return a;
}
function horizons(q){
 if(!(q>0&&q<1&&Number.isFinite(q)))throw Error("subextremal nonzero q required");
 const t=Math.sqrt(1-q*q);
 return {q,outer:1+t,inner:1-t,gap:2*t,inner_horizon_is_charged_not_Kerr:true};
}
function sample(p={}){
 const x=parameters(p),h=horizons(x.q),r=h.inner+h.gap*x.delta;
 // Exact factorization of background f0: (r-r+)(r-r-)/r².
 const f0=-(h.gap*h.gap*x.delta*(1-x.delta))/(r*r);
 const fi=f0-2*x.din/r,fo=f0-2*x.dout/r;
 const interaction=-2*x.din*x.dout/(r*f0);
 const mfinal=1+x.din+x.dout+interaction;
 const ff=f0-2*(x.din+x.dout+interaction)/r;
 const product1=f0*ff,product2=fi*fo;
 const residual=(product1-product2)/Math.max(1e-300,Math.abs(product1),Math.abs(product2));
 const shellScale=Math.max(2*x.din/r,2*x.dout/r)/Math.abs(f0);
 return {...x,r,outer:h.outer,inner:h.inner,gap:h.gap,f0,fi,fo,ff,
  before_m:1,after_m:mfinal,nonlinear_cross_mass:interaction,
  baseline_without_interaction:1+x.din+x.dout,
  incoming_shell_mass:x.din,outgoing_shell_mass:x.dout,
  crossing_to_sum_of_shells:x.din+x.dout>0?interaction/(x.din+x.dout):null,
  DTR_normalized_residual:residual,
  background_trapped_region:f0<0,
  same_sign_branch:Math.sign(f0)===Math.sign(fi)&&Math.sign(f0)===Math.sign(fo),
  near_horizon_small_shell_ratio:shellScale,
  perturbative_shell_relative_to_f0:shellScale<=.1,
  strict_delta_positive:true,
  charged_RN_not_Kerr:true,
  observed_mass_inflation:false,
  evolved_metric:false,
  physical_center_solution:false,
  local_exact_junction_only:true};
}
function logScan(q=.8,din=1e-4,dout=1e-4,n=COUNT){
 if(!Number.isInteger(n)||n<2)throw Error("n must be >=2");
 const out=[];
 for(let i=0;i<n;i++){
  const log=Math.log10(DELTA_MAX)+(Math.log10(DELTA_MIN)-Math.log10(DELTA_MAX))*i/(n-1);
  out.push(sample({q,din,dout,delta:10**log}));
 }
 return out;
}
function selfTest(){
 const approx=(a,b,t=1e-9)=>Math.abs(a-b)<=t*Math.max(1,Math.abs(a),Math.abs(b));
 const checks=[];
 for(const q of CHARGES){
  const data=logScan(q),h=horizons(q),first=data[0],last=data.at(-1);
  if(!(h.inner>0&&h.inner<h.outer&&first.r>last.r&&last.r>h.inner))throw Error("inner radius");
  if(!(last.nonlinear_cross_mass>first.nonlinear_cross_mass*1e5))throw Error("expected near horizon amplification");
  for(const s of data){
   if(!s.background_trapped_region||!s.same_sign_branch)throw Error("crossing wrong region or signs");
   if(!(Math.abs(s.DTR_normalized_residual)<1e-10))throw Error("DTR constraint violated");
   if(!(s.nonlinear_cross_mass>=0))throw Error("positive product not positive correction");
   if(!(s.after_m>=s.baseline_without_interaction))throw Error("nonlinear mass decrease");
  }
  checks.push({q,samples:data.length,nearest_mass:last.after_m,
    outer_far_mass:first.after_m,nearest_DTR_residual:last.DTR_normalized_residual});
 }
 const offIn=sample({din:0}),offOut=sample({dout:0}),bothOff=sample({din:0,dout:0});
 if(!approx(offIn.nonlinear_cross_mass,0)||!approx(offOut.nonlinear_cross_mass,0)||
    !approx(offIn.after_m,1+offIn.dout)||!approx(offOut.after_m,1+offOut.din)||
    !approx(bothOff.after_m,1))throw Error("zero stream controls");
 const s=sample(),x=sample({din:s.dout,dout:s.din});
 if(!approx(s.after_m,x.after_m)||!approx(s.nonlinear_cross_mass,x.nonlinear_cross_mass))throw Error("shell exchange");
 // Exact DTR double-difference algebra for independent shell energies:
 const a=sample({din:1e-4,dout:2e-4}),b=sample({din:1e-4,dout:0}),
 c=sample({din:0,dout:2e-4}),d=sample({din:0,dout:0});
 if(!approx(a.after_m-b.after_m-c.after_m+d.after_m,a.nonlinear_cross_mass))
  throw Error("two-stream bilinear term");
 // Radius approaching inner horizon: interaction scales like 1/delta.
 const near=sample({delta:1e-7}),near2=sample({delta:1e-8});
 if(Math.abs(near2.nonlinear_cross_mass/near.nonlinear_cross_mass-10)>.00002)
  throw Error("near-horizon inverse-gap scaling");
 // Charge approaching 0 is a different Schwarzschild geometry: forbid
 let denied=false;try{sample({q:0})}catch{denied=true}if(!denied)throw Error("q=0 guard");
 return {pass:true,charged_RN_not_Kerr:true,geometric_units:"G=c=Mbase=1",
  test_charges:checks,zero_incoming:"PASS",zero_outgoing:"PASS",
  both_zero:"PASS",stream_swap:"PASS",DTR_product_constraint:"PASS",
  bilinear_two_stream_interaction:"PASS",inverse_gap_asymptotic:"PASS",
  Schwarzschild_no_inner_horizon_guard:"PASS",
  no_observed_mass_or_evolved_metric:true};
}
const api=Object.freeze({CHARGES,DEFAULT,COUNT,DELTA_MIN,DELTA_MAX,RG_SGRA_M,
 parameters,horizons,sample,logScan,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.Bound17DTR=api;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
