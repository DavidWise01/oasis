#!/usr/bin/env python3
"""AETHER-100: causal, fresh-evidence reauthorization under drift.
Synthetic Bernoulli observations only; labels of true regimes never enter policy.
"""
from pathlib import Path
from functools import lru_cache
import csv, json
import numpy as np
from scipy.stats import beta

ROOT=Path(__file__).resolve().parent
REGIMES=('abrupt_recovery','repeat_hazard','decoy')
POLICIES=('stale','fresh3','fresh5')
TRAIN=range(100001,100041)
TEST=range(100201,100281)
T=100; AUDIT=140; SENT=80; ACTIONS=150
ALPHA=.05; LIMIT=.02

def write_csv(name,rows):
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

@lru_cache(maxsize=4096)
def cp_upper(f,n):
    return 1. if n<=0 or f>=n else float(beta.ppf(1-ALPHA,f+1,n-f))

def environment(seed,regime):
    off={'abrupt_recovery':0,'repeat_hazard':100000,'decoy':200000}[regime]
    rng=np.random.default_rng(seed+off)
    # Periodic reset points are evaluator-known, not visible to the controllers.
    risk=np.full(T,.003)
    danger=np.zeros(T,dtype=int)
    sensor_mean=np.zeros(T)
    if regime=='abrupt_recovery':
        risk[28:53]=.078; danger[28:53]=1; sensor_mean[28:53]=2.7
        recoveries=[53]
    elif regime=='repeat_hazard':
        risk[23:41]=.068; risk[57:77]=.083
        danger[23:41]=1;danger[57:77]=1
        sensor_mean[23:41]=2.7;sensor_mean[57:77]=2.7
        recoveries=[41,77]
    else:
        sensor_mean[28:53]=2.7
        recoveries=[53]
    a=rng.binomial(AUDIT,risk)
    # Independent sentinel risk samples (charge for every visible sensor)
    s=rng.normal(sensor_mean,1.)
    outcomes=rng.binomial(ACTIONS,risk)
    return risk,danger,a,s,outcomes,recoveries

def controller(seed,regime,policy,with_ticks=False):
    risk,truth,a,s,outcomes,recovery_points=environment(seed,regime)
    recent=[];fresh=[];suspended=False;previous=False;events=[]
    rows=[]
    for i in range(T):
        error=int(a[i]);recent=(recent+[error])[-5:]
        rolling_bound=cp_upper(sum(recent),len(recent)*AUDIT)
        sensor_alert=bool(s[i]>=2.5 and error>=3)
        if sensor_alert:
            suspended=True;fresh=[]
            events.append(('revoke',i))
        if suspended:
            fresh.append(error)
            n={'stale':0,'fresh3':3,'fresh5':5}[policy]
            if policy=='stale':
                # Flawed old-history gate: new quiet tick, but historical calibration retained.
                release=(error<=2 and s[i]<1.5 and rolling_bound<=LIMIT)
            else:
                release=(len(fresh)>=n and
                         cp_upper(sum(fresh),len(fresh)*AUDIT)<=LIMIT and
                         all(x<=2 for x in fresh[-2:]) and s[i]<1.5)
            if release:
                suspended=False;fresh=[];events.append(('reauthorize',i))
        # Suspended state overrides the otherwise permissive rolling controller.
        # Fresh policies use their fresh certificate at release, even when the
        # historical rolling bound still reflects the recently ended hazard.
        if policy=='stale':
            permit=(not suspended and rolling_bound<=LIMIT)
        else:
            permit=bool(not suspended and (rolling_bound<=LIMIT or bool(events and events[-1]==('reauthorize',i))))
        # No retrospective edits: this tick's evidence precedes this tick's action.
        tick=dict(regime=regime,seed=seed,policy=policy,tick=i+1,true_unsafe=int(truth[i]),
                  audit_errors=error,sensor_signal=round(float(s[i]),5),sensor_alarm=int(sensor_alert),
                  rolling_upper=round(rolling_bound,6),suspended=int(suspended),
                  action='ACT' if permit else 'HOLD',
                  wrong=int(outcomes[i]) if permit else 0,
                  unsafe_auth=int(permit and truth[i]),
                  safe_hold=int(not permit and not truth[i]),
                  hold_actions=0 if permit else ACTIONS,
                  sensor_cost=.2,audit_label_cost=AUDIT*.01)
        rows.append(tick)
        previous=suspended
    total_wrong=sum(x['wrong'] for x in rows)
    total_hold=sum(x['hold_actions'] for x in rows)
    cost=10*total_wrong+.05*total_hold+sum(x['sensor_cost']+x['audit_label_cost'] for x in rows)
    delays=[]
    for onset in recovery_points:
        next_hazard=next((j for j in range(onset+1,T) if truth[j]),T)
        first=next((j for j in range(onset,next_hazard) if rows[j]['action']=='ACT'),None)
        if first is not None:delays.append(first-onset)
        else:delays.append(next_hazard-onset)
    changes=sum(rows[i]['action']!=rows[i-1]['action'] for i in range(1,T))
    result=dict(regime=regime,seed=seed,policy=policy,cost=round(cost,2),wrong=total_wrong,
                unsafe_auth=sum(x['unsafe_auth'] for x in rows),safe_holds=sum(x['safe_hold'] for x in rows),
                authorized_ticks=sum(x['action']=='ACT' for x in rows),chattering=changes,
                revocations=sum(x[0]=='revoke' for x in events),
                reauths=sum(x[0]=='reauthorize' for x in events),
                mean_recovery_delay=round(float(np.mean(delays)),3))
    return (result,rows) if with_ticks else result

def aggregate(records):
    out=[]
    for regime in (*REGIMES,'ALL'):
        for policy in POLICIES:
            z=[x for x in records if x['policy']==policy and (regime=='ALL' or x['regime']==regime)]
            out.append(dict(regime=regime,policy=policy,cases=len(z),cost=round(sum(x['cost'] for x in z),2),
              wrong=sum(x['wrong'] for x in z),unsafe_auth=sum(x['unsafe_auth'] for x in z),
              safe_holds=sum(x['safe_holds'] for x in z),authorized_ticks=sum(x['authorized_ticks'] for x in z),
              chattering=sum(x['chattering'] for x in z),mean_recovery_delay=round(float(np.mean([x['mean_recovery_delay'] for x in z])),3)))
    return out

def main():
    dev=[controller(seed,r,p) for r in REGIMES for seed in TRAIN for p in POLICIES]
    dev_summary=aggregate(dev)
    # Predeclared choice: of fresh3 and fresh5 select lower development cost,
    # but only if unsafe authorization count does not exceed the stale baseline
    # and safe holds are no more than 10% higher.
    stale=next(x for x in dev_summary if x['regime']=='ALL' and x['policy']=='stale')
    choices=[]
    for p in ('fresh3','fresh5'):
        z=next(x for x in dev_summary if x['regime']=='ALL' and x['policy']==p)
        eligible=z['unsafe_auth']<=stale['unsafe_auth'] and z['safe_holds']<=stale['safe_holds']*1.1
        choices.append(dict(policy=p,eligible=eligible,dev_cost=z['cost'],unsafe_auth=z['unsafe_auth'],safe_holds=z['safe_holds']))
    write_csv('development_options.csv',choices)
    eligible=[x for x in choices if x['eligible']]
    chosen=min(eligible,key=lambda x:(x['dev_cost'],x['policy']))['policy'] if eligible else None
    records=[];sample=[]
    for regime in REGIMES:
        for seed in TEST:
            for policy in POLICIES:
                result,ticks=controller(seed,regime,policy,with_ticks=True)
                records.append(result)
                if seed==TEST.start:sample.extend(ticks)
    write_csv('seed_results.csv',records)
    write_csv('trace_samples.csv',sample)
    summary=aggregate(records);write_csv('results.csv',summary)
    z={p:next(x for x in summary if x['regime']=='ALL' and x['policy']==p) for p in POLICIES}
    selected=z[chosen] if chosen else None
    # Acceptance tested ONCE on fresh seeds; compare unsafe, safe holds, cost
    # and recovery delay against the stale-history comparator.
    accepted=bool(chosen and selected['unsafe_auth']<=z['stale']['unsafe_auth'] and
       selected['safe_holds']<=1.05*z['stale']['safe_holds'] and
       selected['cost']<=z['stale']['cost'] and
       selected['mean_recovery_delay']<=z['stale']['mean_recovery_delay'])
    manifest=dict(bound='AETHER-100',status='PASS' if accepted else 'FAIL',
       chosen_policy=chosen,phase_percent=62.5 if accepted else 50.,
       train_seeds=[TRAIN.start,TRAIN.stop-1],holdout_seeds=[TEST.start,TEST.stop-1],
       acceptance=dict(unsafe_auth_max='stale',safe_hold_multiplier_max=1.05,
          cost_max='stale',recovery_delay_max='stale'),
       limitations=['Synthetic Bernoulli risk; no real-world certification',
         'Risk truth and recovery time visible only to evaluator',
         'Fixed-time Clopper-Pearson bound is not anytime-valid',
         'Single-tick reauthorization using a fresh certificate must remain conditioned on subsequent audits'])
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'manifest':manifest,'all':[x for x in summary if x['regime']=='ALL']},indent=2))
if __name__=='__main__':main()