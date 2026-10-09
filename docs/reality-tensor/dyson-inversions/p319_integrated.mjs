/** P3.19: lossless address identity + unitary dual-port transport. */
import {encode,decode} from './p318_hierarchy.mjs';
import {forward,inverse,norm,initial} from './p314_dual_branch.mjs';
const valid=s=>Array.isArray(s)&&s.length===3&&s.every(z=>Array.isArray(z)&&z.length===2&&z.every(Number.isFinite));
export function ingress({seed,dimension=0,quad=0,coords=[0n,0n,0n],state=initial()}){
 if(!valid(state))throw new TypeError('three complex amplitudes required');
 const address=encode(seed,dimension,quad,coords);
 const transported=forward(state);
 return {address,transported,beforeNorm:norm(state),afterNorm:norm(transported)};
}
export function egress(packet){
 if(!packet||!valid(packet.transported))throw new TypeError('packet');
 const parsed=decode(packet.address),recovered=inverse(packet.transported);
 return {...parsed,address:packet.address,recovered,norm:norm(recovered)};
}
export function audit(source){
 const packet=ingress(source),back=egress(packet),original=source.state??initial();
 return {seed:back.seed,addressStable:back.address===packet.address,coordinateStable:back.coords.every((x,i)=>x===(source.coords??[0n,0n,0n])[i]),normError:Math.abs(packet.afterNorm-packet.beforeNorm),recoveryError:Math.max(...original.flatMap((z,i)=>z.map((v,j)=>Math.abs(v-back.recovered[i][j]))))};
}
