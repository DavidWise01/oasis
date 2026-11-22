#!/usr/bin/env python3
"""AETHER-092 — paired synthetic adaptive sentinel scheduling (numpy, scipy)."""
import csv,json
from pathlib import Path
import numpy as np
from scipy.stats import beta,binom
P=Path(__file__).resolve().parent
SEEDS=range(92001,92041);TICKS=90;AUDIT=140;SENTINEL=80;ACTIONS=150
WINDOW=5;ALPHA=.05;TARGET=.02
SCENARIOS={'safe':(.003,.003,.003),'subtle':(.003,.026,.003),'moderate':(.003,.038,.003)}
POLICIES=('rolling','continuous','periodic','adaptive')
THRESHOLD=int(binom.isf(.01,SENTINEL,.003))+1
def ub(w,n):return 1. if n<=0 or w>=n else float(beta.ppf(1-ALPHA,w+1,n-w))
def save(path,data):
 with (P/path).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
rows=[]
for case,risks in SCENARIOS.items():
 for seed in SEEDS:
  rng=np.random.default_rng(seed+{'safe':0,'subtle':1000,'moderate':2000}[case])
  ps=[risks[0] if t<=30 else risks[1] if t<=60 else risks[2] for t in range(1,TICKS+1)]
  observations=[(int(rng.binomial(AUDIT,p)),int(rng.binomial(SENTINEL,p)),int(rng.binomial(ACTIONS,p))) for p in ps]
  state={p:dict(active=True,cooldown=[]) for p in POLICIES};recent=[]
  for t,(p,(ae,se,wrong)) in enumerate(zip(ps,observations),1):
   recent=(recent+[ae])[-WINDOW:]
   bound=ub(sum(recent),len(recent)*AUDIT);baseline=bound<=TARGET
   probe=(t%10==0 or (.010<=bound<=.035) or ae>=2)
   for policy in POLICIES:
    d=state[policy]
    sampled=(policy=='continuous' or policy=='periodic' and t%5==0 or policy=='adaptive' and probe)
    alarm=sampled and se>=THRESHOLD
    if alarm:d['active']=False;d['cooldown']=[]
    if not d['active']:
     d['cooldown']=(d['cooldown']+[ae])[-WINDOW:]
     if len(d['cooldown'])>=WINDOW and ub(sum(d['cooldown']),AUDIT*WINDOW)<=TARGET and not alarm:d['active']=True
    allow=baseline and (policy=='rolling' or d['active'] and not alarm)
    rows.append(dict(scenario=case,seed=seed,tick=t,phase='initial' if t<=30 else 'shift' if t<=60 else 'recovery',
       policy=policy,true_risk=p,audit_errors=ae,sentinel_errors=se,rolling_upper=round(bound,6),
       sentinel_sampled=int(sampled),sentinel_alarm=int(alarm),allowed=int(allow),
       authorized_actions=ACTIONS if allow else 0,wrong_actions=wrong if allow else 0,
       withheld_actions=0 if allow else ACTIONS,labels=AUDIT+SENTINEL*int(sampled)))
save('tick_audit.csv',rows)
summary=[]
for case in SCENARIOS:
 for phase in ('initial','shift','recovery','ALL'):
  for policy in POLICIES:
   ss=[r for r in rows if r['scenario']==case and r['policy']==policy and (phase=='ALL' or r['phase']==phase)]
   a=sum(r['allowed'] for r in ss);w=sum(r['wrong_actions'] for r in ss)
   h=sum(r['withheld_actions'] for r in ss);l=sum(r['labels'] for r in ss)
   actions=sum(r['authorized_actions'] for r in ss)
   summary.append(dict(scenario=case,phase=phase,policy=policy,ticks=len(ss),authorized_ticks=a,
      authorization_pct=round(100*a/len(ss),3),wrong_actions=w,authorized_actions=actions,
      conditional_error_pct=round(100*w/actions,3) if actions else '',withheld_actions=h,
      sentinel_probes=sum(r['sentinel_sampled'] for r in ss),labels=l,total_cost=round(10*w+.05*h+.01*l,2)))
save('results.csv',summary)
events=[]
for case in SCENARIOS:
 for policy in POLICIES:
  for seed in SEEDS:
   ss=[r for r in rows if r['scenario']==case and r['policy']==policy and r['seed']==seed]
   alarms=[r['tick'] for r in ss if r['sentinel_alarm']]
   shift=[t for t in alarms if 31<=t<=60];resume=[r['tick'] for r in ss if r['tick']>=61 and r['allowed']]
   events.append(dict(scenario=case,policy=policy,seed=seed,first_shift_alarm=min(shift) if shift else '',
    detection_delay=min(shift)-31 if shift else '',false_alarms=sum(t<=30 or t>=61 for t in alarms),
    first_postrecovery_authorization=min(resume) if resume else '',sentinel_probes=sum(r['sentinel_sampled'] for r in ss)))
save('events.csv',events)
(P/'manifest.json').write_text(json.dumps(dict(bound='AETHER-092',seeds=[92001,92040],ticks=TICKS,
 scenarios=SCENARIOS,policies=POLICIES,alarm_threshold=THRESHOLD,
 audit_labels=AUDIT,sentinel_labels=SENTINEL,actions=ACTIONS,
 risk_target=TARGET,cost={'wrong':10,'withheld':.05,'label':.01},
 adaptive_rule='probe every 10th tick, or 0.010 <= rolling bound <= 0.035, or >= 2 audit errors',
 limitations=['Synthetic Bernoulli roots','Retrospective fixed-time bounds','Prespecified heuristic, not learned']),indent=2)+'\n')
print(*[s for s in summary if s['phase']=='ALL'],sep='\n')
