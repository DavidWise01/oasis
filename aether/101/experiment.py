#!/usr/bin/env python3
"""AETHER-101 deterministic, single-authority best-admissible action selector.
Synthetic experiments; only observed audit history enters policy.
"""
import csv, json, hashlib
from pathlib import Path
import numpy as np
from scipy.stats import beta
from functools import lru_cache
ROOT=Path(__file__).resolve().parent
REGIMES=('stable','abrupt','oscillatory')
SEEDS=range(101001,101081)
T=96;AUD=140;N_ACT=150;LIMIT=.02
ACTIONS=('direct','guarded','hold')
@lru_cache(maxsize=15000)
def ub(errors,n): return 1.0 if n==0 or errors>=n else float(beta.ppf(.95,errors+1,n-errors))
def env(seed,regime):
 rng=np.random.default_rng(seed+dict(stable=0,abrupt=100000,oscillatory=200000)[regime]);r=np.full(T,.003)
 if regime=='abrupt':r[25:52]=.062
 if regime=='oscillatory':r[20:72]=np.where(np.arange(52)%8<3,.048,.006)
 a=rng.binomial(AUD,r)
 out_direct=rng.binomial(N_ACT,r)
 out_guard=rng.binomial(N_ACT,.55*r)
 return r,a,out_direct,out_guard

def choose(upper,stress,order=ACTIONS):
 specs={
  'direct':dict(admissible=upper<=LIMIT,harm=1+int(stress),cost=1.,evidence=0.),
  'guarded':dict(admissible=upper<=LIMIT,harm=1,cost=1.6,evidence=0.),
  'hold':dict(admissible=True,harm=0,cost=7.5,evidence=0.)
 }
 # HOLD is mandatory iff no active action meets the risk constraint.
 active=[name for name in order if name!='hold' and specs[name]['admissible']]
 if not active:return 'hold'
 return min(active,key=lambda name:(specs[name]['harm'],specs[name]['cost'],specs[name]['evidence'],name))

def run(seed,regime,variant='selector',change_future=False,reverse=False):
 risk,audit,out_direct,out_guard=env(seed,regime)
 if change_future:
  rng=np.random.default_rng(seed+999999)
  audit=audit.copy();audit[48:]=rng.integers(0,25,size=T-48)
 seen=[];last='0'*64;trace=[]
 for t in range(T):
  e=int(audit[t]);seen=(seen+[e])[-5:]
  b=ub(sum(seen),len(seen)*AUD)
  stress=bool(e>=3)
  if variant=='baseline':action='direct' if b<=LIMIT else 'hold'
  else:action=choose(b,stress,tuple(reversed(ACTIONS)) if reverse else ACTIONS)
  # Wrong outcomes are used only for evaluation after the action is fixed.
  wrong=int(out_direct[t]) if action=='direct' else (int(out_guard[t]) if action=='guarded' else 0)
  withheld=N_ACT if action=='hold' else 0
  record=dict(tick=t+1,audit_errors=e,observed_upper=round(b,9),stress=int(stress),action=action,prev_hash=last)
  digest=hashlib.sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  record['hash']=digest;last=digest
  record.update(wrong=wrong,withheld=withheld,actual_unsafe=int(risk[t]>.02),actual_wrong_rate=round(float(risk[t]),5),seed=seed,regime=regime,variant=variant)
  trace.append(record)
 return trace

def summarize(rows):
 counts={a:sum(z['action']==a for z in rows) for a in ACTIONS}
 wrong=sum(z['wrong'] for z in rows);held=sum(z['withheld'] for z in rows)
 labels=len(rows)*AUD
 return dict(ticks=len(rows),direct=counts['direct'],guarded=counts['guarded'],hold=counts['hold'],wrong=wrong,withheld=held,unsafe_action_ticks=sum(z['actual_unsafe'] and z['action']!='hold' for z in rows),cost=round(10*wrong+.05*held+.01*labels+sum(1.6 if z['action']=='guarded' else (1 if z['action']=='direct' else 0) for z in rows),2))

def save(name,rows):
 with (ROOT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
 checks=dict(replay=0,future_prefix=0,order_invariance=0,hash_integrity=0,exact_argmin=0)
 all_rows=[];samples=[];case=[]
 for regime in REGIMES:
  for seed in SEEDS:
   sel=run(seed,regime)
   replay=run(seed,regime)
   fut=run(seed,regime,change_future=True)
   rev=run(seed,regime,reverse=True)
   base=run(seed,regime,variant='baseline')
   checks['replay']+=int(sel==replay)
   checks['future_prefix']+=int(all(x['hash']==y['hash'] for x,y in zip(sel[:48],fut[:48])))
   checks['order_invariance']+=int(all(x['action']==y['action'] for x,y in zip(sel,rev)))
   checks['hash_integrity']+=int(all(hashlib.sha256(json.dumps({k:v for k,v in z.items() if k in ('tick','audit_errors','observed_upper','stress','action','prev_hash')},sort_keys=True,separators=(',',':')).encode()).hexdigest()==z['hash'] and (i==0 or z['prev_hash']==sel[i-1]['hash']) for i,z in enumerate(sel)))
   checks['exact_argmin']+=int(all(z['action']==choose(z['observed_upper'],bool(z['stress'])) for z in sel))
   for variant,r in [('selector',sel),('baseline',base)]:
    s=summarize(r);case.append(dict(regime=regime,seed=seed,variant=variant,**s))
   if seed==min(SEEDS):samples.extend(sel)
   all_rows.extend(sel)
 aggregated=[]
 for regime in (*REGIMES,'ALL'):
  for variant in ('selector','baseline'):
   recs=[z for z in case if z['variant']==variant and (regime=='ALL' or z['regime']==regime)]
   aggregated.append(dict(regime=regime,variant=variant,seeds=len(recs),**{key:round(sum(z[key] for z in recs),2) for key in ('ticks','direct','guarded','hold','wrong','withheld','unsafe_action_ticks','cost')}))
 save('seed_results.csv',case);save('results.csv',aggregated);save('trace_samples.csv',samples)
 num=len(SEEDS)*len(REGIMES)
 selected=next(x for x in aggregated if x['regime']=='ALL' and x['variant']=='selector')
 tie_pass=choose(.005,False,('hold','guarded','direct'))=='direct' and choose(.005,True,('hold','guarded','direct'))=='guarded'
 hold_pass=choose(.9,False)=='hold'
 accepted=all(v==num for v in checks.values()) and tie_pass and hold_pass and all(selected[x]>0 for x in ('direct','guarded','hold')) and selected['unsafe_action_ticks']<=next(x for x in aggregated if x['regime']=='ALL' and x['variant']=='baseline')['unsafe_action_ticks'] and selected['cost']<=next(x for x in aggregated if x['regime']=='ALL' and x['variant']=='baseline')['cost']
 manifest=dict(bound='AETHER-101',status='PASS' if accepted else 'FAIL',phase_percent=75 if accepted else 62.5,seed_range=[min(SEEDS),max(SEEDS)],cases=num,ticks=selected['ticks'],checks=checks,checks_expected=num,checks_tie=tie_pass,checks_fallback=hold_pass,policy='hard risk admissibility, minimize observable harm, then cost, then evidence cost, then stable ID',limitations=['Synthetic Bernoulli outcomes','Bound uses past observations and cannot guarantee current regime risk under drift','Governance selector does not assert global cost optimality'])
 (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'manifest':manifest,'results':aggregated},indent=2))
if __name__=='__main__':main()
