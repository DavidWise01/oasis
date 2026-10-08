#!/usr/bin/env python3
"""SHEET 42 v07: independent relative phase audit of unchanged v05 toroidal scheduler."""
import cmath,importlib.util,json,math,time
from pathlib import Path
from sheet42 import START,digest
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("v05",HERE/"sheet42-toroid-v05.py")
v05=importlib.util.module_from_spec(spec);spec.loader.exec_module(v05)
TURNS=10;PERIOD=360;LANES=5;PHASES=16
def phases_at(sector):
    return tuple(((sector//(PERIOD//PHASES))+ring)%PHASES for ring in range(LANES))
def coherence(row):
    return abs(sum(cmath.exp(2j*math.pi*p/PHASES) for p in row))/len(row)
def benchmark():
    started=time.perf_counter()
    ph=[phases_at(s) for s in range(PERIOD)]
    co=[coherence(q) for q in ph]
    exact=sum(len(set(q))==1 for q in ph)
    offsets={tuple((q[i]-q[0])%PHASES for i in range(LANES)) for q in ph}
    state=START;seen={state};duplicates=0;boundaries=[]
    for t in range(TURNS*PERIOD):
        state=v05.tick(state,t)
        duplicates+=int(state in seen);seen.add(state)
        if (t+1)%PERIOD==0:boundaries.append(digest(state))
    final_hash=digest(state)
    for t in range(TURNS*PERIOD-1,-1,-1):state=v05.tick(state,t,True)
    checks={
        'source_v05':v05.RINGS==LANES and v05.TICKS==PERIOD,
        'all_lane_phases_present':all(len(q)==LANES for q in ph),
        'phase_domain':all(0<=p<PHASES for q in ph for p in q),
        'relative_offsets_invariant':len(offsets)==1,
        'no_five_way_phase_lock':exact==0,
        'coherence_less_than_one':max(co)<1-1e-12,
        'coherence_constant':max(co)-min(co)<1e-12,
        'ten_turns':len(boundaries)==TURNS,
        'no_full_state_recursion':duplicates==0,
        'distinct_turn_boundaries':len(set(boundaries))==TURNS,
        'exact_inverse':state==START,
        'time_literal_unchanged':'1^-1/360' in v05.LITERAL}
    return {'schema':'oasis/sheet42/relative-phase-v07','turns':TURNS,'sectors':PERIOD,
        'node_updates':TURNS*PERIOD*28,'phase_at_zero':ph[0],
        'phase_offsets':[list(x) for x in sorted(offsets)],
        'five_way_locks':exact,'coherence_min':min(co),'coherence_max':max(co),
        'unique_states':len(seen),'state_repetitions':duplicates,
        'recovered_exactly':state==START,'final_hash':final_hash,
        'checks':checks,'passed':sum(checks.values()),'total':len(checks),
        'elapsed_seconds':time.perf_counter()-started,
        'limitation':'Constant prescribed phase offsets are not dynamically entrained or physical particle synchronization.'}
if __name__=='__main__':
    r=benchmark();print(json.dumps(r,indent=2))
    assert r['passed']==r['total']
