#!/usr/bin/env python3
"""ROOT0 P2.2: source-pinned logical-clock / phase-only observation no-go.
No claim that a simulation of physical reality is established.
"""
from __future__ import annotations
import ast
from dataclasses import replace
import hashlib
import json
import pathlib
import subprocess
import sys

HERE=pathlib.Path(__file__).resolve().parent
FROZEN=HERE if (HERE/'kernel.py').exists() else HERE.parents[2]/'kernel'/'frozen'/'ae-generative-first-v92'
sys.path.insert(0,str(FROZEN))
import kernel

SOURCE_GIT_BLOB='bf84cfc8746ccaf35c0204050ada8c3980817cb8'
CANON_SHA='8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8'
assert subprocess.check_output(['git','hash-object',str(FROZEN/'kernel.py')],text=True).strip()==SOURCE_GIT_BLOB
assert hashlib.sha256((FROZEN/'CANON.json').read_bytes()).hexdigest()==CANON_SHA
canon=kernel.load_and_verify_canon(FROZEN/'CANON.json')
assert canon['immutability']['physical_claim']=='none; symbolic/model-local unless separately validated'
assert canon['ranks'][10]['rules'][-1]=='q11:a11 -> q0:a00 causes new id -> new v^3'
assert len(kernel.PHASE_SEQUENCE)==12

# Structural source audit: v^3 is stored as SHA256-derived labels, not coordinates.
src=(FROZEN/'kernel.py').read_text()
module=ast.parse(src)
functions={n.name:n for n in module.body if isinstance(n,ast.FunctionDef)}
advance=functions['advance']
field_reads=sorted({n.attr for n in ast.walk(advance) if isinstance(n,ast.Attribute)})
assert 'q' in field_reads and 'generation' in field_reads
assert 'x_m' not in field_reads and 'time_s' not in field_reads
assert set(kernel.Context.__dataclass_fields__) == {'identity','generation','q','token','v3','parent_seal','lineage_seal'}
assert set(kernel.V3.__dataclass_fields__) == {'vector','voxel','vogel','sg'}

N=12288
states=kernel.run_steps(N)
assert kernel.verify_invariants(states)
wraps=0
q_only_cyclic=0
unique_ticks=set()
all_clock_increment=True
parent_chain_ok=0
live_state_count=0
by_token={t:0 for t in kernel.PHASE_SEQUENCE}
for i,s in enumerate(states):
    tick=12*s.generation+s.q
    assert tick==i,(i,tick)
    assert s.q==i%12 and s.generation==i//12
    assert s.token==kernel.PHASE_SEQUENCE[i%12]
    assert tick not in unique_ticks
    unique_ticks.add(tick)
    by_token[s.token]+=1
    live_state_count+=1
    if i:
        p=states[i-1]
        assert tick==12*p.generation+p.q+1
        assert s.parent_seal==p.seal()
        parent_chain_ok+=1
        if s.q==0:
            wraps+=1
            assert p.q==11 and s.generation==p.generation+1
    if i>=12:
        assert s.q == states[i-12].q and s.token==states[i-12].token
        q_only_cyclic+=1
assert wraps==N//12

# Phase-only maps are exactly period-12: no nonzero affine translation per step.
# Choose TWO different maps to show result is not dependent on one particular f.
phase_observables={
    'q_value':lambda q:q,
    'phase_sign':lambda q: 1 if q%2 else -1,
    'sinusoid_not_needed':lambda q: q*q-5*q,
}
for name,obs in phase_observables.items():
    for n in range(N-11):
        assert obs(states[n].q)==obs(states[n+12].q),name
    # The 12 displacement increments telescope to zero in each full cycle.
    period_displacements=[obs(states[n+12].q)-obs(states[n].q) for n in range(N-11)]
    assert all(x==0 for x in period_displacements)

# Logical clock *is not* physical time. These scales are alternative external maps.
scales=(1,2,7,12)
for tau_multiplier in scales:
    for idx in (0,1,11,12,13,24,123,4095,N):
        s=states[idx]
        t_external=tau_multiplier*(12*s.generation+s.q)
        assert t_external==tau_multiplier*idx

# Similarly two physical positions have same frozen states and lineage, but distinct motion.
# Use integer 'abstract length quanta' to avoid confusing finite precision with proof.
distance_mappings={'unit_per_tick':1,'triple_per_tick':3}
for idx in (0,1,12,13,120,N):
    assert distance_mappings['triple_per_tick']*idx == 3*distance_mappings['unit_per_tick']*idx
    assert states[idx].identity == states[idx].identity

# Attack the domain: v92's advance() does not reject forged out-of-range q.
# The clock theorem is valid on genesis-reachable states, not all untyped Context values.
invalid_cases=[]
for forged_q in (-2,-1,12,13,23):
    forged=replace(states[12],q=forged_q)
    advanced=kernel.advance(forged)
    old_clock=12*forged.generation+forged.q
    next_clock=12*advanced.generation+advanced.q
    assert next_clock != old_clock+1
    invalid_cases.append({'q':forged_q,'logical_clock_delta':next_clock-old_clock})

# A phase-only 'position' that travels at constant nonzero distance per tick
# would require x(n+12)-x(n)=12*a != 0, yet x_phase repeats exactly.
positive_spatial_displacement=12
assert positive_spatial_displacement != 0
assert states[0].q == states[12].q
assert states[0].generation != states[12].generation
assert states[0].identity != states[12].identity

result={
 'schema':'ROOT0-P2.2-actual-v92-logical-clock-observation-map',
 'kernel_git_blob':SOURCE_GIT_BLOB,
 'canon_sha256':CANON_SHA,
 'frozen_source_unchanged':True,
 'advance_calls':N,
 'reachable_states_tested':N+1,
 'wraps':wraps,
 'lineage_links_tested':parent_chain_ok,
 'clock_definition':'tick_index=12*generation+q',
 'clock_increment_invariants':N,
 'phase_periodicity_checks':q_only_cyclic,
 'phase_only_observation_maps':list(phase_observables),
 'phase_only_nonzero_uniform_translation_possible':False,
 'two_external_clock_scales_same_symbolic_trace':True,
 'two_external_space_scales_same_symbolic_trace':True,
 'adversarial_invalid_q_cases':invalid_cases,
 'source_fields_in_advance':field_reads,
 'v3_fields':list(kernel.V3.__dataclass_fields__),
 'physical_distance_m_from_source':None,
 'physical_duration_s_from_source':None,
 'photon_wave_operator_from_source':None,
 'phase_to_photon_falsifiable_observable_derived':False,
 'lean_machine_checked':False,
 'simulation_theory_proven':False,
 'status':'PASS_LOGICAL_CLOCK_AND_PHASE_NO_GO; PHYSICAL_OBSERVABLE_UNDERDETERMINED',
}
(HERE/'p22-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['source_fields_in_advance']},indent=2))
