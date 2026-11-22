#!/usr/bin/env python3
"""AETHER-099: revocation latency and early-shutdown cost, synthetic experiment."""
import csv,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
OUT=Path(__file__).resolve().parent
SEEDS=range(99001,99081)
KINDS=('abrupt','gradual','decoy')
T=100;AUD=140;ACTIONS=150
def upper(e,n):
    return 1. if n<=0 or e>=n else float(beta.ppf(.95,e+1,n-e))
def save(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def episode(seed,kind):
    rng=np.random.default_rng(seed+dict(abrupt=0,gradual=10000,decoy=20000)[kind])
    start=int(rng.integers(25,41));end=start+26
    risk=[];means=[]
    for t in range(T):
        j=t-start
        if kind=='abrupt':p=.065 if 0<=j<26 else .003
        elif kind=='gradual':p=.003+(.065-.003)*min(1.,j/8) if 0<=j<26 else .003
        else:p=.003
        risk.append(p);means.append(2.8 if 0<=j<26 else 0.)
    r=np.array(risk)
    return start,end,r,rng.binomial(AUD,r),rng.binomial(ACTIONS,r),rng.normal(means,1.)
def trial(seed,kind,policy):
    start,end,risk,audit,wrong,sensor=episode(seed,kind)
    recent=[];suspended=False;quiet=0;rows=[]
    for t in range(T):
        recent=(recent+[int(audit[t])])[-5:]
        bound=upper(sum(recent),len(recent)*AUD)
        alarm=False
        if policy=='sensor':
            alarm=bool(sensor[t]>=2.)
            if alarm:suspended=True;quiet=0
            elif suspended:
                quiet=quiet+1 if sensor[t]<1. else 0
                if quiet>=3:suspended=False;quiet=0
        act=bool(bound<=.02 and not suspended)
        rows.append(dict(seed=seed,scenario=kind,tick=t+1,shift_start=start+1,shift_end=end+1,policy=policy,
          actual_unsafe=int(risk[t]>.02),audit_errors=int(audit[t]),risk_upper=round(bound,6),
          sensor=round(float(sensor[t]),6),alarm=int(alarm),sensor_suspended=int(suspended),
          action='ACT' if act else 'HOLD',unsafe_authorized=int(act and risk[t]>.02),
          safe_withheld=int(not act and risk[t]<=.02),wrong=int(wrong[t]) if act else 0,
          withheld=0 if act else ACTIONS,evidence_cost=AUD*.01+(0.2 if policy=='sensor' else 0)))
    return rows
def main():
    rows=[r for kind in KINDS for seed in SEEDS for p in ('rolling','sensor') for r in trial(seed,kind,p)]
    save('tick_audit.csv',rows)
    summaries=[]
    for kind in (*KINDS,'ALL'):
        for p in ('rolling','sensor'):
            z=[x for x in rows if x['policy']==p and (kind=='ALL' or x['scenario']==kind)]
            w=sum(x['wrong'] for x in z);h=sum(x['withheld'] for x in z);e=sum(x['evidence_cost'] for x in z)
            summaries.append(dict(scenario=kind,policy=p,ticks=len(z),
              unsafe_authorized=sum(x['unsafe_authorized'] for x in z),
              safe_withheld=sum(x['safe_withheld'] for x in z),wrong=w,withheld_actions=h,
              sensor_alarms=sum(x['alarm'] for x in z),evidence_cost=round(e,1),
              total_cost=round(10*w+.05*h+e,1)))
    save('results.csv',summaries)
    events=[]
    for kind in KINDS:
        for seed in SEEDS:
            for p in ('rolling','sensor'):
                z=[r for r in rows if r['scenario']==kind and r['seed']==seed and r['policy']==p]
                onset=z[0]['shift_start']-1;end=z[0]['shift_end']-1
                danger=[r for r in z[onset:end] if r['actual_unsafe']]
                f=next((r['tick']-1-onset for r in danger if r['action']=='HOLD'),None)
                events.append(dict(scenario=kind,seed=seed,policy=p,onset_tick=onset+1,
                  first_unsafe_hold_delay='' if f is None else f,
                  unsafe_authorized=sum(r['unsafe_authorized'] for r in danger),
                  safe_withheld=sum(r['safe_withheld'] for r in z)))
    save('events.csv',events)
    z={r['policy']:r for r in summaries if r['scenario']=='ALL'}
    reduction=(z['rolling']['unsafe_authorized']-z['sensor']['unsafe_authorized'])/max(1,z['rolling']['unsafe_authorized'])
    added=z['sensor']['safe_withheld']-z['rolling']['safe_withheld']
    safe_ticks=sum(not r['actual_unsafe'] for r in rows if r['policy']=='sensor')
    accepted=(reduction>=.2 and z['sensor']['total_cost']<=z['rolling']['total_cost']
      and added<=.05*safe_ticks)
    manifest=dict(bound='AETHER-099',status='PASS' if accepted else 'FAIL',phase_percent=50 if accepted else 37.5,
      samples=len(rows),seed_range=[min(SEEDS),max(SEEDS)],unsafe_reduction=round(reduction,4),
      added_safe_holds=added,criteria={'unsafe_reduction_min':.2,'cost_increase_max':0,
      'added_safe_hold_fraction_max':.05},caution='Sensor is a simulated proxy and may shift without hazard; risk truth is evaluation-only.')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'manifest':manifest,'results':summaries},indent=2))
if __name__=='__main__':main()
