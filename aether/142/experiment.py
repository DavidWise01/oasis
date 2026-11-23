#!/usr/bin/env python3
"""AETHER-142 synthetic drift/alarm contract. Independent GitHub reproducer.
This file is NOT byte-identical to the tested local implementation.
No physical reference, certified alarm, or real instrument was used.
"""
import hashlib,hmac,json,csv
from pathlib import Path
D=Path(__file__).resolve().parent
SC=['clean','valid_rotation','slow_drift','hidden_jump','missed_alarm','understated_drift','stale_readout','forged_alarm']
T=24;LIMIT=.025
def raw(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def stamp(k,x):return dict(x,mac=hmac.new(k,raw(x),hashlib.sha256).hexdigest())
def check(k,x):
 return hmac.compare_digest(str(x.get('mac','')),hmac.new(k,raw({a:v for a,v in x.items() if a!='mac'}),hashlib.sha256).hexdigest())
def point(seed,scenario,t):
 fault=scenario not in ('clean','valid_rotation','slow_drift') and 8<=t<16
 true=.045 if fault else .005
 g=2 if scenario=='valid_rotation' and t>=12 else 1
 nonce=hashlib.sha256(raw([seed,scenario,t])).hexdigest()[:20]
 pkt=stamp(b'142-tr',dict(device='DUT-142',generation=g,tick=t,counter=t,
  nonce=nonce,path='ACQUISITION-A',reading=.005,alarm=scenario=='forged_alarm' and fault))
 ref=dict(issuer='EXTERNAL-MOCK',device='DUT-142',generation=g,tick=t,
  nonce=nonce,path='ACQUISITION-A',reading=true,uncertainty=.0003,drift_bound=.0005,expiry=t+1)
 if fault and scenario=='stale_readout':ref['tick']=t-1
 if fault and scenario=='understated_drift':ref['drift_bound']=0
 return true,pkt,stamp(b'142-ref',ref)
def permission(t,p,r):
 if not check(b'142-tr',p) or not check(b'142-ref',r):return False
 if p['tick']!=t or p['counter']!=t or r['expiry']!=t+1:return False
 if any(p[k]!=r[k] for k in ('device','generation','tick','nonce','path')):return False
 if r['issuer']!='EXTERNAL-MOCK' or not .0002<=r['uncertainty']<=.001:return False
 if not .0001<=r['drift_bound']<=.002:return False
 if abs(p['reading']-r['reading'])>r['uncertainty']+r['drift_bound']:return False
 if p['alarm']:return False
 return r['reading']+r['uncertainty']+r['drift_bound']<=LIMIT
def save(n,rows):
 with (D/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run():
 checks=[];cases=[];traces=[]
 for sc in SC:
  for seed in range(142001,142041):
   for policy in ('signed_only','drift_gated'):
    rows=[];prev='0'*64
    for tick in range(T):
     truth,p,r=point(seed,sc,tick);ok=permission(tick,p,r)
     act=(check(b'142-tr',p) and p['reading']<=LIMIT) if policy=='signed_only' else ok
     row=dict(scenario=sc,seed=seed,policy=policy,tick=tick,action='ACT' if act else 'HOLD',
       unsafe=int(act and truth>LIMIT),safe_act=int(act and truth<=LIMIT),
       reference_ok=int(ok),operational_act=0)
     h=hashlib.sha256(prev.encode()+raw(row)).hexdigest()
     row['prev_hash']=prev;row['hash']=h;prev=h;rows.append(row)
    prev='0'*64;chain=True
    for item in rows:
     a={k:v for k,v in item.items() if k not in ('prev_hash','hash')}
     v=hashlib.sha256(prev.encode()+raw(a)).hexdigest()
     chain &= item['prev_hash']==prev and item['hash']==v;prev=v
    gates=dict(chain=chain,ticks=len(rows)==T,one_action=all(x['action'] in ('ACT','HOLD') for x in rows),
      no_unsafe=policy!='drift_gated' or all(x['unsafe']==0 for x in rows),
      fail_closed=policy!='drift_gated' or all(x['action']=='HOLD' for x in rows if not x['reference_ok']),
      clean=sc not in SC[:3] or all(x['safe_act']==1 for x in rows),
      operational_hold=all(x['operational_act']==0 for x in rows),
      monotonic=all(x['tick']==i for i,x in enumerate(rows)))
    checks.extend(dict(scenario=sc,seed=seed,policy=policy,gate=k,passed=int(v)) for k,v in gates.items())
    cases.append(dict(scenario=sc,seed=seed,policy=policy,unsafe=sum(x['unsafe'] for x in rows),
      safe_act=sum(x['safe_act'] for x in rows),reference_ok=sum(x['reference_ok'] for x in rows)))
    if seed==142001:traces.extend(rows)
 save('checkout_checks.csv',checks);save('checkout_seed_results.csv',cases);save('checkout_trace_samples.csv',traces)
 totals=[]
 for sc in SC+['ALL']:
  for policy in ('signed_only','drift_gated'):
   z=[x for x in cases if x['policy']==policy and (sc=='ALL' or x['scenario']==sc)]
   totals.append(dict(scenario=sc,policy=policy,episodes=len(z),unsafe=sum(x['unsafe'] for x in z),
     safe_act=sum(x['safe_act'] for x in z),reference_ok=sum(x['reference_ok'] for x in z)))
 save('checkout_results.csv',totals)
 overall={x['policy']:x for x in totals if x['scenario']=='ALL'}
 passed=all(x['passed'] for x in checks) and overall['signed_only']['unsafe']==1600 and overall['drift_gated']['unsafe']==0
 manifest=dict(bound='AETHER-142',status='PASS' if passed else 'FAIL',
  note='Synthetic, independently authored GitHub implementation; not checkout-verified',
  episodes_per_policy=320,checks=len(checks),physical_validation=0)
 (D/'checkout_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,overall=overall),indent=2))
 if not passed:raise SystemExit(1)
if __name__=='__main__':run()
