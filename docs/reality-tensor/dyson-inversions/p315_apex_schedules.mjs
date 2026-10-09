/** ROOT0 P3.15: dual-arm apex scheduling, explicit unitary conventions.
 * Schedules LR, RL, and Strang paired (L/2, R, L/2).
 * The pinned Complex[0] is a zero reference, NOT a normalization sink.
 */
import {compile,initial,norm,LEFT,RIGHT,APEX} from './p314_dual_branch.mjs';
const multiply=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]];
const expi=t=>[Math.cos(t),Math.sin(t)];
const sq=z=>z[0]*z[0]+z[1]*z[1];
function gate(s,g,half=false,inverse=false){
 const v=s.map(z=>z.slice()),a=v[0],b=v[g.port];
 const theta=Math.asin(Math.sqrt(g.eta))*(half?0.5:1),t=Math.cos(theta),r=Math.sin(theta);
 const phi=g.angle*(half?0.5:1);
 if(inverse){
  const x=[t*a[0]+r*b[1],t*a[1]-r*b[0]];
  v[g.port]=[t*b[0]+r*a[1],t*b[1]-r*a[0]];
  v[0]=multiply(x,expi(-phi));
 }else{
  const x=multiply(a,expi(phi));
  v[0]=[t*x[0]-r*b[1],t*x[1]+r*b[0]];
  v[g.port]=[t*b[0]-r*x[1],t*b[1]+r*x[0]];
 }
 return v;
}
export const MODES=Object.freeze(['LR','RL','PAIRED']);
export function schedule(mode='PAIRED'){
 if(!MODES.includes(mode))throw new RangeError('mode');
 const g=compile(),steps=[];
 for(let i=0;i<g.length;i+=2){
  const L=g[i],R=g[i+1];
  if(mode==='LR')steps.push([L,false],[R,false]);
  else if(mode==='RL')steps.push([R,false],[L,false]);
  else steps.push([L,true],[R,false],[L,true]);
 }
 return steps.map(([descriptor,half])=>Object.freeze({...descriptor,half}));
}
export function run(state=initial(),mode='PAIRED',inverse=false){
 if(!Array.isArray(state)||state.length!==3||!state.every(z=>Array.isArray(z)&&z.length===2&&z.every(Number.isFinite)))throw new TypeError('state');
 const gates=schedule(mode),steps=inverse?gates.reverse():gates;
 return steps.reduce((s,g)=>gate(s,g,g.half,inverse),state.map(z=>z.slice()));
}
export function measure(mode='PAIRED'){
 const input=initial(),out=run(input,mode),back=run(out,mode,true);
 return {mode,events:schedule(mode).length,energy:out.map(sq),norm:norm(out),recovery:Math.max(...back.flatMap((z,i)=>z.map((x,j)=>Math.abs(x-input[i][j])))),allZero:out.every(z=>sq(z)<1e-24)};
}
export function compare(){const LR=run(initial(),'LR'),RL=run(initial(),'RL');return {modes:MODES.map(measure),orderGap:Math.sqrt(LR.reduce((s,z,i)=>s+sq([z[0]-RL[i][0],z[1]-RL[i][1]]),0)),zeroFixedPoint:run([[0,0],[0,0],[0,0]]).every(z=>sq(z)===0),apex:APEX,branches:[LEFT,RIGHT]};}
