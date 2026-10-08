#!/usr/bin/env python3
"""SHEET 42 append-only v02 1024-cycle stress test (requires sheet42.py)."""
import json,random,time
from pathlib import Path
from sheet42 import INITIAL,NODE_COUNT,MASK,walk,rewind,digest

CYCLES=1024
ORDER=tuple(range(NODE_COUNT))
def run(cycles,order=ORDER,phase_at=lambda i:i%16,start=INITIAL):
    s=start;states=[];phases=[]
    for i in range(cycles):
        p=phase_at(i);s,_=walk(start=s,order=order,phase=p)
        states.append(s);phases.append(p)
    return s,states,phases
def reverse(s,phases,order=ORDER):
    for p in reversed(phases):s=rewind(s,order,p)
    return s
def benchmark():
    start=time.perf_counter()
    final,states,phases=run(CYCLES);history=[INITIAL]+states
    changed=[sum(a!=b for a,b in zip(history[i],history[i+1])) for i in range(CYCLES)]
    other,_,_=run(CYCLES,order=ORDER[::-1])
    fixed,_,_=run(CYCLES,phase_at=lambda i:0)
    rng=random.Random(42);seed=tuple(rng.randrange(MASK+1) for _ in range(10))
    trial,_,trial_phases=run(257,start=seed)
    previous=digest(INITIAL);state=INITIAL;ledger_ok=True;records=0
    for c in range(10):
        state,ledger=walk(start=state,phase=c%16)
        ledger_ok &= ledger[0]['before_sha256']==previous
        ledger_ok &= all(ledger[i]['after_sha256']==ledger[i+1]['before_sha256'] for i in range(27))
        previous=digest(state);records+=len(ledger)
    checks={
        '1024_cycles':len(states)==CYCLES,
        'all_boundaries_distinct':len(set(history))==CYCLES+1,
        'each_cycle_changes_state':all(changed),
        'exact_reverse':reverse(final,phases)==INITIAL,
        'deterministic_replay':run(CYCLES)[0]==final,
        'order_matters':other!=final,
        'phase_schedule_matters':fixed!=final,
        '257_cycle_seed_reverse':reverse(trial,trial_phases)==seed,
        'continuous_hash_ledger':ledger_ok,
        '280_ledger_records':records==280,
        'state_bounded':all(all(0<=x<=MASK for x in s) for s in history),
        'all_4_sheets_visited':set(n%4 for n in ORDER)==set(range(4))
    }
    return {'schema':'oasis/sheet-42/repeated-travel-v02',
        'cycles':CYCLES,'node_updates':CYCLES*NODE_COUNT,
        'unique_boundary_states':len(set(history)), 'repeated_boundaries':CYCLES+1-len(set(history)),
        'mean_words_changed':sum(changed)/CYCLES,'min_words_changed':min(changed),'max_words_changed':max(changed),
        'final_state_sha256':digest(final),'checks':checks,
        'passed':sum(checks.values()),'failed':sum(not v for v in checks.values()),
        'elapsed_seconds':time.perf_counter()-start,
        'limitation':'finite-state simulation, no physical quantum claim'}
if __name__=='__main__':
    result=benchmark()
    print(json.dumps(result,indent=2))
    assert result['failed']==0
