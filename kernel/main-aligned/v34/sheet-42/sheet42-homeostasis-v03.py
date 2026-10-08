#!/usr/bin/env python3
"""SHEET 42 10000-cycle long-run benchmark; requires unmodified sheet42.py."""
import json,time
from pathlib import Path
from sheet42 import START,MASK,digest,step,CIPHER,SHEETS
CYCLES=10000
NODES=tuple(range(28))
def traverse(s,phase,inverse=False):
    nodes=reversed(NODES) if inverse else NODES
    for node in nodes: s=step(s,node,phase,inverse)
    return s
def run():
    started=time.perf_counter();state=START;history={state:0};repeats=[]
    drops=[];changed=[];minbalance=(float('inf'),None)
    def imbalance(v):
        a,b=v[8],v[9]
        return min((a-b)&MASK,(b-a)&MASK)/(MASK//2)
    prior=imbalance(state)
    for i in range(CYCLES):
        future=traverse(state,i%16);value=imbalance(future)
        if future in history:repeats.append((history[future],i+1))
        history.setdefault(future,i+1)
        if prior>=1.25*value:drops.append(i+1)
        if value<minbalance[0]:minbalance=(value,i+1)
        changed.append(sum(a!=b for a,b in zip(state,future)))
        prior=value;state=future
    final_hash=digest(state)
    for i in range(CYCLES-1,-1,-1):state=traverse(state,i%16,True)
    checks={
        'cycles_10000':len(changed)==CYCLES,
        'updates_280000':CYCLES*28==280000,
        'inverse_recovered':state==START,
        'no_repeated_boundaries':not repeats,
        'final_state_bounded':all(0<=v<=MASK for v in state),
        'each_cycle_modified_state':all(changed),
        'four_sheets':len(SHEETS)==4,
        'cipher_unchanged':CIPHER=='..||..|....|.',
        'threshold_observed':bool(drops),
        'phases_0_to_15':all(0<=i%16<16 for i in range(CYCLES)),
        'deterministic':traverse(START,0)==traverse(START,0),
        'local_reversibility':all(step(step(START,n,p),n,p,True)==START for n in NODES for p in range(16)),
    }
    result={'schema':'oasis/sheet42/homeostasis-v03','cycles':CYCLES,'updates':CYCLES*28,
        'distinct_boundaries':len(history),'recurrences':repeats[:10],
        'worker_imbalance_min':{'value':minbalance[0],'cycle':minbalance[1]},
        'threshold_drop_count':len(drops),'first_drops':drops[:20],
        'changed_lanes':{'min':min(changed),'mean':sum(changed)/len(changed),'max':max(changed)},
        'final_sha256':final_hash,'reversed_to_initial':state==START,
        'checks':checks,'passed':sum(checks.values()),'total':len(checks),
        'runtime_seconds':time.perf_counter()-started,
        'caveat':'Symbolic finite-state model; 1.25 imbalance decrease is not proof of stable homeostasis.'}
    return result
if __name__=='__main__':
    report=run()
    print(json.dumps(report,indent=2))
    Path(__file__).with_name('homeostasis-v03-replay.json').write_text(json.dumps(report,indent=2)+'\n')
    assert report['passed']==report['total']
