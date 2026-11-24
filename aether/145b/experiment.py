#!/usr/bin/env python3
"""AETHER-145B corrected standalone synthetic acceptance demonstration.
The bench receives simulated truth, NOT a genuine physical measurement.
Run python aether/145b/experiment.py. The full 3840-check local run is
in the companion AETHER-145 evidence ZIP, not this miniature reproducer.
"""
import hashlib,hmac,json
KEY1=b'AETHER145B-REFERENCE-FIXTURE'
KEY2=b'AETHER145B-BENCH-FIXTURE'
SC=('clean_fixture','valid_replacement','missing_raw_acquisition',
'untrusted_standard','unsigned_receipt','wrong_device_serial',
'expired_calibration','reference_contradiction')
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sign(x,key):return dict(x,signature=hmac.new(key,canon(x),hashlib.sha256).hexdigest())
def verify(x,key):
 return hmac.compare_digest(x.get('signature',''),
   hmac.new(key,canon({k:v for k,v in x.items() if k!='signature'}),hashlib.sha256).hexdigest())
def event(seed,sc,t):
 bad=sc not in SC[:2] and 6<=t<14
 truth=.045 if bad else .005
 g=2 if sc=='valid_replacement' and t>=10 else 1
 n=hashlib.sha256(canon([seed,sc,t])).hexdigest()[:24]
 pkt=dict(device='DUT-A',generation=g,tick=t,counter=t,nonce=n,
  path='PATH-A',raw_sha='a'*64,reference_root='MOCK-EXTERNAL',
  ref_value=truth,measured=.005,valid_until=t+1,uncertainty=.0004)
 bench=sign(dict(generation=g,tick=t,nonce=n,
     observed=truth,uncertainty=.0004),KEY2)
 if bad:
  if sc=='missing_raw_acquisition':pkt['raw_sha']=''
  if sc=='untrusted_standard':pkt['reference_root']='DUT-A'
  if sc=='wrong_device_serial':pkt['device']='DUT-B'
  if sc=='expired_calibration':pkt['valid_until']=t
  if sc=='reference_contradiction':pkt['ref_value']=.005
 if sc=='unsigned_receipt' and bad:return truth,pkt,bench
 return truth,sign(pkt,KEY1),bench
def decide(pkt,bench,t):
 if not verify(pkt,KEY1) or not verify(bench,KEY2):return False
 if pkt['device']!='DUT-A' or pkt['path']!='PATH-A' or pkt['reference_root']!='MOCK-EXTERNAL':return False
 if pkt['tick']!=t or pkt['counter']!=t or pkt['valid_until']!=t+1 or len(pkt['raw_sha'])!=64:return False
 if any(pkt[k]!=bench[k] for k in ('generation','tick','nonce')):return False
 if abs(pkt['ref_value']-bench['observed'])>pkt['uncertainty']+bench['uncertainty']:return False
 return max(pkt['ref_value']+pkt['uncertainty'],bench['observed']+bench['uncertainty'])<=.025
def main():
 totals=dict(signed_only_unsafe=0,qualified_unsafe=0,qualified_safe=0,operational_ACT=0)
 for sc in SC:
  for seed in range(145001,145031):
   for t in range(20):
    truth,p,b=event(seed,sc,t)
    naive=p['measured']<=.025
    admitted=decide(p,b,t)
    totals['signed_only_unsafe']+=int(naive and truth>.025)
    totals['qualified_unsafe']+=int(admitted and truth>.025)
    totals['qualified_safe']+=int(admitted and truth<=.025)
 assert totals==dict(signed_only_unsafe=1440,qualified_unsafe=0,
                    qualified_safe=3360,operational_ACT=0),totals
 print(json.dumps(dict(bound='AETHER-145B',status='PASS',mode='SYNTHETIC ONLY',**totals),indent=2))
if __name__=='__main__':main()
