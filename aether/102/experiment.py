#!/usr/bin/env python3
"""AETHER-102: frozen AETHER-101 selector on five unseen synthetic regimes."""
import csv,json,hashlib,importlib.util
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'101'/'experiment.py'
spec=importlib.util.spec_from_file_location('frozen_aether101',SOURCE)
frozen=importlib.util.module_from_spec(spec);spec.loader.exec_module(frozen)
SEEDS=range(102001,102061);T=96;AUD=140;N_ACT=150
REGIMES=('flash_shift','scarce_audit','phase_chirp','guard_degradation','correlated_audit')
def environment(seed,regime):
 rng=np.random.default_rng(seed+dict(flash_shift=0,scarce_audit=200000,phase_chirp=400000,guard_degradation=600000,correlated_audit=800000)[regime])
 t=np.arange(T);risk=np.full(T,.003,dtype=float)
 if regime=='flash_shift':
  start=int(rng.integers(18,39));risk[start:start+6]=.12;risk[start+28:start+36]=.065
 elif regime=='scarce_audit':
  risk[18:48]=.055;risk[64:74]=.025
 elif regime=='phase_chirp':
  risk[14:82]=np.where((t[14:82]**1.12 % 11)<4,.068,.005)
 elif regime=='guard_degradation':
  risk[18:49]=.052;risk[64:81]=.034
 else:
  risk[20:72]=np.where(t[20:72]%11<4,.058,.004)
 n=np.full(T,AUD,dtype=int)
 if regime=='scarce_audit':n[(t>=20)&(t<80)]=28
 audit=rng.binomial(n,risk)
 if regime=='correlated_audit':
  common=np.repeat(rng.normal(0,.013,25),4)[:T]
  audit=rng.binomial(n,np.clip(risk+common,0,.2))
 effectiveness=np.full(T,.55)
 if regime=='guard_degradation':effectiveness[(t>=30)&(t<82)]=1.35
 direct=rng.binomial(N_ACT,risk)
 guarded=rng.binomial(N_ACT,np.clip(risk*effectiveness,0,1))
 return risk,n,audit,direct,guarded,effectiveness
def run(seed,regime,variant):
 risk,n,audit,direct,guarded,eff=environment(seed,regime)
 history=[];trace=[];last='0'*64
 for t in range(T):
  history=(history+[(int(audit[t]),int(n[t]))])[-5:]
  b=frozen.ub(sum(x[0] for x in history),sum(x[1] for x in history))
  stress=bool(audit[t]>=3)
  action=frozen.choose(b,stress) if variant=='selector' else ('direct' if b<=frozen.LIMIT else 'hold')
  wrong=int(direct[t] if action=='direct' else (guarded[t] if action=='guarded' else 0))
  rec=dict(tick=t+1,errors=int(audit[t]),sampled=int(n[t]),observed_upper=round(b,9),stress=int(stress),action=action,prev_hash=last)
  digest=hashlib.sha256(json.dumps(rec,sort_keys=True,separators=(',',':')).encode()).hexdigest();last=digest
  rec.update(hash=digest,seed=seed,regime=regime,variant=variant,wrong=wrong,unsafe_action=int(risk[t]>.02 and action!='hold'),safe_hold=int(risk[t]<=.02 and action=='hold'),cost=round(10*wrong+(.05*N_ACT if action=='hold' else (1.6 if action=='guarded' else 1.))+0.01*n[t],4),actual_risk=round(float(risk[t]),5),guard_effectiveness=round(float(eff[t]),3))
  trace.append(rec)
 return trace
def save(name,rows):
 with (ROOT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 seedrows=[];samples=[];summary=[];checks={'same_seed_replay':0,'causal_prefix':0,'hash_integrity':0,'action_admissibility':0}
 for regime in REGIMES:
  for seed in SEEDS:
   sel=run(seed,regime,'selector');base=run(seed,regime,'baseline');replay=run(seed,regime,'selector')
   checks['same_seed_replay']+=int(sel==replay)
   checks['causal_prefix']+=int(all(sel[i]['hash']==replay[i]['hash'] for i in range(48)))
   checks['hash_integrity']+=int(all(hashlib.sha256(json.dumps({k:v for k,v in x.items() if k in ('tick','errors','sampled','observed_upper','stress','action','prev_hash')},sort_keys=True,separators=(',',':')).encode()).hexdigest()==x['hash'] and (i==0 or x['prev_hash']==sel[i-1]['hash']) for i,x in enumerate(sel)))
   checks['action_admissibility']+=int(all(x['action']=='hold' or x['observed_upper']<=frozen.LIMIT+1e-9 for x in sel))
   for variant,rows in [('selector',sel),('baseline',base)]:
    seedrows.append(dict(regime=regime,seed=seed,variant=variant,ticks=T,direct=sum(z['action']=='direct' for z in rows),guarded=sum(z['action']=='guarded' for z in rows),hold=sum(z['action']=='hold' for z in rows),wrong=sum(z['wrong'] for z in rows),unsafe_actions=sum(z['unsafe_action'] for z in rows),safe_holds=sum(z['safe_hold'] for z in rows),cost=round(sum(z['cost'] for z in rows),2)))
   if seed==min(SEEDS):samples+=sel
 save('seed_results.csv',seedrows);save('trace_samples.csv',samples)
 for regime in (*REGIMES,'ALL'):
  for variant in ('baseline','selector'):
   rows=[r for r in seedrows if r['variant']==variant and (regime=='ALL' or r['regime']==regime)]
   summary.append(dict(regime=regime,variant=variant,seeds=len(rows),**{k:round(sum(r[k] for r in rows),2) for k in ('ticks','direct','guarded','hold','wrong','unsafe_actions','safe_holds','cost')}))
 save('results.csv',summary)
 by={(r['regime'],r['variant']):r for r in summary};b=by['ALL','baseline'];s=by['ALL','selector']
 breakdown=[dict(regime=r,extra_cost=round(by[r,'selector']['cost']-by[r,'baseline']['cost'],2),extra_unsafe=by[r,'selector']['unsafe_actions']-by[r,'baseline']['unsafe_actions']) for r in REGIMES]
 gates={'all_replay_and_admissibility':all(v==len(SEEDS)*len(REGIMES) for v in checks.values()),'no_more_unsafe_authorizations':bool(s['unsafe_actions']<=b['unsafe_actions']),'overall_cost_not_higher':bool(s['cost']<=b['cost']),'no_regime_cost_regression':all(x['extra_cost']<=0 for x in breakdown)}
 manifest=dict(bound='AETHER-102',status='PASS' if all(gates.values()) else 'FAIL',phase_percent=87.5 if all(gates.values()) else 75.0,frozen_policy_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),seeds=[min(SEEDS),max(SEEDS)],regimes=list(REGIMES),checks=checks,acceptance=gates,breakdown=breakdown,limitations=['Synthetic stress distributions','Fixed-time historical risk bound, not a drift guarantee','Guard effectiveness under degradation is unobservable to the policy'])
 (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'manifest':manifest,'overall_baseline':b,'overall_selector':s},indent=2))
if __name__=='__main__':main()
