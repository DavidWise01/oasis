#!/usr/bin/env python3
"""AETHER-138: repository-checkout synthetic receipt identity contract.
NOT the byte-identical local test; verify checkout output separately.
All hardware issuer keys, reference truths, and ingress paths are mocks.
"""
import csv,hashlib,hmac,json
from pathlib import Path
D=Path(__file__).resolve().parent
S=('clean','valid_rotation','cloned_transport_key','counter_replay','stale_reference',
   'swapped_acquisition_path','forged_hardware_flag','missing_hardware_receipt')
KEY=b'mock-device-root-138';SW=b'mock-transport-root-138'
def data(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def signed(key,obj):return dict(obj,mac=hmac.new(key,data(obj),hashlib.sha256).hexdigest())
def valid(key,obj):
 if not isinstance(obj,dict):return False
 q={k:v for k,v in obj.items() if k!='mac'}
 return hmac.compare_digest(obj.get('mac',''),hmac.new(key,data(q),hashlib.sha256).hexdigest())
def observation(seed,sc,t):
 fault=sc not in ('clean','valid_rotation') and 8<=t<16
 truth=.045 if fault else .005
 epoch=2 if sc=='valid_rotation' and t>=12 else 1
 nonce=hashlib.sha256(data([seed,sc,t])).hexdigest()[:20]
 p=signed(SW,dict(device='A',epoch=epoch,tick=t,counter=t,nonce=nonce,
                  path='INPUT-A',reading=.005))
 r=signed(KEY,dict(device='A',epoch=epoch,tick=t,counter=t,nonce=nonce,
   path='INPUT-A',reference_root='ROOT-ASSUMED',valid_until=t+1,
   measured_truth=truth,uncertainty=.0004))
 if fault:
  if sc=='cloned_transport_key':r=signed(SW,{k:v for k,v in r.items() if k!='mac'})
  elif sc=='counter_replay':r=signed(KEY,dict((k,v) for k,v in r.items() if k!='mac')|{'counter':t-1})
  elif sc=='stale_reference':r=signed(KEY,dict((k,v) for k,v in r.items() if k!='mac')|{'valid_until':t})
  elif sc=='swapped_acquisition_path':r=signed(KEY,dict((k,v) for k,v in r.items() if k!='mac')|{'path':'CAL-B'})
  elif sc=='forged_hardware_flag':r=signed(SW,dict((k,v) for k,v in r.items() if k!='mac')|{'hardware_verified':True})
  elif sc=='missing_hardware_receipt':r=None
 return truth,p,r
def bound(p,r,t):
 return valid(SW,p) and valid(KEY,r) and all(p[k]==r[k] for k in
  ('device','epoch','tick','counter','nonce','path')) and p['tick']==t and
  p['counter']==t and r['reference_root']=='ROOT-ASSUMED' and
  r['valid_until']==t+1 and r['path']=='INPUT-A' and r['uncertainty']<=.001
def trial(seed,sc,policy):
 prev='0'*64;out=[]
 for t in range(24):
  truth,p,r=observation(seed,sc,t);ok=bool(bound(p,r,t))
  act=(valid(SW,p) and p['reading']<=.025) if policy=='signed_only' else (
    ok and r['measured_truth']+r['uncertainty']<=.025)
  row=dict(scenario=sc,seed=seed,policy=policy,tick=t,action='ACT' if act else 'HOLD',
   unsafe=int(act and truth>.025),safe_act=int(act and truth<=.025),
   safe_hold=int(not act and truth<=.025),valid_receipt=int(ok),
   operational_action='HOLD') # No physical receipt; never authorize real ACT.
  digest=hashlib.sha256(prev.encode()+data(row)).hexdigest()
  row['previous']=prev;row['digest']=digest;prev=digest;out.append(row)
 return out
def chain(rows):
 prev='0'*64
 for r in rows:
  q={k:v for k,v in r.items() if k not in ('previous','digest')}
  h=hashlib.sha256(prev.encode()+data(q)).hexdigest()
  if r['previous']!=prev or r['digest']!=h:return False
  prev=h
 return True
def save(name,rows):
 with (D/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 checks=[];seed_results=[];traces=[]
 for sc in S:
  for seed in range(138001,138041):
   for policy in ('signed_only','receipt_bound'):
    a=trial(seed,sc,policy)
    tests=dict(replay=a==trial(seed,sc,policy),hash_chain=chain(a),one_action=len(a)==24,
      ticks=all(r['tick']==i for i,r in enumerate(a)),
      operational_hold=all(r['operational_action']=='HOLD' for r in a),
      zero_unsafe=policy!='receipt_bound' or all(r['unsafe']==0 for r in a),
      bound_before_act=policy!='receipt_bound' or all(r['action']=='HOLD' for r in a if not r['valid_receipt']),
      clean_or_rotation=sc not in ('clean','valid_rotation') or all(r['safe_act']==1 for r in a))
    checks.append(dict(scenario=sc,seed=seed,policy=policy,**{k:int(v) for k,v in tests.items()}))
    seed_results.append(dict(scenario=sc,seed=seed,policy=policy,
      unsafe=sum(r['unsafe'] for r in a),safe_act=sum(r['safe_act'] for r in a),
      safe_hold=sum(r['safe_hold'] for r in a),valid_receipts=sum(r['valid_receipt'] for r in a)))
    if seed==138001:traces.extend(a)
 save('checkout_checks.csv',checks);save('checkout_seed_results.csv',seed_results)
 save('checkout_trace_samples.csv',traces)
 summary=[]
 for sc in (*S,'ALL'):
  for policy in ('signed_only','receipt_bound'):
   z=[r for r in seed_results if r['policy']==policy and (sc=='ALL' or r['scenario']==sc)]
   summary.append(dict(scenario=sc,policy=policy,cases=len(z),
     unsafe=sum(r['unsafe'] for r in z),safe_act=sum(r['safe_act'] for r in z),
     safe_hold=sum(r['safe_hold'] for r in z),valid_receipts=sum(r['valid_receipts'] for r in z),
     operational_act=0))
 save('checkout_results.csv',summary)
 end={(r['scenario'],r['policy']):r for r in summary}
 passed=all(all(v==1 for k,v in r.items() if k not in ('scenario','seed','policy')) for r in checks)
 passed &= end['ALL','signed_only']['unsafe']==1920 and end['ALL','receipt_bound']['unsafe']==0
 manifest=dict(bound='AETHER-138',checkout_reproduction_status='PASS' if passed else 'FAIL',
   scenario_count=8,episodes_per_policy=320,checks=5120,physical_validation='NOT PERFORMED',
   operational_ACT=0,local_output_is_separately_archived=True)
 (D/'checkout_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,all=[v for v in summary if v['scenario']=='ALL']),indent=2))
 if not passed:raise SystemExit(1)
if __name__=='__main__':main()
