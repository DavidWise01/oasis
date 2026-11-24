#!/usr/bin/env python3
"""AETHER-153 compact GitHub reproduction.
Standalone simplified check. The full 3200-check executed code is archived in
the local evidence ZIP. All roots and readings here are synthetic only.
"""
import json,hashlib,hmac
SC=['clean_fixture','legitimate_reference_rotation','missing_serial',
    'untrusted_lab','expired_certificate','missing_raw_capture',
    'path_unverified','challenge_mismatch']
KEY=b'AETHER-153-SYNTHETIC-NOT-HARDWARE'
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def sign(x):return dict(x,signature=hmac.new(KEY,enc(x),hashlib.sha256).hexdigest())
def valid(x):return hmac.compare_digest(x.get('signature',''),
     hmac.new(KEY,enc({k:v for k,v in x.items() if k!='signature'}),hashlib.sha256).hexdigest())
def make(seed,sc,t):
 bad=sc not in SC[:2] and 6<=t<14
 truth=.045 if bad else .005
 gen=2 if sc=='legitimate_reference_rotation' and t>=10 else 1
 nonce=sha(enc([seed,sc,t]))[:20]
 raw=enc(dict(reference='REF-153',generation=gen,tick=t,value=truth,nonce=nonce))
 x=dict(instrument='DUT-153',reference='REF-153',generation=gen,tick=t,
  counter=t,nonce=nonce,lab='MOCK-EXTERNAL-LAB',trace='MOCK-CAL-153',
  expires=t+1,path='MEASURE-A',challenge='MATCHED',raw_sha=sha(raw),
  observed=truth,uncertainty=.0005,commissioning='FIXTURE-ONLY')
 if bad:
  if sc=='missing_serial':x['reference']=''
  if sc=='untrusted_lab':x['lab']='DUT-SELF'
  if sc=='expired_certificate':x['expires']=t
  if sc=='missing_raw_capture':raw=b''
  if sc=='path_unverified':x['path']='UNATTESTED'
  if sc=='challenge_mismatch':x['challenge']='WRONG'
 return truth,raw,sign(x)
def gate(raw,receipt):
 if not valid(receipt):return False
 if not raw or sha(raw)!=receipt['raw_sha']:return False
 if receipt['instrument']!='DUT-153' or receipt['reference']!='REF-153':return False
 if receipt['lab']!='MOCK-EXTERNAL-LAB' or receipt['trace']!='MOCK-CAL-153':return False
 if receipt['path']!='MEASURE-A' or receipt['challenge']!='MATCHED':return False
 if receipt['expires']!=receipt['tick']+1 or receipt['counter']!=receipt['tick']:return False
 if receipt['commissioning']!='FIXTURE-ONLY':return False
 return receipt['observed']+receipt['uncertainty']<=.025
def main():
 results=dict(baseline_unsafe=0,setup_gate_unsafe=0,setup_gate_safe=0,operational_ACT=0)
 for sc in SC:
  for seed in range(153001,153026):
   for t in range(20):
    truth,raw,r=make(seed,sc,t)
    act=gate(raw,r)
    results['baseline_unsafe']+=int(truth>.025)
    results['setup_gate_unsafe']+=int(act and truth>.025)
    results['setup_gate_safe']+=int(act and truth<=.025)
 assert results==dict(baseline_unsafe=1200,setup_gate_unsafe=0,setup_gate_safe=2800,operational_ACT=0),results
 print(json.dumps(dict(bound='AETHER-153',mode='MOCK ONLY',**results),indent=2))
if __name__=='__main__':main()
