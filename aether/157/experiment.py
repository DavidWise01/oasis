#!/usr/bin/env python3
"""AETHER-157 synthetic same-path challenge. Compact GitHub reproduction.
Full 3200-check executed local source is in the associated evidence ZIP.
No real physical calibration or operational permission.
"""
import json,hashlib,hmac
CASES=('clean','legitimate_rotation','missing_probe','bypassed_probe',
       'swapped_route','replayed_pulse','late_propagation','false_coupling')
K=b'AETHER157-MOCK'
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sign(x):return dict(x,mac=hmac.new(K,enc(x),hashlib.sha256).hexdigest())
def verify(x):
 return isinstance(x,dict) and hmac.compare_digest(x.get('mac',''),
  hmac.new(K,enc({k:v for k,v in x.items() if k!='mac'}),hashlib.sha256).hexdigest())
def make(seed,sc,t):
 bad=sc not in CASES[:2] and 6<=t<14
 risk=.045 if bad else .005;g=2 if sc=='legitimate_rotation' and t>=10 else 1
 nonce=hashlib.sha256(enc([seed,sc,t])).hexdigest()[:20]
 shared=dict(serial='REF-157',generation=g,tick=t,counter=t,nonce=nonce,path='ACQ-A')
 pulse=dict(shared,response=.012,command=.012,time=1000000+t*1000+110,coupling='DECLARED-MOCK')
 capture=dict(shared,risk=risk,time=1000000+t*1000+130)
 if bad:
  if sc=='missing_probe':pulse=None
  elif sc=='bypassed_probe':pulse['response']=0
  elif sc=='swapped_route':capture['path']='ACQ-B'
  elif sc=='replayed_pulse':pulse['counter']=t-1
  elif sc=='late_propagation':capture['time']+=250
  elif sc=='false_coupling':pulse['coupling']='SELF-ASSERTED'
 return risk,sign(pulse) if pulse else None,sign(capture)
def gate(p,c):
 if not verify(p) or not verify(c):return False
 if any(p[k]!=c[k] for k in ('serial','generation','tick','counter','nonce','path')):return False
 if p['path']!='ACQ-A' or p['coupling']!='DECLARED-MOCK':return False
 if abs(p['response']-p['command'])>.00001:return False
 if p['time']!=1000000+p['tick']*1000+110:return False
 if not 0<c['time']-p['time']<=50:return False
 return c['risk']+.0005<=.025
def main():
 base=unsafe=safe=0
 for sc in CASES:
  for seed in range(157001,157026):
   for tick in range(20):
    truth,p,c=make(seed,sc,tick);act=gate(p,c)
    base+=int(truth>.025);unsafe+=int(act and truth>.025);safe+=int(act and truth<=.025)
 assert (base,unsafe,safe)==(1200,0,2800)
 print(json.dumps(dict(bound='AETHER-157',status='SYNTHETIC PASS',
  baseline_unsafe=base,guarded_unsafe=unsafe,safe_dry_run_act=safe,
  operational_act=0,physical_qualification_percent=0),indent=2))
if __name__=='__main__':main()
