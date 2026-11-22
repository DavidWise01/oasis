#!/usr/bin/env python3
"""AETHER-091: paired synthetic subtle-drift value-of-warning experiment.
Requires numpy and scipy. No physical safety certification.
"""
from pathlib import Path
import csv,json
import numpy as np
from scipy.stats import beta,binom
P=Path(__file__).resolve().parent
SEEDS=range(91001,91041);TICKS=90;AUDIT=140;SENTINEL=80;ACTIONS=150
WINDOW=5;TARGET=.02;ALPHA=.05
SCENARIOS={'near_limit':(.003,.026,.003),'moderate':(.003,.038,.003),'stable_safe':(.003,.003,.003)}
THRESHOLD=int(binom.isf(.01,SENTINEL,.003))+1
def ub(w,n):return 1. if n==0 or w>=n else float(beta.ppf(1-ALPHA,w+1,n-w))
def save(name,rr):
    with (P/name).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rr[0]));writer.writeheader();writer.writerows(rr)
rows=[];events=[]
for case,(p0,p1,p2) in SCENARIOS.items():
    for seed in SEEDS:
        rng=np.random.default_rng(seed+{'near_limit':0,'moderate':500,'stable_safe':1000}[case])
        recent=[];since_alarm=[];state='active';alarms=[];resumes=[]
        for t in range(1,TICKS+1):
            phase='initial' if t<=30 else ('shift' if t<=60 else 'recovery')
            p=p0 if t<=30 else (p1 if t<=60 else p2)
            ae=int(rng.binomial(AUDIT,p));se=int(rng.binomial(SENTINEL,p))
            wrong=int(rng.binomial(ACTIONS,p))
            recent=(recent+[(ae,AUDIT)])[-WINDOW:]
            bound=ub(sum(x for x,n in recent),sum(n for x,n in recent))
            rolling=bound<=TARGET
            alarm=se>=THRESHOLD
            if alarm:
                state='suspended';since_alarm=[];alarms.append(t)
            if state=='suspended':
                since_alarm=(since_alarm+[(ae,AUDIT)])[-WINDOW:]
                if len(since_alarm)==WINDOW and ub(sum(x for x,n in since_alarm),WINDOW*AUDIT)<=TARGET and not alarm:
                    state='active';resumes.append(t)
            sentinel=rolling and state=='active' and not alarm
            for policy,allowed,nlabels in [('rolling_only',rolling,AUDIT),('sentinel_always',sentinel,AUDIT+SENTINEL)]:
                rows.append(dict(scenario=case,seed=seed,tick=t,phase=phase,true_risk=p,policy=policy,
                    audit_errors=ae,sentinel_errors=se,sentinel_alarm=int(alarm),rolling_upper=round(bound,5),
                    allowed=int(allowed),wrong_actions=wrong if allowed else 0,
                    withheld_actions=0 if allowed else ACTIONS,authorized_actions=ACTIONS if allowed else 0,
                    evidence_labels=nlabels,controller_state=state if policy=='sentinel_always' else 'rolling'))
        detected=[t for t in alarms if 31<=t<=60]
        recovered=[t for t in resumes if t>=61]
        events.append(dict(scenario=case,seed=seed,first_shift_alarm=min(detected) if detected else '',
            detection_delay=min(detected)-31 if detected else '',recovery_tick=min(recovered) if recovered else '',
            false_alarms=sum(t<=30 or t>=61 for t in alarms)))
save('tick_audit.csv',rows);save('events.csv',events)
summary=[]
for case in SCENARIOS:
    for phase in ['initial','shift','recovery','ALL']:
        for policy in ['rolling_only','sentinel_always']:
            sample=[r for r in rows if r['scenario']==case and r['policy']==policy and (phase=='ALL' or r['phase']==phase)]
            authorized=sum(r['allowed'] for r in sample);actions=sum(r['authorized_actions'] for r in sample)
            w=sum(r['wrong_actions'] for r in sample);withheld=sum(r['withheld_actions'] for r in sample)
            labels=sum(r['evidence_labels'] for r in sample)
            summary.append(dict(scenario=case,phase=phase,policy=policy,ticks=len(sample),
                authorized_ticks=authorized,authorization_pct=round(100*authorized/len(sample),3),
                wrong_actions=w,authorized_actions=actions,conditional_wrong_pct=round(100*w/actions,3) if actions else '',
                withheld_actions=withheld,labels=labels,total_cost=round(10*w+.05*withheld+.01*labels,2)))
save('results.csv',summary)
(P/'manifest.json').write_text(json.dumps(dict(bound='AETHER-091',seeds=[91001,91040],ticks=TICKS,
    scenarios=SCENARIOS,audit_per_tick=AUDIT,sentinel_per_tick=SENTINEL,actions_per_tick=ACTIONS,
    rolling_window=WINDOW,risk_target=TARGET,alarm_threshold=THRESHOLD,alpha=ALPHA,
    cost={'wrong':10,'abstain':.05,'label':.01},
    limitations=['Synthetic Bernoulli observations','Retrospective fixed-time confidence bound','No guaranteed early-warning safety under hidden shifts']),indent=2)+'\n')
print(*[r for r in summary if r['phase']=='ALL'],sep='\n')
