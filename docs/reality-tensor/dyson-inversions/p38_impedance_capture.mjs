/** ROOT0 P3.8: deterministic reversible Dyson-shell impedance coupling.
 * Symbolic Z(u)=1+u, u=ln(r0/r)/ln(r0/rPlanck).
 * Fresnel-inspired eta=((Znext-Zprev)/(Znext+Zprev))**2.
 * No measured electrum impedance or asserted physical Planck transit.
 */
import * as P37 from './p37_dyson_scale.mjs';
export const VERSION='P3.8';
export const POLICY='log-radius-linear-impedance-fresnel-v1';
export const ROOT='Complex[0]';
const mag2=z=>z[0]**2+z[1]**2;
export function profile(p={}) {
 const cfg=P37.check(p),total=Math.log(cfg.startRadiusM/P37.CONSTANTS.planckM);
 return Array.from({length:cfg.shells},(_,j)=>{
  const u0=cfg.depth*j/cfg.shells,u1=cfg.depth*(j+1)/cfg.shells;
  const Z0=1+u0,Z1=1+u1,eta=((Z1-Z0)/(Z1+Z0))**2;
  return Object.freeze({index:j,radiusOuterM:cfg.startRadiusM*Math.exp(-total*u0),radiusInnerM:cfg.startRadiusM*Math.exp(-total*u1),Z0,Z1,eta});
 });
}
function validate(s,n){if(!Array.isArray(s)||s.length!==n+1||!s.every(z=>Array.isArray(z)&&z.length===2&&z.every(x=>typeof x==='number'&&Number.isFinite(x))))throw new TypeError('complex ports');}
const complexMul=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]];
const phase=x=>[Math.cos(x),Math.sin(x)];
function beam(a,b,eta,inverse){const t=Math.sqrt(1-eta),r=(inverse?-1:1)*Math.sqrt(eta);return [[t*a[0]-r*b[1],t*a[1]+r*b[0]],[t*b[0]-r*a[1],t*b[1]+r*a[0]]];}
export function at(s,j,p={},inverse=false){
 const cfg=P37.check(p);validate(s,cfg.shells);
 if(!Number.isInteger(j)||j<0||j>=cfg.shells)throw new RangeError('shell');
 const eta=profile(cfg)[j].eta,v=s.map(z=>z.slice()),phi=P37.totalPortPhase(cfg)/cfg.shells;
 if(inverse){const [a,b]=beam(v[0],v[j+1],eta,true);v[0]=complexMul(a,phase(-phi));v[j+1]=b;}
 else{const [a,b]=beam(complexMul(v[0],phase(phi)),v[j+1],eta,false);v[0]=a;v[j+1]=b;}
 return v;
}
export function forward(s,p={}){const cfg=P37.check(p);let out=s;for(let j=0;j<cfg.shells;j++)out=at(out,j,cfg);return out;}
export function inverse(s,p={}){const cfg=P37.check(p);let out=s;for(let j=cfg.shells-1;j>=0;j--)out=at(out,j,cfg,true);return out;}
export function analytic(p={}){const xs=profile(p);let travel=1;const captured=[];for(const x of xs){captured.push(travel*x.eta);travel*=1-x.eta;}return {travel,captured,total:travel+captured.reduce((a,b)=>a+b,0)};}
export function audit(p={}){const input=P37.inputState(p),result=forward(input,p),back=inverse(result,p),a=analytic(p);return {policy:POLICY,profile:profile(p),analytic:a,norm:P37.norm(result),maxRecoveryError:Math.max(...back.flatMap((z,i)=>z.map((v,k)=>Math.abs(v-input[i][k])))),maxPowerError:Math.max(Math.abs(mag2(result[0])-a.travel),...result.slice(1).map((z,i)=>Math.abs(mag2(z)-a.captured[i])))};}
export const SCIENCE_STATUS=Object.freeze({mathematicalScatteringUnitary:true,profilePhysicallyMeasured:false,planckTransitDemonstrated:false,voltageConvertedToLength:false});
