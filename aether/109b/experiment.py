#!/usr/bin/env python3
"""AETHER-109B — fresh 2-batch cert with affordable independent sampling.
All decisions use observed audit counts only. Hidden risk is evaluation-only.
Sample size selected on development seeds; disjoint holdout is evaluated once.
"""
from pathlib import Path
import csv,json,hashlib
import numpy as np
from scipy.stats import beta
OUT=Path(__file__).resolve().parent
SCENARIOS=('safe_resume','hazard_at_resume','delayed_delivery','duplicate_flood')
DEV=range(109201,109231);TEST=range(109301,109401)
T=30;OUTAGE_START=7;RESUME=13;ALPHA=.05;LIMIT=.025;ROOTS=560;ACTIONS=150
OPTIONS=(480,500,520,540,560)

def upper(k,n):
 return 1. if not n or k>=n else float(beta.ppf(1-ALPHA/T,int(k)+1,int(n-k)))
def risk(s,t):
 if s=='hazard_at_resume' and RESUME<=t<RESUME+5:return .07
 if s=='delayed_delivery' and RESUME<=t<RESUME+4:return .065
 if s=='duplicate_flood' and 22<=t<26:return .05
 return .003
def episode(seed,s):
 rng=np.random.default_rng(int.from_bytes(hashlib.sha256(f'AETHER109B:{seed}:{s}'.encode()).digest()[:8],'little'))
 return [(risk(s,t),rng.binomial(1,risk(s,t),ROOTS).astype(np.uint8),int(rng.binomial(ACTIONS,risk(s,t)))) for t in range(T)]
def run(seed,s,policy,n,data,emit_ticks=False):
 cached=False;cert=False;prior=[];fresh=[];total=unsafe=safehold=wrong=acts=transitions=0;prev='HOLD';first=None;trace=[]
 for t,(r,roots,w) in enumerate(data):
  outage=OUTAGE_START<=t<RESUME
  if t==OUTAGE_START:cached=cert;cert=False;fresh=[]
  count=0;errors=0;bound=1.;reason='';act=False
  if outage:reason='OUTAGE'
  else:
   count=ROOTS if policy=='stale_reuse' or t<OUTAGE_START else n
   errors=int(roots[:count].sum())
   if t<OUTAGE_START:
    prior=(prior+[(errors,count)])[-2:]
    bound=upper(sum(x for x,_ in prior),sum(y for _,y in prior))
    cert=bool(len(prior)==2 and bound<=LIMIT);act=cert
    reason='PRE_CERT' if act else 'PRE_HOLD'
   elif policy=='stale_reuse' and t<RESUME+3:
    act=cached;reason='STALE_ACT' if act else 'STALE_HOLD'
   else:
    fresh=(fresh+[(errors,count)])[-2:]
    bound=upper(sum(x for x,_ in fresh),sum(y for _,y in fresh))
    cert=bool(len(fresh)==2 and bound<=LIMIT)
    act=cert;reason='FRESH_CERT' if act else 'FRESH_HOLD'
  if act and r<=LIMIT and t>=RESUME and first is None:first=t-RESUME
  action='ACT' if act else 'HOLD'
  transitions+=int(action!=prev);prev=action
  unsafe+=int(act and r>LIMIT);safehold+=int(not act and r<=LIMIT);wrong+=w if act else 0;acts+=int(act)
  tickcost=(10*w if act else .05*ACTIONS)+.01*count
  total+=tickcost
  if emit_ticks:
   trace.append(dict(seed=seed,scenario=s,tick=t+1,policy=policy,audit_roots=count,audit_errors=errors,upper_bound=round(bound,7),action=action,reason=reason,evaluation_risk=r,unsafe_authorized=int(act and r>LIMIT),safe_hold=int(not act and r<=LIMIT),cost=round(tickcost,2)))
 return dict(seed=seed,scenario=s,policy=policy,roots_per_post_tick=n if policy!='stale_reuse' else ROOTS,acts=acts,unsafe_authorized=unsafe,safe_holds=safehold,wrong=wrong,transitions=transitions,first_safe_act_delay=first if first is not None else -1,total_cost=round(total,2)),trace
def save(name,rows):
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def dataset(seeds,n,include_trace=False):
 rows=[];trace=[]
 for s in SCENARIOS:
  for seed in seeds:
   data=episode(seed,s)
   for policy in ('stale_reuse','fresh_optimized'):
    r,t=run(seed,s,policy,n,data,emit_ticks=include_trace and seed in (min(seeds),min(seeds)+17))
    rows.append(r);trace.extend(t)
 return rows,trace
def summary(rows):
 s=[]
 for scenario in (*SCENARIOS,'ALL'):
  for policy in ('stale_reuse','fresh_optimized'):
   a=[x for x in rows if x['policy']==policy and (scenario=='ALL' or x['scenario']==scenario)]
   d=[x['first_safe_act_delay'] for x in a if x['first_safe_act_delay']>=0]
   s.append(dict(scenario=scenario,policy=policy,episodes=len(a),acts=sum(x['acts'] for x in a),unsafe_authorized=sum(x['unsafe_authorized'] for x in a),safe_holds=sum(x['safe_holds'] for x in a),wrong=sum(x['wrong'] for x in a),mean_safe_recovery_delay=round(float(np.mean(d)),3) if d else '',total_cost=round(sum(x['total_cost'] for x in a),2)))
 return s
def gate(rows):
 s=summary(rows);b={x['scenario']:x for x in s if x['policy']=='stale_reuse'};q={x['scenario']:x for x in s if x['policy']=='fresh_optimized'}
 rules=dict(unsafe_lower=q['ALL']['unsafe_authorized']<b['ALL']['unsafe_authorized'],per_scenario_cost_nonincreasing=all(q[k]['total_cost']<=b[k]['total_cost'] for k in SCENARIOS),safe_resume_delay_le_3=q['safe_resume']['mean_safe_recovery_delay']<=3,safe_resume_usefulness=q['safe_resume']['acts']>=b['safe_resume']['acts']-.08*len([x for x in rows if x['scenario']=='safe_resume' and x['policy']=='stale_reuse'])*T)
 return rules,s
def main():
 options=[]
 for n in OPTIONS:
  r,_=dataset(DEV,n);g,s=gate(r)
  options.append(dict(roots=n,**g,passed=all(g.values()),total_savings=round(next(x['total_cost'] for x in s if x['scenario']=='ALL' and x['policy']=='stale_reuse')-next(x['total_cost'] for x in s if x['scenario']=='ALL' and x['policy']=='fresh_optimized'),2)))
 save('development_options.csv',options)
 admissible=[o for o in options if o['passed']]
 selected=min(admissible,key=lambda x:(-x['total_savings'],x['roots']))['roots'] if admissible else 560
 rows,trace=dataset(TEST,selected,include_trace=True)
 rules,s=gate(rows);passed=bool(admissible and all(rules.values()))
 save('seed_results.csv',rows);save('results.csv',s);save('trace_samples.csv',trace)
 manifest=dict(bound='AETHER-109B',status='PASS' if passed else 'FAIL',phase='IV',phase_percent=62.5 if passed else 50,selected_roots=selected,development_seed_range=[min(DEV),max(DEV)],evaluation_seed_range=[min(TEST),max(TEST)],acceptance=rules,passed=passed,limitations=['Synthetic fixed risk schedules and independent observations','Stale reference intentionally uses obsolete authorization','No sequential coverage guarantee under correlated roots','New evaluation seeds used after selection'])
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'manifest':manifest,'development':options,'results':s},indent=2))
if __name__=='__main__':main()
