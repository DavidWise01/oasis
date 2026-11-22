#!/usr/bin/env python3
"""AETHER-097: deterministic context contradiction and permission revocation benchmark.
Synthetic independent audit roots; live controllers never see true regimes.
"""
import csv,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
ROOT=Path(__file__).resolve().parent
SEEDS=range(97201,97281)
T=100;AUD=140;SENT=80;ACTIONS=150;ALPHA=.05
POLICIES=('sticky','instantaneous','contradiction')
def upper(f,n):
    return 1. if not n or f>=n else float(beta.ppf(1-ALPHA,int(f)+1,int(n-f)))
def save(name,rows):
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def episode(seed,kind):
    rng=np.random.default_rng(seed+(0 if kind=='switch' else 100000))
    p=[]
    for t in range(T):
        if kind=='switch':risk=.075 if 20<=t<40 or 60<=t<80 else .003
        else:risk=.075 if 20<=t<40 else (.018 if 60<=t<80 else .003)
        p.append(risk)
    arr=np.array(p)
    return arr,rng.binomial(AUD,arr),rng.binomial(SENT,arr),rng.binomial(ACTIONS,arr)
def evaluate(seed,kind,policy):
    p,a,s,w=episode(seed,kind)
    recent=[];permission=False;quiet=0;rows=[];prior=False
    for t in range(T):
        error=int(a[t]);recent=(recent+[error])[-5:]
        instant=bool(error>=7 or (len(recent)>=2 and recent[-1]+recent[-2]>=13))
        if policy=='instantaneous':permission=instant
        else:
            if instant:permission=True;quiet=0
            elif permission:
                quiet=quiet+1 if error<=3 else 0
                if policy=='contradiction' and error<=3:permission=False;quiet=0
                elif quiet>=8:permission=False;quiet=0
        revoked=bool(prior and not permission)
        history=a[max(0,t-4):t+1];bound=upper(int(history.sum()),len(history)*AUD)
        uncertain=(bound<=.045 and bound>=.015)
        probe=bool(permission and uncertain)
        alarm=bool(probe and s[t]>=3)
        allow=bool(bound<=.02 and not alarm)
        wrong=int(w[t]) if allow else 0
        withheld=0 if allow else ACTIONS
        labels=AUD+SENT*int(probe)
        rows.append(dict(seed=seed,scenario=kind,tick=t+1,policy=policy,actual_burst=int(p[t]>=.07),
          audit_errors=error,instant_signal=int(instant),context_permission=int(permission),
          revoke=int(revoked),sentinel_probe=int(probe),authorized=int(allow),wrong=wrong,
          withheld=withheld,labels=labels,cost=round(10*wrong+.05*withheld+.01*labels,2)))
        prior=permission
    return rows
def main():
    rows=[]
    for kind in ('switch','decoy'):
        for seed in SEEDS:
            for policy in POLICIES:rows.extend(evaluate(seed,kind,policy))
    save('tick_audit.csv',rows)
    summary=[]
    for kind in ('switch','decoy','ALL'):
        for policy in POLICIES:
            z=[r for r in rows if r['policy']==policy and (kind=='ALL' or r['scenario']==kind)]
            false=sum(r['context_permission'] and not r['actual_burst'] for r in z)
            actual=sum(not r['actual_burst'] for r in z)
            positive=sum(r['context_permission'] and r['actual_burst'] for r in z)
            burst=sum(r['actual_burst'] for r in z)
            summary.append(dict(scenario=kind,policy=policy,ticks=len(z),nonburst_ticks=actual,
               stale_or_false_permission=false,false_permission_pct=round(100*false/actual,3),
               burst_recall_pct=round(100*positive/burst,3),revocations=sum(r['revoke'] for r in z),
               wrong_actions=sum(r['wrong'] for r in z),sentinel_probes=sum(r['sentinel_probe'] for r in z),
               total_cost=round(sum(r['cost'] for r in z),2)))
    save('results.csv',summary)
    counter=[]
    for seed in SEEDS:
        for kind in ('switch','decoy'):
            for policy in POLICIES:
                z=[r for r in rows if r['seed']==seed and r['scenario']==kind and r['policy']==policy]
                for start in (40,80) if kind=='switch' else (40,):
                    window=z[start:start+8]
                    first=next((r['tick']-1-start for r in window if not r['context_permission']),None)
                    counter.append(dict(seed=seed,scenario=kind,policy=policy,transition_tick=start+1,
                      revocation_delay=first if first is not None else 8,
                      stale_ticks_in_8=sum(r['context_permission'] for r in window),
                      observed_audit_errors='|'.join(str(r['audit_errors']) for r in window)))
    save('counterexamples.csv',counter)
    def metric(policy,key):return next(r[key] for r in summary if r['scenario']=='ALL' and r['policy']==policy)
    ok=(metric('contradiction','false_permission_pct')<=1.0 and
        metric('contradiction','false_permission_pct')<metric('sticky','false_permission_pct') and
        metric('contradiction','total_cost')<=metric('sticky','total_cost'))
    manifest=dict(bound='AETHER-097',status='PASS' if ok else 'FAIL',seed_range=[min(SEEDS),max(SEEDS)],
     scenarios=['switch','decoy'],tick_count=T,phase_pct=25 if ok else 12.5,
     acceptance='false permissions <=1%, fewer than sticky, no greater cost than sticky',
     limitations=['Synthetic known Bernoulli mechanisms','Untrained heuristic context signal',
                  'No independent classification guarantee'])
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'manifest':manifest,'summary':summary},indent=2))
if __name__=='__main__':main()
