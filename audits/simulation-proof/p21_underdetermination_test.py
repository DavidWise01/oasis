#!/usr/bin/env python3
"""ROOT0 P2.1: exact frozen-v92 source, conditional physical-embedding nonuniqueness.
Source Git blob pinned to bf84cfc8746ccaf35c0204050ada8c3980817cb8.
Does NOT prove or disprove reality-as-simulation.
"""
import ast
from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib
import json
import math
import subprocess

import kernel  # exact original-v92 Python script; does not require CANON.json for run_steps

HERE=Path(__file__).resolve().parent
ORIGINAL_BLOB='bf84cfc8746ccaf35c0204050ada8c3980817cb8'
actual=subprocess.check_output(['git','hash-object',str(HERE/'kernel.py')],text=True).strip()
assert actual==ORIGINAL_BLOB,(actual,ORIGINAL_BLOB)
assert kernel.CANON_SHA256=='8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8'
canon=kernel.load_and_verify_canon(HERE/'CANON.json')
assert canon['schema']=='ae.generative-first.frozen-kernel.v92'
assert canon['immutability']['physical_claim']=='none; symbolic/model-local unless separately validated'
assert canon['ranks'][10]['rules'][5]=='q4=c44'
try:
    kernel.load_and_verify_canon(HERE/'kernel.py')
    raise AssertionError('noncanonical file wrongly accepted')
except RuntimeError:
    pass

# AST audit identifies *which* quantities actually drive the transition code.
source=(HERE/'kernel.py').read_text(encoding='utf-8')
mod=ast.parse(source)
fns={node.name:node for node in mod.body if isinstance(node,ast.FunctionDef)}
assert {'genesis','advance','run_steps','verify_invariants'}.issubset(fns)
transitions=('advance','genesis','run_steps')
read_names=sorted(set(n.id for key in transitions for n in ast.walk(fns[key]) if isinstance(n,ast.Name)))
assert not set(['spacing_m','a_m','lattice_spacing','hbar','light_speed','c_m_s','energy_GeV']).intersection(read_names)
assert all(not arg.arg.startswith(('a_m','spacing_m','wavelength_m')) for n in fns.values() for arg in n.args.args)

C=299792458.0                         # m/s, exact
LP=1.616255e-35                        # m, rounded CODATA
TP=LP/C                               # s, chosen externally; code has no SI tick field
HBARC=0.1973269804e-15                 # GeV*m
GPC=3.0856775814913673e25            # m
HIGH=30.0; LOW=1.0                   # GeV
DURATION=GPC/C                        # s

def delay(a_m, angle4):
    r=(C*TP)/a_m
    assert 3*r*r <1-1e-12, 'require strictly stable centered scalar lattice'
    factor=DURATION*(a_m*a_m)/(8*HBARC*HBARC)*(HIGH*HIGH-LOW*LOW)
    return factor*(angle4-r*r)

@dataclass(frozen=True)
class PhysicalEmbedding:
    label:str
    spacing_m:float
    tick_s:float

# Distinct, equally stable physical attachments, chosen before observation.
worlds=[PhysicalEmbedding('A-two-Planck-lengths',2*LP,TP),
        PhysicalEmbedding('B-three-Planck-lengths',3*LP,TP)]
records=[]
state_fingerprints=[]
STEPS=4096
for w in worlds:
    # Exact frozen function executed independently. No new metric enters genesis/advance.
    trajectory=kernel.run_steps(STEPS)
    assert kernel.verify_invariants(trajectory)
    assert len(trajectory)==STEPS+1
    assert trajectory[0].q==0 and trajectory[12].q==0
    assert trajectory[0].identity==trajectory[11].identity
    assert trajectory[12].identity!=trajectory[11].identity
    for i,s in enumerate(trajectory):
        assert s.q==i%12
        assert s.generation==i//12
    fingerprint=hashlib.sha256(kernel.canonical_json([asdict(x) for x in trajectory])).hexdigest()
    state_fingerprints.append(fingerprint)
    r=C*w.tick_s/w.spacing_m
    ax=delay(w.spacing_m,1.0)
    diag=delay(w.spacing_m,1/3)
    records.append({'label':w.label,'a_m':w.spacing_m,'a_over_lp':w.spacing_m/LP,
     'tau_s':w.tick_s,'courant_r':r,'CFL_max_rhs_3r2':3*r*r,
     'tick_run':STEPS,'final_q':trajectory[-1].q,'final_generation':trajectory[-1].generation,
     'final_lineage_seal':trajectory[-1].lineage_seal,
     'trajectory_sha256':fingerprint,'axis_delay_30vs1_GeV_1Gpc_s':ax,
     'diagonal_delay_30vs1_GeV_1Gpc_s':diag})
assert state_fingerprints[0]==state_fingerprints[1]
assert records[0]['final_lineage_seal']==records[1]['final_lineage_seal']
assert abs(records[1]['axis_delay_30vs1_GeV_1Gpc_s']/records[0]['axis_delay_30vs1_GeV_1Gpc_s']-8/3)<1e-12
assert abs(records[1]['diagonal_delay_30vs1_GeV_1Gpc_s']/records[0]['diagonal_delay_30vs1_GeV_1Gpc_s']-6)<1e-12
assert records[0]['CFL_max_rhs_3r2']<1 and records[1]['CFL_max_rhs_3r2']<1
assert records[0]['axis_delay_30vs1_GeV_1Gpc_s']!=records[1]['axis_delay_30vs1_GeV_1Gpc_s']

# Pointwise scale freedom persists for any positive a that passes CFL. Test a family.
scan=[]
for v in (1.8,2,2.5,3,4,10):
    a=v*LP
    r=LP/a
    assert 3*r*r<1
    scan.append({'a_over_lp':v,'axis_delay_s':delay(a,1),'diagonal_delay_s':delay(a,1/3)})
assert len({round(x['axis_delay_s']/scan[0]['axis_delay_s'],8) for x in scan})==len(scan)

output={
 'schema':'ROOT0-P2.1-source-pinned-physical-bridge-nonidentifiability',
 'tested_original_kernel_git_blob':actual,
 'canonical_digest_embedded_in_kernel':kernel.CANON_SHA256,
 'original_canon_bytes_verified_in_this_run':True,
 'kernel_steps_per_world':STEPS,
 'total_frozen_advance_calls':2*STEPS,
 'symbolic_trajectories_identical':True,
 'lineage_seals_identical':True,
 'wave_rule':'auxiliary centered scalar wave added in P2.0, NOT defined by v92',
 'physical_worlds':records,
 'axis_delay_ratio_B_over_A':records[1]['axis_delay_30vs1_GeV_1Gpc_s']/records[0]['axis_delay_30vs1_GeV_1Gpc_s'],
 'diagonal_delay_ratio_B_over_A':records[1]['diagonal_delay_30vs1_GeV_1Gpc_s']/records[0]['diagonal_delay_30vs1_GeV_1Gpc_s'],
 'dimensional_parameter_scan':scan,
 'transition_ast_names':read_names,
 'nonuniqueness_witness':'two strictly stable, distinct (a/tp) bridges; same exact symbolic states/lineage, different photon delays',
 'mathematical_result':'NO UNIQUE PHOTON DELAY DERIVABLE FROM IMPLEMENTED V92 TRANSITION AND A PLANCK TICK ALONE',
 'physical_reality_simulation_proven':False,
 'lean_compiled':False,
 'status':'PASS_EXPLICIT_NONUNIQUENESS_COUNTERMODELS'
}
(HERE/'p21-results.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in output.items() if k not in ('transition_ast_names','dimensional_parameter_scan')},indent=2))
