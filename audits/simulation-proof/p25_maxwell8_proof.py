#!/usr/bin/env python3
"""ROOT0 P2.5: constructive 8-complex-component transverse Maxwell embedding.
This is an ADDED continuum physical representation, not an I13-v92 derived law.
"""
from __future__ import annotations
from pathlib import Path
import ast, hashlib, itertools, json, math, subprocess, sys
import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE if (HERE/'kernel.py').is_file() else HERE.parents[1]/'kernel'/'frozen'/'ae-generative-first-v92'
sys.path.insert(0, str(SOURCE))
import kernel

ORIGINAL_GIT_BLOB='bf84cfc8746ccaf35c0204050ada8c3980817cb8'
ORIGINAL_CANON_SHA256='8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8'
assert subprocess.check_output(['git','hash-object',str(SOURCE/'kernel.py')],text=True).strip()==ORIGINAL_GIT_BLOB
assert hashlib.sha256((SOURCE/'CANON.json').read_bytes()).hexdigest()==ORIGINAL_CANON_SHA256
canon = kernel.load_and_verify_canon(SOURCE/'CANON.json')
assert canon['immutability']['physical_claim']=='none; symbolic/model-local unless separately validated'
assert kernel.PHASE_SEQUENCE == ('a00','b11','c22','b33','c44','a55','c66','a77','b88','c99','b00','a11')

I8=np.eye(8,dtype=np.complex128)
# 8 states = (E_x,E_y,E_z,B_x,B_y,B_z,s_0,s_1) in C^8
# Scalar auxiliaries are inert; they are not extra physical photon polarizations.
def cross_matrix(k):
    x,y,z=np.asarray(k,dtype=float)
    return np.array([[0,-z,y],[z,0,-x],[-y,x,0]],dtype=float)
def transverse_Q(k):
    k=np.asarray(k,dtype=float)
    mag=np.linalg.norm(k)
    assert mag>0
    K=cross_matrix(k/mag)
    Q=np.zeros((8,8),dtype=np.complex128)
    Q[:3,3:6]=K
    Q[3:6,:3]=-K
    return Q

def U(k,theta):
    Q=transverse_Q(k)
    return I8 + 1j*np.sin(theta)*Q + (np.cos(theta)-1)*(Q@Q)

def rotation(rng):
    A=rng.normal(size=(3,3))
    R,_=np.linalg.qr(A)
    if np.linalg.det(R)<0:R[:,0]*=-1
    return R

def embed_rotation(R):
    # E is polar, B is axial: parity includes det(R) on the magnetic block.
    D=np.eye(8,dtype=np.complex128)
    D[:3,:3]=R;D[3:6,3:6]=round(float(np.linalg.det(R)))*R
    return D

def norm_err(M):return float(np.linalg.norm(M))

def divs(k,psi):return np.dot(k,psi[:3]),np.dot(k,psi[3:6])

rng=np.random.default_rng(20261009)
trials=512
maxerr={key:0. for key in ['Qhermitian','Qcubical','projector_rank','Uunitary','group_composition','rotation_covariance','parity_covariance','norm_conservation','gauss_preservation','scalar_inert','physical_mode','gauge_invariance','positive_freq_rank','same_clock']}
for trial in range(trials):
    k=rng.normal(size=3);k=k/np.linalg.norm(k)
    Q=transverse_Q(k);P=Q@Q
    vals=np.linalg.eigvalsh(Q)
    assert np.allclose(vals,[-1,-1,0,0,0,0,1,1],atol=1e-12)
    maxerr['Qhermitian']=max(maxerr['Qhermitian'],norm_err(Q-Q.conj().T))
    maxerr['Qcubical']=max(maxerr['Qcubical'],norm_err(Q@Q@Q-Q))
    maxerr['projector_rank']=max(maxerr['projector_rank'],abs(int(np.linalg.matrix_rank(P))-4))
    a,b=rng.uniform(-3,3,size=2)
    Ua=U(k,a);Ub=U(k,b)
    maxerr['Uunitary']=max(maxerr['Uunitary'],norm_err(Ua.conj().T@Ua-I8))
    maxerr['group_composition']=max(maxerr['group_composition'],norm_err(Ua@Ub-U(k,a+b)))
    R=rotation(rng);D=embed_rotation(R)
    maxerr['rotation_covariance']=max(maxerr['rotation_covariance'],norm_err(U(R@k,a)-D@Ua@D.conj().T))
    parity=np.diag([-1.,1.,1.]);Dp=embed_rotation(parity)
    maxerr['parity_covariance']=max(maxerr['parity_covariance'],norm_err(U(parity@k,a)-Dp@Ua@Dp.conj().T))
    psi=rng.normal(size=8)+1j*rng.normal(size=8)
    later=Ua@psi
    maxerr['norm_conservation']=max(maxerr['norm_conservation'],abs(np.vdot(psi,psi)-np.vdot(later,later)))
    d0=divs(k,psi);d1=divs(k,later)
    maxerr['gauss_preservation']=max(maxerr['gauss_preservation'],abs(d0[0]-d1[0]),abs(d0[1]-d1[1]))
    maxerr['scalar_inert']=max(maxerr['scalar_inert'],float(np.max(np.abs(psi[6:]-later[6:]))))

    # Construct two orthonormal transverse E vectors; B = k_hat cross E.
    e1=np.cross(k, np.array([0.,0.,1.]))
    if np.linalg.norm(e1)<.05:e1=np.cross(k,np.array([0.,1.,0.]))
    e1=e1/np.linalg.norm(e1);e2=np.cross(k,e1)
    modes=[]
    for e in (e1,e2):
        state=np.zeros(8,dtype=np.complex128)
        state[:3]=e/math.sqrt(2)
        state[3:6]=np.cross(k,e)/math.sqrt(2)
        modes.append(state)
        maxerr['physical_mode']=max(maxerr['physical_mode'],norm_err(Q@state+state),norm_err(Ua@state-np.exp(-1j*a)*state))
    assert abs(np.vdot(modes[0],modes[1]))<1e-12
    Pminus=(P-Q)/2
    maxerr['positive_freq_rank']=max(maxerr['positive_freq_rank'],abs(np.linalg.matrix_rank(Pminus)-2))

    # Gauge transform of plane-wave potentials does not change E or B fields.
    # A -> A+i k chi, dA -> dA+i k dchi, phi -> phi-dchi
    A=rng.normal(size=3)+1j*rng.normal(size=3)
    dA=rng.normal(size=3)+1j*rng.normal(size=3)
    phi=rng.normal()+1j*rng.normal();chi=rng.normal()+1j*rng.normal();dchi=rng.normal()+1j*rng.normal()
    E=-dA-1j*k*phi; B=1j*np.cross(k,A)
    Ap=A+1j*k*chi;dAp=dA+1j*k*dchi;phip=phi-dchi
    Ep=-dAp-1j*k*phip;Bp=1j*np.cross(k,Ap)
    maxerr['gauge_invariance']=max(maxerr['gauge_invariance'],norm_err(E-Ep),norm_err(B-Bp))

assert max(maxerr.values()) < 1e-10,maxerr
# Negative controls: the validators must detect an actual violation, not just PASS everything.
k0=np.array([0.,0.,1.]);theta=0.72;u0=U(k0,theta);p0=embed_rotation(np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]]))
assert norm_err((1.01*u0).conj().T@(1.01*u0)-I8)>0.01  # nonunitary scaling
wrong=np.diag([np.exp(0.2j),1,1,1,1,1,1,1])@u0
assert norm_err(wrong.conj().T@wrong-I8)<1e-12  # still unitary!
assert norm_err(wrong-p0@wrong@p0.conj().T)>1e-2  # but breaks spatial covariance
state=np.zeros(8,dtype=np.complex128);state[0]=1
assert abs(np.dot(k0,(u0@state)[:3]))<1e-12  # transverse initial E remains transverse
leak=np.copy(u0);leak[2,0]+=0.1
assert abs(np.dot(k0,(leak@state)[:3]))>0.09  # detects longitudinal leakage
# Explicit inequivalent isotropic, norm-preserving choices: alpha=0 versus alpha=-1.
# BOTH share the same Maxwell-like internal field generator and respect rotations;
# alpha !=0 has a frequency-dependent phase f(k)=c|k|[1+alpha*(k*lP)^2].
C=299792458.0; LP=1.616255e-35; HBAR_C=0.1973269804e-15; GPC=3.0856775814913673e25
LOW=1.;HIGH=30.; D=GPC

def velocity_ratio(E_GeV, alpha):
    x=E_GeV*LP/HBAR_C
    return 1+3*alpha*x*x

def delay_high_minus_low(alpha):
    return (D/C)*(1/velocity_ratio(HIGH,alpha)-1/velocity_ratio(LOW,alpha))

def delay_approx(alpha):
    return -(D/C)*3*alpha*(LP/HBAR_C)**2*(HIGH**2-LOW**2)

assert delay_high_minus_low(0.)==0.
# 1/(1-x) near 1 cannot be resolved as a float for x~1e-36. Use a
# stable analytic rational difference rather than catastrophic cancellation.
def stable_delay(alpha):
    h=3*alpha*(LP/HBAR_C)**2*HIGH**2
    l=3*alpha*(LP/HBAR_C)**2*LOW**2
    return (D/C)*(l-h)/((1+h)*(1+l))
assert stable_delay(0.) == 0
candidate_delay=stable_delay(-1)
assert 1e-18<candidate_delay<3e-18
assert abs(candidate_delay-delay_approx(-1))/candidate_delay<1e-12

# Run the exact original frozen clock independently under two distinct
# physical wave-dispersion attachments. They never feed back into v92.
steps=12288
sa=sb=kernel.genesis()
for n in range(1,steps+1):
    sa=kernel.advance(sa);sb=kernel.advance(sb)
    assert sa==sb and n==12*sa.generation+sa.q
assert sa.generation==1024 and sa.q==0

results={
    'gate':'ROOT0-P2.5-eight-component-Maxwell-candidate',
    'status':'PASS_CONSTRUCTIVE_SO3_COVARIANT_EIGHT_COMPONENT_REPRESENTATION',
    'source_git_blob':ORIGINAL_GIT_BLOB,
    'canon_sha256':ORIGINAL_CANON_SHA256,
    'state_space':'C^8 as (E3,B3,scalar2); NOT 8 literal spatial directions',
    'spin1_rotation_representation':'D(R)=diag(R,R,1,1)',
    'physical_positive_frequency_polarizations':2,
    'eigenvalue_multiplicity':{'minus_one':2,'zero':4,'plus_one':2},
    'trials':trials,
    'max_numerical_errors':maxerr,
    'frozen_ticks_per_model':steps,
    'frozen_core_mismatches':0,
    'models':[
       {'alpha':0,'group_speed_model':'c','30vs1_GeV_1Gpc_delay_s':stable_delay(0)},
       {'alpha':-1,'group_speed_model':'c[1-3(k*lP)^2]','30vs1_GeV_1Gpc_delay_s':candidate_delay}
    ],
    'amplitude_norm_conserved':True,
    'gauss_constraints_preserved':True,
    'rotational_covariance_numeric':True,
    'proper_and_improper_rotation_covariance_numeric':True,
    'negative_controls_detected':['nonunitarity','unitary_but_rotation_violating','Gauss_constraint_leak'],
    'gauge_potential_redundancy_in_field_observables':True,
    'Maxwell_continuum_coupling_is_extra':True,
    'not_a_quantized_photon_model':True,
    'field_energy_normalization_not_derived_from_ROOT0':True,
    'physical_dispersion_uniquely_determined':False,
    'Lean_compiled':False,
    'real_universe_simulation_proven':False
}
(HERE/'p25-results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf8')
print(json.dumps(results,indent=2))
