#!/usr/bin/env python3
"""AETHER-110 deterministic resource scheduler; synthetic independent-root test."""
from pathlib import Path
import csv,hashlib,json
import numpy as np
from scipy.stats import beta
ROOT=Path(__file__).resolve().parent
SCENARIOS=('stable_safe','hazard_burst','oscillation','scarce_budget','correlated_duplicates')
T=24;MAXROOTS=560;BLOCK=140;ACTIONS=150;LIMIT=.025;ALPHA=.05;LOOKS=4
DEV=range(110001,110031);TEST=range(110101,110181)
def upper(e,n):
 return 1.0 if n<=0 or e>=n else float(beta.ppf(1-ALPHA/(T*LOOKS),int(e)+1,int(n-e)))
def risk(s,t):
 if s=='hazard_burst' and 8<=t<16:return .075
 if s=='oscillation' and (t//3)%2:return .052
 if s=='scarce_budget' and 12<=t<18:return .065
 if s=='correlated_duplicates' and 7<=t<15:return .065
 return .003
def episode(seed,s):
 gen=np.random.default_rng(int.from_bytes(hashlib.sha256(f'110:{seed}:{s}'.encode()).digest()[:8],'big'))
 out=[]
 for t in range(T):
  p=risk(s,t)
  x=gen.binomial(1,p,MAXROOTS).astype(np.int8)
  if s=='correlated_duplicates':
   unique=gen.binomial(1,p,MAXROOTS//10).astype(np.int8)
   x=np.repeat(unique,10)
  out.append((p,x,int(gen.binomial(ACTIONS,p))))
 return out
def run(seed,s,policy,budget,data,trace=False):
 remaining=budget;spent=wrong=held=act=unsafe=safehold=0
 audited=0;probes=0;holds_no_evidence=0;trace_rows=[];chain='0'*64
 for t,(p,x,w) in enumerate(data):
  cap=56 if s=='correlated_duplicates' else MAXROOTS
  can=min(cap,remaining)
  observed=0;n=0;reason='BUDGET_HOLD';allowed=False
  if policy=='fixed':
   n=can
   observed=int(x[::10][:n].sum()) if cap==56 else int(x[:n].sum())
   allowed=n==cap and cap==MAXROOTS and upper(observed,n)<=LIMIT
   reason='FIXED_PASS' if allowed else 'FIXED_HOLD'
  elif policy=='adaptive':
   while n<can:
    chunk=min(BLOCK,can-n);lo=n;n+=chunk
    observed+=int(x[::10][lo:n].sum()) if cap==56 else int(x[lo:n].sum())
    b=upper(observed,n)
    if n>=BLOCK and b<=LIMIT:
     allowed=True;reason='EARLY_CERT';break
    optimistic=upper(observed,can)
    if optimistic>LIMIT:
     reason='NO_CERT_POSSIBLE';break
    reason='FULL_CERT_FAIL'
  else:raise ValueError(policy)
  remaining-=n;spent+=n;audited+=int(n>0)
  if not n:holds_no_evidence+=1
  act+=int(allowed);held+=int(not allowed);wrong+=w if allowed else 0
  unsafe+=int(allowed and p>LIMIT);safehold+=int(not allowed and p<=LIMIT)
  event=dict(seed=seed,scenario=s,tick=t+1,policy=policy,remaining_before=remaining+n,roots_bought=n,errors=observed,upper_bound=round(upper(observed,n),7),action='ACT' if allowed else 'HOLD',reason=reason,hidden_risk_for_evaluation=p)
  chain=hashlib.sha256((chain+json.dumps(event,sort_keys=True,separators=(',',':'))).encode()).hexdigest()
  if trace:trace_rows.append(dict(**event,hash=chain))
 total=10*wrong+.05*ACTIONS*held+.01*spent
 return dict(seed=seed,scenario=s,policy=policy,budget=budget,roots=spent,acts=act,holds=held,wrong=wrong,unsafe_authorized=unsafe,safe_holds=safehold,out_of_budget_holds=holds_no_evidence,cost=round(total,2),final_hash=chain),trace_rows
def collect(seeds,budgets,save_trace=False):
 rows=[];traces=[]
 for s in SCENARIOS:
  for seed in seeds:
   data=episode(seed,s)
   for b in budgets:
    for policy in ('fixed','adaptive'):
     row,trace=run(seed,s,policy,b,data,save_trace and seed==min(seeds) and b==budgets[0])
     rows.append(row);traces.extend(trace)
 return rows,traces
def summarize(rows):
 out=[]
 for s in (*SCENARIOS,'ALL'):
  for policy in ('fixed','adaptive'):
   z=[r for r in rows if r['policy']==policy and (s=='ALL' or r['scenario']==s)]
   out.append(dict(scenario=s,policy=policy,cases=len(z),cost=round(sum(r['cost'] for r in z),2),roots=sum(r['roots'] for r in z),acts=sum(r['acts'] for r in z),holds=sum(r['holds'] for r in z),wrong=sum(r['wrong'] for r in z),unsafe_authorized=sum(r['unsafe_authorized'] for r in z),safe_holds=sum(r['safe_holds'] for r in z)))
 return out
def save(filename,rows):
 with (ROOT/filename).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 budgets=(7000,9000,11000)
 dr,_=collect(DEV,budgets);options=[]
 for b in budgets:
  summary=summarize([r for r in dr if r['budget']==b]);d={x['policy']:x for x in summary if x['scenario']=='ALL'}
  rules={'cost_nonincrease':d['adaptive']['cost']<=d['fixed']['cost'],'unsafe_nonincrease':d['adaptive']['unsafe_authorized']<=d['fixed']['unsafe_authorized'],'safe_acts_at_least_fixed':d['adaptive']['acts']>=d['fixed']['acts']}
  options.append(dict(budget=b,**rules,pass_all=all(rules.values()),savings=round(d['fixed']['cost']-d['adaptive']['cost'],2)))
 feasible=[o for o in options if o['pass_all']]
 selected=max(feasible,key=lambda o:(o['savings'],-o['budget']))['budget'] if feasible else 9000
 hold,traces=collect(TEST,(selected,),True);summary=summarize(hold);d={x['policy']:x for x in summary if x['scenario']=='ALL'}
 rules={'cost_nonincrease':d['adaptive']['cost']<=d['fixed']['cost'],'unsafe_nonincrease':d['adaptive']['unsafe_authorized']<=d['fixed']['unsafe_authorized'],'safe_acts_at_least_fixed':d['adaptive']['acts']>=d['fixed']['acts'],'replay_determinism':all(run(x['seed'],x['scenario'],x['policy'],x['budget'],episode(x['seed'],x['scenario']))[0]['final_hash']==x['final_hash'] for x in hold)}
 passed=bool(feasible and all(rules.values()))
 save('development_options.csv',options);save('results.csv',summary);save('seed_results.csv',hold);save('trace_samples.csv',traces)
 manifest=dict(bound='AETHER-110',phase='IV',status='PASS' if passed else 'FAIL',phase_completion_percent=75 if passed else 62.5,selected_budget=selected,development_seeds=[min(DEV),max(DEV)],test_seeds=[min(TEST),max(TEST)],acceptance=rules,limits=['Synthetic independent Bernoulli roots except explicit tenfold duplication','Fixed-time Bonferroni across 24 inspections × 4 planned looks','No guarantees under unmodeled drift or source ancestry fraud','Costs assume 10 per wrong authorized action, 7.5 per HOLD, 0.01 per root'])
 (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'manifest':manifest,'options':options,'summary':summary},indent=2))
if __name__=='__main__':main()
