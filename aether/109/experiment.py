#!/usr/bin/env python3
"""AETHER-109: synthetic post-outage fresh-certificate recovery experiment.
Only current, independent audit roots can establish a new post-outage certificate.
Requires numpy and scipy. Run: python experiment.py
"""
from pathlib import Path
import hashlib,csv,json
import numpy as np
from scipy.stats import beta
OUT=Path(__file__).resolve().parent
SEEDS=range(109001,109101)
SCENARIOS=('safe_resume','hazard_at_resume','delayed_delivery','duplicate_flood')
POLICIES=('stale_reuse','fresh_certificate')
T=30;ROOTS=560;ACTIONS=150;LIMIT=.025;ALPHA=.05
OUTAGE_START=7;RESUME=13
def upper(k,n):
 return 1. if n==0 or k>=n else float(beta.ppf(1-ALPHA/T,k+1,n-k))
def risk(s,t):
 if s=='hazard_at_resume' and RESUME<=t<RESUME+5:return .07
 if s=='delayed_delivery' and RESUME<=t<RESUME+4:return .065
 if s=='duplicate_flood' and 22<=t<26:return .05
 return .003
def data(seed,s):
 key=int.from_bytes(hashlib.sha256(f'AETHER109:{seed}:{s}'.encode()).digest()[:8],'little')
 rng=np.random.default_rng(key)
 return [(risk(s,t),int(rng.binomial(ROOTS,risk(s,t))),int(rng.binomial(ACTIONS,risk(s,t)))) for t in range(T)]
def evaluate(seed,s,policy,obs):
 pre=[];fresh=[];cert=False;cached=False;result=[]
 for t,(r,k,w) in enumerate(obs):
  if t==OUTAGE_START:cached=cert;cert=False;fresh=[]
  outage=OUTAGE_START<=t<RESUME
  bound=1.;acquired=0
  if outage:
   act=False;reason='OUTAGE'
  elif t<OUTAGE_START:
   acquired=ROOTS;pre=(pre+[k])[-2:]
   bound=upper(sum(pre),len(pre)*ROOTS)
   cert=len(pre)==2 and bound<=LIMIT
   act=cert;reason='PRE_OUTAGE_CERT' if act else 'HOLD_NOT_CERTIFIED'
  elif policy=='stale_reuse' and t<RESUME+3:
   acquired=ROOTS;act=cached;reason='STALE_BADGE' if act else 'STALE_HOLD'
  else:
   acquired=ROOTS;fresh=(fresh+[k])[-2:]
   bound=upper(sum(fresh),len(fresh)*ROOTS)
   cert=len(fresh)==2 and bound<=LIMIT
   act=cert;reason='FRESH_CERT' if act else 'FRESH_HOLD'
  result.append(dict(seed=seed,scenario=s,tick=t+1,policy=policy,
   true_risk_eval_only=r,distinct_current_roots=acquired,
   errors=k if acquired else '',late_reports_ignored=ROOTS if s=='delayed_delivery' and t==RESUME else 0,
   duplicates_ignored=ROOTS*9 if s=='duplicate_flood' and t>=RESUME and t%3==0 else 0,
   upper_bound=round(bound,8),action='ACT' if act else 'HOLD',reason=reason,
   unsafe_authorized=int(act and r>LIMIT),safe_hold=int(not act and r<=LIMIT),
   wrong=int(w if act else 0),withheld=0 if act else ACTIONS,
   cost=round((10*w if act else .05*ACTIONS)+.01*acquired,2)))
 return result
def save(name,rows):
 with (OUT/name).open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]))
  writer.writeheader();writer.writerows(rows)
def main():
 allrows=[];seeds=[]
 for s in SCENARIOS:
  for seed in SEEDS:
   obs=data(seed,s)
   for policy in POLICIES:
    z=evaluate(seed,s,policy,obs);allrows.extend(z)
    eligible=[r for r in z if r['tick']>RESUME and r['true_risk_eval_only']<=LIMIT]
    delay=next((r['tick']-RESUME-1 for r in eligible if r['action']=='ACT'),-1)
    seeds.append(dict(scenario=s,seed=seed,policy=policy,
     acts=sum(r['action']=='ACT' for r in z),
     unsafe_authorized=sum(r['unsafe_authorized'] for r in z),
     safe_holds=sum(r['safe_hold'] for r in z),
     wrong=sum(r['wrong'] for r in z),
     post_resume_first_safe_act_delay=delay,
     total_cost=round(sum(r['cost'] for r in z),2)))
 save('seed_results.csv',seeds)
 summary=[]
 for s in (*SCENARIOS,'ALL'):
  for policy in POLICIES:
   z=[r for r in seeds if r['policy']==policy and (s=='ALL' or r['scenario']==s)]
   delay=[r['post_resume_first_safe_act_delay'] for r in z if r['post_resume_first_safe_act_delay']>=0]
   summary.append(dict(scenario=s,policy=policy,episodes=len(z),
    acts=sum(r['acts'] for r in z),
    unsafe_authorized=sum(r['unsafe_authorized'] for r in z),
    safe_holds=sum(r['safe_holds'] for r in z),wrong=sum(r['wrong'] for r in z),
    mean_first_safe_act_delay=round(float(np.mean(delay)),3) if delay else '',
    total_cost=round(sum(r['total_cost'] for r in z),2)))
 save('results.csv',summary)
 a={r['scenario']:r for r in summary if r['policy']=='stale_reuse'}
 b={r['scenario']:r for r in summary if r['policy']=='fresh_certificate'}
 gate=dict(unsafe_reduction=b['ALL']['unsafe_authorized']<a['ALL']['unsafe_authorized'],
   nonincreasing_cost_all=all(b[s]['total_cost']<=a[s]['total_cost'] for s in SCENARIOS),
   safe_recovery_delay_le_3=b['safe_resume']['mean_first_safe_act_delay']<=3,
   usable_safe_resume=b['safe_resume']['acts']>=a['safe_resume']['acts']-.08*100*T)
 passed=all(gate.values())
 manifest=dict(bound='AETHER-109',phase='IV',status='PASS' if passed else 'FAIL',
  phase_percent=62.5 if passed else 50,seeds=[min(SEEDS),max(SEEDS)],
  scenarios=SCENARIOS,criteria=gate,
  limitations=['Synthetic Bernoulli evidence and deterministic outage timing',
   'Stale comparator intentionally reuses out-of-date evidence',
   'No sequential confidence guarantee under correlated roots',
   'Cost values depend on simulated penalty weights'])
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 save('trace_samples.csv',[r for r in allrows if r['seed'] in (109001,109052) and 10<=r['tick']<=22])
 print(json.dumps({'manifest':manifest,'results':summary},indent=2))
if __name__=='__main__':main()
