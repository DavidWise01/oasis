/* OASIS Bound 14 independent numerical curvature/tetrad witness.
 * No use of analytical projectedTidal() in the actual curvature calculation.
 * Constructs full Kerr Boyer-Lindquist Christoffels from finite metric
 * derivatives; forms the Riemann tensor; projects R_{i0j0} to independently
 * verify the three eigenvalues of the explicitly parallel-transported frame.
 * All validation events strictly OUTSIDE outer horizon (BL valid domain).
 * Finite-difference errors at 1e-5 relative do not imply a quantum result.
 */
(function(root){"use strict";
const K=root.Bound14KerrFall;
if(!K)throw Error("Load bound14_kerr_fall_tetrad_core.js first");
const range=n=>Array.from({length:n},(_,i)=>i);
const zeros2=()=>range(4).map(()=>[0,0,0,0]);
const zeros3=()=>range(4).map(()=>zeros2());
const zeros4=()=>range(4).map(()=>zeros3());
const metric=(y,theta,chi)=>K.metricBL(y,theta,chi);
function invert(g){
 // Kerr Boyer-Lindquist metric has the (t,phi) block + diagonal r,theta.
 const d=g[0][0]*g[3][3]-g[0][3]*g[0][3];
 const a=zeros2();
 a[0][0]=g[3][3]/d;a[3][3]=g[0][0]/d;
 a[0][3]=a[3][0]=-g[0][3]/d;
 a[1][1]=1/g[1][1];a[2][2]=1/g[2][2];return a;
}
function gamma(y,theta,chi,metricStep=2e-5){
 const G=metric(y,theta,chi),Gi=invert(G),deriv=zeros3();
 for(const [axis,value] of [[1,y],[2,theta]]){
  const plus=axis===1?metric(value+metricStep,theta,chi):metric(y,value+metricStep,chi),
        minus=axis===1?metric(value-metricStep,theta,chi):metric(y,value-metricStep,chi);
  for(let j=0;j<4;j++)for(let k=0;k<4;k++)
   deriv[axis][j][k]=(plus[j][k]-minus[j][k])/(2*metricStep);
 }
 const Gam=zeros3();
 for(let a=0;a<4;a++)for(let b=0;b<4;b++)for(let c=0;c<4;c++)
  for(let d=0;d<4;d++)
   Gam[a][b][c]+=Gi[a][d]*(deriv[b][d][c]+deriv[c][d][b]-deriv[d][b][c])/2;
 return Gam;
}
function curvature(y,theta,chi,step=2e-4){
 const G=gamma(y,theta,chi);
 const derivatives=range(4).map(()=>zeros3());
 for(const d of [1,2]){
  const plus=d===1?gamma(y+step,theta,chi):gamma(y,theta+step,chi),
        minus=d===1?gamma(y-step,theta,chi):gamma(y,theta-step,chi);
  for(let a=0;a<4;a++)for(let b=0;b<4;b++)for(let c=0;c<4;c++)
   derivatives[d][a][b][c]=(plus[a][b][c]-minus[a][b][c])/(2*step);
 }
 const R=zeros4(); // R^a_(b c d) = d_c Gamma^a_(d b) - d_d ...
 for(let a=0;a<4;a++)for(let b=0;b<4;b++)for(let c=0;c<4;c++)for(let d=0;d<4;d++){
   let v=derivatives[c][a][d][b]-derivatives[d][a][c][b];
   for(let x=0;x<4;x++)v+=G[a][c][x]*G[x][d][b]-G[a][d][x]*G[x][c][b];
   R[a][b][c][d]=v;
 }
 return R;
}
function fourVectorLower(g,v){return range(4).map(i=>range(4).reduce((a,j)=>a+g[i][j]*v[j],0));}
function project(chi,y){
 const th=Math.PI/2,t=K.carterTetrad(y,chi),e=t.BL,G=metric(y,th,chi),
       R=curvature(y,th,chi),tid=range(3).map(()=>[0,0,0]);
 const l=range(3).map(i=>fourVectorLower(G,e[i+1]));
 for(let i=0;i<3;i++)for(let j=0;j<3;j++){
  let val=0;
  for(let a=0;a<4;a++)for(let b=0;b<4;b++)for(let c=0;c<4;c++)for(let d=0;d<4;d++)
   val-=l[i][a]*R[a][b][c][d]*e[0][b]*e[j+1][c]*e[0][d];
  tid[i][j]=val*K.C*K.C/(K.RG*K.RG); // geometric 1/rg² -> s^-2
 }
 return {tidal:tid,analytic:K.projectedTidal(y,chi)};
}
function transport(chi,y,h=1e-5){
 const th=Math.PI/2,e=K.carterTetrad(y,chi).BL,gm=gamma(y,th,chi),
       plus=K.carterTetrad(y+h,chi).BL,
       minus=K.carterTetrad(y-h,chi).BL;
 return range(3).map(i=>{
  const vec=e[i+1],derivative=range(4).map(a=>(plus[i+1][a]-minus[i+1][a])/(2*h));
  return range(4).map(a=>{
   let val=e[0][1]*derivative[a];
   for(let b=0;b<4;b++)for(let c=0;c<4;c++)val+=gm[a][b][c]*e[0][b]*vec[c];
   return val;
  });
 });
}
function selfTest(){
 let worstTidal=0,worstOffDiagonal=0,worstTransport=0,cases=0;
 for(const chi of [0,.5,.9]){
  for(const y of [5,10,30]){
   let e=project(chi,y),expect=[
     e.analytic.stretch_s2,e.analytic.polar_compress_s2,e.analytic.azimuth_compress_s2];
   for(let i=0;i<3;i++)for(let j=0;j<3;j++){
    const got=e.tidal[i][j],want=i===j?expect[i]:0;
    const scale=Math.max(1e-25,Math.abs(e.analytic.k));
    const delta=Math.abs(got-want)/scale;
    if(i===j)worstTidal=Math.max(worstTidal,delta);
    else worstOffDiagonal=Math.max(worstOffDiagonal,delta);
    if(delta>0.00008)throw Error("Full Riemann disagrees chi="+chi+" y="+y+" i="+i+" j="+j+" delta="+delta);
   }
   const trs=transport(chi,y);
   for(const a of trs.flat())worstTransport=Math.max(worstTransport,Math.abs(a));
   if(worstTransport>1e-7)throw Error("Tetrad is not parallel propagated");
   cases++;
  }
 }
 return {pass:true,samples:cases,max_normalized_tidal_residual:worstTidal,
         max_normalized_tidal_offdiagonal:worstOffDiagonal,
         max_parallel_transport_residual:worstTransport,
         independent_of_closed_form_curvature:"YES, Christoffels and Riemann generated from numerical BL metric derivatives",
         exterior_only:"YES",kerr_observer:"E=1,Lz=0,Q=0"};
}
const api=Object.freeze({invert,gamma,curvature,project,transport,selfTest});
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.Bound14IndependentKerrValidator=api;
})(typeof globalThis!=="undefined"?globalThis:typeof self!=="undefined"?self:this);
