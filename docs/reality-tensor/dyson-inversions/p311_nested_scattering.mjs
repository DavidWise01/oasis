/** ROOT0 P3.11 — two separate d domains, structured unitary map.
 * Exact grammar: {-{d}+{+{d}-}}
 * Signs are labels of traversal boundaries, NOT negative physical energy.
 * Each domain mixes traveling amplitude with its dedicated retained port.
 */
import {CANONICAL,parse,serialize} from './p310_dyson_topology.mjs';
export const VERSION='P3.11';
export const STRUCTURE=CANONICAL;
export const DOMAIN_ORDER=Object.freeze([1,2]);
const finite=x=>typeof x==='number'&&Number.isFinite(x);
export function config(p={}){
 const a={eta1:0.12,eta2:0.08,phase1:0,phase2:0,...p};
 for(const k of ['eta1','eta2'])if(!finite(a[k])||a[k]<0||a[k]>1)throw new RangeError(k);
 for(const k of ['phase1','phase2'])if(!finite(a[k]))throw new RangeError(k);
 return a;
}
const mul=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]];
const phase=t=>[Math.cos(t),Math.sin(t)];
export const norm=s=>s.reduce((n,z)=>n+z[0]**2+z[1]**2,0);
export const initial=()=>[[1,0],[0,0],[0,0]];
const clone=s=>{if(!Array.isArray(s)||s.length!==3||!s.every(z=>Array.isArray(z)&&z.length===2&&z.every(finite)))throw new TypeError('three complex channels');return s.map(z=>z.slice());};
function domain(s,id,eta,theta,inverse=false){
 const v=clone(s),a=v[0],b=v[id],t=Math.sqrt(1-eta),r=Math.sqrt(eta)*(inverse?-1:1);
 if(inverse){
  const x=[t*a[0]+r*b[1],t*a[1]-r*b[0]];
  const y=[t*b[0]+r*a[1],t*b[1]-r*a[0]];
  v[0]=mul(x,phase(-theta));v[id]=y;
 } else{
  const x=mul(a,phase(theta));
  v[0]=[t*x[0]-r*b[1],t*x[1]+r*b[0]];
  v[id]=[t*b[0]-r*x[1],t*b[1]+r*x[0]];
 }
 return v;
}
export function forward(state=initial(),p={}){
 if(serialize(parse())!==STRUCTURE)throw new Error('topology changed');
 const c=config(p);
 return domain(domain(state,1,c.eta1,c.phase1),2,c.eta2,c.phase2);
}
export function backward(state,p={}){
 const c=config(p);
 return domain(domain(state,2,c.eta2,c.phase2,true),1,c.eta1,c.phase1,true);
}
export function analytic(p={}){
 const c=config(p);return {travel:(1-c.eta1)*(1-c.eta2),domain1:c.eta1,domain2:(1-c.eta1)*c.eta2,total:1};
}
export function audit(p={}){
 const x=initial(),y=forward(x,p),z=backward(y,p),a=analytic(p);
 return {structure:STRUCTURE,energyChannels:y.map(v=>v[0]**2+v[1]**2),analytic:a,norm:norm(y),recoveryMax:Math.max(...x.flatMap((v,i)=>v.map((n,j)=>Math.abs(n-z[i][j]))))};
}
export const BOUNDARY=Object.freeze({reversibleMathematicalModel:true,physicalDysonCaptureEstablished:false,negativeEnergyDemonstrated:false,planckScaleTransitDemonstrated:false});
