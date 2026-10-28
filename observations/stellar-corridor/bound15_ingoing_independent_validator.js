/* Bound15 independent ingoing-Kerr numerical verification.
   Numerical derivatives of ingoing metric, independent full connection
   and Riemann projection, local tetrad parallel transport at, before, and
   after future outer horizon. Not an independent astrophysical observation.
*/
(function(root){"use strict";
const F=root.Bound15IngoingKerr,K=root.Bound14KerrFall;
if(!F||!K)throw Error("Load Bound14 and Bound15 cores first");
const I=()=>[0,1,2,3];
const z2=()=>I().map(()=>[0,0,0,0]),z3=()=>I().map(()=>z2()),z4=()=>I().map(()=>z3());
function gamma(y,theta,chi,h=8e-6){
 const g=F.metric(y,theta,chi),inv=F.inverseMetric(y,theta,chi),der=z3();
 for(const ax of [1,2]){
  const gp=ax===1?F.metric(y+h,theta,chi):F.metric(y,theta+h,chi);
  const gm=ax===1?F.metric(y-h,theta,chi):F.metric(y,theta-h,chi);
  for(const i of I())for(const j of I())der[ax][i][j]=(gp[i][j]-gm[i][j])/(2*h);
 }
 const G=z3();
 for(const a of I())for(const b of I())for(const c of I())for(const d of I())
  G[a][b][c]+=inv[a][d]*(der[b][d][c]+der[c][d][b]-der[d][b][c])/2;
 return G;
}
function riemann(y,theta,chi,step=7e-5){
 const G=gamma(y,theta,chi),dG=I().map(()=>z3());
 for(const ax of [1,2]){
  const gp=ax===1?gamma(y+step,theta,chi):gamma(y,theta+step,chi),
        gm=ax===1?gamma(y-step,theta,chi):gamma(y,theta-step,chi);
  for(const a of I())for(const b of I())for(const c of I())
   dG[ax][a][b][c]=(gp[a][b][c]-gm[a][b][c])/(2*step);
 }
 const R=z4();
 for(const a of I())for(const b of I())for(const c of I())for(const d of I()){
  let v=dG[c][a][d][b]-dG[d][a][c][b];
  for(const e of I())v+=G[a][c][e]*G[e][d][b]-G[a][d][e]*G[e][c][b];
  R[a][b][c][d]=v;
 }
 return R;
}
function project(y,chi){
 const t=Math.PI/2,g=F.metric(y,t,chi),e=F.frame(y,chi).PP_basis_ing,
       R=riemann(y,t,chi),lambda=I().slice(0,3).map(()=>[0,0,0]);
 const lower=e.slice(1).map(v=>I().map(i=>I().reduce((s,j)=>s+g[i][j]*v[j],0)));
 for(let i=0;i<3;i++)for(let j=0;j<3;j++){
  let s=0;
  for(const a of I())for(const b of I())for(const c of I())for(const d of I())
   s-=lower[i][a]*R[a][b][c][d]*e[0][b]*e[j+1][c]*e[0][d];
  lambda[i][j]=s*K.C*K.C/(K.RG*K.RG);
 }
 return {projected:lambda,analytic:K.projectedTidal(y,chi)};
}
function parallelResidual(y,chi,h=8e-6){
 const e=F.frame(y,chi).PP_basis_ing,
       gp=F.frame(y+h,chi).PP_basis_ing,
       gm=F.frame(y-h,chi).PP_basis_ing,
       G=gamma(y,Math.PI/2,chi),res=[];
 for(let i=1;i<=3;i++){
  const val=[];
  for(const a of I()){
   let q=e[0][1]*(gp[i][a]-gm[i][a])/(2*h);
   for(const b of I())for(const c of I())q+=G[a][b][c]*e[0][b]*e[i][c];
   val.push(q);
  }
  res.push(val);
 }
 return res;
}
function selfTest(){
 let n=0,maxDiag=0,maxOffDiag=0,maxTransport=0,details=[];
 for(const chi of [0,.5,.9,.99]){
  const l=F.limits(chi);
  for(const y of [l.y_outer+.5,l.y_outer,(l.y_outer+l.y_stop)/2,Math.max(l.y_stop,.3)]){
   const p=project(y,chi),expected=[p.analytic.stretch_s2,
      p.analytic.polar_compress_s2,p.analytic.azimuth_compress_s2],base=p.analytic.k;
   let maxDiagAt=0,maxOffAt=0;
   for(let i=0;i<3;i++)for(let j=0;j<3;j++){
    const e=i===j?expected[i]:0,dev=Math.abs(p.projected[i][j]-e)/base;
    if(i===j){maxDiag=Math.max(maxDiag,dev);maxDiagAt=Math.max(maxDiagAt,dev)}
    else{maxOffDiag=Math.max(maxOffDiag,dev);maxOffAt=Math.max(maxOffAt,dev)}
   }
   let mr=0;
   for(const v of parallelResidual(y,chi).flat()){
    mr=Math.max(mr,Math.abs(v));maxTransport=Math.max(maxTransport,Math.abs(v))
   }
   details.push({chi,y,position:y>l.y_outer?"EXTERIOR":y===l.y_outer?"OUTER_HORIZON":"CLASSICAL_INTERIOR",
     diagonal_error: maxDiagAt,off_diagonal_error:maxOffAt,transport_error:mr});
   n++;
   if(maxDiagAt>0.002||maxOffAt>0.002||mr>1e-5)
    throw Error("Boundary validation failed "+JSON.stringify(details.at(-1)));
  }
 }
 return {pass:true,cases:n,details,
  maximum_relative_diagonal_curvature_error:maxDiag,
  maximum_relative_off_diagonal_curvature_error:maxOffDiag,
  max_absolute_parallel_transport_residual:maxTransport,
  metric_to_connection_to_full_Riemann:"independent of closed form analytic tidal eigenvalue",
  crossing_horizon_without_BL_inverse_Delta:true};
}
const api=Object.freeze({gamma,riemann,project,parallelResidual,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.Bound15IndependentValidator=api;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
