#!/usr/bin/env python3
"""AETHER-095: conditional promotion from disjoint evidence phases, synthetic only."""
from pathlib import Path
import numpy as np,csv,json
from scipy.stats import beta
P=Path(__file__).resolve().parent
REGIMES=('stable','step','ramp','burst','asymmetric_burst','oscillatory_shift')
PHASES={'discovery':range(95001,95025),'validation':range(95101,95161),'holdout':range(95201,95261)}
T=72;AUD=140;SENT=80;ACT=150
OFFSETS=dict(stable=0,step=10000,ramp=20000,burst=30000,asymmetric_burst=40000,oscillatory_shift=50000)
UB={n:np.array([1. if f==n else beta.ppf(.95,f+1,n-f) for f in range(n+1)]) for n in (140,280,420,560,700)}
def upper(f,n):return UB[n][f]
def draw(seed,g):
 rng=np.random.default_rng(seed+OFFSETS[g]);start=int(rng.integers(15,39));length=int(rng.integers(14,26));peak=float(rng.uniform(.022,.055));r=[]
 for t in range(T):
  j=t-start
  if g=='stable':p=.003
  elif g=='step':p=peak if 0<=j<length else .003
  elif g=='ramp':p=.003+(peak-.003)*min(1.,max(0,j/10)) if 0<=j<length else .003
  elif g=='burst':p=peak if 0<=j<length and j%6<3 else .003
  elif g=='asymmetric_burst':p=.11 if 0<=j<length and j%7==0 else (.012 if 0<=j<length else .003)
  else:p=.003+(peak-.003)*(.5+.5*np.sin(j*.9)) if 0<=j<length else .003
  r.append(p)
 q=np.array(r)
 return q,rng.binomial(AUD,q),rng.binomial(SENT,q),rng.binomial(ACT,q)
def evaluate(seed,g,policy):
 risk,audit,sent,wrong=draw(seed,g);history=[];active=True;recovery=[]
 out=dict(wrong=0,withheld=0,labels=0,authorized=0,unsafe=0,probes=0)
 for t in range(T):
  history=(history+[int(audit[t])])[-5:];bound=upper(sum(history),AUD*len(history))
  feature='denied' if bound>.04 else ('uncertain' if bound>.022 or audit[t]>=2 else 'quiet')
  probe=(policy=='learned' and feature=='uncertain')
  alarm=bool(probe and sent[t]>=3)
  if alarm:active=False;recovery=[]
  if not active:
   recovery=(recovery+[int(audit[t])])[-5:]
   if len(recovery)==5 and upper(sum(recovery),AUD*5)<=.02 and not alarm:active=True
  allow=bool(bound<=.02 and (policy=='rolling' or active and not alarm))
  out['wrong']+=int(wrong[t]) if allow else 0
  out['withheld']+=0 if allow else ACT
  out['labels']+=AUD+SENT*int(probe)
  out['authorized']+=int(allow)
  out['unsafe']+=int(allow and risk[t]>.02)
  out['probes']+=int(probe)
 out['cost']=round(10*out['wrong']+.05*out['withheld']+.01*out['labels'],3)
 return out
def save(path,items):
 with (P/path).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
rows=[]
for phase,seeds in PHASES.items():
 for g in REGIMES:
  for seed in seeds:
   for policy in ('rolling','learned'):
    rows.append(dict(phase=phase,regime=g,seed=seed,policy=policy,**evaluate(seed,g,policy)))
save('seed_results.csv',rows)
proposal={}
for g in REGIMES:
 x=[r for r in rows if r['phase']=='discovery' and r['regime']==g]
 proposal[g]=sum(r['cost'] for r in x if r['policy']=='learned')<sum(r['cost'] for r in x if r['policy']=='rolling')
rng=np.random.default_rng(95095);cert=[]
for g in REGIMES:
 x=[r for r in rows if r['phase']=='validation' and r['regime']==g]
 dif=np.array([next(r['cost'] for r in x if r['seed']==seed and r['policy']=='rolling')-next(r['cost'] for r in x if r['seed']==seed and r['policy']=='learned') for seed in PHASES['validation']])
 ix=rng.integers(0,len(dif),size=(10000,len(dif)));sims=dif[ix].mean(axis=1)
 lo=float(np.quantile(sims,.05/6));hi=float(np.quantile(sims,1-.05/6))
 cert.append(dict(regime=g,discovery_candidate=int(proposal[g]),validation_mean_savings=round(float(dif.mean()),3),lower_simultaneous_bound=round(lo,3),upper_simultaneous_bound=round(hi,3),approved=int(proposal[g] and lo>0),validation_seeds=len(dif)))
save('certification.csv',cert)
permission={r['regime']:bool(r['approved']) for r in cert}
hold=[]
for g in REGIMES:
 for seed in PHASES['holdout']:
  x={r['policy']:r for r in rows if r['phase']=='holdout' and r['regime']==g and r['seed']==seed}
  policy='learned' if permission[g] else 'rolling'
  hold.append(dict(seed=seed,regime=g,choice=policy,rolling_cost=x['rolling']['cost'],learned_cost=x['learned']['cost'],deployed_cost=x[policy]['cost'],savings=round(x['rolling']['cost']-x[policy]['cost'],3),rolling_wrong=x['rolling']['wrong'],deployed_wrong=x[policy]['wrong'],rolling_authorized=x['rolling']['authorized'],deployed_authorized=x[policy]['authorized']))
save('holdout.csv',hold)
summary=[]
for g in (*REGIMES,'ALL'):
 z=[r for r in hold if g=='ALL' or r['regime']==g]
 summary.append(dict(regime=g,holdout_cases=len(z),promotion=int(permission.get(g,False)) if g!='ALL' else sum(permission.values()),baseline_cost=round(sum(r['rolling_cost'] for r in z),2),deployed_cost=round(sum(r['deployed_cost'] for r in z),2),savings=round(sum(r['savings'] for r in z),2),baseline_wrong=sum(r['rolling_wrong'] for r in z),deployed_wrong=sum(r['deployed_wrong'] for r in z),baseline_authorized=sum(r['rolling_authorized'] for r in z),deployed_authorized=sum(r['deployed_authorized'] for r in z)))
save('results.csv',summary)
(P/'manifest.json').write_text(json.dumps(dict(bound='AETHER-095',phase_seeds={k:[min(v),max(v)] for k,v in PHASES.items()},certificate=cert,promoted_regimes=[g for g in REGIMES if permission[g]],total=summary[-1],limits=['Simulator-supplied regime label; context detection not demonstrated','No within-episode revocation tested','Bootstrap under finite synthetic populations only']),indent=2)+'\n')
print(*summary,sep='\n')
