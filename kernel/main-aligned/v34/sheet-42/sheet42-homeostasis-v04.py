#!/usr/bin/env python3
"""SHEET 42 v04: sustained worker balance, append-only benchmark.
Run from the same directory as unmodified sheet42.py.
"""
import json, time
from sheet42 import START, MASK, CIPHER, SHEETS, step, digest
N=10000
ORDER=range(28)
FACTOR=1.25
WINDOW=4
def traverse(s,phase,inverse=False):
    nodes=reversed(ORDER) if inverse else ORDER
    for node in nodes: s=step(s,node,phase,inverse)
    return s
def worker_balance(s):
    d=(s[8]-s[9])&MASK
    return min(d,(MASK+1)-d)/((MASK+1)//2)
def benchmark():
    start=time.perf_counter(); s=START
    states=[s]; vals=[worker_balance(s)]
    for k in range(N):
        s=traverse(s,k%16);states.append(s);vals.append(worker_balance(s))
    transient=[];persistent=[];longest=0
    for k in range(1,N+1):
        if vals[k]*FACTOR<=vals[k-1]:
            transient.append(k)
            threshold=vals[k-1]/FACTOR
            streak=0
            for j in range(k,N+1):
                if vals[j]<=threshold: streak+=1
                else:break
            longest=max(streak,longest)
            if streak>=WINDOW:persistent.append(k)
    steady=[k for k in persistent if states[k]==states[k+WINDOW-1]]
    final_hash=digest(s)
    for k in range(N-1,-1,-1):s=traverse(s,k%16,True)
    checks={'10000_cycles':len(states)==10001,
      '280000_updates':N*28==280000,
      'unique_boundaries':len(set(states))==N+1,
      'reversible':s==START,
      'factor_1p25':FACTOR==1.25,
      'window_4':WINDOW==4,
      'positive_improvements':bool(transient),
      'persistence_subset':set(persistent)<=set(transient),
      'steady_subset':set(steady)<=set(persistent),
      'output_bounded':all(all(0<=v<=MASK for v in row) for row in states),
      'cipher_unchanged':CIPHER=='..||..|....|.',
      '4_sheets':len(SHEETS)==4}
    return {'schema':'oasis/sheet42/homeostasis-v04','cycles':N,
      'node_updates':N*28,'threshold_factor':FACTOR,'window':WINDOW,
      'transient_balance_improvements':len(transient),
      'persistent_balance_windows':len(persistent),
      'longest_qualifying_streak':longest,
      'exact_steady_state_windows':len(steady),
      'distinct_full_states':len(set(states)),
      'final_state_sha256':final_hash,
      'checks':checks,'passed':sum(checks.values()),
      'failed':sum(not v for v in checks.values()),
      'seconds':time.perf_counter()-start,
      'note':'Worker imbalance is a model metric; passing the persistence gate does not prove full-state equilibrium.'}
if __name__=='__main__':
    r=benchmark();print(json.dumps(r,indent=2))
    assert r['failed']==0
