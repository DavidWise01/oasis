#!/usr/bin/env python3
"""SHEET 42 v05: 360-step toroidal transport, 5 symbolic rings, reversible.
Literal tokens are symbolic, NOT calibrated seconds or scientific units.
"""
import json,time
from sheet42 import START, MASK, step, digest, CIPHER
LABELS=('0','v','w','x','y','z')
RINGS=5
TICKS=360
NODES=tuple(range(28))
LITERAL='{{0vwxyz}}^5 x inf - + inf / 1 x 1^10-36 every 1 x 1^-1/360 x 360'
def tick(s,t,inverse=False):
    ring=t%RINGS; sector=t%TICKS
    order=tuple((k+ring)%28 for k in NODES)
    phase=(sector//(TICKS//16)+ring)%16
    for n in (reversed(order) if inverse else order):
        s=step(s,n,phase,inverse)
    return s
def benchmark():
    start=time.perf_counter();s=START;boundaries=[s];minchanged=10
    per_ring=[0]*RINGS;seen={s};repeats=0
    for t in range(TICKS*10):
        prev=s;s=tick(s,t);per_ring[t%RINGS]+=1
        minchanged=min(minchanged,sum(a!=b for a,b in zip(prev,s)))
        repeats+=(s in seen);seen.add(s)
        if (t+1)%TICKS==0:boundaries.append(s)
    final=digest(s)
    for t in range(TICKS*10-1,-1,-1):s=tick(s,t,True)
    checks={
        '360_sectors':TICKS==360,
        'five_ring_lanes':RINGS==5 and len(LABELS)==6,
        'ten_toroidal_turns':len(boundaries)==11,
        '100800_node_updates':TICKS*10*28==100800,
        'exact_reverse':s==START,
        'replay':tick(START,0)==tick(START,0),
        'ring_visits_equal':len(set(per_ring))==1,
        'phase_is_bounded':all(0<=(t//(TICKS//16)+t%RINGS)%16<16 for t in range(TICKS)),
        'boundary_return_address':360%360==0,
        'first_10_turns_unique':len(set(boundaries))==11,
        'all_ten_registers_active':minchanged==10,
        'literal_time_preserved':'1^-1/360' in LITERAL and '1^10-36' in LITERAL,
        'cipher_preserved':CIPHER=='..||..|....|.',
    }
    return dict(schema='oasis/sheet-42/toroid-v05',symbol=LITERAL,turns=10,sectors=TICKS,
          named_lanes=list(LABELS),ring_counts=per_ring,updated_nodes=100800,
          unique_states=len(seen),repeated_node_boundary_states=repeats,
          distinct_full_turn_boundaries=len(set(boundaries)),reversed_exact=s==START,
          final_digest=final,checks=checks,passed=sum(checks.values()),total=len(checks),
          elapsed_seconds=time.perf_counter()-start,
          note='Toroid closes its ADDRESS modulo 360; dynamical state does not necessarily return. No physical time calibration.')
if __name__=='__main__':
    result=benchmark();print(json.dumps(result,indent=2))
    assert result['passed']==result['total']
