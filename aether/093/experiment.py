#!/usr/bin/env python3
"""AETHER-093: held-out risk-weighted sentinel scheduling; synthetic only."""
import csv,itertools,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
OUT=Path(__file__).resolve().parent
TRAIN=range(93001,93025);TEST=range(93101,93141)
REGIMES=('stable','step','ramp','burst');POLICIES=('rolling','periodic','continuous','learned')
T=72;NA=140;NS=80;ACT=150;WINDOW=5
def upper(f,n):
 return 1. if n<1 or f>=n else float(beta.ppf(.95,f+1,n-f))
def draws(seed,regime):
 rng=np.random.default_rng(seed)
 start=int(rng.integers(18,40));length=int(rng.integers(12,23));peak=float(rng.uniform(.022,.048))
 pp=[]
 for t in range(1,T+1):
  if regime=='stable':p=.003
  elif regime=='step':p=peak if start<=t<start+length else .003
  elif regime=='ramp':p=.003+(peak-.003)*min(1.,max(0,(t-start)/9)) if start<=t<start+length else .003
  else:p=peak if start<=t<start+length and (t-start)%6<3 else .003
  pp.append(p)
 p=np.array(pp)
 return p,rng.binomial(NA,p),rng.binomial(NS,p),rng.binomial(ACT,p)
def run(seed,regime,policy,choice=None):
 pp,aa,ss,ww=draws(seed,regime);recent=[];active=True;recovery=[];out=[]
 for k in range(T):
  recent=(recent+[int(aa[k])])[-WINDOW:]
  bound=upper(sum(recent),len(recent)*NA)
  feature='denied' if bound>.04 else ('uncertain' if bound>.022 or aa[k]>=2 else 'quiet')
  probe=(policy=='continuous' or policy=='periodic' and k%5==0 or policy=='learned' and bool(choice.get(feature,False))) if policy!='rolling' else False
  alarm=probe and ss[k]>=3
  if alarm:active=False;recovery=[]
  if not active:
   recovery=(recovery+[int(aa[k])])[-WINDOW:]
   if len(recovery)==WINDOW and upper(sum(recovery),NA*WINDOW)<=.02 and not alarm:active=True
  authorize=bound<=.02 and (policy=='rolling' or active and not alarm)
  out.append(dict(seed=seed,regime=regime,tick=k+1,policy=policy,feature=feature,probe=int(probe),unsafe=int(pp[k]>.02),authorized=int(authorize),wrong=int(ww[k]) if authorize else 0,withheld=0 if authorize else ACT,labels=NA+NS*int(probe)))
 return out
def cost(r):return 10*sum(x['wrong'] for x in r)+.05*sum(x['withheld'] for x in r)+.01*sum(x['labels'] for x in r)
def save(filename,rows):
 with (OUT/filename).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
options=[]
for bits in itertools.product((False,True),repeat=3):
 c=dict(zip(('quiet','uncertain','denied'),bits))
 records=[x for regime in ('stable','step','ramp') for seed in TRAIN for x in run(seed,regime,'learned',c)]
 options.append((round(cost(records),2),sum(r['probe'] for r in records),c))
options.sort(key=lambda x:(x[0],x[1]));chosen=options[0][2]
save('training_options.csv',[dict(train_cost=a,train_probes=b,quiet=int(c['quiet']),uncertain=int(c['uncertain']),denied=int(c['denied'])) for a,b,c in options])
rows=[x for regime in REGIMES for seed in TEST for policy in POLICIES for x in run(seed,regime,policy,chosen)]
save('tick_audit.csv',rows)
summary=[]
for regime in (*REGIMES,'ALL'):
 for policy in POLICIES:
  z=[r for r in rows if r['policy']==policy and (regime=='ALL' or r['regime']==regime)]
  a=sum(r['authorized'] for r in z);w=sum(r['wrong'] for r in z)
  summary.append(dict(regime=regime,policy=policy,ticks=len(z),authorized_ticks=a,unsafe_authorized_ticks=sum(r['authorized'] and r['unsafe'] for r in z),wrong_actions=w,withheld_actions=sum(r['withheld'] for r in z),probes=sum(r['probe'] for r in z),labels=sum(r['labels'] for r in z),cost=round(cost(z),2),wrong_per_authorized=round(w/(a*ACT),5) if a else ''))
save('results.csv',summary)
(OUT/'manifest.json').write_text(json.dumps(dict(bound='AETHER-093',training_seeds=[min(TRAIN),max(TRAIN)],evaluation_seeds=[min(TEST),max(TEST)],selected=chosen,limits='Synthetic Bernoulli roots, retrospective risk bounds, no production guarantee'),indent=2)+'\n')
print(chosen,summary)
