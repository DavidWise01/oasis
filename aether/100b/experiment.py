#!/usr/bin/env python3
"""AETHER-100B. Fresh, non-resetting post-revocation certificate.
Synthetic simulation only; hidden risk used solely to score outcomes.
"""
from pathlib import Path
import csv,json
from functools import lru_cache
import numpy as np
from scipy.stats import beta
ROOT=Path(__file__).resolve().parent
REGIMES=('abrupt_recovery','repeat_hazard','decoy')
POLICIES=('stale','fresh2','fresh2_quiet','fresh3')
DEVELOP=range(100301,100341)
HOLDOUT=range(100501,100581)
T=100;AUDIT=140;ACTIONS=150;ALPHA=.05;LIMIT=.02
@lru_cache(maxsize=8192)
def bound(errors,n):
    return 1. if n==0 or errors>=n else float(beta.ppf(1-ALPHA,errors+1,n-errors))
def save(name,rows):
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def environment(seed,regime):
    rng=np.random.default_rng(seed+{'abrupt_recovery':0,'repeat_hazard':100000,'decoy':200000}[regime]);r=np.full(T,.003);m=np.zeros(T)
    if regime=='abrupt_recovery':r[28:53]=.078;m[28:53]=2.7;recoveries=[53]
    elif regime=='repeat_hazard':r[23:41]=.068;r[57:77]=.083;m[23:41]=2.7;m[57:77]=2.7;recoveries=[41,77]
    else:m[28:53]=2.7;recoveries=[53]
    return r,rng.binomial(AUDIT,r),rng.normal(m,1.),rng.binomial(ACTIONS,r),recoveries
def run(seed,regime,policy,trace=False):
    risk,audit,sensor,outcomes,recoveries=environment(seed,regime)
    recent=[];fresh=[];suspended=False;certificate=False;events=[];rows=[]
    for t in range(T):
        e=int(audit[t]);recent=(recent+[e])[-5:];rolling=bound(sum(recent),len(recent)*AUDIT)
        alert=bool(sensor[t]>=2.5 and e>=3)
        # Revocation has priority over any previously issued permission.
        if alert:
            if not suspended:
                suspended=True;fresh=[];certificate=False;events.append(('revoke',t))
            # Repeated alerts do not reset the same suspended episode.
        if suspended:
            fresh=(fresh+[e])[-3:]
            if policy=='stale':
                ready=(e<=2 and sensor[t]<1.5 and rolling<=LIMIT)
            else:
                required=3 if policy=='fresh3' else 2
                window=fresh[-required:]
                ready=(len(window)==required and bound(sum(window),required*AUDIT)<=LIMIT
                      and sensor[t]<1.5 and not alert)
                if policy=='fresh2_quiet':ready=bool(ready and max(window)<=2)
            if ready:
                suspended=False;fresh=[];certificate=policy!='stale';events.append(('reauthorize',t))
        # Fresh certificate remains usable until the normal rolling bound recovers;
        # an alert always revokes it. This removes one-tick permission oscillation.
        if rolling<=LIMIT:certificate=False
        permit=bool(not suspended and (rolling<=LIMIT or certificate))
        rows.append(dict(seed=seed,regime=regime,tick=t+1,policy=policy,
            true_unsafe=int(risk[t]>.02),audit_errors=e,sensor=round(float(sensor[t]),5),
            sensor_alarm=int(alert),rolling_bound=round(rolling,6),suspended=int(suspended),
            fresh_certificate=int(certificate),action='ACT' if permit else 'HOLD',
            wrong=int(outcomes[t]) if permit else 0,unsafe_auth=int(permit and risk[t]>.02),
            safe_hold=int(not permit and risk[t]<=.02),withheld=0 if permit else ACTIONS))
    delays=[]
    for idx in recoveries:
        next_hazard=next((j for j in range(idx+1,T) if risk[j]>.02),T)
        first=next((j for j in range(idx,next_hazard) if rows[j]['action']=='ACT'),None)
        delays.append((first-idx) if first is not None else next_hazard-idx)
    wrong=sum(x['wrong'] for x in rows);withheld=sum(x['withheld'] for x in rows)
    return dict(regime=regime,seed=seed,policy=policy,wrong=wrong,
       unsafe_auth=sum(x['unsafe_auth'] for x in rows),safe_holds=sum(x['safe_hold'] for x in rows),
       authorized_ticks=sum(x['action']=='ACT' for x in rows),
       oscillations=sum(rows[i]['action']!=rows[i-1]['action'] for i in range(1,T)),
       recoveries=len(delays),delay_sum=sum(delays),
       sensor_revokes=sum(x[0]=='revoke' for x in events),
       cost=round(10*wrong+.05*withheld+T*(AUDIT*.01+.2),2)),rows
def aggregate(records):
    result=[]
    for regime in (*REGIMES,'ALL'):
        for p in POLICIES:
            z=[x for x in records if x['policy']==p and (regime=='ALL' or x['regime']==regime)]
            result.append(dict(regime=regime,policy=p,cases=len(z),cost=round(sum(x['cost'] for x in z),2),
                wrong=sum(x['wrong'] for x in z),unsafe_auth=sum(x['unsafe_auth'] for x in z),
                safe_holds=sum(x['safe_holds'] for x in z),authorized_ticks=sum(x['authorized_ticks'] for x in z),
                oscillations=sum(x['oscillations'] for x in z),
                mean_recovery_delay=round(sum(x['delay_sum'] for x in z)/sum(x['recoveries'] for x in z),3)))
    return result
def main():
    dev=[]
    for g in REGIMES:
        for seed in DEVELOP:
            for p in POLICIES:dev.append(run(seed,g,p)[0])
    ds=aggregate(dev);baseline=next(x for x in ds if x['regime']=='ALL' and x['policy']=='stale')
    candidate=[]
    for p in POLICIES[1:]:
        x=next(a for a in ds if a['regime']=='ALL' and a['policy']==p)
        eligible=(x['unsafe_auth']<=baseline['unsafe_auth'] and x['safe_holds']<=baseline['safe_holds']*1.05
           and x['cost']<=baseline['cost'] and x['mean_recovery_delay']<=baseline['mean_recovery_delay'])
        candidate.append(dict(policy=p,eligible=int(eligible),dev_cost=x['cost'],
           unsafe_auth=x['unsafe_auth'],safe_holds=x['safe_holds'],delay=x['mean_recovery_delay']))
    save('development_options.csv',candidate)
    eligible=[x for x in candidate if x['eligible']]
    selected=min(eligible,key=lambda x:(x['dev_cost'],x['policy']))['policy'] if eligible else None
    records=[];traces=[]
    for g in REGIMES:
        for seed in HOLDOUT:
            for p in POLICIES:
                result,ticks=run(seed,g,p);records.append(result)
                if seed==HOLDOUT.start:traces.extend(ticks)
    save('seed_results.csv',records);save('trace_samples.csv',traces)
    summary=aggregate(records);save('results.csv',summary)
    z={p:next(x for x in summary if x['regime']=='ALL' and x['policy']==p) for p in POLICIES}
    checked=z[selected] if selected else None
    passed=bool(checked and checked['unsafe_auth']<=z['stale']['unsafe_auth']
        and checked['safe_holds']<=z['stale']['safe_holds']*1.05 and checked['cost']<=z['stale']['cost']
        and checked['mean_recovery_delay']<=z['stale']['mean_recovery_delay'])
    manifest=dict(bound='AETHER-100B',status='PASS' if passed else 'FAIL',phase_percent=62.5 if passed else 50,
        development_seeds=[min(DEVELOP),max(DEVELOP)],holdout_seeds=[min(HOLDOUT),max(HOLDOUT)],
        selected=selected,criteria=['unsafe_auth <= stale','safe_holds <= 1.05 * stale',
        'cost <= stale','mean_recovery_delay <= stale'],caveats=['Synthetic independent Bernoulli audit roots',
        'Hidden risk and recovery times are evaluator-only','Fixed-time bounds not valid for future drifting risk'])
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'manifest':manifest,'development':candidate,'results':[x for x in summary if x['regime']=='ALL']},indent=2))
if __name__=='__main__':main()