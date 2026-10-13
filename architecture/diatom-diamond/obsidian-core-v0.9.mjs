// OASIS {{i & dd}} v0.9 — additive OBSIDIAN CORE floor visualization and noise diagnostics.
// Physical obsidian is amorphous volcanic glass; the faceted renderer is symbolic.
// The frozen v0.7 dual code is never mutated. The v0.8 state model remains unchanged.
import {createHash} from 'node:crypto';
import {buildCoherent,assertFloor,MAX_LOCAL_DIM,norm} from './quantum-dual.mjs';
import {bindDual,recoverDual} from './frozen/dual5-floor-v0.7/dual5.mjs';
export const VERSION='i-dd-obsidian-floor/v0.9';
export const CHANNEL='global-isotropic-depolarization';
const sha = x => createHash('sha256').update(JSON.stringify(x)).digest('hex');
function requireNoise(p){if(typeof p!=='number'||!Number.isFinite(p)||p<0||p>1)throw new RangeError('noise p must lie in [0,1]');return p;}
function probabilityNoise(output,n,p){
 const dim=n*n;
 return output.map(row=>({positive:row.positive,negative:row.negative,
  probability:(1-p)*row.probability+p/dim}));
}
// Exact isotropic-state partial transpose eigenvalues. For maximally entangled
// |Phi_n> and rho=(1-p)|Phi_n><Phi_n|+p*I/n^2, the transpose has n(n+1)/2
// eigenvalues +(1-p)/n+p/n^2 and n(n-1)/2 of -(1-p)/n+p/n^2.
export function isotropicStats(n,p){
 if(!Number.isInteger(n)||n<2||n>MAX_LOCAL_DIM)throw new RangeError('n must be 2..'+MAX_LOCAL_DIM);
 requireNoise(p);
 const d=n*n,threshold=n/(n+1);
 const plus=(1-p)/n+p/d,minus=-(1-p)/n+p/d;
 const negativeEigenvalues=n*(n-1)/2;
 const negativity=p>=threshold?0:Math.max(0,-minus)*negativeEigenvalues;
 const logNegativity=Math.log2(2*negativity+1);
 const fidelity=1-p+p/d;
 const jointPurity=(1-p)*(1-p)+(2*p-p*p)/d;
 return {n,p,threshold,dimension:d,pureSchmidtBits:Math.log2(n),
  reducedEntropyBits:Math.log2(n),reducedPurity:1/n,
  fidelity,jointPurity,negativePartialTransposeEigenvalue:minus,
  negativeMultiplicity:negativeEigenvalues,
  negativity,logNegativity,entangled:p<threshold,
  separableByIsotropicCriterion:p>=threshold};
}
export function buildObsidian(tokens,{noise=0.10,parent='ROOT',generation=0}={}){
 requireNoise(noise);
 const floor=assertFloor();
 const packet=bindDual(tokens,{parent,generation});
 if(JSON.stringify(recoverDual(packet))!==JSON.stringify(tokens))throw new Error('frozen source failed recovery');
 const quantum=buildCoherent(tokens);
 if(Math.abs(norm(quantum.output)-1)>1e-9||quantum.maxInverseError>1e-9)throw new Error('v0.8 state failure');
 const model=isotropicStats(quantum.maps.n,noise);
 const outcomes=probabilityNoise(quantum.distribution,model.n,noise);
 const total=outcomes.reduce((a,x)=>a+x.probability,0);
 if(Math.abs(total-1)>1e-9)throw new Error('noisy probability failure');
 const upstream={floorSourceSha256:floor.source,floorWitness:packet.witness,
  floorIdentity:packet.identity.seal,sourceTokenDigest:sha(tokens),generation,
  noiseChannel:CHANNEL,noise,dimension:model.n};
 const stateWitness=sha(['OBSIDIAN/v0.9',upstream,model,quantum.maps.positive,quantum.maps.negative]);
 return {version:VERSION,coreMaterial:'faceted obsidian-style black volcanic glass',
  quantumInterpretation:'classical finite Hilbert-space simulation only',
  floor:{frozenVersion:'v0.7',sourceSha256:floor.source,witness:packet.witness,
         identity:packet.identity.seal,stepsPerRail:60,operators:'UUDDLRLRBASS',passesPerRail:5},
  core:{geometry:'dual helices / 5 turns / shared faceted black-glass core',
        coreWitness:stateWitness,noiseChannel:CHANNEL},
  stats:model,distribution:outcomes,
  maps:quantum.maps,maxInverseError:quantum.maxInverseError,
  consistency:{normalized:Math.abs(total-1)<1e-9,identityRecovered:true,floorDigestChecked:true}};
}
