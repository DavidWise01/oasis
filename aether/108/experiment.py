#!/usr/bin/env python3
"""AETHER-108: evidence-efficient sequential decisions with missing, delayed and duplicated measurements.
Synthetic only. Uses a 24-look Bonferroni/CP confidence budget and true distinct-root count.
At tick t, only root measurements tagged t may authorize action at t. Hidden risk is evaluator-only.
"""
from pathlib import Path
import csv,hashlib,json
import numpy as np
from scipy.stats import beta
OUT=Path(__file__).resolve().parent
SEEDS=range(108001,108121)
T=24; ALPHA=.05; RISK_LIMIT=.025; ACT_BATCH=150
SCENARIOS=('full','half_missing','delayed_half','correlated_tenfold','hazard_sparse')
POLICIES=('all_available','early_impossibility')
def write(name,rows):
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def risk(s,t):
 if s=='hazard_sparse':return .035 if 6<=t<17 else .003
 return .003 if t<9 or t>=19 else .035
def upper(k,n,alpha):
 return 1.0 if n<=0 else (1.0 if k==n else float(beta.ppf(1-alpha,k+1,n-k)))
def run(seed,scenario):
 rng=np.random.default_rng(int.from_bytes(hashlib.sha256(f'AETHER108:{seed}:{scenario}'.encode()).digest()[:8],'little'))
 rows=[]
 for t in range(T):
  p=risk(scenario,t)
  potential=560 if scenario in ('full','hazard_sparse') else (280 if scenario in ('half_missing','delayed_half') else 56)
  if scenario=='hazard_sparse':potential=280 if t%3==0 else 560
  samples=rng.binomial(1,p,size=potential)
  outcomes=int(rng.binomial(ACT_BATCH,p))
  budget=ALPHA/((t+1)*(t+2))
  first=min(280,potential)
  first_errors=int(samples[:first].sum());all_errors=int(samples.sum())
  optimistic=upper(first_errors,potential,budget)
  should_buy=bool(potential>first and optimistic<=RISK_LIMIT)
  n_cheap=potential if should_buy else first
  k_cheap=all_errors if should_buy else first_errors
  for policy in POLICIES:
   n=potential if policy=='all_available' else n_cheap
   k=all_errors if policy=='all_available' else k_cheap
   u=upper(k,n,budget)
   action='ACT' if u<=RISK_LIMIT else 'HOLD'
   cost=10*outcomes if action=='ACT' else .05*ACT_BATCH
   cost+=.01*n
   stale_reports=280 if scenario=='delayed_half' and t>0 else 0
   duplicates=9*potential if scenario=='correlated_tenfold' else 0
   rows.append(dict(seed=seed,scenario=scenario,tick=t+1,policy=policy,alpha=round(budget,9),
    actual_risk_eval_only=p,available_distinct_roots=potential,acquired_roots=n,observed_errors=k,
    stale_reports_ignored=stale_reports,duplicate_reports_ignored=duplicates,
    decision=action,unsafe_authorized=int(action=='ACT' and p>RISK_LIMIT),
    safe_hold=int(action=='HOLD' and p<=RISK_LIMIT),wrong=int(outcomes if action=='ACT' else 0),
    cost=round(cost,2)))
 return rows
def main():
 data=[r for s in SCENARIOS for seed in SEEDS for r in run(seed,s)]
 write('seed_results.csv',data)
 aggregate=[]
 for s in (*SCENARIOS,'ALL'):
  for pol in POLICIES:
   z=[r for r in data if r['policy']==pol and (s=='ALL' or r['scenario']==s)]
   aggregate.append(dict(scenario=s,policy=pol,ticks=len(z),act=sum(r['decision']=='ACT' for r in z),
    hold=sum(r['decision']=='HOLD' for r in z),unsafe_authorized=sum(r['unsafe_authorized'] for r in z),
    safe_holds=sum(r['safe_hold'] for r in z),wrong=sum(r['wrong'] for r in z),
    acquired_roots=sum(r['acquired_roots'] for r in z),
    stale_ignored=sum(r['stale_reports_ignored'] for r in z),
    duplicates_ignored=sum(r['duplicate_reports_ignored'] for r in z),
    cost=round(sum(r['cost'] for r in z),2)))
 write('results.csv',aggregate)
 a={(r['scenario'],r['tick'],r['seed']):r['decision'] for r in data if r['policy']=='all_available'}
 discrepancies=[r for r in data if r['policy']=='early_impossibility' and r['decision']!=a[(r['scenario'],r['tick'],r['seed'])]]
 full=next(r for r in aggregate if r['scenario']=='ALL' and r['policy']=='all_available')
 lean=next(r for r in aggregate if r['scenario']=='ALL' and r['policy']=='early_impossibility')
 safe=next(r for r in aggregate if r['scenario']=='full' and r['policy']=='early_impossibility')
 passgate=not discrepancies and lean['unsafe_authorized']<=full['unsafe_authorized'] and lean['cost']<full['cost'] and safe['act']>=1000
 manifest=dict(bound='AETHER-108',phase='IV',status='PASS' if passgate else 'FAIL',completion_pct=50 if passgate else 37.5,
  seeds=[min(SEEDS),max(SEEDS)],t=T,nominal_family_alpha=ALPHA,
  actual_spend=round(sum(ALPHA/((t+1)*(t+2)) for t in range(T)),5),
  policy='Purchase additional independent current-tick roots only when optimistic zero-error continuation could still certify action',
  checks={'identical_actions':not discrepancies,'no_extra_unsafe':lean['unsafe_authorized']<=full['unsafe_authorized'],
   'cost_lower':lean['cost']<full['cost'],'full_environment_actions_min_1000':safe['act']>=1000},
  limitations=['Missing and delayed roots are never inferred or filled in','Known true ancestry of correlated samples by construction',
  'Conditional full-sample equivalence, not a guarantee of performance when all independent sensing is unavailable',
  'Fixed-horizon alpha spending; risk changes between decisions and estimates are local to each tick'])
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 write('trace_samples.csv',[r for r in data if r['seed'] in (108001,108060) and r['tick'] in (1,10,16,24)])
 print(json.dumps({'manifest':manifest,'results':aggregate,'discrepancies':len(discrepancies)},indent=2))
if __name__=='__main__':main()
