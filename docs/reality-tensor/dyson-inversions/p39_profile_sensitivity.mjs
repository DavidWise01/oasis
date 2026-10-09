// ROOT0 P3.9 — impedance sensitivity, independent of the P3.8 implementation
// Run: node p39_profile_sensitivity.mjs
import assert from 'node:assert/strict';
const fns={linear:u=>1+u,quadratic:u=>1+u*u,exponential:u=>Math.exp(u),plateau:u=>1+u/(1+u)};
const power=z=>z[0]**2+z[1]**2, norm=s=>s.reduce((t,z)=>t+power(z),0);
function transform(s,j,eta,inv=false){let v=s.map(z=>z.slice()),a=v[0],b=v[j+1],t=Math.sqrt(1-eta),r=Math.sqrt(eta)*(inv?-1:1);v[0]=[t*a[0]-r*b[1],t*a[1]+r*b[0]];v[j+1]=[t*b[0]-r*a[1],t*b[1]+r*a[0]];return v;}
export function checkProfile(f,N=10,depth=1){
 if(typeof f!=='function'||!Number.isInteger(N)||N<1||N>10||!Number.isFinite(depth)||depth<0||depth>1)throw new RangeError('profile geometry');
 let state=[[1,0],...Array.from({length:N},()=>[0,0])],etas=[],travel=1,captured=[];
 for(let j=0;j<N;j++){const za=f(depth*j/N),zb=f(depth*(j+1)/N);if(!(za>0&&zb>0))throw new RangeError('positive impedance required');
 const eta=((zb-za)/(zb+za))**2;etas.push(eta);captured.push(travel*eta);travel*=1-eta;state=transform(state,j,eta);}
 const nerr=Math.abs(norm(state)-1),aerr=Math.abs(travel+captured.reduce((a,b)=>a+b,0)-1);
 for(let j=N-1;j>=0;j--)state=transform(state,j,etas[j],true);
 const recoveryError=Math.max(...state.flatMap((z,i)=>z.map((v,k)=>Math.abs(v-(i===0&&k===0?1:0)))));
 assert.ok(nerr<1e-12&&aerr<1e-12&&recoveryError<1e-12);
 return {N,depth,etaFirst:etas[0],etaLast:etas.at(-1),travel,capture:1-travel,nerr,aerr,recoveryError};
}
if(process.argv[1]&&import.meta.url===new URL('file://'+process.argv[1]).href){
 const report={profiles:{},randomized:12000,maxRecovery:0,maxNorm:0};
 for(const [name,f] of Object.entries(fns)){report.profiles[name]=[1,0.5,0].map(depth=>checkProfile(f,10,depth));}
 let seed=0x3900ff;const rnd=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return(seed>>>0)/4294967296;};
 for(let i=0;i<12000;i++){const N=1+Math.floor(rnd()*10),d=rnd(),k=rnd(),v=checkProfile(u=>1+(1-k)*u+k*u*u,N,d);report.maxRecovery=Math.max(report.maxRecovery,v.recoveryError);report.maxNorm=Math.max(report.maxNorm,v.nerr);}
 const b=report.profiles.linear[0];assert.ok(Math.abs(b.etaFirst-0.0022675736961451282)<1e-15&&Math.abs(b.travel-0.9875867722265661)<1e-12);
 console.log(JSON.stringify({status:'PASS',...report},null,2));
}
