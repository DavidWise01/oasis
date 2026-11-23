#!/usr/bin/env python3
"""AETHER-121 reproducible synthetic sensor calibration study (no quorum)."""
import csv,hashlib,hmac,json
from pathlib import Path
import numpy as np
from scipy.stats import beta
D=Path(__file__).resolve().parent;KEY=b'aether121-synthetic-measurement-key'
T=24;N=560;LIMIT=.025;LOW=8;HIGH=100
SC=('clean','negative_bias','gradual_drift','stuck_low','abrupt_bias','high_bias','calibration_fault','risk_transition')
SEEDS=range(121001,121061)
def sign(b):
 return dict(b,mac=hmac.new(KEY,json.dumps(b,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest())
def verify(p):
 b={k:v for k,v in p.items() if k!='mac'}
 return hmac.compare_digest(p.get('mac',''),sign(b)['mac'])
def bound(e):return 1. if e>=N else float(beta.ppf(.95,e+1,N-e))
def reality(s,t):return .085 if (5<=t<20 if s=='risk_transition' else 8<=t<18) else .003
def measure(s,t,x):
 if s=='negative_bias':return max(0,x-35)
 if s=='gradual_drift':return max(0,x-max(0,t-3)*3)
 if s=='stuck_low':return 0
 if s=='abrupt_bias':return max(0,x-(40 if t>=8 else 0))
 if s=='high_bias':return min(N,x+30)
 return x
def observation(seed,s,t):
 rng=np.random.default_rng(seed+100000*SC.index(s)+7919*t)
 risk=reality(s,t);truth=int(rng.binomial(N,risk))
 lo=measure(s,t,LOW);hi=measure(s,t,HIGH)
 if s=='calibration_fault' and 8<=t<18:lo=LOW-6
 p=sign(dict(source='risk-audit',epoch=1,seq=t,observed_t=t,counter=t,valid_until=t+1,
  independent=True,n=N,errors=measure(s,t,truth),challenge_low=lo,challenge_high=hi,challenge_seq=t))
 return risk,truth,p
def episode(seed,s,policy):
 rows=[];prev='0'*64
 for t in range(T):
  risk,truth,p=observation(seed,s,t)
  signed=(verify(p) and p['source']=='risk-audit' and p['epoch']==1 and p['seq']==t
   and p['observed_t']==t and p['counter']==t and p['valid_until']==t+1
   and p['independent'] is True and p['n']==N)
  calibrated=(signed and p['challenge_seq']==t and abs(p['challenge_low']-LOW)<=1 and abs(p['challenge_high']-HIGH)<=1)
  admit=signed and (policy=='signed_only' or calibrated)
  act=admit and bound(p['errors'])<=LIMIT
  row=dict(seed=seed,scenario=s,tick=t,policy=policy,truth_risk=risk,truth_errors=truth,
   measured_errors=p['errors'],challenge_low=p['challenge_low'],challenge_high=p['challenge_high'],
   signature_valid=int(signed),calibration_valid=int(calibrated),admitted=int(admit),
   action='ACT' if act else 'HOLD',unsafe=int(act and risk>LIMIT),
   safe_act=int(act and risk<=LIMIT),safe_hold=int(not act and risk<=LIMIT),
   cost=round((10*N*risk if act else .05*N)+(.01*2*N if policy=='calibrated' else 0),2))
  base=json.dumps(row,sort_keys=True,separators=(',',':'))
  row['previous_hash']=prev;prev=hashlib.sha256((prev+base).encode()).hexdigest();row['hash']=prev
  rows.append(row)
 return rows
def chain(rows):
 prev='0'*64
 for row in rows:
  b={k:v for k,v in row.items() if k not in ('previous_hash','hash')}
  digest=hashlib.sha256((prev+json.dumps(b,sort_keys=True,separators=(',',':'))).encode()).hexdigest()
  if row['previous_hash']!=prev or row['hash']!=digest:return False
  prev=digest
 return True
def save(name,records):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
def main():
 seeds=[];checks=[];traces=[]
 for s in SC:
  for seed in SEEDS:
   for policy in ('signed_only','calibrated'):
    a=episode(seed,s,policy);b=episode(seed,s,policy)
    checks.append(dict(scenario=s,seed=seed,policy=policy,replay=int(a==b),
     hash_chain=int(chain(a)),signed_packet=int(all(r['signature_valid'] for r in a)),
     fail_closed=int(all(r['action']=='HOLD' for r in a if policy=='calibrated' and not r['calibration_valid'])),
     zero_unsafe=int(policy!='calibrated' or not any(r['unsafe'] for r in a)),
     no_future=int(all(r['admitted']<=r['signature_valid'] and 0<=r['tick']<T for r in a))))
    seeds.append(dict(scenario=s,seed=seed,policy=policy,unsafe=sum(r['unsafe'] for r in a),
     safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a),
     rejected_calibration=sum(not r['calibration_valid'] for r in a),cost=round(sum(r['cost'] for r in a),2)))
    if seed==SEEDS.start:traces.extend(a)
 save('checks.csv',checks);save('seed_results.csv',seeds);save('trace_samples.csv',traces)
 totals=[]
 for s in (*SC,'ALL'):
  for policy in ('signed_only','calibrated'):
   z=[r for r in seeds if r['policy']==policy and (s=='ALL' or r['scenario']==s)]
   totals.append(dict(scenario=s,policy=policy,cases=len(z),unsafe=sum(r['unsafe'] for r in z),
    safe_act=sum(r['safe_act'] for r in z),safe_hold=sum(r['safe_hold'] for r in z),
    rejected_calibration=sum(r['rejected_calibration'] for r in z),cost=round(sum(r['cost'] for r in z),2)))
 save('results.csv',totals);d={(r['scenario'],r['policy']):r for r in totals}
 gates=dict(no_unsafe=d['ALL','calibrated']['unsafe']==0,
  reduction=d['ALL','calibrated']['unsafe']<d['ALL','signed_only']['unsafe'],
  clean_availability=d['clean','calibrated']['safe_act']==d['clean','signed_only']['safe_act'],
  transition_availability=d['risk_transition','calibrated']['safe_act']==d['risk_transition','signed_only']['safe_act'],
  all_checks=all(all(v==1 for k,v in r.items() if k not in ('scenario','seed','policy')) for r in checks))
 manifest=dict(bound='AETHER-121',phase='VI',status='PASS' if all(gates.values()) else 'FAIL',
  cases=480,decisions_per_policy=11520,check_count=5760,gates=gates,seed_start=SEEDS.start,seed_end=SEEDS.stop-1,
  caveats=['Trusted known challenges and their scheduling assumed','Selective falsification of challenge responses can bypass this quality gate',
   'Single measurement ancestry: no independent source corroboration','Per-tick quality checks add cost; all outcomes synthetic'])
 (D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,results=totals),indent=2))
 if manifest['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
