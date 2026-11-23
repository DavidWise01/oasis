#!/usr/bin/env python3
"""AETHER-133B: corrected bounded synthetic same-path ingress / probe-binding test.

The *trusted* ingress meter supplies an HMAC-protected routing receipt. A sensor
cannot create that receipt in this model; this does not prove a physical property.
No field hardware, external challenge injector, or physical reference used.
"""
import csv, hashlib, hmac, json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
SCENARIOS=('clean','calibration_bypass','path_swap','receipt_replay','nonce_mismatch',
           'counter_rollback','missing_receipt','valid_rekey','response_divergence','stale_calibration')
SEEDS=range(133001,133041);TICKS=24;LIMIT=.025
SENSOR_KEY=b'synthetic-device';INGRESS_KEY=b'synthetic-protected-ingress'

def canon(a):return json.dumps(a,sort_keys=True,separators=(',',':')).encode()
def sign(a,key):
 payload={k:v for k,v in a.items() if k!='mac'}
 return dict(payload,mac=hmac.new(key,canon(payload),hashlib.sha256).hexdigest())
def verify(a,key):
 if a is None or not isinstance(a,dict):return False
 payload={k:v for k,v in a.items() if k!='mac'}
 return hmac.compare_digest(a.get('mac',''),sign(payload,key)['mac'])

def observation(seed,scenario,t):
 rng=np.random.default_rng(seed*7+SCENARIOS.index(scenario)*1000003+t*17)
 hazard=scenario not in ('clean','valid_rekey') and 8<=t<18
 truth=.07 if hazard else .003
 # A compromised device can understate the operational count while preserving
 # the clean dedicated calibration channel (the endpoint-only error).
 apparent=.003+float(rng.uniform(-.00018,.00018)) if hazard else truth+float(rng.uniform(-.00018,.00018))
 epoch=2 if scenario=='valid_rekey' and t>=12 else 1
 token=f'{seed}:{epoch}:{t}:proof'
 receipt=sign(dict(tick=t,epoch=epoch,device='REF-133',path='shared-physical-channel',
   ingress='trusted-port-0',insertion_nonce=token,counter=t,challenge_digest=f'probe-{seed}-{t}',
   probe_path='shared-physical-channel',risk_path='shared-physical-channel'),INGRESS_KEY)
 packet=sign(dict(tick=t,epoch=epoch,device='REF-133',path='shared-physical-channel',
   insertion_nonce=token,counter=t,observed_risk=round(apparent,9),
   challenge_digest=f'probe-{seed}-{t}'),SENSOR_KEY)
 calibration=sign(dict(tick=t,epoch=epoch,device='REF-133',path='shared-physical-channel',
   insertion_nonce=token,challenge_digest=f'probe-{seed}-{t}',
   valid_until=t+1,calibrated=True,residual=.001),SENSOR_KEY)
 if hazard:
  if scenario=='calibration_bypass':
   receipt=sign(dict(receipt,path='dedicated-calibration-channel',probe_path='dedicated-calibration-channel'),INGRESS_KEY)
  elif scenario=='path_swap':
   packet=sign(dict(packet,path='alternate-risk-channel'),SENSOR_KEY)
  elif scenario=='receipt_replay':
   receipt=sign(dict(receipt,tick=t-1,counter=t-1),INGRESS_KEY)
  elif scenario=='nonce_mismatch':
   receipt=sign(dict(receipt,insertion_nonce='old-nonce'),INGRESS_KEY)
  elif scenario=='counter_rollback':
   packet=sign(dict(packet,counter=t-1),SENSOR_KEY)
  elif scenario=='missing_receipt':receipt=None
  elif scenario=='response_divergence':
   receipt=sign(dict(receipt,risk_path='alternate-risk-channel'),INGRESS_KEY)
  elif scenario=='stale_calibration':
   calibration=sign(dict(calibration,valid_until=t),SENSOR_KEY)
 return truth,packet,calibration,receipt

def authorize(t,p,c,r,policy):
 if not (verify(p,SENSOR_KEY) and verify(c,SENSOR_KEY) and p['tick']==t):return False,'invalid_sensor_packet'
 # The independent *signed-only comparator* checks the calibration packet but
 # cannot tell that challenge and operation traversed different physical routes.
 nominal=c['calibrated'] and c['residual']<=.01 and p['observed_risk']+.0004<=LIMIT
 if policy=='signed_only':return bool(nominal),'nominal_calibration'
 if not verify(r,INGRESS_KEY):return False,'missing_or_invalid_ingress'
 joint=(p['device']==c['device']==r['device'] and p['epoch']==c['epoch']==r['epoch']
  and p['tick']==c['tick']==r['tick']==t and r['counter']==p['counter']==t
  and p['path']==c['path']==r['path']==r['probe_path']==r['risk_path']
  and r['ingress']=='trusted-port-0' and p['insertion_nonce']==c['insertion_nonce']==r['insertion_nonce']
  and p['challenge_digest']==c['challenge_digest']==r['challenge_digest']
  and c['valid_until']==t+1)
 if not joint:return False,'path_or_causality_mismatch'
 return bool(nominal),'ingress_bound'

def episode(seed,sc,policy):
 rows=[];prev='0'*64
 for t in range(TICKS):
  truth,p,c,r=observation(seed,sc,t)
  act,reason=authorize(t,p,c,r,policy)
  row=dict(seed=seed,scenario=sc,policy=policy,tick=t,action='ACT' if act else 'HOLD',
   reason=reason,unsafe=int(act and truth>LIMIT),safe_act=int(act and truth<=LIMIT),
   safe_hold=int(not act and truth<=LIMIT),receipt_ok=int(verify(r,INGRESS_KEY)),
   epoch=p['epoch'],ingress_bound=int(reason=='ingress_bound'),truth=truth)
  h=hashlib.sha256(prev.encode()+canon(row)).hexdigest();row['prev_hash']=prev;row['hash']=h
  prev=h;rows.append(row)
 return rows

def chain(rows):
 prev='0'*64
 for r in rows:
  payload={k:v for k,v in r.items() if k not in ('hash','prev_hash')}
  h=hashlib.sha256(prev.encode()+canon(payload)).hexdigest()
  if r['prev_hash']!=prev or r['hash']!=h:return False
  prev=h
 return True

def write(filename,rows):
 with (ROOT/filename).open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def main():
 results=[];checks=[];traces=[]
 for sc in SCENARIOS:
  for seed in SEEDS:
   for policy in ('signed_only','ingress_bound'):
    a=episode(seed,sc,policy);b=episode(seed,sc,policy)
    rules=dict(replay=a==b,hash_chain=chain(a),one_action=len(a)==TICKS and all(r['action'] in ('ACT','HOLD') for r in a),
     tick_continuity=all(r['tick']==i for i,r in enumerate(a)),no_unsafe=policy!='ingress_bound' or all(r['unsafe']==0 for r in a),
     no_unbound_act=policy!='ingress_bound' or all(r['action']=='HOLD' for r in a if not r['ingress_bound']),
     valid_signature=all(verify(observation(seed,sc,t)[1],SENSOR_KEY) and verify(observation(seed,sc,t)[2],SENSOR_KEY) for t in range(TICKS)))
    checks.append(dict(seed=seed,scenario=sc,policy=policy,**{k:int(v) for k,v in rules.items()}))
    results.append(dict(seed=seed,scenario=sc,policy=policy,unsafe=sum(r['unsafe'] for r in a),
      safe_act=sum(r['safe_act'] for r in a),safe_hold=sum(r['safe_hold'] for r in a)))
    if seed==SEEDS.start:traces.extend(a)
 write('checks.csv',checks);write('seed_results.csv',results);write('trace_samples.csv',traces)
 total=[]
 for sc in (*SCENARIOS,'ALL'):
  for policy in ('signed_only','ingress_bound'):
   z=[r for r in results if r['policy']==policy and (sc=='ALL' or r['scenario']==sc)]
   total.append(dict(scenario=sc,policy=policy,cases=len(z),unsafe=sum(r['unsafe'] for r in z),
    safe_act=sum(r['safe_act'] for r in z),safe_hold=sum(r['safe_hold'] for r in z)))
 write('results.csv',total)
 lookup={(r['scenario'],r['policy']):r for r in total}
 gates=dict(zero_unsafe=lookup['ALL','ingress_bound']['unsafe']==0,
  comparator_counterexample=lookup['ALL','signed_only']['unsafe']>0,
  clean_availability=lookup['clean','ingress_bound']['safe_act']==lookup['clean','signed_only']['safe_act'],
  rekey_availability=lookup['valid_rekey','ingress_bound']['safe_act']==lookup['valid_rekey','signed_only']['safe_act'],
  tests=all(all(v==1 for k,v in r.items() if k not in ('seed','scenario','policy')) for r in checks))
 manifest=dict(bound='AETHER-133B',phase='VII',status='PASS' if all(gates.values()) else 'FAIL',
   paired_episodes=len(SEEDS)*len(SCENARIOS),decisions_per_policy=len(SEEDS)*len(SCENARIOS)*TICKS,
   checks=len(checks)*7,gates=gates,limits=['Trusted ingress HMAC issuance is a synthetic assumption',
   'Same-path receipt fields do not independently prove physical route','No physical device or injector connected',
   'Selective attested dishonesty and key compromise are outside the tested model'])
 (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(dict(manifest=manifest,results=total),indent=2))
 if manifest['status']!='PASS':raise SystemExit(2)
if __name__=='__main__':main()
