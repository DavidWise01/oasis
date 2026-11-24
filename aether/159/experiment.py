#!/usr/bin/env python3
"""AETHER-159 separate compact GitHub reproducer.
Full 3200-check local executed source (SHA256 c02f6aa6bf43b46b0b0e92fa5b604c05392c6a237b7d0cde3c971a9a13cb4f56)
is in evidence ZIP. Never claim synthetic samples are physical calibration.
"""
import json,hashlib,hmac
C=('clean','legitimate_rotation','capture_alarm_combo','issuer_path_combo','counter_clock_combo','hidden_bench_contamination','expiry_alarm_combo','signed_false_reference')
K1=b'AETHER159_SYNTHETIC_REFERENCE';K2=b'AETHER159_SYNTHETIC_BENCH'
def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def h(v):return hashlib.sha256(v).hexdigest()
def sign(v,k):return dict(v,mac=hmac.new(k,enc(v),hashlib.sha256).hexdigest())
def valid(v,k):return hmac.compare_digest(v.get('mac',''),hmac.new(k,enc({x:y for x,y in v.items() if x!='mac'}),hashlib.sha256).hexdigest())
def fixture(seed,case,t):
 bad=case not in C[:2] and 6<=t<14
 actual=.045 if bad else .005
 g=2 if case=='legitimate_rotation' and t>=10 else 1
 nonce=h(enc([seed,case,t]))[:20]
 raw=enc(dict(device='DUT-159',tick=t,nonce=nonce,samples=[actual]*3))
 v=dict(serial='DUT-159',generation=g,tick=t,counter=t,nonce=nonce,path='ACQ-A')
 r=dict(v,root='EXTERNAL-MOCK',calibration='CAL-159',expires=t+1,observed=actual,
   uncertainty=.0005,raw_sha=h(raw),alarm=int(actual>.025),latency=20)
 b=dict(v,root='BENCH-MOCK',observed=actual,alarm=int(actual>.025),latency=20)
 if bad:
  if case=='capture_alarm_combo':raw=b'';r['alarm']=0
  if case=='issuer_path_combo':r['root']='DUT-OWNED';b['path']='BYPASS-B'
  if case=='counter_clock_combo':r['counter']-=1;b['latency']=120
  if case=='hidden_bench_contamination':r['observed']=b['observed']=.005;r['alarm']=b['alarm']=0
  if case=='expiry_alarm_combo':r['expires']=t;r['alarm']=0
  if case=='signed_false_reference':r['observed']=.005;r['alarm']=0
 return actual,raw,sign(r,K1),sign(b,K2)
def admit(raw,r,b):
 if not(valid(r,K1) and valid(b,K2)) or not raw or h(raw)!=r['raw_sha']:return False
 if any(r[k]!=b[k] for k in ('serial','generation','tick','counter','nonce','path')):return False
 if r['root']!='EXTERNAL-MOCK' or b['root']!='BENCH-MOCK' or r['path']!='ACQ-A':return False
 if r['expires']!=r['tick']+1 or r['latency']>50 or b['latency']>50:return False
 if r['alarm']!=b['alarm']:return False
 try:
  d=json.loads(raw);a=d['samples'];mean=sum(a)/len(a)
  if enc(d)!=raw or d['device']!='DUT-159' or d['tick']!=r['tick'] or d['nonce']!=r['nonce'] or len(a)!=3:return False
 except (ValueError,KeyError,ZeroDivisionError,TypeError):return False
 return abs(mean-r['observed'])<=r['uncertainty'] and abs(mean-b['observed'])<=r['uncertainty'] and r['alarm']==int(mean>.025) and mean+r['uncertainty']<=.025
def main():
 baseline=unsafe=safe=0
 for case in C:
  for seed in range(159001,159026):
   for tick in range(20):
    truth,raw,r,b=fixture(seed,case,tick);accept=admit(raw,r,b)
    baseline+=int(truth>.025);unsafe+=int(accept and truth>.025);safe+=int(accept and truth<=.025)
 assert (baseline,unsafe,safe)==(1200,0,2800),(baseline,unsafe,safe)
 print(json.dumps(dict(bound='AETHER-159',status='SYNTHETIC PASS',baseline_unsafe=baseline,blind_unsafe=unsafe,blind_safe=safe,physical_act=0),indent=2))
if __name__=='__main__':main()
