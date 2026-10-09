/** P3.20 coordinate-bound dual-arm scattering. Symbolic mathematical model. */
import {encode,decode} from './p318_hierarchy.mjs';
import {compile,initial,norm} from './p314_dual_branch.mjs';
const TAU=2*Math.PI;
function signedMod(n,m){return Number(((n%m)+m)%m);}
export function addressPhase(address){
 const {seed,dimension,quad,coords}=decode(address);
 // Exact modular integer reduction avoids unsafe Number(BigInt) conversions.
 const residue=(BigInt(seed)+11n*BigInt(dimension)+17n*BigInt(quad)+coords[0]+3n*coords[1]+5n*coords[2]);
 return TAU*signedMod(residue,65521n)/65521;
}
const mul=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]];
const phase=t=>[Math.cos(t),Math.sin(t)];
function gate(s,g,theta,invert){
 const v=s.map(z=>z.slice()),a=v[0],b=v[g.port],t=Math.sqrt(1-g.eta),r=Math.sqrt(g.eta);
 if(invert){const x=[t*a[0]+r*b[1],t*a[1]-r*b[0]];v[g.port]=[t*b[0]+r*a[1],t*b[1]-r*a[0]];v[0]=mul(x,phase(-theta));}
 else{const x=mul(a,phase(theta));v[0]=[t*x[0]-r*b[1],t*x[1]+r*b[0]];v[g.port]=[t*b[0]-r*x[1],t*b[1]+r*x[0]];}
 return v;
}
export function execute(state,address,invert=false){
 if(!Array.isArray(state)||state.length!==3||!state.every(z=>Array.isArray(z)&&z.length===2&&z.every(Number.isFinite)))throw new TypeError('complex state');
 const offset=addressPhase(address),ops=compile(),sequence=invert?ops.reverse():ops;
 return sequence.reduce((s,g)=>gate(s,g,g.angle+(g.port===1?1:-1)*offset,invert),state.map(z=>z.slice()));
}
export function ingress({seed,dimension=0,quad=0,coords=[0n,0n,0n],state=initial()}){
 const address=encode(seed,dimension,quad,coords);return {address,channels:execute(state,address),sourceNorm:norm(state)};
}
export function egress(packet){
 if(!packet||typeof packet.address!=='string')throw new TypeError('packet');
 const descriptor=decode(packet.address),recovered=execute(packet.channels,packet.address,true);
 return {...descriptor,recovered,energy:norm(recovered)};
}
export function audit(input){const p=ingress(input),r=egress(p),s=input.state??initial();return {route:p.address,phase:addressPhase(p.address),beforeNorm:p.sourceNorm,afterNorm:norm(p.channels),recoveryError:Math.max(...s.flatMap((z,i)=>z.map((v,j)=>Math.abs(v-r.recovered[i][j]))))};}
