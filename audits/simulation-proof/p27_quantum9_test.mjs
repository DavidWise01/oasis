#!/usr/bin/env node
// ROOT0 P2.7 correction gate: user premise quantum=9, WITHOUT assuming glyph semantics.
// Shows that 9 classical labels cover 9 samples but cannot be closed under
// a nontrivial continuous rotation; a C^3⊗C^3 carrier can rotate continuously.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync, writeFileSync, existsSync} from 'node:fs';
import {dirname, resolve, join} from 'node:path';
import {fileURLToPath} from 'node:url';
const N=9, eps=2e-12;
const eq=(a,b,t=eps)=>Math.abs(a-b)<t;
const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
const norm=a=>Math.hypot(...a);
const eye=n=>Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>+(i===j)));
const Rz=theta=>{
  const c=Math.cos(theta),s=Math.sin(theta);
  return [[c,-s,0],[s,c,0],[0,0,1]];
};
const kron=(A,B)=>A.flatMap(ar=>B.map(br=>ar.flatMap(a=>br.map(b=>a*b))));
const mul=(A,B)=>A.map(row=>B[0].map((_,j)=>row.reduce((s,v,k)=>s+v*B[k][j],0)));
const transpose=A=>A[0].map((_,j)=>A.map(r=>r[j]));
const maxDelta=(A,B)=>Math.max(...A.flatMap((row,i)=>row.map((v,j)=>Math.abs(v-B[i][j]))));
const mv=(A,v)=>A.map(row=>dot(row,v));
const basis=(i,n=N)=>Array.from({length:n},(_,j)=>+(i===j));
const isBasis=(v)=>v.some((x,i)=>Math.abs(x-1)<eps&&v.every((y,j)=>i===j||Math.abs(y)<eps));
const t=.37, D=kron(Rz(t),Rz(t));
assert.equal(D.length,9);assert(D.every(r=>r.length===9));
const unitarity=maxDelta(mul(transpose(D),D),eye(N));
assert(unitarity<eps);
const D2=kron(Rz(-.21),Rz(-.21));
const groupError=maxDelta(mul(D,D2),kron(Rz(.16),Rz(.16)));
assert(groupError<eps);
const nonBasis=Array.from({length:9},(_,i)=>({i,leavesBasis:!isBasis(mv(D,basis(i)))}));
assert.equal(nonBasis.filter(x=>x.leavesBasis).length,8);
assert.equal(nonBasis.filter(x=>!x.leavesBasis)[0].i,8);
// Exhibit >9 *physically different rays* within one SO(3) one-parameter orbit:
// |x>⊗|z> (coordinate i=2) rotated through 10 distinct angles in [0,pi).
const field=theta=>mv(kron(Rz(theta),Rz(theta)),basis(2));
const angles=Array.from({length:10},(_,j)=>j*Math.PI/10);
const orbit=angles.map(field);let leastSeparation=Infinity,highestRayFidelity=0;
for(let i=0;i<10;i++)for(let j=i+1;j<10;j++){
  const fidelity=dot(orbit[i],orbit[j])**2;
  highestRayFidelity=Math.max(highestRayFidelity,fidelity);
  leastSeparation=Math.min(leastSeparation,Math.sqrt(1-fidelity));
  assert(fidelity<1-1e-8);
}
assert(leastSeparation>0);
// 9 distinct samples are not a problem for 9 labels; the 10th is.
const nineSamples=angles.slice(0,9).map(field);
assert.equal(nineSamples.length,9);
// Sampling 9 rotations differs from exactly representing ALL rotations.
// Finite-state continuous action necessarily trivial: connected SO(3) -> discrete S_9.
const here=dirname(fileURLToPath(import.meta.url));
const standalone=existsSync(join(here,'upstream','kernel.py'));
const sourceDir=standalone?join(here,'upstream'):resolve(here,'../../kernel/frozen/ae-generative-first-v92');
const priorPath=standalone?join(here,'upstream','p26-results.json'):join(here,'p26-results.json');
const prevResults=JSON.parse(readFileSync(priorPath));
assert.equal(prevResults.classical_register_size,8);
const frozen=readFileSync(join(sourceDir,'kernel.py'));
const canon=readFileSync(join(sourceDir,'CANON.json'));
assert.equal(createHash('sha256').update(canon).digest('hex'),'8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8');
const result={
  gate:'ROOT0-P2.7-quantum-nine-correction',
  quantum_cardinality_user_specified:9,
  original_P26_cardinality:8,
  previous_nine_gt_eight_argument_applicable:false,
  nine_classical_labels_can_encode_nine_samples:true,
  ten_distinct_rotation_rays_exist:true,
  ten_rays_one_to_one_nine_labels_possible:false,
  complex_candidate:'C^3 tensor C^3 = C^9, added amplitude hypothesis',
  dimension_complex_candidate:9,
  non_basis_outputs_from_nine_basis_states:nonBasis.filter(x=>x.leavesBasis).length,
  SO3_z_rotation_unitarity_max_error:unitarity,
  SO3_representation_composition_max_error:groupError,
  ten_orbit_max_pairwise_fidelity:highestRayFidelity,
  ten_orbit_min_ray_separation:leastSeparation,
  central_zero_semantics:'UNSPECIFIED',
  operator_glyph_semantics:'UNSPECIFIED',
  original_v92_kernel_sha256:createHash('sha256').update(frozen).digest('hex'),
  original_v92_canon_sha256:createHash('sha256').update(canon).digest('hex'),
  from_frozen_runtime:false,
  lean_compiled:false,
  physical_simulation_proven:false,
  status:'PASS_CORRECTED_CARDINALITY_WITH_CONTINUOUS_ROTATION_OBSTRUCTION'
};
writeFileSync(new URL('./p27-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
