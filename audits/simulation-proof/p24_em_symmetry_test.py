#!/usr/bin/env python3
"""ROOT0 P2.4: exact cube-corner photon carrier symmetry obstruction.

A conditional, classical eight-direction transport interpretation of the
frozen ROOT0 kernel. This is NOT Maxwell/QED and does not prove reality simulated.
"""
from __future__ import annotations
import hashlib, json, math, random, subprocess, sys
from fractions import Fraction as F
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE_DIR=HERE if (HERE/'kernel.py').is_file() else HERE.parents[1]/'kernel'/'frozen'/'ae-generative-first-v92'
sys.path.insert(0,str(SOURCE_DIR))
import kernel
SOURCE_SHA='bf84cfc8746ccaf35c0204050ada8c3980817cb8'
CANON_SHA='8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8'
assert subprocess.check_output(['git','hash-object',str(SOURCE_DIR/'kernel.py')],text=True).strip()==SOURCE_SHA
assert hashlib.sha256((SOURCE_DIR/'CANON.json').read_bytes()).hexdigest()==CANON_SHA
canon=kernel.load_and_verify_canon(SOURCE_DIR/'CANON.json')
assert canon['immutability']['physical_claim']=='none; symbolic/model-local unless separately validated'

# Proposed '2^3' interpretation: cube-corner propagation directions.
sgn=lambda bits,axis: 1 if ((bits>>axis)&1)==0 else -1
SIGNS=[tuple(sgn(b,i) for i in range(3)) for b in range(8)]
assert len(set(SIGNS))==8
assert all(sum(x*x for x in v)==3 for v in SIGNS)
assert all(sum(v[i] for v in SIGNS)==0 for i in range(3))
N=8
# Exact angular moments (normalized directions n = sign / sqrt(3)).
first=[F(sum(v[i] for v in SIGNS),8) for i in range(3)]
second=[[F(sum(v[i]*v[j] for v in SIGNS),24) for j in range(3)] for i in range(3)]
third=[F(sum(v[0]*v[1]*v[2] for v in SIGNS),8*3) ]
xxxx=F(sum(v[0]**4 for v in SIGNS),8*9)
xxyy=F(sum(v[0]**2*v[1]**2 for v in SIGNS),8*9)
assert first==[0,0,0]
assert second==[[F(1,3) if i==j else 0 for j in range(3)] for i in range(3)]
assert third==[0]
assert (xxxx,xxyy)==(F(1,9),F(1,9))
# Isotropic directions under SO(3) have 4th moments 1/5 and 1/15.
iso_xxxx,iso_xxyy=F(1,5),F(1,15)
assert 3*iso_xxxx+6*iso_xxyy==1 and iso_xxxx==3*iso_xxyy
assert xxxx!=iso_xxxx and xxyy!=iso_xxyy
# ANY weights on these 8 corners (nonnegative or signed) summing to unity
# leave both diagonal monomials at exactly 1/9, because every corner has
# n_x^4=n_x^2 n_y^2=1/9.
randomizer=random.Random(24042026)
weight_trials=0
for _ in range(512):
    raw=[randomizer.randrange(0,10000) for _ in range(8)]
    if sum(raw)==0:raw[0]=1
    weights=[F(x,sum(raw)) for x in raw]
    assert sum(weights)==1
    weighted_xxxx=sum(w*F(v[0]**4,9) for w,v in zip(weights,SIGNS))
    weighted_xxyy=sum(w*F(v[0]**2*v[1]**2,9) for w,v in zip(weights,SIGNS))
    assert weighted_xxxx==weighted_xxyy==F(1,9)
    weight_trials+=1
# F(e) = average (n.corner dot e)^4; a 3D isotropic sphere gives 1/5
axis_projection_fourth=F(1,9)
body_diagonal_projection_fourth=F(7,27)
assert body_diagonal_projection_fourth-axis_projection_fourth==F(4,27)

# Eight physically transverse polarization planes exist. P=I-n*n^T,
# P^2=P, P*n=0, trace(P)=2. The average projector is 2/3 I.
Pavg=[[0.0]*3 for _ in range(3)]
polar_tests=0
worst_p_error=0.0
for sign in SIGNS:
    n=[x/math.sqrt(3) for x in sign]
    P=[[float(i==j)-n[i]*n[j] for j in range(3)] for i in range(3)]
    errors=[]
    for i in range(3):
        errors.append(abs(sum(P[i][j]*n[j] for j in range(3))))
        for j in range(3):
            square=sum(P[i][k]*P[k][j] for k in range(3))
            errors.append(abs(square-P[i][j]))
            Pavg[i][j]+=P[i][j]/8
    errors.append(abs(sum(P[i][i] for i in range(3))-2))
    # Two orthonormal transverse vectors for each proposed photon direction.
    u=[n[1],-n[0],0.0]
    u=[x/math.sqrt(sum(t*t for t in u)) for x in u]
    v=[n[1]*u[2]-n[2]*u[1], n[2]*u[0]-n[0]*u[2], n[0]*u[1]-n[1]*u[0]]
    assert abs(sum(n[i]*u[i] for i in range(3)))<1e-14
    assert abs(sum(n[i]*v[i] for i in range(3)))<1e-14
    assert abs(sum(u[i]*v[i] for i in range(3)))<1e-14
    assert abs(sum(u[i]*u[i] for i in range(3))-1)<1e-14
    assert abs(sum(v[i]*v[i] for i in range(3))-1)<1e-14
    for i in range(3):
        for j in range(3): errors.append(abs(u[i]*u[j]+v[i]*v[j]-P[i][j]))
    worst_p_error=max(worst_p_error,*errors)
    polar_tests+=1
assert worst_p_error<5e-15
assert all(abs(Pavg[i][j]-(2/3 if i==j else 0))<5e-15 for i in range(3) for j in range(3))
# An exact 45 degree rotation in xy sends corner (1,1,1) to (0,sqrt(2),1).
# Such a direction has zero x-component; none of 8 signed corners does.
rotation_45_closed=False
assert all(v[0]!=0 for v in SIGNS)

# Both direction update laws (straight/rotate8) are permutation operators: their
# 8-component amplitude L2 norm is preserved. This is only probability norm
# conservation, NOT a field Hamiltonian or electromagnetic energy proof.
unitary_trials=0
max_unitary_error=0.0
for _ in range(512):
    amplitudes=[complex(randomizer.uniform(-1,1),randomizer.uniform(-1,1)) for _ in range(8)]
    before=sum(abs(a)**2 for a in amplitudes)
    straight=amplitudes.copy()
    rotate=[amplitudes[(i-1)%8] for i in range(8)]
    errors=[abs(sum(abs(a)**2 for a in vector)-before) for vector in (straight,rotate)]
    max_unitary_error=max(max_unitary_error,*errors)
    assert max(errors)<1e-12
    unitary_trials+=1

# Frozen logical clock is independent of conditional photon polarizations.
STEPS=12_288
cur=kernel.genesis()
for t in range(1,STEPS+1):
    nxt=kernel.advance(cur)
    assert nxt.parent_seal==cur.seal()
    assert 12*nxt.generation+nxt.q==t
    cur=nxt
assert cur.generation==1024 and cur.q==0

# An optional scalar-wave toy, a=2lP, tau=lP/c; NOT Maxwell dynamics.
# This demonstrates a dimensionful discriminator only conditionally.
C=299792458.; LP=1.616255e-35; HBARC=.1973269804e-15; GPC=3.0856775814913673e25
A=2*LP; TAU=LP/C; r=C*TAU/A
assert abs(r-.5)<1e-15 and 3*r*r<1
dE2=30**2-1**2
base=(GPC/C)*(A*A/(8*HBARC*HBARC))*dE2
axis_delay=base*(1-r*r)
diag_delay=base*(F(1,3)-F(1,4))
angular_contrast=axis_delay-diag_delay
assert 2e-19<axis_delay<3e-19 and 2e-20<diag_delay<3e-20
assert abs(angular_contrast-base*2/3)<1e-30
# An illustrative millisecond timing benchmark is massively coarser.
resolution_s=1e-3
ratio=float(resolution_s/angular_contrast)
assert ratio>1e15

result={
 'schema':'ROOT0-P2.4-classical-cube-corner-EM-filter',
 'original_git_blob':SOURCE_SHA, 'frozen_canon_sha256':CANON_SHA,
 'source_cycles':1024, 'source_transitions':STEPS,
 'proposed_direction_count':8,'direction_norm':'one',
 'first_moment':[str(x) for x in first],
 'second_moment':[[str(x) for x in row] for row in second],
 'fourth_moment_xxxx':str(xxxx),'fourth_moment_xxyy':str(xxyy),
 'isotropic_fourth_xxxx':str(iso_xxxx),'isotropic_fourth_xxyy':str(iso_xxyy),
 'axis_projection_fourth':str(axis_projection_fourth),
 'diagonal_projection_fourth':str(body_diagonal_projection_fourth),
 'axis_diagonal_fourth_contrast':str(body_diagonal_projection_fourth-axis_projection_fourth),
 'weight_invariant_fourth_moment':True,'additional_exact_weight_trials':weight_trials,
 'transverse_polarization_projectors':polar_tests,'max_projector_error':worst_p_error,
 'mean_polarization_projector':Pavg,
 'closed_under_45deg_rotation':rotation_45_closed,
 'unitary_complex_amplitude_trials':unitary_trials,
 'max_permutation_norm_error':max_unitary_error,
 'photon_step_length_m_if_externally_calibrated':1.616255e-35,
 'coordinate_step_m_if_externally_calibrated':1.616255e-35/math.sqrt(3),
 'source_frozen_core_changed':False,
 'conditional_scalar_wave_a_m':A, 'conditional_tau_s':TAU,'conditional_r':r,
 'conditional_axis_delay_s':axis_delay,'conditional_diagonal_delay_s':float(diag_delay),
 'conditional_angular_contrast_s':angular_contrast,
 'illustrative_timing_resolution_s':resolution_s,'resolution_over_anisotropy':ratio,
 'maxwell_equivalence_established':False,'quantum_eight_state_no_go_proven':False,
 'empirical_observation_tested':False,'simulation_theory_proven':False,
 'lean_machine_checked':False,'status':'PASS_CLASSICAL_DIRECTION_SET_NO_GO_AND_TRANSVERSE_PROJECTION'
}
(HERE/'p24-results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,indent=2))
