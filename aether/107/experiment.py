#!/usr/bin/env python3
"""AETHER-107: temporal alpha spending, paired synthetic paths.
Requirements: numpy, scipy. Reproduces the results and evidence files.
"""
import csv,json,hashlib
from pathlib import Path
import numpy as np
from scipy.stats import beta
OUT=Path(__file__).resolve().parent
SEEDS=range(107001,107301)
HORIZON=24;AUDIT=560;ROOTS_CORR=56;ACT_BATCH=150
ALPHA_TOTAL=.05;RISK_LIMIT=.025
SCENARIOS=('safe_iid','boundary_shift','oscillatory','correlated_shift')
POLICIES=('per_tick_95','spent_iid_naive','spent_root_aware')
def risk_for(s,t):
 if s=='safe_iid':return .003
 if s=='boundary_shift':return .018 if t<8 else (.035 if t<17 else .003)
 if s=='oscillatory':return .035 if t%3==1 else .003
 return .035 if 6<=t<17 else .003
def write(name,rows):
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
ALPHAS=[ALPHA_TOTAL/((t+1)*(t+2)) for t in range(HORIZON)]
UPPER={}
for n in (AUDIT,ROOTS_CORR):
 for alpha in set([.05]+ALPHAS):
  UPPER[n,alpha]=[float(beta.ppf(1-alpha,k+1,n-k)) for k in range(min(n,45)+1)]
def upper(k,n,alpha):
 vals=UPPER[n,alpha]
 return vals[k] if k<len(vals) else 1.
def episode(seed,scenario):
 key=f'{seed}:{scenario}:AETHER-107'
 rng=np.random.default_rng(int.from_bytes(hashlib.sha256(key.encode()).digest()[:8],'little'))
 rows=[];any_false={p:False for p in POLICIES}
 sum_cost={p:0. for p in POLICIES};num_act={p:0 for p in POLICIES}
 num_false={p:0 for p in POLICIES};safe_holds={p:0 for p in POLICIES}
 for t in range(HORIZON):
  actual_risk=risk_for(scenario,t)
  correlated=scenario=='correlated_shift'
  unique=ROOTS_CORR if correlated else AUDIT
  root_errors=int(rng.binomial(unique,actual_risk))
  reports=root_errors*10 if correlated else root_errors
  outcomes=int(rng.binomial(ACT_BATCH,actual_risk))
  for policy in POLICIES:
   n=unique if policy=='spent_root_aware' else AUDIT
   k=root_errors if policy=='spent_root_aware' else reports
   alpha=.05 if policy=='per_tick_95' else ALPHAS[t]
   U=upper(k,n,alpha)
   action='ACT' if U<=RISK_LIMIT else 'HOLD'
   is_false=int(action=='ACT' and actual_risk>RISK_LIMIT)
   any_false[policy] |= bool(is_false)
   num_false[policy]+=is_false;num_act[policy]+=int(action=='ACT')
   safe_holds[policy]+=int(action=='HOLD' and actual_risk<=RISK_LIMIT)
   cost=10*outcomes if action=='ACT' else .05*ACT_BATCH
   cost+=.01*AUDIT
   sum_cost[policy]+=cost
   if seed in (107001,107150,107300):
    stamp=f'{seed}|{scenario}|{t}|{policy}|{reports}|{root_errors}|{action}|{U:.12g}'
    rows.append(dict(seed=seed,scenario=scenario,tick=t+1,policy=policy,
     observed_reports=reports,distinct_roots=unique,observed_root_errors=root_errors,
     alpha=round(alpha,8),upper=round(U,8),decision=action,
     hidden_risk_eval_only=actual_risk,sha256=hashlib.sha256(stamp.encode()).hexdigest()))
 return [dict(seed=seed,scenario=scenario,policy=p,any_false_cert=int(any_false[p]),
  false_authorized_ticks=num_false[p],acts=num_act[p],safe_holds=safe_holds[p],
  cost=round(sum_cost[p],2)) for p in POLICIES],rows
def main():
 individual=[];traces=[]
 for scen in SCENARIOS:
  for seed in SEEDS:
   a,b=episode(seed,scen);individual.extend(a);traces.extend(b)
 write('seed_results.csv',individual);write('trace_samples.csv',traces)
 summary=[]
 for scen in (*SCENARIOS,'ALL'):
  for pol in POLICIES:
   x=[r for r in individual if r['policy']==pol and (scen=='ALL' or r['scenario']==scen)]
   summary.append(dict(scenario=scen,policy=pol,episodes=len(x),
    episodes_any_false=sum(r['any_false_cert'] for r in x),
    familywise_false_rate=round(sum(r['any_false_cert'] for r in x)/len(x),5),
    false_authorized_ticks=sum(r['false_authorized_ticks'] for r in x),
    act_ticks=sum(r['acts'] for r in x),safe_holds=sum(r['safe_holds'] for r in x),
    cost=round(sum(r['cost'] for r in x),2)))
 write('results.csv',summary)
 def get(s,p):return next(r for r in summary if r['scenario']==s and r['policy']==p)
 risky=('boundary_shift','oscillatory','correlated_shift')
 ok=(all(get(s,'spent_root_aware')['episodes_any_false']<=25 for s in risky)
  and get('safe_iid','spent_root_aware')['act_ticks']>=1000
  and sum(get(s,'spent_root_aware')['episodes_any_false'] for s in risky)<sum(get(s,'per_tick_95')['episodes_any_false'] for s in risky)
  and all(get(s,'spent_root_aware')['episodes_any_false']<=get(s,'spent_iid_naive')['episodes_any_false'] for s in risky))
 manifest=dict(bound='AETHER-107',phase='IV',status='ACCEPTED' if ok else 'FAILED',
  phase_pct=37.5 if ok else 25.,seeds=[min(SEEDS),max(SEEDS)],scenarios=SCENARIOS,
  horizon=HORIZON,nominal_family_alpha=.05,actual_allocated_alpha=round(sum(ALPHAS),8),
  confidence='one-sided CP alpha_t, Bonferroni over 24 looks',
  acceptance={'risky_scenario_episodes_with_any_false_max_per_300':25,
    'safe_iid_min_acts':1000,'overall_risky_familywise_fewer_than_per_tick':True,
    'never_worse_than_naive_spend':True},
  caveats=['Root grouping known by construction, not externally verified',
   'All observations within a tick use one fixed risk',
   'Finite 24-tick familywise error budget, not a lifetime guarantee',
   'Correlated safe episodes may require HOLD throughout'])
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'manifest':manifest,'results':summary},indent=2))
if __name__=='__main__':main()
