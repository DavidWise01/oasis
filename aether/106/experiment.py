#!/usr/bin/env python3
"""AETHER-106: sequential calibration, four optional looks, IID / block10 stress."""
import csv,json,random,hashlib
from pathlib import Path
from scipy.stats import beta
OUT=Path(__file__).resolve().parent
SEEDS=range(106001,106501); RISKS=(.003,.018,.035,.065)
MODES=('iid','block10');LOOKS=(40,140,280,560);LIMIT=.025;ALPHA=.05;ACTIONS=150
POLICIES=('naive_fixed','naive_optional','anytime_naive','anytime_root_aware')
TABLE={}
for n in LOOKS+tuple(x//10 for x in LOOKS):
 for alpha in (ALPHA,ALPHA/len(LOOKS)):
  TABLE[n,alpha]=[1.0 if f==n else float(beta.ppf(1-alpha,f+1,n-f)) for f in range(n+1)]
def one(seed,p,mode):
 rng=random.Random(f'{seed}:{p}:{mode}:AETHER-106')
 if mode=='iid':audit=[int(rng.random()<p) for _ in range(560)]
 else:
  roots=[int(rng.random()<p) for _ in range(56)]
  audit=[v for v in roots for _ in range(10)]
 return audit,[int(rng.random()<p) for _ in range(ACTIONS)]
def decide(audit,mode,policy):
 looks=(560,) if policy=='naive_fixed' else LOOKS
 for n in looks:
  root_aware=(policy=='anytime_root_aware' and mode=='block10')
  if root_aware:k=n//10;x=sum(audit[j] for j in range(0,n,10))
  else:k=n;x=sum(audit[:n])
  alpha=ALPHA/len(LOOKS) if policy.startswith('anytime_') else ALPHA
  upper=TABLE[k,alpha][x]
  if upper<=LIMIT:return 'ACT',n,k,x,round(upper,8)
 return 'HOLD',looks[-1],k,x,round(upper,8)
def save(name,rows):
 with (OUT/name).open('w',newline='') as file:
  writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
def main():
 rows=[];examples=[]
 for mode in MODES:
  for p in RISKS:
   for seed in SEEDS:
    audit,outcomes=one(seed,p,mode)
    for policy in POLICIES:
     decision,n,k,x,upper=decide(audit,mode,policy)
     wrong=sum(outcomes) if decision=='ACT' else 0
     cost=10*wrong+(.05*ACTIONS if decision=='HOLD' else 0)+.01*n
     rows.append(dict(mode=mode,risk=p,seed=seed,policy=policy,decision=decision,
      labels=n,effective_count=k,errors=x,upper=upper,
      unsafe_certificate=int(decision=='ACT' and p>LIMIT),wrong=wrong,cost=round(cost,3)))
     if seed in (106001,106250,106500):
      stamp=f'{mode}|{p}|{seed}|{policy}|{n}|{k}|{x}|{decision}|{upper}'
      examples.append(dict(mode=mode,risk=p,seed=seed,policy=policy,decision=decision,
       labels=n,root_count=k,risk_upper=upper,sha256=hashlib.sha256(stamp.encode()).hexdigest()))
 save('seed_results.csv',rows);save('trace_samples.csv',examples)
 summary=[]
 for mode in MODES:
  for p in RISKS:
   for policy in POLICIES:
    z=[r for r in rows if r['mode']==mode and r['risk']==p and r['policy']==policy]
    summary.append(dict(mode=mode,risk=p,policy=policy,cases=len(z),
     act=sum(r['decision']=='ACT' for r in z),
     false_certificates=sum(r['unsafe_certificate'] for r in z),
     mean_labels=round(sum(r['labels'] for r in z)/len(z),2),
     cost=round(sum(r['cost'] for r in z),2)))
 save('results.csv',summary)
 def get(m,p,policy):return next(x for x in summary if x['mode']==m and x['risk']==p and x['policy']==policy)
 iid_safe=get('iid',.003,'anytime_root_aware')
 iid_risky=[get('iid',p,'anytime_root_aware') for p in (.035,.065)]
 corr_risky=[get('block10',p,'anytime_root_aware') for p in (.035,.065)]
 naive_corr=get('block10',.035,'naive_optional')
 achieved=bool(iid_safe['act']>=250 and
  all(z['false_certificates']<=20 for z in iid_risky+corr_risky) and
  sum(z['false_certificates'] for z in corr_risky)<naive_corr['false_certificates'])
 manifest=dict(bound='AETHER-106',phase='IV',status='ACCEPTED' if achieved else 'FAILED',
  phase_completion_pct=25. if achieved else 12.5,seed_first=106001,seed_last=106500,
  risks=RISKS,modes=MODES,looks=LOOKS,alpha=.05,certification_limit=.025,
  acceptance={'iid_safe_acts_min':250,'risky_false_certificates_max_per_500':20,
   'correlated_root_aware_false_less_than_naive_optional_at_risk_.035':True},
  caveats=['Known independent blocks of 10 are a simulator assumption',
   'Bonferroni Clopper-Pearson is valid for IID roots, not arbitrary drift',
   'Per-episode calibration is not an across-time guarantee'])
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'manifest':manifest,'summary':summary},indent=2))
if __name__=='__main__':main()
