/* OASIS NATURAL BOUND 20 | 2026-10-28
 * SINGLE CONTIGUOUS RECTANGULAR DOUBLE-NULL CHARACTERISTIC INITIAL-VALUE
 * problem for spherical Einstein-Maxwell-neutral-real-scalar, NOT KERR.
 * G=c=M0=1, charge Q=0.8. Coordinates u∈[0,Lu],v∈[0,Lv],
 * with Lv much longer than earlier Bound18 0.4.
 *
 * Important: v is chosen characteristic gauge, NOT an externally
 * established Bondi/advanced time from infinity. The input scalar_v tail
 * B (1+v/v0)^(-p) is ASSUMED, not derived from asymptotic scattering.
 * It approaches the background CH only as an ideal reference; a strict
 * distance guard and numerical convergence gates prevent claimed passage.
 *
 * Metric ds²=-exp(2sigma)du dv+r²dΩ²,
 * E-M-scalar PDE exactly same frozen Bound18 equations, but rectangular
 * cell Δu*Δv and independent constraint-enforcing null boundary data.
 * u=0 arm: φ_v=B(1+v/v0)^(-p), v≥0.
 * v=0 arm: φ(u,0)=A sin²(pi u/Lu), 0≤u≤Lu.
 * Corner φ(0,0)=0. On both arms dr/ds=F(r)/2 and
 * σ=(1/2)ln[-F(r)]+∫ r φ_s²/F ds [boundary constraint].
 * The u arm and v arm are derived from the SAME corner data;
 * no separate r0 snapshots are linked to fake a trajectory.
 */
(function(root){"use strict";
const PI=Math.PI;
const DEFAULT=Object.freeze({Q:.8,r0:1.2,Lu:.2,Lv:8,A:.012,B:.0005,v0:1,p:3,
  guardGapFraction:.0005,maxTailTime:50});
const R_MINUS=.4,R_PLUS=1.6;
const REFINEMENTS=Object.freeze([[12,48],[24,96],[48,192],[96,384]]);
function validate(p={}){
 const x={...DEFAULT,...p};
 if(!(x.Q===.8&&x.r0>R_MINUS&&x.r0<R_PLUS))throw Error("this witness fixes Q=.8 and trapped r0");
 if(!(x.Lu>0&&x.Lu<=.4&&x.Lv>.4&&x.Lv<=x.maxTailTime))throw Error("null rectangle domain");
 if(!(x.A>=0&&x.A<=.05&&x.B>=0&&x.B<=.05))throw Error("scalar amplitudes");
 if(!(x.v0>0&&x.p>1&&x.p<=12))throw Error("tail v0>0, 1<p<=12");
 if(!(x.guardGapFraction>0&&x.guardGapFraction<=.1))throw Error("positive chosen pre-inner guard");
 return x;
}
function F(r,Q){return 1-2/r+Q*Q/(r*r)}
function advanceRadius(r,h,Q){
 const v=x=>F(x,Q)/2,k1=v(r),k2=v(r+h*k1/2),k3=v(r+h*k2/2),k4=v(r+h*k3);
 return r+h*(k1+2*k2+2*k3+k4)/6;
}
function phiU(s,p){return p.A*Math.sin(PI*s/p.Lu)**2}
function dPhiU(s,p){return p.A*PI/p.Lu*Math.sin(2*PI*s/p.Lu)}
function dPhiV(s,p){return p.B*Math.pow(1+s/p.v0,-p.p)}
function phiV(s,p){return -p.B*p.v0*Math.expm1((1-p.p)*Math.log1p(s/p.v0))/(p.p-1)}
function initArm(N,length,Q,r0,p,which){
 const h=length/N,R=new Float64Array(N+1),
  S=new Float64Array(N+1),P=new Float64Array(N+1);
 const phi=which==="u"?phiU:phiV,dp=which==="u"?dPhiU:dPhiV;
 R[0]=r0;S[0]=Math.log(-F(r0,Q))/2;P[0]=0;
 for(let i=0;i<N;i++){
  const t=i*h,rm=advanceRadius(R[i],h/2,Q),r1=advanceRadius(R[i],h,Q);
  if(!(r1>R_MINUS&&F(r1,Q)<0))throw Error("BOUNDARY_RADIUS_OUT_OF_TRAPPED_DOMAIN");
  const c=(r,s)=>r*dp(s,p)**2/F(r,Q),
    source=h*(c(R[i],t)+4*c(rm,t+h/2)+c(r1,t+h))/6;
  S[i+1]=S[i]+(Math.log(-F(r1,Q))-Math.log(-F(R[i],Q)))/2+source;
  R[i+1]=r1;P[i+1]=phi(t+h,p);
 }
 return {R,S,P};
}
function rhs(r,s,ru,rv,pu,pv,Q){
 const Omega2=Math.exp(2*s),r2=r*r;
 return [
  -ru*rv/r-Omega2*(1-Q*Q/r2)/(4*r),
  ru*rv/r2+Omega2*(1-2*Q*Q/r2)/(4*r2)-pu*pv,
  -(ru*pv+rv*pu)/r
 ];
}
function mass(r,s,ru,rv,Q){
 return r/2*(1+4*ru*rv*Math.exp(-2*s)+Q*Q/(r*r));
}
function compute(Nu,Nv,par={},internal=false){
 if(!Number.isInteger(Nu)||Nu<8||Nu>256||!Number.isInteger(Nv)||Nv<16||Nv>1024)throw Error("grid domain");
 const p=validate(par),du=p.Lu/Nu,dv=p.Lv/Nv,guard=R_MINUS+(R_PLUS-R_MINUS)*p.guardGapFraction;
 const u=initArm(Nu,p.Lu,p.Q,p.r0,p,"u"),v=initArm(Nv,p.Lv,p.Q,p.r0,p,"v");
 if(!(v.R[Nv]>guard&&u.R[Nu]>guard))throw Error("ABORT_INITIAL_CHARACTERISTIC_GUARD");
 const R=Array.from({length:Nu+1},()=>new Float64Array(Nv+1)),
  S=Array.from({length:Nu+1},()=>new Float64Array(Nv+1)),
  P=Array.from({length:Nu+1},()=>new Float64Array(Nv+1));
 for(let i=0;i<=Nu;i++){R[i][0]=u.R[i];S[i][0]=u.S[i];P[i][0]=u.P[i]}
 for(let j=0;j<=Nv;j++){R[0][j]=v.R[j];S[0][j]=v.S[j];P[0][j]=v.P[j]}
 let maxFixed=0,minR=Infinity,firstGuardCell=null,computed=0;
 for(let i=0;i<Nu;i++)for(let j=0;j<Nv;j++){
  const r0=R[i][j],r1=R[i+1][j],r2=R[i][j+1],
    s0=S[i][j],s1=S[i+1][j],s2=S[i][j+1],
    p0=P[i][j],p1=P[i+1][j],p2=P[i][j+1];
  let rn=r1+r2-r0,sn=s1+s2-s0,pn=p1+p2-p0;
  let err=0;
  for(let k=0;k<9;k++){
   const midR=(r0+r1+r2+rn)/4,midS=(s0+s1+s2+sn)/4;
   const ru=(r1-r0+rn-r2)/(2*du),rv=(r2-r0+rn-r1)/(2*dv),
    pu=(p1-p0+pn-p2)/(2*du),pv=(p2-p0+pn-p1)/(2*dv);
   const [fr,fs,fp]=rhs(midR,midS,ru,rv,pu,pv,p.Q),
      tr=r1+r2-r0+du*dv*fr,ts=s1+s2-s0+du*dv*fs,tp=p1+p2-p0+du*dv*fp;
   err=Math.max(Math.abs(rn-tr),Math.abs(sn-ts),Math.abs(pn-tp));
   rn=tr;sn=ts;pn=tp;
  }
  if(!Number.isFinite(rn+sn+pn)||!(rn>R_MINUS+1e-8)){
   throw Error("ABORT_EVOLUTION_DOMAIN cell="+i+","+j+" radius="+rn);
  }
  R[i+1][j+1]=rn;S[i+1][j+1]=sn;P[i+1][j+1]=pn;computed++;
  minR=Math.min(minR,rn);maxFixed=Math.max(maxFixed,err);
  if(rn<=guard){firstGuardCell={i:i+1,j:j+1,r:rn,u:(i+1)*du,v:(j+1)*dv};break}
 }
 if(firstGuardCell)throw Error("ABORT_PRE_INNER_GUARD "+JSON.stringify(firstGuardCell));
 const point=(i,j)=>{
  if(i<1||j<1||i>=Nu||j>=Nv)throw Error("interior indices");
  const r=R[i][j],s=S[i][j],ph=P[i][j],
   ru=(R[i+1][j]-R[i-1][j])/(2*du),rv=(R[i][j+1]-R[i][j-1])/(2*dv),
   su=(S[i+1][j]-S[i-1][j])/(2*du),sv=(S[i][j+1]-S[i][j-1])/(2*dv),
   pu=(P[i+1][j]-P[i-1][j])/(2*du),pv=(P[i][j+1]-P[i][j-1])/(2*dv);
  const cu=(R[i+1][j]-2*r+R[i-1][j])/(du*du)-2*su*ru+r*pu*pu,
    cv=(R[i][j+1]-2*r+R[i][j-1])/(dv*dv)-2*sv*rv+r*pv*pv;
  const massNow=mass(r,s,ru,rv,p.Q);
  return {i,j,u:i*du,v:j*dv,r,s,phi:ph,ru,rv,pu,pv,
   mass:massNow,Cuu:cu,Cvv:cv,fluxU:pu*pu,fluxV:pv*pv,
   trapped:ru<0&&rv<0};
 };
 const massGrid=(i,j)=>point(i,j).mass;
 const flux=(i,j)=>{
  const z=point(i,j),mu=(massGrid(i+1,j)-massGrid(i-1,j))/(2*du),
   mv=(massGrid(i,j+1)-massGrid(i,j-1))/(2*dv);
  const fromU=-2*z.r*z.r*Math.exp(-2*z.s)*z.rv*z.pu*z.pu,
    fromV=-2*z.r*z.r*Math.exp(-2*z.s)*z.ru*z.pv*z.pv;
  return {m_u_numeric:mu,m_u_pred:fromU,m_u_res:mu-fromU,
   m_v_numeric:mv,m_v_pred:fromV,m_v_res:mv-fromV};
 };
 let suu=0,svv=0,wu=0,wv=0,count=0,maxmass=-Infinity,smallest=Infinity;
 for(let i=1;i<Nu;i++)for(let j=1;j<Nv;j++){
  const z=point(i,j);
  suu+=z.Cuu*z.Cuu;svv+=z.Cvv*z.Cvv;
  wu=Math.max(wu,Math.abs(z.Cuu));wv=Math.max(wv,Math.abs(z.Cvv));
  maxmass=Math.max(maxmass,z.mass);smallest=Math.min(smallest,z.r);count++;
 }
 const center=point(Nu/2,Nv/2),tail=point(Nu/2,Nv-2),middleFlux=flux(Nu/2,Nv/2);
 const result={Nu,Nv,du,dv,parameters:p,center,tail,
  center_mass_flux:middleFlux,
  constraints:{CuRMS:Math.sqrt(suu/count),CvRMS:Math.sqrt(svv/count),
   CuMax:wu,CvMax:wv,sampled:count},
  last_v_boundary_radius:v.R[Nv],
  minimum_interior_radius:smallest,minimum_evolved_radius:minR,
  corner_radius:R[Nu][Nv],max_interior_mass:maxmass,maximum_cell_iteration_error:maxFixed,
  chosen_guard_radius:guard,completed_cells:computed,
  physical_status:"ONE_FINITE_COUPLED_RECTANGLE_BEFORE_GUARD",
  claim_mass_inflation:false,claim_observed_Price_tail:false,
  is_Kerr:false,local_AMR_implemented:false};
 if(internal)result.grid={R,S,P,point,flux};
 return result;
}
function convergence(p={},sizes=REFINEMENTS){
 const out=sizes.map(([Nu,Nv])=>compute(Nu,Nv,p));
 const diff=(a,b)=>Math.abs(a.center.mass-b.center.mass)+Math.abs(a.center.r-b.center.r)+
  Math.abs(a.center.phi-b.center.phi)+Math.abs(a.center.s-b.center.s);
 const d=out.map((v,i)=>i===0?null:diff(out[i-1],v)).slice(1);
 const ratios=[d[0]/d[1],d[1]/d[2]];
 const cu=out.map(x=>x.constraints.CuRMS),cv=out.map(x=>x.constraints.CvRMS);
 const flU=out.map(x=>Math.abs(x.center_mass_flux.m_u_res)),
  flV=out.map(x=>Math.abs(x.center_mass_flux.m_v_res));
 const factor=a=>a.slice(0,-1).map((x,i)=>x/a[i+1]);
 return {run:out,solution_ratios:ratios,constraintCu_ratios:factor(cu),
  constraintCv_ratios:factor(cv),
  massFluxU_ratios:factor(flU),massFluxV_ratios:factor(flV),
  pass:ratios.every(x=>x>2.7&&x<5.4)&&factor(cu).at(-1)>2.7&&
     factor(cv).at(-1)>2.7&&factor(flU).at(-1)>2.7&&
     factor(flV).at(-1)>2.7,
  not_infinite_time:true};
}
function selfTest(){
 const p=validate(),both=convergence(p),vacuum=convergence({A:0,B:0});
 if(!both.pass||!vacuum.pass)throw Error("rectangular second-order convergence missing");
 if(Math.abs(vacuum.run.at(-1).center.mass-1)>2e-5)throw Error("RN vacuum");
 if(!(both.run.at(-1).center.mass>vacuum.run.at(-1).center.mass))throw Error("scalar mass effect");
 if(!(both.run.at(-1).tail.v>3)&&!(both.run.at(-1).tail.v>p.Lv*.95))
  throw Error("tail witness");
 for(let i=0;i<7;i++){
  const v=p.Lv*i/6,a=dPhiV(v,p),b=dPhiV(v+1,p);
  if(!(a>=b))throw Error("decaying incoming boundary tail");
 }
 const x=compute(24,96,{A:0,B:0});
 if(!(x.corner_radius>R_MINUS&&x.maximum_cell_iteration_error<1e-7))throw Error("domain guard");
 const verdicts={};
 for(const L of [8,12,16,20,30,40]){
  try{const z=compute(24,Math.round(12*L),{Lv:L});verdicts[L]={status:"COMPUTED",corner_r:z.corner_radius,guard:z.chosen_guard_radius,
    mass:z.center.mass,Cu:z.constraints.CuRMS,Cv:z.constraints.CvRMS}}
  catch(e){verdicts[L]={status:"ABORT",reason:String(e).slice(0,200)}}
 }
 return {pass:true,spacetime:"single finite rectangular RN+scalar double-null initial problem",
  inputs:p,
  long_incoming_tail_is_prescribed_not_exterior_solved:true,
  both:{finest:{N:both.run.at(-1).Nu,Nv:both.run.at(-1).Nv,mass:both.run.at(-1).center.mass,
   corner:both.run.at(-1).corner_radius,Cu:both.run.at(-1).constraints.CuRMS,
   Cv:both.run.at(-1).constraints.CvRMS},
   solution_ratios:both.solution_ratios,Cu_ratios:both.constraintCu_ratios,Cv_ratios:both.constraintCv_ratios,
   fluxU_ratios:both.massFluxU_ratios,fluxV_ratios:both.massFluxV_ratios},
  vacuum:{mass:vacuum.run.at(-1).center.mass,
   solution_ratios:vacuum.solution_ratios},
  finite_domain_length_scan:verdicts,
  local_AMR:false,real_mass_inflation_not_demonstrated:true};
}
const api=Object.freeze({DEFAULT,R_MINUS,R_PLUS,REFINEMENTS,
 validate,F,phiU,dPhiU,phiV,dPhiV,initArm,rhs,mass,compute,convergence,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.Bound20LateTail=api;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
