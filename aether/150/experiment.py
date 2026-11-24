#!/usr/bin/env python3
"""AETHER-150 synthetic drift/alarm protocol demonstration.

This is a reduced checkout reproduction; complete locally executed 3840-check
experiment (SHA256 b6459d27a9f15b7d29a6410e178c44dae365268cd524a6393084d711523c75e1)
is distributed separately. Real physical evidence = none; operational ACT = HOLD.
"""
import json,hashlib,hmac
SC=('clean','valid_replacement','hidden_slow_drift','abrupt_drift',
    'suppressed_alarm','delayed_alarm','stale_calibration','forged_drift_certificate')
ROOT=b'MOCK-EXTERNAL-REFERENCE-150'
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sign(x):return dict(x,mac=hmac.new(ROOT,canon(x),hashlib.sha256).hexdigest())
def verify(x):
 return hmac.compare_digest(x.get('mac',''),
  hmac.new(ROOT,canon({k:v for k,v in x.items() if k!='mac'}),hashlib.sha256).hexdigest())
def event(seed,sc,t):
 bad=sc not in SC[:2] and 6<=t<14
 risk=.045 if bad else .005
 generation=2 if sc=='valid_replacement' and t>=10 else 1
 nonce=hashlib.sha256(canon((seed,sc,t))).hexdigest()[:20]
 c=dict(device='DUT-150',generation=generation,tick=t,counter=t,nonce=nonce,
  source='SIMULATED-EXTERNAL-ROOT',path='INPUT-A',calibration_epoch=generation,
  expiry=t+1,observed=risk,uncertainty=.0004,drift_bound=.002,
  alarm_state=int(bad),alarm_latency=0)
 if bad:
  if sc=='hidden_slow_drift':c['drift_bound']=.00001
  if sc=='suppressed_alarm':c['alarm_state']=0
  if sc=='delayed_alarm':c['alarm_latency']=4
  if sc=='stale_calibration':c['expiry']=t
  if sc=='forged_drift_certificate':c['source']='DUT-SELF-ASSERTED'
 oracle=sign(dict(tick=t,nonce=nonce,truth=risk))
 return risk,sign(c),oracle
def allowed(c,o,t):
 if not verify(c) or not verify(o):return False
 if c['tick']!=o['tick'] or c['tick']!=t or c['counter']!=t:return False
 if c['nonce']!=o['nonce'] or c['source']!='SIMULATED-EXTERNAL-ROOT':return False
 if c['path']!='INPUT-A' or c['calibration_epoch']!=c['generation'] or c['expiry']!=t+1:return False
 if not .0003<=c['uncertainty']<=.001 or not .001<=c['drift_bound']<=.003:return False
 if c['alarm_latency']!=0 or c['alarm_state']!=int(o['truth']>.025):return False
 if abs(c['observed']-o['truth'])>c['uncertainty']:return False
 return max(c['observed'],o['truth'])+c['uncertainty']+c['drift_bound']<=.025
def main():
 results={'baseline_unsafe':0,'guarded_unsafe':0,'guarded_safe':0,'physical_ACT':0}
 for sc in SC:
  for seed in range(150001,150031):
   for t in range(20):
    risk,c,o=event(seed,sc,t);act=allowed(c,o,t)
    results['baseline_unsafe']+=int(risk>.025)
    results['guarded_unsafe']+=int(act and risk>.025)
    results['guarded_safe']+=int(act and risk<=.025)
 assert results=={'baseline_unsafe':1440,'guarded_unsafe':0,'guarded_safe':3360,'physical_ACT':0},results
 print(json.dumps(dict(bound='AETHER-150',status='PASS SYNTHETIC DEMONSTRATION',**results),indent=2))
if __name__=='__main__':main()
