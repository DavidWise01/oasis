#!/usr/bin/env python3
"""AETHER-122 — synthetic selective-evasion measurement test, not a security proof."""
import csv,hashlib,hmac,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
P=Path(__file__).resolve().parent
KEY=b'aether122-demo-key';T=24;N=560;LIMIT=.025;PILOT=(0,128)
SC=('clean','selective_underreport','gradual_selective','burst_selective','stuck_risk_only','high_bias','risk_transition')
SEEDS=range(122001,122061)
def auth(b):return hmac.new(KEY,json.dumps(b,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
def sign(b):return dict(b,mac=auth(b))
def verified(p):return hmac.compare_digest(p.get('mac',''),auth({k:v for k,v in p.items() if k!='mac'}))
def upper(x):return 1. if x>=N else float(beta.ppf(.95,x+1,N-x))
def risk(sc,t):return .085 if (6<=t<19 if sc=='risk_transition' else 8<=t<18) else .003
def bias(sc,t):
 if sc=='selective_underreport':return 36
 if sc=='gradual_selective':return max(0,4*(t-3))
 if sc=='burst_selective':return 47 if 8<=t<18 else 0
 if sc=='stuck_risk_only':return 10000
 if sc=='high_bias':return -25
 return 0
def packet(seed,sc,t):
 rng=np.random.default_rng(seed+SC.index(sc)*100000+7919*t)
 q=risk(sc,t);true_errors=int(rng.binomial(N,q));b=bias(sc,t)
 public=(0,128)
 # The experiment ASSUMES hidden pilots cannot be distinguished from ordinary
 # measurements before the device commits its signed response.
 pilot=(max(0,PILOT[0]-max(0,b)),min(128,max(0,PILOT[1]-b)))
 measured=max(0,min(N,true_errors-b))
 base=dict(source='risk-audit',epoch=1,seq=t,counter=t,observed_t=t,valid_until=t+1,
  independent=True,n=N,errors=measured,public_low=public[0],public_high=public[1],
  pilot_low=pilot[0],pilot_high=pilot[1],pilot_commit=t)
 return q,sign(base)
def decide(p,t,policy):
 valid=verified(p) and p.get('seq')==t and p.get('counter')==t and p.get('observed_t')==t and p.get('valid_until')==t+1 and p.get('source')=='risk-audit' and p.get('independent') is True and p.get('n')==N
 public=valid and p.get('public_low')==0 and p.get('public_high')==128
 hidden=public and p.get('pilot_commit')==t and p.get('pilot_low')==0 and p.get('pilot_high')==128
 accepted=public if policy=='public_only' else hidden
 return valid,public,hidden,('ACT' if accepted and upper(p['errors'])<=LIMIT else 'HOLD')
def trial(seed,sc,policy):
 rows=[];prev='0'*64
 for t in range(T):
  truth,p=packet(seed,sc,t);valid,public,hidden,act=decide(p,t,policy)
  row=dict(scenario=sc,seed=seed,policy=policy,tick=t,truth_risk=truth,
    errors=p['errors'],pilot_high=p['pilot_high'],signed_valid=int(valid),public_valid=int(public),
    hidden_valid=int(hidden),action=act,unsafe=int(act=='ACT' and truth>LIMIT),
    safe_act=int(act=='ACT' and truth<=LIMIT),safe_hold=int(act=='HOLD' and truth<=LIMIT),
    cost=round((10*N*truth if act=='ACT' else .05*N)+(.01*256 if policy=='opaque_pilot' else 0),2))
  payload=json.dumps(row,sort_keys=True,separators=(',',':'))
  row['prev_hash']=prev;prev=hashlib.sha256((prev+payload).encode()).hexdigest();row['hash']=prev;rows.append(row)
 return rows
def chain(rows):
 prev='0'*64
 for r in rows:
  d={k:v for k,v in r.items() if k not in ('prev_hash','hash')};h=hashlib.sha256((prev+json.dumps(d,sort_keys=True,separators=(',',':'))).encode()).hexdigest()
  if r['prev_hash']!=prev or r['hash']!=h:return False
  prev=h
 return True
def write(n,rows):
 with (P/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 seeds=[];checks=[];traces=[]
 for sc in SC:
  for seed in SEEDS:
   for policy in ('public_only','opaque_pilot'):
    rows=trial(seed,sc,policy);again=trial(seed,sc,policy)
    cond=dict(replay=rows==again,hash_integrity=chain(rows),single_action=len(rows)==T and all(r['action'] in ('ACT','HOLD') for r in rows),
     current_packet=all(r['signed_valid'] for r in rows),pilot_fail_closed=(policy!='opaque_pilot' or all(r['action']=='HOLD' for r in rows if not r['hidden_valid'])),
     zero_unsafe=(policy!='opaque_pilot' or not any(r['unsafe'] for r in rows)))
    checks.append(dict(scenario=sc,seed=seed,policy=policy,**{k:int(v) for k,v in cond.items()}))
    seeds.append(dict(scenario=sc,seed=seed,policy=policy,unsafe=sum(r['unsafe'] for r in rows),safe_act=sum(r['safe_act'] for r in rows),
     safe_hold=sum(r['safe_hold'] for r in rows),pilot_reject=sum(not r['hidden_valid'] for r in rows),cost=round(sum(r['cost'] for r in rows),2)))
    if seed==SEEDS.start:traces.extend(rows)
 write('checks.csv',checks);write('seed_results.csv',seeds);write('trace_samples.csv',traces)
 summary=[]
 for sc in (*SC,'ALL'):
  for policy in ('public_only','opaque_pilot'):
   z=[r for r in seeds if r['policy']==policy and (sc=='ALL' or r['scenario']==sc)]
   summary.append(dict(scenario=sc,policy=policy,cases=len(z),unsafe=sum(r['unsafe'] for r in z),safe_act=sum(r['safe_act'] for r in z),
     safe_hold=sum(r['safe_hold'] for r in z),pilot_reject=sum(r['pilot_reject'] for r in z),cost=round(sum(r['cost'] for r in z),2)))
 write('results.csv',summary)
 lookup={(r['scenario'],r['policy']):r for r in summary}
 gates=dict(zero_unsafe=lookup['ALL','opaque_pilot']['unsafe']==0,reduces_unsafe=lookup['ALL','public_only']['unsafe']>0,
  clean_preserved=lookup['clean','opaque_pilot']['safe_act']==lookup['clean','public_only']['safe_act'],
  transition_preserved=lookup['risk_transition','opaque_pilot']['safe_act']==lookup['risk_transition','public_only']['safe_act'],
  checks=all(all(v==1 for k,v in c.items() if k not in ('scenario','seed','policy')) for c in checks))
 manifest=dict(bound='AETHER-122',phase='VI',status='PASS' if all(gates.values()) else 'FAIL',seeds=[SEEDS.start,SEEDS.stop-1],
  episodes_per_policy=len(SEEDS)*len(SC),ticks_per_policy=len(SEEDS)*len(SC)*T,checks=len(checks)*6,gates=gates,
  crucial_assumption='Opaque pilots indistinguishable from ordinary measurements until output committed; trusted insertion and ground truth.',
  limitation='If sensor can identify probes or falsifies selected physical channels, this gate is defeated. No general anti-deception proof.')
 (P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,results=summary),indent=2))
 if manifest['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
