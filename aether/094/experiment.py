#!/usr/bin/env python3
"""AETHER-094: paired synthetic generalization and regret test.
Frozen AETHER-093 schedule; independent seed-level paired bootstrap.
Requires numpy and scipy. Results are not a universal risk guarantee.
"""
import csv,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
P=Path(__file__).resolve().parent
SEEDS=range(94101,94141);T=72;AUD=140;SENT=80;ACT=150
REGIMES=('stable','step','ramp','burst','asymmetric_burst','oscillatory_shift')
POLICIES=('rolling','periodic','continuous','learned')
CHOICE={'quiet':False,'uncertain':True,'denied':False}
def upper(f,n):return 1. if n<1 or f>=n else float(beta.ppf(.95,f+1,n-f))
def draw(seed,g):
 rng=np.random.default_rng(seed+dict(stable=0,step=10000,ramp=20000,burst=30000,asymmetric_burst=40000,oscillatory_shift=50000)[g])
 start=int(rng.integers(15,39));length=int(rng.integers(14,26));peak=float(rng.uniform(.022,.055))
 risk=[]
 for tick in range(T):
  j=tick-start
  if g=='stable':p=.003
  elif g=='step':p=peak if 0<=j<length else .003
  elif g=='ramp':p=.003+(peak-.003)*min(1,max(0,j/10)) if 0<=j<length else .003
  elif g=='burst':p=peak if 0<=j<length and j%6<3 else .003
  elif g=='asymmetric_burst':p=.11 if 0<=j<length and j%7==0 else (.012 if 0<=j<length else .003)
  else:p=.003+(peak-.003)*(.5+.5*np.sin(j*.9)) if 0<=j<length else .003
  risk.append(p)
 p=np.array(risk)
 return p,rng.binomial(AUD,p),rng.binomial(SENT,p),rng.binomial(ACT,p)
def trial(seed,g,policy):
 risk,audit,sent,wrong=draw(seed,g);history=[];active=True;recovery=[];out=[]
 for t in range(T):
  history=(history+[int(audit[t])])[-5:]
  bound=upper(sum(history),AUD*len(history))
  feature='denied' if bound>.04 else ('uncertain' if bound>.022 or audit[t]>=2 else 'quiet')
  probe=policy=='continuous' or policy=='periodic' and t%5==0 or policy=='learned' and CHOICE[feature]
  alarm=probe and sent[t]>=3
  if alarm:active=False;recovery=[]
  if not active:
   recovery=(recovery+[int(audit[t])])[-5:]
   if len(recovery)==5 and upper(sum(recovery),AUD*5)<=.02 and not alarm:active=True
  allow=bound<=.02 and (policy=='rolling' or active and not alarm)
  out.append(dict(seed=seed,regime=g,policy=policy,tick=t+1,wrong=int(wrong[t]) if allow else 0,withheld=0 if allow else ACT,labels=AUD+SENT*int(probe),probe=int(probe),authorized=int(allow),unsafe_authorized=int(allow and risk[t]>.02)))
 return out
def save(name,rr):
 with (P/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
results=[]
for g in REGIMES:
 for seed in SEEDS:
  for policy in POLICIES:
   z=trial(seed,g,policy)
   w=sum(x['wrong'] for x in z);a=sum(x['withheld'] for x in z);l=sum(x['labels'] for x in z)
   results.append(dict(seed=seed,regime=g,policy=policy,wrong=w,withheld=a,labels=l,cost=round(10*w+.05*a+.01*l,2),probes=sum(x['probe'] for x in z),unsafe_authorized=sum(x['unsafe_authorized'] for x in z)))
save('seed_results.csv',results)
summary=[]
for g in (*REGIMES,'ALL'):
 for policy in POLICIES:
  z=[x for x in results if x['policy']==policy and (g=='ALL' or x['regime']==g)]
  summary.append(dict(regime=g,policy=policy,paired_cases=len(z),total_cost=round(sum(x['cost'] for x in z),2),wrong=sum(x['wrong'] for x in z),withheld=sum(x['withheld'] for x in z),labels=sum(x['labels'] for x in z),probes=sum(x['probes'] for x in z),unsafe_authorized=sum(x['unsafe_authorized'] for x in z)))
save('results.csv',summary)
paired=[]
for seed in SEEDS:
 z=[x for x in results if x['seed']==seed]
 base=sum(x['cost'] for x in z if x['policy']=='rolling')
 learn=sum(x['cost'] for x in z if x['policy']=='learned')
 paired.append(dict(seed=seed,baseline_cost=base,learned_cost=learn,benefit=round(base-learn,3)))
save('paired_seed_benefits.csv',paired)
rng=np.random.default_rng(94094);delta=np.array([x['benefit'] for x in paired])
boot=np.array([rng.choice(delta,len(delta),replace=True).mean() for _ in range(10000)])
lower,upper_ci=np.quantile(boot,[.025,.975])
sensitivity=[]
for w,a,l in [(10,.05,.01),(3,.05,.01),(20,.05,.01),(10,.05,.05),(10,.15,.01)]:
 costs={p:round(sum(w*x['wrong']+a*x['withheld']+l*x['labels'] for x in results if x['policy']==p),2) for p in POLICIES}
 sensitivity.append(dict(wrong_cost=w,abstention_cost=a,label_cost=l,best_policy=min(costs,key=costs.get),**costs))
save('cost_sensitivity.csv',sensitivity)
promotion=bool(lower>0 and all(next(x['total_cost'] for x in summary if x['regime']==g and x['policy']=='learned')<=next(x['total_cost'] for x in summary if x['regime']==g and x['policy']=='rolling') for g in REGIMES))
(P/'manifest.json').write_text(json.dumps(dict(bound='AETHER-094',seeds=[min(SEEDS),max(SEEDS)],regimes=REGIMES,frozen_policy=CHOICE,bootstrap_replicates=10000,paired_mean_benefit=round(float(delta.mean()),3),bootstrap_95_interval=[round(float(lower),3),round(float(upper_ci),3)],promotion=promotion,limits='Synthetic Bernoulli root evidence; no distribution-free guarantee'),indent=2)+'\n')
print('promotion:',promotion,'bootstrap:',lower,upper_ci)
