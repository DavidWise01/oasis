#!/usr/bin/env python3
"""AETHER-090 | synthetic sentinel drift and conditional reauthorization.
Run with numpy and scipy. Separate sentinel, audit and decision observations.
"""
import csv,json
from pathlib import Path
import numpy as np
from scipy.stats import beta,binom
OUT=Path(__file__).resolve().parent
SEEDS=range(90001,90021);TICKS=90;AUDIT=140;SENTINEL=80
RECENT=5;ALPHA=.05;TARGET=.02
THRESHOLD=int(binom.isf(.005,SENTINEL,.003))+1

def bound(w,n):
    return 1. if n==0 or w>=n else float(beta.ppf(1-ALPHA,w+1,n-w))
def regime(t):
    return 'safe_initial' if t<=30 else ('unsafe_shift' if t<=60 else 'safe_recovery')
def risk(t):
    return .075 if 30<t<=60 else .003
def save(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
records=[]
for seed in SEEDS:
    rng=np.random.default_rng(seed);recent=[];post_alarm=[];status='active'
    for t in range(1,TICKS+1):
        p=risk(t);alarm_errors=int(rng.binomial(SENTINEL,p))
        audit_errors=int(rng.binomial(AUDIT,p))
        recent=(recent+[(audit_errors,AUDIT)])[-RECENT:]
        alarm=alarm_errors>=THRESHOLD
        if alarm: status='suspended';post_alarm=[]
        if status=='suspended':
            post_alarm=(post_alarm+[(audit_errors,AUDIT)])[-RECENT:]
            if len(post_alarm)>=RECENT and bound(sum(a for a,n in post_alarm),sum(n for a,n in post_alarm))<=TARGET and not alarm:status='active'
        radius=bound(sum(a for a,n in recent),sum(n for a,n in recent))
        rolling=radius<=TARGET
        sentinel=rolling and status=='active' and not alarm
        wrong=int(rng.binomial(150,p))
        for policy,authorized in [('rolling_only',rolling),('sentinel_reauthorize',sentinel)]:
            records.append(dict(seed=seed,tick=t,regime=regime(t),true_risk=p,policy=policy,
              sentinel_errors=alarm_errors,sentinel_alarm=int(alarm),audit_errors=audit_errors,
              authorize=int(authorized),wrong_if_authorized=wrong if authorized else 0,
              withheld=0 if authorized else 150,actions=150 if authorized else 0,
              sentinel_labels=SENTINEL if policy=='sentinel_reauthorize' else 0,
              audit_labels=AUDIT,rolling_bound=round(radius,5),state=status if policy=='sentinel_reauthorize' else 'rolling'))
save('tick_audit.csv',records)
results=[]
for policy in ('rolling_only','sentinel_reauthorize'):
    for region in ('safe_initial','unsafe_shift','safe_recovery','ALL'):
        sample=[r for r in records if r['policy']==policy and (r['regime']==region or region=='ALL')]
        a=sum(r['authorize'] for r in sample);w=sum(r['wrong_if_authorized'] for r in sample)
        actions=sum(r['actions'] for r in sample);withheld=sum(r['withheld'] for r in sample)
        labels=sum(r['audit_labels']+r['sentinel_labels'] for r in sample)
        results.append(dict(policy=policy,regime=region,ticks=len(sample),authorized_ticks=a,
          authorization_rate=round(a/len(sample),4),wrong_authorizations=w,
          authorized_actions=actions,withheld_actions=withheld,
          conditional_error=round(w/actions,5) if actions else '',
          labels=labels,illustrative_cost=round(10*w+.05*withheld+.01*labels,2)))
save('results.csv',results)
events=[]
for seed in SEEDS:
    s=[r for r in records if r['policy']=='sentinel_reauthorize' and r['seed']==seed]
    alarms=[r['tick'] for r in s if 31<=r['tick']<=60 and r['sentinel_alarm']]
    resume=[r['tick'] for r in s if r['tick']>=61 and r['authorize']]
    first=min(alarms) if alarms else None;again=min(resume) if resume else None
    events.append(dict(seed=seed,first_shift_alarm=first,alarm_delay=first-31 if first else '',
      first_reauthorized_after_recovery=again,recovery_delay=again-61 if again else '',
      false_alarms_safe=sum(r['sentinel_alarm'] for r in s if r['regime']!='unsafe_shift')))
save('events.csv',events)
(OUT/'manifest.json').write_text(json.dumps(dict(bound='AETHER-090',seed_range=[90001,90020],ticks=TICKS,
  safe_risk=.003,unsafe_risk=.075,risk_target=TARGET,sentinel_labels=SENTINEL,
  audit_labels=AUDIT,rolling_window=RECENT,sentinel_alarm_threshold=THRESHOLD,
  caveat='Simulation only. Fixed-time binomial bounds do not guarantee safety after regime shift.'),indent=2)+'\n')
print(*results,sep='\n')
