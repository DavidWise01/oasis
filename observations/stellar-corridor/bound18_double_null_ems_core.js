/* OASIS Bound 18 | Spherical Einstein-Maxwell-neutral-massless-scalar
   fully coupled characteristic Cauchy boundary evolution (u,v) grid.
   Equations in G=c=1, fixed electric charge Q, metric
    ds² = -exp(2sigma) du dv + r² dOmega², g_uv=-exp(2sigma)/2.
    r_uv = -ru*rv/r -exp(2sigma)/(4r)*(1-Q²/r²)
    sigma_uv = ru*rv/r² + exp(2sigma)/(4r²)*(1-2Q²/r²)-phi_u*phi_v
    phi_uv = -(ru*phi_v+rv*phi_u)/r
   Null constraints (not enforced in interior, MONITORED):
    C_uu=r_uu-2 sigma_u*r_u+r*phi_u²=0;
    C_vv=r_vv-2 sigma_v*r_v+r*phi_v²=0.
   Charge mass function M=r/2*[1+4ru rv/exp(2sigma)+Q²/r²].
   Initial intersecting null rays are exact RN trapped-region boundaries:
    r(0,0)=1.2, Q=.8, M0=1, r_u(0)=r_v(0)=F(r)/2<0,
    Omega²=-F(r)>0, F(r)=1-2/r+Q²/r².
   Along each boundary choose phi(s)=A sin²(pi*s/L).
   Solve constraint exactly in continuum by prescribed r'=F/2 and
    sigma(s)=0.5 ln[-F(r(s))]+integral(r*phi_s²/F(r)) ds,
   using RK4 radius and Simpson quadrature each edge cell.
   2nd order double-null diamond scheme; implicit midpoint (8 iterations).
   Finite-difference interior constraints are *independent* diagnostics.
   This IS coupled Einstein+neutral scalar evolution (within stated domain).
   It is NOT rotating Kerr and it is NOT a late-time mass-inflation solution.
   No calibrated observed scalar radiation, charge, or astrophysical spin.
*/
(function(root){"use strict";
const PARAMS=Object.freeze({Q:.8,M0:1,r0:1.2,L:.4,A:.02,B:.015});
const G_C_UNITS="G=c=M0=1", PI=Math.PI;
function num(x,name){if(!Number.isFinite(x))throw Error(name+" nonfinite");return x;}
function config(p={}){
 const z={...PARAMS,...p};
 if(!(z.Q>0&&z.Q<1&&z.M0===1))throw Error("0<Q<1, M0 fixed to 1");
 if(!(z.r0>1-Math.sqrt(1-z.Q*z.Q)&&z.r0<1+Math.sqrt(1-z.Q*z.Q)))throw Error("r0 inside RN trapped region");
 if(!(z.L>0&&z.L<1))throw Error("0<L<1");
 for(const s of ["A","B"])if(!(z[s]>=0&&z[s]<=.1))throw Error("pulse amplitude in [0,.1]");
 return z;
}
function F(r,Q){return 1-2/r+Q*Q/(r*r)}
function Fp(r,Q){return 2/(r*r)-2*Q*Q/(r*r*r)}
function pulse(s,A,L){return A*Math.sin(PI*s/L)**2}
function pulsePrime(s,A,L){return A*PI/L*Math.sin(2*PI*s/L)}
function radiusRK4(r,h,Q){
 const rhs=x=>F(x,Q)/2;
 const a=rhs(r),b=rhs(r+h*a/2),c=rhs(r+h*b/2),d=rhs(r+h*c);
 return r+h*(a+2*b+2*c+d)/6;
}
function boundary(n,A,p){
 const h=p.L/n,rr=new Float64Array(n+1),ss=new Float64Array(n+1),
  phi=new Float64Array(n+1);
 rr[0]=p.r0;ss[0]=Math.log(-F(p.r0,p.Q))/2;
 for(let i=0;i<n;i++){
  const u=i*h,r=rr[i],rm=radiusRK4(r,h/2,p.Q),
    re=radiusRK4(r,h,p.Q),fun=(x,t)=>x*pulsePrime(t,A,p.L)**2/F(x,p.Q);
  const correction=h*(fun(r,u)+4*fun(rm,u+h/2)+fun(re,u+h))/6;
  rr[i+1]=re;ss[i+1]=Math.log(-F(re,p.Q))/2+(ss[i]-Math.log(-F(r,p.Q))/2)+correction;
 }
 for(let i=0;i<=n;i++)phi[i]=pulse(i*h,A,p.L);
 return{r:rr,sigma:ss,phi};
}
function pde(r,s,phi,ru,rv,phiu,phiv,Q){
 const f=Math.exp(2*s),r2=r*r;
 return[-ru*rv/r-f/(4*r)*(1-Q*Q/r2),
   ru*rv/r2+f/(4*r2)*(1-2*Q*Q/r2)-phiu*phiv,
   -(ru*phiv+rv*phiu)/r];
}
function mass(r,s,ru,rv,Q){return r/2*(1+4*ru*rv/Math.exp(2*s)+Q*Q/(r*r))}
function evolve(N,input={},internal=false){
 if(!Number.isInteger(N)||N<8||N>768||N%2!==0)throw Error("even N in [8,768]");
 const p=config(input),h=p.L/N;
 const u=boundary(N,p.A,p),v=boundary(N,p.B,p);
 const RR=Array.from({length:N+1},()=>new Float64Array(N+1)),
   SS=Array.from({length:N+1},()=>new Float64Array(N+1)),
   PP=Array.from({length:N+1},()=>new Float64Array(N+1));
 for(let i=0;i<=N;i++){RR[i][0]=u.r[i];SS[i][0]=u.sigma[i];PP[i][0]=u.phi[i];
    RR[0][i]=v.r[i];SS[0][i]=v.sigma[i];PP[0][i]=v.phi[i];}
 let fixedPointMax=0;
 for(let i=0;i<N;i++)for(let j=0;j<N;j++){
  const r0=RR[i][j],r1=RR[i+1][j],r2=RR[i][j+1],
  s0=SS[i][j],s1=SS[i+1][j],s2=SS[i][j+1],
  x0=PP[i][j],x1=PP[i+1][j],x2=PP[i][j+1];
  let nr=r1+r2-r0,ns=s1+s2-s0,nx=x1+x2-x0;
  let err=0;
  for(let k=0;k<8;k++){
   const rc=(r0+r1+r2+nr)/4,sc=(s0+s1+s2+ns)/4,
      ru=(r1-r0+nr-r2)/(2*h),rv=(r2-r0+nr-r1)/(2*h),
      xu=(x1-x0+nx-x2)/(2*h),xv=(x2-x0+nx-x1)/(2*h);
   const [fr,fs,fx]=pde(rc,sc,0,ru,rv,xu,xv,p.Q);
   const rt=r1+r2-r0+h*h*fr,st=s1+s2-s0+h*h*fs,xt=x1+x2-x0+h*h*fx;
   err=Math.max(Math.abs(rt-nr),Math.abs(st-ns),Math.abs(xt-nx));
   nr=rt;ns=st;nx=xt;
  }
  if(!Number.isFinite(nr+ns+nx)||nr<=0||nr<=1-Math.sqrt(1-p.Q*p.Q)+1e-6)
   throw Error("evolution reached noncontrolled radius or overflow; reduce domain/pulses");
  fixedPointMax=Math.max(fixedPointMax,err);
  RR[i+1][j+1]=nr;SS[i+1][j+1]=ns;PP[i+1][j+1]=nx;
 }
 function centralDerivs(i,j){
  return {
   ru:(RR[i+1][j]-RR[i-1][j])/(2*h),
   rv:(RR[i][j+1]-RR[i][j-1])/(2*h),
   su:(SS[i+1][j]-SS[i-1][j])/(2*h),
   sv:(SS[i][j+1]-SS[i][j-1])/(2*h),
   pu:(PP[i+1][j]-PP[i-1][j])/(2*h),
   pv:(PP[i][j+1]-PP[i][j-1])/(2*h)
  };
 }
 function point(i,j){
  const d=centralDerivs(i,j),r=RR[i][j],s=SS[i][j],ph=PP[i][j];
  const cu=(RR[i+1][j]-2*r+RR[i-1][j])/(h*h)-2*d.su*d.ru+r*d.pu*d.pu;
  const cv=(RR[i][j+1]-2*r+RR[i][j-1])/(h*h)-2*d.sv*d.rv+r*d.pv*d.pv;
  const m=mass(r,s,d.ru,d.rv,p.Q);
  return{i,j,r,sigma:s,phi:ph,mass:m,r_u:d.ru,r_v:d.rv,
   C_uu:cu,C_vv:cv,scalar_incoming_flux:d.pv*d.pv,
   scalar_outgoing_flux:d.pu*d.pu,
   geometric_charge_term:p.Q*p.Q/r/r,
   trapped:d.ru<0&&d.rv<0};
 }
 const c=point(N/2,N/2),quarter=point(N/4,N/4),
  threequarter=point(3*N/4,3*N/4);
 let worstCu=0,worstCv=0,meanCu=0,meanCv=0,points=0,minimumR=Infinity,maximumMass=-Infinity;
 for(let i=1;i<N;i++)for(let j=1;j<N;j++){
  const P=point(i,j);
  worstCu=Math.max(worstCu,Math.abs(P.C_uu));
  worstCv=Math.max(worstCv,Math.abs(P.C_vv));
  meanCu+=P.C_uu*P.C_uu;meanCv+=P.C_vv*P.C_vv;points++;
  minimumR=Math.min(minimumR,P.r);maximumMass=Math.max(maximumMass,P.mass);
 }
 // At corner u=v=L use 1st-order derivative only as display (not convergence witness).
 const corner_r=RR[N][N],corner_phi=PP[N][N],corner_sigma=SS[N][N];
 const output={N,h,Q:p.Q,initial_A:p.A,initial_B:p.B,
  initial_radius:p.r0,domain_length:p.L,
  center:c,quarter,threequarter,corner_r,corner_phi,corner_sigma,
  constraints:{Cuu_l2:Math.sqrt(meanCu/points),Cvv_l2:Math.sqrt(meanCv/points),
   Cuu_max:worstCu,Cvv_max:worstCv,sampled:points},
  minimum_interior_r:minimumR,maximum_interior_mass:maximumMass,
  fixedPointMax,
  model_kind:"FULLY_COUPLED_SPHERICAL_EM_NEUTRAL_SCALAR_DOUBLE_NULL_DIAMOND",
  not_Kerr:true,mass_inflation_claim:false,
  fluxes_specified_on_both_initial_null_segments:true,
  constraints_interior_monitored_not_manually_forced:true,
  actual_astro_data:false};
 if(internal)output.grid={R:RR,S:SS,P:PP};
 return output;
}
function convergence(caseName,params={A:.02,B:.015},Nlist=[24,48,96,192]){
 const results=Nlist.map(N=>evolve(N,params));
 const difference=(a,b)=>{
  const x=results[a],y=results[b];
  return Math.abs(x.center.mass-y.center.mass)+Math.abs(x.center.r-y.center.r)+
     Math.abs(x.center.phi-y.center.phi)+Math.abs(x.center.sigma-y.center.sigma);
 };
 const d0=difference(0,1),d1=difference(1,2),d2=difference(2,3);
 return{caseName,params,results,
  observed_resolution_ratios:[d0/d1,d1/d2],
  observed_constraint_l2_ratios:{
    Cuu:[results[0].constraints.Cuu_l2/results[1].constraints.Cuu_l2,
         results[1].constraints.Cuu_l2/results[2].constraints.Cuu_l2,
         results[2].constraints.Cuu_l2/results[3].constraints.Cuu_l2],
    Cvv:[results[0].constraints.Cvv_l2/results[1].constraints.Cvv_l2,
         results[1].constraints.Cvv_l2/results[2].constraints.Cvv_l2,
         results[2].constraints.Cvv_l2/results[3].constraints.Cvv_l2]
  }, finest:results.at(-1)};
}
function selfTest(){
 const base=convergence("VACUUM_EXACT_RN",{A:0,B:0}),
      both=convergence("BOTH_SCALAR_STREAMS",{A:.02,B:.015}),
      incoming=convergence("INCOMING_ONLY",{A:0,B:.015}),
      outgoing=convergence("OUTGOING_ONLY",{A:.02,B:0});
 const refs={base,both,incoming,outgoing};
 for(const [name,e] of Object.entries(refs)){
  const l=e.results;
  for(const r of l){
   if(!r.center.trapped||r.minimum_interior_r<=.4)throw Error("trapped RN domain broken: "+name);
   if(!Number.isFinite(r.center.mass+r.constraints.Cuu_l2))throw Error("nonfinite "+name);
  }
  const ratios=e.observed_resolution_ratios;
  if(!(ratios[0]>2.5&&ratios[1]>2.5))throw Error("convergence order not demonstrated "+name+" "+ratios);
  const q=e.observed_constraint_l2_ratios;
  if(!(q.Cuu[2]>2.2&&q.Cvv[2]>2.2))throw Error("constraints not convergent "+name+" "+JSON.stringify(q));
 }
 if(Math.abs(base.finest.center.mass-1)>2e-5)throw Error("vacuum RN mass not recovered");
 const mixed=both.finest.center.mass-incoming.finest.center.mass-outgoing.finest.center.mass+base.finest.center.mass;
 if(!Number.isFinite(mixed))throw Error("two-stream nonlinearity");
 return {pass:true,domain:"RN trapped region r0=1.2, Q=.8; no inner-horizon limit",
  numerically_evolving_Einstein_scalar:true,
  convergence_order:"fourfold second-order expected",
  four_cases:Object.fromEntries(Object.entries(refs).map(([k,v])=>[k,{
    masses:v.results.map(r=>r.center.mass),
    constraint_Cuu_l2:v.results.map(r=>r.constraints.Cuu_l2),
    constraint_Cvv_l2:v.results.map(r=>r.constraints.Cvv_l2),
    observed_refinement_ratios:v.observed_resolution_ratios,
    observed_Cuu_constraint_ratios:v.observed_constraint_l2_ratios.Cuu,
    observed_Cvv_constraint_ratios:v.observed_constraint_l2_ratios.Cvv}])),
  mixed_mass_response_at_center:mixed,
  no_mass_inflation_prediction:true};
}
const api=Object.freeze({PARAMS,G_C_UNITS,config,F,Fp,pulse,pulsePrime,
 radiusRK4,boundary,pde,mass,evolve,convergence,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.Bound18EMS=api;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
